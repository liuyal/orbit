# Backend Optimization Findings
**Project:** Orbit API  
**Author:** Jerry  
**Last Updated:** 2026-04-17 (race-condition + manual-key collision fix applied)  

---

## Overview

This document summarizes all optimization findings and recommendations for the Orbit FastAPI backend.  
Findings are categorized by **priority** and cover correctness bugs, performance issues, and general improvements.

---

## ✅ Completed Optimizations (as of 2026-04-17)

All route-level optimizations have been applied. See `API_OPTIMIZATION_NOTES.md` for the full breakdown.

Key improvements applied:
- `asyncio.gather` used throughout to parallelize independent DB calls.
- `db.count()` replaces `db.find() + len()` everywhere.
- `{"_id": 1}` projection used for key generation — no full documents loaded.
- DB writes removed from GET handlers.
- Redundant re-fetches eliminated by reusing already-fetched documents.
- O(1) dict-keyed cache for runner status lookups.
- Batch `$in` queries replace N×2 individual `find_one` loops in `get_cycle_executions`.
- **Atomic counter (`get_next_sequence`) replaces `max()+1` key generation** in test cases, executions, and cycles — eliminates the concurrent duplicate-key race condition.
- **`sync_sequence` advances the counter on every accepted manual key** — prevents auto-generated keys from colliding with manually-supplied keys that skipped ahead in the sequence (e.g. user inserts T1, T2, T4; next auto-key correctly yields T5 not T3/T4).

---

## ✅ Critical Issues — Resolved

### 1. Race Condition on Key Generation *(Fixed 2026-04-17)*

**Files changed:**
- `db/mongodb.py` — added `get_next_sequence` and `sync_sequence`
- `routes/test_cases.py` → `create_test_case_in_project`
- `routes/test_executions.py` → `create_execution_by_test_case_key`
- `routes/test_cycles.py` → `create_cycle_for_project`

---

#### Part A — Concurrent auto-key race condition

**Root cause:**  
Auto-key generation fetched all existing `_id`s, computed `max() + 1`, then inserted.
Under concurrent requests two callers could read the same max and attempt to insert the
same key, producing a duplicate-key error.

**Fix — `get_next_sequence`:**  
Uses MongoDB's `findOneAndUpdate` + `$inc` against a dedicated `counters` collection.
The operation is atomic on the MongoDB server — no two callers can ever receive the same
sequence number regardless of concurrency.

```python
# db/mongodb.py
async def get_next_sequence(self, db_name: str, sequence_name: str) -> int:
    result = await self._db_client[db_name]["counters"].find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return int(result["seq"])
```

Route handlers now call this instead of scanning:

```python
# Before (race condition)
existing_keys = await db.find(DB_NAME_TM, DB_COLLECTION_TM_TC, {"project_key": project_key}, {"_id": 1})
last_tc = max([int(k["_id"].split(TC_KEY_PREFIX)[-1]) for k in existing_keys]) + 1

# After (atomic, race-free)
seq = await db.get_next_sequence(DB_NAME_TM, f"{project_key}_tc")
test_case_key = f"{project_key}-{TC_KEY_PREFIX}{seq}"
```

Counter documents are auto-created on first use (`upsert=True`) — no schema migration needed.
Each project gets its own counters (e.g. `PROJ-1_tc`, `PROJ-1_te`, `PROJ-1_tcy`).

---

#### Part B — Manual key skipping ahead in the sequence

**Root cause:**  
The `counters` collection and manually-provided keys were completely independent.
If a user inserted T1, T2, T4 manually, the counter had no awareness of T4.
The next two auto-inserts would generate T3 then T4, and T4 would crash with a
`DuplicateKeyError`:

```
pymongo.errors.DuplicateKeyError: E11000 duplicate key error collection:
orbit-tm.test-cases index: _id_ dup key: { _id: "PRJ0-T4" }
```

**Fix — `sync_sequence`:**  
Called in the manual-key `else` branch of each route, immediately after the key passes
both the format check and the duplicate check. Uses MongoDB's `$max` operator to advance
the counter to at least the manually-provided key number — atomically and with no extra
round-trips if the counter is already higher.

```python
# db/mongodb.py
async def sync_sequence(self, db_name: str, sequence_name: str, min_value: int) -> None:
    await self._db_client[db_name]["counters"].update_one(
        {"_id": sequence_name},
        {"$max": {"seq": min_value}},
        upsert=True,
    )
```

```python
# routes/test_cases.py — inside the manual-key else branch
manual_num = int(test_case_key.split(TC_KEY_PREFIX)[-1])
await db.sync_sequence(DB_NAME_TM, f"{project_key}_tc", manual_num)
```

**Behaviour table:**

| Inserted keys (manual) | Counter after syncs | Next auto key |
|---|---|---|
| T1, T2, T4 | 4 | **T5** ✅ |
| T1, T2, T3 | 3 | **T4** ✅ |
| T10 | 10 | **T11** ✅ |

**Why deletion doesn't need special handling:**  
The counter is monotonically increasing and never decrements. Deleting a key leaves a gap
in the sequence (like SQL `AUTO_INCREMENT`) but never causes a future auto-generated key
to collide, because the counter only ever moves forward.

---

## 🟡 Database Architecture

### 2. Collection Strategy — Single Collection vs Per-Project Collections

**Decision: Keep the single shared collection per entity type.**

**Why NOT per-project collections:**
- MongoDB does not support cross-collection joins/queries — cross-project reports would require scatter-gather queries in application code.
- Collection proliferation increases overhead on the MongoDB server (each collection has its own namespace, indexes, and metadata).
- The aggregation framework, `$in` queries, and pagination all work cleanly on a single collection.
- Adding a new project does not require schema or infrastructure changes.

**Why single collection + indexes IS the right choice:**
- A compound index on `project_key` makes per-project queries just as fast as a dedicated collection.
- Cross-project queries remain simple and efficient.
- One index to maintain instead of N.

---

## 🟡 MongoDB Indexes

### 3. What Are Indexes?

An **index** is a data structure that MongoDB maintains alongside a collection to allow fast lookups without scanning every document (a *collection scan*).  
Without an index on `project_key`, every query like `{"project_key": "PROJ-1"}` reads **all** documents in the collection.  
With an index, MongoDB jumps directly to the matching documents — O(log n) instead of O(n).

**Index direction values:**
- `1` = ascending
- `-1` = descending

### 4. How to Create Indexes

The Motor (async MongoDB) method signature is:

```python
await collection.create_index(keys, **kwargs)
```

**Parameter name:** `keys`  
The `keys` argument is a **list of `(field, direction)` tuples**. For example:

```python
[("project_key", 1), ("test_case_key", 1)]
```

This creates a **compound index** on both fields together.

#### Recommended indexes for this project

```python
# db/mongodb.py — call once at startup inside create_indexes()

async def create_indexes(self, db_name: str):
    db = self._db_client[db_name]

    # test_cases: filter by project, or by project + key
    await db["test_cases"].create_index([("project_key", 1)])
    await db["test_cases"].create_index([("project_key", 1), ("_id", 1)])

    # test_executions: filter by project, test case key, or cycle key
    await db["test_executions"].create_index([("project_key", 1)])
    await db["test_executions"].create_index([("test_case_key", 1)])
    await db["test_executions"].create_index([("test_cycle_key", 1)])
    await db["test_executions"].create_index(
        [("project_key", 1), ("test_case_key", 1)]
    )

    # test_cycles: filter by project
    await db["test_cycles"].create_index([("project_key", 1)])
```

Call `create_indexes()` once during app startup in `app/app_def.py` (e.g., inside the `lifespan` handler).

### 5. Do You Need to Reset the Database After Creating Indexes?

**No.** `create_index` is non-destructive:
- It reads existing documents and builds the index in the background.
- All existing data is preserved.
- If the index already exists, the call is a no-op.
- The database stays online and fully operational during index creation.

### 6. How to Measure Performance Gains

Use MongoDB's `explain()` to inspect query plans before and after adding indexes:

```python
# Run in a test script or MongoDB Compass
plan = await db["test_cases"].find(
    {"project_key": "PROJ-1"}
).explain()

print(plan["queryPlanner"]["winningPlan"])
# COLLSCAN  → full collection scan (slow, no index)
# IXSCAN    → index scan (fast, index used)
```

**Other measurement approaches:**
- **Timing in Python:** wrap route calls with `time.perf_counter()` and log before/after.
- **MongoDB Compass:** the "Explain Plan" tab shows `IXSCAN` vs `COLLSCAN` visually.
- **FastAPI middleware:** add a timing middleware to log response time per endpoint.
- **`$indexStats` aggregation:** shows how often each index is actually hit in production.

---

## 🟢 Additional Backend Optimizations (Future Work)

### 7. Pagination

`GET /tm/test-cases` and similar list endpoints return **all** documents. As data grows this will be slow and memory-heavy.

**Fix:** Add `skip` / `limit` query parameters:

```python
@router.get("/tm/test-cases")
async def get_all_test_cases(skip: int = 0, limit: int = 50):
    docs = await db.find("test_cases", {}, skip=skip, limit=limit)
    return docs
```

### 8. Response Caching (read-heavy endpoints)

Endpoints like `GET /tm/projects` are read-heavy and change infrequently. A short TTL in-memory cache (e.g., `cachetools.TTLCache`) avoids repeated DB hits for the same data within the TTL window.

```python
from cachetools import TTLCache
_cache = TTLCache(maxsize=128, ttl=30)  # 30-second TTL
```

### 9. MongoDB Connection Pool Tuning

Motor's default connection pool may be undersized for high concurrency.  
Add `maxPoolSize` when creating the `AsyncIOMotorClient`:

```python
AsyncIOMotorClient(uri, maxPoolSize=50)
```

### 10. Field Projections on List Endpoints

List endpoints (`get_all_test_cases`, `get_all_projects`, etc.) return full documents.  
Return only the fields the frontend actually needs to reduce payload size and serialization time:

```python
await db.find("test_cases", {"project_key": pk}, projection={"_id": 1, "name": 1, "status": 1})
```

### 11. Structured Logging with Correlation IDs

Add a request `X-Request-ID` header and propagate it through log lines.  
This makes it possible to trace a single slow request through all log entries.

### 12. Health-Check / Readiness Endpoint

Add a `GET /health` endpoint that pings MongoDB and returns `200 OK` or `503 Service Unavailable`.  
Docker / Kubernetes can use this for readiness probes instead of relying on the process being alive.

---

## Summary of All Findings

| # | Priority | Category | Finding | Status |
|---|---|---|---|---|
| 1a | ✅ Resolved | Correctness | Concurrent race condition on auto-key generation — atomic `$inc` via `get_next_sequence` | ✅ Fixed 2026-04-17 |
| 1b | ✅ Resolved | Correctness | Manual key skipping ahead collides with auto-generated keys — `$max` sync via `sync_sequence` | ✅ Fixed 2026-04-17 |
| 2 | 🟡 Medium | Architecture | Single collection + indexes is better than per-project collections | ✅ Decision made |
| 3 | 🟡 Medium | Performance | Add compound indexes on `project_key`, `test_case_key`, `test_cycle_key` | ⏳ Pending |
| 4 | 🟡 Medium | Performance | Use `explain()` / Compass to verify `IXSCAN` after index creation | ⏳ Pending |
| 5 | 🟢 Low | Performance | Add pagination (`skip`/`limit`) to all list endpoints | ⏳ Pending |
| 6 | 🟢 Low | Performance | TTL in-memory cache for read-heavy endpoints | ⏳ Pending |
| 7 | 🟢 Low | Performance | Tune Motor connection pool (`maxPoolSize`) | ⏳ Pending |
| 8 | 🟢 Low | Performance | Field projections on list endpoints to reduce payload size | ⏳ Pending |
| 9 | 🟢 Low | Observability | Structured logging with per-request correlation IDs | ⏳ Pending |
| 10 | 🟢 Low | Reliability | Add `GET /health` readiness endpoint for Docker/k8s | ⏳ Pending |


# Backend Route Optimization Notes

Complete analysis of every FastAPI endpoint across all route files.  
Last updated: 2026-04-16 (all optimizations complete)

---

## `projects.py` — 5 endpoints

### `GET /tm/projects` → `get_all_projects` ✅ Optimized
- All project count queries run concurrently via `asyncio.gather` (inner coroutine per project, all gathered in one batch).
- Uses `db.count()` instead of `find` + `len()`.
- DB write removed from GET handler.

### `POST /tm/projects` → `create_project_by_key` ✅ Optimized
- Replaced `get_project_by_key` (3 DB calls) with a direct `db.find_one` — 1 DB call for existence check.

### `GET /tm/projects/{project_key}` → `get_project_by_key` ✅ Optimized
- Project fetch and both counts run concurrently via `asyncio.gather`.
- Uses `db.count()` instead of `find` + `len()`.
- DB write removed from GET handler.

### `PUT /tm/projects/{project_key}` → `update_project_by_key` ✅ Optimized
- Replaced `get_project_by_key` existence check with a direct `db.find_one`.
- Both count queries run concurrently via `asyncio.gather`.
- Uses `db.count()` instead of `find` + `len()`.

### `DELETE /tm/projects/{project_key}` → `delete_project_by_key` ✅ Optimized
- Replaced `get_project_by_key` existence check with a direct `db.find_one`.
- Force-check path: 3 `db.count` queries run concurrently via `asyncio.gather`.
- Force-delete path: 3 `db.delete` calls run concurrently via `asyncio.gather`.

---

## `test_cases.py` — 6 endpoints

### `GET /tm/test-cases` → `get_all_test_cases` ✅ Good
- Single `db.find` + `natsorted` in-memory. No issues.

### `GET /tm/projects/{project_key}/test-cases` → `get_all_test_cases_by_project` ✅ Optimized
- Project check and test cases fetch run concurrently via `asyncio.gather`.

### `POST /tm/projects/{project_key}/test-case` → `create_test_case_in_project` ✅ Optimized
- Key generation uses `{"_id": 1}` projection — only IDs fetched, no full documents.
- Duplicate key check via direct `db.find_one` instead of calling `get_test_case_by_key`.
- Post-create count uses `db.count()` instead of `db.find` + `len()`.
- `json` import removed.

### `DELETE /tm/projects/{project_key}/test-cases` → `delete_all_test_case_from_project` ✅ Optimized
- Project check and execution count run concurrently via `asyncio.gather`.
- Uses `db.count() > 0` instead of `find` + truthy check.
- Reuses already-fetched `project` variable instead of re-querying after deletion.

### `GET /tm/projects/{project_key}/test-cases/{test_case_key}` → `get_test_case_by_key` ✅ Optimized
- Project and test case `find_one` calls run concurrently via `asyncio.gather`.

### `PUT /tm/projects/{project_key}/test-cases/{test_case_key}` → `update_test_case_by_key` ✅ Optimized
- Project and test case fetched concurrently via `asyncio.gather` — eliminates the redundant second project lookup that came with `get_test_case_by_key`.

### `DELETE /tm/projects/{project_key}/test-cases/{test_case_key}` → `delete_test_case_by_key` ✅ Optimized
- All 3 pre-checks (project, test case, execution count) run concurrently via `asyncio.gather`.
- Execution check uses `db.count()` instead of `db.find` + truthy check.
- Post-delete count uses `db.count()` instead of `db.find` + `len()`.

---

## `test_cycles.py` — 8 endpoints

### `GET /tm/projects/{project_key}/cycles` → `get_all_cycles_for_project` ✅ Optimized
- Project check and cycles fetch run concurrently via `asyncio.gather`.

### `POST /tm/projects/{project_key}/cycles` → `create_cycle_for_project` ✅ Optimized
- Queries cycles directly (no redundant project re-check).
- Duplicate key check via direct `db.find_one` instead of `get_cycle_by_key`.
- Post-create count via `db.count()` instead of `find` + `len()`.

### `GET /tm/cycles/{test_cycle_key}` → `get_cycle_by_key` ✅ Good
- Single `db.find_one`. Clean and minimal.

### `PUT /tm/cycles/{test_cycle_key}` → `update_cycle_by_key` ✅ Good
- One update + one re-fetch. Straightforward and efficient.

### `DELETE /tm/cycles/{test_cycle_key}` → `delete_cycle_by_key` ✅ Optimized
- Existence check with `find_one`, then `asyncio.gather` concurrently deletes cycle and clears `test_cycle_key` on all linked executions.
- Data integrity issue resolved.

### `GET /tm/cycles/{test_cycle_key}/executions` → `get_cycle_executions` ✅ Optimized
- 2 sequential batch `$in` queries replacing the old N×2 individual `find_one` loop.
- In-memory O(1) dict merge.

### `POST /tm/cycles/{test_cycle_key}/executions` → `add_execution_to_cycle` ✅ Optimized
- Cycle and execution fetched concurrently via `asyncio.gather` using direct `db.find_one`.
- Both DB writes run concurrently via `asyncio.gather`.
- Eliminated end-of-function re-fetch — returns locally-modified `cycle_data` directly.

### `DELETE /tm/cycles/{test_cycle_key}/executions/{execution_key}` → `remove_executions_from_cycle` ✅ Optimized
- Same improvements as `add_execution_to_cycle`.

---

## `test_executions.py` — 6 endpoints

### `GET /tm/projects/{project_key}/executions` → `get_all_executions_by_project` ✅ Optimized
- Project check and executions fetch run concurrently via `asyncio.gather`.

### `DELETE /tm/projects/{project_key}/executions` → `delete_all_test_execution_by_project` ✅ Optimized
- 3 concurrent bulk operations via `asyncio.gather`: `update_many` test cases + `update_many` cycles + `delete` executions.

### `GET /tm/projects/{project_key}/test-cases/{test_case_key}/executions` → `get_all_executions_by_test_case_key` ✅ Optimized
- Project and test case `find_one` checks run concurrently via `asyncio.gather`.

### `POST /tm/projects/{project_key}/test-cases/{test_case_key}/executions` → `create_execution_by_test_case_key` ✅ Optimized
- Project and test case checks run concurrently via `asyncio.gather`.
- Key generation uses `db.find` with `{"_id": 1}` projection — no full documents loaded.
- Duplicate key check via direct `db.find_one` instead of `get_execution_by_test_case_key`.
- `json` import removed (no longer needed).

### `GET /tm/executions/{execution_key}` → `get_execution_by_key` ✅ Good
- Single `db.find_one`. Clean and minimal.

### `PUT /tm/executions/{execution_key}` → `update_execution_by_key` ✅ Optimized
- Direct `db.find_one` for existence check — raw doc in hand, no JSONResponse overhead.
- Post-update re-fetch eliminated — `test_case_key` and `test_cycle_key` extracted from already-fetched doc.
- Test case and cycle fetches run concurrently via `asyncio.gather`.
- Test case and cycle updates run concurrently via `asyncio.gather`.
- Return value built from in-memory merge — no extra DB round-trip.

### `DELETE /tm/executions/{execution_key}` → `delete_execution_by_key` ✅ Good
- Fetches execution, conditionally updates linked test case, then deletes. Minimal and correct.

---

## `runners.py` — 2 endpoints ✅ Optimized

### `GET /runners/status` → `get_runners_status`
- Returns `list(cache.values())` from dict-keyed cache.

### `GET /runners/status/{name}` → `get_runners_status_by_name`
- O(1) `cache.get(name)` lookup. Cache stored as `{name: runner_data}` dict in `module/runners.py`.

---

## `root.py` — 3 endpoints ✅ No Action Needed

### `GET /` → `root` — Returns 204. No DB calls.
### `GET /api/{version}` → `root_api` — Redirect only. No DB calls.
### `POST /api/{version}/reset-database` → `reset_database` — Admin utility.

---

## Summary Table

| File | Endpoint Function | Status | Notes |
|---|---|---|---|
| projects.py | `get_all_projects` | ✅ Optimized | Concurrent counts, `db.count()`, no write on GET |
| projects.py | `create_project_by_key` | ✅ Optimized | Direct `find_one` existence check |
| projects.py | `get_project_by_key` | ✅ Optimized | 3 concurrent queries, `db.count()`, no write on GET |
| projects.py | `update_project_by_key` | ✅ Optimized | Direct `find_one`, concurrent `db.count()` |
| projects.py | `delete_project_by_key` | ✅ Optimized | Direct `find_one`, concurrent counts + deletes |
| test_cases.py | `get_all_test_cases` | ✅ Good | — |
| test_cases.py | `get_all_test_cases_by_project` | ✅ Optimized | Concurrent project + cases fetch |
| test_cases.py | `delete_all_test_case_from_project` | ✅ Optimized | Concurrent check, `db.count()`, reuse project var |
| test_cases.py | `get_test_case_by_key` | ✅ Optimized | Concurrent project + test case fetch |
| test_cases.py | `create_test_case_in_project` | ✅ Optimized | `_id` projection for key gen, `db.count()`, direct lookups |
| test_cases.py | `update_test_case_by_key` | ✅ Optimized | Concurrent project + test case fetch, no redundant lookup |
| test_cases.py | `delete_test_case_by_key` | ✅ Optimized | 3 concurrent pre-checks, `db.count()` throughout |
| test_cycles.py | `get_all_cycles_for_project` | ✅ Optimized | Concurrent project + cycles fetch |
| test_cycles.py | `create_cycle_for_project` | ✅ Optimized | Direct queries, `db.count()`, no redundant checks |
| test_cycles.py | `get_cycle_by_key` | ✅ Good | — |
| test_cycles.py | `update_cycle_by_key` | ✅ Good | — |
| test_cycles.py | `delete_cycle_by_key` | ✅ Optimized | Concurrent delete + execution cleanup, data integrity fixed |
| test_cycles.py | `get_cycle_executions` | ✅ Optimized | Batch `$in` queries, O(1) merge |
| test_cycles.py | `add_execution_to_cycle` | ✅ Optimized | Concurrent fetch + concurrent writes, no re-fetch |
| test_cycles.py | `remove_executions_from_cycle` | ✅ Optimized | Concurrent fetch + concurrent writes, no re-fetch |
| test_executions.py | `get_all_executions_by_project` | ✅ Optimized | Concurrent project + executions fetch |
| test_executions.py | `delete_all_test_execution_by_project` | ✅ Optimized | 3 concurrent bulk operations |
| test_executions.py | `get_all_executions_by_test_case_key` | ✅ Optimized | Concurrent project + test case check |
| test_executions.py | `create_execution_by_test_case_key` | ✅ Optimized | Concurrent checks, `_id` projection, direct lookups |
| test_executions.py | `get_execution_by_key` | ✅ Good | — |
| test_executions.py | `update_execution_by_key` | ✅ Optimized | Direct fetch, no re-fetch, concurrent TC+cycle ops |
| test_executions.py | `delete_execution_by_key` | ✅ Good | — |
| runners.py | `get_runners_status` | ✅ Optimized | Dict-keyed cache |
| runners.py | `get_runners_status_by_name` | ✅ Optimized | O(1) dict lookup |
| root.py | `root` | ✅ Good | — |
| root.py | `root_api` | ✅ Good | — |
| root.py | `reset_database` | ✅ Good | — |

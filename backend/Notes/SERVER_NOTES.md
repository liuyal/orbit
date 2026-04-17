# Backend Optimization Findings
**Project:** Orbit API  
**Author:** Jerry  
**Last Updated:** 2026-04-17  

---

## Overview

This document summarizes all optimization findings and recommendations for the Orbit FastAPI backend.  
Findings are categorized by **priority** and cover correctness bugs, performance issues, and general improvements.

---

## ✅ Completed Optimizations (as of 2026-04-16)

All route-level optimizations have been applied. See `routes/OPTIMIZATION_NOTES.md` for the full breakdown.

Key improvements applied:
- `asyncio.gather` used throughout to parallelize independent DB calls.
- `db.count()` replaces `db.find() + len()` everywhere.
- `{"_id": 1}` projection used for key generation — no full documents loaded.
- DB writes removed from GET handlers.
- Redundant re-fetches eliminated by reusing already-fetched documents.
- O(1) dict-keyed cache for runner status lookups.
- Batch `$in` queries replace N×2 individual `find_one` loops in `get_cycle_executions`.

---

## 🔴 Critical Issues (Fix Immediately)

### 1. Race Condition on Key Generation

**Files:** `routes/test_cases.py` → `create_test_case_in_project`  
**Files:** `routes/test_executions.py` → `create_execution_by_test_case_key`

**Problem:**  
Auto-key generation fetches all existing `_id`s, computes `max() + 1`, then inserts. Under concurrent requests,
two requests can read the same max and attempt to insert the same key — causing a duplicate key error.

**Fix:** Use MongoDB's atomic counter pattern with `findOneAndUpdate` + `$inc`:

```python
# Add to mongodb.py
async def get_next_sequence(self, db_name: str, sequence_name: str) -> int:
    result = await self._db_client[db_name]["counters"].find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    return result["seq"]
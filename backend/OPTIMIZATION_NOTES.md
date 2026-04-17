# Backend Route Optimization Notes

Complete analysis of every FastAPI endpoint across all route files.  
Last updated: 2026-04-16 (re-analysed after partial optimizations)

---

## `projects.py` — 5 endpoints

### `GET /tm/projects` → `get_all_projects` ✅ Optimized
- All project count queries run concurrently via `asyncio.gather` (inner coroutine per project, all projects gathered in one batch).
- Uses `db.count()` instead of `find` + `len()`.
- DB write removed from GET handler.

### `POST /tm/projects` → `create_project_by_key` 🟡 Remaining
- Still calls `get_project_by_key` for the duplicate existence check.
- `get_project_by_key` now fires 3 concurrent DB calls (project + 2 counts) — better than before, but still unnecessary for a simple existence check that only needs `find_one`.
- **Suggestion**: Replace `get_project_by_key` call with a direct `db.find_one` — only 1 DB call needed.

### `GET /tm/projects/{project_key}` → `get_project_by_key` ✅ Optimized
- Project fetch and both counts run concurrently via `asyncio.gather`.
- Uses `db.count()` instead of `find` + `len()`.
- DB write removed from GET handler.

### `PUT /tm/projects/{project_key}` → `update_project_by_key` 🟡 Remaining
- Still calls `get_project_by_key` for the existence check — triggers 3 concurrent DB calls, but only `find_one` is needed.
- Still uses `db.find` + `len()` for the 2 count queries — should use `db.count()`.
- Both count queries are sequential — should use `asyncio.gather`.
- **Suggestions**:
  - Replace `get_project_by_key` existence check with a direct `db.find_one`.
  - Replace `find` + `len()` with `db.count()`.
  - Run both count queries concurrently with `asyncio.gather`.

### `DELETE /tm/projects/{project_key}` → `delete_project_by_key` 🟡 Remaining
- Still calls `get_project_by_key` for existence check (3 concurrent DB calls, but only `find_one` needed).
- Force-delete path: 3 sequential independent `db.delete` calls.
- **Suggestions**:
  - Replace existence check with a direct `db.find_one`.
  - Run the 3 force-delete calls concurrently with `asyncio.gather`.

---

## `test_cases.py` — 6 endpoints

### `GET /tm/test-cases` → `get_all_test_cases` ✅ Good
- Single `db.find` + `natsorted` in-memory. No issues.

### `GET /tm/projects/{project_key}/test-cases` → `get_all_test_cases_by_project` 🟢 Low
- 2 sequential DB calls: find project → find test cases.
- **Suggestion**: Run both concurrently with `asyncio.gather`, validate project afterward.

### `POST /tm/projects/{project_key}/test-case` → `create_test_case_in_project` 🟡 Remaining
- Fetches project at top, then calls `get_all_test_cases_by_project` for key generation which does **another** project `find_one` — redundant.
- After creation, uses `db.find` + `len()` to update `test_case_count` — should use `db.count()` or just `+1`.
- **Suggestions**:
  - Query cycles directly instead of going through `get_all_test_cases_by_project` to avoid the redundant project check.
  - Replace post-create `find` + `len()` with `db.count()` or increment by 1.

### `DELETE /tm/projects/{project_key}/test-cases` → `delete_all_test_case_from_project` 🟢 Low
- Re-fetches project with `db.find_one` after deletion even though the `project` variable from the top is still valid and in scope.
- Uses `db.find` + truthy check for execution check when `db.count() > 0` is sufficient.
- **Suggestions**:
  - Reuse the already-fetched `project` variable.
  - Replace execution `find` + truthy check with `db.count() > 0`.

### `GET /tm/projects/{project_key}/test-cases/{test_case_key}` → `get_test_case_by_key` 🟢 Low
- 2 sequential DB calls: find project → find test case.
- **Suggestion**: Run both `find_one` calls concurrently with `asyncio.gather`, then validate.

### `PUT /tm/projects/{project_key}/test-cases/{test_case_key}` → `update_test_case_by_key` 🟡 Remaining
- Fetches project at top (1 `find_one`), then calls `get_test_case_by_key` for existence check which fetches project **again** — redundant third project lookup.
- **Suggestion**: Replace `get_test_case_by_key` call with a direct `db.find_one` for just the test case, since project is already verified.

### `DELETE /tm/projects/{project_key}/test-cases/{test_case_key}` → `delete_test_case_by_key` 🟡 Remaining
- Same redundant double project lookup issue as `update_test_case_by_key` above.
- After deletion, uses `db.find` + `len()` to recount test cases — should use `db.count()` or decrement.
- **Suggestions**:
  - Replace `get_test_case_by_key` check with a direct `db.find_one` for the test case.
  - Replace post-delete `find` + `len()` with `db.count()` or decrement by 1.

---

## `test_cycles.py` — 8 endpoints

### `GET /tm/projects/{project_key}/cycles` → `get_all_cycles_for_project` 🟢 Low
- 2 sequential DB calls: find project → find cycles.
- Note: a previous `asyncio.gather` optimization was reverted in the current code.
- **Suggestion**: Re-apply `asyncio.gather` for both queries, validate project afterward.

### `POST /tm/projects/{project_key}/cycles` → `create_cycle_for_project` 🟡 Remaining
- Fetches project at top, then calls `get_all_cycles_for_project` for key generation which does **another** project `find_one` — redundant.
- After creation, uses `db.find` + `len()` to count cycles — should use `db.count()` or `+1`.
- **Suggestions**:
  - Query cycles directly instead of going through `get_all_cycles_for_project`.
  - Replace post-create `find` + `len()` with `db.count()` or increment by 1.

### `GET /tm/cycles/{test_cycle_key}` → `get_cycle_by_key` ✅ Good
- Single `db.find_one`. Clean and minimal.

### `PUT /tm/cycles/{test_cycle_key}` → `update_cycle_by_key` ✅ Good
- One update + one re-fetch. Straightforward and efficient.

### `DELETE /tm/cycles/{test_cycle_key}` → `delete_cycle_by_key` ✅ Optimized
- Existence check with `find_one`, then `asyncio.gather` concurrently deletes the cycle and clears `test_cycle_key` on all linked executions.
- Data integrity issue resolved.

### `GET /tm/cycles/{test_cycle_key}/executions` → `get_cycle_executions` ✅ Optimized
- 2 sequential batch `$in` queries replacing the old N×2 individual `find_one` loop.
- In-memory O(1) dict merge.

### `POST /tm/cycles/{test_cycle_key}/executions` → `add_execution_to_cycle` 🟢 Low
- Cycle fetch and execution fetch are sequential but independent.
- Final re-fetch of cycle after update adds an extra round-trip.
- **Suggestions**:
  - Use `asyncio.gather` for the cycle and execution fetches.
  - Return the locally-modified `cycle_data` directly instead of re-fetching from DB at the end.

### `DELETE /tm/cycles/{test_cycle_key}/executions/{execution_key}` → `remove_executions_from_cycle` 🟢 Low
- Cycle fetch and execution fetch are sequential but independent.
- Final re-fetch of cycle after update adds an extra round-trip.
- **Suggestions**:
  - Use `asyncio.gather` for both fetches.
  - Return the locally-modified `cycle_data` directly instead of re-fetching from DB at the end.

---

## `test_executions.py` — 6 endpoints

### `GET /tm/projects/{project_key}/executions` → `get_all_executions_by_project` 🟢 Low
- 2 sequential DB calls: find project → find executions.
- **Suggestion**: Run both concurrently with `asyncio.gather`, validate project afterward.

### `DELETE /tm/projects/{project_key}/executions` → `delete_all_test_execution_by_project` ✅ Optimized
- Replaced N+M sequential loop writes with 3 concurrent bulk operations via `asyncio.gather`:
  - `update_many` resets all test cases.
  - `update_many` resets all cycles.
  - `delete` removes all executions.

### `GET /tm/projects/{project_key}/test-cases/{test_case_key}/executions` → `get_all_executions_by_test_case_key` 🟢 Low
- 3 sequential DB calls: find project → find test case → find executions.
- First 2 checks are independent.
- **Suggestion**: Run project and test case `find_one` concurrently with `asyncio.gather`, then fetch executions.

### `POST /tm/projects/{project_key}/test-cases/{test_case_key}/executions` → `create_execution_by_test_case_key` 🟡 Remaining
- Project and test case checks are sequential but independent.
- Calls `get_all_executions_by_project` for key generation, which re-checks project existence — redundant.
- Fetches **all execution documents** project-wide just to find the max key number.
- **Suggestions**:
  - Run project and test case `find_one` concurrently with `asyncio.gather`.
  - Query only `execution_key` fields (projection) instead of full documents for key generation.
  - Consider a counter field on the project document to avoid the full scan entirely.

### `GET /tm/executions/{execution_key}` → `get_execution_by_key` ✅ Good
- Single `db.find_one`. Clean and minimal.

### `PUT /tm/executions/{execution_key}` → `update_execution_by_key` 🟡 Remaining
- **6+ sequential DB calls**: check exists → update → re-fetch execution → fetch test case → update test case → fetch cycle → update cycle.
- The post-update re-fetch of execution is used only to get `test_case_key` and `test_cycle_key` — these were already available from the initial `get_execution_by_key` response body which is decoded but the data discarded.
- Test case fetch and cycle fetch are independent once keys are known.
- **Suggestions**:
  - Reuse execution doc from initial `get_execution_by_key` response to avoid the post-update re-fetch.
  - Run test case `find_one` and cycle `find_one` concurrently with `asyncio.gather`.
  - Reduces chain from 6+ sequential to ~4 with 2 parallel.

### `DELETE /tm/executions/{execution_key}` → `delete_execution_by_key` ✅ Good
- Fetches execution, conditionally updates linked test case, then deletes. Minimal and correct.

---

## `runners.py` — 2 endpoints ✅ No Action Needed

### `GET /runners/status` → `get_runners_status`
- Cache-only read. No DB calls.

### `GET /runners/status/{name}` → `get_runners_status_by_name`
- Linear scan over in-memory cache. Acceptable for small runner counts.
- Could use a dict-keyed cache for O(1) lookup if runner count grows large.

---

## `root.py` — 3 endpoints ✅ No Action Needed

### `GET /` → `root`
- Returns 204. No DB calls.

### `GET /api/{version}` → `root_api`
- Redirect only. No DB calls.

### `POST /api/{version}/reset-database` → `reset_database`
- Admin utility. Performance not a concern.

---

## Summary Table

| File | Endpoint Function | Status | Remaining Issue |
|---|---|---|---|
| projects.py | `get_all_projects` | ✅ Optimized | — |
| projects.py | `get_project_by_key` | ✅ Optimized | — |
| test_executions.py | `delete_all_test_execution_by_project` | ✅ Optimized | — |
| test_cycles.py | `delete_cycle_by_key` | ✅ Optimized | — |
| test_cycles.py | `get_cycle_executions` | ✅ Optimized | — |
| test_cases.py | `get_all_test_cases` | ✅ Good | — |
| test_executions.py | `get_execution_by_key` | ✅ Good | — |
| test_cycles.py | `get_cycle_by_key` | ✅ Good | — |
| test_cycles.py | `update_cycle_by_key` | ✅ Good | — |
| test_executions.py | `delete_execution_by_key` | ✅ Good | — |
| projects.py | `create_project_by_key` | 🟡 Remaining | Expensive existence check via `get_project_by_key` |
| projects.py | `update_project_by_key` | 🟡 Remaining | Expensive existence check + `find`+`len` for counts |
| projects.py | `delete_project_by_key` | 🟡 Remaining | Expensive existence check + sequential force-deletes |
| test_cases.py | `create_test_case_in_project` | 🟡 Remaining | Redundant project lookup + `find`+`len` for count |
| test_cases.py | `update_test_case_by_key` | 🟡 Remaining | Redundant project lookup via `get_test_case_by_key` |
| test_cases.py | `delete_test_case_by_key` | 🟡 Remaining | Redundant project lookup + `find`+`len` for count |
| test_cycles.py | `create_cycle_for_project` | 🟡 Remaining | Redundant project lookup + `find`+`len` for count |
| test_executions.py | `create_execution_by_test_case_key` | 🟡 Remaining | Sequential checks + redundant project lookup + full doc scan |
| test_executions.py | `update_execution_by_key` | 🟡 Remaining | 6+ sequential DB calls + avoidable re-fetch |
| test_cases.py | `get_all_test_cases_by_project` | 🟢 Low | 2 sequential independent DB calls |
| test_cases.py | `delete_all_test_case_from_project` | 🟢 Low | Redundant project re-fetch + `find` for existence check |
| test_cases.py | `get_test_case_by_key` | 🟢 Low | 2 sequential independent `find_one` calls |
| test_cycles.py | `get_all_cycles_for_project` | 🟢 Low | 2 sequential independent DB calls |
| test_cycles.py | `add_execution_to_cycle` | 🟢 Low | Sequential independent fetches + avoidable re-fetch |
| test_cycles.py | `remove_executions_from_cycle` | 🟢 Low | Sequential independent fetches + avoidable re-fetch |
| test_executions.py | `get_all_executions_by_project` | 🟢 Low | 2 sequential independent DB calls |
| test_executions.py | `get_all_executions_by_test_case_key` | 🟢 Low | 3 sequential DB calls, first 2 independent |
| runners.py | `get_runners_status_by_name` | 🟢 Low | Linear cache scan (only relevant at scale) |

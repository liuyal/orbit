# Backend Route Optimization Notes

Complete analysis of every FastAPI endpoint across all route files.  
Last updated: 2026-04-16 (re-analysed after all low-priority optimizations applied)

---

## `projects.py` — 5 endpoints

### `GET /tm/projects` → `get_all_projects` ✅ Optimized
- All project count queries run concurrently via `asyncio.gather` (inner coroutine per project, all projects gathered in one batch).
- Uses `db.count()` instead of `find` + `len()`.
- DB write removed from GET handler.

### `POST /tm/projects` → `create_project_by_key` 🟡 Remaining
- Calls `get_project_by_key` for the duplicate existence check — triggers 3 concurrent DB calls (project + 2 counts), but only a `find_one` is needed.
- **Suggestion**: Replace `get_project_by_key` call with a direct `db.find_one` — 1 DB call instead of 3.

### `GET /tm/projects/{project_key}` → `get_project_by_key` ✅ Optimized
- Project fetch and both counts run concurrently via `asyncio.gather`.
- Uses `db.count()` instead of `find` + `len()`.
- DB write removed from GET handler.

### `PUT /tm/projects/{project_key}` → `update_project_by_key` 🟡 Remaining
- Calls `get_project_by_key` for existence check — 3 concurrent DB calls, but only `find_one` needed.
- Still uses `db.find` + `len()` for 2 count queries — should use `db.count()`.
- Both count queries are sequential — should use `asyncio.gather`.
- **Suggestions**:
  - Replace existence check with a direct `db.find_one`.
  - Replace `find` + `len()` with `db.count()`.
  - Run both count queries concurrently with `asyncio.gather`.

### `DELETE /tm/projects/{project_key}` → `delete_project_by_key` 🟡 Remaining
- Calls `get_project_by_key` for existence check — 3 concurrent DB calls, but only `find_one` needed.
- Force-delete path: 3 sequential independent `db.delete` calls.
- **Suggestions**:
  - Replace existence check with a direct `db.find_one`.
  - Run the 3 force-delete calls concurrently with `asyncio.gather`.

---

## `test_cases.py` — 6 endpoints

### `GET /tm/test-cases` → `get_all_test_cases` ✅ Good
- Single `db.find` + `natsorted` in-memory. No issues.

### `GET /tm/projects/{project_key}/test-cases` → `get_all_test_cases_by_project` ✅ Optimized
- Project check and test cases fetch run concurrently via `asyncio.gather`.

### `POST /tm/projects/{project_key}/test-case` → `create_test_case_in_project` 🟡 Remaining
- Fetches project at top, then calls `get_all_test_cases_by_project` for key generation which does **another** project `find_one` — redundant.
- After creation, uses `db.find` + `len()` to update `test_case_count` — should use `db.count()` or `+1`.
- **Suggestions**:
  - Query test cases directly instead of going through `get_all_test_cases_by_project`.
  - Replace post-create `find` + `len()` with `db.count()` or increment by 1.

### `DELETE /tm/projects/{project_key}/test-cases` → `delete_all_test_case_from_project` ✅ Optimized
- Project check and execution count run concurrently via `asyncio.gather`.
- Uses `db.count() > 0` instead of `find` + truthy check.
- Reuses already-fetched `project` variable instead of re-querying after deletion.

### `GET /tm/projects/{project_key}/test-cases/{test_case_key}` → `get_test_case_by_key` ✅ Optimized
- Project and test case `find_one` calls run concurrently via `asyncio.gather`.

### `PUT /tm/projects/{project_key}/test-cases/{test_case_key}` → `update_test_case_by_key` 🟡 Remaining
- Fetches project at top (1 `find_one`), then calls `get_test_case_by_key` for existence check which fetches project **again** — redundant third project lookup.
- **Suggestion**: Replace `get_test_case_by_key` call with a direct `db.find_one` for just the test case.

### `DELETE /tm/projects/{project_key}/test-cases/{test_case_key}` → `delete_test_case_by_key` 🟡 Remaining
- Same redundant double project lookup via `get_test_case_by_key`.
- Uses `db.find` + truthy check for execution check — `db.count() > 0` is sufficient.
- After deletion, uses `db.find` + `len()` for recount — should use `db.count()` or decrement.
- **Suggestions**:
  - Replace `get_test_case_by_key` check with a direct `db.find_one`.
  - Replace execution `find` + truthy check with `db.count() > 0`.
  - Replace post-delete `find` + `len()` with `db.count()` or decrement by 1.

---

## `test_cycles.py` — 8 endpoints

### `GET /tm/projects/{project_key}/cycles` → `get_all_cycles_for_project` ✅ Optimized
- Project check and cycles fetch run concurrently via `asyncio.gather`.
- Uses `[::-1]` for reversal.

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
- Existence check with `find_one`, then `asyncio.gather` concurrently deletes cycle and clears `test_cycle_key` on all linked executions.
- Data integrity issue resolved.

### `GET /tm/cycles/{test_cycle_key}/executions` → `get_cycle_executions` ✅ Optimized
- 2 sequential batch `$in` queries replacing the old N×2 individual `find_one` loop.
- In-memory O(1) dict merge.

### `POST /tm/cycles/{test_cycle_key}/executions` → `add_execution_to_cycle` ✅ Optimized
- Cycle and execution fetched concurrently via `asyncio.gather` using direct `db.find_one` (no JSONResponse overhead).
- Both DB writes (cycle update + execution update) run concurrently via `asyncio.gather`.
- Eliminated end-of-function re-fetch — returns locally-modified `cycle_data` directly.

### `DELETE /tm/cycles/{test_cycle_key}/executions/{execution_key}` → `remove_executions_from_cycle` ✅ Optimized
- Same improvements as `add_execution_to_cycle`.

---

## `test_executions.py` — 6 endpoints

### `GET /tm/projects/{project_key}/executions` → `get_all_executions_by_project` ✅ Optimized
- Project check and executions fetch run concurrently via `asyncio.gather`.

### `DELETE /tm/projects/{project_key}/executions` → `delete_all_test_execution_by_project` ✅ Optimized
- 3 concurrent bulk operations via `asyncio.gather`:
  - `update_many` resets all test cases.
  - `update_many` resets all cycles.
  - `delete` removes all executions.

### `GET /tm/projects/{project_key}/test-cases/{test_case_key}/executions` → `get_all_executions_by_test_case_key` ✅ Optimized
- Project and test case `find_one` checks run concurrently via `asyncio.gather`, then executions fetched.

### `POST /tm/projects/{project_key}/test-cases/{test_case_key}/executions` → `create_execution_by_test_case_key` 🟡 Remaining
- Project and test case checks are still sequential — can be concurrent.
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
- The post-update re-fetch of execution is used only to get `test_case_key` and `test_cycle_key` — already available from the initial `get_execution_by_key` response body but discarded.
- Test case fetch and cycle fetch are independent once keys are known.
- **Suggestions**:
  - Reuse execution doc from initial `get_execution_by_key` response to eliminate the post-update re-fetch.
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
| test_cases.py | `get_all_test_cases_by_project` | ✅ Optimized | — |
| test_cases.py | `delete_all_test_case_from_project` | ✅ Optimized | — |
| test_cases.py | `get_test_case_by_key` | ✅ Optimized | — |
| test_cycles.py | `get_all_cycles_for_project` | ✅ Optimized | — |
| test_cycles.py | `delete_cycle_by_key` | ✅ Optimized | — |
| test_cycles.py | `get_cycle_executions` | ✅ Optimized | — |
| test_cycles.py | `add_execution_to_cycle` | ✅ Optimized | — |
| test_cycles.py | `remove_executions_from_cycle` | ✅ Optimized | — |
| test_executions.py | `get_all_executions_by_project` | ✅ Optimized | — |
| test_executions.py | `delete_all_test_execution_by_project` | ✅ Optimized | — |
| test_executions.py | `get_all_executions_by_test_case_key` | ✅ Optimized | — |
| test_cases.py | `get_all_test_cases` | ✅ Good | — |
| test_cycles.py | `get_cycle_by_key` | ✅ Good | — |
| test_cycles.py | `update_cycle_by_key` | ✅ Good | — |
| test_executions.py | `get_execution_by_key` | ✅ Good | — |
| test_executions.py | `delete_execution_by_key` | ✅ Good | — |
| runners.py | `get_runners_status` | ✅ Good | — |
| runners.py | `get_runners_status_by_name` | ✅ Good | — |
| root.py | `root` | ✅ Good | — |
| root.py | `root_api` | ✅ Good | — |
| root.py | `reset_database` | ✅ Good | — |
| projects.py | `create_project_by_key` | 🟡 Remaining | Expensive existence check via `get_project_by_key` (3 calls → 1 needed) |
| projects.py | `update_project_by_key` | 🟡 Remaining | Expensive existence check + sequential `find`+`len` for counts |
| projects.py | `delete_project_by_key` | 🟡 Remaining | Expensive existence check + sequential force-deletes |
| test_cases.py | `create_test_case_in_project` | 🟡 Remaining | Redundant project lookup + `find`+`len` for count |
| test_cases.py | `update_test_case_by_key` | 🟡 Remaining | Redundant project lookup via `get_test_case_by_key` |
| test_cases.py | `delete_test_case_by_key` | 🟡 Remaining | Redundant project lookup + `find`+`len` for count |
| test_cycles.py | `create_cycle_for_project` | 🟡 Remaining | Redundant project lookup + `find`+`len` for count |
| test_executions.py | `create_execution_by_test_case_key` | 🟡 Remaining | Sequential checks + redundant project lookup + full doc scan for key |
| test_executions.py | `update_execution_by_key` | 🟡 Remaining | 6+ sequential DB calls + avoidable re-fetch |

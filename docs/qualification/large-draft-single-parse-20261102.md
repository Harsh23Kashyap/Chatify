# Large draft single-parse qualification, 2026-11-02

Scope: avoid the second SafeLoader parse in BuildDrafts.put, retaining raw declared top-level sections before validation removes extras or adds schema defaults. validate(text) still returns the same normalized mapping. New validate_declared(text) returns that mapping and the original section set only after all existing validation checks pass. No loader, scrub, persistence, get/reopen, HTTP, model, source or UI changes.

## Evidence

- New real save single-parse assertion failed on baseline for both inferred and explicit app scope. New declared-scope API tests were absent on baseline. Existing tests and assertions retained unchanged.
- An initial new appearance fixture incorrectly used a top-level accent setting. Corrected that fixture to valid appearance: {}, not a product change.
- Focused existing and new tests: 87 passed, 26 subtests.
- Full Python suite split into eight serial groups: see companion qualification JSON and logs.
- Exact before/after saved records and restart get results compared for eight cases, excluding timestamps only: original large payload, app-only, appearance-only, empty config, credential/numeric settings, scope mismatch, invalid fields and rejected anchors. Exact byte equality of the combined results. This verifies backward equivalence, not independent semantic answer quality.
- Saved original payload: 1,920,249 bytes, SHA256 abd4472d603cb36390e1dadde36d21e2b6924ce936b1a88452d567aaacb8a003. Normal local saves 3.329/3.317 seconds versus prior 4.233/4.492. Small local samples, not hosted latency.
- Actual local HTTP save with intentionally lost response then same-ID sequential retry: 3.259/3.185 seconds; one owner-scoped record/file, exact original logo and scope preserved, parent config and secret store unchanged, credentials excluded. Not concurrent writes, ID-less retry, hosted persistence or browser reload recovery.
- No new provider, model, external source or hosted call. No UI change, so no new pixel result claimed. Original semantic acceptance, hosted pilot and Brave key coverage remain unqualified.

# First full browser run: red, not qualified

Run: https://github.com/Harsh23Kashyap/Chatify/actions/runs/40462732221
Head ee5f519, completed in 17m44s. Seven browser shards passed, five failed; syntax/package passed. All twelve actual raw case-output summaries now collected: 471 scripts, 500 executions, 494 passed, six failed. The five failed shards account for 213 executions: 207 passed, six failed.

Corrections in this commit:
- Install missing Caladea font and pdftotext (poppler-utils) in the Ubuntu browser runner.
- Source-summary event harness waits for connected source overview, not just early settings names/motion state. Controlled held-config diagnostic proves the old predicate is true before the saved-source listener exists; after config is released, the row is generated. Two complete local six-combination runs pass with this readiness condition.
- Guide acceptance reflects the independently existing 13-step guide and current headings. Bounds compare simultaneous frame-local rectangles, retaining the same containment assertions. The guide really changed saved simple/advanced mode: restore its original mode on exit. Two full local responsive guide runs pass after the product fix.
- ZIP drop acceptance navigates through the current manual-settings UI before opening the portable section. Complete local drop run passes.

Still unexplained and NOT repaired: workspace_late_deploy_plan_browser.cjs sometimes cannot find Prepare deployment plan after its synthetic open event. CI failure and another fresh local solo failure retained. A local pass and tentative actual-navigation pass do not establish its cause. No assertion, timeout, retry policy, or product behavior changed for this case. Further diagnosis continues; the next full run remains a genuine fail-closed test.

All logs here contain only allowlisted offline case output, never full runner environment logs. Failed diagnostic experiments are retained too. No hosted deployment, restart, upgrade, or release was performed.

## Follow-up: sixth failure captured and corrected locally

Instrumented failure records settings.js/pipeline.js initial Setup events, the test synthetic Deploy event, then panels.js boot rebuilding navigation and dispatching Setup again. The synthetic event leaves location.hash at #sec-finish, so rebuildMenu correctly restores Setup and removes Prepare deployment plan. This is a harness navigation race, not evidence of a late-response product failure. The test now uses actual manual Deploy navigation, which updates the route to #sec-workspace-deploy. Local complete case passes. A separate diagnostic forces that same navigation rebuild immediately after selecting Deploy; the full delayed-response/draft/focus case still passes. All assertions and timeouts remain unchanged. Historical failures and first unsuccessful mechanism probe remain preserved.

The above paragraph supersedes the earlier unresolved status, without erasing it. The corrected full CI on 9a17697 still contains the original sixth test, because changing it mid-run would cancel that run. Its terminal result will be retained before pushing this additional correction.

# First full browser run: red, not qualified

Run: https://github.com/Harsh23Kashyap/Chatify/actions/runs/40462732221
Head ee5f519, completed in 17m44s. Seven browser shards passed, five failed; syntax/package passed. The five failed shard summaries total 213 executions: 207 passed, six failed. The complete manifest expands 471 scripts to 500 executions, but passed-shard logs still need independent count collection.

Corrections in this commit:
- Install missing Caladea font and pdftotext (poppler-utils) in the Ubuntu browser runner.
- Source-summary event harness waits for connected source overview, not just early settings names/motion state. Controlled held-config diagnostic proves the old predicate is true before the saved-source listener exists; after config is released, the row is generated. Two complete local six-combination runs pass with this readiness condition.
- Guide acceptance reflects the independently existing 13-step guide and current headings. Bounds compare simultaneous frame-local rectangles, retaining the same containment assertions. The guide really changed saved simple/advanced mode: restore its original mode on exit. Two full local responsive guide runs pass after the product fix.
- ZIP drop acceptance navigates through the current manual-settings UI before opening the portable section. Complete local drop run passes.

Still unexplained and NOT repaired: workspace_late_deploy_plan_browser.cjs sometimes cannot find Prepare deployment plan after its synthetic open event. CI failure and another fresh local solo failure retained. A local pass and tentative actual-navigation pass do not establish its cause. No assertion, timeout, retry policy, or product behavior changed for this case. Further diagnosis continues; the next full run remains a genuine fail-closed test.

All logs here contain only allowlisted offline case output, never full runner environment logs. Failed diagnostic experiments are retained too. No hosted deployment, restart, upgrade, or release was performed.

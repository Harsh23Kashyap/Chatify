# Qualification Rerun Protocol (RECONSTRUCTED 2026-10-26 ~16:10 IST)

RECONSTRUCTION NOTICE: the original of this document (committed locally as a1bffc3) was
lost with the sandbox rebuild of 16:06 along with all rerun artifacts (results.tsv rows,
per-test logs). This file was reconstructed from the agent transcript record. No lost test
result is counted as a pass: the entire rerun is being re-executed against this protocol,
and only rows in the NEW results.tsv (appended to this directory when complete) qualify.

## Scope and boundary (source-backed)
Census window (09:09-13:33): exactly 2 app-code commits, 091aaa9 (settings.js 11:09) and
8b6f43a (appbuilder.js 11:17), BOTH affecting only chatify/web/settings.html (grep-verified).
Boundary rule: tests that load settings.html whose latest census-window PASS in
tests/census/2026-10-26/results.tsv predates 11:17 (8b6f43a) at census close 13:33.
Re-derived 16:08 from the PUSHED census results.tsv (a8ce3fd): 115 keys; the STRICT pair
(question-nav, sidebar_profile_browser; strict-seed fixture on 8145, not settings.html
grep-visible) is added explicitly -> 117-key rerun set. The original (lost) boundary list
was 116 keys; the 1-key delta is an alias artifact (sidebar_secondary_labels_browser alias
of sidebar_secondary_labels_motion_browser, PASS 13:13, coverage-valid, stability-only) and
cannot be diffed further because the original list is lost. The executed set is a superset.
Disjoint partition at census close: 469 census keys = valid-as-is + rerun set.

## Phases
1. Slice batches A/B/C (106 keys) via pw-runner/slice.sh, 2 lanes, TSV rows, per-test logs.
2. builder_apply_saved_e2e_browser solo with CHATIFY_FIXTURE_YAML=tests/fixtures/builder-trip.yaml
   (ONLY test reading that env; trip yaml has 3 api_suggestions, complete has 2; the
   Offline Trip name + 3-suggestion contract are versioned in the test since 1e4a4a2;
   fixture FILE reconstructed at aa2ca8c -> label: reconstructed-fixture/mock-path coverage).
3. builder_mounted_preview_browser solo against fixture on 8142 (literal goto ignores env).
4. COMBO: 4 button-inventory tests x 4 combos (RELEASE_WIDTH 320|1280 x RELEASE_MOTION
   no-preference|reduce; press_feedback also RELEASE_LEVEL=full). One TSV row per combo.
5. BRAND pair vs builder_brand_retry_fixture_server.py on 18827.
6. STRICT pair vs strict_ui_fixture.py on 8145.
7. appearance_scroll_audit_browser x 4 combos solo (CHATIFY_AUDIT_COMBO W:M).
8. STABILITY: 11 tests x 5 consecutive solo PASSes (see below).

## Verdict rules (per main 13:53/13:59, carried verbatim)
- A solo PASS after a failure does NOT itself prove contention or qualify a failed key.
- Establish the failure mechanism from evidence (fixture contents, git history, logs) or
  retain as unexplained intermittent and run repeatability checks (5 consecutive solo PASS).
- Browser-closed failures need attribution to actual shared lifecycle events, not signature.
- Preserve the original assertion/contract unless source evidence justifies a harness fix.
- All FAIL rows are preserved forever; latest-row supersedes for status only.
- A fixture reconstructed from the same test's assertions is self-consistent harness
  coverage, NOT independent validation: label "reconstructed-fixture/mock-path coverage".

## Stability set (11)
Entered at 1/5 from run-1 solos (those artifacts lost; counts restart at 0/5 in the
re-execution): config_containment_browser, config_design_batch_browser,
builder_checklist_keyboard_motion_browser, builder_keep_current_runtime_motion_browser,
builder_mark_reviewed_motion_browser, builder_whole_dashboard_status_motion_browser,
additional_fields_newer_edits_browser (all unexplained intermittents from run 1);
plus deployment_long_configuration_geometry_browser, appearance_navigation_audit_browser
(pristine boot per repeat), builder_whole_dashboard_fontstress_browser,
sidebar_secondary_labels_motion_browser (historical WATCH keys).

## Run-1 incident dispositions (transcript record; being re-verified by re-execution)
- builder_apply_saved_e2e 2!==3: harness fixture-routing (trip vs complete yaml).
- builder_mounted_preview: harness routing (literal 8142 goto).
- 7 unexplained intermittents (solo-PASSed, mechanism unestablished) -> stability.

# Flake qualification log (release-gated)

Protocol (main 10:00 IST): flakes do not count as clean qualified passes for release until root cause/repeatability assessed. Flag stays in final summary. No "no defect" claims.

## builder_whole_dashboard_fontstress_browser.cjs - FLAKY-OPEN
Assertion: `.builder-remaining-work` scrollHeight>clientHeight && scrollTop>0 after focus+End (keyboard-scroll contract, a11y).
Observed sequence (2026-10-26, apps/minimal@8765, solo unless noted):
1. FAIL lane-contended (2-lane slice) - null .height TypeError was the OTHER test; this one: assertion false at 3rd combo
2. FAIL solo-uncontended ~13s - assertion false, died in 1280 combo group
3. PASS probe-instrumented copy - all 4 combos, margins sh=541/138 ch=67 st=362/329/53/48, activeElement=true
4. PASS solo 22s
5-9. PASS x5 consecutive solo (10:07-10:08, each 22-23s)
Distribution: 2 fail / 8 pass. Both failures in 1280 combos (thinnest scroll margin). Failing runs die early (~13s vs 22s passing).
Root cause: OPEN. Hypothesis (unverified): poll-repaint scroll-restore timing in paintJob readingState capture, or font-metric timing after injected monospace style tag.
Gate: excluded from release-qualifying pass until main rules qualified.

## deployment_long_configuration_geometry_browser.cjs - FLAKY-OPEN
Assertion: getByLabel('Target / service') visible after clicking #menu a[href="#sec-workspace-deploy"] (Deploy panel open contract).
Observed sequence (2026-10-26, apps/minimal@8765):
1. FAIL lane (49s) - 63x "resolved to hidden <input aria-label='Target / service'>"
2. FAIL solo-uncontended - same hidden-input failure
3. PASS probe (instrumented flow copy) at 1280:no-preference - input visible, Deploy h3 rendered
4. PASS probe at 320:no-preference - visible
5. PASS solo-uncontended (unmodified test)
Distribution: 2 fail / 3 pass. Failure mode: input present in DOM but hidden (zero client rects) for the full 30s wait - Deploy panel content rendered into a non-visible container; consistent within a run, differs between runs.
Root cause: OPEN. Hypotheses (unverified): showSection('workspace-deploy') target-section resolution timing; note #sec-workspace-deploy id itself does not exist in DOM (probe secDisplay null) - the nav hash and the section container differ, and which container stays visible may depend on click-vs-init ordering.
Gate: excluded from release-qualifying pass until main rules qualified.

### deployment flake - runtime evidence (10:42-10:44, instrumented copies, assertions unchanged)
Captured failing run DIAG (1280, no-preference): bodies:1 panels:1, input present with 0 client rects. Ancestor chain computed styles:
INPUT inline-block/visible/1 -> LABEL block -> .workspace-body block -> #workspacePanel block -> #sec-finish block opacity:0.7 (cc-settings-group-in animation mid-flight) -> #col flex -> **.layout display:none** -> .card -> body('cfgtop-builder settings-tabs settings-workspace-operation', NO simple class).
Key facts: exactly one .workspace-body and one #workspacePanel (no duplicates); section correctly active; the hiding ancestor is the top-level .layout grid with computed display:none. No CSS rule hides .layout for this body-class state (verified settings.css/settingstabs.css/motion.css); splitters.js only sets width custom properties. The opacity:0.7 mid-animation at DIAG time (after a 30s wait) shows a showSection/panel-entry ran LATE - consistent with delayed menu/showSection execution rather than a stable wrong-state. Next step: timing-instrumented capture (perf.now at goto/waitForFunction/click + MutationObserver on body class and .layout computed display) to identify who hides .layout and why it resolves late. Hypothesis (unverified): async menu build / late init showSection ordering vs test click timing.

### deployment flake - ROOT CAUSE PROVEN + FIXED (11:00-11:08)
Mechanism (runtime-proven, capture /tmp/diag2_run41.log pattern): buildMenu() rebuilds the entire nav (m.replaceChildren()) on every settings render; during boot, repeated renders detach the previously-built menu links. A click dispatched on a link detached moments before (test automation resolving a locator across a rebuild) fires the link's own onclick (showSection runs; settings-workspace-operation appears) but the event never reaches document - so settingstop.js's delegated capture listener (line 20, "navigation into a manual section opens the Manual view") never calls set('manual'). Body keeps cfgtop-builder; rule settingstabs.css `body.settings-tabs.cfgtop-builder .layout{display:none!important}` hides the whole manual layout incl. #sec-finish; the Target/service input stays invisible and the 30s waitFor times out. Evidence: PRECLICK conn=false inMenu=false; capSaw=null (no document capture); POSTCLICK body still cfgtop-builder with workspace-operation set; probe re-click on the CURRENT link flipped cfgtop-manual and .layout to grid.
Fix (product, assertions untouched): settings.js nav-link onclick now switches to Manual view itself (window.CCSettingsTop?.set('manual'); pre-settingstop fallback persists cc_cfg_top_v1=manual for init to honor). Real-user impact of the old code: a click landing during a boot-time rebuild could activate a section while the Manual layout stayed hidden (dead first click, self-healed on second).
Verification: unmodified deployment_long_configuration_geometry_browser.cjs solo 11/11 PASS with the fix present (3/3 on the exact final code). NOT fixed: the underlying boot-time rebuild churn (buildMenu DOM rebuild per render) remains; a guarded-rebuild attempt was reverted after a regression in appearance_navigation_audit (guarded path skipped tail re-activation). 
Distribution update: deployment test now 2 fail (pre-fix) / 14 pass (3 pre-fix + 11 post-fix). FLAKY-OPEN -> FIXED-PENDING-FULLPASS (final qualified status waits the full 469 hosted/local rerun).
### NEW INTERMITTENT CANDIDATE: appearance_navigation_audit_browser.cjs (320, simple mode)
Passed census 08:56. Failed 2/2 solo today (11:05 fixed code, 11:07 pristine HEAD) - NOT caused by the deployment fix (fails on unmodified HEAD too). No product code changed between 08:56 and now (only census docs). Assertion: strictEqual actual 'true' expected 'false' after "Preset initial viewport" log. Root cause OPEN; needs qualification distribution + isolation next. Kept OUT of census PASS/FAIL counts until qualified (latest census row stays PASS from 08:56; flagging separately per no-clean-claim rule).

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

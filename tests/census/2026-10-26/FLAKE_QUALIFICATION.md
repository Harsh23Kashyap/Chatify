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
Passed census 08:56. Failed 2/2 solo today (11:05 fixed code, 11:07 pristine HEAD) - NOT caused by the deployment fix (fails on unmodified HEAD too). No product code changed between 08:56 and now (only census docs). Assertion: strictEqual actual 'true' expected 'false' after "Preset initial viewport" log. Root cause OPEN; needs qualification distribution + isolation next. MAIN RULING 11:10: explicitly FLAKY-OPEN in the qualification list - the retained 08:56 census PASS row does NOT qualify for release gate; final census gate cannot ignore the later 2/2 solo failures. Census traversal row retained per latest-row rule, but the per-case coverage-vs-qualification list shows this case OPEN until root-caused, fixed, and re-passing.

### fontstress flake - ROOT CAUSE PROVEN + FIXED (11:14-11:16)
Mechanism (runtime-proven): .builder-remaining-work scrolls with smooth behavior under no-preference motion (reduce-motion forces auto). End-key starts a smooth scroll; the build-status poll (1s cadence while running) calls paintJob, which detached the node (metrics.replaceChildren) and restored a scrollTop captured BEFORE the scroll produced frames - canceling the in-flight scroll and stomping scrollTop back to 0. Deterministic replication: capture-detach-restore during a smooth scroll -> final scrollTop 0 vs destination 21px; no-detach control -> 21 ({max:21,captured:0,afterDetachRestore:0,control:21}). Real-user impact: a poll landing mid-scroll canceled the user's scroll of the Remaining-work region.
Fix (product, assertions untouched): appbuilder.js paintJob now keeps the existing .builder-remaining-work node in place when its text is unchanged (surgical metrics rebuild around it; no detach, no scrollTop write, no focus steal). Content-changed path keeps the prior replace+restore behavior.
Verification: post-fix real-path probe - smooth scroll survives real 1s polls to destination ({max:21,afterRealPolls:21,focused:true}); unmodified builder_whole_dashboard_fontstress_browser.cjs solo 4/4 PASS (plus the deterministic mechanism probe). Distribution: 2 fail (pre-fix) / 8 pass (pre-fix) + 4 pass (post-fix). FLAKY-OPEN -> FIXED-PENDING-FULLPASS.

## emoji_runtime_quiet_motion_browser — TEST-OBSERVATION RACE (repaired, not a product bug)

Observed: getAnimations() empty at assert time → 1280/none/opening FAIL; lane contention also failed combo 1.
Root cause (verified): anims:1 at click, anims:0 immediately after — the 160ms default-fill entrance
animation FINISHES and drops out of getAnimations() before the assert's evaluate lands on a slow
sandbox. Diag copy with one extra evaluate passed all 12 combos; product behavior (animation plays,
pausable, quiet modes cancel motion) intact.
Repair (contract unchanged): addInitScript wraps Element.prototype.animate to keep records;
assertion uses live animation if present, else the most recent completed record, and pause() +
currentTime=40 rewinds it into getAnimations() so the product's quiet-mode cancel path is still
exercised. PASS 3/3 solo + 1/1 through lane path.

## Lane-contention transients (12:02-12:04 batch) — evidence kept, no product bug

1. hero_motion_audit_browser (11:40 lane FAIL, 4s): empty computed animation names under reduce.
   Evidence: probe (same Chrome, same page) showed animation:none on every hero child under
   reduce; uncontended solo rerun PASS (11:42). Contention artifact.
2. metadata_geometry_audit_browser (12:02 lane FAIL, 35s): 30s locator timeout
   [data-workspace-field="app.id"] under 2-lane contention; uncontended solo rerun PASS in 8s (12:03).
3. mobile_a11y_current_browser (12:03 lane FAIL, 11s): axe returned a violation array mid-run under
   contention; uncontended solo rerun completed the full 41s scan with zero violations (12:04 PASS).
Protocol unchanged: lane FAILs are never claimed as product FAILs until an uncontended solo rerun
confirms; solo PASS supersedes via latest-row. These three are logged here rather than silently
dropped so the qualification list can re-examine them if any recurs.

## sidebar-profile (13:08 lane FAIL 7s, TimeoutError #list .item) — fixture routing, not product

Root cause: positional seeded-chat assertions (STRICT family per map; test honors
CHATIFY_TEST_URL). Generic apps/minimal has no seeded chats -> empty #list.
Rerun against strict fixture (strict_ui_fixture.py bound 8765): PASS 3s (13:09:04).
Latest-row PASS supersedes. settings_finder_clarity 12:54 FAIL = ERR_CONNECTION_REFUSED
(harness boot race after prior call's kill); solo PASS 12:55. Evidence retained, no product defect.

## sidebar_secondary_labels_motion (13:12 lane FAIL 4s) — lane timing transient, watched

getAnimations() returned [] at assert (element's 120ms entrance with 180ms delay read after
completion under lane shift; same observation-race family as emoji_runtime_quiet). Uncontended
solo rerun PASS 30s (13:13:30), latest-row supersedes. WATCH: if this recurs in a solo/full-run
context, apply the emoji-style race-free observation repair (record via animate wrapper +
pause/currentTime rewind) rather than rerunning forever.

## Addendum 2026-10-26 20:20 IST - color_feedback_browser.cjs RECLASSIFIED (harness observation-race, mechanism resolved)

CORRECTION (supersedes earlier node-identity diagnosis): the preserved original FAIL logs
(rerun_logs/color_feedback_browser.log = lane run, .solo.log = uncontended solo) both fail at
line 2 col 2156 = `assert.equal(fail.animations.some(a=>a.duration===160), motion==='no-preference')`
(actual false, expected true). HEX/SWATCH line counts place both failures in no-preference combos
(lane: 320/no-preference; solo: 1280/no-preference). The node-identity asserts (fail.same, fail.status),
the 'Fail 1.0:1' text assert, host-animation count, transform and focus asserts all PASSED in the
failing snapshots. Any earlier claim (mine) that the failures were node-identity losses is withdrawn;
the originals are preserved unchanged in rerun_logs/ and results.tsv.

Mechanism (source-backed): settings.js pvExtra() creates the 160ms row-status fade synchronously in
the hex input handler (setv is synchronous; rows created once behind the dataset.sample!=="colors"
guard and updated in place). The pre-repair test sampled live getAnimations() after waitForTimeout(30)
plus a cross-process evaluate round trip. Each changed() also re-renders the same-process iframe
preview (pushPreview), occupying the shared main thread. When the sample landed >160ms after
animation creation, the finished animation was no longer listed -> false FAIL exactly in
no-preference combos (reduce combos expect absence and pass trivially). Consistent with the observed
lane FAIL + solo FAIL + solo2 PASS distribution under slow-regime timing. Same family as the accepted
builder_keep_current_removal_motion 120ms race (commit da1afdc).

Harness repair (precedent 486baf4, pass-through, no timing/playback change): an
Element.prototype.animate wrapper records original calls (window.__anims) and returns the original
Animation. The 160ms assert now reads recorded calls targeted at the asserted row
(a.effect.target===n) created after a pre-fill mark (window.__animMark). Unmodified-runtime
assertions retained: 'Fail 1.0:1' text, node identity, host getAnimations()===0, transform, focus,
swatch transition durations, calm-gating (0 animations). ADDED unmodified natural-completion check:
after the existing waitForTimeout(400), the row's live getAnimations() must no longer contain a 160ms
animation (verifies natural finish/removal). Pre-repair test preserved:
rerun_logs/color_feedback_browser.cjs.pre-repair.bak.

Target/mark discrimination verified empirically (rerun_logs/color_feedback_target_probe.log):
3 pre-mark animations correctly excluded; 7 post-mark animations recorded, all on .cc rows, exactly
2 targeting the asserted first row (bg-fill round: later cancelled by the ink-round pvExtra, playState
idle = product-correct supersede; ink-fill round: finished naturally within 160ms). Without the
row-target filter, sibling rows' recorded animations could satisfy the assert; with it, the assert
measures the same row the original live sampling measured.

Repeatability: repaired test 3 consecutive solo PASSes (30s/26s/27s,
rerun_logs/color_feedback_browser.repaired_solo{1,2,3}.log). Case remains in
stability_set.txt for the 5-consecutive-solo phase using the repaired file.

Scope: this classification covers THIS failure signature only. It is not a blanket absence of product
risk for color_feedback or any other case.

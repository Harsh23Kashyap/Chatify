# Final command checks, October27

- Unit discovery:1107 entries,1102 distinct IDs. Five repeated aliases resolve to test_buildjobs.Jobs methods imported by another test module.
- Resumable per-ID chunks:1104 actual executions,1102distinct IDs (two aliases repeated within a chunk),0failures,0errors,1skip.
- Alias occurrence verification:5additional executions,0failures/errors/skips. Total actualexecutions1109, distinctcoverage1102. This is per-ID chunk execution, not an uninterrupted unittest discovery lifecycle. Original monolithic discovery interrupted by120s command limit; no finalsummary, not reportedPASS.
- Skip reason: F1appassets absent fromcheckout (test_answer_depth.FormulaOneSources.test_fia_snapshots_have_original_links_and_real_text).
- node --check every top-level chatify/web/*.js:exit0. Syntaxcheck, NOT lint/typeanalysis.
- Python compileall -q chatify:exit0. Bytecompile, NOT typeanalysis.
- pip wheel . --no-deps:exit0,chatify_app-0.4.32-py3-none-any.whl,12967171bytes,sha25662e59b615a1b7425f679ef9829b14a8fa1a9d0bc3ee085ddcd93897bf0756ae3. Buildonly, notpublished/installmatrixqualification.
- No dedicated lint/typecheck configuration/command found in projectroot/second-level search. Do not report lint/typecheckPASSED.
- Runtime active-retirement quiet-transition fullmatrix coverage remainsBLOCKED/UNQUALIFIED; unit/build success doesn't override that gate.

## After phone-usability CSS adjustment

- Original screenshots in stills/ precede these changes; after-usability/ captures the revised toolbar and build header.
- mobile_toolbar_visibility_browser.cjs PASS at320/390/768/1280: all visible header buttons within toolbar bounds, keyboard traversal remains in viewport, Reading dialog opens, build menu toggles on phones.
- Mounted-preview test first failed because its hardcoded8142 server was not running. Preserved connection-error log. Identical test with URL changed only to current8765 server PASS at root and/chatify/ mounts. This is a current-server diagnostic, not a change to assertions.
- Configuration sample preview native wheel scrollTop0->291, scrollHeight479/client188: content is internally scrollable, not dead clipping.
- Fresh wheel after CSS: build exit0, hash recorded alongside the build log. Unit counts above refer to the pre-CSS revision; the affected browser checks were rerun separately.

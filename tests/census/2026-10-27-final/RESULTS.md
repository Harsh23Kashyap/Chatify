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

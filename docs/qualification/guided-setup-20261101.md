# Guided setup qualification - 1 November 2026

Local working branch only. No production deployment or main merge. This records acceptance evidence and gaps, not a release approval.

## Professor wireframe and user's follow-up matrix

| Requested behavior | Local implementation and evidence | Remaining limitation |
|---|---|---|
| Describe an app, then submit | Describe stage, single persistent Draft configuration footer; advanced section-only drafting collapsed | Actual selected-model complete build subsequently passed; see later checkpoint for limits |
| Clear progress during execution | Actual phase and completed/total counts; indeterminate bar for unmeasured operations; terminal success/failure and next action; status survives closing dialog on same page | No guarantee for closing browser tab; progress is not a percent estimate |
| Default sources and optional service checkboxes | Native public PubMed/arXiv/Crossref/Wikipedia choices; recommendation checkbox selection flows into saved source blocks | Unknown recommendations are inert, not silently executable |
| Distinguish free/default from paid services | No blanket equation of key-required with paid. Public-source labels, optional-account labels, provider documentation links | All provider pricing not requalified; no new paid plans/cards/accounts |
| Skip optional source instead of creating key | Inline Skip and checkbox removal; local revalidation before save | No automatic signup or key creation |
| Selected API key and code setup in one place | Inline save/test for supported native sources; Brave deterministic code template, fixed BRAVE_API_KEY binding independent of display name; code explicitly not executed | No saved Brave key, so Brave live call not qualified; exact reported Try it 'os error' still not recovered |
| Model/provider/key/test in same window | Explicit provider, model identifier, custom base URL, provider model discovery, save key and test controls | Actual gpt-4o-mini complete build and saved child runtime subsequently exercised; citation quality still not accepted |
| Default design review: logo, color, size, all OK | Expanded always-on preview; design fields include editable/removable logo URL, color/hex and text size. Unchanged draft can validate/save without required cosmetic edit | Broad aesthetic add/remove UX is field-driven, not a new feature-picker wizard |
| Add/remove sources and aesthetics later | Structured source add/remove, API selection, editable design fields, group keep-current/review; existing configuration controls retained | Generic advanced API/feature setup can remain manual |
| Taller dialog, no Expand/Compact toggle | 96dvh dialog, always-expanded preview, no toggle buttons; inspected actual desktop screenshots | Long model panel requires internal scroll |
| Stable rename/configuration | Native source IDs/key bindings fixed. Matching default heading follows app rename; deliberately customized heading is retained | Rename is not an instruction to rewrite all copy |
| Remove top Build navigation | Five page headers no longer show Build; direct route and Configuration Build with AI retained | Local only |
| Feature video choice | Selector uses actual feature manifest entries, selection updates video/poster/label, native media controls retained | No new media files |
| At least ten runs on various free APIs | Separate direct 14-run connectivity subcheck across five services; guided four-source inline tests -> validate/save/use/reload -> ten source-isolated child questions, cache_ttl=0 and remote HTTP trace | Offline declarative generation and mock runtime model. This proves source configuration/retrieval, not synthesis or full model build |

## Live retrieval findings

The initial arXiv query `all:habitat fragmentation` returned smart-home/navigation papers. The minimal fix scopes each ordinary query word: `all:habitat AND all:fragmentation`. Explicit field/Boolean queries and quoted phrases are preserved. A live comparison and the rerun child path returned forest-herb habitat-fragmentation studies. Negative controls cover single word, quoted phrase, explicit Boolean/field syntax and existing transient/permanent retry behavior.

Crossref can return title-only metadata, not article bodies. Several runs contained only 40-50 characters. Relevance and coverage must not be inferred from HTTP200 or nonempty evidence. Older papers were returned on non-recency queries. OpenAlex worked with the existing private key; the earlier keyless attempt was rate-limited and was not repeated. Temporary secret copy deleted. No live Brave call.

The guided uncached run traced 23 successful HTTP200 remote responses and one transient PubMed HTTPError followed by the connector's existing retry. Ten child questions returned evidence without final source_errors. No further live probes were made solely to raise a counter.

## Automated evidence

- Eight bounded unittest groups: 1,344 tests passed before the final small logo/label/rename/query refinements. Not a pytest/full browser-suite claim. Plain function tests are not collected by unittest; the two arXiv retry functions were also invoked directly.
- Latest focused HTTP/provider/query checks: 44 passed; explicit custom model/base HTTP regression independently passed after addition.
- Latest guided Brave browser case passed: offline generated draft, real parse/review/save/use, synthetic saved credential copied to child, stable rename key, base URL/model-list request contracts, logo add/clear and color/size edits.
- Review capabilities case passed at existing widths, retaining original source/edit/review/reopen assertions; only obsolete Expand/Compact assertions changed for the explicit no-toggle request.
- Jobs case passed partial/closed/retry/done states.
- Full browser suite remains open. Subsequent real model build/runtime evidence is recorded below, separately from semantic quality acceptance.

## Sources checked

- https://api-dashboard.search.brave.com/documentation/services/web-search
- https://api-dashboard.search.brave.com/documentation/guides/authentication
- https://api-dashboard.search.brave.com/documentation/quickstart
- https://api-dashboard.search.brave.com/documentation/pricing
- https://developers.openalex.org/guides/authentication
- https://developers.openalex.org/quickstart
- https://www.ncbi.nlm.nih.gov/books/NBK25501/
- https://info.arxiv.org/help/api/user-manual.html
- https://www.crossref.org/documentation/retrieve-metadata/rest-api/
- https://www.mediawiki.org/wiki/API:Etiquette

Evidence files accompany the task report separately. Synthetic-key fixtures never establish a live provider result.

## Later checkpoint: 21:29 IST

- Simplified first screen: description comes first, model connection starts collapsed, import/library/partial-scope controls are under Other setup options. One primary action notice replaces duplicate footer status. Detailed local/model/safety observations remain in Build checks and technical details. No safety checks removed.
- The initial real OpenAI build found a conflict: a brief explicitly requesting only the public PubMed source still hit the default three-to-five recommendation requirement. The minimal fix recognizes only an exact single-source restriction, rejects conflicting checkbox selections before a model call, and uses the existing confirmed-source contract. It does not infer a source from a topic or silently pad services. 68 contract tests passed.
- A new actual UI-selected gpt-4o-mini build then reached 31/31 done with no errors. Exact original 1.92MB generated YAML was reopened after the combined harness timeout, validated, saved and launched. Child retained OpenAI gpt-4o-mini and PubMed only. Actual model answer returned 11 PubMed evidence items and no source_errors. Generated helper code was never executed. Citation checker still flagged uncited lead/summary text; answer_verified remained false, not semantic-quality acceptance.
- Full pytest tooling installed. Current initial eight-group verdict: 1,376 passed, one skipped, one gallery default-owner redirect HTTP503 failure. That exact test passed its single isolated rerun, recorded as intermittent rather than erasing the original failure. Later source-contract and key-wiring additions require a fresh full-suite verdict.
- A second independently found Try it defect: native saved source keys lived in the private store but helper environment read only server environment variables. Canonical, explicitly declared source-key names now read the same native private store, with negative controls proving unrelated/undeclared saved keys are not injected. No arbitrary key-name guessing or full-store forwarding.
- Temp-folder/process PermissionError/OSError now gives an actionable startup error and does not claim a request ran. This is reproduced error-path coverage, not proof of the original device-specific os-error root cause. User has no screenshot; investigation proceeds without asking again.

## Regression follow-through: 21:38 IST

Current checkpoint initial parallel pytest result: 1,384 passed, one skipped, one gallery default-owner redirect HTTP503 failure. Gallery full file (16 tests) and its entire 28-file pytest group (148 tests) pass in sequential isolated execution. Keep the parallel failure classified as resource-sensitive/intermittent; no assertion weakened or product retry added.

Broader browser tests caught and fixed disclosure reachability after simplification: saved drafts and import remain reachable from review; routine edit status opens the checks disclosure, and final-retry failure remains visible even when the draft stage is hidden. Existing safety/model notes remain secondary, not deleted. Passing current cases include appbuilder_states, builder_apply_saved_e2e with axe, builder_final_failure, builder_import_route, keep-current singleflight, add-source singleflight and the guided native setup case. This is still not a full 481-script browser-suite verdict.

## Follow-through: 21:47 IST

Missing-model guidance now sits above the disabled Draft action. Final-only check failure does not say draft areas failed. Actual desktop screenshot reviewed. Draft loading/beforeunload/close/reopen/keyboard-loop, progress persistence, truthful progress, lifecycle, source planning, retry states, save/use navigation and remove-source singleflight pass on the current local branch. The latter two needed only opening the new secondary setup disclosure in their test interactions, with original assertions retained.

Advanced section scope's preserved 180ms animation was overridden by the generic settings disclosure animation after relocation. Specific CSS restores its original timing, retains reduced-motion and motion-none exceptions. All 17 scope choices retain the description, issue no calls merely by selection, and the original scope keyboard/menu geometry/timing assertions pass after opening both secondary disclosures. Current full 481-script browser verdict is still absent. No main merge, push or deploy.

## Bounded browser sweep: 22:10 IST

51 of the 53 builder/appbuilder/guided scripts have current passing orchestration logs. This is a scoped sweep, not all 481 scripts. Original conversation, full-app, job, studio lifecycle, native source setup, real save/use, review assets, explicit source planning, progress, brand retry, source singleflight, review accessibility and manual-checklist keyboard/focus cases pass. The studio case exposed a real CSS regression: the description override remained visible during a build. Scoped has-build hiding restores the previous contract. Actual desktop running and saved screenshots inspected.

Saved-library test interaction routes now open Other setup options before opening saved drafts; no original safety, geometry, focus or timing assertions removed. Video case now expects the explicitly requested 60-option feature selector instead of the superseded no-picker requirement; media error/retry, controls, pause during build and no implicit apply assertions pass.

Two scoped cases are not qualified: generic disclosure motion audit fails because final API details use their dedicated 140ms builder-api-enter animation rather than the older generic m-in animation; original assertion retained. Example motion levels printed its terminal PASS in the child log after the outer shell timeout, but the orchestration exit result was lost, so no completed pass claim. Both are distinct from citation quality and the earlier parallel pytest gallery503.

## Current sequential suite and remaining scope: 22:15 IST

Fresh all-eight-group sequential Python verdict at local checkpoint 30de87c: 1,385 passed, one skipped, 540 subtests passed, zero failures. This includes the gallery group with 148 passed. Earlier concurrent eight-group gallery HTTP503 is still recorded; sequential success does not establish parallel reliability. A prior 740-subtest summary was an arithmetic error; raw current logs sum to 540. Separate helper safety/key checks: 10 passed.

Example motion levels has now completed a clean orchestrated rerun across its default full width/motion matrix. The scoped builder/appbuilder/guided verdict is 52 of 53 current passing scripts. Generic disclosure motion audit still fails on the new final-API-specific animation versus older generic m-in expectation. No full 481-script browser verdict and no semantic answer-quality release claim.

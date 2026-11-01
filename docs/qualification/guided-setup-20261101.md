# Guided setup qualification - 1 November 2026

Local working branch only. No production deployment or main merge. This records acceptance evidence and gaps, not a release approval.

## Professor wireframe and user's follow-up matrix

| Requested behavior | Local implementation and evidence | Remaining limitation |
|---|---|---|
| Describe an app, then submit | Describe stage, single persistent Draft configuration footer; advanced section-only drafting collapsed | Real model-generated complete build not rerun after latest changes |
| Clear progress during execution | Actual phase and completed/total counts; indeterminate bar for unmeasured operations; terminal success/failure and next action; status survives closing dialog on same page | No guarantee for closing browser tab; progress is not a percent estimate |
| Default sources and optional service checkboxes | Native public PubMed/arXiv/Crossref/Wikipedia choices; recommendation checkbox selection flows into saved source blocks | Unknown recommendations are inert, not silently executable |
| Distinguish free/default from paid services | No blanket equation of key-required with paid. Public-source labels, optional-account labels, provider documentation links | All provider pricing not requalified; no new paid plans/cards/accounts |
| Skip optional source instead of creating key | Inline Skip and checkbox removal; local revalidation before save | No automatic signup or key creation |
| Selected API key and code setup in one place | Inline save/test for supported native sources; Brave deterministic code template, fixed BRAVE_API_KEY binding independent of display name; code explicitly not executed | No saved Brave key, so Brave live call not qualified; exact reported Try it 'os error' still not recovered |
| Model/provider/key/test in same window | Explicit provider, model identifier, custom base URL, provider model discovery, save key and test controls | UI controls and mocked transport qualification are not a live model integration test |
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
- Full browser suite and live model-build acceptance remain open.

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

# AgricultureChat qualification work in progress

Not yet in the public gallery. No claim of globally uniform or field-specific fertilizer guidance.

Sources researched31October2026:
- FAO global principles, Voluntary Guidelines for Sustainable Soil Management (2017): https://openknowledge.fao.org/server/api/core/bitstreams/9a5b9373-3558-43b3-b732-f69326a7314d/content
- Minnesota regional soil-test interpretation: https://extension.umn.edu/agriculture/crop-production/nutrient-management-for-minnesota-crops/understanding-the-soil-test-report
- Europe PMC REST core metadata/abstracts: https://europepmc.org/restfulwebservice and https://europepmc.org/developers . No bulk full-text scraping; abstracts only, no API key.
- AGRIS ODS is a metadata dataset, not instant fertilizer prescriptions: https://www.fao.org/agris/agris-ods
- AGROVOC is a vocabulary, not dosage evidence: https://www.fao.org/agrovoc/using-agrovoc

Sources preserve attribution and region. FAO and extension excerpts are not fertilizer application tables. Any final app must ask farm country/crop/soil context, state missing coverage and avoid inventing application rates.

Current live research probes: Europe PMC core works without a key. Explicit TITLE_ABS terms with AND are narrower than its default broad matching; generic relevance results can still be about a different crop. A query for legumes/soil fertility/Tanzania returned zero under this exact filter. Bangladesh rice query returned relevant rice material plus a wheat study mentioning rice context. Do not treat counts as relevance or answer-quality proof. Need independent query/evidence checks, crop/region applicability handling and real-provider answer review before gallery.

Europe PMC sort=RELEVANCE produced503 in this environment; removing unsupported sort fixed requests. Bounded transient retry remains, no endless polling.

Qualification update, 31 October 2026:
- Conversational crop/country terms are retained, while grow/growing and question boilerplate are removed from the exact Europe PMC query. Query rewriting is disabled so it cannot silently erase geographic constraints.
- Repeated DOI/title records are deduplicated within each search response.
- Literature requests do not receive the global or Minnesota guidance snapshots. This deliberately preserves an empty Tanzania search instead of turning FAO general principles into local research.
- Generic fertilizer-choice requests do not receive arbitrary experimental fertilizer papers.
- Actual gpt-4o-mini rechecks retrieved maize/phosphorus studies for Kenya and rice/nitrogen/water studies for Bangladesh. Unsupported DAP dosage and Tanzania literature requests returned an explicit evidence gap.
- Nine source-contract tests pass. These are contract tests, not proof of relevance or factual answer quality.
- NOT READY FOR GALLERY: real-provider answers still contain uncited lead/conclusion sentences and sometimes generalize study findings beyond their supplied limits. The support warning remains visible. Short attributed paragraphs and a revision stage reduced length but did not meet the answer-quality gate. No broad global coverage or farm-prescription claim is justified.

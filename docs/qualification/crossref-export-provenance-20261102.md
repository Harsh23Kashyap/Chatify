# Crossref title-only provenance in previews and exports

Extends isolated checkpoint 08d6cdca7af8541ab8f4f895ece168278f338885. Main remains separate at released 3b80fa5 during qualification. Recipe checkpoint is not included.

The explicit title-only marker now survives the unverified source-preview projection. Its label is outside the unchanged quoted source text, and answer_verified remains false. The model-unavailable fallback preview also labels marked rows. Answer Markdown, chat Markdown, PDF source snapshots and BibTeX preserve the provenance. BibTeX uses a note field, not an invented abstract.

Nine new Python controls: projection retention/no mutation, label outside quote, answer/chat Markdown, PDF extraction, BibTeX note, unmarked title-text equality negative control, unknown-kind negative control, oversize omission and model-unavailable fallback. Six tests fail on checkpoint08d6 baseline. Existing tests and assertions retained.

Qualification:
- Full clean serial Python regression: 1403 passed, 1 skipped, 549 subtests across221files. After adding the final fallback label, affected group7 rerun225passed/27subtests; group0 also repeated193/7. Other seven groups unchanged. Final focused44tests/6subtests pass across preview, export and legacy behavior.
- Existing provenance card/drawer browser scenario replayed with the actual generated preview Markdown, desktop normal/reduced motion. This is a diagnostic local fixture run, not a newly classified script or live source/model call. Exact preview marker verified in rendered thread. Source card and drawer assertions retained.
- Actual PDF rendered and pixels inspected: clear title-only note beside the correct source, short abstract control unmarked, title/DOI readable, no clipping. Actual preview UI pixels inspected: title-only label outside source quote, short abstract unmarked. Markdown and BibTeX text inspected.
- No provider/model requests, hosted changes or resource/spend operations.

Limits retained: no retroactive inference for old unmarked cache/history, OpenAlex fallback remains outside this change, no semantic answer acceptance. Source data can be false or incomplete despite accurate provenance. Recipe source503/relevance, Brave missing live-key proof and large-logo hosted performance remain separate. These changes do not claim that an article's full text lacks an abstract, only that the retrieved record supplied no abstract or article text.

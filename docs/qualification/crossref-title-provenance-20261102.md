# Crossref title-only record provenance

Base: released 3b80fa516993762ac565cd10c20d561944ae2ad0. Separate from the Recipe defensive checkpoint.

Historical actual free-API evidence includes Crossref results with no abstract. The connector used the title as text. Forty-to-fifty-character title records appeared as ordinary excerpts in the answer evidence card and Sources drawer, with no label explaining the absence of article text.

This candidate preserves the title, DOI URL, year and exact text. A missing or markup-only abstract adds `content_kind: title_only`. An actual abstract, even a short one, is not marked based on length. Both card and drawer label marked records `Title only; no abstract or article text`. Evidence serialization for generation, relevance, correction, revision, support checking and support repair carries the same provenance. The optional verbatim named-entity passage listing skips marked rows rather than duplicating a title as an unlabeled passage. No system instruction, model, score, citation-check threshold or document inclusion rule changed.

Qualification:
- Eight new Python controls cover preserved references, blank/markup-only abstracts, short real abstract negative control, prompt marker, absence of unlabeled entity duplicate, exact text slicing, retrieve/cache retention and support-check input.
- UI regression fails on released app.js and passes candidate. Captured title-only shape and synthetic short abstract control are shown at desktop normal/reduced motion. Actual pixels inspected after transition completion: label readable in card and drawer, short abstract unchanged, DOI link retained.
- Existing source-filter browser test passes with its original available/unavailable/filter/focus assertions.
- Two scoped browser scripts, two executions, not all 484 classified scripts.
- Full clean Python suite: 1394 passed, 1 skipped, 543 subtests, eight serial groups across 220 files.
- No new provider or model requests, no hosted changes, no key/resource/spend operations during qualification.

Limits: replay/controlled payload coverage, not improved semantic answer acceptance. Titles alone do not establish article findings. Existing persisted evidence/cache rows without the new marker are not retroactively inferred from title-text equality, because a real short abstract can equal its title. Newly fetched missing-abstract Crossref records carry the label; old unmarked cache/history may remain unlabeled until refreshed. OpenAlex's separate missing-abstract fallback remains outside this candidate. Source-preview Markdown/export layouts are not newly qualified here. Recipe 503, processed-cheese relevance, Brave missing-key live proof, semantic quality and large-logo hosted performance remain separate.

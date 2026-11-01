# OpenAlex title fallback provenance

Based on released b5ceb4934254bea0ea2594a04386e24da3978f44. Recipe isolated. Local qualification only.

OpenAlex currently substitutes its title when the inverted abstract index yields no text. The connector now adds the existing explicit content_kind:title_only marker for exactly that fallback. Real short abstracts, including abstracts equal to the title, remain unmarked. Title, text, DOI, author, year, venue, ranking, query, authentication and model behavior unchanged. No inference for legacy unmarked cache/history.

Seven new tests use synthetic API shapes, not captured raw OpenAlex payloads or live API evidence. Historical request reports retained titles and IDs, not the inverted abstract index. Corrected year expectation to existing Evidence string contract before baseline comparison. Pristine b5: three failing test methods and four subtest failures, four unchanged controls pass. Candidate: seven pass plus four subtests. Combined Crossref/preview/export focused24/13; wider53/4.

Full clean serial Python regression:1410passed,1skipped,553subtests across222files, all eight groups run on final product diff. Actual local Store+HTTP boundary with connector-produced synthetic OpenAlex record:10/10 checks pass (stored/history/answer Markdown/chat Markdown/BibTeX/PDF plus legacy remains unmarked).

Diagnostic local UI replay uses actual generated OpenAlex-shaped preview Markdown and marked/short-abstract fixtures. Desktop normal/reduced motion, existing card/drawer checks retained. PDF/preview/card/drawer pixels inspected: readable label under correct source; short abstract unmarked; exact source text retained. Not newly classified suite coverage, not live API/model/semantic acceptance. The reused diagnostic console heading mentions Crossref; it is not provenance evidence. No provider/model requests or remote changes during qualification.

Limits: no raw historical OpenAlex null-index payload retained, no new live-source proof; source content can be false/incomplete. Old cache/history remains unmarked until refreshed. Other semantic, Brave live-key, large-logo hosted-latency and Recipe503/relevance gaps unchanged.

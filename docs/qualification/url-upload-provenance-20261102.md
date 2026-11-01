# Source URL provenance for newly imported pages

Local candidate based on released004380fe. No old upload origin inference and no new external requests.

Problem: Add sources > Web address imported only name/text. Uploaded evidence used an empty URL, so the relevant paragraph could not reliably open its publisher page. Putting a link in the first paragraph is insufficient when another paragraph is retrieved.

Change: the bounded URL loader optionally returns its final, per-hop checked address, preserving its default two-value contract. The HTTP import persists origin separately; every retrieved upload chunk gets that origin. Local/file uploads and legacy imports remain unmarked. No generic URL extraction from text, crawling, audio transcription, or semantic acceptance.

A side table preserves existing five-column upload records/direct inserts. Upload+origin insertion and deletion are transactional. Injected origin insert failure rolls back the upload; injected upload deletion failure rolls back origin removal. Owner isolation, restart, legacy SQLite database, redirect rechecks, invalid/credential-bearing origins and existing storage degradation controls pass. MySQL source_url DDL uses LONGTEXT, covered by translation test only, not live MySQL.

Eleven new Python tests plus three subtests. Initial six-test baseline on004380 failed four methods and three subtests; two unchanged controls passed. Initial focused128/3; atomic/core/degrade110/3. Full final serial Python regression:1421passed,1skipped,556subtests across223files, eight groups completed. Existing tests/assertions retained.

Actual local HTTP load (mocked page fetch, not live fetch) -> Store -> retrieved body chunk without header -> history, answer Markdown, chat Markdown, BibTeX and PDF -> delete:10/10 checks pass. PDF pixels inspected: correct original publisher URL readable under source title, no clipping. Diagnostic source drawer UI replay, desktop normal motion only, shows Open source with exact original URL. Fixture contains synthetic note labels, no claimed interview extraction or publication date. Reused console heading mentions Crossref; it is not evidence of source or suite scope.

Private MPV snapshot diagnosis remains distinct: two publisher-note pages do not cover Madagascar and do not independently prove media-induced conflict reduction. Raw BM25 returns generic passages for those questions, not proof of final answer failure or adequacy. No model/API/source calls, hosted uploads, external messages or public corpus publication. Recipe remains isolated. Old history/cache, semantic answer quality, Brave live-key and large-logo hosted-latency limitations stay open.

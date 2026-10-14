# Formula One Chat sources

No source key, payment card or paid service is needed for the bundled FIA sources.
Wikipedia, arXiv, Crossref and PubMed remain available as secondary sources; not
all questions will have relevant evidence in every catalog. The model provider
still needs its own key or a configured local model.

The new FIA connector searches verbatim, locally bundled text from:

- Technical regulations, Issue 20, 5 August 2026:
  https://www.fia.com/system/files/documents/fia_2026_f1_regulations_-_section_c_technical_-_iss_20_-_2026-08-05.pdf
- Sporting regulations, Issue 09, 1 October 2026:
  https://www.fia.com/system/files/documents/fia_2026_f1_regulations_-_section_b_sporting_-_iss_09_-_2026-10-01.pdf

These are dated snapshots, not a live update feed or proof that no newer issue
exists. Plain text loses amendment colors and page layout. Consult the original
PDF and the FIA regulation index for competition decisions:
https://www.fia.com/regulation/category/110

Keep `f1_sources.py` and `sources/` with either YAML file. The Python connector
requires the app loader's normal code review/consent. It does not make network
requests or execute commands. Source results retain their original PDF URLs and
PDF-page labels for citation checks.

Default answers use up to 12 passages; Deep uses up to 24. Fuller answers are
requested only when the evidence supports them, never to fill a word count.

Historical source excerpts added15October2026:
- https://www.ferrari.com/en-EN/history/moments/1950/debut-in-f1
- https://www.ferrari.com/en-EN/history/moments/1951/first-f1-win
- https://www.formula1.com/en/information/ferrari-year-by-year.61yfcjhl05vSlmNJB1SIJ0
These are historical material, not current standings or live championship totals.

"""Key-free, offline-searchable FIA regulation snapshots with original PDF links.

Text extracted without summarizing from the dated official PDFs listed in README.
Not a live rule update feed. Colors in the PDFs carry editorial status that plain
text cannot preserve; competition decisions must be checked in the original PDF.
"""
from pathlib import Path
from chatify.connectors.local_files import LocalFiles

BASE = Path(__file__).resolve().parent
URLS = {
    'ferrari-debut.md': 'https://www.ferrari.com/en-EN/history/moments/1950/debut-in-f1',
    'ferrari-first-win.md': 'https://www.ferrari.com/en-EN/history/moments/1951/first-f1-win',
    'ferrari-history.md': 'https://www.formula1.com/en/information/ferrari-year-by-year.61yfcjhl05vSlmNJB1SIJ0',
    'fia-technical.md': 'https://www.fia.com/system/files/documents/fia_2026_f1_regulations_-_section_c_technical_-_iss_20_-_2026-08-05.pdf',
    'fia-sporting.md': 'https://www.fia.com/system/files/documents/fia_2026_f1_regulations_-_section_b_sporting_-_iss_09_-_2026-10-01.pdf',
}
_index = None

def search(query, k=12):
    global _index
    if _index is None:
        _index = LocalFiles({'id':'fia-regulations','label':'FIA regulations','path':'sources'}, str(BASE))
    out = _index.search(query, k)
    for item in out:
        item['url'] = URLS.get(item.get('document'), '')
        item['year'] = '2026'
        item['venue'] = 'FIA (dated regulation snapshot)' if item.get('document','').startswith('fia-') else 'Ferrari / Formula 1 (historical excerpt)'
        if item.get('document','').startswith('fia-'):item['text'] = 'Dated 2026 regulation snapshot; consult the linked PDF for amendment colors and current applicability. ' + item['text']
    return out

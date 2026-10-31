"""Preserve origin and date on packaged Wikipedia reference snapshots."""
from pathlib import Path
from chatify.connectors.local_files import LocalFiles
BASE=Path(__file__).resolve().parent
URLS={'01-mars.md':'https://en.wikipedia.org/wiki/Mars','02-artemis.md':'https://en.wikipedia.org/wiki/Artemis_program','03-webb.md':'https://en.wikipedia.org/wiki/James_Webb_Space_Telescope','04-iss.md':'https://en.wikipedia.org/wiki/International_Space_Station'}
_index=None
def reference(query,k=8):
 global _index
 if _index is None:_index=LocalFiles({'id':'reference','label':'Dated reference texts','path':'docs'},str(BASE))
 rows=_index.search(query,k)
 for row in rows:
  row['url']=URLS.get(row.get('document'),'')
  row['venue']='Wikipedia reference snapshot, fetched 21 October 2026 (CC BY-SA 4.0)'
  row['text']='Dated reference snapshot, fetched 21 October 2026. Mission plans may have changed; not a live status feed. '+row['text']
 return rows

"""Attributed dated public-health guidance; not personal exercise prescriptions."""
from pathlib import Path
from chatify.connectors.local_files import LocalFiles
BASE=Path(__file__).resolve().parent
URLS={
 '01-pag-executive-summary.pdf':'https://odphp.health.gov/sites/default/files/2019-10/PAG_ExecutiveSummary.pdf',
 '02-benefits.md':'https://medlineplus.gov/benefitsofexercise.html',
 '03-exercise-fitness.md':'https://medlineplus.gov/exerciseandphysicalfitness.html',
 '04-older-adults.md':'https://medlineplus.gov/exerciseforolderadults.html',
}
_index=None
def guidance(query,k=8):
 global _index
 if _index is None:_index=LocalFiles({'id':'guidance','label':'Public health guidance','path':'docs'},str(BASE))
 rows=_index.search(query,k)
 for row in rows:
  row['url']=URLS.get(row.get('document'),'')
  row['venue']='US public-health guidance, dated snapshot'
  row['text']='Dated US guidance snapshot. See the original linked source; not a personal exercise prescription. '+row['text']
 return rows

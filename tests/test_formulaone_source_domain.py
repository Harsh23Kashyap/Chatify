"""Narrow metadata/recall controls over dated official source snapshots."""
import importlib.util,pathlib,unittest
from chatify.pipeline import relevance_gate
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('formulaone_domain',ROOT/'apps/formulaone/f1_sources.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class FormulaOneDomain(unittest.TestCase):
 def test_source_domain_title_retains_document_and_verbatim_rule(self):
  rows=module.search('sporting rules pit stops Formula One',2)
  self.assertTrue(rows)
  for row in rows:
   self.assertTrue(row['title'].startswith('Formula One (F1): '));self.assertIn('FIA 2026 Sporting Regulations',row['title']);self.assertTrue(row['url'].startswith('https://www.fia.com/'))
   self.assertIn('Dated 2026 regulation snapshot',row['text'])
 def test_spelled_out_domain_survives_named_entity_ranking(self):
  q='What are the sporting rules regarding pit stops in Formula 1?';rows=module.search(q,2)
  # Explicit contrast reproduces the competing research anchors from the live audit.
  adjacent=[{'title':'Optimizing Pit Stops Strategies in Formula 1','text':'Research on competition in Formula 1 pit stop strategies','source':'crossref','score':1,'id':'research1','url':'fixture:1'},{'title':'Statistical Race Simulations of Pit Stops in Formula One','text':'Formula One research on lap times and pit stops','source':'crossref','score':.5,'id':'research2','url':'fixture:2'}]
  kept=relevance_gate(q,rows+adjacent,public_ids={'crossref'})
  self.assertTrue(any('FIA 2026 Sporting Regulations' in x['title'] for x in kept))
if __name__=='__main__':unittest.main()

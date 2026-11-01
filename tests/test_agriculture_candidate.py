"""Configuration/source integrity, not real-model safety or answer acceptance."""
import pathlib, unittest
from chatify import schema
from chatify.connectors.local_files import LocalFiles
ROOT=pathlib.Path(__file__).resolve().parents[1]
class AgricultureCandidate(unittest.TestCase):
 def setUp(self):
  self.path=ROOT/'apps/agriculturechat';self.cfg=schema.load(str(self.path/'app.yaml'))
 def test_global_intake_and_no_dose_policy(self):
  policy=self.cfg['prompt']['system']
  for text in ['never assume India','country and locality','crop and growth stage','soil-test results','field area and units','do not guess an application rate','qualified local agronomist','not live regulations']:
   self.assertIn(text,policy)
 def test_no_evidence_keeps_intake_and_no_dose(self):
  fallback=self.cfg['prompt']['no_evidence']
  for text in ['country and locality','crop and growth stage','soil-test results','not have enough relevant evidence','before you apply fertilizer']:
   self.assertIn(text,fallback)
 def test_only_qualified_sources_configured(self):
  self.assertEqual([s['type'] for s in self.cfg['sources']],['local_files'])
  self.assertNotIn('agriculturechat',(ROOT/'apps/gallery.yaml').read_text())
 def test_all_snapshots_attributed_scoped_and_dated(self):
  docs=list((self.path/'docs').glob('*.md'));self.assertEqual(len(docs),3)
  for p in docs:
   text=p.read_text();self.assertIn('Source: https://',text);self.assertIn('Fetched: 2026-11-01',text);self.assertIn('Scope:',text);self.assertIn('not the full source',text)
 def test_examples_find_relevant_guidance(self):
  source=LocalFiles(self.cfg['sources'][0],str(self.path))
  for question,expected in [('soil test report','Minnesota Extension'),('site-specific nutrient management','IRRI'),('fertilizer soil tillage','FAO')]:
   results=source.search(question,k=4);self.assertTrue(results);self.assertTrue(any(expected in x['title'] for x in results))
if __name__=='__main__':unittest.main()

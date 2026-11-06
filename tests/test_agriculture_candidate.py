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
 def test_every_retrievable_passage_keeps_original_source_scope(self):
  source=LocalFiles(self.cfg['sources'][0],str(self.path))
  self.assertEqual(len(source.docs),7)
  for doc in source.docs:
   with self.subTest(document=doc['document'],chunk=doc['id']):
    self.assertIn('Source: https://',doc['text'])
    self.assertIn('Fetched: 2026-11-01',doc['text'])
    self.assertIn('not the full source',doc['text'])
    expected={'01-fao-principles.md':'General principles, not a field prescription.',
              '02-irri-rice-scope.md':'Rice-specific, not all crops or countries.',
              '03-minnesota-soil-tests.md':'Minnesota/North-Central US examples; do not transfer local calibration globally.'}
    self.assertIn('Scope: '+expected[doc['document']],doc['text'])
 def test_fetch_date_never_masquerades_as_publication_date(self):
  source=LocalFiles(self.cfg['sources'][0],str(self.path))
  for doc in source.docs:
   self.assertIn('date',doc);self.assertEqual(doc['date'],'')
   self.assertIn('date_src',doc);self.assertEqual(doc['date_src'],'')
  for doc in source.search('soil nutrient fertilizer rice laboratory',k=20):
   self.assertIn('year',doc);self.assertEqual(doc['year'],'')
if __name__=='__main__':unittest.main()

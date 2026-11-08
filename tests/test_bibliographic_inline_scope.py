import json
from pathlib import Path
import unittest
from chatify.pipeline import Engine
class InlineBibliography(unittest.TestCase):
 def setUp(self):
  self.fixture=json.loads((Path(__file__).parent/'fixtures/paper_trail_repair_drafts_20261108.json').read_text());self.draft=self.fixture['drafts'][1];self.rows=self.draft['evidence'];self.line=self.draft['answer'].splitlines()[2]
 def test_frozen_metadata_units_and_separate_residual(self):
  for item in self.fixture['drafts']:
   for tidy in [False,True]:
    a,rows=Engine.tidy(item['answer'],item['evidence']) if tidy else (item['answer'],item['evidence'])
    led=Engine.ledger(a,rows);meta=[r for r in led if 'Source: http' in r['claim']];self.assertEqual(len(meta),2)
    for row in meta:
     self.assertTrue(row['supported']);self.assertFalse(row['weak_cites']);self.assertFalse(row['bad_numbers'])
     source=next(e for e in rows if e['n']==row['cites'][0]);self.assertIn(source['title'],row['claim']);self.assertIn(source['url'],row['claim'])
     for name in source['authors']:self.assertIn(name,row['claim'])
    self.assertFalse(any(r['claim'].startswith(('Barron,','Eren,')) for r in led))
    bad=[r for r in led if not r['supported'] or r['weak_cites']]
    if item['call']==7:self.assertEqual(bad,[])
    else:
     self.assertEqual(len(bad),2);self.assertIn('In simpler terms',bad[0]['claim']);self.assertFalse(bad[0]['supported']);self.assertIn('The titles, authors',bad[1]['claim']);self.assertTrue(bad[1]['weak_cites'])
 def test_trailing_metadata_cite_not_lent_to_description(self):
  no_own_cite=self.line.replace('tasks. [1]','tasks.')
  parts=Engine.bibliographic_parts(no_own_cite,self.rows);self.assertIsNotNone(parts);self.assertNotIn('[1]',parts[1]);led=Engine.ledger(no_own_cite,self.rows);desc=next(r for r in led if r['claim'].startswith('Its description'));self.assertFalse(desc['supported']);self.assertTrue(desc['uncited'])
 def test_unsupported_quantities_and_adjacent_claim_still_blocked(self):
  line=self.line.replace('Its description says the paper studies multilingual RAG and reports that CrossRAG improves performance on knowledge-intensive tasks. [1]', 'Patients lost999kg. [1] Unrelated unsupported facts have no citation here.')
  led=Engine.ledger(line,self.rows);self.assertTrue(any(r['bad_numbers'] for r in led));self.assertTrue(any(r['uncited'] for r in led));self.assertTrue(led[0]['supported'])
 def test_altered_metadata_url_and_wrong_cite_fail_closed(self):
  for line in [self.line.replace('2025','2026'),self.line.replace('Leonardo Ranaldi','Leonardo Fake'),self.line.replace('v2)','v2999)'),self.line[:-3]+'[2]']:
   self.assertIsNone(Engine.bibliographic_parts(line,self.rows))
 def test_uncited_preamble_stays_blocked(self):
  led=Engine.ledger('Here are several excellent papers that guarantee success.\n\n'+self.line,self.rows);self.assertTrue(led[0]['uncited']);self.assertFalse(led[0]['supported'])
if __name__=='__main__':unittest.main()

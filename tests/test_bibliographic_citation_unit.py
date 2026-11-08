import copy,json,pathlib,unittest
from chatify.pipeline import Engine
class BibliographicUnit(unittest.TestCase):
 def row(self):return {'n':2,'title':'Retrieval methods and evidence','authors':['Ryan C. Barron','Maksim E. Eren','Manish Bhattarai'],'year':'2024','url':'https://example.invalid/papers/2410.02721v1','text':'The abstract compares sparse retrieval with dense retrieval.'}
 def line(self):return '- **“Retrieval methods and evidence”** - Ryan C. Barron, Maksim E. Eren, and Manish Bhattarai (2024). Source: https://example.invalid/papers/2410.02721v1 [2]'
 def test_exact_metadata_is_one_supported_unit(self):
  r=self.row();line=self.line();before=copy.deepcopy(r);self.assertEqual(Engine.bibliographic_record(line,[r]),r);led=Engine.ledger(line,[r]);self.assertEqual(len(led),1);self.assertTrue(led[0]['supported']);self.assertEqual(r,before)
 def test_extra_claim_wrong_metadata_or_citation_never_grouped(self):
  for line in [self.line()+' It cures cancer.',self.line().replace('2024','2023'),self.line().replace('Maksim E. Eren','Maksim E.'),self.line().replace('[2]','[1]'),self.line().replace('2410.02721','9999'),self.line().replace('Source:','Guaranteed accurate Source:')]:
   with self.subTest(line=line):self.assertIsNone(Engine.bibliographic_record(line,[self.row()]))
 def test_uncited_adjacent_factual_prose_stays_unsupported(self):
  line=self.line()+'\nThis method always cures every disease without any risks.';led=Engine.ledger(line,[self.row()]);self.assertTrue(any(not l['supported'] and 'cures' in l['claim'] for l in led))
 def test_wrong_quantity_same_line_not_supported_by_url_or_year(self):
  line=self.line().replace('(2024).','(2024). It reduced risk by999kg.');self.assertIsNone(Engine.bibliographic_record(line,[self.row()]));led=Engine.ledger(line,[self.row()]);self.assertTrue(any(not l['supported'] for l in led))
 def test_actual_captured_author_initial_lines_are_one_unit(self):
  path=pathlib.Path(__file__).parent/'fixtures/paper_trail_actual_metadata_20261108.json';rows=json.loads(path.read_text())['evidence']
  for row in rows:
   line='- '+row['title']+' - '+', '.join(row['authors'])+' ('+row['year']+'). Source: '+row['url']+' ['+str(row['n'])+']';self.assertEqual(len(Engine.ledger(line,rows)),1);self.assertTrue(Engine.ledger(line,rows)[0]['supported'])
if __name__=='__main__':unittest.main()

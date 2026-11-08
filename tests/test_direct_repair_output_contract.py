import json,copy,unittest
from pathlib import Path
from unittest.mock import Mock
from chatify import schema
from chatify.pipeline import Engine
from chatify.store import Store
class DirectRepairContract(unittest.TestCase):
 def setUp(self):
  self.item=json.loads((Path(__file__).parent/'fixtures/paper_trail_repair_drafts_20261108.json').read_text())['drafts'][1];self.rows=self.item['evidence'];self.original=self.item['answer'];self.question='Explain the previous answer more simply using the same cited sources.'
  lines=self.original.splitlines();self.fixed='\n\n'.join(lines[i] for i in [2,3]);self.note='Note: the sources may not fully support this: intro'
  self.e=Engine(schema.validate({}),Store(':memory:'));self.e.provider=Mock();self.e.check_support=Mock(return_value='')
 def repair(self,candidate):
  self.e.provider.complete.return_value=candidate;return self.e.repair_support(self.original,self.rows,self.question,self.note)
 def test_supported_direct_answer_preserves_metadata_rechecked(self):
  result=self.repair(self.fixed);self.assertEqual(result[3],'');self.assertTrue(result[2]);self.e.check_support.assert_called_once();self.assertEqual(self.e.provider.complete.call_count,1)
  for row in self.rows:
   self.assertIn(row['url'],result[0]);self.assertIn(row['year'],result[0])
   for author in row['authors']:self.assertIn(author,result[0])
  wire=self.e.provider.complete.call_args.args[0];self.assertIn(self.question,wire[1]['content']);self.assertIn('not a conversational preamble',wire[0]['content']);self.assertIn('not permission to omit requested uncertainty',wire[0]['content']);self.assertIn('separate line',wire[0]['content'])
 def test_unsupported_preamble_and_quantities_still_withheld(self):
  for candidate in ['Here are several excellent papers that guarantee clinical success.\n\n'+self.fixed,self.fixed+'\n\nPatients lost999kg. [1]',self.original,self.fixed.replace('2504.03616v2','2504.03616v2888'),self.fixed.replace(' [1] [Source link]',' [999] [Source link]')]:
   with self.subTest(candidate=candidate[-50:]):
    self.e.check_support.reset_mock();result=self.repair(candidate);self.assertIn('withheld',result[3]);self.e.check_support.assert_not_called()
 def test_faithfulness_rejection_never_overridden(self):
  self.e.check_support.return_value='Note: the sources may not fully support this: invented finding';self.assertIn('withheld',self.repair(self.fixed)[3])
 def test_generation_contract_nonmutating_and_classifier_unchanged(self):
  before=copy.deepcopy(self.rows);q='Name the papers, preserve requested limitations and explain simply.';system=self.e.prompt(q,self.rows,'standard',[],'')[0]['content'];self.assertIn(Engine.direct_output_contract(),system);self.assertEqual(before,self.rows);self.assertNotIn('not a conversational preamble',self.e.stage_prompt('question_check'));self.assertIn('supporting evidence',system)
if __name__=='__main__':unittest.main()

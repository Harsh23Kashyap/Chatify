"""Hosted starter regression: no unsolicited bibliographic appendices in rewrites.

Prompt checks are control-flow coverage. Real model checks are recorded separately.
"""
import json, os, unittest
from unittest.mock import Mock, patch
from chatify import schema
from chatify.pipeline import Engine
from chatify.store import Store

class StarterContract(unittest.TestCase):
 def test_howto_and_citation_explanations_do_not_request_bibliographies(self):
  for q in ('What is Chatify?', 'How do I build my own chat app?', 'How are answers cited?', 'How do I run Chatify on my own computer?'):
   with self.subTest(q=q):
    contract=Engine.direct_output_contract(q)
    self.assertIn('Do not append a Sources, References, Evidence or bibliography section',contract)
    self.assertNotIn('List each bibliographic title',contract)
 def test_requested_metadata_is_preserved(self):
  for q in ('Name the papers and their authors', 'Give the bibliography', 'Give citation details including DOI'):
   self.assertIn('List each bibliographic title',Engine.direct_output_contract(q))
 def test_withheld_reason_is_observable_by_default_without_context(self):
  e=Engine(schema.validate({}),Store(':memory:'));e.provider=Mock();e.provider.complete.return_value=''
  with patch.dict(os.environ,{'CHATIFY_SUPPORT_DIAGNOSTICS':'0'}),patch('chatify.pipeline.logging.getLogger') as logger:
   e.repair_support('Private content', [{'n':1,'title':'Private title','text':'Private passage'}], 'Private question','Note: the sources may not fully support this: private reason')
   calls=logger.return_value.warning.call_args_list
   self.assertEqual(len(calls),1);self.assertEqual(calls[0].args[0],'answer_withheld %s')
   self.assertEqual(json.loads(calls[0].args[1]),{'stage':'repair','outcome':'short_candidate','evidence_count':1})
   self.assertNotIn('Private',str(calls))
if __name__=='__main__':unittest.main()

"""Generated pre-retrieval instructions must not claim evidence state."""
import unittest
from chatify import generator_design
class StageScope(unittest.TestCase):
 def test_answer_and_upload_duties_rejected_even_with_valid_stage_words(self):
  for stage in ('standalone','question_check'):
   for drift in ('Your primary function is to answer questions strictly related to uploaded documents.', 'If no documents are available, you must prompt the user to upload a document before proceeding.', 'If the input is insufficient, you should ask for the necessary evidence.'):
    text=drift+' Rewrite the latest runtime question using history. Classify intent only: VALID or INVALID.'
    self.assertTrue(generator_design.validate_draft(stage,{'prompt':text}))
 def test_negated_upload_duties_and_answer_stage_remain_allowed(self):
  text='Rewrite the latest runtime question using history only to resolve a referent. Never ask for documents or answer questions. If unclear return the original unchanged.'
  self.assertEqual(generator_design.validate_draft('standalone',{'prompt':text}),[])
  text='Classify reader intent only. Do not request uploads or evidence. Output VALID or INVALID: reason.'
  self.assertEqual(generator_design.validate_draft('question_check',{'prompt':text}),[])
  self.assertEqual(generator_design.validate_draft('answer',{'prompt':'If no documents are available, you must prompt the user to upload a document. Cite every factual sentence with [n].'}),[])

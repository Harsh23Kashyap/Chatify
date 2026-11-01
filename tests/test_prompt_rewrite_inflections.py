"""Recovered regression from actual earlier rewriting/rephrasing false rejection."""
import unittest
from chatify.generator_design import validate_draft
class RewriteInflections(unittest.TestCase):
 def test_reusable_inflected_instruction(self):
  self.assertEqual(validate_draft('standalone',{'prompt':'You are tasked with rewriting or rephrasing the latest question related to peacebuilding news. Preserve the question and resolve references only from supplied history. Return only the rewritten question.'}),[])
 def test_fixed_question_still_rejected(self):
  self.assertTrue(validate_draft('standalone',{'prompt':'What are the latest successful peace agreements in Northern Ireland?'}))
 def test_unrelated_substring_still_rejected(self):
  self.assertTrue(validate_draft('standalone',{'prompt':'The converter and turningpoint questions are about peacebuilding news.'}))

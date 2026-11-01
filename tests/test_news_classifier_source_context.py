"""Instruction contract; actual-model accuracy is separately qualified."""
import unittest
from chatify import schema
from chatify.pipeline import Engine
from chatify.store import Store
class NewsContext(unittest.TestCase):
 def test_publisher_not_required_for_event_time_question(self):
  e=Engine(schema.validate({'sources':[]}),Store(':memory:'));text=e.stage_prompt('question_check');self.assertIn('Do not require a publisher, article title',text);self.assertIn('does not establish that reporting exists',text)

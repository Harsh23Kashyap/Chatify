import unittest
from unittest.mock import patch
from chatify import schema
from chatify.pipeline import Engine
from chatify.store import Store
class RefusalState(unittest.TestCase):
 def test_refusal_distinct_from_empty_search_sync_stream_and_saved(self):
  for stream in (False,True):
   e=Engine(schema.validate({}),Store(':memory:'));c=e.store.new_chat('u')
   with patch.object(e,'check_question',return_value='Cannot provide personal doses.'),patch.object(e,'retrieve',side_effect=AssertionError('refusal should not search')):
    r=next(d for k,d in e.ask_stream('u',c,'dose?') if k=='done') if stream else e.ask('u',c,'dose?')
   self.assertEqual(r['response_kind'],'question_refused');self.assertEqual(e.store.get_state('u','reply-kind-'+r['id']),'question_refused')
 def test_no_results_not_mislabeled_refusal(self):
  e=Engine(schema.validate({}),Store(':memory:'));c=e.store.new_chat('u')
  with patch.object(e,'retrieve',return_value=([],{})):
   self.assertEqual(e.ask('u',c,'ordinary question')['response_kind'],'answer')

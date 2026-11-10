"""Generated helper drafts are review artifacts, not runtime query transforms."""
import copy,unittest
from chatify import schema,generators
from chatify.pipeline import Engine
from chatify.store import Store

class InertHelperBoundary(unittest.TestCase):
 def test_control_only_cleanup_fallback_is_not_executed_by_generated_runtime(self):
  # This deliberately poor helper would destroy a normal question if activated.
  cfg=copy.deepcopy(schema.DEFAULTS)
  cfg['helper_drafts']={'clean_query':{'brief':'Inert reviewed draft','code':'def clean_query(query):\n    return "DESTROYED QUERY"\n'}}
  e=Engine(cfg,Store(':memory:'),connectors={})
  baseline=Engine(copy.deepcopy(schema.DEFAULTS),Store(':memory:'),connectors={})
  for question in ['What is Chatify?', '\x00\x01']:
   with self.subTest(question=repr(question)):
    actual=e.ask('owner',e.store.new_chat('owner'),question,use_cache=False)
    expected=baseline.ask('owner',baseline.store.new_chat('owner'),question,use_cache=False)
    self.assertEqual(actual['answer'],expected['answer'])
    self.assertNotIn('DESTROYED QUERY',str(actual))
 def test_inert_template_fallback_is_explicit_not_control_sanitization(self):
  namespace={};exec(generators.code_template('clean_query',''),namespace)
  self.assertEqual(namespace['clean_query'](''), '')
  self.assertEqual(namespace['clean_query']('  books  '), 'books')
  self.assertEqual(namespace['clean_query']('\x00\x01'), '\x00\x01')

import json,tempfile,unittest,yaml
from pathlib import Path
from unittest.mock import patch
from chatify import appbuilder,schema
class ReviewPerformance(unittest.TestCase):
 def test_review_uses_single_checked_parse_and_json_yaml_output(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'app.yaml';p.write_text('{}');cfg=schema.load(str(p));cfg['_path']=str(p)
   with patch('chatify.appbuilder.validate_declared',wraps=appbuilder.validate_declared) as checked,patch('yaml.safe_load',wraps=yaml.safe_load) as parsed,patch('yaml.safe_dump',side_effect=AssertionError('review must not rescan or YAML-emit large data')):
    plan=appbuilder.review(cfg,json.dumps({'app':{'title':'Example 🌱'}}),['app'])
   self.assertEqual(checked.call_count,1);self.assertFalse(any(call.args and call.args[0]==json.dumps({'app':{'title':'Example 🌱'}}) for call in parsed.call_args_list));self.assertEqual(json.loads(plan['yaml'])['app']['title'],'Example 🌱');self.assertEqual(yaml.safe_load(plan['yaml']),plan['config'])
 def test_json_yaml_equivalence_and_scope(self):
  samples=[{'app':{'title':'Example','examples':['why?','a: b','yes']}},{'provider':{'type':'mock','base_url':None}},{'appearance':{'txt_title':'Garden 🌱'}},{'retrieval':{'top_k':4,'query_rewrite':True}},{}]
  for raw in samples:
   with self.subTest(raw=raw):
    expected=appbuilder.validate_declared(yaml.safe_dump(raw));self.assertEqual(appbuilder.validate_declared(json.dumps(raw,ensure_ascii=False)),expected);self.assertEqual(appbuilder.validate_declared(json.dumps(raw,ensure_ascii=True)),expected)
 def test_anchor_alias_tags_scope_and_complexity_still_blocked(self):
  for text in ['app: &ref {title: no}','app: *ref','!!python/object/apply:os.system [echo no]','unknown: yes','[1,2]','{"app":{"title":true}}']:
   with self.subTest(text=text),self.assertRaises(ValueError):appbuilder.validate_declared(text)
  with self.assertRaisesRegex(ValueError,'too complex'):appbuilder.validate_declared(json.dumps({'app':{'examples':['x']*11000}}))
 def test_native_scanner_unavailable_falls_back_safely(self):
  with patch('yaml.CSafeLoader',yaml.SafeLoader):self.assertEqual(appbuilder.validate('{"app":{"title":"Example"}}')['app']['title'],'Example')
 def test_cs_scanner_surrogate_rejection_keeps_prior_accepted_json(self):
  text=json.dumps({'app':{'title':'Garden 🌱'}},ensure_ascii=True);self.assertEqual(appbuilder.validate(text)['app']['title'],'Garden 🌱')
 def test_recovery_query_can_survive_manual_navigation_hash(self):
  text=(Path(__file__).parents[1]/'chatify/web/appbuilder.js').read_text();self.assertIn("get('recovered')",text);self.assertIn("recoveredHandoff.match(/^([0-9a-f]{32})$/)",text)

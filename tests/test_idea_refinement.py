import json,unittest
from unittest.mock import Mock
from chatify import appbuilder,schema
class IdeaRefinement(unittest.TestCase):
 def setUp(self):self.cfg=schema.validate({'provider':{'type':'openai','model':'selected-model'}})
 def call(self,p,**overrides):return appbuilder.refine_idea(p,self.cfg,{'consent':True,'brief':'weather app',**overrides})
 def test_one_call_text_only_no_configuration(self):
  p=Mock();p.complete.return_value=json.dumps({'brief':'Weather app. Suggested audience: people planning outdoor activities. Review a suitable forecast source connection before use.'});r=self.call(p);self.assertEqual(p.complete.call_count,1);self.assertFalse(r['changed']);self.assertNotIn('yaml',r);self.assertIn('Weather app',r['brief'])
 def test_no_consent_no_call(self):
  p=Mock()
  with self.assertRaises(ValueError):self.call(p,consent=False)
  p.complete.assert_not_called()
 def test_mock_no_call(self):
  p=Mock();self.cfg['provider']['type']='mock'
  with self.assertRaises(ValueError):self.call(p)
  p.complete.assert_not_called()
 def test_empty_oversized_secret_no_call(self):
  for text in ('','x'*4001,'api_key=PRIVATEFIXTURE'):
   p=Mock()
   with self.assertRaises(ValueError):self.call(p,brief=text)
   p.complete.assert_not_called()
 def test_invalid_output_not_applied(self):
  for output in ('not json','{}','{"brief":""}','{"brief":"okay","config":{}}',json.dumps({'brief':'x'*4001}),'{"brief":"password=PRIVATEFIXTURE"}'):
   p=Mock();p.complete.return_value=output
   with self.assertRaises(ValueError):self.call(p)
   self.assertEqual(p.complete.call_count,1)
 def test_generic_input_and_explicit_constraints_pass_unchanged(self):
  text='A birdwatching app for children. Spanish only. No GPS. Only my supplied notes.';p=Mock();p.complete.return_value=json.dumps({'brief':text});r=self.call(p,brief=text);self.assertEqual(p.complete.call_args.args[0][1]['content'],text);self.assertEqual(r['brief'],text)
 def test_private_configuration_not_disclosed(self):
  self.cfg['sources']=[{'type':'http_json','url':'https://private.invalid','label':'PRIVATE_SOURCE'}];p=Mock();p.complete.return_value='{"brief":"A weather app"}';self.call(p);self.assertNotIn('private.invalid',str(p.complete.call_args));self.assertNotIn('PRIVATE_SOURCE',str(p.complete.call_args))
 def test_error_no_automatic_retry(self):
  p=Mock();p.complete.side_effect=RuntimeError('fixture failure')
  with self.assertRaises(RuntimeError):self.call(p)
  self.assertEqual(p.complete.call_count,1)

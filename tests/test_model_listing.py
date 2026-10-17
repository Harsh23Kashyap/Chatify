import unittest
from unittest.mock import patch
from chatify import providers, schema

class ModelListingTests(unittest.TestCase):
 def cfg(self, kind='mock'):
  return schema.validate({'provider':{'type':kind,'model':'fixture','api_key_env':'CUSTOM_KEY'}})
 def test_gemini_paginated_normalized(self):
  pages=[{'models':[{'name':'models/gemini-fixture','supportedGenerationMethods':['generateContent']},{'name':'models/embed','supportedGenerationMethods':['embedContent']}],'nextPageToken':'x y'}, {'models':[{'name':'models/gemini-next','supportedGenerationMethods':['generateContent']}]}]
  with patch.object(providers,'_key',return_value='not-real') as key,patch.object(providers,'_get',side_effect=pages) as get:
   self.assertEqual(providers.list_models(self.cfg('gemini'),'gemini','https://example.test/v1beta'),['gemini-fixture','gemini-next'])
   self.assertIn('/v1beta/models?pageSize=100',get.call_args_list[0].args[0]);self.assertNotIn('/v1beta/v1beta',get.call_args_list[0].args[0]);self.assertIn('pageToken=x+y',get.call_args_list[1].args[0]);self.assertEqual(get.call_args_list[0].args[1],{'x-goog-api-key':'not-real'});key.assert_called_with('CUSTOM_KEY','gemini')
 def test_claude_paginated(self):
  with patch.object(providers,'_key',return_value='not-real'),patch.object(providers,'_get',side_effect=[{'data':[{'id':'claude-a'}],'has_more':True,'last_id':'a'},{'data':[{'id':'claude-b'}],'has_more':False}]) as get:
   self.assertEqual(providers.list_models(self.cfg('claude'),'claude','https://example.test/v1'),['claude-a','claude-b']);self.assertIn('after_id=a',get.call_args_list[1].args[0])
 def test_all_compatible_providers(self):
  for kind in ['openai','openai_compatible','deepseek','groq','openrouter','mistral','minimax','mimo']:
   with self.subTest(kind=kind),patch.object(providers,'_key',return_value='not-real'),patch.object(providers,'_get',return_value={'data':[{'id':'fixture'},None,{'id':None},{}]}) as get:
    self.assertEqual(providers.list_models(self.cfg(kind),kind),['fixture']);url,headers=get.call_args.args;self.assertTrue(url.endswith('/models'));self.assertEqual(headers,{'api-key':'not-real'} if kind=='mimo' else {'Authorization':'Bearer not-real'})
 def test_array_response(self):
  with patch.object(providers,'_key',return_value='not-real'),patch.object(providers,'_get',return_value=[{'id':'fixture'}]):self.assertEqual(providers.list_models(self.cfg('openai'),'openai'),['fixture'])
 def test_ollama_and_demo(self):
  with patch.object(providers,'_get',return_value={'models':[{'name':'local:latest'}]}):self.assertEqual(providers.list_models(self.cfg(),'ollama'),['local:latest'])
  self.assertEqual(providers.list_models(self.cfg(),'mock'),['demo'])
 def test_list_error_not_model_generation_error(self):
  with patch.object(providers,'_key',return_value='not-real'),patch.object(providers,'_get',side_effect=providers.ProviderError('bad',400)):
   with self.assertRaises(providers.ProviderError) as cm:providers.list_models(self.cfg('gemini'),'gemini')
   self.assertIn('model-list request',str(cm.exception));self.assertNotIn('model name',str(cm.exception))
 def test_invalid_responses_do_not_crash(self):
  for kind in ['gemini','claude','ollama','openai']:
   with self.subTest(kind=kind),patch.object(providers,'_key',return_value='not-real'),patch.object(providers,'_get',return_value=None):
    with self.assertRaises(providers.ProviderError):providers.list_models(self.cfg(),kind)
 def test_repeated_cursor_stops(self):
  with patch.object(providers,'_key',return_value='not-real'),patch.object(providers,'_get',return_value={'models':[{'name':'models/gemini-fixture','supportedGenerationMethods':['generateContent']}],'nextPageToken':'same'}) as get:
   self.assertEqual(providers.list_models(self.cfg('gemini'),'gemini'),['gemini-fixture']);self.assertEqual(get.call_count,2)
 def test_catalog_has_every_provider_and_sources(self):
  from chatify.modelcatalog import CATALOG,suggestions
  self.assertEqual(set(CATALOG),schema.PROVIDERS)
  for kind in CATALOG:
   self.assertTrue(suggestions(kind))
   self.assertTrue(all(x['source'].startswith('https://') for x in suggestions(kind) if kind!='mock'))

 def test_missing_key_is_not_reported_as_refused(self):
  with patch.object(providers,'_key',side_effect=providers.ProviderError('No API key yet. Paste one under Model, Save key.',401)):
   with self.assertRaises(providers.ProviderError) as cm:providers.list_models(self.cfg('gemini'),'gemini')
   self.assertIn('No API key yet',str(cm.exception));self.assertNotIn('refused',str(cm.exception));self.assertNotIn('HTTP',str(cm.exception))

import unittest,urllib.error,json
import test_workspace_api
class GuideHTTP(test_workspace_api.WorkspaceAPITests):
 def test_guide_owner_gate(self):
  with self.assertRaises(urllib.error.HTTPError) as e:self.call(self.clients[1],'/api/settings/guide',{'question':'font','consent':True})
  self.assertEqual(e.exception.code,403)
 def test_guide_auth_and_applied_demo(self):
  import urllib.request
  with self.assertRaises(urllib.error.HTTPError):self.call(urllib.request.build_opener(),'/api/settings/guide',{'question':'font','consent':True})
  for data in ({'question':'font','consent':False},{'question':'font','consent':True},{'question':'password=fixture','consent':True}):
   with self.assertRaises(urllib.error.HTTPError) as e:self.call(self.clients[0],'/api/settings/guide',data)
   self.assertEqual(e.exception.code,400)
 def test_guide_engine_uses_no_private_state(self):
  class Fixture:
   def complete(inner,m):inner.payload=m;return '{"answer":"Open Fonts","sections":["sec-fonts","evil"]}'
  p=Fixture();self.engine.provider=p;self.cfg['provider']['type']='openai';self.cfg['provider']['model']='fixture';self.cfg['sources']=[{'url':'PRIVATE_SENTINEL_URL'}]
  r=self.call(self.clients[0],'/api/settings/guide',{'question':'make font bigger','consent':True});self.assertEqual(r['sections'],['sec-fonts']);self.assertFalse(r['changed']);self.assertNotIn('PRIVATE_SENTINEL',json.dumps(p.payload));self.assertEqual(r['provider'],'openai')

 def test_guide_selected_provider_and_model_transport(self):
  from unittest.mock import patch
  from chatify import providers
  for kind,model in [('openai','user-openai-model'),('claude','user-claude-model'),('gemini','user-gemini-model'),('ollama','user-local-model'),('openai_compatible','user-custom-model')]:
   with self.subTest(provider=kind):
    self.cfg['provider'].update(type=kind,model=model,base_url='',fallback=None)
    self.engine.provider=providers.make(self.cfg)
    calls=[]
    def transport(url,body,headers,timeout):
     calls.append((url,body))
     answer='{"answer":"Use Model","sections":["sec-model"]}'
     if kind=='claude':return {'content':[{'type':'text','text':answer}]}
     if kind=='gemini':return {'candidates':[{'content':{'parts':[{'text':answer}]}}]}
     if kind=='ollama':return {'message':{'content':answer}}
     return {'choices':[{'message':{'content':answer}}]}
    with patch('chatify.providers._key',return_value='test-only'),patch('chatify.providers._post',side_effect=transport):
     original=dict(self.cfg['provider']);self.cfg['provider']['type']='mock';self.cfg['provider']['model']='applied-demo'
     result=self.call(self.clients[0],'/api/settings/guide',{'question':'Which model setting?','consent':True,'selection':{'provider':kind,'model':model,'base_url':''}})
     self.assertEqual(self.cfg['provider']['type'],'mock');self.assertEqual(self.cfg['provider']['model'],'applied-demo')
    self.assertEqual(result['provider'],kind);self.assertEqual(result['model'],model);self.assertEqual(len(calls),1)
    if kind=='gemini':self.assertIn('/'+model+':generateContent',calls[0][0])
    else:self.assertEqual(calls[0][1]['model'],model)

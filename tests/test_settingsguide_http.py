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

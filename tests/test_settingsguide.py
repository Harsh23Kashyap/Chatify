import unittest,json
from chatify import settingsguide as g
class Fake:
 def __init__(self,text):self.text=text;self.calls=[]
 def complete(self,m):self.calls.append(m);return self.text
class TestSettingsGuide(unittest.TestCase):
 def setUp(self):self.cfg={'provider':{'type':'openai','model':'fixture','key':'PRIVATE_KEY_SENTINEL'},'sources':[{'url':'PRIVATE_URL_SENTINEL'}]};self.p=Fake('{"answer":"Open Fonts","sections":["sec-fonts","evil","sec-fonts"]}')
 def test_allowlist_and_private_config(self):
  r=g.guide(self.p,self.cfg,'make font big',True);self.assertEqual(r['sections'],['sec-fonts']);self.assertFalse(r['changed']);self.assertNotIn('PRIVATE_',str(self.p.calls))
 def test_consent(self):
  with self.assertRaises(ValueError):g.guide(self.p,self.cfg,'font',False)
  self.assertFalse(self.p.calls)
 def test_demo(self):
  with self.assertRaises(ValueError):g.guide(self.p,{'provider':{'type':'mock'}},'font',True)
 def test_bad_query(self):
  for q in ['',None,'x'*1201,'api_key=sk-testcredential00000000','password=secret']:
   with self.assertRaises(ValueError):g.guide(self.p,self.cfg,q,True)
 def test_malformed(self):
  for t in ['invalid','[]','{"answer":[]}','{"answer":""}']:
   with self.assertRaises(ValueError):g.guide(Fake(t),self.cfg,'font',True)
 def test_missing_or_bad_links(self):
  for v in [None,17,['evil',None]]:
   r=g.guide(Fake(json.dumps({'answer':'Guide','sections':v})),self.cfg,'font',True);self.assertEqual(r['sections'],[])

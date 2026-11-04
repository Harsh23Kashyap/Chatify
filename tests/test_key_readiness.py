"""Offline status follows actual connector key lookup, not model or service calls."""
import tempfile,unittest,os
from unittest.mock import patch
from chatify import schema,secrets
from chatify.store import Store
from chatify.pipeline import Engine
from chatify.management import Management
class KeyReadiness(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=secrets.STORE;secrets.STORE=secrets.SecretStore(self.tmp.name)
 def tearDown(self):secrets.STORE=self.old;self.tmp.cleanup()
 def check(self,sources):
  cfg=schema.validate({'sources':sources});cfg['_dir']=self.tmp.name;engine=Engine(cfg,Store(':memory:'));m=Management(cfg,engine,lambda:{},lambda x:None,lambda _:[])
  with patch('chatify.providers._post') as post,patch('urllib.request.urlopen') as request:result=m.status('owner')
  post.assert_not_called();request.assert_not_called();return result
 def test_saved_search_and_openalex_recognized_then_removed(self):
  sources=[{'id':'search','type':'web_search','label':'Search','providers':['brave']},{'id':'papers','type':'openalex','label':'Papers'}]
  with patch.dict(os.environ,{},clear=True):
   before=self.check(sources);self.assertEqual([r['state'] for r in before['rows'] if r['item'] in ('Search / Brave Search','Papers access')],['setup','setup'])
   secrets.STORE.set('search:brave','OFFLINE-FAKE');secrets.STORE.set('catalog:openalex','OFFLINE-FAKE')
   after=self.check(sources);self.assertEqual([r['state'] for r in after['rows'] if r['item'] in ('Search / Brave Search','Papers access')],['present','present']);self.assertNotIn('OFFLINE-FAKE',str(after))
 def test_native_http_store_lookup_and_no_credential_echo(self):
  from chatify.source_credentials import name
  src={'id':'remote','label':'Remote','type':'http_json','url':'https://source.invalid/items?q={query}','header_env':{'X-Key':'REMOTE_KEY'}}
  with patch.dict(os.environ,{},clear=True):
   self.assertEqual(next(r for r in self.check([src])['rows'] if r['item']=='Remote / REMOTE_KEY')['state'],'setup')
   secrets.STORE.set(name('remote','REMOTE_KEY',src['url']),'OFFLINE-FAKE')
   result=self.check([src]);self.assertEqual(next(r for r in result['rows'] if r['item']=='Remote / REMOTE_KEY')['state'],'present');self.assertNotIn('OFFLINE-FAKE',str(result))
 def test_python_does_not_claim_native_saved_key_is_in_environment(self):
  src={'id':'plugin','label':'Plugin','type':'python','entry':'fixture:search','execution':'bounded','api_key_env':'PLUGIN_KEY'}
  secrets.STORE.set('PLUGIN_KEY','OFFLINE-FAKE')
  with patch.dict(os.environ,{},clear=True):self.assertEqual(next(r for r in self.check([src])['rows'] if r['item']=='Plugin / PLUGIN_KEY')['state'],'setup')
 def test_environment_lookup_for_search_http_and_catalog(self):
  with patch.dict(os.environ,{'BRAVE_API_KEY':'OFFLINE-FAKE','OPENALEX_API_KEY':'OFFLINE-FAKE'},clear=True):
   result=self.check([{'id':'s','label':'Search','type':'web_search','providers':['brave']},{'id':'o','label':'Papers','type':'openalex'}]);self.assertEqual([r['state'] for r in result['rows'] if r['item'] in ('Search / Brave Search','Papers access')],['present','present'])

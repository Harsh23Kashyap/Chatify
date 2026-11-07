import json, tempfile, threading, unittest, urllib.request, urllib.error
from http.server import ThreadingHTTPServer
from chatify import schema
from chatify.store import Store
from chatify.pipeline import Engine
from chatify.server import make_handler
from chatify.providers import ProviderError

class PromptSampleRoute(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.cfg=schema.validate({'provider':{'type':'openai','model':'fixture-only'},'sources':[],'storage':{'path':self.tmp.name+'/store.db'}});self.cfg['_dir']=self.tmp.name
  self.store=Store(self.cfg['storage']['path']);self.engine=Engine(self.cfg,self.store)
  self.calls=[];self.fail=False
  outer=self
  class FixtureProvider:
   def complete(self,messages):
    outer.calls.append(messages)
    if outer.fail:raise ProviderError('Fixture provider unavailable')
    return 'VALID'
  self.engine.provider=FixtureProvider()
  self.server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(self.cfg,self.engine));threading.Thread(target=self.server.serve_forever,daemon=True).start();self.root='http://127.0.0.1:'+str(self.server.server_port)
 def tearDown(self):self.server.shutdown();self.server.server_close();self.tmp.cleanup()
 def api(self,path,body=None):
  req=urllib.request.Request(self.root+path,data=None if body is None else json.dumps(body).encode(),headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(req) as r:return json.load(r)
 def test_exact_unsaved_prompt_without_runtime_suffix_or_retrieval(self):
  before=self.api('/api/prompts');payload={'key':'question_check','text':'Exact system $50 "quoted"\nNo suffix','question':'Sample?','passages':''}
  self.assertEqual(self.api('/api/prompts/test',payload),{'ok':True,'output':'VALID'})
  self.assertEqual(self.calls,[[{'role':'system','content':payload['text']},{'role':'user','content':'Sample?'}]])
  self.assertEqual(self.api('/api/prompts'),before);self.assertEqual(self.api('/api/budget')['used'],{'model':1})
 def test_optional_passages_are_user_data_not_system(self):
  self.api('/api/prompts/test',{'text':'system','question':'q','passages':'data'})
  self.assertEqual(self.calls[0],[{'role':'system','content':'system'},{'role':'user','content':'q\n\nPassages:\ndata'}])
 def test_empty_input_no_invocation(self):
  for body in [{'text':'','question':'q'},{'text':'system','question':' '}]:
   with self.assertRaises(urllib.error.HTTPError) as e:self.api('/api/prompts/test',body)
   self.assertEqual(e.exception.code,400)
  self.assertEqual(self.calls,[]);self.assertEqual(self.api('/api/budget')['used'],{})
 def test_error_counts_one_and_does_not_mutate_prompt(self):
  before=self.api('/api/prompts');self.fail=True
  result=self.api('/api/prompts/test',{'text':'system','question':'q'})
  self.assertFalse(result['ok']);self.assertEqual(result['error'],'Fixture provider unavailable');self.assertEqual(len(self.calls),1)
  self.assertEqual(self.api('/api/budget')['used'],{'model':1});self.assertEqual(self.api('/api/prompts'),before)
 def test_server_length_contract(self):
  self.api('/api/prompts/test',{'text':'x'*6100,'question':'y'*1100,'passages':'z'*6100})
  self.assertEqual(len(self.calls[0][0]['content']),6000);self.assertEqual(self.calls[0][1]['content'],'y'*1000+'\n\nPassages:\n'+'z'*6000)
if __name__=='__main__':unittest.main()

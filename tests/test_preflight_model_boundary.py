"""Source-only preflight must not invoke retrieval's paid expansion rescue.
Real Engine/Management with frozen empty connector; no network or actual model.
"""
import unittest,time
from unittest.mock import Mock
from chatify import schema
from chatify.pipeline import Engine
from chatify.store import Store
from chatify.management import Management
class SourcePreflightModelBoundary(unittest.TestCase):
 def run_check(self,model):
  cfg=schema.validate({'provider':{'type':'openai','model':'gpt-4o-mini'},'sources':[{'id':'arxiv','type':'arxiv','label':'arxiv'}],'retrieval':{'query_expansion':True,'rerank':False}})
  conn=Mock();conn.search.return_value=[];conn.refresh.return_value=False
  provider=Mock();provider.complete.return_value='OK'
  e=Engine(cfg,Store(':memory:'),provider=provider,connectors={'arxiv':conn})
  m=Management(cfg,e,lambda:{},lambda _:None,e.store.export_all)
  plan=m.prepare_live('a',{'model':model,'sources':['arxiv']})
  self.assertEqual(plan['model_calls'],int(model))
  jid=m.start('a','preflight',{'ticket':plan['ticket'],'confirmed':True})['id']
  for _ in range(100):
   result=m.job('a',jid)
   if result['state']!='running':break
   time.sleep(.01)
  self.assertEqual(result['state'],'done')
  self.assertEqual(provider.complete.call_count,int(model))
  self.assertEqual(conn.search.call_count,1)
  self.assertTrue(cfg['retrieval']['query_expansion'])
  self.assertEqual(e.store.chats('a'),[])
 def test_source_only_zero_model_calls(self):self.run_check(False)
 def test_selected_model_exactly_one_probe(self):self.run_check(True)

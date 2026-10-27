import unittest
from unittest.mock import Mock
from chatify import schema
from chatify.pipeline import Engine
from chatify.store import Store
from chatify.suggestions import starters,recent,clean
class Suggestions(unittest.TestCase):
    def engine(self):
        cfg=schema.validate({'app':{'title':'Diet Chat','examples':['What are the protein sources?']}})
        return Engine(cfg,Store(':memory:'))
    def test_demo_never_calls_model(self):
        e=self.engine();e.provider=Mock();self.assertEqual(starters(e)['origin'],'configured');e.provider.complete.assert_not_called()
    def test_non_mock_cold_and_repeat_loads_never_call_model(self):
        e=self.engine();e.cfg['provider'].update(type='openai',model='cheap-test');e.provider=Mock()
        e.provider.complete.side_effect=AssertionError('page load must not infer')
        expected={'questions':['What are the protein sources?'],'origin':'configured'}
        self.assertEqual(starters(e),expected);self.assertEqual(starters(e),expected)
        e.cfg['prompt']['system']='New scope'
        self.assertEqual(starters(e),expected);e.provider.complete.assert_not_called()
    def test_examples_change_without_old_generated_cache(self):
        e=self.engine();e.provider=Mock()
        e.store.get_state=Mock(side_effect=AssertionError('generated cache must not be used'))
        self.assertEqual(starters(e)['questions'],['What are the protein sources?'])
        e.cfg['app']['examples']=['What topics do the sources cover?']
        self.assertEqual(starters(e)['questions'],e.cfg['app']['examples'])
        e.provider.complete.assert_not_called()
    def test_empty_examples_fallback_without_model_or_budget(self):
        from chatify.budget import Budget
        e=self.engine();e.cfg['provider'].update(type='openai',model='cheap-test')
        e.cfg['app']['examples']=[];provider=Mock();provider.complete.return_value='What topics do the sources cover?';e.provider=Budget(e.cfg).wrap(provider)
        self.assertEqual(starters(e)['origin'],'fallback');self.assertTrue(starters(e)['questions'])
        self.assertEqual(e.provider.budget.view()['used'],{});provider.complete.assert_not_called()
    def test_recent_private_deleted_and_deduped(self):
        e=self.engine();s=e.store
        for owner,q in [('alice','How much fiber is in beans?'),('bob','What is my private history?'),('alice','How much fiber is in beans?')]:
            c=s.new_chat(owner);t=s.add_turn(c,None,q,q,'',[],[],'standard')
        self.assertEqual(recent(s,'alice'),['How much fiber is in beans?'])
        s.delete_turn('alice',t);s.delete_chat('alice',s.chats('alice')[1]['id'])
        self.assertEqual(recent(s,'alice'),[])
    def test_filter_bounded_safe_distinct(self):
        self.assertEqual(clean(['<script>evil?</script>','x?','What are the protein sources?','What are the protein sources?']),['What are the protein sources?'])
    def test_http_temporary_hides_recent(self):
        import threading,json,urllib.request
        from chatify.server import LocalHTTPServer,make_handler
        e=self.engine();e.cfg['provider'].update(type='openai',model='cheap-test');e.provider=Mock();e.provider.complete.side_effect=AssertionError('HTTP starter load must not infer');raw_provider=e.provider;c=e.store.new_chat('local');e.store.add_turn(c,None,'How much fiber is in beans?','','',[],[],'standard')
        srv=LocalHTTPServer(('127.0.0.1',0),make_handler(e.cfg,e));threading.Thread(target=srv.serve_forever,daemon=True).start()
        try:
            def call(temp):
                req=urllib.request.Request('http://127.0.0.1:'+str(srv.server_port)+'/api/suggestions',data=json.dumps({'temporary':temp}).encode(),headers={'Content-Type':'application/json'})
                return json.load(urllib.request.urlopen(req))
            self.assertEqual(call(True)['recent'],[])
            self.assertTrue(call(False)['questions'])
            raw_provider.complete.assert_not_called()
            self.assertEqual(e.provider.budget.view()['used'],{})
        finally:srv.shutdown();srv.server_close()
    def test_recent_ui_cross_group_dedupe(self):
        from pathlib import Path
        js=(Path('chatify/web')/'app.js').read_text()
        self.assertIn('recent.filter(x=>!shown.has',js)
        self.assertIn('TV("txt_examples")',js)

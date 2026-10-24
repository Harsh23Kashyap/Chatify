import unittest, tempfile, os
from chatify import schema
from chatify.pipeline import Engine
from chatify.store import Store
from chatify.connectors.base import Evidence
class NewsRegression(unittest.TestCase):
    def engine(self):
        cfg=schema.validate({'sources':[{'id':'feed','type':'http_json','label':'Feed','url':'https://example.org/a','results_path':'items'}],'retrieval':{'cache_ttl':100}})
        return Engine(cfg,Store(':memory:'))
    def test_source_config_change_invalidates_cache(self):
        e=self.engine()
        class C:
            def __init__(self,title):self.title=title
            def search(self,q,k):return [Evidence('news '+self.title,self.title,'https://example.org/'+self.title,[],2026,'','feed',1)]
        e.connectors['feed']=C('First');self.assertEqual(e.retrieve('news')[0][0]['title'],'news First')
        e.cfg['sources'][0]['url']='https://example.org/b';e.connectors['feed']=C('Second');self.assertEqual(e.retrieve('news')[0][0]['title'],'news Second')
    def test_numeric_cleanup_does_not_leave_fragment(self):
        e=self.engine();ev=[{'n':1,'title':'AI report','text':'AI report','year':'2026','source':'feed','url':'https://example.org'}]
        claim='This report occurred on 2026-10-10'
        out,evidence,_=e._drop_uncited_numbers('The U.S. '+claim,ev,[{'claim':claim,'cites':[]}],'dates')
        self.assertIn('[1]',out);self.assertTrue(evidence)
    def test_chart_prompt_requires_sample_only_numeric_data(self):
        e=self.engine();p=e.prompt('Make an AI chart',[],'standard',[], '')[0]['content'];self.assertIn('markdown table',p);self.assertIn('Never invent measurements',p)
    def test_headline_prompt_requires_attribution(self):
        e=self.engine();self.assertIn('not independent verification or consensus',e.prompt('news',[],'standard',[],'')[0]['content'])
    def test_chart_count_is_computed_not_invented(self):
        text=Engine.headline_chart('chart headline count',[{'n':1,'source':'feed'},{'n':2,'source':'feed'}]);self.assertIn('| feed | 2 | [1] [2] |',text)
        self.assertEqual(Engine.headline_chart('plot global employment',[]),'')
    def test_numeric_cleanup_removes_whole_line(self):
        e=self.engine();ev=[{'n':1,'title':'AI report','text':'AI report','year':'2026','source':'feed','url':'https://example.org'}]
        claim='This was reported on 2026-10-10'
        out,_,_=e._drop_uncited_numbers('"AI report. '+claim+'"\nSupported AI report [1].',ev,[{'claim':claim,'cites':[]}],'dates')
        self.assertNotIn('"AI report.',out);self.assertIn('[1]',out)
    def test_natural_language_rest_query_has_keyword_fallback(self):
        e=self.engine();self.assertIn('AI',e.queries('Summarize AI headlines with citations.'))
    def test_short_keyword_not_changed(self):
        e=self.engine();self.assertEqual(e.queries('AI'),['AI'])
    def test_chart_refuses_non_count_world_data(self):
        e=self.engine();ev=[{'n':1,'source':'feed'}]
        self.assertEqual(Engine.headline_chart('plot global employment',ev),'')
if __name__=='__main__':unittest.main()

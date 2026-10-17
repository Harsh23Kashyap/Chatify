import copy, unittest
from unittest.mock import patch
from chatify import schema, providers
from chatify.pipeline import Engine
from chatify.store import Store
from chatify.connectors.base import Evidence

class Connector:
    def __init__(self): self.calls=[]
    def search(self,q,k):
        self.calls.append(k)
        return [Evidence('Aerodynamics finding '+str(i), 'Aerodynamics affects car performance via tested detail '+str(i)+'.', 'https://example.test/'+str(i),source='s',score=1/(i+1)) for i in range(k)]

class AnswerDepth(unittest.TestCase):
    def engine(self, raw=None):
        c=schema.validate(raw or {'sources':[{'id':'s','type':'wikipedia'}]}); con=Connector()
        return Engine(c,Store(':memory:'),connectors={'s':con}),con
    def test_defaults_and_prompts(self):
        e,_=self.engine()
        self.assertEqual(e.cfg['retrieval']['top_k'],12)
        self.assertEqual(e.cfg['provider']['max_output_tokens'],4096)
        self.assertIn('Do not pad',e.cfg['prompt']['style']['standard'])
        self.assertIn('sparse evidence',e.cfg['prompt']['style']['standard'])
        self.assertEqual(e.cfg['prompt']['style']['quick'],'Answer in 2 to 4 sentences.')
    def test_deep_retrieval_and_cache_isolation(self):
        e,c=self.engine()
        self.assertEqual(len(e.retrieve('aerodynamics')[0]),12)
        self.assertEqual(len(e.retrieve('aerodynamics',style='deep')[0]),24)
        self.assertEqual(len(e.retrieve('aerodynamics')[0]),12)
        self.assertEqual(c.calls,[12,24])
        e.cfg['retrieval']['top_k']=40
        self.assertEqual(e.retrieval_limit('deep'),50)
    def test_explicit_limits_preserved(self):
        e,_=self.engine({'retrieval':{'top_k':3},'provider':{'max_output_tokens':1024}})
        self.assertEqual(e.retrieval_limit(),3);self.assertEqual(e.retrieval_limit('deep'),6)
        self.assertEqual(e.cfg['provider']['max_output_tokens'],1024)
    def test_invalid_output_limit(self):
        for n in [-1,0,255,32769,1.5,True,'4096',float('nan')]:
            with self.subTest(n=n):self.assertRaises(schema.ConfigError,schema.validate,{'provider':{'max_output_tokens':n}})
            with self.subTest(fallback=n):self.assertRaises(schema.ConfigError,schema.validate,{'provider':{'fallback':{'type':'mock','max_output_tokens':n}}})
    def test_openai_and_reasoning_request_fields(self):
        for model,key in [('gpt-4.1-mini','max_tokens'),('gpt-5','max_completion_tokens'),('o3','max_completion_tokens')]:
            c=schema.validate({'provider':{'type':'openai','model':model,'max_output_tokens':6000}})
            p=providers.OpenAICompatible(c);b=p._body([],stream=True)
            self.assertEqual(b[key],6000);self.assertNotIn('max_tokens' if key=='max_completion_tokens' else 'max_completion_tokens',b)
            if key=='max_completion_tokens':self.assertNotIn('temperature',b)
    def test_claude_limit(self):
        c=schema.validate({'provider':{'type':'claude','model':'model','max_output_tokens':6000}})
        p=providers.Claude(c)
        with patch('chatify.providers._key',return_value='test'),patch('chatify.providers._post',return_value={'content':[{'type':'text','text':'ok'}]}) as post:
            self.assertEqual(p.complete([]),'ok');self.assertEqual(post.call_args.args[1]['max_tokens'],6000)
    def test_deep_mode_reaches_stream_and_fresh(self):
        e,c=self.engine()
        list(e.ask_stream('local',None,'Explain aerodynamics',style='deep',temporary=True))
        self.assertTrue(c.calls and all(k == 24 for k in c.calls))
        e._fresh('aerodynamics',None,style='deep');self.assertEqual(c.calls[-1],24)
    def test_expanded_prompt_fits_default_budget(self):
        e,c=self.engine();ev=c.search('aerodynamics',50)
        for i,x in enumerate(ev,1):x['n']=i;x['text']='Source content. '*400
        messages=e.prompt('Explain aerodynamics',ev,'deep',[],'')
        self.assertLess(sum(len(m['content']) for m in messages),e.context_budget())
        self.assertIn('[50]',messages[1]['content'])

if __name__=='__main__':unittest.main()

class FormulaOneSources(unittest.TestCase):
    def test_fia_snapshots_have_original_links_and_real_text(self):
        import sys
        from pathlib import Path
        base=Path(__file__).resolve().parents[1]/'Formula One Chat'
        if not base.exists(): self.skipTest('F1 app assets are not in this checkout')
        sys.path.insert(0,str(base))
        from f1_sources import search
        for query,expected in [('aerodynamic influence bodywork','technical'),('pit lane pit stops','sporting'),('fire extinguishers','technical')]:
            rows=search(query,12)
            self.assertTrue(0 < len(rows) <= 12)
            self.assertTrue(any(expected in x['url'] for x in rows))
            self.assertTrue(all(x['text'] and x['url'].startswith('https://www.fia.com/system/files/documents/') for x in rows))
        for name in ['app.yaml','Formula One Chat.yaml']:
            c=schema.load(str(base/name))
            self.assertEqual(c['retrieval']['top_k'],12)
            self.assertEqual(c['provider']['max_output_tokens'],4096)
            self.assertEqual(c['sources'][0]['entry'],'f1_sources:search')

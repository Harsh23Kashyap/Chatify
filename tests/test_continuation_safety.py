"""Local continuation regression tests. No external providers or credentials."""
import unittest
from unittest.mock import patch
from customchat import schema
from customchat.pipeline import Engine
from customchat.store import Store

class ContinuationSafety(unittest.TestCase):
    def engine(self, news=True):
        cfg=schema.validate({'app':{'id':'newsnerd' if news else 'other','title':'NewsNerd' if news else 'Other'}})
        return Engine(cfg,Store(':memory:'))
    def ev(self, title='Fresh'):
        return [{'n':1,'source':'feed','title':title,'text':title+' article content','year':'2026','url':'https://example.org/'+title}]
    def test_hindi_claim_cannot_be_presented_without_attribution(self):
        out=self.engine().attribute_news('- परमाणु ऊर्जा AI का भविष्य है [1].',self.ev())
        self.assertIn('स्रोत के अनुसार',out);self.assertIn('स्वतंत्र पुष्टि नहीं',out)
    def test_english_opinion_is_attributed(self):
        out=self.engine().attribute_news('Nuclear energy is the future of AI [1].',self.ev())
        self.assertIn('According to feed (not independently verified)',out)
    def test_attribution_is_idempotent(self):
        e=self.engine();out=e.attribute_news('A reported claim [1].',self.ev())
        self.assertEqual(e.attribute_news(out,self.ev()),out)
    def test_other_apps_unchanged(self):
        self.assertEqual(self.engine(False).attribute_news('A finding [1].',self.ev()),'A finding [1].')
    def test_table_remains_parseable(self):
        e=self.engine();t=e.headline_chart('chart headline count',self.ev());self.assertEqual(e.attribute_news(t,self.ev()),t)
    def test_duplicate_article_chunks_count_once(self):
        ev=self.ev();ev.append({**ev[0],'n':2});self.assertIn('| feed | 1 | [1] |',Engine.headline_chart('chart headline count',ev))
    def test_pipe_source_is_escaped(self):
        ev=self.ev();ev[0]['source']='A|B';self.assertIn('| A\\|B | 1 |',Engine.headline_chart('chart source count',ev))
    def followup(self,stream,scoped=False):
        e=self.engine(False);s=e.store;c=s.new_chat('local');a=s.new_topic('local','A');b=s.new_topic('local','B')
        good=s.add_turn(c,a,'prior','prior','prior',self.ev('Eligible'),[],'standard')
        other=s.add_turn(c,a if scoped else b,'private','private','private',self.ev('Wrong'),[],'standard')
        if scoped:s.save_state('local','scope-'+other,{'source':'feed'})
        e.connectors={'feed':object()}
        with patch.object(e,'retrieve',return_value=(self.ev('Fresh'),{})),patch.object(e,'filter_relevant',side_effect=lambda q,ev:ev):
            if stream:r=next(d for k,d in e.ask_stream('local',c,'chart those headline counts',topic=a) if k=='done')
            else:r=e.ask('local',c,'chart those headline counts',topic=a)
        self.assertEqual(r['evidence'][0]['title'],'Eligible')
    def test_sync_followup_respects_topic(self):self.followup(False)
    def test_stream_followup_respects_topic(self):self.followup(True)
    def test_sync_followup_excludes_scoped_turn(self):self.followup(False,True)
    def test_stream_followup_excludes_scoped_turn(self):self.followup(True,True)
    def test_attribution_runs_in_sync_and_stream_paths(self):
        for stream in (True,False):
            e=self.engine();s=e.store;c=s.new_chat('local');ev=self.ev()
            class Provider:
                def complete(self,m):return 'यह भविष्य है [1].'
                def stream(self,m):yield 'यह भविष्य है [1].'
            e.provider=Provider()
            with patch.object(e,'retrieve',return_value=(ev,{})),patch.object(e,'filter_relevant',side_effect=lambda q,ev:ev):
                r=next(d for k,d in e.ask_stream('local',c,'News') if k=='done') if stream else e.ask('local',c,'News')
            self.assertIn('स्रोत के अनुसार',r['answer'])
            self.assertEqual(s.turns('local',c)[-1]['answer'],r['answer'])
    def test_missing_publication_dates_is_clear_not_fallback(self):
        for stream in (False,True):
            e=self.engine();c=e.store.new_chat('local');ev=self.ev();ev[0]['year']=''
            with patch.object(e,'retrieve',return_value=(ev,{})),patch.object(e,'filter_relevant',side_effect=lambda q,x:x):
                q='List publication dates from these sources'
                r=next(d for k,d in e.ask_stream('local',c,q) if k=='done') if stream else e.ask('local',c,q)
            self.assertIn('not provided',r['answer']);self.assertNotIn('passages instead',r['answer'])
    def test_prompt_distinguishes_quoted_disagreement(self):
        p=self.engine().prompt('What do sources disagree about?',self.ev(),'standard',[],'')
        self.assertIn('differing people quoted inside a single article',p[0]['content'])
        self.assertIn('source: feed',p[1]['content'])
    def test_same_publisher_disagreement_guard_sync_stream(self):
        for stream in (False,True):
            e=self.engine();c=e.store.new_chat('local');ev=self.ev()
            with patch.object(e,'retrieve',return_value=(ev,{})),patch.object(e,'filter_relevant',side_effect=lambda q,x:x):
                q='What do sources disagree about?'
                r=next(d for k,d in e.ask_stream('local',c,q) if k=='done') if stream else e.ask('local',c,q)
            self.assertIn('do not establish a disagreement',r['answer'])

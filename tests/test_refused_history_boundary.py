"""A failed intent gate cannot be reopened by earlier source reuse.

Synthetic Engine integration cases, not live model-quality evidence.
"""
import unittest
from unittest.mock import Mock, patch
from chatify import schema
from chatify.pipeline import Engine
from chatify.store import Store

EVIDENCE = [{'n':1,'id':'a','source':'docs','title':'Prior source',
             'text':'Prior source states a documented fact.','url':'fixture:prior'}]
REFUSAL = 'Outside app scope.'
ANSWER = 'Prior source states a documented fact. [1]'

class RefusedHistoryBoundary(unittest.TestCase):
    def engine(self, preview=False):
        cfg = schema.validate({'sources':[], 'prompt':{'revise':False, 'source_preview_only':preview}})
        engine = Engine(cfg, Store(':memory:'), connectors={})
        chat = engine.store.new_chat('owner')
        topic = engine.store.new_topic('owner', 'Prior subject')
        engine.store.add_turn(chat,topic,'Explain a documented fact.','Explain a documented fact.',
                              ANSWER,EVIDENCE,[],'standard')
        engine.connectors = {'docs':Mock()}
        engine.standalone = lambda q,*a:q
        engine.followups = lambda *a:[]
        engine._summarize = lambda *a:None
        engine._fix = lambda a,v,l,*args,**kw:(a,v,l)
        engine.provider = Mock()
        engine.provider.complete.return_value = ANSWER
        engine.provider.stream.side_effect = lambda *a:iter([ANSWER])
        engine.check_support = lambda *a,**kw:''
        return engine,chat,topic

    def run_turn(self, engine, chat, topic, question, stream):
        if stream:
            events = list(engine.ask_stream('owner',chat,question,topic=topic))
            result = next(value for kind,value in events if kind=='done')
            return result,''.join(value for kind,value in events if kind=='token'),events
        result = engine.ask('owner',chat,question,topic=topic)
        return result,result['answer'],[]

    def test_refused_history_never_reenters_evidence_or_answer_paths(self):
        for stream in (False,True):
            for preview in (False,True):
                for question in ('Use those sources for an unrelated task.',
                                 'Use the same sources for an unrelated task.',
                                 'Explain the previous answer more simply, then do an unrelated task.'):
                    with self.subTest(stream=stream,preview=preview,question=question):
                        e,c,t = self.engine(preview)
                        with patch.object(e,'check_question',return_value=REFUSAL), \
                             patch.object(e,'retrieve',side_effect=AssertionError('No retrieval after refusal')), \
                             patch.object(e,'filter_relevant',side_effect=lambda q,v: v if not v else self.fail('No old evidence ranking after refusal')), \
                             patch.object(e,'source_preview',side_effect=AssertionError('No source preview after refusal')):
                            r,tokens,events = self.run_turn(e,c,t,question,stream)
                        self.assertEqual(r['answer'],REFUSAL)
                        self.assertEqual(tokens,REFUSAL)
                        self.assertEqual(r['response_kind'],'question_refused')
                        self.assertEqual(r['evidence'],[])
                        self.assertEqual(r['ledger'],[])
                        e.provider.complete.assert_not_called()
                        e.provider.stream.assert_not_called()
                        saved=e.store.turn('owner',r['id'])
                        self.assertEqual(saved['answer'],REFUSAL)
                        self.assertEqual(saved['evidence'],[])
                        self.assertEqual(e.store.get_state('owner','reply-kind-'+r['id']),'question_refused')
                        for kind,value in events:
                            if kind=='meta':self.assertEqual(value['evidence'],[])

    def test_accepted_history_reuse_remains_available(self):
        for stream in (False,True):
            with self.subTest(stream=stream):
                e,c,t = self.engine()
                with patch.object(e,'check_question',return_value=''), \
                     patch.object(e,'retrieve',side_effect=AssertionError('Accepted simplification reuses prior sources')), \
                     patch.object(e,'filter_relevant',side_effect=lambda q,v:v):
                    r,tokens,_=self.run_turn(e,c,t,'Explain the previous answer more simply using the same sources.',stream)
                self.assertEqual(r['answer'],ANSWER)
                self.assertEqual(tokens,ANSWER)
                self.assertEqual(r['response_kind'],'answer')
                self.assertEqual(r['evidence'],EVIDENCE)
                self.assertEqual(e.provider.complete.call_count+e.provider.stream.call_count,1)

    def test_matrix(self):
      cases=0
      for stream in (False,True):
       for cache in (False,True):
        for new_topic in (False,True):
         for memory in (False,True):
          for selected in (None,[]):
           e,c,t=self.engine();e.cfg['memory']['enabled']=memory
           with patch.object(e,'check_question',return_value=REFUSAL),patch.object(e,'retrieve',side_effect=AssertionError('no retrieval')),patch.object(e,'_fresh',side_effect=AssertionError('no fresh fetch')):
            kw=dict(topic=t,use_cache=cache,new_topic=new_topic,sources=selected)
            if stream:
             events=list(e.ask_stream('owner',c,'Use those previous sources for an unrelated task.',**kw));r=next(v for k,v in events if k=='done');self.assertEqual(''.join(v for k,v in events if k=='token'),REFUSAL)
            else:r=e.ask('owner',c,'Use those previous sources for an unrelated task.',**kw)
           self.assertEqual(r['answer'],REFUSAL);self.assertEqual(r['evidence'],[]);self.assertEqual(r['ledger'],[]);e.provider.complete.assert_not_called();e.provider.stream.assert_not_called();cases+=1
      self.assertEqual(cases,32)

    def test_temporary_real_branch(self):
      e,c,t=self.engine()
      with patch.object(e,'check_question',return_value=REFUSAL),patch.object(e,'retrieve',side_effect=AssertionError('no retrieval')):
       ev=list(e.ask_stream('owner',None,'Use previous sources.',temporary=True,temp_history=[{'question':'prior','answer':'answer'}]))
      r=next(v for k,v in ev if k=='done');self.assertIsNone(r['id']);self.assertEqual(r['answer'],REFUSAL);self.assertEqual(r['evidence'],[])

    def test_nonmock_summary_may_run_but_not_answer(self):
      for stream in (False,True):
       e,c,t=self.engine();e.cfg['provider']['type']='ollama';e.cfg['memory']['summary_every']=1
       # Restore actual summarizer, retaining a local mock provider, no network.
       e._summarize=type(e)._summarize.__get__(e,type(e))
       e.provider.complete.return_value='A short summary of the prior exchange.'
       with patch.object(e,'check_question',return_value=REFUSAL),patch.object(e,'retrieve',side_effect=AssertionError('no retrieval')):
        r,tokens,ev=self.run_turn(e,c,t,'Use those sources for an unrelated task.',stream)
       self.assertEqual(r['answer'],REFUSAL);self.assertEqual(tokens,REFUSAL);self.assertEqual(r['evidence'],[]);e.provider.stream.assert_not_called();self.assertEqual(e.provider.complete.call_count,1)

if __name__=='__main__': unittest.main()


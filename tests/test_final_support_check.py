import unittest
from unittest.mock import patch
from chatify import schema
from chatify.pipeline import Engine
from chatify.store import Store
class FinalSupport(unittest.TestCase):
 def test_sync_and_stream_check_final_corrected_answer(self):
  for stream in (False,True):
   e=Engine(schema.validate({}),Store(':memory:'));c=e.store.new_chat('u');e.cfg['prompt']['answer_note']='This app is not an emergency warning service.';e.cfg['provider']['type']='openai'
   ev=[{'n':1,'title':'Trial','year':'2026','text':'Corrected supported finding has enough words.'}]
   class P:
    def complete(self,m):return 'Original draft claim has enough words. [1]'
    def stream(self,m):yield self.complete(m)
   e.provider=P();seen=[]
   def support(answer,evidence):seen.append(answer);return 'Note: the support check could not be completed; support was not verified.'
   fixed='Corrected supported finding has enough words. [1]'
   with patch.object(e,'retrieve',return_value=(ev,{})),patch.object(e,'filter_relevant',side_effect=lambda q,x:x),patch.object(e,'revise',side_effect=lambda a,x,*rest:a),patch.object(e,'_fix',return_value=(fixed,ev,e.ledger(fixed,ev))),patch.object(e,'check_support',side_effect=support),patch.object(e,'followups',return_value=[]):
    r=next(d for k,d in e.ask_stream('u',c,'Question') if k=='done') if stream else e.ask('u',c,'Question')
   self.assertEqual(seen,[fixed]);self.assertIn('not an emergency warning service',r['answer']);self.assertIn('support was not verified',r['answer']);self.assertFalse(any('Note:' in l['claim'] for l in r['ledger']));self.assertIn('support was not verified',e.store.turns('u',c)[-1]['answer'])

 def test_final_ledger_flags_trigger_bounded_repair_even_if_semantic_check_passes(self):
  for stream in (False,True):
   e=Engine(schema.validate({}),Store(':memory:'));c=e.store.new_chat('u');e.cfg['provider']['type']='openai'
   ev=[{'n':1,'title':'Trial','year':'2026','text':'Men and women at high cardiovascular risk were included.'}]
   bad='Adults at high cardiovascular risk were included. [1]';fixed='Men and women at high cardiovascular risk were included. [1]'
   class P:
    def complete(self,m):return bad
    def stream(self,m):yield bad
   e.provider=P()
   with patch.object(e,'retrieve',return_value=(ev,{})),patch.object(e,'filter_relevant',side_effect=lambda q,x:x),patch.object(e,'revise',side_effect=lambda a,x,*rest:a),patch.object(e,'_fix',return_value=(bad,ev,e.ledger(bad,ev))),patch.object(e,'check_support',return_value=''),patch.object(e,'repair_support',return_value=(fixed,ev,e.ledger(fixed,ev),'')) as repair,patch.object(e,'followups',return_value=[]):
    r=next(d for k,d in e.ask_stream('u',c,'Question') if k=='done') if stream else e.ask('u',c,'Question')
   self.assertEqual(r['answer'],fixed);repair.assert_called_once();self.assertIn('unsupported precision',repair.call_args.args[-1])

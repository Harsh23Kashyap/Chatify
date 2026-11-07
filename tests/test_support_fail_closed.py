"""Offline boundary tests. Mocked transport is not semantic model acceptance."""
import unittest
from unittest.mock import Mock, patch
from chatify import schema, providers
from chatify.pipeline import Engine
from chatify.store import Store

BAD='For your farm, apply the F2 recommended NPK dose. [1]'
FIX='Fruit yield increased with fertilization at F2 and F3 doses. [1]'
EV=[{'n':1,'title':'Tomato trial','year':'2026','text':'Fruit yield increased with fertilization at F2 and F3 doses.'}]
WITHHELD='Note: an unsupported answer was withheld because its repair could not be verified against the sources.'
NOTE='Note: the sources may not fully support this: farm recommendation not established'
class FailClosed(unittest.TestCase):
 def engine(self):
  e=Engine(schema.validate({}),Store(':memory:'));e.cfg['provider']['type']='openai';e.cfg['memory']['enabled']=False;e.provider=Mock();return e
 def test_repair_failures_never_return_known_unsupported_original(self):
  for result in ('{"replacements":{}}','short','No citation but a long enough response asking for crop location soil test and growth stage.', 'Apply 950 kg of nitrogen per hectare to your farm immediately. [1]'):
   with self.subTest(result=result):
    e=self.engine();e.provider.complete.return_value=result;e.check_support=Mock()
    a,ev,led,n=e.repair_support(BAD,EV,'Farm dosage?',NOTE)
    self.assertNotIn('apply the F2',a);self.assertIn('No recommendation is provided',a);self.assertEqual(ev,EV);self.assertEqual(led,[]);self.assertEqual(n,WITHHELD);e.check_support.assert_not_called();self.assertEqual(e.provider.complete.call_count,1)
 def test_transport_failure_withholds(self):
  e=self.engine();e.provider.complete.side_effect=providers.ProviderError('unavailable')
  a,ev,led,n=e.repair_support(BAD,EV,'Farm dosage?',NOTE);self.assertNotIn(BAD,a);self.assertEqual(led,[]);self.assertEqual(n,WITHHELD)
 def test_recheck_failure_withholds_repaired_candidate(self):
  for verdict in (NOTE,'Note: the support check returned an invalid result; support was not verified.','Note: the support check could not be completed; support was not verified.'):
   e=self.engine();e.provider.complete.return_value=FIX;e.check_support=Mock(return_value=verdict)
   a,ev,led,n=e.repair_support(BAD,EV,'Study finding?',NOTE);self.assertNotIn(FIX,a);self.assertEqual(led,[]);self.assertEqual(n,WITHHELD);e.check_support.assert_called_once_with(FIX,EV)
 def test_supported_repair_rechecked_once_and_kept(self):
  e=self.engine();e.provider.complete.return_value=FIX;e.check_support=Mock(return_value='')
  a,ev,led,n=e.repair_support(BAD,EV,'Study finding?',NOTE);self.assertEqual(a,FIX);self.assertFalse(n);self.assertTrue(all(r['supported'] for r in led));e.check_support.assert_called_once_with(FIX,EV)
 def test_sync_stream_and_history_withhold_failed_repair_without_unsafe_tokens(self):
  for streaming in (False,True):
   e=self.engine();chat=e.store.new_chat('u');e.provider.complete.return_value='{"replacements":{}}';e.provider.stream.return_value=iter([BAD[:25],BAD[25:]])
   with patch.object(e,'retrieve',return_value=(EV,{})),patch.object(e,'filter_relevant',side_effect=lambda q,x:x),patch.object(e,'revise',side_effect=lambda a,*args,**kw:a),patch.object(e,'_fix',side_effect=lambda a,v,l,*args,**kw:(a,v,l)),patch.object(e,'check_support',return_value=NOTE),patch.object(e,'followups',return_value=[]):
    if streaming:
     events=list(e.ask_stream('u',chat,'Farm dosage?'));r=next(v for k,v in events if k=='done');tokens=''.join(v for k,v in events if k=='token');self.assertNotIn('apply the F2',tokens);self.assertIn('No recommendation is provided',tokens)
    else:
     # Generation and repair use the same provider method in synchronous mode.
     e.provider.complete.side_effect=[BAD,'{"replacements":{}}'];r=e.ask('u',chat,'Farm dosage?')
   self.assertNotIn('apply the F2',r['answer']);self.assertEqual(r['ledger'],[]);self.assertEqual(r['evidence'],EV);self.assertIn(WITHHELD,r['answer']);self.assertEqual(e.store.turns('u',chat)[-1]['answer'],r['answer'])

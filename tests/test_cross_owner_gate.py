"""Synthetic cross-owner storage/export checks, no external accounts."""
import unittest
from chatify.store import Store
from chatify.actions import Actions
from chatify.schema import validate
class CrossOwnerGate(unittest.TestCase):
 def setUp(self):
  self.s=Store(':memory:');self.chat=self.s.new_chat('a','A private chat');self.topic=self.s.new_topic('a','A private topic');self.turn=self.s.add_turn(self.chat,self.topic,'A question','A question','A answer',[],[],'standard')
 def test_topic_list_and_turns_owner_gate(self):
  self.assertEqual(self.s.topics('b'),[])
  with self.assertRaises(PermissionError):self.s.topic_turns('b',self.topic)
 def test_import_export_stay_under_importing_owner(self):
  data=self.s.export_all('a');self.s.import_chats('b',data)
  self.assertEqual(len(self.s.export_all('a')),1);self.assertEqual(len(self.s.export_all('b')),1)
  self.assertNotEqual(self.s.export_all('b')[0]['id'],self.chat)
  with self.assertRaises(PermissionError):self.s.turn('b',self.turn)
 def test_foreign_chat_row_in_owned_topic_is_filtered(self):
  # Simulate inconsistent legacy state. A topic grant never grants another chat.
  c=self.s.new_chat('b','B private chat');self.s.add_turn(c,self.topic,'B question','B question','B answer',[],[],'standard')
  self.assertEqual([x['answer'] for x in self.s.topic_turns('a',self.topic)],['A answer']);self.assertEqual(self.s.topics('a')[0]['turns'],1)
 def test_note_list_excludes_other_owner_and_failed_ticket_not_consumed(self):
  a=Actions(validate({}),self.s);p=a.prepare('a','save_note',{'title':'A note','text':'A text'})
  with self.assertRaises(ValueError):a.execute('b',p['ticket'])
  self.assertTrue(a.execute('a',p['ticket'])['saved'])
  b=a.prepare('b','list_notes',{});self.assertEqual(a.execute('b',b['ticket'])['notes'],[])
 def test_foreign_topic_rename_no_effect(self):
  with self.assertRaises(PermissionError):self.s.rename_topic('b',self.topic,'wrong')
  self.assertEqual(self.s.topic('a',self.topic)['title'],'A private topic')

import copy,json,unittest
from chatify.pipeline import Engine
from chatify.store import Store
from chatify import schema
from chatify.prompts import PromptStore
class DomainCheck(unittest.TestCase):
 def test_recent_question_is_data(self):
  class P:
   def complete(self,m):self.messages=m;return 'VALID'
  cfg=copy.deepcopy(schema.DEFAULTS);cfg['provider']['type']='openai';p=P();e=Engine(cfg,Store(':memory:'),provider=p,connectors={});e.prompts=PromptStore('',{'on':{'question_check':True}})
  self.assertEqual(e.check_question('Explain that simply',[{'question':'What is compost?','answer':'private answer'}]),'')
  data=json.loads(p.messages[-1]['content']);self.assertEqual(data['recent_questions'],['What is compost?']);self.assertNotIn('private answer',p.messages[-1]['content'])
  self.assertIn('Requests to explain or simplify domain information are valid',p.messages[0]['content'])
 def test_invalid_question_still_blocked(self):
  class P:
   def complete(self,m):return 'INVALID: outside the app domain'
  cfg=copy.deepcopy(schema.DEFAULTS);cfg['provider']['type']='openai';e=Engine(cfg,Store(':memory:'),provider=P(),connectors={});e.prompts=PromptStore('',{'on':{'question_check':True}})
  self.assertEqual(e.check_question('outside question',[{'question':'valid earlier topic'}]),'outside the app domain')

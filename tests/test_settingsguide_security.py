import unittest,json
from customchat import settingsguide as g
from customchat import providers,budget
class Model:
 def __init__(self):self.calls=0
 def complete(self,m):self.calls+=1;return '{"answer":"No changes","sections":["sec-model"]}'
class Security(unittest.TestCase):
 def test_budget_preserved(self):
  b=budget.Budget({'budget':{}},None);b.value['spend_cap_usd']=1;p=Model()
  with self.assertRaises(budget.BudgetError):g.guide(b.wrap(p),{'provider':{'type':'openai'}},'font',True)
  self.assertEqual(p.calls,0)
 def test_schema_is_names_not_values(self):
  data=json.dumps(g.PUBLIC_FIELDS);self.assertIn('memory.context_chars',data);self.assertNotIn('127.0.0.1',data);self.assertNotIn('You answer only',data)

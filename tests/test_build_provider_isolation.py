"""Source API selection must never silently replace the user's model connection.
Regression contract recovered from original Signal Desk review, not generated output.
"""
import copy,json,unittest
from chatify import buildjobs,schema
class Isolation(unittest.TestCase):
 def run_part(self,provider,answer):
  class Model:
   def __init__(self):self.instruction=''
   def complete(self,messages):self.instruction=messages[0]['content'];return json.dumps(answer)
  model=Model();cfg=copy.deepcopy(schema.DEFAULTS);cfg['provider']=copy.deepcopy(provider)
  jobs=buildjobs.BuildJobs();job={'provider':model,'cfg':cfg,'brief':'NewsAPI source uses NEWSAPI_KEY at https://newsapi.org/v2/everything. Keep current language model.','parts':{},'cancel':False,'calls':0,'owner':'test','errors':{}}
  jobs._draft_part(job,'config:provider',copy.deepcopy(dict(buildjobs.PARTS)['config:provider']))
  return job,model
 def base(self):
  p=copy.deepcopy(schema.DEFAULTS['provider']);p.update(type='openai',model='gpt-4o-mini',base_url='https://api.openai.com/v1',api_key_env='OPENAI_API_KEY');return p
 def test_current_model_preserved(self):
  p=self.base();j,m=self.run_part(p,p);self.assertEqual(j['parts']['config:provider'],p);self.assertIn('not a source API',m.instruction)
 def test_source_address_cannot_replace_model(self):
  p=self.base();wrong=copy.deepcopy(p);wrong['base_url']='https://newsapi.org/v2'
  with self.assertRaisesRegex(ValueError,'Model connection changed unexpectedly'):self.run_part(p,wrong)
 def test_source_key_cannot_replace_model_key(self):
  p=self.base();wrong=copy.deepcopy(p);wrong['api_key_env']='NEWSAPI_KEY'
  with self.assertRaisesRegex(ValueError,'Model connection changed unexpectedly'):self.run_part(p,wrong)
 def test_another_model_cannot_silently_replace_current(self):
  p=self.base();wrong=copy.deepcopy(p);wrong['model']='different-model'
  with self.assertRaisesRegex(ValueError,'Model connection changed unexpectedly'):self.run_part(p,wrong)
 def test_provider_fields_not_silently_dropped(self):
  p=self.base();wrong=copy.deepcopy(p);del wrong['api_key_env']
  with self.assertRaisesRegex(ValueError,'Model connection changed unexpectedly'):self.run_part(p,wrong)
if __name__=='__main__':unittest.main()

class HelperContracts(unittest.TestCase):
 def test_clean_query_instruction_is_local_not_search(self):
  class Model:
   def __init__(self):self.system=''
   def complete(self,messages):
    self.system=messages[0]['content'];return json.dumps({'brief':'Local cleanup only','code':'def clean_query(query):\n    return query.strip() or query\n'})
  m=Model();j={'provider':m,'cfg':copy.deepcopy(schema.DEFAULTS),'brief':'NewsAPI news app','parts':{},'cancel':False,'calls':0,'owner':'test','errors':{}}
  b=buildjobs.BuildJobs();b._draft_part(j,'helper:clean_query',copy.deepcopy(dict(buildjobs.PARTS)['helper:clean_query']))
  self.assertIn('No network, API request',m.system);self.assertNotIn('All search helpers need',m.system)
 def test_http_source_example_keeps_key_name_in_header_mapping(self):
  class Model:
   def __init__(self):self.system=''
   def complete(self,messages):self.system=messages[0]['content'];return '[]'
  m=Model();j={'provider':m,'cfg':copy.deepcopy(schema.DEFAULTS),'brief':'No supplied source','parts':{},'cancel':False,'calls':0,'owner':'test','errors':{}}
  buildjobs.BuildJobs()._draft_part(j,'config:sources',copy.deepcopy(dict(buildjobs.PARTS)['config:sources']))
  self.assertIn('header_env',m.system);self.assertIn('results_path',m.system)

class ActionsContract(unittest.TestCase):
 def run_actions(self,answer):
  class Model:
   def complete(self,messages):self.instruction=messages[0]['content'];return json.dumps(answer)
  m=Model();j={'provider':m,'cfg':copy.deepcopy(schema.DEFAULTS),'brief':'Garden research assistant. Keep writes disabled.','parts':{},'cancel':False,'calls':0,'owner':'test','errors':{}}
  buildjobs.BuildJobs()._draft_part(j,'config:actions',copy.deepcopy(dict(buildjobs.PARTS)['config:actions']))
  return j,m
 def test_instruction_supplies_real_tool_ids_and_safe_empty_policy(self):
  from chatify.actions import REGISTRY
  j,m=self.run_actions({'allow':[],'writes':False})
  self.assertIn('registered_action_ids',m.instruction)
  for tool in REGISTRY:self.assertIn(tool,m.instruction)
  self.assertIn('This does not disable answer generation',m.instruction)
  self.assertEqual(j['parts']['config:actions'],{'allow':[],'writes':False})
 def test_unknown_tool_still_rejected(self):
  with self.assertRaisesRegex(ValueError,'registered tool IDs'):self.run_actions({'allow':['search_web'],'writes':False})

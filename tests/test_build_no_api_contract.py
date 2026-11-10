"""Explicit API opt-out is distinct from no selected active connectors."""
import copy,json,unittest
from chatify import buildjobs,schema
class Capture:
 def __init__(self,value):self.value=value
 def complete(self,messages):self.messages=messages;return json.dumps(self.value)
class NoAPIContract(unittest.TestCase):
 def job(self,brief,value):return {'brief':brief,'provider':Capture(value),'cfg':copy.deepcopy(schema.DEFAULTS),'cancel':False,'calls':0,'parts':{},'errors':{},'confirmed_sources':[]}
 def test_empty_recommendations_accepted_only_for_explicit_prohibition(self):
  b='Create a fictional library handbook assistant. Never retrieve external sources. Keep all optional APIs disabled.'
  j=self.job(b,[]);buildjobs.BuildJobs()._draft_part(j,'api',dict(buildjobs.PARTS)['api'])
  self.assertEqual(j['parts']['api'],[]);self.assertIn('Return exactly []',j['provider'].messages[0]['content'])
  self.assertFalse(j.get('defaulted'))
 def test_empty_checkboxes_do_not_mean_no_suggestions(self):
  for b in ['Create a library assistant. Recommend optional free sources only for later consideration; leave them inactive.','Create a library assistant','No paid logo. Use uploaded documents.']:
   with self.subTest(brief=b):
    self.assertFalse(buildjobs.no_external_api_recommendations(b));j=self.job(b,[])
    with self.assertRaisesRegex(ValueError,'three to five'):buildjobs.BuildJobs()._draft_part(j,'api',dict(buildjobs.PARTS)['api'])
 def test_prohibition_never_accepts_unrequested_service(self):
  j=self.job('Do not recommend any APIs',[{'service':'Wikipedia'}])
  with self.assertRaisesRegex(ValueError,'prohibited'):buildjobs.BuildJobs()._draft_part(j,'api',dict(buildjobs.PARTS)['api'])
 def test_prompt_validator_still_rejects_fixed_output(self):
  from chatify import generator_design
  for stage in ['standalone','summary']:
   self.assertTrue(generator_design.validate_draft(stage,{'prompt':'The Cedar library allows three books. '*15}))
 def test_full_explicit_optout_build_merge_no_defaulted_areas(self):
  import time
  from unittest.mock import patch
  from test_buildjobs import Fixture
  class OptOut(Fixture):
   def complete(self,messages):
    if 'Return exactly an empty JSON list []' in messages[0]['content']:return '[]'
    return super().complete(messages)
  f=OptOut();jobs=buildjobs.BuildJobs()
  with patch('chatify.buildimages.capability',return_value={'available':False,'note':'test only'}):
   r=jobs.start('owner',f,schema.DEFAULTS,{'brief':'Create a library handbook app. Keep all optional APIs disabled. Never retrieve external sources.'})
   for _ in range(600):
    r=jobs.view('owner',r['id'])
    if r['state']!='running':break
    time.sleep(.01)
  self.assertEqual(r['state'],'done',r);self.assertEqual(r['defaulted'],[])
  self.assertEqual(r['completed'],len(buildjobs.PARTS))
  import yaml
  raw=yaml.safe_load(r['yaml']);self.assertEqual(raw['api_suggestions'],[]);self.assertEqual(raw['sources'],[])
 def test_conflicting_selected_sources_rejected_before_calls(self):
  j=self.job('Do not recommend any APIs',[]);f=j['provider']
  with self.assertRaisesRegex(ValueError,'checkboxes'):buildjobs.BuildJobs().start('owner',f,schema.DEFAULTS,{'brief':j['brief'],'confirmed_sources':['arxiv']})
  self.assertFalse(hasattr(f,'messages'))
 def test_model_recommendations_remain_unselected_without_owner_connector_choice(self):
  from test_buildjobs import Fixture
  j=self.job('Recommend optional free sources only for later consideration; leave them inactive.',None);j['provider']=Fixture()
  buildjobs.BuildJobs()._draft_part(j,'api',dict(buildjobs.PARTS)['api'])
  self.assertEqual(len(j['parts']['api']),3)
  self.assertTrue(all(p['selected'] is False for p in j['parts']['api']))

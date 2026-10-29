import unittest,json,copy
from chatify import buildjobs,schema,generators
class ConfirmedSources(unittest.TestCase):
 def run_part(self,selected,connectors):
  rows=[{'name':c,'service':c,'what':'This service provides searchable published information for research questions.','reason':'This service helps answer the specific research questions in this application.','connector':c,'setup':'Review documentation','caveat':'External details unverified','helper':{'brief':'Inert helper','code':generators.code_template('search','')}} for c in connectors]
  class Provider:
   def complete(self,messages):self.message=messages[0]['content'];return json.dumps(rows)
  pv=Provider();job={'cancel':False,'calls':0,'provider':pv,'cfg':copy.deepcopy(schema.DEFAULTS),'parts':{},'errors':{},'active':set(),'brief':'Research','confirmed_sources':selected}
  buildjobs.BuildJobs()._draft_part(job,'api',dict(buildjobs.PARTS)['api']);return job,pv
 def test_one_confirmed_source(self):
  j,p=self.run_part(['pubmed'],['pubmed']);self.assertEqual(len(j['parts']['api']),1);self.assertIn('overrides the open-ended',p.message)
 def test_multiple_confirmed_preserved(self):
  j,p=self.run_part(['pubmed','crossref'],['crossref','pubmed']);self.assertEqual({r['connector'] for r in j['parts']['api']},{'pubmed','crossref'})
 def test_zero_selected_keeps_default(self):
  with self.assertRaisesRegex(ValueError,'three to five'):self.run_part([],['pubmed'])
  self.run_part([],['pubmed','crossref','arxiv'])
 def test_unrelated_replacement_rejected(self):
  with self.assertRaisesRegex(ValueError,'confirmed sources'):self.run_part(['pubmed'],['wikipedia'])
 def test_missing_selected_rejected(self):
  with self.assertRaisesRegex(ValueError,'confirmed sources'):self.run_part(['pubmed','crossref'],['pubmed'])
 def test_duplicate_selected_output_rejected(self):
  with self.assertRaisesRegex(ValueError,'confirmed sources'):self.run_part(['pubmed','crossref'],['pubmed','pubmed'])
 def test_changed_selection_does_not_resume_old_checkpoint(self):
  import tempfile
  with tempfile.TemporaryDirectory() as tmp:
   jobs=buildjobs.BuildJobs(spend_dir=tmp)
   old={'owner':'test','id':'old','cancel':False,'brief':'Research','fingerprint':'same','confirmed_sources':['pubmed'],'parts':{'api':[]},'errors':{},'calls':1}
   jobs._checkpoint(old)
   new=dict(old,id='new',confirmed_sources=['crossref'],parts={},calls=0)
   jobs._checkpoint_resume(new)
   self.assertEqual(new['parts'],{})
 def test_same_selection_resumes_checkpoint(self):
  import tempfile
  with tempfile.TemporaryDirectory() as tmp:
   jobs=buildjobs.BuildJobs(spend_dir=tmp)
   old={'owner':'test','id':'old','cancel':False,'brief':'Research','fingerprint':'same','confirmed_sources':['pubmed'],'parts':{'api':[]},'errors':{},'calls':1}
   jobs._checkpoint(old)
   new=dict(old,id='new',parts={},calls=0)
   jobs._checkpoint_resume(new)
   self.assertIn('api',new['parts'])

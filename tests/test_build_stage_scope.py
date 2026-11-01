"""Recovered stage metadata controls, not model behavior proof."""
import copy,json,unittest
from chatify import buildjobs,generator_design,schema
class Capture:
 def complete(self,messages):
  self.system=messages[0]['content'];spec=json.JSONDecoder().raw_decode(self.system[self.system.index('{',self.system.index('This is one isolated')):])[0]
  return json.dumps({'text':generator_design.template(spec['stage'],'Peacebuilding news and conflict resolution'),'on':True})
class BuildStageScope(unittest.TestCase):
 def instruction(self,stage):
  p=Capture();j={'id':'scope','owner':'owner','brief':'Peacebuilding news and conflict resolution','provider':p,'cfg':copy.deepcopy(schema.DEFAULTS),'cancel':False,'calls':0,'parts':{},'errors':{}}
  buildjobs.BuildJobs()._draft_part(j,'prompt:'+stage,dict(buildjobs.PARTS)['prompt:'+stage]);return p.system
 def test_answer_not_given_classifier_or_rewrite_duties(self):
  s=self.instruction('answer');self.assertNotIn('For question_check classify',s);self.assertNotIn('For standalone explicitly',s);self.assertIn('each factual sentence',s)
 def test_classifier_subject_scope(self):self.assertIn('not the act of creating a website',self.instruction('question_check'))
 def test_standalone_rewrite_contract(self):self.assertIn('rewrite or rephrase the latest runtime question',self.instruction('standalone'))

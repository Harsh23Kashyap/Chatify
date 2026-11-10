import json,unittest,copy
from chatify import buildjobs,schema
class Capture:
 def complete(self,messages):self.messages=messages;return '{}'
class DocumentScope(unittest.TestCase):
 def test_classifier_contract_preserves_document_only_scope_without_evidence_gate(self):
  f=Capture();j={'brief':'Answer only questions about documents the owner uploads. Never invent library policy.','provider':f,'cfg':copy.deepcopy(schema.DEFAULTS),'cancel':False,'calls':0,'parts':{},'errors':{},'confirmed_sources':[]}
  with self.assertRaises(ValueError):buildjobs.BuildJobs()._draft_part(j,'prompt:question_check',dict(buildjobs.PARTS)['prompt:question_check'])
  text=f.messages[0]['content'];offset=text.index('{',text.index('This is one isolated'));spec=json.JSONDecoder().raw_decode(text[offset:])[0]
  rules=spec['stage_rules'];self.assertIn('do not expand scope to general domain education',rules);self.assertIn('without requiring their contents',rules);self.assertIn('Missing evidence is never a reason to reject',rules)
  self.assertNotIn('Accept ordinary educational questions and domain-related safety questions.',rules)
  self.assertIn('never broaden an uploaded-documents-only app',text)

import copy,json,time,unittest
from chatify import buildjobs,schema,appbuilder
from test_buildjobs import Fixture,Jobs
class ValidationDetails(Jobs):
 def test_exact_prompt_and_helper_failures_retry_preserves_parts(self):
  class Bad(Fixture):
   def __init__(self):super().__init__();self.bad=True
   def complete(self,messages):
    system=messages[0]['content']
    if self.bad and '"stage": "faithfulness"' in system:return json.dumps({'text':'x'*6001,'on':True})
    if self.bad and '"kind": "search"' in system:return json.dumps({'brief':'fixture','code':None})
    return super().complete(messages)
  f=Bad();jobs=buildjobs.BuildJobs();d=self.wait(jobs,jobs.start('owner',f,schema.DEFAULTS,{'brief':'Garden advice'})['id']);self.assertEqual(d['state'],'partial');self.assertIn('6001',d['errors']['prompt:faithfulness']);self.assertIn('code field',d['errors']['helper:search']);parts=d['completed'];calls=d['calls'];f.bad=False;jobs.retry('owner',d['id']);d=self.wait(jobs,d['id']);self.assertEqual(d['state'],'done',d);self.assertEqual(d['calls'],calls);self.assertEqual(d['retry_calls'],3);self.assertEqual(d['completed'],parts+2)
 def test_helper_missing_brief_and_length_reasons(self):
  for value,reason in [({'code':'pass'},'brief field'),({'brief':'x','code':'x'*12001},'12001')]:
   with self.assertRaisesRegex(ValueError,reason):appbuilder.validate_extras({'helper_drafts':{'search':value}})

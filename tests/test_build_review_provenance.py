"""Historical review concerns survive completed-job retention, updates and restart."""
import tempfile,time,unittest
from unittest.mock import patch
from chatify import buildjobs,builddrafts,schema
from test_buildjobs import Fixture
class ReviewProvenance(unittest.TestCase):
 def test_full_note_retained_with_owner_isolation_and_edits(self):
  review={'review_status':'concerns','ready':False,'issues':['unresolved '+('x'*900)],'setup_notes':['Verify source access.','Do not deploy yet.']}
  note=builddrafts.review_note(review,['Literal destination unverified.'])
  with tempfile.TemporaryDirectory() as folder:
   store=builddrafts.BuildDrafts(folder);d=store.put('alice','app: {title: Draft}',review_note=note)
   self.assertEqual(store.get('alice',d['id'])['review_note'],note)
   store.put('alice','app: {title: Edited}',ident=d['id'])
   self.assertEqual(builddrafts.BuildDrafts(folder).get('alice',d['id'])['review_note'],note)
   self.assertIn('not cleared by editing, validation or saving',note)
   self.assertRaises(ValueError,store.get,'bob',d['id'])
 @patch('chatify.buildimages.capability',return_value={'available':False,'note':'Fixture: no image calls'})
 def test_done_worker_persists_review_findings_not_only_not_run(self,cap):
  class Model(Fixture):
   def complete(self,messages):
    if 'Review this complete merged draft' in messages[0]['content']:
     return '{"issues":["Fixture faithfulness lacks question context."],"setup_notes":["Verify source access."],"ready":false}'
    return super().complete(messages)
  with tempfile.TemporaryDirectory() as folder:
   store=builddrafts.BuildDrafts(folder);jobs=buildjobs.BuildJobs(drafts=store)
   ident=jobs.start('owner',Model(),schema.DEFAULTS,{'brief':'Garden fixture'})['id']
   for _ in range(1000):
    d=jobs.view('owner',ident)
    if d['state']!='running' and store.list('owner'):break
    time.sleep(.01)
   self.assertEqual(d['state'],'done',d['errors'])
   note=builddrafts.BuildDrafts(folder).get('owner',ident)['review_note']
   self.assertIn('concerns',note);self.assertIn('Fixture faithfulness lacks question context.',note);self.assertIn('Verify source access.',note)

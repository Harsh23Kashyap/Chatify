"""Real HTTP owner session and BuildJobs state; worker deliberately held, no model calls."""
import threading,urllib.error
from types import SimpleNamespace
from unittest.mock import patch
import test_workspace_api
from chatify import buildjobs

class ActiveRecoveryHTTP(test_workspace_api.WorkspaceAPITests):
 def setUp(self):
  self.release_worker=threading.Event();self.worker_entered=threading.Event();self.jobs=None
  original=buildjobs.BuildJobs.__init__
  def initialize(instance,*args,**kwargs):
   original(instance,*args,**kwargs);self.jobs=instance
  def held_worker(instance,job,parts):
   self.worker_entered.set();self.release_worker.wait(10)
   with instance.lock:job['state']='cancelled'
  self.patches=[patch.object(buildjobs.BuildJobs,'__init__',initialize),patch.object(buildjobs.BuildJobs,'_run',held_worker)]
  for p in self.patches:p.start()
  try:super().setUp()
  except Exception:
   for p in reversed(self.patches):p.stop()
   raise
 def tearDown(self):
  self.release_worker.set()
  try:super().tearDown()
  finally:
   for p in reversed(self.patches):p.stop()
 def test_real_active_snapshot_reconnect_and_duplicate_guard(self):
  body={'brief':'Reload recovery fixture','consent':True,'explicit_selection':True,'selection':{'provider':'openai','model':'fixture'}}
  self.assertEqual(self.call(self.clients[0],'/api/settings/build/active')['mine'],[])
  with patch('chatify.providers.make',return_value=SimpleNamespace()),patch('chatify.providers._post') as transport:
   started=self.call(self.clients[0],'/api/settings/build/start',body)
   self.assertTrue(self.worker_entered.wait(2))
   # A new HTTP read has no browser-held job ID; discover the live owner job.
   snapshot=self.call(self.clients[0],'/api/settings/build/active')
   self.assertEqual([j['id'] for j in snapshot['mine']],[started['id']])
   recovered=self.call(self.clients[0],'/api/settings/build/job?id='+snapshot['mine'][0]['id'])
   self.assertEqual(recovered['state'],'running');self.assertEqual(recovered['calls'],0)
   with self.assertRaises(urllib.error.HTTPError) as duplicate:self.call(self.clients[0],'/api/settings/build/start',body)
   self.assertIn('already running',duplicate.exception.read().decode())
   self.assertEqual(len(self.jobs.jobs),1);transport.assert_not_called()
  for path in ('/api/settings/build/active','/api/settings/build/job?id='+started['id']):
   with self.assertRaises(urllib.error.HTTPError) as denied:self.call(self.clients[1],path)
   self.assertIn(denied.exception.code,(403,404))
  self.assertEqual(self.jobs.active('another-owner')['mine'],[])

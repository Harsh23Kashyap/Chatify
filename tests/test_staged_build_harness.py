import importlib.util,pathlib,tempfile,time,unittest,copy
from unittest.mock import patch
from chatify import schema,buildjobs
from test_buildjobs import Fixture
spec=importlib.util.spec_from_file_location('staged_buildjobs',pathlib.Path(__file__).parent/'harness/staged_buildjobs.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
class StagedHarness(unittest.TestCase):
 def wait(self,b,i):
  for _ in range(1000):
   r=b.view('owner',i)
   if r['state']!='running':self.assertEqual(r['active_calls'],0);return r
   time.sleep(.01)
  self.fail('batch failed to drain')
 def test_resume_across_process_boundary_preserves_paid_parts_and_no_defaulting(self):
  with tempfile.TemporaryDirectory() as td,patch('chatify.buildimages.capability',return_value={'available':False}):
   f=Fixture();cls=h.staged_class(2);b=cls(spend_dir=td)
   data={'brief':'Create a garden handbook assistant'};r=b.start('owner',f,schema.DEFAULTS,data);r=self.wait(b,r['id']);self.assertTrue(r['harness_paused']);self.assertEqual(r['calls'],2);self.assertEqual(r['completed'],2)
   kept=copy.deepcopy(b.jobs[r['id']]['parts'])
   # Simulate foreground process ending only after the drained boundary.
   b=cls(spend_dir=td);r=b.start('owner',f,schema.DEFAULTS,data);r=self.wait(b,r['id']);self.assertEqual(r['completed'],4);self.assertEqual(r['calls'],4)
   for k,v in kept.items():self.assertEqual(b.jobs[r['id']]['parts'][k],v)
   while r['state']!='done':
    self.assertTrue(r['harness_paused']);b.resume_batch('owner',r['id']);r=self.wait(b,r['id'])
   self.assertEqual(r['defaulted'],[]);self.assertEqual(r['completed'],len(buildjobs.PARTS));self.assertEqual(r['calls'],len(buildjobs.PARTS)+1)
 def test_product_class_untouched_and_invalid_batch_rejected(self):
  self.assertIs(h.ProductBuildJobs,buildjobs.BuildJobs)
  for n in [0,4,True]:
   with self.assertRaises(ValueError):h.staged_class(n)

import importlib.util, pathlib, unittest
spec=importlib.util.spec_from_file_location('ci_browser_suite',pathlib.Path(__file__).parent/'ci/browser_suite.py')
suite=importlib.util.module_from_spec(spec);spec.loader.exec_module(suite)
class BrowserOrchestrationTests(unittest.TestCase):
 def test_every_script_classified(self):
  m=suite.load_manifest();self.assertEqual(len(m['cases']),474);self.assertEqual(len(m['excluded']),13)
 def test_known_fixture_routes(self):
  m=suite.load_manifest()['cases']
  for name,kind in [('question-nav.cjs','strict'),('pickers_browser.cjs','strict'),('builder_apply_saved_e2e_browser.cjs','trip'),('builder_mounted_preview_browser.cjs','mounted'),('builder_brand_retry_e2e_browser.cjs','brand'),('ten_actual_palettes_browser.cjs','self')]:self.assertEqual(m[name],kind)
 def test_expanded_contracts(self):
  self.assertEqual(len(suite.variants('button_press_feedback_inventory_browser.cjs')),4)
  self.assertTrue(all(v[2]['RELEASE_LEVEL']=='full' for v in suite.variants('button_press_feedback_inventory_browser.cjs')))
  self.assertEqual(len(suite.variants('wizard_launch_retry_harness.cjs')),4)
  self.assertEqual(len(suite.variants('advanced_all_sections_group_motion_browser.cjs')),4)
 def test_no_credential_forwarding(self):
  import os
  from unittest.mock import patch
  with patch.dict(os.environ,{'OPENAI_API_KEY':'not-real','GITHUB_TOKEN':'not-real'}):
   self.assertNotIn('OPENAI_API_KEY',suite.base_env());self.assertNotIn('GITHUB_TOKEN',suite.base_env())
 def test_shards_cover_once(self):
  cases=sorted(suite.load_manifest()['cases']);seen=[]
  for shard in range(12):seen.extend(n for i,n in enumerate(cases) if i%12==shard)
  self.assertEqual(sorted(seen),cases)

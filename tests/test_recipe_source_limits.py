import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('recipe_sources_limits',Path(__file__).resolve().parents[1]/'apps/recipechat/recipe_sources.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
class RecipeSourceLimits(unittest.TestCase):
 def test_production_does_not_use_development_key_silently(self):
  for env in ({},{'THEMEALDB_API_KEY':'1'}):
   with patch.dict(os.environ,env,clear=True),patch.object(a,'_get',side_effect=AssertionError('network')):
    with self.assertRaisesRegex(ValueError,'production access'):a.mealdb('pizza')
 def test_explicit_educational_mode(self):
  urls=[]
  with patch.dict(os.environ,{'CHATIFY_MEALDB_EDUCATIONAL_DEMO':'1'},clear=True),patch.object(a,'_get',side_effect=lambda u:urls.append(u) or {'meals':[]}):self.assertEqual(a.mealdb('pizza'),[])
  self.assertTrue(all('/v1/1/' in u for u in urls))
 def test_own_production_key_route(self):
  urls=[]
  with patch.dict(os.environ,{'THEMEALDB_API_KEY':'synthetic_test_key'},clear=True),patch.object(a,'_get',side_effect=lambda u:urls.append(u) or {'meals':[]}):a.mealdb('pizza')
  self.assertTrue(all('/v1/synthetic_test_key/' in u for u in urls))
 def test_off_cache_and_request_spacing(self):
  a._OFF_CACHE.clear();a._OFF_LAST=99
  with patch.object(a.time,'monotonic',return_value=100),patch.object(a.time,'sleep') as sleep,patch.object(a,'_get',return_value={'products':[]}) as get:
   self.assertEqual(a.offfoods('cheddar'),[]);self.assertEqual(a.offfoods('cheddar'),[])
   self.assertEqual(get.call_count,1);self.assertAlmostEqual(sleep.call_args.args[0],5.1)
if __name__=='__main__':unittest.main()

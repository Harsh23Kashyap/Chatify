"""No-network regression: safe source errors and reviewed source-only checks."""
import sys,pathlib,unittest,urllib.error,json
from unittest.mock import patch,Mock
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'apps/weatherchat'))
import weather_sources as w
from chatify import schema
from chatify.pipeline import Engine
from chatify.store import Store
from chatify.management import Management
class Tests(unittest.TestCase):
 def engine(self):
  cfg=schema.load(str(ROOT/'apps/weatherchat/app.yaml'));cfg['retrieval'].update(query_rewrite=False,query_expansion=False);cfg['provider']['type']='mock';return Engine(cfg,Store(':memory:'))
 def test_errors_expose_only_fixed_stage_category_and_http_status(self):
  errors=[(urllib.error.HTTPError('https://secret.invalid/?key=PRIVATE',403,'PRIVATE',{},None),'http:403'),(urllib.error.URLError('PRIVATEhttps://secret.invalid'), 'network')]
  for url,stage in [(w.GEOCODE_URL,'geocoding'),(w.FORECAST_URL,'forecast')]:
   for error,kind in errors:
    with self.subTest(stage=stage,kind=kind),patch('weather_sources.urllib.request.urlopen',side_effect=error):
     with self.assertRaises(w.WeatherSourceError)as ctx:w._get(url,{'private':'PRIVATE'})
     text=str(ctx.exception);self.assertIn('[weather:'+stage+':'+kind+']',text);self.assertNotIn('PRIVATE',text);self.assertNotIn('https:',text);self.assertIsInstance(ctx.exception,ValueError)
 def test_json_failure_has_no_body_or_url(self):
  class Reply:
   def __enter__(self):return self
   def __exit__(self,*a):pass
   def read(self,*a):return b'PRIVATEinvalidJSON'
  with patch('weather_sources.urllib.request.urlopen',return_value=Reply()):
   with self.assertRaises(w.WeatherSourceError)as ctx:w._get(w.FORECAST_URL,{})
   self.assertIn('[weather:forecast:json]',str(ctx.exception));self.assertNotIn('PRIVATE',str(ctx.exception))
 def test_source_error_survives_real_retrieval_without_raw_exception(self):
  e=self.engine()
  with patch('weather_sources.urllib.request.urlopen',side_effect=urllib.error.HTTPError('https://secret.invalid',403,'PRIVATE',{},None)):
   rows,errors=e.retrieve('weather in Bengaluru',['open-meteo-weather'],'owner')
  self.assertEqual(rows,[]);self.assertIn('[weather:geocoding:http:403]',errors['open-meteo-weather']);self.assertNotIn('PRIVATE',str(errors));self.assertNotIn('https:',str(errors))
 def test_preflight_reviews_actual_example_and_zero_model_calls(self):
  e=self.engine();m=Management(e.cfg,e,lambda:{},lambda x:None,e.store.export_all);plan=m.prepare_live('owner',{'model':False,'sources':['open-meteo-weather']});self.assertEqual(plan['model_calls'],0);self.assertEqual(plan['questions'],[e.cfg['app']['examples'][0]])
  spec=m.reviews.take('owner','preflight',plan['ticket'],True);e.retrieve=Mock(return_value=([],{'open-meteo-weather':'Open-Meteo failed [weather:geocoding:http:403] SECREThttps://private.invalid'}));e.provider.complete=Mock(side_effect=AssertionError('No model allowed'));m.jobs['test']={'owner':'owner','state':'running'};m.active=True;m._run('test','owner','preflight',spec,e);e.retrieve.assert_called_once_with(e.cfg['app']['examples'][0],['open-meteo-weather'],'owner');self.assertEqual(e.provider.complete.call_count,0);result=m.jobs['test']['results'][0];self.assertIn('[weather:geocoding:http:403]',result['message']);self.assertNotIn('SECRET',json.dumps(result));self.assertNotIn('https:',json.dumps(result))
 def test_nonweather_preflight_query_unchanged(self):
  e=self.engine();e.cfg['app']['id']='other';m=Management(e.cfg,e,lambda:{},lambda x:None,e.store.export_all);plan=m.prepare_live('owner',{'model':False,'sources':['open-meteo-weather']});self.assertEqual(plan['questions'],['Chatify connection check'])
if __name__=='__main__':unittest.main()

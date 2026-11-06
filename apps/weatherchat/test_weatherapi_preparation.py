"""Offline documented-field tests. No account, network or model acceptance implied."""
import os
import json
import unittest
import urllib.error
from unittest.mock import patch
import weatherapi_sources as w

PAYLOAD = {'location': {'name': 'Bengaluru', 'region': 'Karnataka', 'country': 'India', 'tz_id': 'Asia/Kolkata', 'lat':12.98,'lon':77.58},
 'current': {'last_updated': '2026-11-06 21:30', 'temp_c': 24, 'feelslike_c': 25, 'humidity': 70, 'wind_kph': 5, 'precip_mm': 0.5},
 'forecast': {'forecastday': [{'date': '2026-11-%02d' % d, 'day': {'maxtemp_c': 30, 'mintemp_c': 22, 'daily_chance_of_rain': 0, 'totalprecip_mm': 0, 'maxwind_kph': 10}} for d in range(6, 11)]}}

class Tests(unittest.TestCase):
 def test_bound_to_three_days_and_current_native_fields(self):
  items=w._evidence(PAYLOAD,'Bangalore');self.assertEqual(len(items),1)
  lines=[json.loads(line.split(':',1)[1]) for line in items[0]['text'].splitlines() if line.startswith('WEATHERAPI_FACTS_JSON:')]
  self.assertEqual(len(lines),4);self.assertEqual(lines[0]['meta']['valid'],'2026-11-06T21:30');self.assertFalse(lines[0]['meta']['forecast']);self.assertEqual(lines[1]['meta']['valid'],'2026-11-06');self.assertTrue(lines[1]['meta']['forecast']);self.assertEqual(lines[-1]['meta']['valid'],'2026-11-08')
  self.assertNotIn('precip_mm',[f['field'] for f in lines[0]['fields']]);self.assertNotIn('Open-Meteo',items[0]['text'])
 def test_missing_fields_not_zero(self):
  p={'location':PAYLOAD['location'],'current':{'last_updated':'2026-11-06 21:30','temp_c':None}}
  self.assertEqual(w._evidence(p,'Bengaluru'),[])
 def test_ambiguous_never_fetches_forecast(self):
  matches=[{'name':'Cambridge','lat':52,'lon':0,'country':'UK'},{'name':'Cambridge','lat':42,'lon':-71,'country':'USA'}]
  with patch.object(w,'_request',return_value=matches) as r:
   items=w.weatherapi('Weather in Cambridge');self.assertEqual(r.call_count,1);self.assertTrue(items[0]['id'].startswith('weatherapi-clarify-'))
 def test_source_contract_no_card_free_endpoints_only(self):
  with patch.object(w,'_request',side_effect=[[{'id':123,'name':'Bengaluru','lat':12.97,'lon':77.59}],PAYLOAD]) as r:
   w.weatherapi('weather in Bangalore right now');self.assertEqual(r.call_count,2);self.assertEqual(r.call_args.args,('forecast.json',{'q':'id:123','days':3,'aqi':'no','alerts':'no'}))
 def test_error_never_leaks_key_or_response(self):
  secret='test-only-placeholder-not-a-real-secret'
  with patch.dict(os.environ,WEATHERAPI_API_KEY=secret),patch('urllib.request.urlopen',side_effect=urllib.error.HTTPError('https://test/?key='+secret,429,secret,{},None)) as r:
   with self.assertRaises(w.WeatherSourceError) as c:w._request('forecast.json',{'q':'X','days':3})
   self.assertNotIn(secret,str(c.exception));self.assertIn('http:429',str(c.exception));self.assertEqual(r.call_count,1)
 def test_missing_key_no_network(self):
  with patch.dict(os.environ,{'WEATHERAPI_API_KEY':''}),patch('urllib.request.urlopen') as r:
   with self.assertRaises(w.WeatherSourceError):w._request('search.json',{'q':'X'})
   r.assert_not_called()

if __name__=='__main__':unittest.main()

class ContractTests(unittest.TestCase):
 def setUp(self):
  from chatify import weatherapi_contract
  self.contract=weatherapi_contract
  self.ev=[dict(e,n=i+1) for i,e in enumerate(w._evidence(PAYLOAD,'Bangalore'))]
 def test_native_catalog_no_legacy_semantics(self):
  fs=self.contract.facts(self.ev);self.assertEqual(len(fs),19);self.assertEqual(fs[0]['field'],'temp_c');self.assertFalse(any(f['field']=='precipitation' for f in fs))
  answer=self.contract.render(json.dumps({'answer':[{'fact_id':fs[0]['fact_id']}]}),self.ev)
  self.assertIn('reported current temperature 24 C',answer);self.assertIn('WeatherAPI.com',answer);self.assertNotIn('Open-Meteo',answer);self.assertNotIn('station observation',answer)
 def test_prose_and_wrong_field_rejected(self):
  for row in [{'text':'no rain'},{'fact_id':'1:2026-11-07:precipitation_probability_max'},{'fact_id':'1:2026-11-06T21:30:temp_c','value':90}]:
   with self.assertRaises(ValueError):self.contract.render(json.dumps({'answer':[row]}),self.ev)
 def test_forecast_date_zero_probability(self):
  answer=self.contract.render(json.dumps({'answer':[{'fact_id':'1:2026-11-07:daily_chance_of_rain'}]}),self.ev)
  self.assertIn('2026-11-07 (Asia/Kolkata): forecast rain chance 0%',answer);self.assertIn('predictions, not guarantees',answer);self.assertNotIn('will not rain',answer)
 def test_recovery_boundary_retains_typed_fields(self):
  from chatify.connectors.recovery import recover_evidence
  evidence=recover_evidence(self.ev,'weatherapi-weather',8)
  evidence=[dict(e,n=i+1) for i,e in enumerate(evidence)]
  self.assertEqual(len(self.contract.facts(evidence)),19)

class IntegrationTests(unittest.TestCase):
 def engine(self):
  import pathlib
  from chatify import schema
  from chatify.pipeline import Engine
  from chatify.store import Store
  cfg=schema.load(str(pathlib.Path(__file__).resolve().parent/'app.yaml'));cfg['provider']['type']='mock'
  return Engine(cfg,Store(':memory:'))
 def test_default_source_free_range_and_no_secret_url(self):
  e=self.engine();self.assertEqual(list(e.connectors),['weatherapi-weather']);self.assertFalse(e.cfg['retrieval']['query_rewrite'])
  self.assertNotIn('week',str(e.cfg['app']['examples']));self.assertIn('WeatherAPI',e.cfg['app']['footer'])
  for row in w._evidence(PAYLOAD,'Bengaluru'):self.assertEqual(row['url'],'')
 def test_actual_source_recovery_and_multicity_no_url_collision(self):
  e=self.engine();p2=dict(PAYLOAD,location=dict(PAYLOAD['location'],name='Mumbai'))
  rows=w._evidence(PAYLOAD,'Bengaluru')+w._evidence(p2,'Mumbai')
  with patch.object(w,'weatherapi',return_value=rows):
   from chatify.connectors.recovery import recover_evidence
   e.connectors['weatherapi-weather'].search=lambda q,k:recover_evidence(rows,'weatherapi-weather',k)
   result,errors=e.retrieve('Bengaluru Mumbai weather',['weatherapi-weather'],'owner')
  self.assertFalse(errors);self.assertEqual(len(result),2)
  from chatify import weatherapi_contract as c
  self.assertEqual(len(c.facts(result)),38)
 def test_sync_stream_no_raw_model_or_summary_on_boundary_one(self):
  from unittest.mock import Mock
  for stream in (False,True):
   e=self.engine();e.cfg['memory']['summary_every']=1;e.cfg['provider']['type']='openai'
   rows=[dict(x,n=i+1,text=x['text'].replace(__import__('datetime').datetime.now(__import__('datetime').timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),'2026-11-06 15:00 UTC')) for i,x in enumerate(w._evidence(PAYLOAD,'Bengaluru'))]
   e.retrieve=lambda *a,**k:(rows,{});e._llm_on=lambda *a:False
   e.provider.complete=Mock(return_value='{"answer":[{"fact_id":"1:2026-11-07:daily_chance_of_rain"}]}')
   e.provider.stream=Mock(side_effect=AssertionError('No raw model output'));e._summarize=Mock(side_effect=AssertionError('No summary'));e.followups=Mock(side_effect=AssertionError('No followups'))
   chat=e.store.new_chat('owner');r=list(e.ask_stream('owner',chat,'Rain tomorrow?'))[-1][1] if stream else e.ask('owner',chat,'Rain tomorrow?')
   self.assertEqual(e.provider.complete.call_count,1);self.assertIn('forecast rain chance 0%',r['answer']);self.assertEqual(r['model_status'],'ok');self.assertFalse(e._summarize.called)
 def test_clarification_deterministic_no_model(self):
  from unittest.mock import Mock
  e=self.engine();rows=[dict(w._clarify('Cambridge',[{'name':'Cambridge','country':'UK'},{'name':'Cambridge','country':'USA'}]),n=1)]
  e.provider.complete=Mock(side_effect=AssertionError('No model'))
  answer,status=e.weather_answer('Cambridge weather',rows);self.assertIn('No weather was fetched',answer);self.assertEqual(status,'ok');e.provider.complete.assert_not_called()
 def test_reviewed_source_check_no_model_secret_safe(self):
  from chatify.management import Management
  e=self.engine();m=Management(e.cfg,e,lambda:{},lambda x:None,e.store.export_all)
  plan=m.prepare_live('owner',{'model':False,'sources':['weatherapi-weather']})
  self.assertEqual(plan['model_calls'],0);self.assertEqual(plan['questions'],[e.cfg['app']['examples'][0]])

class RequestedPeriodTests(unittest.TestCase):
 def setUp(self):
  from chatify import weatherapi_contract as c
  self.c=c
  with patch.object(w,'datetime') as dt:
   from datetime import datetime,timezone
   dt.now.return_value=datetime(2026,11,6,22,56,tzinfo=timezone.utc)
   p=dict(PAYLOAD,current=dict(PAYLOAD['current'],last_updated='2026-11-07 04:15'))
   self.ev=[dict(e,n=i+1) for i,e in enumerate(w._evidence(p,'Bangalore'))]
 def test_real_failure_tomorrow_uses_place_date_not_utc_date(self):
  fs=self.c.requested_facts('Will it rain in Mumbai tomorrow?',self.ev)
  self.assertTrue(fs);self.assertEqual({f['valid'] for f in fs},{'2026-11-08'})
  with self.assertRaises(ValueError):self.c.render('{"answer":[{"fact_id":"1:2026-11-07:daily_chance_of_rain"}]}',self.ev,'Will it rain tomorrow?')
 def test_current_never_selects_daily_max(self):
  fs=self.c.requested_facts('weather right now',self.ev);self.assertTrue(fs);self.assertFalse(any(f['forecast'] for f in fs))
 def test_three_days_not_week_or_hour(self):
  for q in ['weather this week','hourly weather','weather next 7 days','weather tonight']:
   self.assertEqual(self.c.requested_facts(q,self.ev),[])
 def test_empty_catalog_no_model(self):
  from unittest.mock import Mock
  p=Mock();self.assertIn('does not support',self.c.synthesize(p,'weather this week',self.ev,'policy'));p.complete.assert_not_called()
 def test_valid_tomorrow_model_catalog_only_correct_date(self):
  from unittest.mock import Mock
  p=Mock();p.complete.return_value='{"answer":[{"fact_id":"1:2026-11-08:daily_chance_of_rain"}]}'
  answer=self.c.synthesize(p,'Will it rain tomorrow?',self.ev,'policy');self.assertIn('2026-11-08',answer)
  catalog=json.loads(p.complete.call_args.args[0][1]['content'])['facts'];self.assertEqual({f['valid'] for f in catalog},{'2026-11-08'})

class PlaceBindingTests(unittest.TestCase):
 def test_missing_search_id_stops_without_forecast(self):
  with patch.object(w,'_request',return_value=[{'name':'Mumbai','lat':19,'lon':73}]) as r:
   with self.assertRaises(w.WeatherSourceError):w.weatherapi('weather in Mumbai')
   self.assertEqual(r.call_count,1)
 def test_returned_different_place_rejected(self):
  with patch.object(w,'_request',side_effect=[[{'id':7,'name':'Mumbai','lat':19,'lon':73}],PAYLOAD]):
   with self.assertRaises(w.WeatherSourceError) as e:w.weatherapi('weather in Mumbai')
   self.assertIn('weather:forecast:place',str(e.exception))
 def test_multiplace_does_not_silently_choose_first(self):
  with patch.object(w,'_request') as r:
   rows=w.weatherapi('compare weather in Delhi and Mumbai today')
   self.assertTrue(rows[0]['id'].startswith('weatherapi-clarify-'));r.assert_not_called()

class TemporalAndCompoundTests(RequestedPeriodTests):
 def test_unknown_period_does_not_default_current(self):
  for q in ['How hot on Sunday?','Weather December 5','rain in 2 days','weather next month','weather later','weather at 6 pm','weather by noon','weather on 11/9']:
   with self.subTest(q=q):self.assertEqual(self.c.requested_facts(q,self.ev),[])
 def test_next_three_includes_today_and_disclosure(self):
  self.assertEqual({f['valid'] for f in self.c.requested_facts('weather next 3 days',self.ev)},{'2026-11-07','2026-11-08'})
  # Fixture intentionally has only Nov6-8. Missing Nov9 is not invented.
  answer=self.c.render('{"answer":[{"fact_id":"1:2026-11-08:maxtemp_c"}]}',self.ev,'weather next 3 days');self.assertIn('include today',answer)
 def test_compound_country_not_split_or_treated_as_comparison(self):
  with patch.object(w,'_request',return_value=[]) as r:
   self.assertEqual(w.weatherapi('Weather in Trinidad and Tobago today'),[])
   r.assert_called_once_with('search.json',{'q':'Trinidad and Tobago'})

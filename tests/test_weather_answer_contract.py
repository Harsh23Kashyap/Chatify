import unittest,json,sys,pathlib,tempfile
from unittest.mock import Mock
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from chatify import weather_contract as w, workspace, providers
from chatify.pipeline import Engine
from chatify.store import Store
from chatify import schema

class Tests(unittest.TestCase):
 def setUp(self):
  self.ev=[{'n':1,'id':'open-meteo-current-x','source':'open-meteo-weather','text':'This weather data is for Bengaluru, Karnataka, India.\nLive conditions valid at 2026-11-06T20:45 (Asia/Kolkata).\n- Temperature: 21.8 C (feels like 22.2 C)\n- Humidity: 90%\n- Wind: 5.2 km/h\n- Precipitation in the 15 minutes up to that time: 0.1 mm. Retrieved: 2026-11-06 15:15 UTC. All times below are Asia/Kolkata.'}]
  self.key='1:2026-11-06T20:45:temperature_2m'
  self.day=[dict(self.ev[0],id='open-meteo-tomorrow-mumbai',text='This weather data is for Mumbai, India.\nTomorrow in Mumbai, India (Asia/Kolkata):\n2026-11-07: clear, high 31.2 C, low 24.3 C, rain chance 0%, rain total 0.0 mm, max wind 12.1 km/h. Retrieved: 2026-11-06 15:15 UTC. All times below are Asia/Kolkata.')]
 def render(self,keys=None,ev=None):return w.render(json.dumps({'answer':[{'fact_id':k} for k in (keys if keys is not None else [self.key])]}),ev or self.ev)
 def test_valid_selection_is_typed_and_cited(self):
  s=self.render();self.assertIn('Bengaluru, Karnataka, India, 2026-11-06T20:45 (Asia/Kolkata): model temperature 21.8 C',s);self.assertIn('retrieved 2026-11-06 15:15 UTC. [1]',s)
 def test_humidity_cannot_be_temperature(self):
  s=self.render(['1:2026-11-06T20:45:relative_humidity_2m']);self.assertIn('relative humidity 90%',s);self.assertNotIn('temperature 90',s)
 def test_exact_reviewer_false_prose_counterexamples_rejected(self):
  for text in ['Temperature 90 C','Mumbai 21.8 C','Temperature below 21.8 C','There is no rain']:
   claim={'text':text,'sources':[1],'place':'Bengaluru, Karnataka, India','timezone':'Asia/Kolkata','validity':'2026-11-06T20:45'}
   with self.subTest(text=text),self.assertRaises(ValueError):w.render(json.dumps({'answer':[claim]}),self.ev)
 def test_extra_prose_cannot_override_selected_fact(self):
  for field,value in [('text','Mumbai temperature below 90 C'),('place','Mumbai'),('value','90'),('unit','F'),('relation','below'),('valid','2026-11-07')]:
   with self.subTest(field=field),self.assertRaises(ValueError):w.render(json.dumps({'answer':[{'fact_id':self.key,field:value}]}),self.ev)
 def test_wrong_source_or_field_or_date_rejected(self):
  for k in ['2:2026-11-06T20:45:temperature_2m','1:2026-11-07:temperature_2m','1:2026-11-06T20:45:rainfall','1:2026-11-06T20:45:temperature_2m:below']:
   with self.subTest(key=k),self.assertRaises(ValueError):self.render([k])
 def test_precipitation_window_not_observation(self):
  s=self.render(['1:2026-11-06T20:45:precipitation']);self.assertIn('model precipitation 0.1 mm in the 15 minutes up to that time',s);self.assertNotIn('recorded',s)
 def test_forecast_zero_probability_never_no_rain(self):
  s=self.render(['1:2026-11-07:precipitation_probability_max'],self.day);self.assertIn('Mumbai, India, 2026-11-07 (Asia/Kolkata): forecast rain chance 0%',s);self.assertIn('predictions, not guarantees',s);self.assertNotIn('will not rain',s);self.assertNotIn('no rain',s)
 def test_missing_field_not_zero(self):
  ev=[dict(self.day[0],text=self.day[0]['text'].replace('rain chance 0%','rain chance None%'))]
  self.assertFalse(any(f['field']=='precipitation_probability_max' for f in w.facts(ev)))
  with self.assertRaises(ValueError):self.render(['1:2026-11-07:precipitation_probability_max'],ev)
  self.assertIn('does not support',self.render([],ev))
 def test_each_forecast_date_stays_bound(self):
  ev=[dict(self.day[0],text=self.day[0]['text']+'\n2026-11-08: high 33 C, low 23 C, rain chance 20%')]
  s=self.render(['1:2026-11-08:temperature_2m_max'],ev);self.assertIn('2026-11-08 (Asia/Kolkata): forecast high temperature 33 C',s);self.assertNotIn('31.2 C',s)
 def test_unknown_answer_no_conclusion(self):self.assertEqual(self.render([]),w.UNKNOWN)
 def test_duplicate_selection_rejected(self):
  with self.assertRaises(ValueError):self.render([self.key,self.key])
 def test_missing_metadata_rejected(self):
  with self.assertRaises(ValueError):self.render(ev=[dict(self.ev[0],text='Temperature: 21.8 C')])
 def test_dotted_place_is_not_truncated(self):
  ev=[dict(self.ev[0],text=self.ev[0]['text'].replace('Bengaluru, Karnataka, India.','St. Louis, United States.'))];self.assertIn('St. Louis, United States,',self.render(ev=ev))
 def test_place_note_is_not_part_of_binding(self):
  ev=[dict(self.ev[0],text=self.ev[0]['text'].replace('India.\n','India. Place note: Matched Bengaluru.\n'))];self.assertEqual(w.facts(ev)[0]['place'],'Bengaluru, Karnataka, India')
 def test_no_out_of_range_percentage_or_negative_precip(self):
  ev=[dict(self.ev[0],text=self.ev[0]['text'].replace('90%','110%').replace('0.1 mm','-2 mm'))];fields=[f['field']for f in w.facts(ev)];self.assertNotIn('precipitation',fields);self.assertNotIn('relative_humidity_2m',fields)
 def test_one_real_selection_call_and_effective_policy(self):
  p=Mock();p.complete.return_value=json.dumps({'answer':[{'fact_id':self.key}]});w.synthesize(p,'temperature?',self.ev,'ACTIVE POLICY');self.assertEqual(p.complete.call_count,1);messages=p.complete.call_args.args[0];self.assertIn('ACTIVE POLICY',messages[0]['content']);self.assertIn('temperature_2m',messages[1]['content']);self.assertNotIn('"evidence"',messages[1]['content'])
 def engine(self):return Engine(schema.load(str(pathlib.Path(__file__).resolve().parents[1]/'apps/minimal/app.yaml')),Store(':memory:'))
 def test_no_override_policy(self):
  e=self.engine();self.assertIn(e.cfg['prompt']['system'],e.answer_constraints())
 def test_active_override_policy(self):
  e=self.engine();e.prompts.text=lambda key,fallback='':'CUSTOM ACTIVE ANSWER' if key=='answer' else fallback;self.assertIn('CUSTOM ACTIVE ANSWER',e.answer_constraints());self.assertNotIn(e.cfg['prompt']['system'],e.answer_constraints())
 def test_invalid_status_complete_lifecycle_roundtrip(self):
  with tempfile.TemporaryDirectory() as folder:
   e=self.engine();e.provider.complete=Mock(return_value='{"answer":[{"text":"Temperature 90 C"}]}');answer,status=e.weather_answer('temperature?',self.ev);self.assertEqual(status,'invalid_answer');self.assertEqual(answer,w.FAILURE)
   db=Store(str(pathlib.Path(folder)/'history.db'));chat=db.new_chat('owner');tid=db.add_turn(chat,None,'temperature?','temperature?',answer,[],[],'standard',model_status=status);db=Store(str(pathlib.Path(folder)/'history.db'));self.assertEqual(db.turn('owner',tid)['model_status'],status)
   target=db.add_turn(chat,None,'branch','branch','next',[],[],'standard');branch=db.branch('owner',target,'followup');self.assertEqual(db.turns('owner',branch['chat'])[0]['model_status'],status)
   payload=json.loads(json.dumps(workspace.archive(db.export_all('owner'))));clean=workspace.validate_archive(payload);dest=Store(':memory:');dest.import_chats('other',clean);self.assertEqual(dest.export_all('other')[0]['turns'][0]['model_status'],status)
 def test_provider_unavailable_remains_distinct(self):
  e=self.engine();e.provider.complete=Mock(side_effect=providers.ProviderError('timeout'));answer,status=e.weather_answer('temperature?',self.ev);self.assertEqual(status,'unreachable');self.assertIn('model is unavailable',answer)

 def test_summary_boundary_one_call_sync_and_stream(self):
  for stream in (False,True):
   for invalid in (False,True):
    with self.subTest(stream=stream,invalid=invalid):
     e=self.engine();e.cfg['app']['id']='weatherchat';e.cfg['memory'].update(enabled=True,summary_every=1);e.cfg['provider']['type']='openai';e.retrieve=lambda *a,**k:(self.ev,{});e._llm_on=lambda key:False;e.provider.complete=Mock(return_value='bad json' if invalid else json.dumps({'answer':[{'fact_id':self.key}]}));e.provider.stream=Mock(side_effect=AssertionError('raw stream forbidden'));e._summarize=Mock(side_effect=AssertionError('Weather summary forbidden'));e.followups=Mock(side_effect=AssertionError('Weather followups forbidden'))
     chat=e.store.new_chat('owner');r=list(e.ask_stream('owner',chat,'temperature?',use_cache=False))[-1][1] if stream else e.ask('owner',chat,'temperature?',use_cache=False);self.assertEqual(e.provider.complete.call_count,1);self.assertEqual(r['model_status'],'invalid_answer' if invalid else 'ok');self.assertFalse(e._summarize.called);self.assertFalse(e.followups.called)
 def test_actual_connector_fields_parse_offline(self):
  import importlib.util
  folder=pathlib.Path(__file__).resolve().parents[1]/'apps/weatherchat';sys.path.insert(0,str(folder))
  import weather_sources, test_weatherchat
  from unittest.mock import patch
  with patch('weather_sources._get',return_value=('https://api.open-meteo.com/v1/forecast',test_weatherchat.FORECAST)):
   evidence=weather_sources._evidence(test_weatherchat.GEO_BENGALURU['results'][0],[],queried='Bangalore')
  evidence=[dict(v,n=i+1) for i,v in enumerate(evidence)]
  facts=w.facts(evidence);self.assertEqual(len(facts),30);self.assertIn('question named "Bangalore"',facts[0]['place_note']);key=facts[0]['fact_id'];answer=self.render([key],evidence);self.assertIn('Source place match note:',answer);self.assertIn('Bengaluru, Karnataka, India',answer)

 def test_actual_gallery_provider_endpoint_not_inherited_ollama(self):
  from chatify import gallery
  root=pathlib.Path(__file__).resolve().parents[1]
  cfg=next(a['cfg']for a in gallery.load(str(root/'apps/gallery.yaml'))['apps']if a['slug']=='weatherchat')
  p=providers.make(cfg);self.assertEqual(cfg['provider']['type'],'openai');self.assertEqual(p.base,'https://api.openai.com/v1');self.assertEqual(cfg['provider']['api_key_env'],'OPENAI_API_KEY');self.assertEqual(cfg['budget']['daily_model_calls'],500);self.assertTrue(cfg['server']['public'])
  standalone=schema.load(str(root/'apps/weatherchat/app.yaml'));self.assertIn(providers.make(standalone).base,('http://127.0.0.1:11434','http://localhost:11434'))

if __name__=='__main__':unittest.main()

import copy,json,time,unittest,yaml,threading
import unittest.mock
from pathlib import Path
from customchat import buildjobs,schema,theme,prompts,generators
class Fixture:
 def __init__(self):self.calls=[];self.fail=None
 def complete(self,messages):
  system=messages[0]['content'];self.calls.append(system)
  if 'Review this complete merged draft' in system:return json.dumps({'issues':[],'ready':True})
  spec=json.JSONDecoder().raw_decode(system[system.index('{',system.index('This is one isolated')):])[0]
  if self.fail and self.fail==spec.get('stage'):self.fail=None;raise ValueError('fixture part failure')
  if spec['area']=='pipeline prompt':return json.dumps({'text':spec['default_prompt'],'on':True})
  if spec['area']=='inert Python helper':return json.dumps({'brief':'Fixture inert helper','code':generators.code_template(spec['kind'],'')})
  if spec['area']=='API recommendations':return json.dumps([{'name':'OpenAlex','reason':'Catalog','connector':'openalex','setup':'Review setup','caveat':'Verify limits'}])
  defaults=copy.deepcopy(spec['defaults'])
  if isinstance(defaults,dict):
   for key,value in defaults.items():
    if key.startswith('txt_') and not value:defaults[key]='Garden fixture wording'
   if spec['area']=='app':defaults['title']='Garden Field Guide';defaults['id']='garden';defaults['footer']='Garden fixture footer';defaults['examples']=['How do I grow basil?']
  return json.dumps(defaults)
class Jobs(unittest.TestCase):
 def wait(self,jobs,ident):
  for _ in range(500):
   data=jobs.view('owner',ident)
   if data['state']!='running':return data
   time.sleep(.01)
  self.fail('timeout')
 @unittest.mock.patch('customchat.buildimages.capability',return_value={'available':False,'note':'fixture'})
 def test_complete(self,cap):
  jobs=buildjobs.BuildJobs();f=Fixture();data=jobs.start('owner',f,schema.DEFAULTS,{'brief':'Garden advice'});data=self.wait(jobs,data['id']);self.assertEqual(data['state'],'done',data);raw=yaml.safe_load(data['yaml']);self.assertEqual(set(raw['pipeline_prompts']['text']),set(prompts.STAGES));self.assertEqual(set(raw['appearance']),set(theme.DEFAULT_CLEAN()));self.assertLessEqual(data['calls'],36);self.assertEqual(data['completed'],data['total']);self.assertEqual(len(f.calls),data['total']+1);self.assertRaises(ValueError,jobs.view,'wrong',data['id'])
 @unittest.mock.patch('customchat.buildimages.capability',return_value={'available':False,'note':'fixture'})
 def test_retry_only_failed(self,cap):
  jobs=buildjobs.BuildJobs();f=Fixture();f.fail=next(iter(prompts.STAGES));d=jobs.start('owner',f,schema.DEFAULTS,{'brief':'Garden advice'});d=self.wait(jobs,d['id']);self.assertEqual(d['state'],'partial');calls=d['calls'];jobs.retry('owner',d['id']);d=self.wait(jobs,d['id']);self.assertEqual(d['state'],'done',d);self.assertEqual(d['calls'],calls+2)
 def test_provider_block_stops_pending_calls(self):
  class Down:
   def complete(self,m):raise ValueError('The model is not responding right now')
  jobs=buildjobs.BuildJobs();d=jobs.start('owner',Down(),schema.DEFAULTS,{'brief':'Garden advice'});d=self.wait(jobs,d['id']);self.assertEqual(d['state'],'partial');self.assertLess(d['calls'],30);self.assertTrue(d['errors'])

class SafePatchChecks(unittest.TestCase):
 wait=Jobs.wait
 def part_job(self,output,brief='Garden advice',cfg=None):
  class P:
   def complete(self,m):return output
  return {'cancel':False,'calls':0,'provider':P(),'cfg':cfg or copy.deepcopy(schema.DEFAULTS),'parts':{},'errors':{},'active':set(),'brief':brief}
 def test_known_api_wrapper_only(self):
  rows=[{'name':'A','reason':'r','connector':'openalex','setup':'s','caveat':'c'}]
  for name in ['api_recommendations','api_suggestions']:
   job=self.part_job(json.dumps({name:rows}));buildjobs.BuildJobs()._draft_part(job,'api',dict(buildjobs.PARTS)['api']);self.assertEqual(job['parts']['api'],rows)
  job=self.part_job(json.dumps({'unrelated_requests':rows}))
  with self.assertRaises(ValueError):buildjobs.BuildJobs()._draft_part(job,'api',dict(buildjobs.PARTS)['api'])
  self.assertNotIn('api',job['parts'])
 def test_json_escape_not_silently_repaired(self):
  self.assertIsNone(buildjobs._extract_json('{"code":"bad\\s escape"}'))
  text={'code':r'Pattern \\s, path C:\\coastal'}
  self.assertEqual(buildjobs._extract_json(json.dumps(text)),text)
 def test_topic_language_never_sets_app_quotas(self):
  cfg=copy.deepcopy(schema.DEFAULTS);cfg['budget']['daily_questions']=42
  for brief in ['Garden advice','coastal advice','limit saturated fat','budget meals','daily nutrition','cap spending at $2','20 questions per day']:
   job=self.part_job(json.dumps(dict(cfg['budget'],daily_questions=5)),brief,cfg)
   buildjobs.BuildJobs()._draft_part(job,'config:budget',dict(buildjobs.PARTS)['config:budget'])
   self.assertEqual(job['parts']['config:budget'],cfg['budget'])
 @unittest.mock.patch('customchat.buildimages.capability',return_value={'available':False,'note':'fixture'})
 def test_blank_wording_retry_retains_successful_parts(self,cap):
  class Blank(Fixture):
   blank=True
   def complete(self,m):
    out=super().complete(m)
    if '"area": "appearance"' in m[0]['content'] and '"txt_disclaimer"' in m[0]['content'] and self.blank:
     self.blank=False;raw=json.loads(out);raw['txt_disclaimer']=' ';return json.dumps(raw)
    return out
  jobs=buildjobs.BuildJobs();f=Blank();d=self.wait(jobs,jobs.start('owner',f,schema.DEFAULTS,{'brief':'Garden advice'})['id'])
  self.assertEqual(d['state'],'partial');self.assertIn('appearance:wording_motion',d['errors']);before=copy.deepcopy(jobs.jobs[d['id']]['parts']);calls=d['calls']
  jobs.retry('owner',d['id']);d=self.wait(jobs,d['id']);self.assertEqual(d['state'],'done',d);self.assertEqual(d['calls'],calls+2)
  self.assertTrue(any('previous_validation_failure' in m and 'Interface wording left blank: txt_disclaimer' in m for m in f.calls))
  for k,v in before.items():self.assertEqual(jobs.jobs[d['id']]['parts'][k],v)
 def test_invalid_helper_json_reports_exact_corrective_contract(self):
  malformed='{"brief":"Cleaner","code":"re.sub(r\'\\s+\', \' \', query)"}'
  job=self.part_job(malformed)
  with self.assertRaisesRegex(ValueError,'invalid JSON.*double backslashes'):
   buildjobs.BuildJobs()._draft_part(job,'helper:clean_query',dict(buildjobs.PARTS)['helper:clean_query'])
  self.assertNotIn('helper:clean_query',job['parts']);self.assertEqual(job['calls'],1)
 @unittest.mock.patch('customchat.buildimages.capability',return_value={'available':False,'note':'fixture'})
 def test_review_context_keeps_unknowns_and_real_concerns(self,cap):
  class Review(Fixture):
   def complete(self,m):
    if 'Review this complete merged draft' in m[0]['content']:
     self.calls.append(m[0]['content']);return json.dumps({'issues':['Helper needs endpoint verification'],'ready':False})
    return super().complete(m)
  f=Review();jobs=buildjobs.BuildJobs();d=self.wait(jobs,jobs.start('owner',f,schema.DEFAULTS,{'brief':'Garden advice'})['id'])
  self.assertEqual(d['review']['issues'],['Helper needs endpoint verification']);self.assertFalse(d['review']['ready'])
  review=[m for m in f.calls if 'Application-provided context' in m][0]
  for text in ['no local count limit','no local dollar cap','not checked by this review','not tested','remaining setup prerequisites','Preserve genuine safety risks']:
   self.assertIn(text,review)

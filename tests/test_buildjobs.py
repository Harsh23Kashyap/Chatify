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

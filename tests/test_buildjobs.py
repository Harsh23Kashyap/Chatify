import copy,json,os,time,unittest,yaml,threading
import unittest.mock
from pathlib import Path
from chatify import buildjobs,schema,theme,prompts,generators
class Fixture:
 def __init__(self):self.calls=[];self.fail=None
 def complete(self,messages):
  system=messages[0]['content'];self.calls.append(system)
  if 'Review this complete merged draft' in system:return json.dumps({'issues':[],'ready':True})
  spec=json.JSONDecoder().raw_decode(system[system.index('{',system.index('This is one isolated')):])[0]
  if self.fail and self.fail==spec.get('stage'):self.fail=None;raise ValueError('fixture part failure')
  if spec['area']=='pipeline prompt':return json.dumps({'text':spec['domain_reference'],'on':True})
  if spec['area']=='inert Python helper':return json.dumps({'brief':'Fixture inert helper','code':generators.code_template(spec['kind'],'')})
  if spec['area']=='API recommendations':return json.dumps([{'service':service,'name':service,'what':'This service provides searchable information from published content and public data.','reason':'This service helps the app find background information for the reader questions.','connector':'openalex','setup':'Review setup','caveat':'Verify limits','helper':{'brief':service+' fixture helper','code':generators.code_template('search','')}} for service in ['OpenAlex','Wikipedia','Crossref']])
  defaults=copy.deepcopy(spec['defaults'])
  if isinstance(defaults,dict):
   for key,value in defaults.items():
    if key.startswith('txt_') and not value:defaults[key]='Garden fixture wording'
   if spec['area']=='app':defaults['title']='Garden Field Guide';defaults['id']='garden';defaults['footer']='Garden fixture footer';defaults['examples']=['How do I grow basil?']
  return json.dumps(defaults)
class Checkpoints(unittest.TestCase):
 def wait(self,jobs,ident):
  for _ in range(500):
   data=jobs.view('owner',ident)
   if data['state']!='running':return data
   time.sleep(.01)
  self.fail('timeout')
 @unittest.mock.patch('chatify.buildimages.capability',return_value={'available':False,'note':'fixture'})
 def test_resume_keeps_finished_parts_after_restart(self,cap):
  import tempfile
  with tempfile.TemporaryDirectory() as tmp:
   jobs=buildjobs.BuildJobs(spend_dir=tmp);f=Fixture();f.fail=next(iter(prompts.STAGES))
   d=self.wait(jobs,jobs.start('owner',f,schema.DEFAULTS,{'brief':'Garden advice'})['id'])
   self.assertEqual(d['state'],'partial');first_calls=len(f.calls)
   saved=[n for n in os.listdir(os.path.join(tmp,'build-checkpoints')) if n.endswith('.json')]
   self.assertEqual(len(saved),1)
   payload=json.load(open(os.path.join(tmp,'build-checkpoints',saved[0])))
   self.assertEqual(len(payload['parts']),d['completed']);self.assertNotIn('cfg',payload);self.assertNotIn('provider',payload)
   # simulated restart: a fresh BuildJobs over the same directory
   jobs2=buildjobs.BuildJobs(spend_dir=tmp);f2=Fixture()
   d2=jobs2.start('owner',f2,schema.DEFAULTS,{'brief':'Garden advice'})
   self.assertIn('Resumed from a saved checkpoint',d2['notice'])
   d2=self.wait(jobs2,d2['id']);self.assertEqual(d2['state'],'done',d2)
   self.assertLessEqual(len(f2.calls),4,'only the failed part plus final review run after resume: '+str(len(f2.calls)))
   # the checkpoint clear runs just after the state flips to done; allow that ordering
   for _ in range(200):
    if not os.listdir(os.path.join(tmp,'build-checkpoints')):break
    time.sleep(.01)
   self.assertEqual(os.listdir(os.path.join(tmp,'build-checkpoints')),[])
 @unittest.mock.patch('chatify.buildimages.capability',return_value={'available':False,'note':'fixture'})
 def test_different_brief_starts_fresh(self,cap):
  import tempfile
  with tempfile.TemporaryDirectory() as tmp:
   jobs=buildjobs.BuildJobs(spend_dir=tmp);f=Fixture();f.fail=next(iter(prompts.STAGES))
   self.wait(jobs,jobs.start('owner',f,schema.DEFAULTS,{'brief':'Garden advice'})['id'])
   jobs2=buildjobs.BuildJobs(spend_dir=tmp);f2=Fixture()
   d2=jobs2.start('owner',f2,schema.DEFAULTS,{'brief':'Astronomy questions'})
   self.assertNotIn('Resumed',d2.get('notice',''))
   d2=self.wait(jobs2,d2['id']);self.assertEqual(d2['state'],'done',d2)
   self.assertGreater(len(f2.calls),20,'fresh build reruns all parts')

class CheckpointEdges(unittest.TestCase):
 def wait(self,jobs,ident):
  for _ in range(500):
   data=jobs.view('owner',ident)
   if data['state']!='running':return data
   time.sleep(.01)
  self.fail('timeout')
 def fp(self,cfg):
  return buildjobs.BuildJobs._fingerprint(cfg)
 def cpfile(self,tmp,jobs,owner='owner'):
  return jobs._checkpoint_path(owner)
 @unittest.mock.patch('chatify.buildimages.capability',return_value={'available':False,'note':'fixture'})
 def test_model_change_starts_fresh(self,cap):
  import tempfile
  with tempfile.TemporaryDirectory() as tmp:
   jobs=buildjobs.BuildJobs(spend_dir=tmp);f=Fixture();f.fail=next(iter(prompts.STAGES))
   self.wait(jobs,jobs.start('owner',f,schema.DEFAULTS,{'brief':'Garden advice'})['id'])
   changed=copy.deepcopy(schema.DEFAULTS);changed['provider']['model']='some-other-model'
   jobs2=buildjobs.BuildJobs(spend_dir=tmp);f2=Fixture()
   d2=jobs2.start('owner',f2,changed,{'brief':'Garden advice'})
   self.assertNotIn('Resumed',d2.get('notice',''))
   # start() launches workers before returning; completed may already be positive.
   # No-resume notice plus a complete fresh call inventory below proves fresh work.
   d2=self.wait(jobs2,d2['id']);self.assertEqual(d2['state'],'done',d2);self.assertGreater(len(f2.calls),20)
 @unittest.mock.patch('chatify.buildimages.capability',return_value={'available':False,'note':'fixture'})
 def test_changed_budget_settings_start_fresh(self,cap2):
  import tempfile
  with tempfile.TemporaryDirectory() as tmp:
   jobs=buildjobs.BuildJobs(spend_dir=tmp);f=Fixture();f.fail=next(iter(prompts.STAGES))
   self.wait(jobs,jobs.start('owner',f,schema.DEFAULTS,{'brief':'Garden advice'})['id'])
   changed=copy.deepcopy(schema.DEFAULTS);changed['budget']['spend_cap_usd']=3.5
   jobs2=buildjobs.BuildJobs(spend_dir=tmp);f2=Fixture()
   d2=jobs2.start('owner',f2,changed,{'brief':'Garden advice'})
   self.assertNotIn('Resumed',d2.get('notice',''))
   # start() launches workers before returning; completed may already be positive.
   # No-resume notice plus a complete fresh call inventory below proves fresh work.
   d2=self.wait(jobs2,d2['id']);self.assertEqual(d2['state'],'done',d2);self.assertGreater(len(f2.calls),20)
 @unittest.mock.patch('chatify.buildimages.capability',return_value={'available':False,'note':'fixture'})
 def test_corrupt_checkpoint_starts_fresh(self,cap):
  import tempfile
  with tempfile.TemporaryDirectory() as tmp:
   jobs=buildjobs.BuildJobs(spend_dir=tmp)
   path=jobs._checkpoint_path('owner');os.makedirs(os.path.dirname(path));open(path,'w').write('{not json')
   f=Fixture();d=jobs.start('owner',f,schema.DEFAULTS,{'brief':'Garden advice'})
   self.assertNotIn('Resumed',d.get('notice',''))
   d=self.wait(jobs,d['id']);self.assertEqual(d['state'],'done',d)
 def test_unknown_part_keys_filtered_on_resume(self):
  import tempfile
  with tempfile.TemporaryDirectory() as tmp:
   jobs=buildjobs.BuildJobs(spend_dir=tmp)
   path=jobs._checkpoint_path('owner');os.makedirs(os.path.dirname(path))
   json.dump({'brief':'Garden advice','fingerprint':self.fp(schema.DEFAULTS),'writer':'old','parts':{'config:app':{'title':'Kept garden'},'bogus:key':{'x':1}},'errors':{},'calls':5,'retry_calls':0,'updated':time.time()},open(path,'w'))
   gate=threading.Event()
   class Slow:
    def complete(self,messages):gate.wait(10);raise ValueError('released')
   jobs2=buildjobs.BuildJobs(spend_dir=tmp)
   d=jobs2.start('owner',Slow(),schema.DEFAULTS,{'brief':'Garden advice'})
   try:
    self.assertIn('Resumed from a saved checkpoint',d['notice'])
    ids=[p['id'] for p in d['parts'] if p['state']=='done']
    self.assertEqual(ids,['config:app'],'only the valid checkpointed part is kept: '+str(ids))
   finally:
    jobs2.cancel('owner',d['id']);gate.set()
 def test_stale_writer_cannot_clear_newer_checkpoint(self):
  import tempfile
  with tempfile.TemporaryDirectory() as tmp:
   jobs=buildjobs.BuildJobs(spend_dir=tmp)
   path=jobs._checkpoint_path('owner');os.makedirs(os.path.dirname(path))
   json.dump({'brief':'B','writer':'newer-job','parts':{},'errors':{},'calls':0,'updated':time.time()},open(path,'w'))
   jobs._checkpoint_clear('owner','older-job')
   self.assertTrue(os.path.exists(path),'stale writer must not clear a newer checkpoint')
   jobs._checkpoint_clear('owner','newer-job')
   self.assertFalse(os.path.exists(path))
 @unittest.mock.patch('chatify.buildimages.capability',return_value={'available':False,'note':'fixture'})
 def test_cancelled_inflight_writes_no_checkpoint(self,cap):
  import tempfile
  with tempfile.TemporaryDirectory() as tmp:
   gate=threading.Event()
   class Slow:
    def complete(self,messages):gate.wait(10);raise ValueError('released')
   jobs=buildjobs.BuildJobs(spend_dir=tmp)
   d=jobs.start('owner',Slow(),schema.DEFAULTS,{'brief':'Garden advice'})
   jobs.cancel('owner',d['id']);gate.set()
   d=self.wait(jobs,d['id']);self.assertEqual(d['state'],'cancelled',d)
   self.assertFalse(os.path.exists(jobs._checkpoint_path('owner')),'cancelled build must not leave a checkpoint')
 def test_resume_never_touches_persisted_spend(self):
  import tempfile
  with tempfile.TemporaryDirectory() as tmp:
   jobs=buildjobs.BuildJobs(spend_dir=tmp)
   jobs.spend={'day':time.strftime('%Y-%m-%d',time.gmtime()),'est_usd':buildjobs.DAILY_SPEND_CAP_USD,'calls':99}
   jobs._spend_record(0,0)
   before=open(jobs.spend_path).read()
   path=jobs._checkpoint_path('owner');os.makedirs(os.path.dirname(path))
   json.dump({'brief':'Garden advice','fingerprint':self.fp(schema.DEFAULTS),'writer':'old','parts':{'config:app':{'title':'Kept'}},'errors':{},'calls':5,'retry_calls':0,'updated':time.time()},open(path,'w'))
   jobs2=buildjobs.BuildJobs(spend_dir=tmp)
   d=jobs2.start('owner',Fixture(),schema.DEFAULTS,{'brief':'Garden advice'})
   d=self.wait(jobs2,d['id'])
   self.assertEqual(d['state'],'partial',d)
   self.assertTrue(any('spend cap' in m for m in d['errors'].values()),d['errors'])
   self.assertEqual(open(jobs.spend_path).read(),before,'resume path must not reset persisted spend')

class ActiveView(unittest.TestCase):
 def test_active_empty(self):
  jobs=buildjobs.BuildJobs();data=jobs.active('owner');self.assertEqual(data,{'active':False,'running_total':0,'mine':[]})
 def test_active_scopes_details_to_owner(self):
  gate=threading.Event()
  class Slow:
   def complete(self,messages):gate.wait(10);raise ValueError('released')
  jobs=buildjobs.BuildJobs()
  own=jobs.start('owner',Slow(),schema.DEFAULTS,{'brief':'Private owner brief'})
  other=jobs.start('other',Slow(),schema.DEFAULTS,{'brief':'Private other brief'})
  try:
   data=jobs.active('owner')
   self.assertTrue(data['active']);self.assertEqual(data['running_total'],2);self.assertEqual(len(data['mine']),1)
   mine=data['mine'][0];self.assertEqual(mine['id'],own['id']);self.assertIn('phase',mine);self.assertIn('completed',mine);self.assertIn('total',mine)
   blob=json.dumps(data)
   self.assertNotIn('Private other brief',blob);self.assertNotIn(other['id'],blob)
   for entry in data['mine']:
    self.assertNotIn('brief',entry);self.assertNotIn('cfg',entry)
   nobody=jobs.active('nobody');self.assertEqual(nobody['running_total'],2);self.assertEqual(nobody['mine'],[])
  finally:
   jobs.cancel('owner',own['id']);jobs.cancel('other',other['id']);gate.set()

class Jobs(unittest.TestCase):
 def wait(self,jobs,ident):
  for _ in range(500):
   data=jobs.view('owner',ident)
   if data['state']!='running':return data
   time.sleep(.01)
  self.fail('timeout')
 @unittest.mock.patch('chatify.buildimages.capability',return_value={'available':False,'note':'fixture'})
 def test_complete(self,cap):
  jobs=buildjobs.BuildJobs();f=Fixture();data=jobs.start('owner',f,schema.DEFAULTS,{'brief':'Garden advice'});data=self.wait(jobs,data['id']);self.assertEqual(data['state'],'done',data);raw=yaml.safe_load(data['yaml']);self.assertEqual(set(raw['pipeline_prompts']['text']),set(prompts.STAGES));self.assertEqual(set(raw['appearance']),set(theme.DEFAULT_CLEAN()));self.assertLessEqual(data['calls'],36);self.assertEqual(data['completed'],data['total']);self.assertEqual(len(f.calls),data['total']+1);self.assertRaises(ValueError,jobs.view,'wrong',data['id'])
 @unittest.mock.patch('chatify.buildimages.capability',return_value={'available':False,'note':'fixture'})
 def test_retry_only_failed(self,cap):
  jobs=buildjobs.BuildJobs();f=Fixture();f.fail=next(iter(prompts.STAGES));d=jobs.start('owner',f,schema.DEFAULTS,{'brief':'Garden advice'});d=self.wait(jobs,d['id']);self.assertEqual(d['state'],'partial');calls=d['calls'];jobs.retry('owner',d['id']);d=self.wait(jobs,d['id']);self.assertEqual(d['state'],'done',d);self.assertEqual(d['calls'],calls+2);self.assertEqual(d['retry_calls'],2)
 @unittest.mock.patch('chatify.buildimages.generate',return_value='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAAB')
 @unittest.mock.patch('chatify.buildimages.capability',return_value={'available':True,'provider':'openai','model':'fixture-image','note':'fixture'})
 def test_optional_logo_reaches_final_review_and_completed_draft(self,cap,generate):
  jobs=buildjobs.BuildJobs();f=Fixture()
  data=self.wait(jobs,jobs.start('owner',f,schema.DEFAULTS,{'brief':'Garden advice'})['id'])
  self.assertEqual(data['state'],'done',data)
  generate.assert_called_once()
  self.assertEqual(data['logo_status']['state'],'done',data['logo_status'])
  self.assertEqual(data['calls'],data['total']+2)
  self.assertEqual(data['errors'],{})
  self.assertTrue(any('Review this complete merged draft' in call for call in f.calls))
  self.assertEqual(data['remaining_work'],[])
  self.assertEqual(yaml.safe_load(data['yaml'])['appearance']['logo'],generate.return_value)
 @unittest.mock.patch('chatify.buildimages.generate',side_effect=ValueError('fixture image unavailable'))
 @unittest.mock.patch('chatify.buildimages.capability',return_value={'available':True,'provider':'openai','model':'fixture-image','note':'fixture'})
 def test_optional_logo_failure_keeps_text_draft_and_finishes_review(self,cap,generate):
  jobs=buildjobs.BuildJobs();f=Fixture()
  data=self.wait(jobs,jobs.start('owner',f,schema.DEFAULTS,{'brief':'Garden advice'})['id'])
  self.assertEqual(data['state'],'done',data)
  generate.assert_called_once()
  self.assertEqual(data['logo_status']['state'],'skipped')
  self.assertIn('fixture image unavailable',data['logo_status']['note'])
  self.assertNotIn('MAX_CALLS',data['logo_status']['note'])
  self.assertTrue(data['yaml'])
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
  rows=[{'name':service,'service':service,'what':'This service provides searchable information from published content and public data.','reason':'This service helps the app find background information for the reader questions.','connector':'openalex','setup':'s','caveat':'c','helper':{'brief':'Fixture','code':generators.code_template('search','')}} for service in ['OpenAlex','Wikipedia','Crossref']]
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
 @unittest.mock.patch('chatify.buildimages.capability',return_value={'available':False,'note':'fixture'})
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
  jobs.retry('owner',d['id']);d=self.wait(jobs,d['id']);self.assertEqual(d['state'],'done',d);self.assertEqual(d['calls'],calls+2);self.assertEqual(d['retry_calls'],2)
  self.assertTrue(any('previous_validation_failure' in m and 'Interface wording left blank: txt_disclaimer' in m for m in f.calls))
  for k,v in before.items():self.assertEqual(jobs.jobs[d['id']]['parts'][k],v)
 def test_invalid_helper_json_reports_exact_corrective_contract(self):
  malformed='{"brief":"Cleaner","code":"re.sub(r\'\\s+\', \' \', query)"}'
  job=self.part_job(malformed)
  # JSON salvage is tested separately in DraftJSONRepairTests. Salvage must
  # not authorize an executable fragment lacking the required helper function.
  with self.assertRaisesRegex(ValueError,'Helper safety contract failed'):
   buildjobs.BuildJobs()._draft_part(job,'helper:clean_query',dict(buildjobs.PARTS)['helper:clean_query'])
  self.assertNotIn('helper:clean_query',job['parts']);self.assertEqual(job['calls'],1)
 @unittest.mock.patch('chatify.buildimages.capability',return_value={'available':False,'note':'fixture'})
 def test_review_context_keeps_unknowns_and_real_concerns(self,cap):
  class Review(Fixture):
   def complete(self,m):
    if 'Review this complete merged draft' in m[0]['content']:
     self.calls.append(m[0]['content']);return json.dumps({'issues':['Helper needs endpoint verification'],'setup_notes':['Add source documents'],'ready':False})
    return super().complete(m)
  f=Review();jobs=buildjobs.BuildJobs();d=self.wait(jobs,jobs.start('owner',f,schema.DEFAULTS,{'brief':'Garden advice'})['id'])
  self.assertEqual(d['review']['issues'],['Helper needs endpoint verification']);self.assertFalse(d['review']['ready']);self.assertEqual(d['review']['setup_notes'],['Add source documents']);self.assertIn('not deployment readiness',d['review']['scope'])
  review=[m for m in f.calls if 'Application-provided context' in m][0]
  for text in ['no local count limit','no local dollar cap','not checked by this review','not tested','remaining deployment prerequisites','Preserve genuine safety risks']:
   self.assertIn(text,review)
 @unittest.mock.patch('chatify.buildimages.capability',return_value={'available':False,'note':'fixture'})
 def test_review_verdict_never_erases_concerns_or_uncertainty(self,cap):
  for response,expected in [({'issues':[],'ready':False},'inconsistent'),({'issues':['Unsupported medical claim'],'ready':True},'inconsistent'),({'issues':['Cannot assess helper endpoint'],'ready':False},'concerns'),({'issues':[],'setup_notes':['Add sources'],'ready':True},'completed')]:
   class R(Fixture):
    def complete(self,m):
     if 'Review this complete merged draft' in m[0]['content']:return json.dumps(response)
     return super().complete(m)
   jobs=buildjobs.BuildJobs();d=self.wait(jobs,jobs.start('owner',R(),schema.DEFAULTS,{'brief':'Garden advice'})['id'])
   self.assertEqual(d['review']['review_status'],expected);self.assertEqual(d['review']['ready'],response['ready']);self.assertEqual(d['review']['issues'],response['issues'])

class RetainedFailureMatrix(unittest.TestCase):
 wait=Jobs.wait
 @unittest.mock.patch('chatify.buildimages.capability',return_value={'available':False,'note':'fixture'})
 def test_targeted_contract_failures_retry_only_owner_and_keep_success(self,cap):
  for target,broken in [('prompt:answer',{'text':'','on':True}),('helper:clean_query',{'brief':'Fixture','code':'def broken(:'}),('config:sources',[{'type':'url','url':'https://not-supplied.invalid/fixture'}]),('prompt:standalone',{'text':'Example question: What should I eat? Rewrite question: What diet is best?','on':True})]:
   with self.subTest(target=target):
    class BadOnce(Fixture):
     failed=False
     def complete(self,m):
      result=super().complete(m)
      system=m[0]['content']
      if 'This is one isolated' not in system:return result
      spec=json.JSONDecoder().raw_decode(system[system.index('{',system.index('This is one isolated')):])[0]
      hit=(target.startswith('prompt:') and spec.get('stage')==target.split(':')[1]) or (target=='helper:clean_query' and spec.get('kind')=='clean_query') or (target=='config:sources' and spec.get('area')=='sources')
      if hit and not self.failed:self.failed=True;return json.dumps(broken)
      return result
    f=BadOnce();jobs=buildjobs.BuildJobs();d=self.wait(jobs,jobs.start('owner',f,schema.DEFAULTS,{'brief':'Garden advice'})['id'])
    self.assertTrue(f.failed,target);self.assertEqual(d['state'],'partial',d);self.assertIn(target,d['errors']);self.assertNotIn(target,jobs.jobs[d['id']]['parts'])
    kept=copy.deepcopy(jobs.jobs[d['id']]['parts']);calls=d['calls'];self.assertEqual(len(kept),len(buildjobs.PARTS)-1)
    jobs.retry('owner',d['id']);done=self.wait(jobs,d['id']);self.assertEqual(done['state'],'done',done);self.assertEqual(done['calls'],calls+2);self.assertEqual(done['retry_calls'],2)
    for key,value in kept.items():self.assertEqual(jobs.jobs[d['id']]['parts'][key],value)

class DraftJSONRepairTests(unittest.TestCase):
 def test_illegal_escape_preserves_literal_regex(self):
  raw=r'{"brief":"Cleaner","code":"re.sub(r\'\s+\', \' \', query)"}'.replace("\\'", "'")
  self.assertEqual(buildjobs.parse_draft_json(raw)['code'],"re.sub(r'\\s+', ' ', query)")
 def test_truncated_and_missing_fields_never_invented(self):
  self.assertIsNone(buildjobs.parse_draft_json('{"light":'))
  self.assertEqual(buildjobs.parse_draft_json('{"brief":"only"}'),{'brief':'only'})

class BrandingRetryTests(unittest.TestCase):
 def test_final_branding_redrafts_identity_only(self):
  from unittest.mock import patch
  jobs=buildjobs.BuildJobs();cfg=schema.validate({})
  job={'id':'x','owner':'owner','state':'partial','calls':31,'errors':{'final':'App branding was not tailored to the request'},'parts':{k:copy.deepcopy(v['defaults']) if 'defaults' in v else {} for k,v in buildjobs.PARTS},'cfg':cfg,'active':set(),'phase':'Final local validation','notice':'fixture','yaml':None,'created':time.time()}
  jobs.jobs['x']=job
  before=copy.deepcopy(job['parts'])
  # Patch the module binding, not threading.Thread process-wide: unrelated
  # executor workers can otherwise overwrite this mock's last call.
  with patch('chatify.buildjobs.threading') as threads:
   jobs.retry('owner','x')
   selected=threads.Thread.call_args.kwargs['args'][1]
  self.assertEqual([k for k,_ in selected],['config:app'])
  self.assertNotIn('config:app',job['parts'])
  for k,v in before.items():
   if k!='config:app':self.assertEqual(job['parts'][k],v)

class DomainPromptChecks(SafePatchChecks):
 def test_builtin_generic_stage_is_rejected(self):
  stage='question_check';job=self.part_job(json.dumps({'text':prompts.STAGES[stage]['default'],'on':True}),'A trip planning app')
  with self.assertRaisesRegex(ValueError,'app-specific prompt'):buildjobs.BuildJobs()._draft_part(job,'prompt:'+stage,dict(buildjobs.PARTS)['prompt:'+stage])
 def test_every_stage_request_has_domain_and_stage_contract(self):
  from chatify import generator_design
  for domain in ['Trip planning','Diet app','Sports app']:
   for stage in prompts.STAGES:
    job=self.part_job(json.dumps({'text':generator_design.template(stage,domain),'on':True}),domain)
    buildjobs.BuildJobs()._draft_part(job,'prompt:'+stage,dict(buildjobs.PARTS)['prompt:'+stage])
    self.assertIn('prompt:'+stage,job['parts'])

class APIDescriptionChecks(SafePatchChecks):
 def test_name_only_api_description_rejected(self):
  picks=[{'name':name,'service':name,'what':name,'reason':'This API helps the app provide background information about destinations.','helper':{'brief':'Fixture','code':generators.code_template('search','')}} for name in ['Wikipedia','Brave Search','Open-Meteo']]
  job=self.part_job(json.dumps(picks))
  with self.assertRaisesRegex(ValueError,'useful sentence'):buildjobs.BuildJobs()._draft_part(job,'api',dict(buildjobs.PARTS)['api'])
 def test_too_few_api_picks_rejected(self):
  job=self.part_job(json.dumps([{'name':'Wikipedia','service':'Wikipedia','helper':{'brief':'Fixture','code':generators.code_template('search','')}}]))
  with self.assertRaisesRegex(ValueError,'three to five'):buildjobs.BuildJobs()._draft_part(job,'api',dict(buildjobs.PARTS)['api'])
class RetryCompletion(unittest.TestCase):
 def wait(self,jobs,ident):
  for _ in range(500):
   data=jobs.view('owner',ident)
   if data['state']!='running':return data
   time.sleep(.01)
  self.fail('timeout')
 @unittest.mock.patch('chatify.buildimages.capability',return_value={'available':False,'note':'fixture'})
 def test_stubborn_part_filled_locally_and_build_completes(self,cap):
  class AlwaysFail(Fixture):
   def complete(self,messages):
    system=messages[0]['content']
    if 'This is one isolated' in system:
     spec=json.JSONDecoder().raw_decode(system[system.index('{',system.index('This is one isolated')):])[0]
     if spec.get('area')=='appearance' and 'font' in spec.get('defaults',{}):raise ValueError('fixture always fails')
    return super().complete(messages)
  jobs=buildjobs.BuildJobs();f=AlwaysFail();d=jobs.start('owner',f,schema.DEFAULTS,{'brief':'Garden advice'});d=self.wait(jobs,d['id']);self.assertEqual(d['state'],'partial')
  for _ in range(buildjobs.MAX_PART_ATTEMPTS-1):
   jobs.retry('owner',d['id']);d=self.wait(jobs,d['id']);self.assertEqual(d['state'],'partial')
  jobs.retry('owner',d['id']);d=self.wait(jobs,d['id'])
  self.assertEqual(d['state'],'done',d)
  self.assertIn('appearance:fonts',d['defaulted'])
  self.assertIn('safe defaults',d['notice'])
  self.assertEqual(d['calls'],32+buildjobs.MAX_PART_ATTEMPTS-1);self.assertEqual(d['retry_calls'],buildjobs.MAX_PART_ATTEMPTS-1+1)
  raw=yaml.safe_load(d['yaml']);self.assertEqual(set(raw['appearance']),set(theme.DEFAULT_CLEAN()));self.assertTrue(raw['appearance']['font'])

class SourceSelectionChecks(SafePatchChecks):
 def test_unnamed_public_connector_is_not_activated(self):
  job=self.part_job(json.dumps([{'id':'wiki','type':'wikipedia','label':'Wikipedia','weight':1.0}]),'Read uploaded library documents; no live APIs are needed')
  with self.assertRaisesRegex(ValueError,'not named or selected'):buildjobs.BuildJobs()._draft_part(job,'config:sources',dict(buildjobs.PARTS)['config:sources'])
 def test_named_public_connector_remains_available(self):
  job=self.part_job(json.dumps([{'id':'wiki','type':'wikipedia','label':'Wikipedia','weight':1.0}]),'Use Wikipedia for background reading')
  buildjobs.BuildJobs()._draft_part(job,'config:sources',dict(buildjobs.PARTS)['config:sources'])
  self.assertEqual(job['parts']['config:sources'][0]['type'],'wikipedia')

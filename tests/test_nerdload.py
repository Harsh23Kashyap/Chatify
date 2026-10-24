import base64,io,tempfile,unittest,zipfile
from pathlib import Path
from chatify.nerdload import NerdLoader
from chatify import schema
from chatify.portable import bundle
class NerdLoadTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.loader=NerdLoader(self.root);self.addCleanup(self.loader.close)
 def encoded(self,files):
  out=io.BytesIO()
  with zipfile.ZipFile(out,'w') as z:
   for n,d in files.items():z.writestr(n,d)
  return base64.b64encode(out.getvalue()).decode()
 def test_review_does_not_run_python(self):
  cfg='sources: [{id: plugin, type: python, entry: example:search}]'
  d=self.loader.review('demo.zip',self.encoded({'app.yaml':cfg,'example.py':'raise RuntimeError("must not execute")'}));self.assertEqual(len(d['code']),1)
  with self.assertRaisesRegex(ValueError,'Review Python'):self.loader.load(d['token'])
 def test_path_traversal(self):
  with self.assertRaisesRegex(ValueError,'Unsafe path'):self.loader.review('d.zip',self.encoded({'../bad.txt':'x','app.yaml':'{}'}))
 def test_env_rejected(self):
  with self.assertRaisesRegex(ValueError,'Private file.*.env'):self.loader.review('d.zip',self.encoded({'.env':'secret','app.yaml':'{}'}))
 def test_yaml_without_documents_loads_empty_folder(self):
  d=self.loader.review('app.yaml',base64.b64encode(b'sources: [{id: docs, type: local_files, path: docs}]').decode())
  self.assertTrue(any('No documents included' in r['message'] for r in d['readiness']['rows']))
  r=self.loader.load(d['token']);self.assertTrue((Path(r['workspace'])/'docs').is_dir())
 def test_export_empty_source_roundtrip(self):
  (self.root/'docs').mkdir();cfg=schema.validate({'sources':[{'id':'docs','type':'local_files','path':'docs'}]});cfg['_dir']=str(self.root)
  data,_=bundle(cfg);d=self.loader.review('nerd.zip',base64.b64encode(data).decode());r=self.loader.load(d['token'])
  self.assertTrue((Path(r['workspace'])/'assets/source-1').is_dir())
 def test_inline_secret_rejected(self):
  raw=b'sources: [{id: x, type: http_json, url: "https://a.example/?token=secret"}]'
  with self.assertRaises(ValueError):self.loader.review('app.yaml',base64.b64encode(raw).decode())
 def test_local_roundtrip_start(self):
  (self.root/'docs').mkdir();(self.root/'docs/guide.md').write_text('Local evidence');cfg=schema.validate({'app':{'title':'Loaded Nerd'},'sources':[{'id':'guide','type':'local_files','path':'docs'}]});cfg['_dir']=str(self.root)
  data,_=bundle(cfg);d=self.loader.review('nerd.zip',base64.b64encode(data).decode());r=self.loader.load(d['token']);self.assertTrue(r['url'].startswith('http://127.0.0.1:'));self.assertEqual(r['title'],'Loaded Nerd')
 def test_missing_python(self):
  with self.assertRaisesRegex(ValueError,'missing'):self.loader.review('app.yaml',base64.b64encode(b'sources: [{id: x, type: python, entry: absent:search}]').decode())
 def test_auth_not_silently_replaced(self):
  with self.assertRaisesRegex(ValueError,'auth.mode'):self.loader.review('app.yaml',base64.b64encode(b'auth: {mode: accounts}').decode())
 def test_stop_list_remove(self):
  (self.root/'docs').mkdir();(self.root/'docs/guide.md').write_text('Local evidence');cfg=schema.validate({'sources':[{'id':'guide','type':'local_files','path':'docs'}]});cfg['_dir']=str(self.root)
  data,_=bundle(cfg);d=self.loader.review('nerd.zip',base64.b64encode(data).decode());self.loader.load(d['token']);row=self.loader.list()[0];self.assertTrue(row['running']);self.loader.stop(row['id']);self.assertFalse(self.loader.list()[0]['running'])
  with self.assertRaises(ValueError):self.loader.remove(row['id'],False)
  folder=self.loader.workspaces[row['id']]['folder'];self.loader.remove(row['id'],True);self.assertFalse(folder.exists());self.assertEqual(self.loader.list(),[]);self.assertTrue((self.root/'docs/guide.md').exists())
 def test_discover_stopped(self):
  f=self.root/'nerds'/'nerd-saved';f.mkdir(parents=True);(f/'app.yaml').write_text('app: {title: Saved}')
  l=NerdLoader(self.root);self.assertEqual(l.list()[0]['title'],'Saved');self.assertFalse(l.list()[0]['running']);l.remove('nerd-saved',True)
 def test_bounded_import_default(self):
  d=self.loader.review('demo.zip',self.encoded({'app.yaml':'sources: [{id: p, type: python, entry: plugin:search}]','plugin.py':'def search(q,k):return []'}));cfg=self.loader.pending[d['token']][1];self.assertEqual(cfg['sources'][0]['execution'],'bounded');self.assertFalse(cfg['actions']['writes'])

 def test_static_preview_no_execution(self):
  import yaml
  raw=yaml.safe_dump({'app':{'title':'<img src=x onerror=alert(1)>','tagline':'Bundle tagline','examples':['Example question?']},'provider':{'type':'mock'},'sources':[]})
  d=self.loader.review('demo.zip',self.encoded({'app.yaml':raw}));self.assertTrue(d['preview']['static']);self.assertEqual(d['preview']['title'],'<img src=x onerror=alert(1)>');self.assertEqual(d['preview']['examples'],['Example question?']);self.assertEqual(self.loader.list(),[])

 def test_benign_dotfiles_skipped(self):
  d=self.loader.review('demo.zip',self.encoded({'Nerd/app.yaml':'{}','Nerd/.gitignore':'data/','Nerd/.github/workflows/test.yml':'{}','Nerd/.DS_Store':'x','Nerd/__MACOSX/._doc':'x'}))
  self.assertEqual(d['preview']['files'],['app.yaml'])
 def test_secrets_in_ignored_metadata_still_rejected(self):
  for name in ['.env.local','.env.example','.ssh/id_rsa','.aws/config','.pypirc','.github/.env','__MACOSX/.env','credentials.json']:
   with self.subTest(name=name),self.assertRaisesRegex(ValueError,'Private file.*'+name.replace('.','\\.')):
    self.loader.review('d.zip',self.encoded({'app.yaml':'{}',name:'secret'}))
 def test_unknown_dotfile_named(self):
  with self.assertRaisesRegex(ValueError,'Unsupported hidden file: .private'):
   self.loader.review('d.zip',self.encoded({'app.yaml':'{}','.private':'x'}))
 def test_source_archive_explained(self):
  with self.assertRaisesRegex(ValueError,'Chatify source ZIP, not a Nerd bundle'):
   self.loader.review('source.zip',self.encoded({'chatify/.gitignore':'x','chatify/pyproject.toml':'x','chatify/chatify/__init__.py':'x','chatify/chatify/accounts.py':'x'}))
 def test_article_response_has_routing_hint_without_import(self):
  with self.assertRaisesRegex(ValueError,'Match a real response'):
   self.loader.review('response.json',base64.b64encode(b'{"articles": [{"title":"Fixture"}]}').decode())

import os
from chatify import nerdload
class HostedNerdLoadTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.old=nerdload.GALLERY_CHILDREN;self.registry={};nerdload.GALLERY_CHILDREN=self.registry
  self.addCleanup(setattr,nerdload,'GALLERY_CHILDREN',self.old)
  self.loader=NerdLoader(self.root);self.addCleanup(self.loader.close)
 def bundle_cfg(self,provider='mock'):
  cfg=schema.validate({'app':{'title':'Guest App'},'provider':{'type':provider,'model':'gpt-4o-mini','api_key_env':'OPENAI_API_KEY'} if provider!='mock' else {'type':'mock'},'sources':[]});cfg['_dir']=str(self.root)
  return bundle(cfg)
 def test_hosted_load_registers_slug_relative_url_and_owner(self):
  data,_=self.bundle_cfg();d=self.loader.review('nerd.zip',base64.b64encode(data).decode())
  self.assertTrue(d['hosted']);self.assertTrue(any('Hosted workspace' in w for w in d['warnings']))
  r=self.loader.load(d['token'],owner='visitor:'+'a'*32)
  slug=r['url'].strip('/');self.assertRegex(slug,r'^nerd-[A-Za-z0-9_-]+$');self.assertTrue(r['hosted'])
  self.assertEqual(self.registry[slug]['owner'],'visitor:'+'a'*32);self.assertIsInstance(self.registry[slug]['port'],int)
  row=self.loader.list(owner='visitor:'+'a'*32)[0];self.assertTrue(row['hosted']);self.assertEqual(row['slug'],slug)
 def test_hosted_child_gets_no_host_key_env(self):
  os.environ['OPENAI_API_KEY']='sk-host-fixture-key'
  self.addCleanup(os.environ.pop,'OPENAI_API_KEY')
  data,_=self.bundle_cfg(provider='openai');d=self.loader.review('nerd.zip',base64.b64encode(data).decode())
  r=self.loader.load(d['token'],owner='visitor:'+'a'*32)
  pid=self.loader.workspaces[r['url'].strip('/')]['process'].pid
  env=open('/proc/%d/environ'%pid,'rb').read().decode('utf-8','replace')
  self.assertNotIn('sk-host-fixture-key',env)
  try:
   with open('/proc/%d/status'%pid) as fh:rss=int([l for l in fh if l.startswith('VmRSS')][0].split()[1])
   print('HOSTED_CHILD_RSS_KB=%d'%rss)
  except IndexError:pass
 def test_desktop_child_keeps_declared_env(self):
  nerdload.GALLERY_CHILDREN=None
  os.environ['OPENAI_API_KEY']='sk-desktop-fixture-key'
  self.addCleanup(os.environ.pop,'OPENAI_API_KEY')
  data,_=self.bundle_cfg(provider='openai');d=self.loader.review('nerd.zip',base64.b64encode(data).decode())
  self.assertFalse(d['hosted'])
  r=self.loader.load(d['token']);self.assertTrue(r['url'].startswith('http://127.0.0.1:'))
  pid=self.loader.workspaces[r['workspace'].rsplit('/',1)[-1]]['process'].pid
  env=open('/proc/%d/environ'%pid,'rb').read().decode('utf-8','replace')
  self.assertIn('sk-desktop-fixture-key',env)
 def test_owner_scoping_and_unregister(self):
  data,_=self.bundle_cfg();d=self.loader.review('nerd.zip',base64.b64encode(data).decode())
  r=self.loader.load(d['token'],owner='visitor:'+'a'*32);slug=r['url'].strip('/')
  self.assertEqual(self.loader.list(owner='visitor:'+'b'*32),[])
  with self.assertRaises(ValueError):self.loader.stop(slug,owner='visitor:'+'b'*32)
  with self.assertRaises(ValueError):self.loader.remove(slug,True,owner='visitor:'+'b'*32)
  self.assertIn(slug,self.registry)
  self.loader.stop(slug,owner='visitor:'+'a'*32);self.assertNotIn(slug,self.registry)
 def test_hosted_limit_defaults_two_and_review_enforces(self):
  self.assertEqual(nerdload._nerd_limit(),2)
  os.environ['CHATIFY_NERD_LIMIT']='3';self.assertEqual(nerdload._nerd_limit(),3);del os.environ['CHATIFY_NERD_LIMIT']
  data,_=self.bundle_cfg()
  for _ in range(2):
   d=self.loader.review('nerd.zip',base64.b64encode(data).decode());self.loader.load(d['token'],owner='visitor:'+'a'*32)
  with self.assertRaisesRegex(ValueError,'Up to 2 Nerds'):
   self.loader.review('nerd.zip',base64.b64encode(data).decode())
  self.assertEqual(nerdload.GALLERY_CHILDREN and 2,len(self.registry))

class ReadinessBudgetTest(unittest.TestCase):
    def test_readiness_budget_covers_slow_free_hosts(self):
        # The hosted demo boots a child Python on a throttled free instance; a
        # 4-second budget made first launches fail with 'Nerd did not become
        # ready'. Keep the budget generous.
        from chatify import nerdload
        self.assertGreaterEqual(nerdload.READY_POLLS * nerdload.READY_INTERVAL, 30)
class RemoveResilience(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.loader=NerdLoader(self.root);self.addCleanup(self.loader.close)
 def _ws(self):
  self.loader.root.mkdir(parents=True,exist_ok=True);folder=self.loader.root/'nerd-test01';folder.mkdir();(folder/'app.yaml').write_text('app: {id: w}\n')
  self.loader.workspaces['nerd-test01']={'folder':folder,'process':None,'title':'W','url':'x','owner':'local','slug':None,'hosted':False}
  return folder
 def test_remove_retries_transient_file_failure_once(self):
  import shutil
  folder=self._ws();calls=[]
  real=shutil.rmtree
  def flaky(path):calls.append(path)
  def once(path):
   calls.append(path)
   if len(calls)==1:raise OSError('child still releasing files')
   return real(path)
  import chatify.nerdload as m
  orig=shutil.rmtree;shutil.rmtree=once
  try:r=self.loader.remove('nerd-test01',True)
  finally:shutil.rmtree=orig
  self.assertEqual(r,{'removed':True});self.assertEqual(len(calls),2)
  self.assertNotIn('nerd-test01',self.loader.workspaces);self.assertFalse(folder.exists())
 def test_remove_persistent_failure_keeps_entry_and_files(self):
  import shutil
  folder=self._ws()
  def always(path):raise OSError('fs busy')
  orig=shutil.rmtree;shutil.rmtree=always
  try:
   with self.assertRaisesRegex(ValueError,'could not be deleted yet'):self.loader.remove('nerd-test01',True)
  finally:shutil.rmtree=orig
  self.assertIn('nerd-test01',self.loader.workspaces);self.assertTrue((folder/'app.yaml').exists())

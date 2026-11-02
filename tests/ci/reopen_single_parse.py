import importlib.util,pathlib,tempfile,subprocess,os,json,urllib.request,sys
root=pathlib.Path(__file__).resolve().parents[2];spec=importlib.util.spec_from_file_location('suite',root/'tests/ci/browser_suite.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
with tempfile.TemporaryDirectory() as d:
 env=s.base_env();env['PYTHONPATH']=str(root);env['PLAYWRIGHT_MODULE']=os.environ.get('PLAYWRIGHT_MODULE','playwright');env['DRAFT_ID']='b'*32
 with s.fixture('minimal',pathlib.Path(d),env):
  for ident,title in [('b'*32,'Reopen first'),('c'*32,'Reopen second')]:
   body={'id':ident,'yaml':'app: {title: '+title+'}','title':title,'sections':['app']}
   req=urllib.request.Request(env['CHATIFY_TEST_URL']+'/api/settings/build/draft',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
   with urllib.request.urlopen(req,timeout=15) as response:assert response.status==200
  result=subprocess.run(['node',str(root/'tests/ci/reopen_single_parse.cjs')],env=env,timeout=65)
  raise SystemExit(result.returncode)

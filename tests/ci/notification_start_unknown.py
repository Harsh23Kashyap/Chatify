import importlib.util,pathlib,tempfile,subprocess,os
root=pathlib.Path(__file__).resolve().parents[2];spec=importlib.util.spec_from_file_location('suite',root/'tests/ci/browser_suite.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
with tempfile.TemporaryDirectory() as d:
 env=s.base_env();env['PYTHONPATH']=str(root);env['PLAYWRIGHT_MODULE']='/tmp/dennis-ci-matched/node_modules/playwright-core'
 if os.getenv('CANDIDATE'):env['CANDIDATE']='1'
 with s.fixture('minimal',pathlib.Path(d),env):
  raise SystemExit(subprocess.run(['node',str(root/'tests/ci/notification_start_unknown.cjs')],env=env,timeout=65).returncode)

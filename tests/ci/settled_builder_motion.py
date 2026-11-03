"""Settled Build hero motion levels and reduced-motion checks. No provider calls."""
import importlib.util,pathlib,tempfile,subprocess,os
root=pathlib.Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('suite',root/'tests/ci/browser_suite.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
with tempfile.TemporaryDirectory() as d:
 env=s.base_env();env['PYTHONPATH']=str(root);env['PLAYWRIGHT_MODULE']=os.environ.get('PLAYWRIGHT_MODULE','playwright')
 with s.fixture('minimal',pathlib.Path(d),env):
  raise SystemExit(subprocess.run(['node',str(root/'tests/ci/settled_builder_motion.cjs')],env=env,timeout=90).returncode)

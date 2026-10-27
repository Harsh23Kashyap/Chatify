"""Single bounded offline reproduction on the CI OS, not a retry or qualification."""
import pathlib, subprocess, tempfile
import browser_suite as suite
with tempfile.TemporaryDirectory(prefix='disclosure-diagnostic-') as tmp:
    env=suite.base_env()
    env.update(PYTHONPATH=str(suite.ROOT), CI_CASE='settings_disclosure_cue_audit_browser.cjs', CHATIFY_AUDIT_COMBO='320:no-preference')
    with suite.fixture('generic', pathlib.Path(tmp), env):
        subprocess.run(['node',str(pathlib.Path(__file__).with_suffix('.cjs'))],cwd=suite.ROOT,env=env,check=True,timeout=360)

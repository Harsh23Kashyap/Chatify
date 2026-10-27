"""Offline browser regression orchestration. Assertions remain in original tests."""
import argparse, contextlib, itertools, json, os, pathlib, shutil, signal, socket, subprocess, sys, tempfile, time, urllib.request
ROOT = pathlib.Path(__file__).resolve().parents[2]
MANIFEST = pathlib.Path(__file__).with_name('browser_manifest.json')

def load_manifest():
    manifest = json.loads(MANIFEST.read_text())
    actual = {p.name for p in (ROOT/'tests').glob('*.cjs')} | {'tour_browser.py','workspace_drop_browser.py'}
    classified = set(manifest['cases']) | set(manifest['excluded'])
    if actual != classified:
        raise ValueError(f'Unclassified={sorted(actual-classified)} missing={sorted(classified-actual)}')
    return manifest

def variants(name):
    if name in ('wizard_launch_retry_harness.cjs', 'workspace_review_confirm_harness.cjs'):
        scenarios = ('retry-ticket','expired-review','start-wires-url','back-and-return') if name.startswith('wizard') else ('consent-gate','confirm-once','failure-retry','no-zombies')
        return [(s, [s], {}) for s in scenarios]
    if name.startswith(('button_hover_exact_duration_', 'button_hover_transition_', 'button_press_feedback_', 'button_release_inventory_')):
        return [(f'{w}-{m}', [], dict(RELEASE_WIDTH=str(w), RELEASE_MOTION=m, **({'RELEASE_LEVEL':'full'} if name.startswith('button_press') else {}))) for w,m in itertools.product((320,1280),('no-preference','reduce'))]
    if name in ('appearance_scroll_audit_browser.cjs','settings_disclosure_cue_audit_browser.cjs'):
        return [(f'{w}-{m}', [], {'CHATIFY_AUDIT_COMBO':f'{w}:{m}'}) for w,m in itertools.product((320,1280),('no-preference','reduce'))]
    if name == 'advanced_all_sections_group_motion_browser.cjs':
        return [(f'{w}-{m}', [], {'AUDIT_WIDTH':str(w),'AUDIT_REDUCE':m}) for w,m in itertools.product((320,1280),('no-preference','reduce'))]
    if name in ('dynamic_button_hover_inventory_browser.cjs','picker_source_hover_inventory_browser.cjs'):
        return [(m, [], {'HOVER_MOTION':m}) for m in ('no-preference','reduce')]
    return [('default', [], {})]

def base_env():
    # Deliberately do not forward account/service credentials to fixture/test children.
    allowed = ('PATH','HOME','LANG','LC_ALL','DISPLAY','XAUTHORITY','TMPDIR','PLAYWRIGHT_MODULE','PYTHONPATH','PYTHONUNBUFFERED')
    return {k:os.environ[k] for k in allowed if k in os.environ}

@contextlib.contextmanager
def fixture(kind, folder, env):
    app = folder/'app'; app.mkdir()
    fixed = 8190 if env.get('CI_CASE')=='pickers_browser.cjs' else 8142 if kind=='mounted' else None
    with socket.socket() as probe:
        probe.bind(('127.0.0.1',fixed or 0));port=probe.getsockname()[1]
    if kind == 'strict':
        command = [sys.executable,str(ROOT/'tests/strict_ui_fixture.py')]
    else:
        source = ROOT/'tests/fixtures/builder-trip.yaml' if kind=='trip' else ROOT/'apps/minimal/app.yaml'
        shutil.copyfile(source,app/'app.yaml')
        shutil.copytree(ROOT/'apps/minimal/docs',app/'docs')
        if kind == 'brand':
            import yaml
            cfg=yaml.safe_load((app/'app.yaml').read_text());cfg['provider']={'type':'mock','model':'fixture'}
            (app/'app.yaml').write_text(yaml.safe_dump(cfg))
            command=[sys.executable,str(ROOT/'tests/builder_brand_retry_fixture_server.py')]
            env.update(CHATIFY_FIXTURE_APP=str(app/'app.yaml'),CHATIFY_FIXTURE_PORT=str(port))
        else:
            command=[sys.executable,'-m','chatify','run',str(app/'app.yaml'),'--host','127.0.0.1','--port',str(port),'--no-browser']
    env['CHATIFY_TEST_URL']=f'http://127.0.0.1:{port}'
    env['CHATIFY_URL']=env['CHATIFY_TEST_URL']
    with (folder/'server.log').open('w') as log:
        proc=subprocess.Popen(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        try:
            for _ in range(200):
                if proc.poll() is not None:raise RuntimeError('Fixture exited before ready')
                try:
                    with urllib.request.urlopen(env['CHATIFY_TEST_URL']+'/api/health',timeout=.5) as response:
                        if response.status==200:break
                except OSError:time.sleep(.1)
            else:raise RuntimeError('Fixture not ready within20s')
            if proc.poll() is not None:raise RuntimeError('Fixture exited at readiness')
            yield
        finally:
            with contextlib.suppress(ProcessLookupError):os.killpg(proc.pid,signal.SIGTERM)
            try:proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                with contextlib.suppress(ProcessLookupError):os.killpg(proc.pid,signal.SIGKILL)
                proc.wait()

def run_case(name, kind, variant, args, extra, output):
    started=time.monotonic(); status='FAIL'; code=1
    with tempfile.TemporaryDirectory(prefix='chatify-ci-') as tmp:
        folder=pathlib.Path(tmp);env=base_env();env.update(extra)
        env.update(PYTHONPATH=str(ROOT),CHATIFY_FIXTURE_YAML=str(ROOT/'tests/fixtures/builder-trip.yaml'),CHATIFY_TEST_OUTPUT=str(folder),CI_CASE=name)
        command=([sys.executable] if name.endswith('.py') else ['node'])+[str(ROOT/'tests'/name)]+args
        if name.startswith('settings_native_browser_zoom_'):command=['xvfb-run','-a']+command
        manager=fixture(kind,folder,env) if kind not in ('node','self') else contextlib.nullcontext()
        logpath=output/(name+'.'+variant+'.log')
        try:
            with manager, logpath.open('w') as log:
                proc=subprocess.Popen(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                try:code=proc.wait(timeout=360)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid,signal.SIGKILL);proc.wait();code=124;log.write('\nCI_TIMEOUT360s\n')
                finally:
                    with contextlib.suppress(ProcessLookupError):os.killpg(proc.pid,signal.SIGKILL)
            status='PASS' if code==0 else 'FAIL'
        except Exception as exc:
            with logpath.open('a') as log:log.write(f'CI_HARNESS_ERROR {type(exc).__name__}: {exc}\n')
        print(f'CASE {name} {variant} {status} exit={code} seconds={time.monotonic()-started:.1f}',flush=True)
        # Only offline fixture test output, never server metadata or directory exports.
        print(logpath.read_text(),flush=True)
    return status

def main():
    p=argparse.ArgumentParser();p.add_argument('--shard',type=int,default=0);p.add_argument('--shards',type=int,default=12);p.add_argument('--list',action='store_true');p.add_argument('--case');a=p.parse_args()
    if not 0<=a.shard<a.shards:p.error('invalid shard')
    manifest=load_manifest();cases=sorted(manifest['cases'])
    selected=[n for i,n in enumerate(cases) if i%a.shards==a.shard] if not a.case else [a.case]
    if a.list:print(json.dumps({'total_scripts':len(cases),'selected':selected,'excluded':manifest['excluded']},indent=2));return
    output=pathlib.Path(tempfile.mkdtemp(prefix='chatify-ci-logs-'));pathlib.Path('/downloads').mkdir(exist_ok=True)
    rows=[]
    for name in selected:
        for variant,args,env in variants(name):rows.append((name,variant,run_case(name,manifest['cases'][name],variant,args,env,output)))
    print(json.dumps({'scripts':len(selected),'executions':len(rows),'passed':sum(r[2]=='PASS' for r in rows),'failed':sum(r[2]!='PASS' for r in rows)},sort_keys=True),flush=True)
    if any(r[2]!='PASS' for r in rows):raise SystemExit(1)
if __name__=='__main__':main()

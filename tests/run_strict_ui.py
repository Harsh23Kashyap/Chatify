"""Run strict UI cases on a fresh fixture per test. Requires Chrome + Playwright.
PLAYWRIGHT_MODULE may point to a installed Playwright package. Screenshots and
JSON evidence are written under CUSTOMCHAT_TEST_OUTPUT (default /tmp).
"""
import os,subprocess,sys,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CASES=['sidebar_profile_browser','chat-lifecycle','reading-persistence','topic-temp','answer-delete-topic','local-actions','question-nav','branch-review','stream-buttons','regen-buttons','undo-view-route','multi-topic-cancel','topic-export','deleted-chat-topic','unicode-export']
def main():
 env=os.environ.copy();env.setdefault('CUSTOMCHAT_TEST_URL','http://127.0.0.1:8145');env.setdefault('CUSTOMCHAT_TEST_OUTPUT','/tmp');Path(env['CUSTOMCHAT_TEST_OUTPUT']).mkdir(parents=True,exist_ok=True)
 for name in CASES:
  server=subprocess.Popen([sys.executable,str(ROOT/'tests/strict_ui_fixture.py')],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  try:
   for _ in range(50):
    if server.poll() is not None:raise RuntimeError(server.stderr.read().decode())
    try:urllib.request.urlopen(env['CUSTOMCHAT_TEST_URL']+'/api/chats',timeout=1).close();break
    except OSError:time.sleep(.1)
   else:raise RuntimeError('Fixture startup timed out')
   subprocess.run(['node',str(ROOT/'tests'/(name+'.cjs'))],env=env,check=True,cwd=ROOT)
   print('PASS '+name,flush=True)
  finally:server.terminate();server.wait(timeout=5)
if __name__=='__main__':main()

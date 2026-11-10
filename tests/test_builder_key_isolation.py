"""Hosted launches cannot bundle parent saved keys; desktop keeps local behavior."""
import json,yaml,unittest
from pathlib import Path
from unittest.mock import patch
import test_appbuilder_http
from chatify import keybundle,portable
class KeyIsolation(test_appbuilder_http.BuilderHTTP):
 def test_hosted_launch_bundle_excludes_saved_host_keys(self):
  self._assert_launch_keys(True)
 def test_local_launch_retains_local_key_transport(self):
  self._assert_launch_keys(False)
 def _assert_launch_keys(self,hosted):
  path=Path(self.cfg['_dir'])/'app.yaml';path.write_text(yaml.safe_dump({k:self.cfg[k] for k in __import__('chatify.schema',fromlist=['DEFAULTS']).DEFAULTS}));self.cfg['_path']=str(path)
  captured={};loader=self.engine.nerd_loader
  real_review=loader.review
  def review(name,data):
   r=real_review(name,data);captured['imported_keys']=loader.pending[r['token']][3];return r
  with patch('chatify.workspace_default.choose'),patch('chatify.nerdload._hosted',return_value=hosted),patch.object(keybundle,'export_keys',return_value={'openai':'fixture-only-not-real'}) as exported,patch.object(loader,'review',side_effect=review),patch.object(loader,'load',return_value={'url':'http://127.0.0.1:9999','workspace':str(Path(self.tmp.name)/'nerd-fixture'),'title':'Key fixture'}):
   plan=self.call(self.clients[0],'/api/settings/build/review',{'yaml':'app: {title: Key fixture}\nauth: {mode: none}','sections':['app','auth']})
   saved=self.call(self.clients[0],'/api/settings/build/save',{'ticket':plan['ticket'],'confirmed':True})
   result=self.call(self.clients[0],'/api/settings/build/launch',{'ticket':saved['launch_ticket']})
  if hosted:exported.assert_not_called();self.assertEqual(captured['imported_keys'],{})
  else:exported.assert_called_once();self.assertEqual(captured['imported_keys'],{'openai':'fixture-only-not-real'})
  self.assertNotIn('fixture-only-not-real',json.dumps(result))
 def test_restore_uses_same_hosted_key_gate(self):
  import ast
  tree=ast.parse((Path(__file__).parents[1]/'chatify/server.py').read_text())
  launches=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='bundle' and any(k.arg=='include_docs' for k in n.keywords)]
  self.assertEqual(len(launches),2)
  for call in launches:
   kw={k.arg:ast.unparse(k.value) for k in call.keywords};self.assertEqual(kw['include_keys'],kw['include_docs']);self.assertEqual(kw['include_keys'],'not nerdloadmod._hosted()')

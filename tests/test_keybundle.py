import unittest,tempfile,yaml,json,base64,zipfile,io,os
from pathlib import Path
from customchat import secrets,schema,keybundle,portable
from customchat.nerdload import NerdLoader
class Keys(unittest.TestCase):
 def test_import_values_not_in_review_or_app_file(self):
  with tempfile.TemporaryDirectory() as folder:
   loader=NerdLoader(folder);secret='fixture-private-value-not-real';raw={'app':{'title':'Key fixture'},'provider':{'type':'mock','api_key':secret},'api_keys':{'openai':'fixture-model-key','claude':''}}
   try:
    r=loader.review('fixture.yaml',base64.b64encode(yaml.safe_dump(raw).encode()).decode());self.assertEqual(r['imported_key_count'],2);self.assertNotIn(secret,json.dumps(r));item=loader.pending[r['token']];self.assertNotIn(secret,item[0]['app.yaml'].decode());result=loader.load(r['token']);root=Path(result['workspace']);self.assertEqual(secrets.SecretStore(str(root/'data')).get('mock'),secret);self.assertEqual(os.stat(root/'data/secrets.json').st_mode&0o777,0o600);self.assertNotIn(secret,(root/'app.yaml').read_text())
   finally:loader.close()
 def test_export_opt_in_only(self):
  with tempfile.TemporaryDirectory() as folder:
   old=secrets.STORE;secrets.STORE=secrets.SecretStore(folder);secrets.STORE.set('openai','fixture-export-key')
   try:
    cfg=schema.validate({});cfg['_dir']=folder
    plain,_=portable.bundle(cfg);private,_=portable.bundle(cfg,include_keys=True)
    with zipfile.ZipFile(io.BytesIO(plain)) as z:self.assertNotIn(b'fixture-export-key',z.read('app.yaml'))
    with zipfile.ZipFile(io.BytesIO(private)) as z:self.assertIn(b'fixture-export-key',z.read('app.yaml'))
   finally:secrets.STORE=old

 def test_header_environment_transport_maps_to_bound_http_key(self):
  from customchat import source_credentials
  raw={'sources':[{'id':'private-api','type':'http','url':'https://example.invalid/items','header_env':{'Authorization':'FIXTURE_API'}}],'api_keys':{'env:FIXTURE_API':'fixture-header-key'}}
  clean,keys=keybundle.extract(raw);name=source_credentials.name('private-api','FIXTURE_API','https://example.invalid/items')
  self.assertEqual(keys,{name:'fixture-header-key'});self.assertNotIn('api_keys',clean)
 def test_import_key_validation(self):
  for raw in ({'api_keys':[]},{'api_keys':{'unknown':'fixture'}},{'api_keys':{'openai':'space is forbidden'}},{'api_keys':{'openai':22}}):
   with self.subTest(raw=raw),self.assertRaises(ValueError):keybundle.extract(raw)

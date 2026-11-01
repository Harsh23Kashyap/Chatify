import os,unittest
from unittest.mock import patch
from chatify.generators import _helper_environment,test_code as run_code

def test_only_literal_declared_keys_forwarded():
 with patch.dict(os.environ,{'TEST_SOURCE_KEY':'private','UNRELATED_SECRET':'not-forwarded'}):
  env=_helper_environment('import os\ndef search(query, limit=6):\n return os.environ.get("TEST_SOURCE_KEY")\n')
  assert env['TEST_SOURCE_KEY']=='private'
  assert 'UNRELATED_SECRET' not in env

def test_dynamic_names_not_forwarded():
 with patch.dict(os.environ,{'UNRELATED_SECRET':'not-forwarded'}):
  env=_helper_environment('import os\ndef search(query, limit=6):\n return os.getenv(query)\n')
  assert 'UNRELATED_SECRET' not in env

def test_keyed_helper_can_test_without_echoing_key():
 code='import os\ndef search(query, limit=6):\n # timeout guard\n try:\n  key=os.getenv("TEST_SOURCE_KEY")\n except Exception:\n  key=None\n return [{"title":"ready","text":"configured" if key else "missing","url":"https://example.com","year":None}]\n'
 with patch.dict(os.environ,{'TEST_SOURCE_KEY':'private-key-not-output'}):
  result=run_code('search',code,'test')
 assert result['ok']
 assert result['items'][0]['text']=='configured'
 assert 'private-key-not-output' not in str(result)

class SavedNativeKeys(unittest.TestCase):
 def test_declared_brave_key_uses_private_native_store(self):
  from chatify import secrets
  import tempfile
  with tempfile.TemporaryDirectory() as folder:
   store=secrets.SecretStore(folder);store.set('search:brave','synthetic-not-real');store.set('openai','unrelated-not-real')
   with patch.object(secrets,'STORE',store),patch.dict(os.environ,{},clear=True):
    env=_helper_environment('import os\ndef search(query, limit=6):\n return os.environ.get("BRAVE_API_KEY", "")\n')
   self.assertEqual(env['BRAVE_API_KEY'],'synthetic-not-real');self.assertNotIn('OPENAI_API_KEY',env);self.assertNotIn('openai',env)
 def test_undeclared_saved_key_not_injected(self):
  from chatify import secrets
  import tempfile
  with tempfile.TemporaryDirectory() as folder:
   store=secrets.SecretStore(folder);store.set('search:brave','synthetic-not-real')
   with patch.object(secrets,'STORE',store),patch.dict(os.environ,{},clear=True):env=_helper_environment('def search(query, limit=6):\n return []\n')
   self.assertNotIn('BRAVE_API_KEY',env)

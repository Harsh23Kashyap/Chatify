"""New URL imports retain explicit origin, without inferring old upload origins."""
import tempfile,unittest,os,io
from unittest.mock import patch
from email.message import Message
from chatify import fetch,schema
from chatify.pipeline import Engine
from chatify.store import Store

class UrlUploadProvenance(unittest.TestCase):
 def test_uploaded_origin_survives_body_chunk_without_header(self):
  s=Store(':memory:');s.add_upload('a','Episode notes','Navigation intro.\n\n'+('Mozambique negotiation implementation details. '*40),source_url='https://www.makingpeacevisible.org/neha-sanghrajka')
  e=Engine(schema.validate({'sources':[]}),s);rows=e._uploads_evidence('a','Mozambique negotiation',1)
  self.assertTrue(rows);self.assertEqual(rows[0]['url'],'https://www.makingpeacevisible.org/neha-sanghrajka');self.assertNotIn('https://',rows[0]['text'])
 def test_legacy_upload_and_url_in_text_not_inferred(self):
  s=Store(':memory:');s.add_upload('a','legacy','Mozambique https://example.org/not-an-origin');self.assertFalse(s.uploads('a')[0].get('source_url'))
  r=Engine(schema.validate({'sources':[]}),s)._uploads_evidence('a','Mozambique',1)[0];self.assertEqual(r['url'],'')
 def test_origin_persists_restart_and_is_owner_scoped(self):
  with tempfile.TemporaryDirectory()as tmp:
   path=os.path.join(tmp,'state.db');s=Store(path);s.add_upload('a','note','Mozambique peace details',source_url='https://example.org/note');s=Store(path)
   self.assertEqual(s.uploads('a')[0]['source_url'],'https://example.org/note');self.assertEqual(s.uploads('b'),[])
 def test_delete_cleans_origin(self):
  s=Store(':memory:');uid=s.add_upload('a','note','Mozambique',source_url='https://example.org/note');s.delete_upload('b',uid);self.assertTrue(s.uploads('a'));s.delete_upload('a',uid);self.assertEqual(s.uploads('a'),[]);self.assertEqual(s.q('SELECT * FROM upload_origins'),[])
 def test_final_redirect_origin_and_legacy_load_contract(self):
  class Reply(io.BytesIO):
   def __init__(self):
    super().__init__(b'<html><title>Notes</title><p>Mozambique peace.</p></html>');self.headers=Message();self.headers['Content-Type']='text/html; charset=utf-8'
  class Opener:
   def open(self,request,timeout):return Reply()
  with patch('chatify.fetch.check_public'):
   self.assertEqual(fetch.load('https://example.org/notes',opener=Opener()),('Notes','Mozambique peace.'))
   self.assertEqual(fetch.load('https://example.org/notes',opener=Opener(),with_origin=True),('Notes','Mozambique peace.','https://example.org/notes'))
 def test_reject_nonweb_origins_before_storage(self):
  s=Store(':memory:')
  for url in ['javascript:alert(1)','file:///tmp/a','https://user:password@example.org/']:
   with self.subTest(url=url),self.assertRaises(ValueError):s.add_upload('a','note','Mozambique',source_url=url)
  self.assertEqual(s.uploads('a'),[])
 def test_origin_failure_rolls_back_upload(self):
  import sqlite3
  s=Store(':memory:');s.q("CREATE TRIGGER fail_origin BEFORE INSERT ON upload_origins BEGIN SELECT RAISE(ABORT,'injected origin failure'); END",write=True)
  with self.assertRaises(sqlite3.IntegrityError):s.add_upload('a','note','Mozambique',source_url='https://example.org/note')
  self.assertEqual(s.uploads('a'),[])
 def test_delete_failure_rolls_back_origin_removal(self):
  import sqlite3
  s=Store(':memory:');uid=s.add_upload('a','note','Mozambique',source_url='https://example.org/note');s.q("CREATE TRIGGER fail_upload_delete BEFORE DELETE ON uploads BEGIN SELECT RAISE(ABORT,'injected delete failure'); END",write=True)
  with self.assertRaises(sqlite3.IntegrityError):s.delete_upload('a',uid)
  self.assertEqual(s.uploads('a')[0]['source_url'],'https://example.org/note')
 def test_old_database_and_direct_five_column_insert_compatible(self):
  import sqlite3
  with tempfile.TemporaryDirectory()as tmp:
   path=os.path.join(tmp,'legacy.db');c=sqlite3.connect(path);c.execute('CREATE TABLE uploads(id TEXT PRIMARY KEY, owner TEXT, name TEXT, text TEXT, created REAL)');c.execute('INSERT INTO uploads VALUES(?,?,?,?,?)',('legacy','a','old','Mozambique',1));c.commit();c.close();s=Store(path)
   self.assertEqual(s.uploads('a')[0]['id'],'legacy');self.assertIsNone(s.uploads('a')[0]['source_url']);s.add_upload('a','new','Mozambique',source_url='https://example.org/note');self.assertEqual(len(s.uploads('a')),2)
 def test_mysql_origin_column_not_truncated_to_190(self):
  from chatify.mysqlstore import ddl
  self.assertIn('source_url LONGTEXT',ddl('CREATE TABLE upload_origins(upload TEXT PRIMARY KEY, source_url TEXT)'))
 def test_redirect_records_final_url_and_rechecks_each_hop(self):
  import urllib.error
  class Reply(io.BytesIO):
   def __init__(self):
    super().__init__(b'Peace episode notes');self.headers=Message();self.headers['Content-Type']='text/plain'
  class Opener:
   def open(self,request,timeout):
    if request.full_url.endswith('/start'):raise urllib.error.HTTPError(request.full_url,302,'redirect',{'Location':'/final'},None)
    return Reply()
  with patch('chatify.fetch.check_public')as check:
   self.assertEqual(fetch.load('https://example.org/start',opener=Opener(),with_origin=True)[2],'https://example.org/final');self.assertEqual([c.args[0]for c in check.call_args_list],['https://example.org/start','https://example.org/final'])

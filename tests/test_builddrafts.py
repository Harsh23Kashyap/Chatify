import tempfile,unittest,os
from customchat.builddrafts import BuildDrafts
class Drafts(unittest.TestCase):
 def test_restart_owner_isolation_and_no_apply(self):
  with tempfile.TemporaryDirectory() as d:
   store=BuildDrafts(d);x=store.put('alice','app: {title: Garden}\n','Garden');again=BuildDrafts(d)
   self.assertEqual(again.get('alice',x['id'])['title'],'Garden');self.assertEqual(len(again.list('alice')),1);self.assertEqual(again.list('bob'),[]);self.assertRaises(ValueError,again.get,'bob',x['id']);self.assertFalse(os.path.exists(d+'/app.yaml'));self.assertRaises(ValueError,again.get,'alice','../secret')
 def test_key_fields_scrubbed(self):
  with tempfile.TemporaryDirectory() as d:
   x=BuildDrafts(d).put('owner','provider: {type: mock, api_key_env: SOME_KEY}\n');self.assertNotIn('SOME_KEY',x['yaml'])

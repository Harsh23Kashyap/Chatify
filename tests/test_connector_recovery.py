import unittest
from chatify.connectors.recovery import recover_evidence
class RecoveryTests(unittest.TestCase):
 def test_json_string(self):
  r=recover_evidence('{"results":[{"title":"Study","abstract":"Relevant findings","url":"https://example.org"}]}','test')
  self.assertEqual(r[0]['text'],'Relevant findings');self.assertEqual(r[0]['source'],'test')
 def test_text(self):
  self.assertEqual(recover_evidence('Useful source reply','test')[0]['title'],'Source reply')
 def test_shape(self):
  r=recover_evidence([{'title':'x','text':{'a':1}},None,{'title':'empty'}],'test')
  self.assertEqual(len(r),1);self.assertIn('"a": 1',r[0]['text'])
 def test_error_not_evidence(self):
  with self.assertRaises(ValueError):recover_evidence({'error':'private credential error'},'test')
 def test_bound(self):
  self.assertEqual(len(recover_evidence(['data']*100,'test',2)),2)
 def test_no_execution(self):
  self.assertIn('__import__',recover_evidence('__import__("os").system("false")','test')[0]['text'])

class HelperResultRecovery(unittest.TestCase):
 def test_plain_string_preserved(self):
  from unittest.mock import patch
  from types import SimpleNamespace
  from chatify.generators import test_code
  with patch('chatify.generators.review_code',return_value=(True,[])),patch('subprocess.run',return_value=SimpleNamespace(stdout='@@RESULT@@"A useful source reply"',stderr='')):
   r=test_code('search','def search(query,limit=6):return "A useful source reply"','question')
  self.assertTrue(r['recovered']);self.assertTrue(r['ok']);self.assertEqual(r['items'][0]['text'],'A useful source reply')
 def test_error_object_not_evidence(self):
  from unittest.mock import patch
  from types import SimpleNamespace
  from chatify.generators import test_code
  with patch('chatify.generators.review_code',return_value=(True,[])),patch('subprocess.run',return_value=SimpleNamespace(stdout='@@RESULT@@{"error":"request failed"}',stderr='')):
   r=test_code('search','def search(query,limit=6):return {}','question')
  self.assertFalse(r['ok']);self.assertFalse(r['recovered'])

import unittest
from customchat.connectors.recovery import recover_evidence
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

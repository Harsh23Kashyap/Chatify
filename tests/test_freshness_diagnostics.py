import tempfile,unittest
from pathlib import Path
from customchat.connectors.local_files import LocalFiles
class FreshnessDiagnostics(unittest.TestCase):
 def test_change_counts_and_retained_last_index(self):
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder);(p/'a.txt').write_text('First sample words')
   conn=LocalFiles({'id':'docs','label':'Documents','path':folder});self.assertEqual(conn.status()['last_check']['added'],1);self.assertGreater(conn.status()['last_check']['passages_added'],0)
   conn.refresh(force=True);self.assertEqual(conn.status()['last_check']['state'],'unchanged')
   (p/'a.txt').write_text('Updated sample words');(p/'b.txt').write_text('Second sample words');conn.refresh(force=True)
   self.assertGreater(conn.status()['last_check']['passages_removed'],0);self.assertEqual(conn.status()['last_check']['changed'],1);self.assertEqual(conn.status()['last_check']['added'],1)
   (p/'a.txt').unlink();conn.refresh(force=True);self.assertEqual(conn.status()['last_check']['removed'],1)
   before=conn.status()['chunks'];(p/'b.txt').unlink();p.rmdir()
   with self.assertRaises(OSError):conn.refresh(force=True)
   self.assertEqual(conn.status()['chunks'],before);self.assertIn('folder',conn.status()['error']);self.assertEqual(conn.status()['last_check']['state'],'failed')

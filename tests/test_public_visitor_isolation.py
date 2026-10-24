"""Public demos must not share one visitor's chats and drafts with every other visitor."""
import pathlib,unittest
from chatify.schema import validate
class PublicVisitorIsolation(unittest.TestCase):
 def test_schema_allows_server_public_flag(self):
  cfg=validate({'server':{'public':True}})
  self.assertTrue(cfg['server']['public'])
 def test_no_auth_public_mode_uses_a_per_browser_owner(self):
  root=pathlib.Path(__file__).resolve().parents[1]
  server=(root/'chatify/server.py').read_text()
  self.assertIn('def _cookie_named(self, name):',server)
  self.assertIn('if cfg.get("server", {}).get("public") or os.environ.get("CHATIFY_GALLERY_REGISTER"):',server)
  self.assertIn('return "visitor:" + visitor',server)
  self.assertIn('cc_visitor=%s; Path=/; HttpOnly; SameSite=Strict',server)
 def test_hosted_demo_opts_in(self):
  root=pathlib.Path(__file__).resolve().parents[1]
  hosted=(root/'apps/hosted/app.yaml').read_text()
  self.assertIn('public: true',hosted)

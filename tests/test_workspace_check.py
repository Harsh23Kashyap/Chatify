import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import chatify.server as server
from chatify import nerdload as nerdloadmod

class WorkspaceBase(unittest.TestCase):
    def setUp(self):
        self.saved = nerdloadmod.GALLERY_CHILDREN
    def tearDown(self):
        nerdloadmod.GALLERY_CHILDREN = self.saved
    def test_local_url_passthrough(self):
        nerdloadmod.GALLERY_CHILDREN = None
        self.assertEqual(server._workspace_base({'url': 'http://127.0.0.1:9001/'}), 'http://127.0.0.1:9001')
    def test_hosted_path_resolves_child_port(self):
        # Regression for 2026-10-24 live failure: hosted workspace url '/nerd-x/'
        # reached urllib as a relative path -> "unknown url type" on Check evidence.
        nerdloadmod.GALLERY_CHILDREN = {'nerd-x': {'port': 9123, 'owner': 'local'}}
        self.assertEqual(server._workspace_base({'url': '/nerd-x/'}), 'http://127.0.0.1:9123')
    def test_hosted_path_plain_port_entry(self):
        nerdloadmod.GALLERY_CHILDREN = {'nerd-x': 9124}
        self.assertEqual(server._workspace_base({'url': '/nerd-x/'}), 'http://127.0.0.1:9124')
    def test_missing_child_registration_is_honest(self):
        nerdloadmod.GALLERY_CHILDREN = {}
        with self.assertRaisesRegex(ValueError, 'not reachable yet'):
            server._workspace_base({'url': '/nerd-gone/'})

if __name__ == '__main__':
    unittest.main()

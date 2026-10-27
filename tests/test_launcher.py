import tempfile,unittest,socket
from pathlib import Path
from chatify.launcher import workspace,pick_port
from chatify.schema import ConfigError,load
class LauncherTests(unittest.TestCase):
    def test_packaged_template_and_rerun(self):
        with tempfile.TemporaryDirectory() as tmp:
            app=workspace(Path(tmp)/'demo');self.assertEqual(load(str(app))['provider']['type'],'mock')
            self.assertTrue((app.parent/'docs/about.md').is_file())
            app.write_text('custom user content');self.assertEqual(workspace(app.parent).read_text(),'custom user content')
    def test_existing_directory_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ConfigError):workspace(tmp)
    def test_busy_port_fallback(self):
        with socket.socket() as s:
            s.bind(('127.0.0.1',0));port=s.getsockname()[1]
            if port<=65515:self.assertNotEqual(pick_port(port),port)
    def test_bad_port(self):
        with self.assertRaises(ConfigError):pick_port(65535)
if __name__=='__main__':unittest.main()

class InstalledStartTests(unittest.TestCase):
    def test_locked_start_sets_flag_before_server_import(self):
        import inspect
        from chatify.launcher import start
        source=inspect.getsource(start)
        self.assertLess(source.index('if lock_config:'),source.index('from .server import serve'))

class PortProbeFlags(unittest.TestCase):
    def test_probe_uses_actual_http_server_reuse_flags(self):
        from unittest.mock import patch,MagicMock,call
        from chatify.server import LocalHTTPServer
        self.assertTrue(LocalHTTPServer.allow_reuse_address)
        self.assertFalse(getattr(LocalHTTPServer,'allow_reuse_port',False))
        sock=MagicMock()
        with patch('chatify.launcher.socket.socket') as factory:
            factory.return_value.__enter__.return_value=sock
            self.assertEqual(pick_port(8080),8080)
        self.assertEqual(sock.method_calls[:2],[call.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1),call.bind(('127.0.0.1',8080))])
    def test_denied_reuse_bind_skips_candidate(self):
        from unittest.mock import patch,MagicMock
        first=MagicMock();first.bind.side_effect=PermissionError(10013,'reserved')
        second=MagicMock()
        with patch('chatify.launcher.socket.socket') as factory:
            factory.side_effect=[MagicMock(__enter__=MagicMock(return_value=first)),MagicMock(__enter__=MagicMock(return_value=second))]
            self.assertEqual(pick_port(8080),8081)
        first.setsockopt.assert_called_once_with(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        second.bind.assert_called_once_with(('127.0.0.1',8081))

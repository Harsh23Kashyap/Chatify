import unittest
from unittest.mock import patch
from chatify.cli import _main
from chatify import schema
class RunBrowserTests(unittest.TestCase):
 def run_cli(self, args):
  cfg=dict(schema.DEFAULTS);cfg['server']={'host':'127.0.0.1','port':8081}
  with patch('chatify.schema.load',return_value=cfg), patch('chatify.server.serve') as serve, patch('chatify.launcher.open_when_ready') as op:
   _main(['run','sample.yaml']+args)
   return serve.call_args,op.call_args
 def test_default_opens_configured_url(self):
  serve,op=self.run_cli([]);self.assertEqual(op.args,('http://127.0.0.1:8081',))
 def test_no_browser(self):
  serve,op=self.run_cli(['--no-browser']);self.assertIsNone(op)
 def test_wildcard_uses_loopback_browser(self):
  serve,op=self.run_cli(['--host','0.0.0.0','--port','8082']);self.assertEqual(op.args,('http://127.0.0.1:8082',))

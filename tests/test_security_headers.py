"""Baseline security headers on every response, and HEAD answers like GET without a body."""
import http.client, json, threading, unittest
from http.server import ThreadingHTTPServer
from chatify import schema
from chatify.pipeline import Engine
from chatify.store import Store
from chatify.server import make_handler, SECURITY_HEADERS


class SecurityHeaders(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = __import__("tempfile").TemporaryDirectory()
        cfg = schema.validate({"auth": {"mode": "none"}, "sources": []})
        cfg["_dir"] = cls.tmp.name
        cls.engine = Engine(cfg, Store(":memory:"))
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(cfg, cls.engine))
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.port = cls.server.server_port

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.engine.nerd_loader.close(); cls.tmp.cleanup()

    def request(self, method, path):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        conn.request(method, path)
        resp = conn.getresponse()
        body = resp.read()
        headers = {k.lower(): v for k, v in resp.getheaders()}
        conn.close()
        return resp.status, headers, body

    def test_every_response_carries_the_baseline(self):
        for path in ("/", "/app.js", "/api/health"):
            with self.subTest(path=path):
                status, headers, _ = self.request("GET", path)
                self.assertEqual(status, 200)
                for name, value in SECURITY_HEADERS.items():
                    self.assertEqual(headers.get(name.lower()), value, name)
                self.assertEqual(headers.get("x-content-type-options"), "nosniff")

    def test_csp_blocks_foreign_scripts_embeds_and_framing(self):
        _, headers, _ = self.request("GET", "/")
        csp = headers["content-security-policy"]
        for clause in ("default-src 'self'", "object-src 'none'", "base-uri 'none'",
                       "form-action 'self'", "frame-ancestors 'self'", "connect-src 'self'"):
            self.assertIn(clause, csp)
        # the settings preview iframe and inline bootstrap scripts must keep working
        self.assertIn("frame-src 'self'", csp)
        self.assertIn("'unsafe-inline'", csp)
        self.assertIn("https://fonts.googleapis.com", csp)
        self.assertIn("https://fonts.gstatic.com", csp)

    def test_permissions_policy_keeps_voice_input(self):
        _, headers, _ = self.request("GET", "/")
        self.assertIn("microphone=(self)", headers["permissions-policy"])

    def test_head_matches_get_headers_without_body(self):
        get_status, get_headers, get_body = self.request("GET", "/")
        head_status, head_headers, head_body = self.request("HEAD", "/")
        self.assertEqual(get_status, 200)
        self.assertEqual(head_status, 200)  # was 501 before HEAD was routed
        self.assertEqual(head_body, b"")
        self.assertGreater(len(get_body), 0)
        self.assertEqual(head_headers.get("content-length"), str(len(get_body)))
        self.assertEqual(head_headers.get("content-type"), get_headers.get("content-type"))
        for name in SECURITY_HEADERS:
            self.assertEqual(head_headers.get(name.lower()), get_headers.get(name.lower()))

    def test_head_on_json_and_static(self):
        for path in ("/app.js", "/api/health"):
            with self.subTest(path=path):
                status, _, body = self.request("HEAD", path)
                self.assertEqual(status, 200)
                self.assertEqual(body, b"")


if __name__ == "__main__":
    unittest.main()

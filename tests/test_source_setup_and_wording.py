import unittest, tempfile, threading, json, urllib.request, os
from http.server import ThreadingHTTPServer
from unittest.mock import patch
from chatify import schema
from chatify.store import Store
from chatify.pipeline import Engine
from chatify.server import make_handler
from chatify.connectors import make_connector
from chatify.connectors.open_sources import SetupRequired


class OpenAlexSetupRequired(unittest.TestCase):
    def test_missing_key_raises_named_setup_error(self):
        conn = make_connector({"id": "oa", "label": "OpenAlex", "type": "openalex"})
        with patch("chatify.secrets.saved", return_value=""), patch.dict(os.environ, {}, clear=True):
            os.environ.pop("OPENALEX_API_KEY", None)
            with self.assertRaises(SetupRequired) as ctx:
                conn.search("minimum wage", 3)
        self.assertIn("API key", str(ctx.exception))

    def test_engine_surfaces_setup_message_in_source_errors(self):
        cfg = schema.load("apps/minimal/app.yaml")
        cfg["sources"] = [{"id": "oa", "label": "OpenAlex", "type": "openalex"}]
        engine = Engine(cfg, Store(":memory:"))
        with patch("chatify.secrets.saved", return_value=""):
            os.environ.pop("OPENALEX_API_KEY", None)
            found, errors = engine.retrieve("effects of minimum wage increases on employment", ["oa"])
        self.assertEqual(found, [])
        self.assertIn("oa", errors)
        self.assertIn("API key", errors["oa"], "the answer UI must name the missing setup, not a bare exception type")


class EffectiveWording(unittest.TestCase):
    def test_config_and_exports_follow_theme_wording_overrides(self):
        with tempfile.TemporaryDirectory() as folder:
            cfg = schema.validate({"storage": {"path": os.path.join(folder, "s.db")}})
            cfg["_dir"] = folder
            store = Store(cfg["storage"]["path"])
            engine = Engine(cfg, store)
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(cfg, engine))
            threading.Thread(target=server.serve_forever, daemon=True).start()
            root = "http://127.0.0.1:" + str(server.server_port)

            def api(path, body=None, raw=False):
                req = urllib.request.Request(root + path, data=None if body is None else json.dumps(body).encode(), headers={"Content-Type": "application/json"})
                r = urllib.request.urlopen(req)
                return r.read() if raw else json.load(r)

            try:
                base = api("/api/config")["app"]
                theme = api("/api/theme")["theme"]
                theme["txt_title"] = "Effective Title"
                theme["txt_tagline"] = "Effective tagline for readers."
                api("/api/theme", {"theme": theme})
                shown = api("/api/config")["app"]
                self.assertEqual(shown["title"], "Effective Title")
                self.assertEqual(shown["tagline"], "Effective tagline for readers.")
                self.assertNotEqual(cfg["app"]["title"], "Effective Title", "api/config must copy, never mutate cfg")
                chat = store.new_chat("local", "t")
                turn = store.add_turn(chat, "", "Q?", "Q?", "A [1]", [{"n": 1, "title": "T", "text": "x", "url": "u", "source": "s", "id": "e1"}], [], "standard")
                md = api("/api/answer-markdown?turn=" + turn, raw=True).decode()
                self.assertIn("Effective tagline for readers.", md)
                pdf = api("/api/pdf?turn=" + turn, raw=True)
                self.assertTrue(pdf.startswith(b"%PDF"))
            finally:
                server.shutdown()
                server.server_close()


if __name__ == "__main__":
    unittest.main()

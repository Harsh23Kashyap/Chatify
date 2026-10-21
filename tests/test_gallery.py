import io, json, os, subprocess, sys, tempfile, time, unittest, urllib.request, urllib.error

ROOT = os.path.join(os.path.dirname(__file__), "..")


def _write_gallery(base):
    for slug, title in [("alpha", "Alpha App"), ("beta", "Beta App")]:
        d = os.path.join(base, slug)
        os.makedirs(os.path.join(d, "docs"))
        io.open(os.path.join(d, "docs", "a.md"), "w").write("Docs about %s." % title)
        io.open(os.path.join(d, "app.yaml"), "w").write(
            "app: {id: %s, title: %s, tagline: The %s test app}\n"
            "provider: {type: mock}\n"
            "sources: [{id: docs, type: local_files, label: Docs, path: docs}]\n"
            "storage: {path: data/chatify.db}\n" % (slug, title, title))
    io.open(os.path.join(base, "gallery.yaml"), "w").write(
        "gallery:\n"
        "  title: Test Gallery\n"
        "  tagline: Smoke test\n"
        "  provider: {type: openai, model: gpt-4o-mini, api_key_env: OPENAI_API_KEY}\n"
        "  budget: {daily_questions: 300, daily_model_calls: 500}\n"
        "  apps:\n"
        "    - {dir: alpha, slug: alpha, icon: chat, tags: [TagOne, TagTwo]}\n"
        "    - {dir: beta, slug: beta}\n")


class GalleryConfig(unittest.TestCase):
    def test_detection(self):
        from chatify import gallery
        self.assertTrue(gallery.is_gallery(os.path.join(ROOT, "apps", "gallery.yaml")))
        self.assertFalse(gallery.is_gallery(os.path.join(ROOT, "apps", "minimal", "app.yaml")))

    def test_guardrails_forced(self):
        from chatify import gallery
        g = gallery.load(os.path.join(ROOT, "apps", "gallery.yaml"))
        for app in g["apps"]:
            cfg = app["cfg"]
            self.assertEqual(cfg["provider"]["type"], "openai")           # host key, server-side only
            self.assertEqual(cfg["provider"]["api_key_env"], "OPENAI_API_KEY")
            self.assertTrue(cfg["server"]["public"])                      # per-visitor isolation
            self.assertEqual(cfg["app"]["theme"], "light")                # consistent look; no dark settings pages
            self.assertEqual(cfg["budget"]["user_daily_questions"], 0)    # shared pool stays off
            self.assertEqual(cfg["budget"]["daily_questions"], 300)
            self.assertEqual(cfg["budget"]["daily_model_calls"], 500)

    def test_slugs_validated(self):
        from chatify import gallery, schema
        base = tempfile.mkdtemp()
        d = os.path.join(base, "alpha"); os.makedirs(os.path.join(d, "docs"))
        io.open(os.path.join(d, "docs", "a.md"), "w").write("x")
        io.open(os.path.join(d, "app.yaml"), "w").write("app: {id: alpha, title: A}\nprovider: {type: mock}\nsources: [{id: docs, type: local_files, label: D, path: docs}]\n")
        io.open(os.path.join(base, "gallery.yaml"), "w").write("gallery:\n  apps:\n    - {dir: alpha, slug: API}\n")
        self.assertRaises(schema.ConfigError, gallery.load, os.path.join(base, "gallery.yaml"))


class GalleryServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = tempfile.mkdtemp()
        _write_gallery(cls.base)
        cls.port = 8937
        cls.proc = subprocess.Popen(
            [sys.executable, "-m", "chatify", "run", os.path.join(cls.base, "gallery.yaml"), "--port", str(cls.port), "--no-browser"],
            cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for _ in range(40):
            time.sleep(0.25)
            if cls.proc.poll() is not None:
                raise AssertionError("gallery server died: " + cls.proc.stdout.read()[-1500:])
            try:
                urllib.request.urlopen("http://127.0.0.1:%d/api/health" % cls.port, timeout=2)
                break
            except Exception:
                continue
        else:
            raise AssertionError("gallery server never came up")

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate(); cls.proc.wait()

    def get(self, path, accept="text/html"):
        req = urllib.request.Request("http://127.0.0.1:%d%s" % (self.port, path), headers={"Accept": accept})
        try:
            r = urllib.request.urlopen(req, timeout=10)
            return r.status, r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", "replace")

    def test_gallery_page_lists_apps(self):
        s, b = self.get("/")
        self.assertEqual(s, 200)
        self.assertEqual(b.count('class="g-card"'), 2)
        self.assertIn("Alpha App", b); self.assertIn("Beta App", b)
        self.assertIn('class="g-ico"', b)                    # card icons render
        self.assertIn("TagOne", b)                           # card tags render
        self.assertIn('class="g-info"', b)                   # trust tile fills the grid
        self.assertIn('href="/alpha/"', b)
        self.assertIn("navflow", b)  # page transitions on the gallery too

    def test_app_home_is_rewritten(self):
        s, b = self.get("/alpha/")
        self.assertEqual(s, 200)
        self.assertIn("CC_APP_BASE", b)                 # fetch/XHR/EventSource shim
        self.assertIn('"/alpha"', b)
        self.assertIn('href="/alpha/', b)               # nav stays inside the app
        self.assertIn(">Gallery</a>", b)                # way back to the gallery

    def test_each_app_answers_on_its_own_endpoint(self):
        s, b = self.get("/alpha/api/health", "application/json")
        self.assertEqual((s, json.loads(b)["ok"]), (200, True))
        s, b = self.get("/beta/api/health", "application/json")
        self.assertEqual((s, json.loads(b)["ok"]), (200, True))
        s, b = self.get("/api/health", "application/json")
        self.assertEqual(json.loads(b)["apps"], ["alpha", "beta"])

    def test_statics_work_under_the_prefix(self):
        s, b = self.get("/alpha/style.css")
        self.assertEqual(s, 200)
        self.assertGreater(len(b), 1000)

    def test_unknown_paths_get_the_designed_404(self):
        s, b = self.get("/nope/")
        self.assertEqual((s, "Page not found" in b), (404, True))
        s, b = self.get("/alpha/nope.html")
        self.assertEqual((s, "Page not found" in b), (404, True))

    def test_mock_chat_streams_through_the_proxy(self):
        req = urllib.request.Request("http://127.0.0.1:%d/alpha/api/ask" % self.port,
                                     data=json.dumps({"question": "hi", "chat": ""}).encode(),
                                     headers={"Content-Type": "application/json"})
        r = urllib.request.urlopen(req, timeout=15)
        self.assertEqual(r.status, 200)
        self.assertIn('"chat"', r.read().decode("utf-8", "replace")[:200])


if __name__ == "__main__": unittest.main()

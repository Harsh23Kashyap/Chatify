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
        "    - {dir: beta, slug: beta}\n"
        "    - {slug: ext, url: 'https://example.com/ext', title: External App, tagline: Links out, icon: planet, accent: '#8c4f9e'}\n")


class GalleryConfig(unittest.TestCase):
    def test_detection(self):
        from chatify import gallery
        self.assertTrue(gallery.is_gallery(os.path.join(ROOT, "apps", "gallery.yaml")))
        self.assertFalse(gallery.is_gallery(os.path.join(ROOT, "apps", "minimal", "app.yaml")))

    def test_guardrails_forced(self):
        from chatify import gallery
        g = gallery.load(os.path.join(ROOT, "apps", "gallery.yaml"))
        for app in g["apps"]:
            if "cfg" not in app:
                continue  # redirect entries carry no hosted config
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
        self.assertEqual(b.count('class="g-card"'), 3)
        self.assertIn("Alpha App", b); self.assertIn("Beta App", b)
        self.assertIn('href="https://example.com/ext"', b)   # redirect app card links out
        self.assertIn('class="g-ico"', b)                    # card icons render
        self.assertIn("TagOne", b)                           # card tags render
        self.assertIn('class="g-info"', b)                   # trust tile fills the grid
        self.assertIn('href="/alpha/"', b)
        self.assertIn("navflow", b)  # page transitions on the gallery too

    def test_redirect_apps_link_out_and_redirect(self):
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *a, **k):
                return None
        opener = urllib.request.build_opener(NoRedirect)
        for path in ("/ext", "/ext/anything/deeper"):
            try:
                opener.open("http://127.0.0.1:%d%s" % (self.port, path), timeout=5)
                self.fail("expected a redirect for " + path)
            except urllib.error.HTTPError as e:
                self.assertIn(e.code, (301, 302))
                self.assertEqual(e.headers["Location"], "https://example.com/ext")
        s3, health = self.get("/api/health", accept="application/json")
        self.assertEqual(s3, 200)
        h = json.loads(health)
        self.assertEqual(sorted(h["apps"]), ["alpha", "beta"])   # hosted copies only
        self.assertEqual(h["redirects"], ["ext"])

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


import base64

GUEST_YAML = ("app: {id: guestapp, title: Guest Workspace, tagline: Built by a visitor}\n"
              "provider: {type: openai, model: gpt-4o-mini, api_key_env: OPENAI_API_KEY}\n"
              "sources: []\n")


class GalleryWorkspaceHandoff(unittest.TestCase):
    """A visitor's built app loads as a same-origin proxied workspace, gated to its creator."""
    @classmethod
    def setUpClass(cls):
        cls.base = tempfile.mkdtemp()
        _write_gallery(cls.base)
        cls.port = 8941
        env = dict(os.environ, OPENAI_API_KEY="sk-gallery-host-fixture")
        cls.proc = subprocess.Popen(
            [sys.executable, "-m", "chatify", "run", os.path.join(cls.base, "gallery.yaml"), "--port", str(cls.port), "--no-browser"],
            cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
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

    def req(self, method, path, cookie=None, body=None, accept="text/html"):
        headers = {"Accept": accept}
        if cookie is not None:
            headers["Cookie"] = "cc_visitor=" + cookie
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        r = urllib.request.Request("http://127.0.0.1:%d%s" % (self.port, path), data=data, headers=headers, method=method)
        try:
            resp = urllib.request.urlopen(r, timeout=30)
            return resp.status, resp.read().decode("utf-8", "replace"), dict(resp.headers)
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", "replace"), dict(e.headers)

    def test_full_hosted_handoff_flow(self):
        A, B = "a" * 32, "b" * 32
        # issuance: first HTML visit sets a 128-bit HttpOnly visitor cookie
        s, body, h = self.req("GET", "/alpha/")
        self.assertEqual(s, 200)
        setc = h.get("Set-Cookie", "")
        self.assertIn("cc_visitor=", setc); self.assertIn("HttpOnly", setc); self.assertIn("SameSite=Strict", setc)
        issued = setc.split("cc_visitor=", 1)[1].split(";", 1)[0]
        self.assertRegex(issued, r"^[0-9a-f]{32}$")

        # review: owner A gets a hosted review with the honest warning
        bundle64 = base64.b64encode(GUEST_YAML.encode()).decode()
        s, body, _ = self.req("POST", "/alpha/api/nerds/review", cookie=A, body={"name": "app.yaml", "data": bundle64}, accept="application/json")
        self.assertEqual(s, 200, body[:300])
        review = json.loads(body)
        self.assertTrue(review["hosted"])
        self.assertTrue(any("Hosted workspace" in w for w in review["warnings"]))
        self.assertIn("OPENAI_API_KEY", review["required_env"])

        # load: same-origin relative URL, slug registered
        s, body, _ = self.req("POST", "/alpha/api/nerds/load", cookie=A, body={"token": review["token"]}, accept="application/json")
        self.assertEqual(s, 200, body[:300])
        loaded = json.loads(body)
        self.assertTrue(loaded["hosted"])
        url = loaded["url"]
        self.assertRegex(url, r"^/nerd-[A-Za-z0-9_-]+/$")

        # gate: every route class is protected - no cookie, wrong cookie, malformed cookie
        for probe in (url, url + "settings.html", url + "api/health", url + "api/provider/status"):
            for bad in (None, B, "not-a-real-cookie", "a" * 31):
                s, body, _ = self.req("GET", probe, cookie=bad, accept="application/json")
                self.assertEqual(s, 403, probe + " with cookie " + str(bad))
                self.assertIn("Private workspace", body)
        # gate: owner reaches HTML, API and settings
        s, body, _ = self.req("GET", url, cookie=A)
        self.assertEqual(s, 200)
        self.assertIn("CC_APP_BASE", body)
        self.assertIn('"/' + url.strip("/") + '"', body)
        s, body, _ = self.req("GET", url + "api/health", cookie=A, accept="application/json")
        self.assertEqual((s, json.loads(body)["ok"]), (200, True))
        s, body, _ = self.req("GET", url + "settings.html", cookie=A)
        self.assertEqual(s, 200)

        # host key is NOT inherited by the guest workspace, and the state is surfaced honestly
        s, body, _ = self.req("GET", "/alpha/api/provider/status", cookie=A, accept="application/json")
        self.assertTrue(json.loads(body)["keys"]["openai"]["has"])   # gallery child sees host env
        s, body, _ = self.req("GET", url + "api/provider/status", cookie=A, accept="application/json")
        self.assertEqual(s, 200)
        guest_key = json.loads(body)["keys"]["openai"]
        self.assertFalse(guest_key["has"])                           # guest workspace does not inherit it
        self.assertTrue(guest_key["needed"])                         # and says a key is still needed

        # traversal does not escape into another app
        s, body, _ = self.req("GET", url + "../alpha/", cookie=A)
        self.assertNotEqual(s, 200)

        # owner-scoped management: B cannot see, stop or remove A's workspace
        s, body, _ = self.req("GET", "/alpha/api/nerds", cookie=B, accept="application/json")
        self.assertEqual(json.loads(body)["workspaces"], [])
        s, body, _ = self.req("GET", "/alpha/api/nerds", cookie=A, accept="application/json")
        rows = json.loads(body)["workspaces"]
        self.assertEqual(len(rows), 1); self.assertTrue(rows[0]["hosted"]); self.assertTrue(rows[0]["running"])
        wid = rows[0]["id"]
        s, body, _ = self.req("POST", "/alpha/api/nerds/stop", cookie=B, body={"id": wid}, accept="application/json")
        self.assertNotEqual(s, 200)
        s, body, _ = self.req("POST", "/alpha/api/nerds/remove", cookie=B, body={"id": wid, "confirmed": True}, accept="application/json")
        self.assertNotEqual(s, 200)
        # still running after B's attempts
        s, body, _ = self.req("GET", url + "api/health", cookie=A, accept="application/json")
        self.assertEqual(s, 200)
        # owner stops it; slug unregisters and later requests fail honestly (503 waking page)
        s, body, _ = self.req("POST", "/alpha/api/nerds/stop", cookie=A, body={"id": wid}, accept="application/json")
        self.assertEqual(s, 200, body[:300])
        time.sleep(1.5)
        s, body, _ = self.req("GET", url + "api/health", cookie=A, accept="application/json")
        self.assertNotEqual(s, 200)

    def test_python_connector_stays_off_without_explicit_allow(self):
        A = "c" * 32
        files = {"app.yaml": "app: {id: codeapp, title: Code App}\nprovider: {type: mock}\nsources: [{id: p, type: python, entry: plugin:search}]\n",
                 "plugin.py": "def search(q, k):\n    return []\n"}
        out = io.BytesIO()
        import zipfile
        with zipfile.ZipFile(out, "w") as z:
            for n, d in files.items():
                z.writestr(n, d)
        bundle64 = base64.b64encode(out.getvalue()).decode()
        s, body, _ = self.req("POST", "/alpha/api/nerds/review", cookie=A, body={"name": "codeapp.zip", "data": bundle64}, accept="application/json")
        self.assertEqual(s, 200, body[:300])
        token = json.loads(body)["token"]
        s, body, _ = self.req("POST", "/alpha/api/nerds/load", cookie=A, body={"token": token}, accept="application/json")
        self.assertNotEqual(s, 200)
        self.assertIn("allow", json.loads(body)["error"].lower())

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


BUILD_YAML_SECTIONS = None  # filled in test from schema + appbuilder


class GalleryBuilderUseThisApp(unittest.TestCase):
    """The builder's own Use-this-app route: review -> save -> launch -> hosted workspace."""
    @classmethod
    def setUpClass(cls):
        cls.base = tempfile.mkdtemp()
        _write_gallery(cls.base)
        cls.port = 8943
        env = dict(os.environ, OPENAI_API_KEY="sk-builder-host-fixture")
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

    def req(self, method, path, cookie, body=None):
        h = {"Accept": "application/json", "Cookie": "cc_visitor=" + cookie}
        data = None
        if body is not None:
            data = json.dumps(body).encode(); h["Content-Type"] = "application/json"
        r = urllib.request.Request("http://127.0.0.1:%d%s" % (self.port, path), data=data, headers=h, method=method)
        try:
            resp = urllib.request.urlopen(r, timeout=30)
            return resp.status, resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", "replace")

    def test_save_then_launch_carries_everything_but_keys(self):
        import yaml
        from chatify import schema
        A = "d5e6f7a8" * 4
        draft = schema.validate({
            "app": {"id": "spacefacts", "title": "Space Facts", "tagline": "Planets and missions", "examples": ["How far is Mars?"]},
            "provider": {"type": "openai", "model": "gpt-4o-mini", "api_key_env": "OPENAI_API_KEY"},
            "sources": [
                {"id": "docs", "type": "local_files", "label": "Mission notes", "path": "docs"},
                {"id": "launches", "type": "http_json", "label": "Launch API", "url": "https://api.example.com/launches", "api_key_env": "LAUNCH_API_KEY"},
            ],
        })
        draft["appearance"] = {"mode": "light", "bubble": "flat"}
        draft["pipeline_prompts"] = {"text": {s: "CUSTOM PROMPT %s" % s for s in
            ["question_check", "standalone", "queries", "relevance", "answer", "faithfulness", "revise", "followups", "summary"]}, "on": {}}
        draft["helper_drafts"] = {"search": {"brief": "Find rows", "code": "def search(query, items):\n    return []\n"}}
        sections = sorted(schema.DEFAULTS) + ["appearance", "pipeline_prompts", "helper_drafts"]
        yaml_text = yaml.safe_dump(draft, sort_keys=False)

        s, b = self.req("POST", "/alpha/api/settings/build/review", A, {"yaml": yaml_text, "sections": sections})
        self.assertEqual(s, 200, b[:300])
        ticket = json.loads(b)["ticket"]
        s, b = self.req("POST", "/alpha/api/settings/build/save", A, {"ticket": ticket, "confirmed": True})
        self.assertEqual(s, 200, b[:300])
        launch_ticket = json.loads(b)["launch_ticket"]
        # Multi-visitor isolation: the served app file must be untouched; the
        # reviewed build lands in the visitor's own build app dir.
        saved_cfg = yaml.safe_load(io.open(os.path.join(self.base, "alpha", "app.yaml")))
        self.assertEqual(saved_cfg["app"]["title"], "Alpha App")
        self.assertFalse(os.path.exists(os.path.join(self.base, "alpha", "data", "theme.json")))
        import glob
        built = glob.glob(os.path.join(self.base, "alpha", "data", "build-apps", "*", "*", "app.yaml"))
        self.assertEqual(len(built), 1)
        bdir = os.path.dirname(built[0])
        saved_cfg = yaml.safe_load(io.open(built[0]))
        self.assertEqual(saved_cfg["app"]["title"], "Space Facts")
        self.assertEqual(json.load(io.open(os.path.join(bdir, "data", "theme.json")))["bubble"], "flat")
        self.assertEqual(json.load(io.open(os.path.join(bdir, "data", "prompts.json")))["text"]["answer"], "CUSTOM PROMPT answer")

        s, b = self.req("POST", "/alpha/api/settings/build/launch", A, {"ticket": launch_ticket})
        self.assertEqual(s, 200, b[:300])
        launched = json.loads(b)
        self.assertTrue(launched["hosted"])
        url = launched["url"]
        self.assertRegex(url, r"^/nerd-[A-Za-z0-9_-]+/$")
        self.assertEqual(launched["title"], "Space Facts")
        wsdir = launched["workspace"]

        s, b = self.req("GET", url, A)
        self.assertEqual(s, 200); self.assertIn("Space Facts", b); self.assertIn("CC_APP_BASE", b)
        s, b = self.req("GET", url, "e6f7a8b9" * 4)
        self.assertEqual(s, 403)

        ws_cfg = yaml.safe_load(io.open(os.path.join(wsdir, "app.yaml")))
        srcs = {x["id"]: x for x in ws_cfg["sources"]}
        self.assertEqual(srcs["launches"]["url"], "https://api.example.com/launches")
        self.assertEqual(srcs["launches"]["api_key_env"], "LAUNCH_API_KEY")
        self.assertEqual(ws_cfg["app"]["examples"], ["How far is Mars?"])
        self.assertEqual(json.load(io.open(os.path.join(wsdir, "data", "theme.json")))["bubble"], "flat")
        self.assertEqual(json.load(io.open(os.path.join(wsdir, "data", "prompts.json")))["text"]["revise"], "CUSTOM PROMPT revise")
        self.assertIn("search", json.load(io.open(os.path.join(wsdir, "data", "code-drafts.json"))))
        moved = next(x["path"] for x in ws_cfg["sources"] if x["type"] == "local_files")
        # Hosted launch bundles never copy the SHARED app's documents into a
        # guest workspace (live demo 2026-10-25: guests answered domain
        # questions with the host's seeded guide); the guest's source starts
        # empty and they add their own documents inside the workspace.
        self.assertFalse(os.path.isfile(os.path.join(wsdir, moved, "a.md")))
        leftovers = [f for f in glob.glob(os.path.join(wsdir, moved, "**", "*"), recursive=True) if os.path.isfile(f)]
        self.assertEqual(leftovers, [])

        # Workspace source isolation semantics (live demo 2026-10-25 defect):
        # the SHARED app's own documents never enter a guest workspace, while
        # the visitor's own uploads inside the workspace feed answers, survive
        # reload and appear in exports.
        s, b = self.req("POST", url + "api/uploads", A, {"name": "mission-notes.md", "text": "The Zebra protocol governs quarantine handling for returned samples. Zebra quarantine lasts eleven days."})
        self.assertEqual(s, 200, b[:300])
        s, b = self.req("POST", url + "api/ask", A, {"question": "How long does Zebra quarantine last?"})
        self.assertEqual(s, 200, b[:300])
        ans = json.loads(b)
        self.assertIn("Zebra", ans["answer"])
        self.assertTrue(any(e.get("source") == "uploads" for e in ans["evidence"]))
        # Nothing from the host app's docs/a.md (content "x") leaked into the workspace.
        self.assertFalse(any(e.get("source") == "docs" for e in ans["evidence"]))
        self.assertFalse(any("a.md" in str(e.get("document") or "") for e in ans["evidence"]))
        chat_id = ans["chat"]
        s, b = self.req("GET", url + "api/turns?chat=" + chat_id, A)
        self.assertEqual(s, 200, b[:300]); self.assertIn("Zebra", b)
        s, b = self.req("GET", url + "api/export?chat=" + chat_id, A)
        self.assertEqual(s, 200, b[:300]); self.assertIn("Zebra quarantine lasts eleven days", b)

        s, b = self.req("GET", url + "api/provider/status", A)
        key = json.loads(b)["keys"]["openai"]
        self.assertFalse(key["has"]); self.assertTrue(key["needed"])
        slug = url.strip("/")
        s, b = self.req("POST", "/alpha/api/nerds/stop", A, {"id": slug})
        self.assertEqual(s, 200, str(b)[:150])
        s, b = self.req("POST", "/alpha/api/nerds/remove", A, {"id": slug, "confirmed": True})
        self.assertEqual(s, 200, str(b)[:150])


class GalleryNestedWorkspaceLaunch(unittest.TestCase):
    """A workspace launched from INSIDE a guest workspace still gets a same-origin hosted URL."""
    @classmethod
    def setUpClass(cls):
        cls.base = tempfile.mkdtemp()
        _write_gallery(cls.base)
        cls.port = 8944
        env = dict(os.environ, OPENAI_API_KEY="sk-nested-host-fixture", CHATIFY_NERD_GLOBAL_CAP="2")
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

    def req(self, method, path, cookie, body=None, raw=False):
        h = {"Accept": "application/json", "Cookie": "cc_visitor=" + cookie}
        data = None
        if body is not None:
            data = json.dumps(body).encode(); h["Content-Type"] = "application/json"
        r = urllib.request.Request("http://127.0.0.1:%d%s" % (self.port, path), data=data, headers=h, method=method)
        try:
            resp = urllib.request.urlopen(r, timeout=60)
            out = resp.read().decode("utf-8", "replace")
            return resp.status, (out if raw else json.loads(out))
        except urllib.error.HTTPError as e:
            out = e.read().decode("utf-8", "replace")
            if raw: return e.code, out
            try: return e.code, json.loads(out)
            except ValueError: return e.code, {"error": out[:200]}

    def test_launch_inside_workspace_registers_same_origin(self):
        import base64
        A = "a1b2c3d4" * 4
        minimal = io.open(os.path.join(ROOT, "apps", "minimal", "app.yaml"), "rb").read()
        s, b = self.req("POST", "/alpha/api/nerds/review", A, {"name": "app.yaml", "data": base64.b64encode(minimal).decode()})
        self.assertEqual(s, 200, str(b)[:200])
        self.assertTrue(b["hosted"])
        s, b = self.req("POST", "/alpha/api/nerds/load", A, {"token": b["token"]})
        self.assertEqual(s, 200, str(b)[:200])
        self.assertTrue(b["hosted"])
        w1 = b["url"]
        self.assertRegex(w1, r"^/nerd-[A-Za-z0-9_-]+/$")

        # builder chain INSIDE W1: review -> save -> launch
        yaml_text = "app:\n  id: nested\n  title: Nested App\nprovider:\n  type: openai\n  model: gpt-4o-mini\n  api_key_env: OPENAI_API_KEY\nsources: []\n"
        s, b = self.req("POST", w1 + "api/settings/build/review", A, {"yaml": yaml_text, "sections": ["app", "provider", "sources"]})
        self.assertEqual(s, 200, str(b)[:200])
        s, b = self.req("POST", w1 + "api/settings/build/save", A, {"ticket": b["ticket"], "confirmed": True})
        self.assertEqual(s, 200, str(b)[:200])
        s, b = self.req("POST", w1 + "api/settings/build/launch", A, {"ticket": b["launch_ticket"]})
        self.assertEqual(s, 200, str(b)[:300])
        self.assertTrue(b["hosted"], str(b)[:200])
        w2 = b["url"]
        self.assertRegex(w2, r"^/nerd-[A-Za-z0-9_-]+/$", str(b)[:200])
        self.assertEqual(b["title"], "Nested App")
        self.assertNotEqual(w1, w2)

        # owner opens W2 same-origin; a stranger is denied
        s, body = self.req("GET", w2, A, raw=True)
        self.assertEqual(s, 200); self.assertIn("Nested App", body)
        s, body = self.req("GET", w2, "b2c3d4e5" * 4, raw=True)
        self.assertEqual(s, 403); self.assertIn("Private workspace", body)
        # W2 inherits no host key material
        s, st = self.req("GET", w2 + "api/provider/status", A)
        self.assertEqual(s, 200)
        self.assertFalse(st["keys"]["openai"]["has"])

        # depth guard: W2 cannot launch a third level
        s, b = self.req("POST", w2 + "api/settings/build/review", A, {"yaml": yaml_text, "sections": ["app", "provider", "sources"]})
        self.assertEqual(s, 200, str(b)[:200])
        s, b = self.req("POST", w2 + "api/settings/build/save", A, {"ticket": b["ticket"], "confirmed": True})
        self.assertEqual(s, 200, str(b)[:200])
        s, b = self.req("POST", w2 + "api/settings/build/launch", A, {"ticket": b["launch_ticket"]})
        self.assertEqual(s, 400, str(b)[:200])
        self.assertIn("cannot launch further workspaces", b["error"])

        # a parent cannot stop while its nested workspace runs (no orphans)
        key1 = w1.strip("/")
        s, b = self.req("POST", "/alpha/api/nerds/stop", A, {"id": key1})
        self.assertEqual(s, 400, str(b)[:200])
        self.assertIn("running workspace of its own", b["error"])
        # global cap across nested processes: W1 + W2 = 2, a third import refuses
        s, b = self.req("POST", "/alpha/api/nerds/review", A, {"name": "app.yaml", "data": base64.b64encode(minimal).decode()})
        self.assertEqual(s, 200, str(b)[:200])
        s, b = self.req("POST", "/alpha/api/nerds/load", A, {"token": b["token"]})
        self.assertEqual(s, 400, str(b)[:200])
        self.assertIn("workspace limit", b["error"])
        # cleanup: W2 is managed by W1's own API (the process that spawned it),
        # W1 by the gallery app's; registry forgets both
        key2 = w2.strip("/")
        s, b = self.req("POST", w1 + "api/nerds/stop", A, {"id": key2})
        self.assertEqual(s, 200, str(b)[:150])
        s, b = self.req("POST", w1 + "api/nerds/remove", A, {"id": key2, "confirmed": True})
        self.assertEqual(s, 200, str(b)[:150])
        s, lst = self.req("GET", w1 + "api/nerds", A)
        self.assertEqual(lst["workspaces"], [])
        s, b = self.req("POST", "/alpha/api/nerds/stop", A, {"id": key1})
        self.assertEqual(s, 200, str(b)[:150])
        s, b = self.req("POST", "/alpha/api/nerds/remove", A, {"id": key1, "confirmed": True})
        self.assertEqual(s, 200, str(b)[:150])
        s, body = self.req("GET", w2, A, raw=True)
        self.assertEqual(s, 404)
        s, body = self.req("GET", w1, A, raw=True)
        self.assertEqual(s, 404)
        s, lst = self.req("GET", "/alpha/api/nerds", A)
        self.assertEqual(lst["workspaces"], [])


class GalleryFeaturedBuildCta(unittest.TestCase):
    """The featured card's Build with AI button opens the AI build wizard, never manual settings."""
    @classmethod
    def setUpClass(cls):
        cls.base = tempfile.mkdtemp()
        _write_gallery(cls.base)
        # make alpha the featured build-your-own app
        p = os.path.join(cls.base, "gallery.yaml")
        s = io.open(p).read()
        s = s.replace("{dir: alpha, slug: alpha, icon: chat, tags: [TagOne, TagTwo]}",
                      "{dir: alpha, slug: alpha, icon: chat, tags: [TagOne, TagTwo], featured: true}")
        io.open(p, "w").write(s)
        cls.port = 8945
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

    def get(self, path):
        try:
            r = urllib.request.urlopen("http://127.0.0.1:%d%s" % (self.port, path), timeout=10)
            return r.status, r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", "replace")

    def test_featured_cta_opens_ai_wizard(self):
        s, b = self.get("/")
        self.assertEqual(s, 200)
        self.assertIn('class="g-f-cta" href="/alpha/build.html"', b)
        self.assertNotIn('class="g-f-cta" href="/alpha/settings.html"', b)
        # the wizard is actually reachable through the proxy and is the AI flow
        s, b = self.get("/alpha/build.html")
        self.assertEqual(s, 200)
        self.assertIn("Chatify builds it.", b)
        self.assertIn("buildBrief", b)
        s, b = self.get("/alpha/build.js")
        self.assertEqual(s, 200)
        self.assertIn("launch_ticket", b)

import io, os, re, unittest

W = os.path.join(os.path.dirname(__file__), "..", "chatify", "web")
rd = lambda n: io.open(os.path.join(W, n), encoding="utf-8").read()

PAGES = ["index.html", "settings.html", "about.html", "run-locally.html", "error.html"]


class PageTransitions(unittest.TestCase):
    """Every page change animates: a short exit on the old page, a short rise on the new one,
    and nothing at all for visitors who prefer reduced motion."""

    def test_shared_assets_exist(self):
        css, js = rd("navflow.css"), rd("navflow.js")
        self.assertIn("@keyframes nav-in", css)
        self.assertIn("@keyframes nav-out", css)
        self.assertIn("prefers-reduced-motion:no-preference", css)
        self.assertIn("sessionStorage", js)
        self.assertIn("pageshow", js)  # bfcache restore must undo a half-played exit
        self.assertIn("prefers-reduced-motion", js)
        self.assertIn("catch (e)", js)  # decoration never throws

    def test_every_page_wires_the_transition(self):
        for name in PAGES:
            html = rd(name)
            self.assertIn('href="/navflow.css"', html, name)
            self.assertIn('src="/navflow.js"', html, name)
            # inline pre-paint snippet: without it the entering page would flash visible first
            self.assertIn('sessionStorage.getItem("cc_nav")', html, name)
            self.assertIn('classList.add("nav-in")', html, name)

    def test_transition_is_short_and_gentle(self):
        css = rd("navflow.css")
        for m in re.finditer(r"animation:nav-(?:in|out) ([\d.]+)s", css):
            self.assertLessEqual(float(m.group(1)), 0.3)  # never a long, showy jump

    def test_exit_only_flags_real_page_changes(self):
        js = rd("navflow.js")
        self.assertIn('a.target', js)            # new-tab links untouched
        self.assertIn('hasAttribute("download")', js)
        self.assertIn("url.origin !== location.origin", js)  # external links untouched
        self.assertIn("url.pathname === location.pathname", js)  # same-page/hash untouched


class ErrorPages(unittest.TestCase):
    def test_every_code_has_a_designed_page(self):
        srv = io.open(os.path.join(W, "..", "server.py"), encoding="utf-8").read()
        for code in (401, 403, 404, 413, 429, 500, 503):
            self.assertIn("%d: (" % code, srv, "ERR_PAGES missing %d" % code)

    def test_error_page_is_animated_and_calm(self):
        html = rd("error.html")
        self.assertIn("@keyframes float", html)
        self.assertIn("@keyframes up", html)
        self.assertIn("prefers-reduced-motion:no-preference", html)
        self.assertIn("prefers-reduced-motion:reduce", html)
        for token in ("{{CODE}}", "{{TITLE}}", "{{MSG}}", "{{ART}}"):
            self.assertIn(token, html)


if __name__ == "__main__": unittest.main()

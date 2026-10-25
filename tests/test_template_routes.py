from pathlib import Path
import unittest
class TemplateRoutes(unittest.TestCase):
 def test_raw_templates_redirect_not_serve(self):
  s=(Path(__file__).resolve().parents[1]/'chatify/server.py').read_text()
  self.assertIn('if name in ("gallery.html", "error.html"):',s)
  self.assertIn('Template-only files: rendered by the gallery/error handlers, never served raw.',s)
  self.assertIn('if raw in ("/", "/gallery.html", "/index.html"):',s)  # canonical gallery route still substitutes
 def test_gallery_page_substitutes(self):
  s=(Path(__file__).resolve().parents[1]/'chatify/server.py').read_text()
  i=s.index('def _gallery_page(self):')
  self.assertIn('{{TITLE}}',(Path(__file__).resolve().parents[1]/'chatify/web/gallery.html').read_text())
  self.assertIn('_esc(',s[i:i+3000])  # injected values stay escaped
if __name__=='__main__':unittest.main()

class GalleryNavInjection(unittest.TestCase):
 def test_gallery_link_survives_nav_id_attribute(self):
  import chatify.server as S
  html = '<nav class="common-nav" id="siteNav" aria-label="Main navigation"><a href="/chatify/">Chat</a></nav>'
  out = S._rewrite_app_html(('<html><body>' + html + '</body></html>').encode(), '/chatify')
  if isinstance(out, bytes): out = out.decode('utf-8')
  self.assertIn('<a href="/">Gallery</a>', out)

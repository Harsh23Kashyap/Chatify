import pathlib,unittest
class ThemeContrastSettle(unittest.TestCase):
 def test_contrast_correction_reads_final_colors_not_transition_frames(self):
  root=pathlib.Path(__file__).resolve().parents[1]/'chatify/web'
  js=(root/'theme.js').read_text();css=(root/'style.css').read_text()
  self.assertIn('classList.add("contrast-measuring")',js)
  self.assertIn('classList.remove("contrast-measuring")',js)
  self.assertIn('html.contrast-measuring *',css)
 def test_alpha_backgrounds_and_text_opacity_are_composited(self):
  js=(pathlib.Path(__file__).resolve().parents[1]/'chatify/web/theme.js').read_text()
  self.assertIn('layers.reverse()',js)
  self.assertIn('opacity*=Number(measuredStyle(host).opacity)',js)
  self.assertIn('const cs=getComputedStyle(node);style={color:cs.color,backgroundColor:cs.backgroundColor,opacity:cs.opacity}',js)
  self.assertIn('hex(blend(parseHex(changed),backValues,opacity))',js)
 def test_inline_transition_override_prevents_false_pass_during_reset(self):
  js=(pathlib.Path(__file__).resolve().parents[1]/'chatify/web/theme.js').read_text()
  self.assertIn('node.style.setProperty("transition","none","important")',js)
  self.assertIn('getPropertyPriority("transition")',js)
  self.assertIn('transitions.forEach',js)

 def test_svg_only_controls_and_bundled_icon_fallback(self):
  root=pathlib.Path(__file__).resolve().parents[1]/'chatify/web'
  self.assertIn('node.matches("button,a")&&node.querySelector("svg")',(root/'theme.js').read_text())
  app=(root/'app.js').read_text()
  self.assertIn('const supported=e&&(CCEmoji.assets[e]||CCEmoji.staticAssets[e]',app)
  self.assertIn('b.replaceChildren(supported ?',app)

 def test_contrast_work_is_batched_and_impossible_targets_skip_search(self):
  js=(pathlib.Path(__file__).resolve().parents[1]/'chatify/web/theme.js').read_text()
  self.assertIn('const corrections=[]',js)
  self.assertIn('corrections.forEach',js)
  self.assertIn('if(!possible){changed=CCBrand.shade(color,back,20.9);}',js)

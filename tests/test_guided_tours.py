from pathlib import Path
import unittest
W=Path(__file__).resolve().parents[1]/'chatify/web'
class GuidedTours(unittest.TestCase):
 def test_both_pages_load_shared_guide_and_replay(self):
  for file,button in [('index.html','chatGuide'),('settings.html','configGuide')]:
   s=(W/file).read_text();self.assertIn('/tour.css',s);self.assertIn('/tour.js',s);self.assertIn('id="'+button+'"',s)
 def test_configuration_has_fourteen_steps_and_independent_first_open(self):
  s=(W/'tour.js').read_text();config=s.split('const configSteps=[')[1].split('const chatSteps=')[0]
  self.assertEqual(config.count('{title:'),14);self.assertIn("key:'cc_cfg_tour_v1'",s);self.assertIn("key:'cc_tour'",s)
 def test_skip_keyboard_focus_and_local_only(self):
  s=(W/'tour.js').read_text()
  for text in ["'Skip'","'cancel'","ArrowRight","ArrowLeft","showModal()","before.focus","localStorage.setItem"]:self.assertIn(text,s)
  self.assertIn('/api/guide-seen',s);self.assertNotIn('/api/ask',s)
 def test_motion_and_small_viewport_limits(self):
  css=(W/'tour.css').read_text()
  for text in ['prefers-reduced-motion','100dvh','max-height:540px',':focus-visible']:self.assertIn(text,css)
 def test_preview_does_not_autostart_main_guide(self):
  s=(W/'app.js').read_text();self.assertLess(s.index('if (PREVIEW) { previewMode(); return; }'),s.index('loadSuggestions(); tour();'))
 def test_current_tabs_and_honest_save_scopes(self):
  s=(W/'tour.js').read_text();config=s.split('const configSteps=[')[1].split('const chatSteps=')[0]
  for text in ['Workspace','Answers','Appearance','Maintenance','Type in Find a setting','Save answer settings','appearance changes save automatically','not prompts, sources or keys','does not change your settings']:
   self.assertIn(text,config)
  self.assertNotIn('Configuration, Frontend and App management',config)
  self.assertNotIn('Presets give you ready-made configurations',config)

 def test_quiet_guide_has_no_decorative_scene_or_transform(self):
  s=(W/'tour.js').read_text()
  self.assertNotIn("cc-tour-orb",s)
  self.assertNotIn("✦",s)
  self.assertNotIn("translateY",s)
  self.assertIn("duration:160",s)
  css=(W/'tour.css').read_text()
  self.assertNotIn("@keyframes cc-guide-orb",css)
  self.assertIn("text-transform:none;letter-spacing:normal",css)

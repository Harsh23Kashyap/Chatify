from pathlib import Path
import unittest
R=Path(__file__).resolve().parents[1]
class FeedbackPatch(unittest.TestCase):
 def test_settings_groups_with_helper_loader(self):
  html=(R/'chatify/web/settings.html').read_text();js=(R/'chatify/web/settings.js').read_text()
  self.assertIn('src="/pipeline.js"',html);self.assertIn('src="/codeeditor.js"',html)
  for x in ('Workspace','Answers','Appearance','Maintenance','Sources and APIs','aria-orientation','settings-active-panel','CCSettingsRefreshNavigation'):self.assertIn(x,js)
 def test_real_assets_and_package(self):
  files=list((R/'chatify/web/emoji').glob('*.webp'));self.assertEqual(len(files),17)
  for p in files:
   self.assertIn(b"ANIM",p.read_bytes());self.assertGreater(p.read_bytes().count(b"ANMF"),1)
   self.assertTrue(p.with_suffix('.png').exists())
  self.assertIn('web/emoji/*',(R/'pyproject.toml').read_text())
 def test_preview_and_logo_regressions(self):
  s=(R/'chatify/web/settings.js').read_text()
  self.assertIn('ccPreviewMotion',(Path(__file__).resolve().parents[1]/'chatify/web/appearanceextras.js').read_text())
  for x in ('readAsDataURL','testLog.unshift','detail:message','Suggested local models'):self.assertIn(x,s)
  self.assertNotIn('motion-sample',s)
 def test_disclosures_are_not_height_clipped(self):
  s=(R/'chatify/web/settings.css').read_text()
  self.assertIn('details::details-content{block-size:auto!important',s)
  self.assertIn('#pv{pointer-events:none}',s)
class DraftPaletteGuard(unittest.TestCase):
 def test_degreen_remaps_green_proposals(self):
  import sys
  sys.path.insert(0,str(R))
  from chatify.appbuilder import _degreen
  import colorsys
  draft={'light':{'brand':'#2e7d32','accent':'#7fae3c','bg':'#eef5ec','ink':'#1c3a30','line':'#d5ddce','danger':'#a8493c'},'dark':{'brand':'#4caf50','bg':'#101c17','surface':'#16241d'},'bg_color2':'#7fae3c','pattern_color':'#3e7c4f'}
  out=_degreen({k:(dict(v) if isinstance(v,dict) else v) for k,v in draft.items()})
  vals=list(out['light'].values())+list(out['dark'].values())+[out['bg_color2'],out['pattern_color']]
  for v in vals:
   r,g,b=(int(v[i:i+2],16)/255 for i in (1,3,5))
   h,l,sat=colorsys.rgb_to_hls(r,g,b)
   if sat>=0.18:self.assertFalse(75<=h*360<=170,v+' still green')
 def test_degreen_keeps_neutrals_and_nongreens(self):
  import sys
  sys.path.insert(0,str(R))
  from chatify.appbuilder import _degreen
  keep={'light':{'bg':'#ffffff','ink':'#222222','brand':'#2f5d8a','danger':'#b3261e','muted':'#6b6b6b'}}
  self.assertEqual(_degreen({'light':dict(keep['light'])}),keep)
 def test_user_chosen_green_survives_validation_save_and_import(self):
  import sys
  sys.path.insert(0,str(R))
  from chatify.appbuilder import validate_extras
  green={'brand':'#2e7d32','accent':'#7fae3c','bg':'#eef5ec','surface':'#f4f9f1','ink':'#1c3a30','muted':'#5d6b64','line':'#cfe0cc','sidebar':'#e2efe0','bot':'#eef7ea','you':'#e4f2dc','danger':'#a8493c'}
  out=validate_extras({'appearance':{'mode':'light','light':dict(green)}})
  self.assertEqual(out['appearance']['light'],green)
 def test_local_fallback_palette_is_not_green(self):
  import sys
  sys.path.insert(0,str(R))
  from chatify.buildjobs import BuildJobs
  import colorsys
  filled=BuildJobs()._local_fill({'brief':'garden notes from my allotment','parts':{}},'appearance:colors')
  for v in list(filled['light'].values())+list(filled['dark'].values()):
   r,g,b=(int(v[i:i+2],16)/255 for i in (1,3,5))
   h,l,sat=colorsys.rgb_to_hls(r,g,b)
   if sat>=0.18:self.assertFalse(75<=h*360<=170,v+' fallback still green')
 def test_explicit_green_request_bypasses_recolor(self):
  import sys
  sys.path.insert(0,str(R))
  from chatify.appbuilder import green_requested
  from chatify.buildjobs import BuildJobs
  from chatify import theme
  self.assertTrue(green_requested('a garden app with a green theme'))
  self.assertTrue(green_requested('forest and sage tones please'))
  self.assertFalse(green_requested('a diet assistant'))
  self.assertFalse(green_requested(''))
  self.assertFalse(green_requested(None))
  base={field:theme.DEFAULT_CLEAN()[field] for field in __import__('chatify.buildjobs',fromlist=['LOOK']).LOOK['colors']}
  filled=BuildJobs()._local_fill({'brief':'garden notes with a calm green palette','parts':{}},'appearance:colors')
  self.assertEqual(filled,base)

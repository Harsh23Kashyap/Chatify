import copy, pathlib, tempfile, unittest, yaml
from chatify import gallery, schema, providers
from chatify.budget import Budget, BudgetError
from unittest.mock import patch
from tests.test_gallery import _write_gallery

class GalleryModelOverride(unittest.TestCase):
 def test_only_target_model_changes_and_host_identity_stays(self):
  with tempfile.TemporaryDirectory() as d:
   _write_gallery(d);p=pathlib.Path(d)/'gallery.yaml';raw=yaml.safe_load(p.read_text());before=gallery.load(str(p));raw['gallery']['apps'][0]['model']='gpt-6-luna';p.write_text(yaml.safe_dump(raw));after=gallery.load(str(p))
   expected=copy.deepcopy(before);expected['apps'][0]['cfg']['provider']['model']='gpt-6-luna';self.assertEqual(after,expected)
   self.assertEqual(after['apps'][0]['cfg']['provider']['api_key_env'],'OPENAI_API_KEY');self.assertEqual(after['apps'][1]['cfg']['provider']['model'],'gpt-4o-mini')
 def test_invalid_overrides_fail_before_start(self):
  for model in [None,True,{},[],0,'',' ','x'*201,'gpt\nsecret']:
   with self.subTest(model=model),tempfile.TemporaryDirectory() as d:
    _write_gallery(d);p=pathlib.Path(d)/'gallery.yaml';raw=yaml.safe_load(p.read_text());raw['gallery']['apps'][0]['model']=model;p.write_text(yaml.safe_dump(raw))
    with self.assertRaises(schema.ConfigError):gallery.load(str(p))
 def test_public_paper_trail_model_guard_and_no_private_payload(self):
  g=gallery.load('apps/gallery.yaml');paper=next(a for a in g['apps'] if a['slug']=='paper-trail');cfg=paper['cfg']
  self.assertEqual(cfg['provider']['model'],'gpt-6-luna');self.assertEqual(cfg['budget']['spend_cap_usd'],0);self.assertTrue(cfg['server']['public']);self.assertEqual([s['type'] for s in cfg['sources']],['arxiv','crossref']);self.assertFalse(cfg['prompt']['source_preview_only']);self.assertNotIn('helper_drafts',yaml.safe_load(pathlib.Path('apps/paper-trail/app.yaml').read_text()));self.assertEqual(list(pathlib.Path('apps/paper-trail').iterdir()),[pathlib.Path('apps/paper-trail/app.yaml')])
  for app in g['apps']:
   if app.get('cfg') and app['slug']!='paper-trail':self.assertEqual(app['cfg']['provider']['model'],'gpt-4o-mini')
  pv=providers.OpenAICompatible(cfg)
  with patch.object(pv,'complete',side_effect=AssertionError('paid transport must not run')),patch.object(pv,'stream',side_effect=AssertionError('paid stream must not run')):
   guard=Budget(cfg).wrap(pv)
   with self.assertRaises(BudgetError):guard.complete([])
   with self.assertRaises(BudgetError):list(guard.stream([]))

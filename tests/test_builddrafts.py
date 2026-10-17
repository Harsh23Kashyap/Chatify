import tempfile,unittest,os
from chatify.builddrafts import BuildDrafts
class Drafts(unittest.TestCase):
 def test_restart_owner_isolation_and_no_apply(self):
  with tempfile.TemporaryDirectory() as d:
   store=BuildDrafts(d);x=store.put('alice','app: {title: Garden}\n','Garden');again=BuildDrafts(d)
   self.assertEqual(again.get('alice',x['id'])['title'],'Garden');self.assertEqual(len(again.list('alice')),1);self.assertEqual(again.list('bob'),[]);self.assertRaises(ValueError,again.get,'bob',x['id']);self.assertFalse(os.path.exists(d+'/app.yaml'));self.assertRaises(ValueError,again.get,'alice','../secret')
 def test_key_fields_scrubbed(self):
  with tempfile.TemporaryDirectory() as d:
   x=BuildDrafts(d).put('owner','provider: {type: mock, api_key_env: SOME_KEY}\n');self.assertNotIn('SOME_KEY',x['yaml'])

 def test_section_draft_preserves_scope_and_can_be_reviewed_after_restart(self):
  import yaml
  from pathlib import Path
  from chatify import schema,appbuilder
  with tempfile.TemporaryDirectory() as d:
   cfg=schema.validate({});path=Path(d)/'app.yaml';path.write_text(yaml.safe_dump(cfg));cfg['_dir']=d;cfg['_path']=str(path)
   record=BuildDrafts(d).put('owner','app: {title: Section draft}',sections=['app'])
   restored=BuildDrafts(d).get('owner',record['id'])
   self.assertEqual(set(yaml.safe_load(restored['yaml'])),{'app'})
   plan=appbuilder.review(cfg,restored['yaml'],restored['sections'])
   self.assertEqual(plan['config']['app']['title'],'Section draft')
   self.assertEqual(plan['selected'],['app'])

 def test_selected_section_mismatch_is_rejected_without_retention(self):
  with tempfile.TemporaryDirectory() as d:
   store=BuildDrafts(d)
   for source,selected in [('app: {title: X}',['app','provider']),('app: {title: X}\nprovider: {type: mock}',['app'])]:
    with self.assertRaises(ValueError):store.put('owner',source,sections=selected)
   self.assertEqual(store.list('owner'),[])

 def test_inferred_scope_and_legacy_expanded_record_recovery(self):
  import json,yaml
  from chatify import schema
  with tempfile.TemporaryDirectory() as d:
   store=BuildDrafts(d);record=store.put('owner','app: {title: Inferred}')
   self.assertEqual(record['sections'],['app'])
   legacy=dict(record);legacy['yaml']=yaml.safe_dump(schema.validate({'app':{'title':'Legacy'}}));legacy['sections']=['app']
   store._path('owner',record['id']).write_text(json.dumps(legacy))
   recovered=store.get('owner',record['id'])
   self.assertEqual(set(yaml.safe_load(recovered['yaml'])),{'app'})
   self.assertEqual(recovered['sections'],['app'])
   legacy['yaml']='app: {title: Without scope}';legacy['sections']=None
   store._path('owner',record['id']).write_text(json.dumps(legacy))
   self.assertEqual(store.get('owner',record['id'])['sections'],['app'])

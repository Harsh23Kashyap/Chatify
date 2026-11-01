"""Keep raw scope separate from normalized defaults without reparsing payloads."""
import tempfile
import unittest
from unittest.mock import patch
import yaml
from chatify import appbuilder
from chatify.builddrafts import BuildDrafts

class SingleParseDrafts(unittest.TestCase):
 def test_real_save_parses_input_once_with_and_without_explicit_scope(self):
  for sections in (None,['app']):
   with self.subTest(sections=sections),tempfile.TemporaryDirectory() as folder:
    with patch('yaml.safe_load',wraps=yaml.safe_load) as parse:
     saved=BuildDrafts(folder).put('owner','app: {title: Raw section}',sections=sections)
    self.assertEqual(parse.call_count,1)
    self.assertEqual(set(yaml.safe_load(saved['yaml'])),{'app'})
    self.assertEqual(saved['sections'],['app'])

 def test_declared_sections_precede_defaults_and_extra_removal(self):
  for text,expected in [('app: {title: Scope}',{'app'}),('appearance: {}',{'appearance'}),('{}',set()),('provider: {type: mock}\napp: {title: Mixed}',{'provider','app'})]:
   with self.subTest(text=text):
    clean,declared=appbuilder.validate_declared(text)
    self.assertEqual(declared,expected)
    self.assertEqual(clean,appbuilder.validate(text))
    self.assertIn('storage',clean)

 def test_failed_validation_cannot_return_declared_scope_or_write(self):
  for text in ('app: [invalid]','unknown: yes','app: &shared {title: Anchor}','[app]'):
   with self.subTest(text=text),tempfile.TemporaryDirectory() as folder:
    with self.assertRaises(ValueError):appbuilder.validate_declared(text)
    store=BuildDrafts(folder)
    with self.assertRaises(ValueError):store.put('owner',text)
    self.assertEqual(store.list('owner'),[])

import importlib.util
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
def load(app,module):
 s=importlib.util.spec_from_file_location(module,ROOT/'apps'/app/(module+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class AttributedSources(unittest.TestCase):
 def test_fit_guidance_has_original_links(self):
  rows=load('fitchat','fit_sources').guidance('older adults strength training',8)
  self.assertTrue(rows);self.assertTrue(all(x['url'].startswith('https://') and 'Dated US guidance' in x['text'] for x in rows))
 def test_space_snapshot_retains_date_and_origin(self):
  rows=load('spacechat','space_sources').reference('Artemis program',8)
  self.assertTrue(rows);self.assertTrue(all(x['url'].startswith('https://en.wikipedia.org/') and '21 October 2026' in x['text'] for x in rows))
if __name__=='__main__':unittest.main()

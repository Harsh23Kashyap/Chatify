"""Public story assets must survive source and wheel packaging."""
import fnmatch
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class StoryPackageData(unittest.TestCase):
    def test_manifest_assets_are_explicit_package_data(self):
        text = (ROOT / 'pyproject.toml').read_text()
        patterns = ['web/media/stories/*.mp4', 'web/media/stories/*.jpg', 'web/media/stories/manifest.json']
        for pattern in patterns:
            self.assertIn('"' + pattern + '"', text)
        manifest = ROOT / 'chatify/web/media/stories/manifest.json'
        rows = json.loads(manifest.read_text())['stories']
        self.assertEqual(len(rows), len({r['id'] for r in rows}))
        self.assertTrue(rows)
        for row in rows:
            for key in ('src', 'poster'):
                name = row[key]
                self.assertEqual(Path(name).name, name)
                path = manifest.parent / name
                self.assertTrue(path.is_file(), name)
                self.assertTrue(any(fnmatch.fnmatch(str(path.relative_to(ROOT / 'chatify')), p) for p in patterns))

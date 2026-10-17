import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
class ReleasePins(unittest.TestCase):
    def test_installer_and_readme_target_renamed_release(self):
        version=re.search(r'^version = "([^"]+)"', (ROOT/'pyproject.toml').read_text(),re.M).group(1)
        self.assertIn("RELEASE='v"+version+"'",(ROOT/'scripts/install.py').read_text())
        readme=(ROOT/'README.md').read_text()
        self.assertNotIn('/blob/v0.1.',readme)
        self.assertNotIn('`uvx chatify`',readme)
        self.assertNotIn('Not published yet',(ROOT/'docs/RELEASE.md').read_text())

import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
class ReleasePins(unittest.TestCase):
    def test_installer_and_readme_target_renamed_release(self):
        version=re.search(r'^version = "([^"]+)"', (ROOT/'pyproject.toml').read_text(),re.M).group(1)
        # Main b50275b intentionally pins the published stable installer while
        # source metadata remains a separate candidate. Independently verified:
        # https://github.com/Harsh23Kashyap/Chatify/releases/tag/v0.4.33
        # https://pypi.org/pypi/chatify-app/json (2026-11-01)
        self.assertIn("RELEASE='v0.4.33'", (ROOT/'scripts/install.py').read_text())
        package_version = re.search(r'^__version__ = "([^"]+)"', (ROOT/'chatify/__init__.py').read_text(), re.M).group(1)
        self.assertEqual(version, package_version)
        readme=(ROOT/'README.md').read_text()
        self.assertNotIn('/blob/v0.1.',readme)
        self.assertNotIn('`uvx chatify`',readme)
        self.assertNotIn('Not published yet',(ROOT/'docs/RELEASE.md').read_text())

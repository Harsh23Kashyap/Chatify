import re
from pathlib import Path

import chatify


def test_package_version_matches_pyproject():
    root = Path(__file__).resolve().parent.parent
    text = (root / "pyproject.toml").read_text()
    m = re.search(r'^version = "([^"]+)"', text, re.M)
    assert m and chatify.__version__ == m.group(1)


def test_install_script_release_matches_version():
    root = Path(__file__).resolve().parent.parent
    script = (root / "scripts" / "install.py").read_text()
    m = re.search(r"RELEASE='v([^']+)'", script)
    assert m and m.group(1) == chatify.__version__

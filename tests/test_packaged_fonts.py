"""Distribution metadata must retain the offline reading fonts and their licenses."""
import pathlib, unittest

class PackagedFonts(unittest.TestCase):
    def test_font_directory_is_package_data(self):
        root=pathlib.Path(__file__).resolve().parents[1]
        metadata=(root/'pyproject.toml').read_text()
        self.assertIn('"web/fonts/*"',metadata)
        fonts=root/'chatify/web/fonts'
        self.assertTrue(any(fonts.glob('*.ttf')))
        self.assertTrue((fonts/'OFL.txt').is_file())

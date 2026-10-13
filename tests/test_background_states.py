import pathlib,unittest
class BackgroundStates(unittest.TestCase):
 def test_loading_and_local_files_share_selection_sequence(self):
  s=(pathlib.Path(__file__).resolve().parents[1]/'customchat/web/settings.js').read_text();start=s.index('if(f.key === "bg_image")');end=s.index('const v = get(f);',start);s=s[start:end];self.assertIn('const seq=++imageRequest;file.value=""',s);self.assertIn('if(seq!==imageRequest){URL.revokeObjectURL(url);return}',s);self.assertIn('Previous background kept.',s);self.assertIn('background-picture-preview',s);self.assertIn('link.value="";theme.bg_style="image"',s)

"""Generic source errors do not establish that a network was unreachable."""
from pathlib import Path
import unittest
class SourceErrorWording(unittest.TestCase):
 def test_generic_error_copy_is_about_results_not_connectivity(self):
  text=(Path(__file__).resolve().parents[1]/'chatify/web/app.js').read_text();section=text[text.index('const failedSources ='):text.index('if (!t.evidence.length)',text.index('const failedSources ='))]
  self.assertIn('could not return usable results',section);self.assertNotIn('could not be reached',section)
  self.assertIn('msg.includes(" ")',section);self.assertIn('named.join(" ")',section);self.assertIn('answered from the other sources.',section)
 def test_export_generic_and_fallback_wording_without_false_connectivity_claim(self):
  from chatify.exports import source_note,answer_markdown,chat_markdown
  from chatify.pipeline import Engine
  sources=[{'id':'ax','label':'arXiv'},{'id':'cr','label':'Crossref'}]
  expected='arXiv could not return usable results - answered from the other sources.'
  self.assertEqual(source_note({'ax':'ValueError'},sources),expected)
  turn={'question':'Fixture question','answer':'Fixture answer','evidence':[],'source_errors':{'ax':'ValueError'}}
  self.assertIn(expected,answer_markdown({'title':'Fixture'},turn,sources));self.assertIn(expected,chat_markdown('Fixture',[turn],sources))
  default=Engine.fallback_answer([]);self.assertIn('did not return an answer',default);self.assertNotIn('could not be reached',default)
  self.assertIn('Fixture named reason',Engine.fallback_answer([],why='Fixture named reason'))
if __name__=='__main__':unittest.main()

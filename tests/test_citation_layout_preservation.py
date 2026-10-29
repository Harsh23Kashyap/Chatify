import unittest
from chatify.pipeline import Engine
class CitationLayout(unittest.TestCase):
 def test_next_bold_heading_not_moved_into_previous_citation(self):
  answer='A supported finding [1].\n\n**Trial-based evidence:** Another finding [1].'
  out,ev=Engine.tidy(answer,[{'n':1,'title':'Trial','text':'findings','year':'2023'}])
  self.assertIn('\n\n**Trial-based evidence:**',out)
 def test_citation_before_heading_without_period_keeps_paragraph(self):
  answer='A supported finding. [1]\n\n**Trial-based evidence:** Another finding. [1]'
  out,ev=Engine.tidy(answer,[{'n':1,'title':'Trial','text':'findings','year':'2023'}])
  self.assertIn('[1]\n\n**Trial-based evidence:**',out)
 def test_citation_inside_bold_still_moved_outside(self):
  out,ev=Engine.tidy('**A supported finding [1]**',[{'n':1,'title':'Trial','text':'findings','year':'2023'}])
  self.assertIn('finding** [1]',out)

class CitationGrammar(unittest.TestCase):
 def test_replaced_evidence_reference_keeps_plural_verb_and_capital(self):
  from chatify.pipeline import Engine
  ev=[{'n':1,'title':'Source','text':'source'}]
  answer,_=Engine.tidy('The provided evidence reports an association. [1]\n\nThe available evidence describes a cohort. [1]',ev)
  self.assertIn('The cited sources report an association.',answer)
  self.assertIn('The cited sources describe a cohort.',answer)

 def test_meaningful_evidence_nouns_are_not_rewritten(self):
  answer='The evidence review reports findings and judged the evidence for diabetes. [1]'
  out,_=Engine.tidy(answer,[{'n':1,'title':'Review','text':'findings'}])
  self.assertEqual(out,answer)

class InlineBoldCitations(unittest.TestCase):
 def test_next_inline_bold_label_stays_after_citation(self):
  answer='**Randomized assignment** records the allocated diet. [1] **Achieved adherence** measures actual diet. [1]'
  out,_=Engine.tidy(answer,[{'n':1,'title':'Trial','text':'diet'}])
  self.assertEqual(out,answer)
 def test_citation_inside_later_bold_span_moves_outside(self):
  out,_=Engine.tidy('**First label** words. **Another supported claim [1]** Next words.',[{'n':1,'title':'Trial','text':'words'}])
  self.assertEqual(out,'**First label** words. **Another supported claim** [1] Next words.')
 def test_citation_after_plain_text_keeps_next_bold_label(self):
  answer='Supported finding. [1] **Limits:** More findings. [1]'
  out,_=Engine.tidy(answer,[{'n':1,'title':'Trial','text':'finding'}])
  self.assertEqual(out,answer)

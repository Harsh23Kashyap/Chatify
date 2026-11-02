import copy,io,unittest
from pypdf import PdfReader
from chatify.exports import _answer_pdf_line,pdf_bytes,answer_markdown
class PDFAnswerMarkdown(unittest.TestCase):
 def test_balanced_bold_display_without_content_loss(self):
  self.assertEqual(_answer_pdf_line('**Direct Answer**: A qualified finding [1].'),('body','Direct Answer: A qualified finding [1].'))
  self.assertEqual(_answer_pdf_line('**Established Findings**:'),('body','Established Findings:'))
  self.assertEqual(_answer_pdf_line('1. **Conservation Marketing**: potential [1].'),('body','1. Conservation Marketing: potential [1].'))
  self.assertEqual(_answer_pdf_line('**Findings**'),('answer_heading','Findings'))
  self.assertEqual(_answer_pdf_line('### Uncertainty'),('answer_heading','Uncertainty'))
 def test_literal_code_math_and_unmatched_not_rewritten(self):
  for text in ['x**2','**unfinished','literal **','`**literal**`','A * B','a_b','10^9','A\\*\\*literal\\*\\*','pipe | prose']:
   self.assertEqual(_answer_pdf_line(text),('body',text))
 def test_pdf_only_presentation_not_stored_body_or_markdown(self):
  t={'question':'Evidence?','answer':'**Direct Answer**: uncertain [1].\n\n1. **Evidence**: NOT established [1].\n\n### Limitations\nNo long-term result [1].','evidence':[{'n':1,'title':'Source','url':'https://example.invalid'}]};before=copy.deepcopy(t)
  text='\n'.join(p.extract_text()for p in PdfReader(io.BytesIO(pdf_bytes('Chat',t))).pages)
  self.assertNotIn('**',text);self.assertNotIn('###',text)
  for part in ['Direct Answer: uncertain','Evidence: NOT established','Limitations','No long-term result','[1]']:self.assertIn(part,text)
  self.assertIn(t['answer'],answer_markdown({},t));self.assertEqual(t,before)

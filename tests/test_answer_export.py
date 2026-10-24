import unittest
from chatify.exports import pdf_bytes,answer_markdown
class Export(unittest.TestCase):
 def turn(self):return {'question':'Fiber?','answer':('Fiber answer [1].\n'*200)+'FINAL END','evidence':[{'n':1,'title':'A source','url':'https://example.invalid/source','document':'file.md','page':2,'version':'abc123'}],'owner':'secret-owner','chat':'secret-chat','profile':'private'}
 def test_markdown_snapshot_private(self):
  m=answer_markdown({'title':'Diet Chat'},self.turn());self.assertIn('abc123',m);self.assertIn('page 2',m);self.assertIn('FINAL END',m)
  for private in ['secret-owner','secret-chat','private']:self.assertNotIn(private,m)
 def test_multi_page_no_cut(self):
  b=pdf_bytes('Diet Chat',self.turn());self.assertIn(b'FINAL END',b);self.assertIn(b'abc123',b);self.assertGreater(b.count(b'/Type /Page '),1)
 def test_unicode_no_silent_loss(self):
  t=self.turn();t['answer']='नमस्ते'
  with self.assertRaises(ValueError):pdf_bytes('Chat',t)
  self.assertIn('नमस्ते',answer_markdown({'title':'Chat'},t))
 def test_typographic_unicode_renders_real_pdf(self):
  t=self.turn();t['answer']='Returns - net 4.5% \u2014 \u201cgrowth\u201d \u2022 \u20b91,000 \u2192 \u20b91,045'
  b=pdf_bytes('Wealth Chat',t)
  self.assertTrue(b.startswith(b'%PDF-1.4'));self.assertIn(b'Rs. 1,000 -> Rs. 1,045',b);self.assertIn(b'\x97',b)
 def test_typographic_unicode_no_longer_rejected(self):
  t=self.turn();t['answer']='Em dash \u2014 en dash \u2013 quotes \u2018x\u2019 \u201cy\u201d bullet \u2022 ellipsis \u2026'
  self.assertTrue(pdf_bytes('Chat',t).startswith(b'%PDF'))
 def test_stylized_latin_and_accents_fold_not_reject(self):
  # Real failing text from the live demo: Wikipedia "E L I T Ǝ" extract
  t=self.turn();t['answer']='- Elite (Spanish: Élite; stylized as E L I T Ǝ) is a Spanish teen drama series created by Carlos Montero and Darío Madrona.'
  t['evidence']=[{'n':1,'title':'Elite (TV series)','url':'https://en.wikipedia.org/wiki/Elite_(TV_series)','document':'wikipedia','snapshot':'stylized as E L I T Ǝ'}]
  b=pdf_bytes('Balcony Gardening Chat',t)
  self.assertTrue(b.startswith(b'%PDF-1.4'));self.assertIn(b'E L I T E',b);self.assertIn(b'Madrona',b)
  self.assertIn('E L I T Ǝ',answer_markdown({'title':'Chat'},t))
 def test_accented_latin_folds_via_nfkd(self):
  t=self.turn();t['answer']='S\u0219l\u0142owacki \u0151\u017c \u0103\u010d\u011b'
  self.assertTrue(pdf_bytes('Chat',t).startswith(b'%PDF'))
 def test_accent_not_pdf_injection(self):self.assertIn(b'0.090 0.247 0.208',pdf_bytes('Chat',self.turn(),'bad-pdf'))

 def test_branded_template_fonts_paper_and_metadata(self):
  b=pdf_bytes('Diet Chat',self.turn())
  self.assertIn(b'/BaseFont /Times-Roman',b)
  self.assertIn(b'/BaseFont /Helvetica-Bold',b)
  self.assertIn(b'0.973 0.957 0.914 rg 0 0 595 842 re f',b)
  self.assertIn(b'Sources at answer time',b)
  self.assertIn('## Sources at answer time',answer_markdown({'title':'Chat'},self.turn()))
 def test_wide_unbroken_text_preserved(self):
  t=self.turn();t['answer']='W'*240+' END WIDE';t['question']='W'*90
  b=pdf_bytes('Chat',t)
  self.assertIn(b'END WIDE',b)
  import re
  lines=re.findall(rb'\(([^()]*)\) Tj',b)
  self.assertTrue(any(b'W' in row for row in lines))
  self.assertLessEqual(max(len(row) for row in lines if b'WW' in row),70)
 def test_table_recomposed_as_labeled_rows(self):
  t=self.turn();t['answer']='| Source | Headline count | Citations |\n| --- | --- | --- |\n| Feed | 2 | [1] |'
  b=pdf_bytes('Chat',t);self.assertIn(b'Source: Feed; Headline count: 2; Citations: [1]',b);self.assertNotIn(b'| --- |',b)
 def test_bibtex_missing_optional_metadata(self):
  from chatify.exports import bibtex
  self.assertIn('Minimal',bibtex([{'title':'Minimal','url':'https://example.org'}]))
 def test_null_optional_url_exports(self):
  t=self.turn();t['evidence'][0]['url']=None
  self.assertIn('A source',answer_markdown({'title':'Chat'},t));self.assertIn(b'A source',pdf_bytes('Chat',t))
 def test_table_extra_cells_and_following_pipe_prose_not_lost(self):
  t=self.turn();t['answer']='| A | B |\n| --- | --- |\n| one | two | EXTRA |\nProse with | pipe'
  b=pdf_bytes('Chat',t);self.assertIn(b'EXTRA',b);self.assertIn(b'Prose with',b)
 def test_escaped_pipe_table_label_retained(self):
  t=self.turn();t['answer']='| Source | Count |\n| --- | --- |\n| A\\|B | 1 |'
  self.assertIn(b'Source: A|B; Count: 1',pdf_bytes('Chat',t))

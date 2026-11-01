import copy,io,unittest
from chatify.exports import answer_markdown,chat_markdown,pdf_bytes,bibtex
from chatify.pipeline import Engine
from chatify.support_verdicts import unverified_source_preview
from pypdf import PdfReader

LABEL='Title only; no abstract or article text supplied'
class CrossrefExportProvenance(unittest.TestCase):
 def row(self):return {'n':1,'id':'doi:10.1201/9781351114585-6','title':'Soil sampling for soil health assessment','text':'Soil sampling for soil health assessment','url':'https://doi.org/10.1201/9781351114585-6','year':'2018','content_kind':'title_only','authors':[]}
 def turn(self):return {'question':'Which soil-health reference was retrieved?','answer':'A reference title was retrieved, not study findings [1].','evidence':[self.row()]}
 def test_projection_retains_kind_not_false_verification(self):
  row=self.row();before=copy.deepcopy(row);p=unverified_source_preview([row]);self.assertEqual(p['items'][0]['content_kind'],'title_only');self.assertEqual(p['items'][0]['text'],row['text']);self.assertFalse(p['answer_verified']);self.assertEqual(row,before)
 def test_preview_label_outside_exact_quote(self):
  text=Engine.source_preview(None,[self.row()]);self.assertIn(LABEL+'.',text);self.assertIn('> '+self.row()['text'],text);self.assertIn('not a verified answer',text)
 def test_answer_and_chat_markdown_keep_provenance(self):
  turn=self.turn()
  for text in [answer_markdown({'title':'Source provenance'},turn),chat_markdown('Source provenance',[turn])]:
   with self.subTest(text=text):self.assertIn(LABEL,text);self.assertIn(turn['evidence'][0]['url'],text);self.assertIn(turn['answer'],text)
 def test_pdf_keeps_provenance_with_source(self):
  pages=PdfReader(io.BytesIO(pdf_bytes('Source provenance',self.turn()))).pages
  text='\n'.join(p.extract_text()for p in pages);self.assertIn(LABEL,text);self.assertIn(self.row()['title'],text)
 def test_bibtex_note_not_fake_abstract(self):
  text=bibtex([self.row()]);self.assertIn('note = {'+LABEL+'}',text);self.assertNotIn('abstract =',text);self.assertIn(self.row()['url'],text)
 def test_unmarked_equal_title_text_does_not_infer_absence(self):
  row=self.row();row.pop('content_kind');turn=self.turn();turn['evidence']=[row]
  self.assertNotIn('content_kind',unverified_source_preview([row])['items'][0])
  for text in [Engine.source_preview(None,[row]),answer_markdown({},turn),chat_markdown('Chat',[turn]),bibtex([row])]:
   with self.subTest(text=text):self.assertNotIn(LABEL,text)
 def test_unknown_kind_not_promoted_to_title_only(self):
  row=self.row();row['content_kind']='abstract';self.assertNotIn('content_kind',unverified_source_preview([row])['items'][0]);self.assertNotIn(LABEL,bibtex([row]))
 def test_large_title_only_still_omitted_not_truncated(self):
  row=self.row();row['text']='X'*12001;p=unverified_source_preview([row]);self.assertEqual(p['items'],[]);self.assertEqual(p['omitted_sources'],1)

 def test_model_unavailable_fallback_also_labels_title_only(self):
  self.assertIn(LABEL,Engine.fallback_answer([self.row()]))
  row=self.row();row.pop('content_kind');self.assertNotIn(LABEL,Engine.fallback_answer([row]))

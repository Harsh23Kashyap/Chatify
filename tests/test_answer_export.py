import unittest
from chatify.exports import pdf_bytes,answer_markdown
def _pdf_text(b):
 import io
 from pypdf import PdfReader
 return '\n'.join(p.extract_text() for p in PdfReader(io.BytesIO(b)).pages)
def _pdf_pages(b):
 import io
 from pypdf import PdfReader
 return PdfReader(io.BytesIO(b)).pages
def _pdf_fonts(b):
 import io
 from pypdf import PdfReader
 names=set()
 for p in PdfReader(io.BytesIO(b)).pages:
  for f in (p['/Resources'].get('/Font') or {}).values():
   names.add(str(f.get_object().get('/BaseFont')))
 return names
class Export(unittest.TestCase):
 def turn(self):return {'question':'Fiber?','answer':('Fiber answer [1].\n'*200)+'FINAL END','evidence':[{'n':1,'title':'A source','url':'https://example.invalid/source','document':'file.md','page':2,'version':'abc123'}],'owner':'secret-owner','chat':'secret-chat','profile':'private'}
 def test_markdown_snapshot_private(self):
  m=answer_markdown({'title':'Diet Chat'},self.turn());self.assertIn('abc123',m);self.assertIn('page 2',m);self.assertIn('FINAL END',m)
  for private in ['secret-owner','secret-chat','private']:self.assertNotIn(private,m)
 def test_multi_page_no_cut(self):
  b=pdf_bytes('Diet Chat',self.turn())
  self.assertGreater(len(_pdf_pages(b)),1)
  text=_pdf_text(b);self.assertIn('FINAL END',text);self.assertIn('abc123',text)
 def test_devanagari_renders_not_rejected(self):
  # Live-demo gap: ordinary Hindi answer text was rejected outright. Bundled Noto
  # fonts + shaping now export it; extraction of shaped runs is approximate, so
  # correctness of the rendering is covered by the pixel-checked fixture.
  t=self.turn();t['answer']='नमस्ते';t['question']='नमस्ते'
  b=pdf_bytes('Chat',t)
  self.assertTrue(b.startswith(b'%PDF'))
  self.assertIn('नमस्ते',_pdf_text(b))
  self.assertIn('नमस्ते',answer_markdown({'title':'Chat'},t))
 def test_uncovered_scripts_still_rejected_honestly(self):
  t=self.turn();t['answer']='日本語のテキスト'
  with self.assertRaises(ValueError):pdf_bytes('Chat',t)
  self.assertIn('日本語のテキスト',answer_markdown({'title':'Chat'},t))
 def test_typographic_unicode_renders_real_pdf(self):
  t=self.turn();t['answer']='Returns - net 4.5% \u2014 \u201cgrowth\u201d \u2022 \u20b91,000 \u2192 \u20b91,045'
  b=pdf_bytes('Wealth Chat',t)
  self.assertTrue(b.startswith(b'%PDF'))
  text=_pdf_text(b)
  # Real Unicode now: the rupee sign and arrow render as themselves, no folding.
  self.assertIn('\u20b91,000 \u2192 \u20b91,045',text)
 def test_typographic_unicode_no_longer_rejected(self):
  t=self.turn();t['answer']='Em dash \u2014 en dash \u2013 quotes \u2018x\u2019 \u201cy\u201d bullet \u2022 ellipsis \u2026 check \u2713'
  self.assertTrue(pdf_bytes('Chat',t).startswith(b'%PDF'))
 def test_stylized_latin_and_accents_render_as_themselves(self):
  # Real failing text from the live demo: Wikipedia "E L I T Ǝ" extract
  t=self.turn();t['answer']='- Elite (Spanish: Élite; stylized as E L I T Ǝ) is a Spanish teen drama series created by Carlos Montero and Darío Madrona.'
  t['evidence']=[{'n':1,'title':'Elite (TV series)','url':'https://en.wikipedia.org/wiki/Elite_(TV_series)','document':'wikipedia','snapshot':'stylized as E L I T Ǝ'}]
  text=_pdf_text(pdf_bytes('Balcony Gardening Chat',t))
  self.assertIn('E L I T Ǝ',text);self.assertIn('Madrona',text)
  self.assertIn('E L I T Ǝ',answer_markdown({'title':'Chat'},t))
 def test_accented_latin_renders_via_font(self):
  t=self.turn();t['answer']='S\u0219l\u0142owacki \u0151\u017c \u0103\u010d\u011b'
  self.assertIn('S\u0219l\u0142owacki',_pdf_text(pdf_bytes('Chat',t)))
 def test_accent_not_pdf_injection(self):
  b=pdf_bytes('Chat',self.turn(),'bad-pdf')
  self.assertTrue(b.startswith(b'%PDF'));self.assertGreaterEqual(len(_pdf_pages(b)),1)

 def test_branded_template_fonts_paper_and_metadata(self):
  b=pdf_bytes('Diet Chat',self.turn())
  fonts=_pdf_fonts(b)
  self.assertTrue(any('NotoSans' in n for n in fonts),fonts)
  self.assertIn('Sources at answer time',_pdf_text(b))
  self.assertIn('## Sources at answer time',answer_markdown({'title':'Chat'},self.turn()))
 def test_wide_unbroken_text_preserved(self):
  t=self.turn();t['answer']='W'*240+' END WIDE';t['question']='W'*90
  text=_pdf_text(pdf_bytes('Chat',t))
  self.assertIn('END WIDE',text);self.assertIn('W'*40,text)
 def test_table_recomposed_as_labeled_rows(self):
  t=self.turn();t['answer']='| Source | Headline count | Citations |\n| --- | --- | --- |\n| Feed | 2 | [1] |'
  text=_pdf_text(pdf_bytes('Chat',t))
  self.assertIn('Source: Feed; Headline count: 2; Citations: [1]',text);self.assertNotIn('| --- |',text)
 def test_bibtex_missing_optional_metadata(self):
  from chatify.exports import bibtex
  self.assertIn('Minimal',bibtex([{'title':'Minimal','url':'https://example.org'}]))
 def test_null_optional_url_exports(self):
  t=self.turn();t['evidence'][0]['url']=None
  self.assertIn('A source',answer_markdown({'title':'Chat'},t));self.assertIn('A source',_pdf_text(pdf_bytes('Chat',t)))
 def test_table_extra_cells_and_following_pipe_prose_not_lost(self):
  t=self.turn();t['answer']='| A | B |\n| --- | --- |\n| one | two | EXTRA |\nProse with | pipe'
  text=_pdf_text(pdf_bytes('Chat',t));self.assertIn('EXTRA',text);self.assertIn('Prose with',text)
 def test_escaped_pipe_table_label_retained(self):
  t=self.turn();t['answer']='| Source | Count |\n| --- | --- |\n| A\\|B | 1 |'
  self.assertIn('Source: A|B; Count: 1',_pdf_text(pdf_bytes('Chat',t)))
class PlainTextDisplay(unittest.TestCase):
 def test_markdown_and_latex_normalized_in_exports(self):
  # Live demo 2026-10-25: uploaded "##"/"**" and arXiv "$z>10$" / "MgAl$_2$O$_4$"
  # rendered literally in the answer text and PDF.
  from chatify.exports import pdf_bytes,answer_markdown,chat_markdown
  from chatify.pipeline import Engine,plain_text
  assert plain_text('Li-Doped MgAl$_2$O$_4$')=='Li-Doped MgAl_2O_4'
  t={'question':'Why malformed hands?','answer':'- Hands fail when fine detail is under-modeled [1]','evidence':[{'n':1,'title':'Li-Doped MgAl$_2$O$_4$ at $z>10$','url':'https://example.invalid/a'}]}
  m=answer_markdown({'title':'Chat'},t)
  self.assertIn('Li-Doped MgAl_2O_4 at z>10',m);self.assertNotIn('$_2$',m)
  text=_pdf_text(pdf_bytes('Chat',t))
  self.assertIn('Li-Doped MgAl_2O_4',text);self.assertNotIn('$_',text)
  cm=chat_markdown('Chat',[t]);self.assertIn('Li-Doped MgAl_2O_4',cm)
 def test_script_markers_keep_explicit_notation(self):
  # R3 rendered review 2026-10-25: flattening scripts concatenated them into
  # the base and corrupted magnitudes - 10^{9} displayed as "109" and
  # M_{\rm UV} as "Mrm UV". Explicit caret/underscore notation keeps the
  # scientific meaning unambiguous; legacy font switches never leak or eat.
  from chatify.pipeline import plain_text
  self.assertEqual(plain_text('galaxies of 10^{9} M\\odot at z>10'),'galaxies of 10^9 M⊙ at z>10')
  self.assertEqual(plain_text('M_{\\rm UV} LF slope'),'M_UV LF slope')
  self.assertEqual(plain_text('Lyman-$\\alpha$ at $10^{12}$'),'Lyman-α at 10^12')
  self.assertEqual(plain_text('Li-Doped MgAl$_2$O$_4$ spinel'),'Li-Doped MgAl_2O_4 spinel')
  self.assertEqual(plain_text('{\\bf H$_2$O} band, \\cal{} X, \\tt X$_1$'),'H_2O band, X, X_1')
 def test_pdf_keeps_sources_heading_with_first_source(self):
  # R5 rendered review 2026-10-25: "Sources at answer time" sat orphaned at the
  # bottom of a page while its first source opened the next.
  from chatify.exports import pdf_bytes
  t={'question':'Q?','answer':'\n'.join('finding %d with a fair amount of supporting prose around it'%i for i in range(30)),
   'evidence':[{'n':1,'title':'Source one','url':'https://example.invalid/1'},{'n':2,'title':'Source two','url':'https://example.invalid/2'}]}
  import io
  from pypdf import PdfReader
  pages=[p.extract_text() for p in PdfReader(io.BytesIO(pdf_bytes('Chat',t))).pages]
  idx=[i for i,p in enumerate(pages) if 'Sources at answer time' in p]
  self.assertTrue(idx)
  self.assertIn('Source one',pages[idx[-1]])
 def test_preview_bullets_normalized(self):
  from chatify.pipeline import Engine
  a=Engine.fallback_answer([{'n':1,'text':'## Hands and fine structure\n\n**Malformed hands** appear at $z>10$ in MgAl$_2$O$_4$.'}])
  self.assertIn('Malformed hands appear at z>10 in MgAl_2O_4.',a)
  self.assertNotIn('##',a);self.assertNotIn('**',a);self.assertNotIn('$',a)
class SourceNoteExports(unittest.TestCase):
 SOURCES=[{'id':'openalex','label':'OpenAlex'},{'id':'web','label':'Live web search'},{'id':'arxiv','label':'arXiv'}]
 def turn(self):
  return {'question':'Q','answer':'Preview [1]','evidence':[{'n':1,'title':'A source','url':'https://example.invalid/s'}],
          'source_errors':{'openalex':'OpenAlex needs a free API key. Add it under Sources.','web':'SetupRequired'}}
 def test_markdown_carries_named_note(self):
  from chatify.exports import answer_markdown,chat_markdown
  m=answer_markdown({'title':'Chat'},self.turn(),self.SOURCES)
  self.assertIn('OpenAlex: OpenAlex needs a free API key. Add it under Sources.',m)
  self.assertIn('Answered from the other sources.',m)
  cm=chat_markdown('Chat',[self.turn()],self.SOURCES)
  self.assertIn('OpenAlex needs a free API key',cm)
 def test_pdf_carries_named_note(self):
  from chatify.exports import pdf_bytes
  text=_pdf_text(pdf_bytes('Chat',self.turn(),sources=self.SOURCES))
  self.assertIn('OpenAlex needs a free API key',text);self.assertIn('Answered from the other sources',text)
 def test_all_failed_wording(self):
  from chatify.exports import source_note
  note=source_note({'openalex':'TimeoutError'},[{'id':'openalex','label':'OpenAlex'}])
  self.assertIn('OpenAlex could not be reached for this question.',note)
  self.assertEqual(source_note({},self.SOURCES),'');self.assertEqual(source_note(None,None),'')
 def test_no_note_without_errors(self):
  from chatify.exports import answer_markdown
  t=self.turn();t['source_errors']={}
  self.assertNotIn('could not be reached',answer_markdown({'title':'Chat'},t,self.SOURCES))

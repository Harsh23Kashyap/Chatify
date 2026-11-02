import copy,io,unittest
from chatify.answer_status import answer_note,UNVERIFIED_NOTE
from chatify.exports import answer_markdown,chat_markdown,pdf_bytes
from pypdf import PdfReader
class AnswerStatusNote(unittest.TestCase):
 def turn(self):return {'question':'Outcome?','answer':'The source suggests an effect, not a confirmed outcome [1].\n\nUncertainty remains [1].','evidence':[{'n':1,'title':'Title only','text':'Title only','url':'https://example.invalid/source','content_kind':'title_only'}]}
 def test_missing_false_and_true_do_not_imply_independent_verification(self):
  for flag in [None,False,True]:
   t=self.turn()
   if flag is not None:t['answer_verified']=flag
   self.assertEqual(answer_note(t),UNVERIFIED_NOTE)
 def test_export_note_preserves_body_provenance_and_input(self):
  t=self.turn();before=copy.deepcopy(t)
  for text in [answer_markdown({},t),chat_markdown('Chat',[t])]:
   self.assertEqual(text.count(UNVERIFIED_NOTE),1);self.assertIn(t['answer'],text);self.assertIn('Title only; no abstract or article text supplied',text);self.assertIn(t['evidence'][0]['url'],text)
  self.assertEqual(t,before)
 def test_no_evidence_no_false_sources_label(self):
  t=self.turn();t['evidence']=[];self.assertEqual(answer_note(t),'');self.assertNotIn(UNVERIFIED_NOTE,answer_markdown({},t))
 def test_pdf_preserves_note_and_answer(self):
  t=self.turn();text='\n'.join(p.extract_text()for p in PdfReader(io.BytesIO(pdf_bytes('Answer status',t))).pages)
  self.assertIn('Not independently verified.',text);self.assertIn('uncertainty, attribution',text);self.assertIn('The source suggests an effect',text);self.assertIn('Uncertainty remains',text);self.assertIn('Title only;',text)

 def test_preview_warning_not_replaced(self):
  t=self.turn();t.update(response_kind='source_preview',answer='Retrieved source preview, not a verified answer.\n\n> Exact original source uncertainty.')
  out=answer_markdown({},t);self.assertIn(t['answer'],out);self.assertIn(UNVERIFIED_NOTE,out)
 def test_existing_support_warning_preserved(self):
  t=self.turn();t['answer']+='\n\nNote: the sources may not fully support this: uncertain outcome.'
  for out in [answer_markdown({},t),chat_markdown('Chat',[t])]:self.assertIn(t['answer'],out);self.assertEqual(out.count(UNVERIFIED_NOTE),1)

 def test_saved_history_keeps_original_body_and_missing_status_unverified(self):
  from chatify.store import Store
  store=Store(':memory:');chat=store.new_chat('owner');topic=store.new_topic('owner','Status topic');t=self.turn();before=copy.deepcopy(t)
  ident=store.add_turn(chat,topic,t['question'],t['question'],t['answer'],t['evidence'],[],'standard')
  saved=store.turn('owner',ident);self.assertEqual(saved['answer'],before['answer']);self.assertEqual(saved['evidence'],before['evidence']);self.assertNotIn('answer_verified',saved)
  self.assertIn(UNVERIFIED_NOTE,answer_markdown({},saved));self.assertEqual(store.turn('owner',ident)['answer'],before['answer'])

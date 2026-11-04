import json,unittest
from unittest.mock import patch,Mock
from chatify import providers,schema
from chatify.pipeline import Engine
from chatify.store import Store
from chatify.exports import answer_markdown
TEXT='Formula One wings generate downforce. [1] More details include'
class OutputLimit(unittest.TestCase):
 def test_complete_preserves_partial_and_no_fallback(self):
  p=providers.OpenAICompatible(schema.validate({'provider':{'type':'openai','model':'gpt-4o-mini'}}));other=Mock()
  with patch.object(p,'_auth',return_value={}),patch.object(providers,'_post',return_value={'choices':[{'message':{'content':TEXT},'finish_reason':'length'}]}):
   with self.assertRaises(providers.OutputLimitReached) as err:providers.WithFallback(p,other).complete([])
  self.assertEqual(err.exception.partial,TEXT);other.complete.assert_not_called()
 def test_stream_length_not_success_and_no_fallback(self):
  for text in (TEXT,''):
   p=providers.OpenAICompatible(schema.validate({'provider':{'type':'openai','model':'gpt-4o-mini'}}));other=Mock();seen=[]
   lines=['data: '+json.dumps({'choices':[{'delta':{'content':text},'finish_reason':'length'}]}),'data: [DONE]']
   with patch.object(p,'_auth',return_value={}),patch.object(providers,'_stream_lines',return_value=iter(lines)):
    with self.assertRaises(providers.OutputLimitReached):
     for x in providers.WithFallback(p,other).stream([]):seen.append(x)
   self.assertEqual(''.join(seen),text);other.stream.assert_not_called()
 def test_normal_stream_save_reopen_export_no_second_call(self):
  for stream,text in ((False,TEXT),(True,TEXT),(True,''),(False,'')):
   c=schema.validate({'provider':{'type':'openai','model':'gpt-4o-mini'},'memory':{'enabled':False},'prompt':{'model_followups':False},'retrieval':{'query_expansion':False}});e=Engine(c,Store(':memory:'));calls=[]
   class P:
    def complete(self,m):calls.append(m);raise providers.OutputLimitReached(text)
    def stream(self,m):calls.append(m);yield text;raise providers.OutputLimitReached()
   e.provider=P();e.followups=Mock(side_effect=AssertionError('no model followup after limit'));e._summarize=Mock(side_effect=AssertionError('no model summary after limit'));e.retrieve=lambda *a,**k:([{'n':1,'title':'F1','text':'Formula One wings generate downforce.','year':'','source':'docs','url':'fixture:source'}],{});chat=e.store.new_chat('u')
   with patch.object(e,'_llm_on',return_value=False):r=list(e.ask_stream('u',chat,'Explain Formula One wings.',new_topic=True))[-1][1] if stream else e.ask('u',chat,'Explain Formula One wings.',new_topic=True)
   self.assertEqual(r['model_status'],'output_limit');self.assertEqual(e.store.turn('u',r['id'])['model_status'],'output_limit');self.assertEqual(len(calls),1);self.assertTrue(r['answer'].startswith(text));self.assertIn('configured output limit and is incomplete',r['answer']);saved=e.store.turn('u',r['id']);self.assertEqual(saved['answer'],r['answer']);self.assertIn(r['answer'],answer_markdown(c['app'],saved));self.assertFalse(r['answer_verified'])
 def test_status_migrates_and_survives_disk_reopen(self):
  import sqlite3,tempfile,pathlib
  with tempfile.TemporaryDirectory() as d:
   path=str(pathlib.Path(d)/'old.db');db=sqlite3.connect(path);db.executescript("CREATE TABLE turns(id TEXT PRIMARY KEY,chat TEXT,topic TEXT,question TEXT,standalone TEXT,answer TEXT,evidence TEXT,ledger TEXT,style TEXT,source_errors TEXT,created REAL);");db.close();s=Store(path);chat=s.new_chat('u');tid=s.add_turn(chat,None,'q','q',TEXT,[],[],'standard',model_status='output_limit');self.assertEqual(Store(path).turn('u',tid)['model_status'],'output_limit')
 def test_ui_uses_saved_status_not_warning_text(self):
  import pathlib
  js=(pathlib.Path(__file__).resolve().parents[1]/'chatify/web/app.js').read_text()
  self.assertIn('t.model_status === "output_limit"',js);self.assertIn('Incomplete answer: output limit reached',js);self.assertIn('Incomplete answer. Scroll to latest',js);self.assertIn('S.turns.at(-1)?.model_status === "output_limit"',js)

 def test_branch_and_portable_roundtrip_keep_status_and_legacy_null(self):
  s=Store(':memory:');chat=s.new_chat('u');body=TEXT+'\n\n(The answer reached the configured output limit and is incomplete.)'
  a=s.add_turn(chat,None,'limited','limited',body,[],[],'standard',model_status='output_limit');b=s.add_turn(chat,None,'legacy','legacy','Legacy body',[],[],'standard');target=s.add_turn(chat,None,'target','target','Target',[],[],'standard')
  branch=s.branch('u',target,'new branch question');copied=s.turns('u',branch['chat']);self.assertEqual([x['model_status'] for x in copied],['output_limit',None]);self.assertEqual(copied[0]['answer'],body)
  payload=json.loads(json.dumps(s.export_all('u')));self.assertEqual(payload[0]['turns'][0]['model_status'],'output_limit');self.assertIsNone(payload[0]['turns'][1]['model_status'])
  dest=Store(':memory:');self.assertEqual(dest.import_chats('other',payload),2);turns=dest.export_all('other')[0]['turns'];self.assertEqual(turns[0]['model_status'],'output_limit');self.assertIsNone(turns[1]['model_status']);self.assertEqual(turns[0]['answer'],body)
  old=[{'turns':[{'question':'old','answer':'Old export'}]}];dest.import_chats('other',old);self.assertIsNone(dest.export_all('other')[-1]['turns'][0]['model_status'])
  self.assertEqual(s.turn('u',a)['model_status'],'output_limit');self.assertIsNone(s.turn('u',b)['model_status'])
 def test_import_invalid_status_rejects_batch_before_write(self):
  s=Store(':memory:')
  with self.assertRaises(ValueError):s.import_chats('u',[{'turns':[{'question':'q','answer':'a','model_status':'anything'}]}])
  self.assertEqual(s.export_all('u'),[])

"""Actual bundled app/runtime prompt contracts, not model-quality claims."""
import pathlib,tempfile,unittest
from unittest.mock import patch
from chatify import schema
from chatify.pipeline import Engine,concise_request,word_count_request
from chatify.store import Store
ROOT=pathlib.Path(__file__).resolve().parents[1]
class PlainLanguageDepth(unittest.TestCase):
 def engine(self):
  c=schema.load(str(ROOT/'apps/formulaone/app.yaml'));c['memory']['enabled']=False;c['retrieval']['query_rewrite']=False;c['retrieval']['query_expansion']=False;c['prompt']['auto_repair']=False;c['prompt']['model_followups']=False
  e=Engine(c,Store(':memory:'));e.followups=lambda *a,**k:[];return e
 def test_plain_language_is_not_forced_short(self):
  e=self.engine()
  for style,q in [('deep','Explain Formula One aerodynamics in plain language.'),('standard','Explain Formula One aerodynamics in plain language with detailed sections.'),('standard','Explain Formula One aerodynamics in plain English.')]:
   p=e.prompt(q,[],style,[],'')[0]['content'];self.assertNotIn('at most 120 words',p);self.assertIn('Plain vocabulary does not require a shorter answer',p)
 def test_explicit_shortening_and_ordinary_simplification_remain(self):
  for q,style in [('Explain that more simply.','standard'),('Give a brief summary in plain language.','deep'),('Explain that in detail but shorter.','deep')]:self.assertTrue(concise_request(q,style))
  self.assertFalse(concise_request('Explain more simply in full detail.'))
  self.assertFalse(concise_request('How do simply supported beams distribute loads?'))
 def test_normal_and_stream_actual_f1_engine_forward_detail(self):
  for stream in (False,True):
   e=self.engine();seen=[];q='Explain Formula One aerodynamics in plain language with detailed sections.'
   ev=[{'n':1,'id':'f1','title':'Formula One aerodynamics','text':'Formula One wings generate downforce. Drag resists motion.','source':'fia-regulations','year':'2026','venue':'FIA','url':'https://www.fia.com/'}]
   class P:
    def complete(self,m):seen.append(m);return 'Formula One wings generate downforce. [1]'
    def stream(self,m):seen.append(m);yield 'Formula One wings generate downforce. [1]'
   e.provider=P();e.retrieve=lambda *a,**kw:(ev,{})
   with patch.object(e,'_llm_on',return_value=False):
    chat=e.store.new_chat('u');r=list(e.ask_stream('u',chat,q,style='deep',new_topic=True))[-1][1] if stream else e.ask('u',chat,q,style='deep',new_topic=True)
   self.assertEqual(len(seen),1);self.assertNotIn('at most 120 words',seen[0][0]['content']);self.assertIn('full paragraphs',seen[0][0]['content']);self.assertEqual(e.store.turn('u',r['id'])['answer'],r['answer']);self.assertEqual(e.cfg['provider']['model'],'gpt-4.1-mini');self.assertEqual(e.cfg['provider']['max_output_tokens'],4096)
 def test_revision_uses_same_length_intent(self):
  e=self.engine();seen=[];e._llm_on=lambda k:True
  class P:
   def complete(self,m):seen.append(m);return 'Formula One wings generate downforce. [1]'
  e.provider=P();e.revise('Formula One wings generate downforce. [1]',[{'n':1,'title':'F1','text':'Formula One wings generate downforce.'}],'Explain Formula One aerodynamics in plain language with detailed sections.',style='deep')
  self.assertNotIn('at most 120 words',seen[0][0]['content'])

 def test_bounded_intent_table_generation_revision_normal_stream(self):
  cases=[
   ('Compare shorter and longer wings in detail',False,''),
   ('Give a brief history of aerodynamics in plain English',False,''),
   ('Compare shorter distance and drag',False,''),
   ('Keep the response short',True,''),
   ('Give me a short simple explanation',True,''),
   ('Give a short answer',True,''),('Keep it brief',True,''),
   ('Explain more simply, with all technical details',False,''),
   ('More simply and completely',False,''),
   ('Explain in plain language with all details',False,''),
   ('Make this easier to understand',False,''),
   ('Explain in simple language',False,''),('Explain in simple terms',False,''),
   ('Explain plainly',False,''),('Make this accessible',False,''),
   ('Explain more simply',True,''),
   ('Explain in 100 words',False,'100 words'),
   ('Explain in under 100 words',False,'under 100 words'),
   ('Give an exactly 300 words explanation',False,'exactly 300 words'),
   ('Give a 300-word answer in simple terms',False,'300-word answer'),
   ('Compare the 100-word detail in these reports',False,''),
  ]
  ev=[{'n':1,'id':'f1','title':'F1','text':'Wings generate downforce.','source':'docs','year':'','url':'fixture:source'}]
  for q,short,words in cases:
   for stream in (False,True):
    with self.subTest(q=q,stream=stream):
     e=self.engine();seen=[];e.cfg['prompt']['revise']=True;e._llm_on=lambda k:k=='revise'
     class P:
      def complete(self,m):seen.append(m);return 'Wings generate downforce. [1]'
      def stream(self,m):seen.append(m);yield 'Wings generate downforce. [1]'
     e.provider=P();e.retrieve=lambda *a,**k:(ev,{});chat=e.store.new_chat('u')
     r=list(e.ask_stream('u',chat,q,new_topic=True))[-1][1] if stream else e.ask('u',chat,q,new_topic=True)
     self.assertEqual(concise_request(q),short);self.assertEqual(word_count_request(q),words)
     self.assertEqual(len(seen),2)
     for m in seen:
      system=m[0]['content'];self.assertEqual('at most 120 words' in system,short)
      if words:self.assertIn("explicit word-count request: "+words,system)
     self.assertEqual(e.store.turn('u',r['id'])['answer'],r['answer'])

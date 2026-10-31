"""Safety and source contracts, independent of live retrieval relevance qualification."""
import importlib.util,json,sys,unittest,urllib.parse
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('agriculture_sources',ROOT/'apps/agriculturechat/agriculture_sources.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
class Response:
 def __init__(self,data):self.data=data
 def __enter__(self):return self
 def __exit__(self,*args):pass
 def read(self,size):return self.data[:size]
class AgricultureSources(unittest.TestCase):
 def test_empty_and_zero_do_not_call_network(self):
  with patch.object(a.urllib.request,'urlopen',side_effect=AssertionError('network')):
   self.assertEqual(a.research('what should I do'),[])
   self.assertEqual(a.research('rice nitrogen',0),[])
 def test_abstract_metadata_and_preprint_label(self):
  row={'id':'123','source':'PPR','title':'Rice <i>study</i>','abstractText':'<p>Limited experiment &amp; uncertainty</p>','pubYear':'2025','doi':'10.123/a'}
  def fetch(req,timeout):
   q=urllib.parse.parse_qs(urllib.parse.urlsplit(req.full_url).query)
   self.assertEqual(q['pageSize'],['10']);self.assertEqual(q['resultType'],['core']);self.assertIn('TITLE_ABS:agricultur*',q['query'][0]);self.assertEqual(timeout,20)
   return Response(json.dumps({'resultList':{'result':[row]}}).encode())
  with patch.object(a.urllib.request,'urlopen',side_effect=fetch):r=a.research('rice nitrogen Bangladesh',100)
  self.assertEqual(r[0]['title'],'Rice study');self.assertIn('PREPRINT',r[0]['text']);self.assertIn('not a farm-specific',r[0]['text']);self.assertEqual(r[0]['year'],'2025')
 def test_literature_does_not_receive_global_or_regional_guides(self):
  self.assertEqual(a.guidance('research legumes soil fertility Tanzania'),[])
  self.assertEqual(a.guidance('studies of rice nitrogen Bangladesh'),[])
 def test_generic_fertilizer_choice_does_not_promote_random_experiments(self):
  with patch.object(a.urllib.request,'urlopen',side_effect=AssertionError('network')):
   self.assertEqual(a.research('What should I know before choosing fertilizer for my farm?'),[])
 def test_conversational_words_removed_without_losing_country_crop(self):
  def fetch(req,timeout):
   query=urllib.parse.parse_qs(urllib.parse.urlsplit(req.full_url).query)['query'][0]
   for word in ('rice','Bangladesh','nitrogen','water'):self.assertIn('TITLE_ABS:'+chr(34)+word+chr(34),query)
   for word in ('grow','say','research','my'):self.assertNotIn('TITLE_ABS:'+chr(34)+word+chr(34),query)
   return Response(b'{}')
  with patch.object(a.urllib.request,'urlopen',side_effect=fetch):a.research('I grow rice in Bangladesh. What does research say about nitrogen and water management?')
 def test_duplicate_metadata_does_not_count_as_two_studies(self):
  row={'id':'123','source':'MED','title':'Rice study.','abstractText':'Rice research','doi':'10.123/a'}
  other=dict(row,id='456',source='AGR',title='Rice study')
  with patch.object(a.urllib.request,'urlopen',return_value=Response(json.dumps({'resultList':{'result':[row,other]}}).encode())):self.assertEqual(len(a.research('rice nitrogen')),1)
 def test_oversized_response_rejected(self):
  with patch.object(a.urllib.request,'urlopen',return_value=Response(b'x'*2000001)):
   with self.assertRaises(ValueError):a.research('rice nitrogen')
 def test_missing_abstract_and_invalid_identifier_omitted(self):
  payload={'resultList':{'result':[{'id':'123','source':'MED','title':'Missing abstract'},{'id':'../unsafe','source':'MED','title':'Rice','abstractText':'Test'}]}}
  with patch.object(a.urllib.request,'urlopen',return_value=Response(json.dumps(payload).encode())):self.assertEqual(a.research('rice nitrogen'),[])
 def test_guidance_has_origin_and_region(self):
  rows=a.guidance('soil test nutrient management',8)
  self.assertTrue(rows)
  self.assertTrue(all(r['url'].startswith('https://') and 'Not a field-specific' in r['text'] for r in rows))
if __name__=='__main__':unittest.main()

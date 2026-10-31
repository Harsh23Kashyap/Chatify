import unittest,copy,json
from chatify import apipicks,buildjobs,schema,theme
class GeneratedDrafts(unittest.TestCase):
 def test_observed_provider_aliases_get_verified_metadata(self):
  picks=apipicks.enrich([{'service':x} for x in ['OpenAlex Works API','Crossref REST API','PubMed and the NCBI Entrez E-utilities']])
  self.assertFalse(picks[0]['key_required']);self.assertIn('openalex.org',picks[0]['key_url'])
  self.assertFalse(picks[1]['key_required']);self.assertFalse(picks[2]['key_required'])
 def test_unknown_suffix_not_authenticated_as_known_service(self):
  self.assertNotIn('provider_page',apipicks.enrich([{'service':'OpenAlex malicious proxy'}])[0])
 def test_builder_supplies_source_enum(self):
  class Provider:
   def complete(self,messages):
    self.message=messages[0]['content'];return '[]'
  pv=Provider();job={'cancel':False,'calls':0,'provider':pv,'cfg':copy.deepcopy(schema.DEFAULTS),'parts':{},'errors':{},'active':set(),'brief':'Nutrition'}
  buildjobs.BuildJobs()._draft_part(job,'config:sources',dict(buildjobs.PARTS)['config:sources'])
  self.assertIn('supported_connectors',pv.message);self.assertIn('pubmed',pv.message)
 def test_long_interface_text_rejected_not_silently_cut(self):
  defaults=dict(buildjobs.PARTS)['appearance:wording_motion']['defaults'];result=copy.deepcopy(defaults)
  for k in result:
   if k.startswith('txt_'):result[k]='Nutrition interface copy'
  result['txt_hint']='A'*121
  class Provider:
   def complete(self,messages):return json.dumps(result)
  job={'cancel':False,'calls':0,'provider':Provider(),'cfg':copy.deepcopy(schema.DEFAULTS),'parts':{},'errors':{},'active':set(),'brief':'Nutrition'}
  with self.assertRaisesRegex(ValueError,'txt_hint.*120'):buildjobs.BuildJobs()._draft_part(job,'appearance:wording_motion',dict(buildjobs.PARTS)['appearance:wording_motion'])
  self.assertNotIn('appearance:wording_motion',job['parts'])

 def test_search_contract_handles_attributed_mixed_content_xml(self):
  from chatify import generators
  contract=generators.KINDS['search']['contract']
  self.assertIn('ElementTree.fromstring',contract);self.assertIn('attributes and nested inline text',contract)

 def test_manual_helper_prompt_names_actual_safety_limits(self):
  from chatify import generator_design,generators
  prompt=generator_design.code_system('search',generators.KINDS['search']['contract'])
  for text in ['Do not import socket','No classes','executable module-level','ElementTree.fromstring']:
   self.assertIn(text,prompt)

 def test_source_urls_bind_to_actual_row_identity_after_filtering(self):
  from chatify import generators
  contract=generators.KINDS['search']['contract']
  self.assertIn("same parsed item's actual ID",contract)
  self.assertIn('never its list position',contract);self.assertIn('deduplicate by real item ID/URL',contract)

 def test_confirmed_pubmed_gets_verified_interface_not_blank_url_instruction(self):
  class Provider:
   def complete(self,messages):self.message=messages[0]['content'];return '[]'
  pv=Provider();job={'cancel':False,'calls':0,'provider':pv,'cfg':copy.deepcopy(schema.DEFAULTS),'parts':{},'errors':{},'active':set(),'brief':'Nutrition','confirmed_sources':['pubmed']}
  with self.assertRaisesRegex(ValueError,'confirmed sources'):buildjobs.BuildJobs()._draft_part(job,'api',dict(buildjobs.PARTS)['api'])
  for text in ['verified_source_interface','esearch.fcgi','efetch.fcgi','esearchresult.idlist','not empty URL placeholders']:self.assertIn(text,pv.message)

 def test_api_branch_receives_same_search_output_and_xml_contract(self):
  class Provider:
   def complete(self,messages):self.message=messages[0]['content'];return '[]'
  pv=Provider();job={'cancel':False,'calls':0,'provider':pv,'cfg':copy.deepcopy(schema.DEFAULTS),'parts':{},'errors':{},'active':set(),'brief':'Nutrition','confirmed_sources':['pubmed']}
  with self.assertRaises(ValueError):buildjobs.BuildJobs()._draft_part(job,'api',dict(buildjobs.PARTS)['api'])
  for text in ['helper_contract','ElementTree.fromstring','exactly these keys','Never return a records/error envelope']:self.assertIn(text,pv.message)

 def test_observed_api_envelope_and_literal_xml_search_rejected(self):
  from chatify import generators
  code='''import urllib.request

def search(query, limit=6):
    try:
        with urllib.request.urlopen(query, timeout=15) as response:
            text=response.read(1000).decode('utf8')
        text=text.split('<PubmedArticle')[1:]
        return {'records': text, 'error': ''}
    except Exception:
        return {'records': [], 'error': 'failed'}
'''
  ok,problems=generators.review_code('search',code)
  self.assertFalse(ok)
  self.assertTrue(any('dict envelope' in p for p in problems));self.assertTrue(any('ElementTree' in p for p in problems))

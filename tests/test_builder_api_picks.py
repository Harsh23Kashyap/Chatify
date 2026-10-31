import copy,json,unittest,yaml
from chatify import apipicks,appbuilder,buildjobs,schema,theme,prompts,generators
class Picks(unittest.TestCase):
 def test_links_are_registry_only(self):
  data=apipicks.enrich([{'service':'Brave Search','provider_page':'https://evil.invalid','key_url':'https://evil.invalid'}, {'service':'Unknown service','provider_page':'https://evil.invalid'}, {'service':'Not Wikipedia','provider_page':'https://evil.invalid'}])
  self.assertEqual(data[0]['key_url'],'https://api-dashboard.search.brave.com/register');self.assertNotIn('provider_page',data[1]);self.assertNotIn('provider_page',data[2])
 def test_merge_preserves_each_api_helper_without_activating_recommendations(self):
  job={'cfg':copy.deepcopy(schema.DEFAULTS),'parts':{},'brief':'Trip planning'}
  for key,spec in buildjobs.PARTS:
   if key.startswith('config:'):job['parts'][key]=copy.deepcopy(spec['defaults'])
   elif key.startswith('appearance:'):job['parts'][key]={k:('Trip wording' if k.startswith('txt_') else v) for k,v in spec['defaults'].items()}
   elif key.startswith('prompt:'):job['parts'][key]={'text':'Trip planning prompt '+key,'on':True}
   elif key.startswith('helper:'):job['parts'][key]={'brief':'Trip helper','code':generators.code_template(key[7:],'')}
  job['parts']['config:app'].update(id='trip',title='Trip planner',tagline='Trip plans',footer='Review facts',examples=['Plan a trip'])
  job['parts']['api']=[{'name':name+' trip search','service':name,'connector':connector,'reason':'Trip information','setup':'Review setup','caveat':'Not live tested','helper':{'brief':name+' trip helper','code':generators.code_template('search','')}} for name,connector in [('Wikipedia','wikipedia'),('Brave Search','web_search')]]
  raw=buildjobs.BuildJobs()._merge(job)
  self.assertEqual(len(raw['helper_drafts']),4);self.assertEqual(raw['sources'],[]);self.assertEqual(raw['api_suggestions'][1]['key_url'],'https://api-dashboard.search.brave.com/register')
 def test_multiple_helper_schema_and_invalid_code_reported(self):
  extra=appbuilder.validate_extras({'helper_drafts':{'search_api_1':{'brief':'Wikipedia','code':generators.code_template('search','')},'search_api_2':{'brief':'Brave','code':'import socket\ndef search(query, limit=6):\n return []'}}})
  self.assertIsInstance(extra['helper_drafts']['search_api_1']['review_problems'],list);self.assertTrue(extra['helper_drafts']['search_api_2']['review_problems'])

 def test_api_helper_static_failure_rejected_in_build_part(self):
  class Provider:
   def complete(self,messages):return json.dumps([{'name':'Bad fixture','service':service,'what':'This service provides searchable public information to help answer user questions.','reason':'This API helps the trip app supply background information about destinations.','connector':'wikipedia','setup':'Review','caveat':'Offline','helper':{'brief':'Bad','code':'import socket\ndef search(query, limit=6):\n return []'}} for service in ['Wikipedia','Brave Search','Open-Meteo']])
  job={'cancel':False,'calls':0,'provider':Provider(),'cfg':copy.deepcopy(schema.DEFAULTS),'parts':{},'errors':{},'active':set(),'brief':'Trip fixture'}
  with self.assertRaisesRegex(ValueError,'API helper contract failed'):buildjobs.BuildJobs()._draft_part(job,'api',dict(buildjobs.PARTS)['api'])
  self.assertNotIn('api',job['parts'])

 def test_section_api_generation_is_concrete_and_does_not_widen_scope(self):
  cfg=copy.deepcopy(schema.DEFAULTS);cfg['provider'].update(type='openai',model='fixture')
  picks=[{'name':name,'service':name,'what':'This service provides searchable public information for reader questions.','reason':'This service helps the app provide background information about destinations.','connector':'wikipedia','setup':'Review','caveat':'Offline','helper':{'brief':'Wikipedia fixture','code':generators.code_template('search','')}} for name in ['Wikipedia','Brave Search','Open-Meteo']]
  class Provider:
   def complete(self,messages):return json.dumps({'message':'Review API','config':{'api_suggestions':picks}})
  data={'consent':True,'messages':[{'role':'user','content':'Trip app API choices'}],'sections':['api_suggestions']}
  raw=yaml.safe_load(appbuilder.talk(Provider(),cfg,data)['yaml'])
  self.assertEqual(set(raw),{'api_suggestions'});self.assertEqual(raw['api_suggestions'][0]['docs_url'],apipicks.PAGES['wikipedia']['page'])
  picks[0].pop('helper')
  with self.assertRaisesRegex(ValueError,'Missing independent code helper'):appbuilder.talk(Provider(),cfg,data)

class OlderAPICardMetadata(unittest.TestCase):
 def test_known_legacy_name_gets_docs_and_optional_key_route(self):
  from chatify.apipicks import enrich
  wiki,oa=enrich([{'name':'Wikipedia'},{'name':'OpenAlex'}])
  self.assertEqual(wiki['key_required'],False)
  self.assertIn('mediawiki.org',wiki['docs_url'])
  self.assertEqual(oa['key_required'],False)
  self.assertEqual(oa['key_url'],'https://openalex.org/settings/api')
  self.assertEqual(oa['docs_url'],'https://developers.openalex.org/guides/authentication')

 def test_openalex_validated_metadata_keeps_optional_key_route(self):
  item=appbuilder.validate_extras({'api_suggestions':[{'service':'OpenAlex'}]})['api_suggestions'][0]
  self.assertFalse(item['key_required'])
  self.assertEqual(item['key_url'],'https://openalex.org/settings/api')
  self.assertEqual(item['docs_url'],'https://developers.openalex.org/guides/authentication')

"""Source plan contract regressions, not live retrieval/answer proof."""
import copy,json,unittest
from unittest.mock import patch
from chatify import buildjobs,schema
from chatify.connectors.web_search import WebSearch
from chatify.connectors.open_sources import SetupRequired
class Reply:
 def __init__(self,result):self.result=result;self.messages=None
 def complete(self,messages):self.messages=messages;return json.dumps(self.result)
class SelectedSourcePlan(unittest.TestCase):
 def draft(self,selected,result,brief='Please create a website about news stories concerning successful efforts at ending violent conflict'):
  provider=Reply(result);jobs=buildjobs.BuildJobs();job={'id':'unit','owner':'owner','brief':brief,'confirmed_sources':selected,'provider':provider,'cfg':copy.deepcopy(schema.DEFAULTS),'cancel':False,'calls':0,'parts':{},'errors':{}}
  jobs._draft_part(job,'config:sources',dict(buildjobs.PARTS)['config:sources']);return job,provider
 def test_selected_news_connector_is_explicit_and_configured(self):
  source={'id':'web_search','label':'Live web search','type':'web_search','providers':['tavily','exa','firecrawl','parallel']}
  job,p=self.draft(['web_search'],[source]);self.assertEqual(job['parts']['config:sources'],[source]);self.assertIn('selected_source_contracts',p.messages[0]['content'])
 def test_selected_connector_cannot_disappear(self):
  with self.assertRaisesRegex(ValueError,'explicitly selected'):self.draft(['web_search'],[])
 def test_selection_does_not_authorize_endpoint(self):
  with self.assertRaisesRegex(ValueError,'contracts exactly'):self.draft(['web_search'],[{'id':'web_search','label':'Live web search','type':'web_search','url':'https://not-authorized.invalid'}])
 def test_no_selection_keeps_document_upload_empty(self):
  job,_=self.draft([],[],brief='Answer questions from my uploaded reading-room handbook');self.assertEqual(job['parts']['config:sources'],[])
 def test_unselected_connector_still_rejected(self):
  with self.assertRaisesRegex(ValueError,'not named or selected'):self.draft([],[{'id':'web','label':'Web','type':'web_search'}])
 def test_source_plan_does_not_bypass_key_requirement(self):
  with patch('chatify.websearch.has_key',return_value=False),patch('chatify.websearch.search') as search:
   with self.assertRaisesRegex(SetupRequired,'needs an API key'):WebSearch({'id':'web','label':'Web','providers':['tavily','exa','firecrawl','parallel']}).search('peace talks')
   search.assert_not_called()
if __name__=='__main__':unittest.main()

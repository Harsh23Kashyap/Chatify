import urllib.parse
from unittest.mock import patch
from chatify.connectors.open_sources import OpenAlex

def test_questions_do_not_trigger_openalex_wildcard_error():
 seen=[]
 with patch('chatify.secrets.saved',return_value='private'), patch('chatify.connectors.open_sources._get',side_effect=lambda u:seen.append(u) or {'results':[]}):
  OpenAlex({'id':'x','label':'OpenAlex'}).search('What is fiber?')
 assert urllib.parse.parse_qs(urllib.parse.urlparse(seen[0]).query)['search']==['What is fiber']

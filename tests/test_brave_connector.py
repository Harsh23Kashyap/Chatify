import io,json,unittest
from unittest.mock import patch
from chatify import websearch,generators,apipicks
class BraveConnector(unittest.TestCase):
 def test_request_contract_and_normalized_response(self):
  response=io.BytesIO(json.dumps({'web':{'results':[{'title':'Habitat report','description':'Actual source snippet','url':'https://example.org/report'},None]}}).encode())
  with patch.object(websearch,'key_for',return_value='test-not-a-real-key'),patch('urllib.request.urlopen',return_value=response) as send:
   rows=websearch.search('brave','habitat loss',3)
  request=send.call_args.args[0]
  self.assertEqual(request.get_method(),'GET');self.assertIsNone(request.data)
  self.assertEqual(request.get_header('X-subscription-token'),'test-not-a-real-key')
  self.assertIn('q=habitat+loss',request.full_url);self.assertIn('count=3',request.full_url)
  self.assertEqual(rows,[{'title':'Habitat report','text':'Actual source snippet','url':'https://example.org/report'}])
 def test_inference_template_and_selected_provider(self):
  self.assertEqual(generators.infer_search('Use BraveSearch API'),'brave')
  self.assertEqual(generators.infer_search('Use Brave Search API'),'brave')
  self.assertEqual(generators.infer_search('Use Brave or Tavily'),'')
  code=generators.known_search_template('brave');self.assertTrue(generators.review_code('search',code)[0]);self.assertIn('BRAVE_API_KEY',code)
  self.assertEqual(apipicks.enrich([{'service':'Brave Search'}])[0]['connector'],'brave')
 def test_missing_key_does_not_call_network(self):
  with patch.object(websearch,'key_for',return_value=''),patch('urllib.request.urlopen') as send:
   with self.assertRaisesRegex(websearch.SearchError,'No key saved for Brave Search'):websearch.search('brave','habitat')
   send.assert_not_called()

 def test_process_os_error_is_actionable(self):
  code='def clean_query(query):\n    return query\n'
  with patch('subprocess.run',side_effect=OSError('private path omitted')):
   result=generators.test_code('clean_query',code,'habitat')
  self.assertFalse(result['ok']);self.assertFalse(result['ran']);self.assertIn('could not start (OSError)',result['error']);self.assertNotIn('private path',result['error'])

class HelperStartFailures(unittest.TestCase):
 def test_unwritable_temp_folder_is_actionable_without_request(self):
  code='def clean_query(query):\n    return query\n'
  with patch('tempfile.TemporaryDirectory',side_effect=PermissionError('private server path')),patch('subprocess.run') as run:
   result=generators.test_code('clean_query',code,'habitat')
  self.assertFalse(result['ok']);self.assertFalse(result['ran']);self.assertIn('PermissionError',result['error']);self.assertNotIn('private server path',result['error']);run.assert_not_called()

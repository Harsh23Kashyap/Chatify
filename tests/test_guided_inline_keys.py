"""Real HTTP/private key storage, fake values only, no provider transport."""
import urllib.error
from unittest.mock import patch
import test_workspace_api
from chatify import secrets
class GuidedInlineKeysHTTP(test_workspace_api.WorkspaceAPITests):
 def test_private_provider_and_source_updates_are_separate(self):
  old=secrets.STORE;secrets.STORE=secrets.SecretStore(self.tmp.name)
  try:
   with patch('chatify.providers._post') as transport:
    for value in ('OFFLINE-FAKE-FIRST','OFFLINE-FAKE-REPLACEMENT'):
     result=self.call(self.clients[0],'/api/provider/key',{'provider':'openai','key':value})
     self.assertNotIn(value,str(result));self.assertTrue(result['key']['has'])
    source=self.call(self.clients[0],'/api/catalog/key',{'id':'openalex','key':'OFFLINE-SOURCE-FAKE'})
    self.assertTrue(source['has_key']);self.assertNotIn('OFFLINE-SOURCE-FAKE',str(source));transport.assert_not_called()
   self.assertEqual(secrets.saved('openai'),'OFFLINE-FAKE-REPLACEMENT')
   self.assertEqual(secrets.saved('catalog:openalex'),'OFFLINE-SOURCE-FAKE')
   for path,body in [('/api/provider/key',{'provider':'openai','key':'DENIED-FAKE'}),('/api/catalog/key',{'id':'openalex','key':'DENIED-FAKE'})]:
    with self.assertRaises(urllib.error.HTTPError) as denied:self.call(self.clients[1],path,body)
    self.assertIn(denied.exception.code,(403,404))
   self.assertEqual(secrets.saved('openai'),'OFFLINE-FAKE-REPLACEMENT')
  finally:secrets.STORE=old

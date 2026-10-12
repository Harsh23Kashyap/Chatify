import http.client,io,unittest,urllib.error
from unittest.mock import patch
from customchat import providers
class ProviderErrorDetails(unittest.TestCase):
 def test_rejection_codes_plain_reason_without_provider_body(self):
  for code,word in [(400,'rejected'),(401,'refused'),(403,'not allowed'),(404,'not found'),(413,'too large'),(429,'rate limiting')]:
   with self.subTest(code=code):
    e=urllib.error.HTTPError('https://fixture.invalid',code,'fixture',{},io.BytesIO(b'key=fixture-private-token'))
    actual=providers._http_error(e);self.assertIn(word,str(actual));self.assertIn('HTTP '+str(code),str(actual));self.assertNotIn('fixture-private-token',str(actual));self.assertEqual(actual.transient,code in providers.RETRY_CODES)
 def test_network_timeout_disconnect_are_distinct_and_private(self):
  for exception,word in [(TimeoutError('fixture secret'), 'timed out'),(urllib.error.URLError(TimeoutError('fixture secret')),'timed out'),(urllib.error.URLError('fixture-private-token in URL'),'network'),(http.client.IncompleteRead(b'fixture-private-token'),'dropped')]:
   for transport in [providers._post_once,providers._stream_once]:
    with self.subTest(exception=type(exception).__name__,transport=transport.__name__),patch('urllib.request.urlopen',side_effect=exception):
     with self.assertRaises(providers.ProviderError) as raised:
      result=transport('https://fixture.invalid',{}, {},1)
      if transport is providers._stream_once:list(result)
     self.assertIn(word,str(raised.exception));self.assertNotIn('fixture-private-token',str(raised.exception));self.assertNotIn('fixture secret',str(raised.exception))

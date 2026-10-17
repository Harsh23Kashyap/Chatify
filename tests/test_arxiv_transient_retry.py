import io,urllib.error
from unittest.mock import patch
from chatify.connectors.arxiv import Arxiv

def test_retries_transient_http_error():
 xml=b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>https://arxiv.org/abs/test</id><title>Test</title><summary>Text</summary></entry></feed>'
 err=urllib.error.HTTPError('http://export.arxiv.org',503,'temporary',{},None)
 with patch('chatify.connectors.arxiv.urllib.request.urlopen',side_effect=[err,io.BytesIO(xml)]) as call,patch('chatify.connectors.arxiv.time.sleep') as sleep:
  rows=Arxiv({'id':'s','label':'arxiv'}).search('test',2)
 assert len(rows)==1 and call.call_count==2
 sleep.assert_called_once_with(3)

def test_no_retry_permanent_http_error():
 err=urllib.error.HTTPError('http://export.arxiv.org',400,'bad query',{},None)
 with patch('chatify.connectors.arxiv.urllib.request.urlopen',side_effect=err) as call,patch('chatify.connectors.arxiv.time.sleep') as sleep:
  try:Arxiv({'id':'s','label':'arxiv'}).search('test',2)
  except urllib.error.HTTPError:pass
  else:raise AssertionError('must preserve failure')
 assert call.call_count==1 and not sleep.called

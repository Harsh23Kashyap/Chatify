import unittest,unittest.mock as mock,base64,struct
from chatify import buildimages,schema
class Images(unittest.TestCase):
 def test_unsupported_provider(self):self.assertFalse(buildimages.capability(schema.validate({}))['available'])
 @mock.patch('chatify.providers._key',return_value='fixture-not-secret')
 @mock.patch('chatify.providers._get',return_value={'data':[{'id':'gpt-image-1-mini'}]})
 def test_openai_probe(self,get,key):self.assertEqual(buildimages.capability(schema.validate({'provider':{'type':'openai','model':'gpt-4o-mini'}}))['model'],'gpt-image-1-mini')
 @mock.patch('chatify.providers._post')
 @mock.patch('chatify.providers._key',return_value='fixture-not-secret')
 def test_logo_draft(self,key,post):
  raw=b'\x89PNG\r\n\x1a\n'+b'12345678'+struct.pack('>II',1024,1024);post.return_value={'data':[{'b64_json':base64.b64encode(raw).decode()}]};cfg=schema.validate({'provider':{'type':'openai','model':'gpt-4o-mini'}});r=buildimages.generate(cfg,{'provider':'openai','model':'gpt-image-1-mini'},'space logo');self.assertTrue(r.startswith('data:image/png;base64,'));self.assertEqual(post.call_args[0][1]['n'],1);self.assertIn('no gradients of any kind',post.call_args[0][1]['prompt']);self.assertIn('no texture',post.call_args[0][1]['prompt']);self.assertIn('#173f35',post.call_args[0][1]['prompt'])

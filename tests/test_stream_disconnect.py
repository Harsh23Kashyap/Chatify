import unittest,io
from tests.test_core import engine
from customchat.server import make_handler

class Disconnect(unittest.TestCase):
 def test_stream_disconnect_closes_generator_no_second_response(self):
  for exc in (BrokenPipeError,ConnectionResetError,ConnectionAbortedError):
   eng,cfg=engine();closed=[]
   def stream(*a,**kw):
    try:
     yield 'progress',{'label':'Starting'}
     yield 'token','text'
    finally:closed.append(True)
   eng.ask_stream=stream
   H=make_handler(cfg,eng);h=object.__new__(H);h.path='/api/ask-stream';h.headers={};h.client_address=('127.0.0.1',1);h._owner=lambda:'fixture';h._body=lambda:{'question':'test'};h.send_response=lambda n:None;h.send_header=lambda *a:None;h.end_headers=lambda:None
   class Dead:
    def write(self,*a):raise exc('disconnected')
    def flush(self):pass
   h.wfile=Dead();h._guard('POST');self.assertTrue(h.close_connection);self.assertEqual(closed,[True])
 def test_disconnect_while_sending_error_never_escapes(self):
  eng,cfg=engine();H=make_handler(cfg,eng);h=object.__new__(H)
  h._route=lambda method:(_ for _ in ()).throw(ValueError('bad input'))
  h._send=lambda *a:(_ for _ in ()).throw(BrokenPipeError('dead socket'))
  h._guard('POST');self.assertTrue(h.close_connection)

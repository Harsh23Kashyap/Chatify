import contextlib,io,threading,unittest,urllib.error
from unittest.mock import patch
from chatify.connectors import arxiv
ATOM=b'<feed xmlns="http://www.w3.org/2005/Atom"></feed>'
class Clock:
 def __init__(self):self.now=10.;self.waits=[]
 def monotonic(self):return self.now
 def sleep(self,n):self.waits.append(n);self.now+=n
class Cadence(unittest.TestCase):
 def setUp(self):self.clock=Clock();self.starts=[];self.stack=contextlib.ExitStack();self.addCleanup(self.stack.close);self.stack.enter_context(patch.object(arxiv,'_next_request_at',0.));self.stack.enter_context(patch.object(arxiv.time,'monotonic',self.clock.monotonic));self.stack.enter_context(patch.object(arxiv.time,'sleep',self.clock.sleep))
 def response(self,*a,**k):self.starts.append(self.clock.now);return contextlib.closing(io.BytesIO(ATOM))
 def connector(self):return arxiv.Arxiv({'id':'a','label':'arXiv'})
 def test_successive_instances_share_cadence(self):
  with patch.object(arxiv.urllib.request,'urlopen',self.response):self.connector().search('one');self.connector().search('two');self.connector().search('three')
  self.assertEqual(self.starts,[10.,13.,16.])
 def test_slow_success_needs_no_extra_delay(self):
  with patch.object(arxiv.urllib.request,'urlopen',self.response):self.connector().search('one');self.clock.now+=5;self.connector().search('two')
  self.assertEqual(self.starts,[10.,15.]);self.assertEqual(self.clock.waits,[])
 def test_failed_request_still_consumes_interval(self):
  def fail(*a,**k):self.starts.append(self.clock.now);raise urllib.error.HTTPError('x',400,'bad',{},None)
  with patch.object(arxiv.urllib.request,'urlopen',fail),self.assertRaises(urllib.error.HTTPError):self.connector().search('one')
  with patch.object(arxiv.urllib.request,'urlopen',self.response):self.connector().search('two')
  self.assertEqual(self.starts,[10.,13.])
 def test_transient_retries_spaced(self):
  def response(*a,**k):
   if len(self.starts)<2:self.starts.append(self.clock.now);raise urllib.error.URLError('temporary')
   return self.response(*a,**k)
  with patch.object(arxiv.urllib.request,'urlopen',response):self.connector().search('one')
  self.assertEqual(self.starts,[10.,13.,19.])
 def test_one_connection_across_threads(self):
  entered=threading.Event();release=threading.Event();second_started=threading.Event();errors=[]
  @contextlib.contextmanager
  def response(*a,**k):
   if not entered.is_set():entered.set();self.assertTrue(release.wait(2))
   else:second_started.set()
   yield io.BytesIO(ATOM)
  def run():
   try:self.connector().search('query')
   except Exception as e:errors.append(e)
  with patch.object(arxiv.urllib.request,'urlopen',response):
   a=threading.Thread(target=run);b=threading.Thread(target=run);a.start();self.assertTrue(entered.wait(2));b.start();self.assertFalse(second_started.wait(.05));release.set();a.join(2);b.join(2)
  self.assertFalse(a.is_alive());self.assertFalse(b.is_alive());self.assertEqual(errors,[]);self.assertTrue(second_started.is_set())

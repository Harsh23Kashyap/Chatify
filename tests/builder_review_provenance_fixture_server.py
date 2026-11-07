"""Zero-external-call fixture; ordinary HTTP BuildJobs and draft persistence."""
import os,sys,json
from pathlib import Path
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parent)]
from test_buildjobs import Fixture
from chatify import providers,buildimages,server
class Model(Fixture):
 def complete(self,messages):
  if 'Review this complete merged draft' in messages[0]['content']:
   return json.dumps({'issues':['Fixture faithfulness lacks question context.'],'setup_notes':['Verify source access before deployment.'],'ready':False})
  return super().complete(messages)
providers.make=lambda cfg:Model()
providers.list_models=lambda *a,**kw:['fixture']
def no_transport(*a,**kw):raise AssertionError('External provider transport forbidden in fixture')
providers._post=no_transport;providers._get=no_transport
buildimages.capability=lambda *a,**kw:{'available':False,'note':'Fixture: no image call'}
server.serve(os.environ['CHATIFY_FIXTURE_APP'],'127.0.0.1',int(os.environ.get('CHATIFY_FIXTURE_PORT','18997')))

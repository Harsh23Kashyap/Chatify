"""Real local HTTP/BuildJobs recovery path with a mock text provider.
No provider, source API, image or live-account requests are made.
"""
import sys,os,copy
from pathlib import Path
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parent)]
from test_buildjobs import Fixture
from chatify import providers,buildimages,buildjobs,server
providers.make=lambda cfg:Fixture()
buildimages.capability=lambda *a,**kw:{'available':False,'note':'Fixture: no image request'}
original=buildjobs.BuildJobs._draft_part

def legacy_provider_failure(self,job,key,spec):
 if key=='config:provider':
  # Reproduce the deployed 17dd921 optional-address contract failure exactly.
  job['cfg']['provider']['base_url']=None
  self._call(job,'Return a provider connection object matching the current defaults. '+__import__('json').dumps({'area':'provider','defaults':job['cfg']['provider']}))
  raise ValueError('Expected text at .provider.base_url')
 return original(self,job,key,spec)
buildjobs.BuildJobs._draft_part=legacy_provider_failure
server.serve(os.environ['CHATIFY_FIXTURE_APP'],'127.0.0.1',int(os.environ.get('CHATIFY_FIXTURE_PORT','18995')))

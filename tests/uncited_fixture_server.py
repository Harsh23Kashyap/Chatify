"""Local actual HTTP/store fixture, no external model or source calls."""
import os,sys,json,pathlib
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from chatify import providers,server
from chatify.pipeline import Engine
output=json.loads((pathlib.Path(__file__).parent/'fixtures/organic_quake_uncited.json').read_text())['answer']
class P:
 def complete(self,m):return output
 def stream(self,m):yield output[:100];yield output[100:]
providers.make=lambda cfg:P()
Engine.retrieve=lambda self,q,*a,**kw:([],{}) if 'no evidence' in q.lower() else ([{'n':1,'title':'USGS catalog','text':'Magnitude 4.6. Depth 103.682 km.','year':'2026','source':'usgs','url':'fixture:usgs'}],{})
Engine.filter_relevant=lambda self,q,x,*a,**kw:x
Engine._llm_on=lambda *a:False
Engine.followups=lambda *a:[]
server.serve(os.environ['APP'],'127.0.0.1',18996)

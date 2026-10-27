"""Opt-in installed-wheel controls. Pre-download models; no network in inference.
Run from outside the checkout using the installed extra's Python.
"""
import os,json,tempfile,pathlib,socket,traceback,importlib.metadata,sys,argparse
ap=argparse.ArgumentParser()
ap.add_argument('--embedding-model',required=True)
ap.add_argument('--rerank-model',required=True)
ap.add_argument('--output',required=True)
args=ap.parse_args()
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
from chatify.connectors.local_files import LocalFiles
from sentence_transformers import SentenceTransformer,CrossEncoder
embedding,rerank=args.embedding_model,args.rerank_model
models=[{'role':'embedding','path':embedding},{'role':'rerank','path':rerank}]
rows=[];attempts=[]
def no_network(*a,**kw):
 attempts.append(repr(a));raise AssertionError('Network attempted during local inference')
socket.socket.connect=no_network;socket.create_connection=no_network

def check(name,fn):
 try:
  data=fn();rows.append({'name':name,'status':'PASS','evidence':data})
 except Exception as e:rows.append({'name':name,'status':'FAIL','error':str(e),'trace':traceback.format_exc()})
 print(rows[-1],flush=True)

def smoke():
 a=LocalFiles._model(embedding,False); b=LocalFiles._model(rerank,True)
 v=a.encode(['A motorcar travels on the road.','Fresh apples contain dietary fiber.'],normalize_embeddings=True)
 assert v.shape==(2,384),v.shape
 s=b.predict([('What transports passengers on roads?','A motorcar travels on the road.'),('What transports passengers on roads?','Fresh apples contain dietary fiber.')])
 assert float(s[0])>float(s[1]),s
 return {'shape':list(v.shape),'cross_encoder_scores':[float(x) for x in s]}
check('installed absolute-local model loading and inference',smoke)
with tempfile.TemporaryDirectory() as d:
 docs={'car.txt':'A motorcar is a road vehicle used to transport people. It has an engine and four wheels.','fruit.txt':'Apples are edible fruit grown on trees. Apples contain dietary fiber and vitamins.','plant.txt':'Photosynthesis converts sunlight into chemical energy in green plants. Chlorophyll absorbs light.','rome.txt':'The fall of the Western Roman Empire involved invasions, civil wars and economic troubles.'}
 for name,text in docs.items():pathlib.Path(d,name).write_text(text)
 c=LocalFiles({'id':'docs','label':'Docs','path':'.','semantic_model':embedding,'rerank_model':rerank},d)
 def query(q,expected):
  got=c.search(q,k=4)
  assert got and got[0]['id'].startswith(expected),[(x['id'],x['score']) for x in got]
  assert len(got)==4 and len({x['id'] for x in got})==4
  return {'question':q,'expected':expected,'actual_order':[x['id'] for x in got]}
 for q,expected in [('What transports passengers on roads?','car.txt'),('Which food supplies dietary fiber?','fruit.txt'),('How do green plants turn sunlight into energy?','plant.txt'),('Why did the Western Roman Empire collapse?','rome.txt')]:
  check('hybrid retrieval and rerank: '+expected,lambda q=q,e=expected:query(q,e))
 def cached():
  old=c._vectors;revision=c._vector_revision;c.search('fruit',k=2)
  assert old is c._vectors and revision==c._vector_revision
  return {'revision':revision,'vectors_reused':True}
 check('unchanged document vectors cached',cached)
 def refresh():
  old=c.revision;pathlib.Path(d,'ocean.txt').write_text('Whales are marine mammals that breathe air and nurse their young.')
  c.refresh(force=True);assert c.revision!=old
  got=c.search('Which marine mammals breathe air?',k=5)
  assert got[0]['id'].startswith('ocean.txt'),[x['id'] for x in got]
  assert c._vector_revision==c.revision and len(c._vectors)==5
  return {'new_order':[x['id'] for x in got],'vectors':len(c._vectors)}
 check('changed corpus refreshes real embeddings',refresh)
 def filtered():
  got=c.search('What transports passengers on roads?',k=4,documents=['fruit.txt'])
  assert len(got)==1 and got[0]['id'].startswith('fruit.txt'),got
  return {'only_document':got[0]['id']}
 check('document filter stays enforced with actual models',filtered)
check('inference stayed offline',lambda: (_ for _ in ()).throw(AssertionError(attempts)) if attempts else {'socket_connect_attempts':0})
report={'python':sys.version,'installed_chatify':__import__('chatify').__file__,'versions':{x:importlib.metadata.version(x) for x in ['chatify-app','sentence-transformers','torch','transformers','tokenizers','huggingface-hub']},'models':models,'rows':rows}
pathlib.Path(args.output).write_text(json.dumps(report,indent=2))
sys.exit(any(r['status']=='FAIL' for r in rows))

import copy,json,unittest
from chatify.workspace import archive,validate_archive
from chatify.store import Store
from chatify.management import Management
from chatify.pipeline import Engine
from chatify import schema

class ArchiveStatusRoundtripTests(unittest.TestCase):
 def setUp(self):
  self.store=Store(':memory:');self.cfg=schema.validate({'provider':{'type':'mock'},'sources':[]});self.engine=Engine(self.cfg,self.store)
  self.m=Management(self.cfg,self.engine,lambda:{},lambda x:None,self.store.export_all)
 def request(self,path,data=None,owner='owner'):
  return self.m.handle(owner,'/api/workspace/'+path,'GET' if data is None else 'POST',data or {},{})
 def payload(self):
  cid=self.store.new_chat('owner','Keep original')
  for status in ('ok','output_limit','cut','no_key','unreachable',None):
   self.store.add_turn(cid,None,'Question','Question','Exact answer\nincluding warning.',[],[],'standard',model_status=status)
  return json.loads(json.dumps(self.request('archive')))
 def test_real_export_review_restore_preserves_every_status(self):
  payload=self.payload();before=copy.deepcopy(payload)
  r=self.request('archive/review',{'archive':payload});self.assertEqual((r['chats'],r['turns']),(1,6))
  self.assertEqual(self.request('archive/restore',{'ticket':r['ticket'],'confirmed':True})['imported'],1)
  chats=self.store.export_all('owner');self.assertEqual(len(chats),2);self.assertEqual(self.store.chats('other'),[])
  self.assertEqual([t['model_status'] for t in chats[1]['turns']],['ok','output_limit','cut','no_key','unreachable',None])
  self.assertEqual(chats[1]['turns'][1]['answer'],'Exact answer\nincluding warning.');self.assertEqual(payload,before)
  self.assertEqual(chats[0]['turns'],before['chats'][0]['turns'])
 def test_legacy_without_status_stays_accepted(self):
  payload=archive([{'title':'Legacy','turns':[{'question':'q','answer':'a','evidence':[]}]}]);clean=validate_archive(payload)
  self.assertNotIn('model_status',clean[0]['turns'][0]);self.store.import_chats('owner',clean)
  self.assertIsNone(self.store.export_all('owner')[0]['turns'][0]['model_status'])
 def test_invalid_status_rejected_before_review_or_writes(self):
  for status in ('invented',{},[],0,True):
   with self.subTest(status=status):
    payload=self.payload();payload['chats'][0]['turns'][-1]['model_status']=status;before=self.store.export_all('owner')
    with self.assertRaisesRegex(ValueError,'Unknown model status'):self.request('archive/review',{'archive':payload})
    self.assertEqual(self.store.export_all('owner'),before);self.assertEqual(self.m.reviews.items,{})
 def test_other_unknown_turn_field_still_rejected(self):
  payload=self.payload();payload['chats'][0]['turns'][0]['private_token']='fixture'
  with self.assertRaisesRegex(ValueError,'Invalid turn fields'):self.request('archive/review',{'archive':payload})
 def test_review_confirmation_owner_and_replay_guards(self):
  r=self.request('archive/review',{'archive':self.payload()});data={'ticket':r['ticket'],'confirmed':True}
  with self.assertRaises(ValueError):self.request('archive/restore',data,owner='other')
  with self.assertRaises(ValueError):self.request('archive/restore',{'ticket':r['ticket'],'confirmed':False})
  self.request('archive/restore',data)
  with self.assertRaises(ValueError):self.request('archive/restore',data)

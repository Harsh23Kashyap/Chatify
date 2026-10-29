import tempfile,unittest
from chatify.store import Store
from chatify import workspace_default as d
class Defaults(unittest.TestCase):
 def test_owner_isolation_and_stopped_fallback(self):
  with tempfile.TemporaryDirectory() as tmp:
   store=Store(tmp+'/db');rows={'a':[{'id':'one','url':'/nerd-one/','running':True}], 'b':[{'id':'two','url':'/nerd-two/','running':True}]}
   class Loader:
    def list(self,owner=None):return rows[owner]
   loader=Loader()
   d.choose(store,loader,'a','one')
   self.assertEqual(d.destination(store,loader,'a','/'),'/nerd-one/')
   self.assertEqual(d.destination(store,loader,'a','/settings.html'),'/nerd-one/settings.html')
   self.assertEqual(d.destination(store,loader,'a','/build.html'),'')
   self.assertEqual(d.destination(store,loader,'b','/'),'')
   with self.assertRaises(ValueError):d.choose(store,loader,'b','one')
   store.save_state('b',d.STATE,{'id':'two'})
   store.save_state('a',d.STATE,{})
   self.assertEqual(d.destination(store,loader,'a','/'),'')
   self.assertEqual(d.destination(store,loader,'b','/'),'/nerd-two/')
   d.choose(store,loader,'a','one')
   rows['a'][0]['running']=False
   self.assertEqual(d.destination(store,loader,'a','/'),'')

 def test_public_host_requires_resolved_visitor_identity(self):
  self.assertFalse(d.routing_owner('local',True))
  self.assertFalse(d.routing_owner('',True))
  self.assertTrue(d.routing_owner('visitor:'+'a'*32,True))
  self.assertTrue(d.routing_owner('account-123',True))
  self.assertTrue(d.routing_owner('local',False))

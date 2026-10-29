import unittest,json
from chatify import buildjobs,schema,generators
class BuildHelperSafety(unittest.TestCase):
 def test_build_rejects_compilable_but_unsafe_helper(self):
  class P:
   def complete(self,m):return json.dumps({'brief':'inert draft','code':'import socket\ndef search(query, limit=6):\n    return []'})
  jobs=buildjobs.BuildJobs()
  job={'provider':P(),'parts':{},'brief':'Earth science','cfg':schema.DEFAULTS,'retry_corrections':{},'confirmed_sources':[],'cancel':False,'calls':0,'active':set(),'errors':{}}
  # Direct part validation exercises the same product path as Build, no model.
  with self.assertRaisesRegex(ValueError,'Helper safety contract failed'):
   jobs._part(job,'helper:search',{'area':'inert Python helper','kind':'search','contract':generators.KINDS['search']['contract']})

import copy,json,unittest
from chatify.support_verdicts import parse,evaluate,InvalidVerdict
class VerdictProtocol(unittest.TestCase):
 def setUp(self):
  self.c=[{'id':1,'text':'The pause held for 30 hours.'}];self.e=[{'n':1,'text':'Officials reported 30 hours without incident.'}];self.r={'claims':[{'id':1,'text':self.c[0]['text'],'verdict':'supported','kind':'assertion','reason':'Reported duration','evidence_ids':[1],'quotes':[{'evidence_id':1,'text':'30 hours without incident'}]}]}
 def test_valid(self):self.assertEqual(parse(json.dumps(self.r),self.c,self.e),self.r)
 def test_reject_mutations(self):
  for field,val in [('text','The pause failed.'),('id',2),('verdict','OK'),('evidence_ids',[99]),('quotes',[{'evidence_id':1,'text':'two days'}]),('quotes',[]),('reason','')]:
   r=copy.deepcopy(self.r);r['claims'][0][field]=val
   with self.subTest(field=field,val=val):self.assertRaises(InvalidVerdict,parse,json.dumps(r),self.c,self.e)
 def test_absence_requires_all_evidence(self):
  r=copy.deepcopy(self.r);self.c[0]['text']='The supplied passage does not establish aid delivery.';r['claims'][0].update(text=self.c[0]['text'],kind='scoped_absence',quotes=[]);self.assertEqual(parse(json.dumps(r),self.c,self.e),r);self.assertRaises(InvalidVerdict,parse,json.dumps(r),self.c,self.e+[{'n':2,'text':'Another passage.'}])
 def test_failure_unknown_not_pass(self):
  class P:
   def complete(self,m):return 'OK'
  self.assertEqual(evaluate(P(),self.c,self.e)['status'],'unknown')
 def test_explicit_unknown_retained(self):
  r=copy.deepcopy(self.r);r['claims'][0]['verdict']='unknown'
  class P:
   def complete(_,m):return json.dumps(r)
  self.assertEqual(evaluate(P(),self.c,self.e)['status'],'unknown')
 def test_missing_duplicate_extra_claims_rejected(self):
  for rows in [[],self.r['claims']*2]:self.assertRaises(InvalidVerdict,parse,json.dumps({'claims':rows}),self.c,self.e)
 def test_duplicate_input_ids_and_empty_inputs_fail(self):
  for claims,evidence in [([],self.e),(self.c,[]),(self.c*2,self.e),(self.c,self.e*2)]:
   with self.subTest(claims=claims,evidence=evidence):self.assertRaises(InvalidVerdict,parse,json.dumps(self.r),claims,evidence)
 def test_missing_or_changed_claim_order_fails(self):
  r=copy.deepcopy(self.r);r['claims'][0]['id']=True;self.assertRaises(InvalidVerdict,parse,json.dumps(r),self.c,self.e)
  r=copy.deepcopy(self.r);r['claims'][0]['extra']='ignored';self.assertRaises(InvalidVerdict,parse,json.dumps(r),self.c,self.e)
 def test_positive_claim_cannot_be_supported_as_absence(self):
  r=copy.deepcopy(self.r);r['claims'][0].update(kind='scoped_absence',quotes=[]);self.assertRaises(InvalidVerdict,parse,json.dumps(r),self.c,self.e)
 def test_quote_from_wrong_passage_fails(self):
  r=copy.deepcopy(self.r);r['claims'][0]['quotes'][0]['evidence_id']=2;self.assertRaises(InvalidVerdict,parse,json.dumps(r),self.c,self.e+[{'n':2,'text':'Nothing happened.'}])
 def test_provider_exception_unknown(self):
  class P:
   def complete(self,m):raise RuntimeError('offline')
  self.assertEqual(evaluate(P(),self.c,self.e)['status'],'unknown')

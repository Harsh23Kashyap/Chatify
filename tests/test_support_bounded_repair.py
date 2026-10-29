import unittest
from unittest.mock import Mock
from chatify import schema
from chatify.pipeline import Engine
from chatify.store import Store
class Repair(unittest.TestCase):
 def test_only_explicit_unsupported_verdict_is_repaired_once(self):
  e=Engine(schema.validate({}),Store(':memory:'));e.provider=Mock();ev=[{'n':1,'title':'Source','text':'The mountain has a steep profile.'}]
  answer='The mountain has a steep profile and invented ash definitions. [1]'
  fixed='The mountain has a steep profile. [1]';e.provider.complete.return_value=fixed;e.check_support=Mock(return_value='')
  a,v,l,n=e.repair_support(answer,ev,'Describe the mountain','Note: the sources may not fully support this: invented ash definitions')
  self.assertEqual(a,fixed);self.assertEqual(n,'');self.assertEqual(e.provider.complete.call_count,1);e.check_support.assert_called_once_with(fixed,ev)
 def test_invalid_or_unavailable_check_does_not_trigger_repair(self):
  e=Engine(schema.validate({}),Store(':memory:'));e.provider=Mock();ev=[{'n':1,'title':'Source','text':'The mountain has a steep profile.'}]
  n='Note: the support check could not be completed; support was not verified.'
  a,_,_,out=e.repair_support('The mountain has a steep profile. [1]',ev,'Describe',n)
  self.assertEqual(out,n);e.provider.complete.assert_not_called()

import unittest
from chatify.pipeline import Engine

class NumericFields(unittest.TestCase):
 # Minimal excerpt transcribed from captured actual USGS evidence, not model output.
 # The full actual passage and origin are retained in the review evidence bundle.
 def source(self):
  return [{'n':1,'title':'M 4.8 - 36 km WNW of Poso, Indonesia','text':'Origin time (UTC): 2026-11-06T19:07:01.269000+00:00. Magnitude: 4.8 (mb). Longitude: 120.4589, latitude: -1.2393, depth km: 10.'}]
 def test_equal_decimal_depth_representation(self):
  for v in ['10','10.0','10.00']:
   with self.subTest(value=v):self.assertTrue(Engine.ledger('The depth at Poso was '+v+' km. [1]',self.source())[0]['supported'])
 def test_date_component_cannot_support_depth(self):
  row=Engine.ledger('The depth at Poso was 11 km. [1]',self.source())[0]
  self.assertFalse(row['supported'])
 def test_other_numeric_field_cannot_support_depth(self):
  row=Engine.ledger('The depth at Poso was 4.8 km. [1]',self.source())[0]
  self.assertFalse(row['supported'])
 def test_question_numeric_value_cannot_support_depth(self):
  row=Engine.ledger('The depth at Poso was 12 km. [1]',self.source(),'Was its depth 12 km?')[0]
  self.assertFalse(row['supported'])
 def test_unequal_decimal_still_rejected(self):
  self.assertFalse(Engine.ledger('The depth at Poso was 10.01 km. [1]',self.source())[0]['supported'])
 def test_explicit_depth_sign_is_not_lost(self):
  ev=[{'n':1,'title':'Record','text':'depth km: -10. Date: 2026-11-06.'}]
  self.assertFalse(Engine.ledger('The depth was 10 km. [1]',ev)[0]['supported'])
  self.assertTrue(Engine.ledger('The depth was -10.0 km. [1]',ev)[0]['supported'])
 def test_missing_field_does_not_invent_a_contract(self):
  self.assertEqual(Engine.depth_number_conflicts('The depth was 10 km.',[1],[{'n':1,'text':'A 10 km distance.'}]),[])
 def test_uncited_field_cannot_supply_depth(self):
  ev=self.source()+[{'n':2,'title':'Different record','text':'depth km: 11.'}]
  self.assertFalse(Engine.ledger('The depth was 11 km. [1]',ev)[0]['supported'])
 def test_value_remains_bound_to_kilometres_without_conversion(self):
  self.assertEqual(Engine.depth_number_conflicts('The depth was 10000 metres.',[1],self.source()),[])
 def test_intervening_location_distance_is_not_mistaken_for_depth(self):
  row=Engine.ledger('The depth at 36 km from Poso was 10 km. [1]',self.source())[0]
  self.assertTrue(row['supported'])
  self.assertEqual(Engine.depth_number_conflicts('The depth at 36 km from Poso was 10 km.',[1],self.source()),[])
 def test_numeric_normalization_never_rounds(self):
  self.assertEqual(Engine.numbers('0010.000 and 10.0000000000000000000000000000001'),{'10','10.0000000000000000000000000000001'})
if __name__=='__main__':unittest.main()

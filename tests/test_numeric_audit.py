import copy,math,unittest,yaml,tempfile,json,io,zipfile,base64
from pathlib import Path
from customchat import schema,theme,appbuilder
from customchat.nerdload import NerdLoader
class NumericAudit(unittest.TestCase):
 def test_every_config_numeric_bad_values(self):
  fields={'provider.temperature':(0,2,False),'provider.timeout':(1,600,False),'retrieval.top_k':(1,50,True),'retrieval.min_score':(0,1,False),'retrieval.cache_ttl':(0,86400,True),'memory.recent_turns':(1,20,True),'memory.summary_every':(1,50,True),'memory.context_chars':(8000,2000000,True),'server.port':(1,65535,True),'budget.daily_questions':(0,10000000,True),'budget.user_daily_questions':(0,10000000,True),'budget.daily_model_calls':(0,10000000,True),'budget.spend_cap_usd':(0,1000000,False)}
  for field,(lo,hi,integer) in fields.items():
   for value in [-26,float('nan'),float('inf'),hi+1,'',True,'3',lo-1]+([1.5] if integer else []):
    if field=='budget.spend_cap_usd' and value is None:continue
    with self.subTest(field=field,value=value):
     raw=copy.deepcopy(schema.DEFAULTS);area,key=field.split('.');raw[area][key]=value
     self.assertRaises(ValueError,schema.validate,raw);self.assertRaises(ValueError,appbuilder.validate,yaml.safe_dump(raw))
 def test_all_appearance_ranges(self):
  for key,(lo,hi) in theme.RANGES.items():
   for value in [-26,float('nan'),float('inf'),hi+1,'',True,lo-.5]:
    with self.subTest(key=key,value=value):self.assertRaises(ValueError,theme.clean,{key:value})
 def test_yaml_and_zip_import_reject_negative_budget(self):
  with tempfile.TemporaryDirectory() as folder:
   loader=NerdLoader(folder)
   try:
    bad='budget: {daily_questions: -26}'
    self.assertRaises(ValueError,loader.review,'bad.yaml',base64.b64encode(bad.encode()).decode())
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w') as z:z.writestr('app.yaml',bad)
    self.assertRaises(ValueError,loader.review,'bad.zip',base64.b64encode(buf.getvalue()).decode())
   finally:loader.close()
 def test_source_numbers_and_fallback(self):
  for key,hi in [('weight',1000),('refresh_interval',86400),('timeout',600),('max_chars',2000000),('max_docs',100000),('max_bytes',64000000)]:
   for value in [-26,float('nan'),float('inf'),hi+1,'',True]:
    with self.subTest(source=key,value=value):self.assertRaises(ValueError,schema.validate,{'sources':[{'id':'docs','type':'local_files','path':'docs',key:value}]})
  for key in ('temperature','timeout'):
   for value in [-26,float('nan'),float('inf'),10000000,'',True]:
    with self.subTest(fallback=key,value=value):self.assertRaises(ValueError,schema.validate,{'provider':{'fallback':{'type':'mock',key:value}}})

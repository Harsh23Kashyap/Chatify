"""Keyless USGS M4.5+ past-day feed, not an alert or safety service.
https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php
"""
import json,time,datetime,urllib.request,threading,math
URL='https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson'
_LOCK=threading.Lock();_CACHE=None

def parse_feed(data,now=None,k=6):
 now=time.time() if now is None else now
 if not isinstance(data,dict) or not isinstance(data.get('features'),list):raise ValueError('USGS feed format unavailable')
 generated=(data.get('metadata') or {}).get('generated')
 if type(generated) not in (int,float) or not math.isfinite(generated):raise ValueError('USGS feed lacks a timestamp')
 if generated/1000>now+300:raise ValueError('USGS feed timestamp is in the future')
 if now-generated/1000>3600:raise ValueError('USGS feed is too old for a recent-event answer')
 fetched=datetime.datetime.fromtimestamp(generated/1000,datetime.timezone.utc).isoformat()
 out=[]
 for row in data['features']:
  if not isinstance(row,dict):continue
  p=row.get('properties') or {};coords=(row.get('geometry') or {}).get('coordinates') or []
  if p.get('type')!='earthquake' or type(p.get('mag')) not in (int,float) or not math.isfinite(p['mag']) or p['mag']<4.5:continue
  ts=p.get('time');url=p.get('url','')
  if type(ts) not in (int,float) or not math.isfinite(ts) or ts/1000>now+300 or now-ts/1000>86400:continue
  if not isinstance(url,str) or not url.startswith('https://earthquake.usgs.gov/earthquakes/eventpage/'):continue
  when=datetime.datetime.fromtimestamp(ts/1000,datetime.timezone.utc).isoformat()
  title=str(p.get('title') or 'USGS earthquake event')
  text='USGS event '+str(row.get('id',''))+': '+title+'. Origin time (UTC): '+when+'. Magnitude: '+str(p['mag'])+' ('+str(p.get('magType') or 'type not supplied')+'). Review status: '+str(p.get('status') or 'not supplied')+'.'
  if len(coords)>=3 and all(type(x) in (int,float) and math.isfinite(x) for x in coords[:3]) and -180<=coords[0]<=180 and -90<=coords[1]<=90:text+=' Longitude: '+str(coords[0])+', latitude: '+str(coords[1])+', depth km: '+str(coords[2])+'.'
  text+=' Feed generated (UTC): '+fetched+'. Scope: catalog M4.5+ past-day feed, not all earthquakes. Values may be revised. This is not an earthquake prediction, emergency alert, tsunami forecast or safety assessment.'
  out.append({'id':str(row.get('id','')),'title':title,'text':text,'url':url,'authors':['U.S. Geological Survey'],'year':str(datetime.datetime.fromtimestamp(ts/1000,datetime.timezone.utc).year),'venue':'USGS earthquake catalog','source':'usgs-earthquakes','score':1/(len(out)+1)})
 return out[:max(1,min(int(k),10))]

def quakes(query,k=6):
 global _CACHE
 with _LOCK:
  if not _CACHE or time.monotonic()-_CACHE[0]>60:
   req=urllib.request.Request(URL,headers={'User-Agent':'Chatify-QuakeBrief/0.1'})
   with urllib.request.urlopen(req,timeout=15) as response:raw=response.read(1000001)
   if len(raw)>1000000:raise ValueError('USGS feed response is too large')
   _CACHE=(time.monotonic(),json.loads(raw))
  return parse_feed(_CACHE[1],k=k)

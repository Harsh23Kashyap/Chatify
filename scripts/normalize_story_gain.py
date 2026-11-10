"""Explicit maintenance utility. Rebuild only the 30 qualified constant-gain variants.

Run with --apply after inspecting docs/story-gain-normalization-20261110.json.
Original files are never written. No model or web calls.
"""
import pathlib,json,hashlib,subprocess,concurrent.futures,sys
if sys.argv[1:] != ['--apply']: raise SystemExit('Review the audit first; use --apply to regenerate gain variants')
ROOT=pathlib.Path(__file__).resolve().parents[1];MEDIA=ROOT/'chatify/web/media/stories'
AUDIT=json.loads((ROOT/'docs/story-gain-normalization-20261110.json').read_text())['verification']
OUT=ROOT/'story-gain-verification';OUT.mkdir(exist_ok=True)
def cmd(args):return subprocess.run(args,capture_output=True,text=True,check=True)
def measure(p):
 r=cmd(['ffmpeg','-nostdin','-hide_banner','-nostats','-i',str(p),'-vn','-af','loudnorm=I=-24:TP=-2:LRA=20:print_format=json','-f','null','-'])
 return json.loads(r.stderr[r.stderr.rfind('{'):r.stderr.rfind('}')+1])
def video_hash(p):return cmd(['ffmpeg','-nostdin','-v','error','-i',str(p),'-map','0:v:0','-c','copy','-f','streamhash','-hash','sha256','-']).stdout.strip()
def probe(p):return json.loads(cmd(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]).stdout)
def run(r):
 p=MEDIA/r['original'];new=p.with_name(r['normalized'])
 assert hashlib.sha256(p.read_bytes()).hexdigest()==r['original_sha256'],r['id']+' original changed'
 before=measure(p);gain=-24-float(before['input_i'])
 assert float(before['input_tp'])+gain<=-2.5, 'Insufficient peak headroom for gain only'
 for attempt in range(2):
  cmd(['ffmpeg','-nostdin','-y','-v','error','-i',str(p),'-map','0:v:0','-map','0:a:0','-c:v','copy','-af',f'volume={gain:.5f}dB','-c:a','aac','-b:a','128k','-movflags','+faststart',str(new)])
  after=measure(new)
  if abs(float(after['input_i'])+24)<=.25:break
  gain+=-24-float(after['input_i'])
 assert abs(float(after['input_i'])+24)<=.25,(r['id'],after)
 assert float(after['input_tp'])<=-2,(r['id'],after)
 a=probe(p);b=probe(new);h1=video_hash(p);h2=video_hash(new);assert h1==h2
 assert abs(float(a['format']['duration'])-float(b['format']['duration']))<.05
 aa=next(x for x in a['streams'] if x['codec_type']=='audio');ba=next(x for x in b['streams'] if x['codec_type']=='audio')
 assert (aa['sample_rate'],aa['channels'])==(ba['sample_rate'],ba['channels'])
 assert abs(float(aa['duration'])-float(ba['duration']))<=.05
 decoded=cmd(['ffmpeg','-nostdin','-v','error','-i',str(new),'-f','null','-']);assert not decoded.stderr
 result={'id':r['id'],'original':p.name,'normalized':new.name,'original_sha256':r['original_sha256'],'normalized_sha256':hashlib.sha256(new.read_bytes()).hexdigest(),'gain_db':gain,'before':before,'after':after,'video_packet_hash_identical':h1,'original_duration':a['format']['duration'],'normalized_duration':b['format']['duration'],'original_audio_duration':aa['duration'],'normalized_audio_duration':ba['duration'],'sample_rate':ba['sample_rate'],'channels':ba['channels'],'subjective_listening':'NOT REVIEWED'}
 (OUT/(r['id']+'.json')).write_text(json.dumps(result,indent=2));print(r['id'],before['input_i'],'->',after['input_i'],'peak',after['input_tp'],flush=True);return result
eligible=AUDIT
assert len(eligible)==30
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(run,eligible))
(OUT/'verification.json').write_text(json.dumps(results,indent=2));print('VERIFIED',len(results),flush=True)

"""Execute the shipped preview function with a deterministic overlapping clock."""
import pathlib,subprocess,unittest,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
@unittest.skipUnless(shutil.which('node'),'Node required for actual UI function execution')
class PreviewModeTimer(unittest.TestCase):
 def test_new_mode_owns_pulse_and_quiet_mode_clears_it(self):
  source=(ROOT/'chatify/web/settings.js').read_text();start=source.index('let sendTimer = 0, lastPreviewMode = null');end=source.index('\nfunction updateVis()',start)
  script=r'''
const assert=require('node:assert/strict');let now=0,id=0,timers=new Map(),mode='light',quiet=false,classes=new Set();
const frame={classList:{add:s=>classes.add(s),remove:s=>classes.delete(s)},contentWindow:{postMessage(){}}};
const theme={motion:'full'},clone=o=>({...o}),document={documentElement:{dataset:{}}};
const $=selector=>selector==='#pv'?frame:{dataset:{m:mode}};
const matchMedia=()=>({matches:quiet});const location={origin:'http://127.0.0.1'};
const setTimeout=(fn,ms)=>{timers.set(++id,{fn,at:now+ms});return id};const clearTimeout=id=>timers.delete(id);
function advance(ms){now+=ms;for(const [id,t]of [...timers])if(t.at<=now){timers.delete(id);t.fn()}}
'''+source[start:end]+r'''
pushPreview();mode='dark';pushPreview();assert(classes.has('preview-changing'));
advance(80);mode='light';pushPreview();advance(81);
assert(classes.has('preview-changing'),'older mode timer must not retire newer mode pulse');
advance(79);assert(!classes.has('preview-changing'),'new pulse retires after its own160ms');
mode='dark';pushPreview();quiet=true;pushPreview();assert(!classes.has('preview-changing'),'reduced motion immediately clears outstanding pulse');
quiet=false;mode='light';pushPreview();theme.motion='calm';pushPreview();assert(!classes.has('preview-changing'),'Calm immediately clears outstanding pulse');
console.log('PASS overlapping preview clocks and immediate quiet-mode cleanup');
'''
  subprocess.run(['node','-e',script],check=True,capture_output=True,text=True)

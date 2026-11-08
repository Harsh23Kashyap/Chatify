"""Actual local gallery dispatcher plus mock document apps. No external calls."""
import os,sys,pathlib
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from tests.test_gallery import _write_gallery
from chatify import server
folder=pathlib.Path(os.environ['CHATIFY_FIXTURE_ROOT'])
_write_gallery(str(folder))
p=folder/'gallery.yaml';p.write_text(p.read_text().replace('type: openai, model: gpt-4o-mini, api_key_env: OPENAI_API_KEY','type: mock').replace('dir: alpha, slug: alpha,','dir: alpha, slug: alpha, featured: true,'))
server.serve_gallery(str(p),'127.0.0.1',int(os.environ['CHATIFY_FIXTURE_PORT']))

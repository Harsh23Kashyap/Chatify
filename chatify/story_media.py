"""Wheel installs stream selected story binaries; source deployments serve locally."""
import json,re
from pathlib import Path
CANONICAL_HOST='chatify-demo-779c.onrender.com'
CANONICAL_BASE='https://'+CANONICAL_HOST+'/chatify/media/stories/'

def missing_story_url(name,web,request_host=''):
    """Fixed-host redirect only for a manifest-selected, missing video. No proxy."""
    if not re.fullmatch(r'media/stories/[a-z0-9-]+\.mp4',name):return ''
    # A broken canonical deployment must 404, never redirect to itself forever.
    if request_host.lower().split(':',1)[0]==CANONICAL_HOST:return ''
    folder=Path(web)/'media'/'stories'
    filename=name.rsplit('/',1)[-1]
    if (folder/filename).is_file():return ''
    try:stories=json.loads((folder/'manifest.json').read_text())['stories']
    except (OSError,ValueError,KeyError,TypeError):return ''
    for story in stories:
        if not isinstance(story,dict):continue
        ident=story.get('id','')
        if not isinstance(ident,str) or not re.fullmatch(r'[a-z0-9-]+',ident):continue
        if story.get('src')==filename and filename in (ident+'.mp4',ident+'-gain24.mp4'):
            return CANONICAL_BASE+filename
    return ''

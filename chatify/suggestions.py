"""No-inference public app starters and owner-scoped recent questions."""
import re

def clean(rows,limit=4):
    out=[];seen=set()
    for value in rows:
        value=re.sub(r'^\s*[-*\d.)]+\s*','',str(value)).strip().strip('"')
        value=' '.join(value.split())
        if not 12<=len(value)<=110 or not value.endswith('?') or '<' in value or '>' in value:continue
        key=value.casefold()
        if key not in seen:out.append(value);seen.add(key)
        if len(out)>=limit:break
    return out

def starters(engine, owner=None):
    """Ordinary page loads never opt the owner into model inference.

    Use the configured public examples, not old generated caches. Suggestions
    are presentation data; this path must never call a model.
    """
    cfg=engine.cfg
    rows=clean(cfg['app'].get('examples',[]));origin='configured'
    if not rows:
        title=cfg['app'].get('title','this topic')[:65]
        rows=clean(['What can I ask about '+title+'?', 'What topics do the sources cover?'])
        origin='fallback'
    return {'questions':rows,'origin':origin}

def recent(store,owner):
    rows=store.q("SELECT t.question FROM turns t JOIN chats c ON c.id=t.chat WHERE c.owner=? AND c.deleted IS NULL AND t.style NOT LIKE 'deleted:%' ORDER BY t.created DESC LIMIT 24",(owner,))
    return clean([r['question'] for r in rows],3)

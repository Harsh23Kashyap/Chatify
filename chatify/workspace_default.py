"""Owner-scoped default routing to an already owned, running workspace.

Stores only a loader identity, never a caller-supplied redirect URL. The parent
configuration and its data remain intact. Missing/stopped workspaces fail open
back to the parent instead of a redirect loop.
"""
STATE = 'workspace-default'


def choose(store, loader, owner, workspace):
    rows = loader.list(owner=owner)
    row = next((x for x in rows if x['id'] == workspace and x.get('running')), None)
    if not row:
        raise ValueError('Choose one of your running workspaces')
    store.save_state(owner, STATE, {'id': row['id']})
    return row


def current(store, loader, owner):
    try:
        saved = store.get_state(owner, STATE)
    except ValueError:
        return None
    return next((x for x in loader.list(owner=owner)
                 if x['id'] == saved.get('id') and x.get('running')), None)


def destination(store, loader, owner, path):
    if path not in ('/', '/index.html', '/settings.html'):
        return ''
    row = current(store, loader, owner)
    if not row:
        return ''
    return row['url'].rstrip('/') + ('/settings.html' if path == '/settings.html' else '/')


def routing_owner(owner, public=False):
    # Missing visitor cookie on a public host must never become a shared default.
    return bool(owner) and not (public and owner == 'local')

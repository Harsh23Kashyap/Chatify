"""Immutable saved versions of an app's configuration.

Each record snapshots app.yaml, theme.json, prompts.json and code-drafts.json
from the app state folder into versions/<id>/ and appends one entry to
versions.json. Snapshots are never edited in place: a restore writes a chosen
snapshot back to the live files and records that as a new version, so history
only grows and every restore stays reversible.
"""
import hashlib, json, os, re, threading, time, yaml
from pathlib import Path

FILES = ('app.yaml', 'theme.json', 'prompts.json', 'code-drafts.json')
_ID = re.compile(r'v\d{8}-\d{6}-[0-9a-f]{6}')
_lock = threading.RLock()

SECTION_LABELS = [('app', 'app details'), ('provider', 'model'), ('sources', 'sources'),
                  ('prompt', 'main prompt'), ('retrieval', 'retrieval'), ('memory', 'memory'),
                  ('budget', 'budget'), ('auth', 'sign-in'), ('citations', 'citations')]

def _state_folder(cfg):
    # Version history belongs to the workspace, not a movable chat database.
    root = Path(cfg.get('_dir', '.'))
    legacy = (root / cfg['storage']['path']).parent
    if not (root / 'versions.json').exists() and (legacy / 'versions.json').is_file():
        return legacy
    return root

def _content_folder(cfg):
    # Saves can change storage.path before the running server is restarted.
    path = _app_yaml_path(cfg)
    try:
        raw = yaml.safe_load(path.read_text())
        storage = raw['storage']['path']
        folder = (Path(cfg.get('_dir', '.')) / storage).parent.resolve()
        if not folder.is_relative_to(Path(cfg.get('_dir', '.')).resolve()):
            raise ValueError('Version state must stay inside the workspace')
        return folder
    except (OSError, KeyError, TypeError, yaml.YAMLError):
        return (Path(cfg.get('_dir', '.')) / cfg['storage']['path']).parent

def _read(folder, name):
    p = folder / name
    try:
        if p.is_symlink() or not p.is_file():
            return None
        return p.read_bytes()
    except OSError:
        return None

def _write(folder, name, data):
    p = folder / name
    if data is None:
        if p.exists() and not p.is_symlink():
            p.unlink()
        return
    tmp = folder / ('.' + name + '.tmp')
    tmp.write_bytes(data)
    os.replace(tmp, p)

def _app_yaml_path(cfg):
    return Path(cfg.get('_path') or (Path(cfg.get('_dir', '.')) / 'app.yaml'))

def _snapshot(folder, cfg=None):
    content = _content_folder(cfg) if cfg is not None else folder
    snap = {name: _read(content, name) for name in FILES}
    if cfg is not None:
        p = _app_yaml_path(cfg)
        try:
            snap['app.yaml'] = p.read_bytes() if p.is_file() and not p.is_symlink() else None
        except OSError:
            snap['app.yaml'] = None
    return snap

def _write_files(folder, snap, cfg):
    # Restore assets to the destination named by the restored configuration.
    target = yaml.safe_load(snap['app.yaml']) if snap.get('app.yaml') else {}
    content = (Path(cfg.get('_dir', '.')) / target.get('storage', cfg['storage'])['path']).parent.resolve()
    if not content.is_relative_to(Path(cfg.get('_dir', '.')).resolve()):
        raise ValueError('Version state must stay inside the workspace')
    content.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        if name == 'app.yaml':
            if snap[name] is not None:
                p = _app_yaml_path(cfg)
                tmp = p.parent / ('.' + p.name + '.tmp')
                tmp.write_bytes(snap[name])
                os.replace(tmp, p)
        else:
            _write(content, name, snap[name])

def _digest(snap):
    h = hashlib.sha256()
    for name in FILES:
        h.update(name.encode())
        h.update(b'\0')
        h.update(snap.get(name) or b'')
        h.update(b'\0')
    return h.hexdigest()

def _index_path(folder):
    return folder / 'versions.json'

def _load_index(folder):
    try:
        d = json.loads(_index_path(folder).read_text())
        if isinstance(d, dict) and isinstance(d.get('versions'), list):
            return d
    except (OSError, ValueError):
        pass
    return {'schema_version': 1, 'versions': []}

def _save_index(folder, index):
    tmp = folder / '.versions.json.tmp'
    tmp.write_text(json.dumps(index, indent=2))
    os.replace(tmp, _index_path(folder))

def _parse(data):
    import yaml
    try:
        out = yaml.safe_load((data or b'').decode('utf-8'))
        return out if isinstance(out, dict) else {}
    except Exception:
        return {}

def _changes(old_snap, new_snap):
    if old_snap is None:
        return 'First saved version'
    out = []
    old_cfg, new_cfg = _parse(old_snap.get('app.yaml')), _parse(new_snap.get('app.yaml'))
    for key, label in SECTION_LABELS:
        o, n = old_cfg.get(key), new_cfg.get(key)
        if o != n:
            if key == 'sources' and isinstance(o, list) and isinstance(n, list):
                out.append('sources: %d to %d' % (len(o), len(n)))
            else:
                out.append(label)
    if (old_snap.get('theme.json') or b'') != (new_snap.get('theme.json') or b''):
        out.append('look')
    if (old_snap.get('prompts.json') or b'') != (new_snap.get('prompts.json') or b''):
        out.append('answer steps')
    if (old_snap.get('code-drafts.json') or b'') != (new_snap.get('code-drafts.json') or b''):
        out.append('helper drafts')
    return ', '.join(out) if out else 'No configuration changes'

def record(cfg, label, restored_from=None):
    """Snapshot the current saved files. No-ops when nothing changed since the last version."""
    folder = _state_folder(cfg)
    with _lock:
        snap = _snapshot(folder, cfg)
        if all(data is None for data in snap.values()):
            return {'created': False, 'reason': 'No saved app files to version yet.'}
        digest = _digest(snap)
        index = _load_index(folder)
        versions = index['versions']
        if versions and versions[-1].get('config_hash') == digest:
            return {'created': False, 'reason': 'Nothing changed since the last saved version.', 'version': versions[-1]}
        vid = time.strftime('v%Y%m%d-%H%M%S-', time.gmtime()) + hashlib.sha256(os.urandom(8)).hexdigest()[:6]
        parent = versions[-1] if versions else None
        parent_snap = _snapshot(_versions_dir(folder) / parent['id']) if parent else None
        store = _versions_dir(folder)
        store.mkdir(parents=True, exist_ok=True)
        tmp = store / ('.' + vid + '.tmp')
        target = store / vid
        try:
            tmp.mkdir()
            manifest = {'schema_version': 1, 'id': vid, 'created_at': _now(), 'files': {}}
            for name, data in snap.items():
                if data is not None:
                    (tmp / name).write_bytes(data)
                    manifest['files'][name] = len(data)
            (tmp / 'manifest.json').write_text(json.dumps(manifest, indent=2))
            os.replace(tmp, target)
        except OSError:
            if tmp.exists():
                import shutil
                shutil.rmtree(tmp, ignore_errors=True)
            raise ValueError('Could not save this version. The app itself is unchanged.')
        entry = {'id': vid, 'parent_id': parent['id'] if parent else None,
                 'restored_from_id': restored_from, 'created_at': _now(),
                 'label': str(label or 'Saved version')[:120],
                 'change_summary': _changes(parent_snap, snap), 'config_hash': digest}
        versions.append(entry)
        _save_index(folder, index)
        return {'created': True, 'version': _public(entry, digest)}

def _now():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

def _versions_dir(folder):
    return folder / 'versions'

def _public(entry, current_digest):
    return {'id': entry['id'], 'created_at': entry['created_at'], 'label': entry['label'],
            'change_summary': entry.get('change_summary', ''), 'parent_id': entry.get('parent_id'),
            'restored_from_id': entry.get('restored_from_id'),
            'status': 'current' if entry.get('config_hash') == current_digest else 'saved'}

def list_versions(cfg):
    """Newest first; status is honest: 'current' matches the saved app files, 'saved' is older."""
    folder = _state_folder(cfg)
    with _lock:
        index = _load_index(folder)
        current = _digest(_snapshot(folder, cfg))
        out = [_public(v, current) for v in index['versions']]
    out.reverse()
    marked = False
    for v in out:
        if v['status'] == 'current' and not marked:
            marked = True
        elif v['status'] == 'current':
            v['status'] = 'saved'
    return {'versions': out}

def _entry(folder, vid):
    if not _ID.fullmatch(str(vid or '')):
        raise ValueError('Unknown version')
    index = _load_index(folder)
    entry = next((v for v in index['versions'] if v['id'] == vid), None)
    snap_dir = _versions_dir(folder) / str(vid)
    if not entry or not snap_dir.is_dir() or snap_dir.is_symlink():
        raise ValueError('Unknown version')
    return entry, snap_dir

def restore(cfg, vid):
    """Write a saved snapshot back to the live files, then record that as a new version."""
    folder = _state_folder(cfg)
    with _lock:
        entry, snap_dir = _entry(folder, vid)
        snap = {name: _read(snap_dir, name) for name in FILES}
        if _digest(snap) != entry.get('config_hash'):
            raise ValueError('This saved version is damaged and was not restored.')
        old = _snapshot(folder, cfg)
        try:
            _write_files(folder, snap, cfg)
        except OSError:
            try:
                _write_files(folder, old, cfg)
            except OSError:
                pass
            raise ValueError('Could not restore this version; the current app was left unchanged.')
        result = record(cfg, 'Restored: ' + (entry.get('label') or vid), restored_from=vid)
        return {'version': result['version'], 'restored': _public(entry, _digest(_snapshot(folder, cfg)))}

def diff(cfg, vid):
    """Plain-English list of what would change if this version were restored."""
    folder = _state_folder(cfg)
    with _lock:
        entry, snap_dir = _entry(folder, vid)
        snap = {name: _read(snap_dir, name) for name in FILES}
        current = _snapshot(folder, cfg)
    changes = _changes(snap, current)
    return {'id': entry['id'], 'label': entry['label'],
            'changes': 'Current app matches this version' if changes == 'No configuration changes' else changes}

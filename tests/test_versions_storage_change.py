import copy,json,yaml
from chatify import schema,versions

def test_history_survives_storage_parent_change_and_restores_assets(tmp_path):
    cfg=copy.deepcopy(schema.DEFAULTS)
    cfg.update(_dir=str(tmp_path),_path=str(tmp_path/'app.yaml'))
    cfg['storage']['path']='chat.db'
    path=tmp_path/'app.yaml'
    path.write_text(yaml.safe_dump({k:v for k,v in cfg.items() if not k.startswith('_')}))
    (tmp_path/'theme.json').write_text('{"mode":"dark"}')
    first=versions.record(cfg,'First')['version']['id']
    raw=yaml.safe_load(path.read_text());raw['storage']['path']='data/chat.db'
    path.write_text(yaml.safe_dump(raw));(tmp_path/'data').mkdir()
    (tmp_path/'data/theme.json').write_text('{"mode":"light"}')
    second=versions.record(cfg,'Moved')['version']['id']
    cfg['storage']['path']='data/chat.db'
    listed=versions.list_versions(cfg)['versions']
    assert [v['id'] for v in listed]==[second,first]
    assert listed[0]['status']=='current'
    snap=tmp_path/'versions'/second/'theme.json'
    assert json.loads(snap.read_text())['mode']=='light'
    versions.restore(cfg,first)
    assert yaml.safe_load(path.read_text())['storage']['path']=='chat.db'
    assert json.loads((tmp_path/'theme.json').read_text())['mode']=='dark'
    assert len(versions.list_versions(cfg)['versions'])==3

def test_existing_legacy_history_remains_readable(tmp_path):
    cfg=copy.deepcopy(schema.DEFAULTS);cfg.update(_dir=str(tmp_path),_path=str(tmp_path/'app.yaml'))
    cfg['storage']['path']='data/chat.db';(tmp_path/'data').mkdir()
    (tmp_path/'data/versions.json').write_text('{"versions":[]}')
    assert versions._state_folder(cfg)==tmp_path/'data'

def test_restore_route_reads_restored_not_running_asset_folder():
    # The running config can still name the pre-save storage directory.
    from pathlib import Path
    source=(Path(__file__).resolve().parent.parent/'chatify/server.py').read_text()
    section=source.split("if path == '/api/settings/versions/restore'")[1].split("if path in (")[0]
    assert "folder=(Path(clean['_dir'])/clean['storage']['path']).parent" in section
    assert "folder=(Path(cfg.get('_dir','.'))/cfg['storage']['path']).parent" not in section

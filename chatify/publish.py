"""Guided self-hosting package: extends the portable app bundle with a Render
blueprint, a publishing guide and a secret-requirements manifest.

No cloud API is used and no credentials are collected: the package is a zip the
owner reviews, pushes to their own GitHub repository and deploys themselves.
Secrets are listed by environment-variable name only, never values.
"""
import io, json, re, zipfile

GUIDE = """# Publishing your Chatify app

This package turns the app you built into a small repository you can host.
Work through the stages in order. Each stage is checked before the next one
starts, and secrets stay with you: this package contains no keys, accounts or
chat history.

## 1. Prepare this package

- Unzip it. You get app.yaml, your theme and prompts, a render.yaml blueprint
  and this guide.
- Run it once locally to confirm it behaves like the app you built:

      pip install chatify-app
      chatify run app.yaml

- Set the environment variables listed in SECRETS.md before asking real
  questions; without them the app answers in demo mode or skips that source.

## 2. Put it on GitHub

- Create a new private repository in your own GitHub account.
- Commit every file from this package and push.
- Keep the repository private until you have decided who the app is for.

## 3. Deploy on Render

- In the Render dashboard choose New, then Blueprint, and connect your
  repository. Render reads render.yaml from the repo root.
- When Render asks for the environment variables marked sync:false, paste the
  values from your own records. Render stores them; they never appear in the
  repository or in this package.
- Deploy and wait for the first build to finish.

## 4. Open the live app and check it

- Open the URL Render gives the service and ask one real question.
- Confirm the answer cites your evidence sources and the look matches your
  local version. Configuration, runtime, environment and behavior should all
  match what you reviewed before publishing.
- If anything differs, fix it locally, push, and Render redeploys.

## 5. Your own domain (optional, do this last)

- Buy or use a domain you already own, then add it in the Render service
  settings under Custom Domains and follow the DNS instructions shown there.
- Only point a domain you have already purchased at the app after the Render
  URL works. A domain is a name for a working app, not a first step.

## Notes

- Render and model providers bill you directly. Check current prices on their
  sites; nothing here is a quote.
- Local document sources are included in this package only if they were part
  of your app; re-check what you are publishing before making the repository
  public.
- Render's free services sleep when idle; the first request after a quiet
  period can take a minute.
"""

SECRETS_HEAD = """# Secrets this app needs

Listed by environment-variable name only. Values are never stored in this
package, in Chatify exports or in version history. Set them in your own
environment for local runs and in the Render dashboard for the hosted app.
Presence of a variable does not prove the key is valid; the app's source check
and one real question are the verification.
"""

def required_env(cfg):
    from . import source_credentials
    envs = set()
    if cfg['provider'].get('api_key_env'):
        envs.add(cfg['provider']['api_key_env'])
    for source in cfg['sources']:
        if source.get('api_key_env'):
            envs.add(source['api_key_env'])
    for item in source_credentials.status(cfg):
        if item.get('env'):
            envs.add(item['env'])
    return sorted(envs)

def _slug(cfg):
    slug = re.sub(r'[^a-z0-9-]+', '-', str(cfg['app'].get('id') or 'chatify-app').lower()).strip('-')
    return slug or 'chatify-app'

def render_yaml(cfg, envs):
    lines = ['# Render blueprint for %s - review before deploying' % _slug(cfg),
             'services:', '  - type: web', '    name: %s' % _slug(cfg), '    runtime: python',
             '    buildCommand: pip install chatify-app',
             '    startCommand: chatify run app.yaml --host 0.0.0.0 --port $PORT --no-browser',
             '    healthCheckPath: /api/health']
    if envs:
        lines.append('    envVars:')
        for name in envs:
            lines += ['      - key: %s' % name, '        sync: false']
    return '\n'.join(lines) + '\n'

def secrets_md(cfg, envs):
    rows = ['', '## Required environment variables', '']
    if not envs:
        rows.append('None. This app uses no keyed services.')
    for name in envs:
        purpose = 'model provider key' if name == cfg['provider'].get('api_key_env') else 'evidence source credential'
        rows.append('- `%s` - %s' % (name, purpose))
    return SECRETS_HEAD + '\n'.join(rows) + '\n'

def package(saved):
    """ZIP bytes: portable app bundle + render.yaml + PUBLISHING.md + SECRETS.md.
    `saved` is one consistent on-disk config snapshot (with appearance/pipeline_prompts merged in)."""
    from .portable import bundle
    data, manifest = bundle(saved, theme_value=saved.get('appearance'), prompt_value=saved.get('pipeline_prompts'))
    envs = required_env(saved)
    extra = {'render.yaml': render_yaml(saved, envs), 'PUBLISHING.md': GUIDE, 'SECRETS.md': secrets_md(saved, envs)}
    buf = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data)) as src, zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as out:
        for name in src.namelist():
            if name not in extra and not name.endswith('/'):
                out.writestr(name, src.read(name))
        for name, content in extra.items():
            out.writestr(name, content)
    return buf.getvalue(), {'env': envs, 'files': list(manifest['files']) + list(extra)}

def check(saved):
    """Readiness of the saved on-disk app: configuration checks only, live services not contacted."""
    import io, zipfile
    from .portable import bundle
    from .readiness import check as readiness
    data, manifest = bundle(saved, theme_value=saved.get('appearance'), prompt_value=saved.get('pipeline_prompts'))
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        files = {n: archive.read(n) for n in archive.namelist() if not n.endswith("/")}
    return {"readiness": readiness(saved, files), "warnings": manifest["warnings"],
            "excluded": ["API keys and credentials", "Accounts and chat history", "Personal uploads", "Installed local models"]}

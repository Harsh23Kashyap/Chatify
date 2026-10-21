"""Gallery mode: host several Chatify apps on one server, each at its own endpoint.

A gallery config is a YAML file with a top-level "gallery" mapping:

    gallery:
      title: Chatify Gallery
      tagline: Try every app built with Chatify.
      provider:            # optional: forced onto every member app (host key stays server-side)
        type: openai
        model: gpt-4o-mini
        api_key_env: OPENAI_API_KEY
      budget:              # optional: forced daily caps for every member app
        daily_questions: 300
        daily_model_calls: 500
      apps:
        - dir: dietchat    # resolved relative to this file; must contain app.yaml
          slug: dietchat   # the endpoint: /<slug>/

Guardrails applied to every member app in gallery mode: the host provider block
replaces the app's own (so all apps run on the server-side key), per-visitor
isolation is forced on (server.public: true), the per-person quota stays off
(no-auth apps would share it), and the forced daily caps win over the app's own.
"""
import os, re
import yaml

from . import schema

ConfigError = schema.ConfigError

SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,40}$")
RESERVED = {"api", "gallery", "favicon.ico"}


def is_gallery(path):
    try:
        with open(path, encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
    except (OSError, yaml.YAMLError):
        return False
    return isinstance(raw, dict) and isinstance(raw.get("gallery"), dict)


def load(path):
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    g = raw.get("gallery")
    if not isinstance(g, dict):
        raise ConfigError("Not a gallery config: missing top-level 'gallery' mapping")
    base = os.path.dirname(os.path.abspath(path))
    title = str(g.get("title") or "Chatify Gallery")
    tagline = str(g.get("tagline") or "Try every app built with Chatify.")
    provider = g.get("provider")
    if provider is not None and not isinstance(provider, dict):
        raise ConfigError("gallery.provider must be a mapping")
    budget = g.get("budget") or {}
    if not isinstance(budget, dict) or set(budget) - {"daily_questions", "daily_model_calls", "user_daily_questions", "spend_cap_usd"}:
        raise ConfigError("gallery.budget must be a mapping of budget keys")
    apps_raw = g.get("apps")
    if not isinstance(apps_raw, list) or not apps_raw:
        raise ConfigError("gallery.apps must be a non-empty list")
    apps, seen = [], set()
    for entry in apps_raw:
        if not isinstance(entry, dict) or not entry.get("dir") or not entry.get("slug"):
            raise ConfigError("Each gallery app needs a dir and a slug")
        slug = str(entry["slug"]).strip().lower()
        if not SLUG.match(slug) or slug in RESERVED:
            raise ConfigError("Bad gallery slug: %r (lowercase letters, numbers, dashes; not reserved)" % slug)
        if slug in seen:
            raise ConfigError("Duplicate gallery slug: %s" % slug)
        seen.add(slug)
        app_path = os.path.join(base, str(entry["dir"]), "app.yaml")
        cfg = schema.load(app_path)
        cfg["_path"] = os.path.abspath(app_path)
        if provider:
            merged = dict(cfg.get("provider") or {})
            merged.update(provider)
            cfg["provider"] = merged
        cfg.setdefault("server", {})["public"] = True
        cfg["app"]["theme"] = "light"  # one consistent look across the gallery; settings pages have no dark theme
        caps = dict(cfg.get("budget") or {})
        caps.update(budget)
        caps["user_daily_questions"] = 0  # no-auth apps share one quota pool; keep it off
        cfg["budget"] = caps
        apps.append({"slug": slug, "cfg": cfg})
    return {"title": title, "tagline": tagline, "apps": apps, "_path": os.path.abspath(path)}

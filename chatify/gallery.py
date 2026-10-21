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

# Card glyphs for the gallery home page (inner SVG markup, stroke = card accent).
ICONS = {
    "chat": '<path d="M4 5.5h16v10.5H9.5L5 19.5z"/><circle cx="9" cy="10.7" r=".9" fill="currentColor" stroke="none"/><circle cx="12.6" cy="10.7" r=".9" fill="currentColor" stroke="none"/><circle cx="16.2" cy="10.7" r=".9" fill="currentColor" stroke="none"/>',
    "leaf": '<path d="M5.5 18.5C5.5 9.8 12.6 4.5 19.5 4.5c0 7.5-4.4 14-12.5 14"/><path d="M5.5 18.5c2-4.5 5.5-8 9.5-9.8"/>',
    "signal": '<path d="M12 20v-7"/><circle cx="12" cy="10.5" r="1.4"/><path d="M8.2 13.7a5.4 5.4 0 0 1 0-6.4M15.8 7.3a5.4 5.4 0 0 1 0 6.4M5.4 16.5a9.6 9.6 0 0 1 0-12M18.6 4.5a9.6 9.6 0 0 1 0 12"/>',
    "flag": '<path d="M6 21V4.2"/><path d="M6 5h12.2l-2.8 3.8 2.8 3.7H6"/>',
    "news": '<path d="M4 6.5h13v11a1.8 1.8 0 0 0 1.8 1.7H6a2 2 0 0 1-2-2z"/><path d="M17 9.5h2.2a.8.8 0 0 1 .8.8v7.2a1.7 1.7 0 0 1-1.7 1.7"/><path d="M7 9.5h7M7 12.5h7M7 15.5h4.5" opacity=".55"/>',
    "spark": '<path d="M12 3.5 13.8 9 19.5 12 13.8 14.5 12 20.5 10.2 14.5 4.5 12 10.2 9z"/>',
}


ACCENT = re.compile(r"^#[0-9a-fA-F]{6}$")


def _meta(entry):
    icon = str(entry.get("icon") or "spark").strip().lower()
    if icon not in ICONS:
        raise ConfigError("Unknown gallery icon: %r (one of: %s)" % (icon, ", ".join(sorted(ICONS))))
    tags = entry.get("tags") or []
    if not isinstance(tags, list) or len(tags) > 4 or any(not isinstance(t, str) or not t.strip() or len(t) > 24 for t in tags):
        raise ConfigError("gallery app tags must be a list of up to 4 short strings")
    accent = entry.get("accent")
    if accent is not None and not ACCENT.match(str(accent)):
        raise ConfigError("gallery app accent must look like #1a2b3c (card color only; the app keeps its own)")
    return icon, [t.strip() for t in tags], (str(accent) if accent else None)


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
        icon, tags, accent = _meta(entry)
        apps.append({"slug": slug, "cfg": cfg, "icon": icon, "tags": tags, "accent": accent})
    return {"title": title, "tagline": tagline, "apps": apps, "_path": os.path.abspath(path)}

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

# Card art for the gallery home page (inner SVG markup, stroke = card accent).
# Classes used by the gallery stylesheet for micro-animations: .bob (gentle float),
# .sway (rotate around base), .pulse (radiating fade), .tick (heartbeat), .draw (stroke draw).
ICONS = {
    "chat": '<path d="M7 8.5h11a3 3 0 0 1 3 3v4.5a3 3 0 0 1-3 3h-6.5L7 22v-3H7a3 3 0 0 1-3-3v-4.5a3 3 0 0 1 3-3z" transform="translate(-1.5 -3)"/><circle cx="9.4" cy="11.2" r="1" fill="currentColor" stroke="none"/><circle cx="13" cy="11.2" r="1" fill="currentColor" stroke="none"/><circle cx="16.6" cy="11.2" r="1" fill="currentColor" stroke="none"/><path class="bob" d="m18.6 2.2.7 1.9 1.9.7-1.9.7-.7 1.9-.7-1.9-1.9-.7 1.9-.7z"/>',
    "leaf": '<g class="sway"><path d="M5.5 18.5C5.5 9.8 12.6 4.5 19.5 4.5c0 7.5-4.4 14-12.5 14"/><path d="M5.5 18.5c2-4.5 5.5-8 9.5-9.8"/></g><path class="bob" d="m19.2 15.8.5 1.4 1.4.5-1.4.5-.5 1.4-.5-1.4-1.4-.5 1.4-.5z"/>',
    "signal": '<path d="M12 20.5v-6.5"/><circle cx="12" cy="11" r="1.6"/><g class="pulse"><path d="M8.6 14.2a4.8 4.8 0 0 1 0-6.4M15.4 7.8a4.8 4.8 0 0 1 0 6.4"/></g><g class="pulse p2"><path d="M5.8 16.8a8.6 8.6 0 0 1 0-11.6M18.2 5.2a8.6 8.6 0 0 1 0 11.6"/></g>',
    "flag": '<path d="M5.5 21.5v-17"/><g class="sway"><path d="M5.5 4.8c3-1.6 6 1.4 9 0s4-.4 4.5 0v8.6c-.5-.4-1.5-1.4-4.5 0s-6-1.4-9 0"/><path d="M8.8 4.4v8.2M13.4 4.4v8.2" opacity=".45"/></g>',
    "news": '<path d="M4 6.5h13v11a1.8 1.8 0 0 0 1.8 1.7H6a2 2 0 0 1-2-2z"/><path d="M17 9.5h2.2a.8.8 0 0 1 .8.8v7.2a1.7 1.7 0 0 1-1.7 1.7"/><g class="draw" opacity=".6"><path d="M7 9.5h7M7 12.5h7M7 15.5h4.5"/></g>',
    "heart": '<g class="tick"><path d="M12 20s-7.5-4.6-7.5-9.8A4.3 4.3 0 0 1 12 7.6a4.3 4.3 0 0 1 7.5 2.6C19.5 15.4 12 20 12 20z"/></g><path class="draw" d="M6.8 12h2.6l1.2-2.4 1.8 4.6 1.2-2.2h2.4"/>',
    "planet": '<circle cx="12" cy="12" r="5.2"/><path class="sway" d="M4.5 15.5c-1.6.8-2.5 1.7-2 2.5 1 1.6 6.5.8 12-1.8s8.6-6.2 7.7-7.8c-.4-.8-2-.7-4-.2"/><circle class="bob" cx="18.6" cy="5.6" r="1" fill="currentColor" stroke="none"/><circle class="bob" cx="5" cy="5.4" r=".8" fill="currentColor" stroke="none"/>',
    "spark": '<path class="bob" d="M12 3.5 13.8 9 19.5 12 13.8 14.5 12 20.5 10.2 14.5 4.5 12 10.2 9z"/>',
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
        if not isinstance(entry, dict) or not entry.get("slug"):
            raise ConfigError("Each gallery app needs a slug plus a dir (hosted here) or a url (links out)")
        slug = str(entry["slug"]).strip().lower()
        if not SLUG.match(slug) or slug in RESERVED:
            raise ConfigError("Bad gallery slug: %r (lowercase letters, numbers, dashes; not reserved)" % slug)
        if slug in seen:
            raise ConfigError("Duplicate gallery slug: %s" % slug)
        seen.add(slug)
        url = entry.get("url")
        if url is not None:
            url = str(url).strip()
            if not url.startswith("https://"):
                raise ConfigError("gallery app url must be an https link")
            if not entry.get("title"):
                raise ConfigError("A redirect gallery app (url) needs a title for its card")
            icon, tags, accent = _meta(entry)
            apps.append({"slug": slug, "url": url, "title": str(entry["title"]),
                         "tagline": str(entry.get("tagline") or ""), "icon": icon, "tags": tags,
                         "accent": accent})
            continue
        if not entry.get("dir"):
            raise ConfigError("Each gallery app needs a slug plus a dir (hosted here) or a url (links out)")
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

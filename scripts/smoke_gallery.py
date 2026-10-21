#!/usr/bin/env python3
"""Post-deploy smoke test for the hosted gallery: asks every demo app one real
question and fails the run when an app cannot answer from its sources.

Usage: python3 scripts/smoke_gallery.py [base_url] [--external]
Run after EVERY release that ships to the hosted demo. Exit code 1 = something
user-visible is broken; the printed line says which app and why.
"""
import json, re, sys, urllib.request

LOCAL_PROBES = {  # slug -> a question its bundled sources must answer
    "chatify": "How do I change the AI model?",
    "spacechat": "Why is Mars red?",
    "fitchat": "How much exercise should an adult get each week?",
    "formulaone": "What is DRS in Formula 1?",
    "newsnerd": "What is NewsNerd?",
}
EXTERNAL_PROBES = {  # slug -> (absolute URL, question)
    "dietchat": ("https://dietchat.org", "How much protein do adults need each day?"),
    "wirelesschat": ("https://wirelesschat-review.onrender.com", "What is MIMO in wireless communications?"),
}
MID_THOUGHT = re.compile(r"^\s*(additionally|moreover|furthermore|in addition|also|secondly|thirdly|finally|however|but|and|so)\b", re.I)


def ask(base, slug, question, timeout=120):
    url = "%s/%s/api/ask-stream" % (base.rstrip("/"), slug)
    body = json.dumps({"question": question}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    done = None
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        for raw in resp:
            line = raw.decode("utf-8", "replace").strip()
            if not line:
                continue
            try:
                evt = json.loads(line)
            except ValueError:
                continue
            if evt.get("type") == "done":
                done = evt.get("data") or {}
    return done


def check_app(base, slug, question):
    done = ask(base, slug, question)
    if done is None:
        return "no done event (app unreachable or stream failed)"
    errors = done.get("source_errors") or {}
    if errors:
        return "sources unavailable: %s" % errors
    answer = (done.get("answer") or "").strip()
    if not done.get("evidence"):
        return "no evidence found for a question its sources must answer"
    if "could not be reached" in answer:
        return "model call failed (fallback answer)"
    if len(answer) < 120:
        return "answer too short (%d chars): %r" % (len(answer), answer[:80])
    if MID_THOUGHT.match(answer):
        return "answer starts mid-thought: %r" % answer[:60]
    return None


def main():
    base = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "http://127.0.0.1:8080"
    include_external = "--external" in sys.argv
    failures = []
    try:
        with urllib.request.urlopen(base.rstrip("/") + "/api/health", timeout=30) as resp:
            health = json.loads(resp.read())
        if not health.get("ok"):
            failures.append(("gallery", "health not ok: %s" % health))
    except Exception as exc:
        print("FAIL gallery: health check failed: %s" % exc)
        return 1
    probes = dict(LOCAL_PROBES)
    if include_external:
        for slug, (url, q) in EXTERNAL_PROBES.items():
            probes[slug] = (url, q)
    for slug, probe in probes.items():
        if isinstance(probe, tuple):
            ext_base, q = probe
            try:
                problem = check_app(ext_base, slug, q)
            except Exception as exc:
                problem = "request failed: %s" % exc
            label = "%s (external)" % slug
        else:
            try:
                problem = check_app(base, slug, probe)
            except Exception as exc:
                problem = "request failed: %s" % exc
            label = slug
        if problem:
            failures.append((label, problem))
            print("FAIL %s: %s" % (label, problem))
        else:
            print("PASS %s" % label)
    print("%d/%d apps healthy" % (len(probes) - len(failures), len(probes)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

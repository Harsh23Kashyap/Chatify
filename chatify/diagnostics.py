"""Explicit opt-in metadata. Fixed enums/counts only, never content or identifiers."""
import json, logging, os

_OUTCOMES = {
    "question": {"disabled", "accepted", "refused", "provider_error", "no_key", "invalid_contract"},
    "retrieval": {"selected", "scope_denied", "memory_cache", "collected", "gated", "complete"},
    "refresh": {"os_error"},
    "connector": {"disk_cache", "searched", "setup_required", "os_error", "value_error", "error", "complete"},
    "relevance": {"empty_input", "mock", "disabled", "provider_error", "invalid_contract", "none", "selected"},
    "feed": {"fetch_started", "http_error", "oversize", "json_error", "cached", "format_error", "timestamp_invalid", "timestamp_future", "timestamp_stale", "parse_error", "parsed"},
}
_COUNTS = {"source_count", "evidence_count", "error_count", "input_count", "output_count", "feature_count", "denied_count", "unusable_count", "duplicate_count", "below_score_count"}

def retrieval_diagnostic(stage, outcome, **counts):
    # Everything, including validation and formatting, is best-effort. A broken
    # logger must not change results, exceptions, provider calls or safety gates.
    try:
        if os.environ.get("CHATIFY_SUPPORT_DIAGNOSTICS") != "1": return
        if outcome not in _OUTCOMES.get(stage, set()): return
        payload = {"stage": stage, "outcome": outcome}
        payload.update({k:v for k,v in counts.items() if k in _COUNTS and type(v) is int and v >= 0})
        logging.getLogger("chatify.retrieval").warning("retrieval_diagnostic %s", json.dumps(payload, sort_keys=True))
    except Exception:
        pass

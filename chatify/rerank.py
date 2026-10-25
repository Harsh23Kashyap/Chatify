"""Optional local cross-encoder re-ordering of retained evidence.

A small quantized ONNX cross-encoder (cross-encoder/ms-marco-MiniLM-L6-v2,
Apache-2.0, int8 ~23MB) re-scores the passages that retrieval already kept, so the
displayed lead is the passage that best answers the question instead of the one with
the most keyword overlap. This stage ORDERS ONLY: it never drops a passage, so the
lexical gate alone decides recall and honest no-evidence abstention (cross-encoder
scores are not calibrated across queries - measured on frozen user cases
2026-10-25 - so no score can serve as an accept/reject floor).

The stage is fail-open in both directions: without the model directory or the
optional runtime it returns the input order untouched, and any scoring error keeps
the gate's order. Model directory comes from CHATIFY_RERANK_MODEL_DIR; retrieval.rerank
= false in the app config disables it explicitly.
"""
import os

_dir = os.environ.get("CHATIFY_RERANK_MODEL_DIR", "")
_session = None
_tok = None
_inputs = None
_tried = False
_MAXLEN = 256


def _load():
    global _session, _tok, _inputs, _tried
    if _tried:
        return _session is not None
    _tried = True
    try:
        if not _dir or not os.path.isdir(_dir):
            return False
        import onnxruntime as ort  # optional dependency, absent in the dev battery
        from tokenizers import Tokenizer
        model = os.path.join(_dir, "model_quint8_avx2.onnx")
        if not os.path.isfile(model):
            return False
        _tok = Tokenizer.from_file(os.path.join(_dir, "tokenizer.json"))
        _session = ort.InferenceSession(model, providers=["CPUExecutionProvider"])
        _inputs = [i.name for i in _session.get_inputs()]
        return True
    except Exception:
        _session = _tok = _inputs = None
        return False


def available():
    return _load()


def rerank(question, found, enabled=True):
    """Return the retained passages in semantic-relevance order.

    Order only, never a filter; on any problem the original order is returned
    unchanged so retrieval behavior never regresses when the stage is missing
    or slower hardware rejects the quantized ops.
    """
    if not enabled or not found or len(found) < 2 or not _load():
        return found
    try:
        import numpy as np

        def score(e):
            text = (str(e.get("title") or "") + ". " + str(e.get("text") or "")[:1200])[:1500]
            enc = _tok.encode(str(question or ""), text)
            ids, tt, am = enc.ids[:_MAXLEN], enc.type_ids[:_MAXLEN], enc.attention_mask[:_MAXLEN]
            pad = _MAXLEN - len(ids)
            ids += [0] * pad; tt += [0] * pad; am += [0] * pad
            feed = {"input_ids": np.array([ids], dtype=np.int64),
                    "attention_mask": np.array([am], dtype=np.int64)}
            if "token_type_ids" in _inputs:
                feed["token_type_ids"] = np.array([tt], dtype=np.int64)
            return float(_session.run(None, feed)[0][0][0])

        scored = [(score(e), i, e) for i, e in enumerate(found)]
        scored.sort(key=lambda x: (-x[0], x[1]))  # stable: ties keep the gate's order
        return [e for _, _, e in scored]
    except Exception:
        return found

"""Order-only cross-encoder re-order stage (chatify/rerank.py + retrieve() hook)."""
import os
import pytest
from chatify import rerank


def test_fail_open_without_model_dir(monkeypatch):
    monkeypatch.setattr(rerank, "_dir", "", raising=False)
    monkeypatch.setattr(rerank, "_tried", False)
    monkeypatch.setattr(rerank, "_session", None)
    assert rerank.available() is False
    found = [{"title": "a", "text": "x"}, {"title": "b", "text": "y"}]
    assert rerank.rerank("question", found, enabled=True) == found


def test_disabled_flag_and_single_passage_short_circuit():
    found = [{"title": "only", "text": "z"}]
    assert rerank.rerank("question", found, enabled=False) is found
    assert rerank.rerank("question", found, enabled=True) is found
    assert rerank.rerank("question", [], enabled=True) == []


@pytest.mark.skipif(not os.environ.get("CHATIFY_RERANK_MODEL_DIR"),
                    reason="model directory only present in the rerank verification env")
def test_semantic_order_with_real_model(monkeypatch):
    monkeypatch.setattr(rerank, "_tried", False)
    monkeypatch.setattr(rerank, "_session", None)
    assert rerank.available() is True
    q = "What were the primary causes of the fall of the Western Roman Empire?"
    found = [
        {"title": "The Holy Roman Empire", "text": "The Holy Roman Empire was a polity in Central Europe... the empire of the German nation."},
        {"title": "Fall of the Western Roman Empire", "text": "The fall of the Western Roman Empire: invasions, civil wars, economic troubles and overreliance on slave labor weakened Rome."},
    ]
    out = rerank.rerank(q, found, enabled=True)
    assert out[0]["title"] == "Fall of the Western Roman Empire"

# Local cross-encoder for evidence re-ordering

cross-encoder/ms-marco-MiniLM-L6-v2, official ONNX int8 (avx2) export.
License: Apache-2.0 (ungated, verified via HF API 2026-10-25).
Source: https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2 (onnx/ + tokenizer files).
Used by chatify/rerank.py for ORDER-ONLY re-ranking of retained evidence; the app
runs unchanged without these files (fail-open). See issue10-rerank-plan.md.

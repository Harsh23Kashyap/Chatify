# Installed semantic extra: bounded local qualification

October 27, 2026, 14:51 IST. No product change was required by these checks.

- Linux, clean Python 3.12 environment, existing 0.4.32 wheel installed from outside the source checkout with `[semantic]` and the CPU PyTorch index (`uv --torch-backend cpu`). This is not evidence for the default CUDA download size or all Python/platform combinations.
- Actual resolved stack: sentence-transformers 6.2.0, torch 2.14.1+cpu, transformers 5.21.0, tokenizers 0.23.3. Full resolution is in install.log.
- Real pretrained model snapshots were downloaded separately for this check. The product's local-only model loader did not download them. Public sources: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 and https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2 . Exact snapshot commits and original result are in result.json.
- Installed `chatify` loaded from the environment's site-packages. Its local_files.py, schema.py, pipeline.py and rerank.py match the current source by SHA256.
- Nine checks PASS: real absolute-local embedding/cross-encoder loading and inference; four predeclared synthetic question/document controls; vector-cache reuse; corpus-change reindexing; document filter; zero socket-connect attempts during inference. Offline environment flags and a fail-on-connect guard were active. The preserved reusable runner was separately executed successfully after parameterization, not used as a retry of failed rows.

These narrow controls are not independent owner-corpus relevance/recall evaluation, end-answer quality, hosted verification, deployment-ONNX qualification, PyPI installation, or a full cross-version extras matrix. The four documents intentionally have distinct topics and simple paraphrase queries. No live model-provider API, credentials, paid inference, hosted mutation or release was used. Previous failures elsewhere remain unchanged.

## Reproduce

Pre-download the two public snapshots to absolute local directories, then install the wheel and its semantic extra in an isolated environment. Copy `tests/qualification/semantic_installed.py` outside the checkout and run it with that environment's Python:

```sh
cd /tmp
OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 /path/to/env/bin/python semantic_installed.py \
  --embedding-model /absolute/local/embedding-snapshot \
  --rerank-model /absolute/local/cross-encoder-snapshot \
  --output /tmp/semantic-result.json
```

The runner is opt-in, not part of the ordinary no-model offline browser fixture. It does not acquire model weights, access paid providers or silently retry checks. The normal push/PR browser regression remains unchanged. This evidence-only commit uses a skip marker to avoid a redundant complete browser census.

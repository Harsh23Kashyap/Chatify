# Exact-head CI follow-up, 2026-10-27

888783d remains unqualified. Remote Python3.12 unit discovery failed one test of1114 (two skips), and Windows installer failed iteration4/10; the twelve offline browser shards have not all finished as of22:44IST. Raw remote logs retained in sibling remote-888783d.

## Unit isolation

BrandingRetryTests patched threading.Thread on the shared module. BuildJobs and ThreadPoolExecutor use that same module object, so an unrelated executor worker can replace the captured mock's last call with SimpleQueue args. Scope the mock to BuildJobs' module-local threading binding. Same selected-part and retained-part assertions, no product contract change. Targeted Python3.12 launcher+buildjobs53 tests PASS, Python3.10 buildjobs46 PASS. Branding case five consecutive solo PASS. First added probe assertion lacked a Python3.10 getattr default for allow_reuse_port and failed; retained before correction.

## Windows bind

Actual remote error was WinError10013 on HTTP server bind port50053 after plain pick_port probe accepted it. Match the probe to the server's SO_REUSEADDR flags, test ordering and permission-denied fallback. This is a grounded flag mismatch and proposed repair, NOT proof of the Windows failure's full OS-level cause. Windows run required before closure. No assertion removed. Linux shared installer8 scenarios x10 all PASS after current wheel. Monolithic unit discovery was explicitly bounded at105sec and stopped near test_degrade; not PASS and not a fresh qualification total.

## Free real-model exploration

Official Qwen3-0.6B-Q8_0 weights at revision23749fefcc72300e3a2ad315e1317431b06b590a, Apache2.0 metadata, llama.cpp b11811 CPU. No account/key/payment/deployment/env changes. Actual local no-key provider probe generated text. 16k context process failed load;8k starts. Scoped real app draft timed out90s; later120s batch interrupted before result, no success inferred. Real answer using actual previously retrieved PubMed abstracts completed18.55sec but cited only at end and omitted population/limits: unacceptable demo quality. Not full E2E or hosted model qualification. Model process stopped after bounded attempts.

Sources:
- https://huggingface.co/Qwen/Qwen3-0.6B-GGUF
- https://github.com/QwenLM/Qwen3/blob/main/docs/source/run_locally/llama.cpp.md
- https://github.com/ggml-org/llama.cpp/releases/tag/b11811

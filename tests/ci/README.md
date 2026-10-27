# Automatic offline regression

`offline browser regression` runs on every push, pull request and manual dispatch,
including app YAML/question/example changes. `tests` and `installer matrix` remain
separate automatic workflows. A successful browser workflow alone is not a full
release result: check all three workflows for the same commit.

The manifest covers 469 CJS regression scripts and two standalone Python browser
acceptance scripts. Twelve instrumented diagnostic copies and one shared helper
are explicitly excluded with reasons. New unclassified CJS files fail preflight,
not silently disappear. Python `test_*.py` files remain in unittest discovery.
Viewport/motion and behavioral-harness scenario expansions run separately when a
script has such selectors; other scripts retain their own full internal loops.

Twelve standard public Ubuntu jobs execute cases sequentially, each with a fresh
scratch app and server. No shared-state lanes, retries, changed product timers or
weakened assertions. Strict seeded, deterministic brand, mounted-port and trip
fixture routing follow the preserved census map. Native browser zoom runs alone
under Xvfb. Self-spawning palette/acceptance tests own their scratch servers.
The trip fixture is reconstructed/mock-path coverage, not independent real-world
answer validation. Assertions remain in their original source files.

Dependencies: Python3.12.15, Node22.23.3, Playwright-core1.56.1,
Python Playwright1.56.0, axe-core4.14.0, documents extra, runner-installed Chrome,
Xvfb/xdotool/ImageMagick. Chrome version is explicitly printed, not silently
assumed fixed. This ongoing automation is distinct from the historical five-pass
fixed-stack runtime experiment. Future tool or runner drift can fail a check.

Each case logs file/variant/PASS-or-FAIL/exit/duration and original test output.
Any failed case makes its job fail; other cases continue so failures are visible.
No automatic retry turns a failure green. Per-case timeout360s, per-job90minutes.
A cancellation/timeout is not a pass. Job logs hold evidence; no cache/artifact
upload, credentials, production accounts or saved user applications are used.
Fixture children receive only allowlisted environment fields. Downloads and
server scratch files are never uploaded. Workflow token permissions are read-only.

Run locally after installing dependencies:

    python tests/ci/browser_suite.py --list
    PLAYWRIGHT_MODULE=/path/to/playwright-core python tests/ci/browser_suite.py --shard 0 --shards 12

Unit checks for the runner live in tests/test_ci_browser_suite.py. The first live
run must be inspected before claiming this automation passes. A red result is a
failure to investigate, not authority to skip a case. Offline browser and mock
provider tests do not qualify live models, paid providers, real retrieval quality,
production data retention, hosted deployment, every OS/browser or release/video.

# Re-execution environment (post-rebuild 2026-10-26 16:07 IST)
- Box: 2 vCPU, 2 GB RAM (nproc/free 17:07). Load 6.06 during 2-lane slice.
- Fixture: pristine minimal app on 127.0.0.1:8765 (apps/minimal/app.yaml + docs copy),
  booted: PYTHONPATH=/home/sandbox/chatify /tmp/venv310b/bin/python -m chatify run <dir>/app.yaml --host 127.0.0.1 --port 8765
- venv: python 3.10.12 at /tmp/venv310b (requirements.txt installed).
- playwright-core 1.64.1 at /home/sandbox/pw-runner/node_modules; system google-chrome via executablePath.
- axe-core reinstalled at /tmp/cc-ui-tools/node_modules (14 test dependents; absence caused 2 explained harness FAILs).
- slice.sh: 2 lanes, CHATIFY_TEST_URL=http://127.0.0.1:8765, CHATIFY_FIXTURE_YAML=tests/fixtures/builder-complete.yaml.
- detach.py: double-fork+setsid launcher (plain setsid children get reaped at call boundary).
- Pace note: 12-25 min/case under 2-lane saturation; saturation is a likely contributor,
  not proven cause; no concurrency change made without uncontended comparison (main 17:08).

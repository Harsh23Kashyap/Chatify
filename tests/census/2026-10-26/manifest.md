# 469 browser-test census - checkpoint 2026-10-26 08:40 IST

Basis: 469 .cjs files in tests/ at HEAD (7a575df). Split by playwright-import criterion: 462 browser / 7 node (differs from earlier-reported 445/24 under a different criterion; total stable).

## Counts (deduped: latest row per test supersedes earlier attempts)
- Unique completed: 31 PASS (30 clean + 1 PASS-teardown-rerun)
- Product FAILs: 0
- Wrong-fixture attempts (not completed, requeued): 2 (answer-delete-topic -> strict_ui_fixture; appbuilder_full -> builder mock fixture)
- Remaining: 438 of 469 (includes the 2 requeued)

## Harness
node v22.23.3 + playwright-core (/home/sandbox/pw-runner) + /usr/bin/google-chrome. Runner: /home/sandbox/pw-runner/slice.sh (2 lanes, per-test timing). Fixture map: FIXTURE_MAP.md this dir.

## Protocols
- Teardown artifact: held-route TargetClosedError at teardown with passing body -> rerun with --unhandled-rejections=warn; recorded PASS-teardown-rerun.
- Contention: stateful settings/builder tests get sequential uncontended rerun before any FAIL claim.
- Fixture contract: generic apps/minimal mock is valid only for tests whose contract is generic-app UI; STRICT/MOUNTED/BUILDER-MOCK/NODE families per FIXTURE_MAP.md. Prior 31 PASS audit against this map is tracked in the task thread.
- Semantic answer quality is NOT covered by any mock-fixture pass (mock provider).

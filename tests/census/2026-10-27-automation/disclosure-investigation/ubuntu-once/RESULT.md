# Single Ubuntu disclosure diagnostic

- Source: https://github.com/Harsh23Kashyap/Chatify/actions/runs/40478194548
- Head: 112c0a545ade91fed5f6eaeda959336a1d93c1ca. One manual run, no retry.
- Terminal result: SUCCESS, 1m7s total; diagnostic job1m3s.
- Actual runner: Ubuntu24.04.5, Google Chrome155.0.8059.39.
- Original strict disclosure test: 320px/no-preference,39disclosures passed. All39asserted closed matrices were matrix(0.707107,-0.707107,0.707107,0.707107,0,0).
- Native transition and frame timelines captured for the close assertion. Original175ms waits and .001matrix tolerance unchanged. Diagnostic registration changes observation overhead; this is not a contention-equivalent replay of the earlier12-shard failure.
- Historical failure in40467125286 remains UNEXPLAINED: its actual failure matrix and transition timing were not captured. This pass does not prove a fix.
- No product/timer/assertion change, no new full-suite rerun, no private questions/config, no live model calls, no hosting change.
- Existing normal regression retains failure-only actual matrix/animation output. Further speculative repeats are not justified; preserve the strict failure and inspect richer timing evidence if it recurs during normal changes.

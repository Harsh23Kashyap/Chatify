# About motion test lifecycle qualification, October 27

Guard commit35f40b8 ordinary browser run40513881613 failed. Eleven browser shards and syntax/package passed. Shard1 had42PASS/1FAIL; chat_about_off_motion_inventory_browser.cjs failed with route.fetch TargetClosedError while GET /api/theme used /about.html as referer. Original complete shard output is preserved in original-ci-shard1.log.

Source owns async route.fetch/json/fulfill but closed the page without waiting for callbacks. Controlled original-probe adds a delayed, explicitly labelled theme read after the unchanged animation inventory assertions. It produces the same route.fetch TargetClosedError. drained-probe waits for routes with behavior:wait before close, then completes all12 matrix combinations. This demonstrates a test-owned teardown failure mechanism, not proof of the exact CI request's scheduling. No exceptions are suppressed.

Initial delayed-response diagnostic variants also fail: original-delayed/drained-delayed assert before About's data-motion arrives; second-read variants mistakenly awaited CCTheme on About, which has no CCTheme object. These failed experiments are retained and are not passing qualification evidence. setup-missing-playwright.log records a local environment setup miss, separate from product evidence.

Correction changes only the test: wait for expected About data-motion before inventory, then await all route callbacks before page close. All widths, reduced-motion states, modes and computed animation/transition assertions remain intact. Product source unchanged. Five consecutive fixed-solo runs pass. This is bounded offline-fixture harness qualification, not hosted/provider E2E or full-CI success. Original full CI remains failed. No provider calls or deployment performed.

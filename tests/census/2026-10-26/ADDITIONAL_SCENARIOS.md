# Additional scenario queue - 2026-10-27

Requested by Harsh at01:15 IST: keep adding test scenarios. These are additional
coverage requirements, not replacements for the current failed cases. Nothing in
this queue is counted as executed or passed. The current serial qualification
runner retains exclusive browser-test execution until it finishes.

## Keep-current review retirement

- Capture row/host geometry synchronously at natural fade creation and host clear,
  retaining original animate arguments, returned Animation and playback. Record
  timestamps, connected/hidden/inert state and host child count. Establish whether
  the existing cross-round-trip geometry observation crosses the120/160ms boundary.
- Geometry invariant while retirement is actually active: dialog/header/footer and
  outer-page scroll remain unchanged; no whole-dialog movement. Check320/1280px,
  Full/Subtle, device normal/reduced, and Calm/None independently.
- Motion setting changes during retirement: device reduction, Calm/None selection,
  cancellation and natural finish must all clear inert state and retire stale
  review content exactly once. Preserve natural timing, do not pause during flow.
- Duplicate keyboard/pointer reject events while parse is held must not create a
  second parse or dialog. Closing the builder during held parse must not update a
  detached review or revive an obsolete review after reopen.
- Delayed parse failure after retirement must recover editor controls, leave Apply
  unavailable, preserve the revised draft and show a visible error without stale
  validation success or unexpected focus jumps.

## Configuration-state settlement

- Separate required save GET/POST settlement from optional late refresh requests;
  a failed required request must still fail the test and show the product error.
- Assert all held routes release before test teardown. Timeout is a failure, never
  a swallowed cleanup exception. Exercise a deliberately rejected refresh and a
  deliberately unreleased held route as negative controls for the harness.

## Delivery safeguards

- Read-only pre-deploy inventory/export completeness check for saved drafts/apps
  and uploaded-source metadata. A code rollback is not data recovery.
- Do not exercise destructive deployment, deletion or private-content publication
  merely to satisfy a test. Saved-data backup or informed loss approval remains a
  separate gate. Hosted and reconstructed-fixture coverage are reported separately.

Instrumentation prepared (not executed): tests/diagnostics/review_lifecycle_probe.js.
Pass-through animate wrapper returns the original Animation; records declared
frames/timing, natural finish/cancel events, host mutations and geometry samples.
It never pauses/cancels/replays animations or rewrites product timeouts. Its reads
can add observation overhead, so it provides lifecycle evidence, not a speed
benchmark. Original failing tests remain unchanged and preserved.

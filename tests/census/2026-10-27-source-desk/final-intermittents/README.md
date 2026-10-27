# Current gate failures, not waived

7ad38ea shard1 AI activity42/43PASS, shard2 nativezoom45/46PASS. Global gate remains FAILED even if these solo tests pass.

AI activity: five unchanged solo PASS, but delay80ms before route handler registration reproduced stuck activity. UI sets ai-working before request route receives; releasing empty pending-list loses release, so held request remains and networkidle times out later. Synchronize test on actual held request before release; retain every activity assertion. Delayed registration probe PASS after repair; five full320/390/1280 reruns PASS. This is harness synchronization only, no product change.

Native400%zoom: original five consecutive solo PASS plus4xCPU throttle PASS. Further five diagnostic runs PASS with original caret assertion unchanged. Mechanism remains unexplained intermittent, NOT fixed or waived. Add full editor/scroller/selection geometry logging only on assertion failure to diagnose remotely. No assertion changed and no product adjusted to match.

All failed logs retained; full remote gate needed. No deployment/model activity. Last remote shard11 still running at23:19IST.

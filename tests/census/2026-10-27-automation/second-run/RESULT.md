# Second full browser regression: red

Run https://github.com/Harsh23Kashyap/Chatify/actions/runs/40465087933, head9a17697.
All12 actual raw case-output summaries collected: 471 scripts, 500 executions, 499 PASS, 1 FAIL. Eleven browser shards passed; shard0 failed the native media-event cancellation check described in MEMORY_EVENT.md. Unit, installer matrix and syntax/package passed. No retries or discarded failures.

The six first-full-run failing cases now pass in this run, including the original late-deploy test. Its separately captured initialization navigation race is still corrected by the next commit, not waived by this pass. Both follow-up harness corrections have targeted local proofs; the next complete run must establish their integrated result. No hosted deployment, restart or upgrade.

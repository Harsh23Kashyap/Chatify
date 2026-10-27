# Fourth complete regression remains red: new archive harness race

https://github.com/Harsh23Kashyap/Chatify/actions/runs/40470898068 head0629114.
All12 actual summaries collected:471 scripts/500 executions/499PASS/1FAIL. Eleven browser jobs passed; shard2 failed workspace_all_late_reviews_browser.cjs because Private chat archive to restore disappeared. Unit/installer/syntax passed. All five third-run failing cases now pass. Disclosure's historical unexplained failure remains unresolved even though it passes here.

Actual local failure trace reproduces same error twice: Backup synthetic event, then panels.js boot rebuildMenu dispatches Setup because hash stayed#sec-finish. The archive input is removed before setInputFiles. This is the same proven route consistency problem as the earlier late-deploy harness, not an archive review product failure. The correction uses actual manual Backup/Changes/Setup navigation and actual Deploy navigation. Full8scenario320/1280 review200/503 test passes, as does diagnostic forcing the same navigation rebuild after selection. Original delayed-review/newerpanel/noerror/focus assertions and timeouts unchanged. Failed traces retained. No retry or discarded failure.

No hosted deployment/restart/upgrade/release. Complete green verification still pending; disclosure cause investigation continues independently.

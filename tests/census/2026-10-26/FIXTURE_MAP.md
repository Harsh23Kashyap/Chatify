# 469 census fixture map v2 (contract-based, 2026-10-26 08:43)
Classification evidence: per-test source reads for seed strings, builder-draft assertions, mount paths, playwright import — not port heuristics alone. Ports are corroboration.

- STRICT (17): needs tests/strict_ui_fixture.py seeded server (NewsNerd; Sample headlines, Hindi/CJK, navigation, Cedar, multi-chat fixtures). Evidence: default port 8145 (17 tests) of which 12 also reference seed strings literally; 5 (local-actions, mobile_profile, reading-persistence, sidebar_profile_browser, stream-buttons) interact with seeded chats positionally. Plus seed-string matches outside 8145 (unicode-export family overlap) — run any seed-string test against strict fixture.
- BUILDER-MOCK-REVIEW (9): assert deterministic AI draft content. 5 by string contract (appbuilder_full_browser, builder_long_configuration_geometry_browser, builder_mounted_preview_browser, builder_proposed_checkbox_immediate_motion_browser, studio_polish_browser) + 4 by brand-fixture naming (review_capabilities_browser, review_precision_browser, ten_actual_palettes_browser, theme_contrast_settle_browser). Fixture: tests/builder_brand_retry_fixture_server.py. Verify by first run per test: if generic mock draft satisfies assertions, reclassify GENERIC with note.
- MOUNTED (1 confirmed): builder_mounted_preview_browser (goto mount= root + /chatify/). Fixture: apps/gallery.yaml serving root + mounted app. 4 node files contain '/chatify/' as static strings — NOT evidence of mount need.
- NODE (7): no playwright import; likely static integrity checks or self-spawning. chart_integrity, model_shortlist, nav_helpers, settings_search_rank, topic_navigation_integrity, wizard_launch_retry_harness, workspace_review_confirm_harness. Run directly with node; observe.
- GENERIC (~438): everything else; contract = generic-app UI, apps/minimal mock valid. Ask-flow tests assert DOM structure (sources/chips/toast), not answer semantics. Semantic answer quality NOT covered by ANY mock-fixture pass.

Audit of first 31 PASS (08:43): zero references to strict seeds, builder-draft strings, or mount paths in all 31 => contract-generic, valid on apps/minimal. Counts stand: 31 completed / 438 remaining.

Teardown artifact protocol + contention protocol unchanged (see manifest.md).

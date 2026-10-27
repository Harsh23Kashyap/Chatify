# Historical disclosure failure: unresolved, no waiver

Original failing run40467125286, settings_disclosure_cue_audit_browser.cjs320/no-preference, strict closed-chevron-45degree matrix assertion after175ms. Only assertion stack captured, not actual matrix or animation timestamp. Subsequent complete runs40470898068 and40473114290 pass this unchanged assertion. Failure-only matrix/animation diagnostics added in0629114 remain active.

Local attempts, none establish cause:
- Five consecutive same320normal diagnostic full passes; headed full pass.
- Chrome156 single-core CPU-affinity full pass;4xCPU full pass;12xCPU freshness/budget passes.
-60 repeated freshness cycles pass.
- Actual failed CI used Chrome155.0.8059.39, local systemChrome156.0.8078.47. Official ChromeForTesting155.0.8059.39 downloaded using the version manifest. Two same320normal full passes on155 too. This rules out treating156-only passes as environment-equivalent, not all environment differences or a155 defect.

No product change, assertion change, timeout increase, retries or discarded failure. Further broad repeats are not useful proof. Prefer a single targeted CI diagnostic retaining original assertion and recording native transition/frame timeline if another failure occurs. Historical cause remains UNKNOWN even if a targeted run passes.

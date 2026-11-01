# Recipe nutrition comparison candidate, Nov 2

Local qualified defensive candidate, not live-comparison or answer-quality acceptance.

The displayed feta-versus-cheddar example previously searched for both foods as one product name. Narrow explicit comparison syntax now sends two food queries, preserving food qualifiers and ignoring terminal punctuation/emoji. It refuses a one-result budget, a missing comparison side, and products with no nutrient values. Each result is labeled a product-specific example, not typical nutrition for the food.

Configured retrieval exposed a separate hole: its generic query ladder could reintroduce one-sided feta results after the full comparison returned empty. A trusted in-process Python connector may now opt into preserving the original question; only this nutrition function opts in. Other connectors retain their query ladder. This capability is function metadata, not an instruction taken from source responses.

Records with nonnumeric, negative, nonfinite or impossible over-100g per-100g mass values are excluded. Saturated fat greater than fat or sugars greater than carbs are also excluded. Legitimate zero and equal component totals remain. Values are not silently corrected. This is a narrow consistency filter, not nutritional validation or a reliable processed-cheese classifier.

Evidence:
- Existing recorded live response contained processed-cheddar products and saturated fat 10g versus total fat 8g, establishing a real source-integrity counterexample.
- One bounded current direct check at Nov2 00:03 returned feta, then cheddar HTTP503. No combined success, repeated retry, hosted polling or model call.
- Actual configured Engine.retrieve controls use deterministic provider payloads. Exact displayed comparison sends only feta and cheddar, retains both when available, and cannot rescue a missing side through broader queries. Other source query ladders remain unchanged.
- Full clean Python test files: 1401 passed, 1 skipped, 546 subtests. Earlier released counts are not this candidate's verdict.

Open: current live two-food success, hosted selected-route acceptance, processed-food relevance, generalized nutrition reliability and synthesized-answer entailment. No semantic model/prompt experiment retained. No key, paid resource or helper execution.

Adverse followthrough: reject ambiguous nested comparison syntax without provider calls; food qualifiers remain intact. Bounded plugins do not import function metadata in the parent process. Their existing execution route is unchanged. 57 recipe/gallery/connector-recovery/bounded-plugin tests passed; affected full Python group rerun gives 115 passed / 16 subtests, bringing candidate full-file total to 1404 passed / 1 skipped / 546 subtests. No additional live requests made. Numeric strings remain excluded as the pre-existing adapter did not emit them as numbers; missing nutrition cannot satisfy a comparison side. This is intentionally conservative, not a claim of full Open Food Facts schema coverage.

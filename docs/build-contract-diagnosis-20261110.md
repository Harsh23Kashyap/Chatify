# Build contract diagnosis, 10 November 2026

Source baseline: 816d7b5. Actual run failures relayed by the ten-run reviewer used gpt-4o-mini, normal local UI, empty confirmed_sources. The rejected raw provider text was not captured, so identity and reusable-prompt failures cannot be attributed to a model or called false positives.

Two product contracts are repaired here:

- An explicit API-recommendation opt-out can yield an empty recommendation list. The part validator and final merge previously both rejected that valid choice. Empty active-source checkboxes alone are not an opt-out: recommendations for later consideration still require the ordinary three-to-five useful service picks with independently checked inert helpers.
- Recommendations stay unselected unless the owner explicitly selected that connector. The ordinary review UI defaults absent selection flags to checked, so omitting this flag silently changed later-consideration recommendations into proposed active sources. No model-written selection controls owner choice.

The source helper remains an inert disabled adapter when no API is requested, with empty API_URL and guarded request skeleton. It is not installed, does not implement uploaded-document search, and is not a defaulted area. All areas, helper safety checks and final model review remain required. Contradictory explicit opt-out plus selected connectors is rejected before model calls.

Missing app fields are now named in error messages. Summary generation explicitly asks for reusable runtime conversation/history instructions instead of a summary of the app idea. Identity shape, reusable prompt, JSON parsing and helper safety validators were not weakened. This does not establish better mini behavior, a Luna comparison or ten successful real builds.

Tests: 96 targeted deterministic checks pass, including full background-job merge with explicit empty API list and no defaulted areas, inactive recommendations, preserved strict prompt checks, provider isolation, retry, helper safety and review provenance. These fixtures are contract coverage, not actual-model qualification. A fresh real canary and CI are required before release.

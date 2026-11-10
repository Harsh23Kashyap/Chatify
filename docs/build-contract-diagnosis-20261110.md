# Build contract diagnosis, 10 November 2026

Source baseline: 816d7b5. Actual run failures relayed by the ten-run reviewer used gpt-4o-mini, normal local UI, empty confirmed_sources. The rejected raw provider text was not captured, so identity and reusable-prompt failures cannot be attributed to a model or called false positives.

Two product contracts are repaired here:

- An explicit API-recommendation opt-out can yield an empty recommendation list. The part validator and final merge previously both rejected that valid choice. Empty active-source checkboxes alone are not an opt-out: recommendations for later consideration still require the ordinary three-to-five useful service picks with independently checked inert helpers.
- Recommendations stay unselected unless the owner explicitly selected that connector. The ordinary review UI defaults absent selection flags to checked, so omitting this flag silently changed later-consideration recommendations into proposed active sources. No model-written selection controls owner choice.

The source helper remains an inert disabled adapter when no API is requested, with empty API_URL and guarded request skeleton. It is not installed, does not implement uploaded-document search, and is not a defaulted area. All areas, helper safety checks and final model review remain required. Contradictory explicit opt-out plus selected connectors is rejected before model calls.

Missing app fields are now named in error messages. Summary generation explicitly asks for reusable runtime conversation/history instructions instead of a summary of the app idea. Identity shape, reusable prompt, JSON parsing and helper safety validators were not weakened. This does not establish better mini behavior, a Luna comparison or ten successful real builds.

Tests: 96 targeted deterministic checks pass, including full background-job merge with explicit empty API list and no defaulted areas, inactive recommendations, preserved strict prompt checks, provider isolation, retry, helper safety and review provenance. These fixtures are contract coverage, not actual-model qualification. A fresh real canary and CI are required before release.

## Raw standalone canary, 17:43
Two worker-supplied raw replies have premature root closure before the `on` field.
Both are invalid JSON (`Extra data`), with finish_reason=stop. Strict rejection
is correct. No brace repair or validator bypass was added. The prompt now uses
one concrete valid JSON example, states sibling-field shape, and separates
rewrite-only duties from answer/design/upload duties. JSON failure feedback
reports character position and safe structural guidance, never response text.
Retry retains this diagnostic. Three new regressions cover rejection, valid
reusable instructions, and two-root rejection. This is prompt/test work, not
an actual model success claim.

## Child acceptance and host keys, 17:49
The raw generated classifier and rewrite prompts both contain positive upload
request duties before retrieval, contradicting their stage-only duties. Narrow
checks now reject those positive duties (while allowing prohibitions). Runtime
stage I/O was not in the supplied artifact, so the exact runtime refusal stage
remains unverified. This is not proof of end-answer repair.

Build launch and restored-version preview both called bundle(include_keys=True)
even when hosted. Both now gate key transport on not hosted, matching the
existing environment scrub. Sentinel HTTP tests inspect actual reviewed bundle
imports for hosted/local launch. Restore path also has a structural gate test;
full restored-version runtime isolation is not newly proven by that test.
Local reuse is retained and the setup banner explains both paths. setup=1 opens
Manual settings without requiring a section hash. Local Save copy explicitly
states parent configuration changes while existing chats and source files stay.

## V4 generation contract candidate, 17:55
230a9df safely rejected question_check and standalone outputs that copied the
whole product brief into a pre-retrieval stage. Adding more trailing rules did
not stop that pattern. V4 separates prompt generation from app-wide PART_SYSTEM
and omits the generic domain_reference for these two stages. The model receives
the actual brief as topic data and the exact stage contract, with an explicit
scope-extraction rule. No validator was loosened. 175 build* tests pass. The
mock fixture reconstructs its own template solely for harness continuity;
these tests do not establish actual model quality. Paired worker calls pending.

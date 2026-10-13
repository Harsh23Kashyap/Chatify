## 0.1.29 - 2026-10-14

- Fix left-aligned labels and consistent padding across all eight Appearance sections, including mobile layouts.
- Provide documented model suggestions for every provider when live listing is unavailable, clearly marked as not verified for the connected account or server. Keep manual model entry available.
- Retry rejected generic app branding by redrafting App identity only, keeping the other ready drafts.
- Distinguish final-check failure from failed draft areas, show readable full-width error text, and bound retry requests with status reconciliation after a timeout.
- Repair illegal JSON backslash escapes locally without changing helper code or making an extra model call. Reject incomplete drafts rather than inventing content.
- Fix conditional Background fields and upward-opening font menus. Add focused Appearance, range and motion audits.
- Update both generic launch scripts to 0.1.29.

Checks: 759 tests and 483 subtests passed before the release bump. Browser fixture checks cover the new model suggestions, final-check errors, retry timeout and Appearance alignment. No real provider calls were used in these checks. These are tested fixes, not a claim that every item in the independent backlog is complete.

## 0.1.27 - 2026-10-12

- Shorten the shared README and PyPI description, with install/configuration steps and clean app screenshots.
- Simplify shared dropdowns and answer-depth choices, with aligned labels, readable descriptions and viewport-aware placement.
- Fix settings spacing, mobile navigation link heights, scalar control types, toggle alignment and the Simple/Advanced switch.
- Keep model lists tied to the selected provider, preserve typed models, and make empty/error states usable.
- Add Gemini and Claude model-list pagination and base-address normalization; use MiMo's documented api-key header.
- Include clearly labeled, officially documented model suggestions when live listing fails, without claiming account availability.
- Refresh pinned installer versions and add small dropdown/button/panel/answer animations, with reduced-motion opt-out.
- Add Start over after completed builds, keep retained drafts, and confirm before discarding unretained or edited drafts.

## 0.1.26 - 2026-10-12

- Rework Build with AI and Ask AI after an AI-tell audit: remove sparkle glyphs, the eyebrow badge, gradient buttons, uniform step cards, status dots and the dark ornament loader.
- Add rotating realistic example briefs in the describe box: random order, gentle crossfade, paused on focus or typing, one static example under reduced motion.
- Replace the build loader with a calm progress track driven only by real completed-area counts, a soft fill pulse while work runs, and per-part states that settle in gently.
- Ask AI gets a thinking indicator tied to the real request, a gentle answer arrival, plainer copy, list-style local results and rotating example questions with the same pause rules.

## 0.1.25

- Expand the Configuration guide, keep provider icon cards in Simple mode, remove redundant Search and top rules, and place Build with AI in its own action row.
- Use keyboard-friendly custom pickers across the app.
- Show friendly per-part build status, inspectable draft content, remaining final work, and reduced-motion-safe micro animations.
- Preview the actual draft chat, show readable API recommendations and long prompts, and use plain-language review/save summaries with color swatches and image thumbnails.
- Add local saved drafts that survive restart, plus a user checklist with setting jump links. Nothing is applied until validated, saved and restarted.

## 0.1.24 - 2026-10-12

- Replace the flat builder step tabs with connected milestone cards, active forest/citrus treatment, completed checkmarks, navigation-driven connector animation and panel transitions.
- Keep phone Describe/Review/Save labels on one line, full accessible names, clear focus and 44px-plus targets; reduced-motion is static.
- Clean the README/PyPI description into current features and instructions. Remove per-version introductions and historical feature sections, the Installer tests stub, old test campaigns and stale 0.1.5 install wording. Release history remains in this changelog; current safety limits remain in the README.

## 0.1.23 - 2026-10-12

- Redesign Build with AI as an editorial cream/forest app studio, with a compact running view and explicit per-part Queued, Waiting for model, Draft received and Needs retry states.
- Replace the three-dot loader with an animated orbit mark and a progress track driven only by completed build areas. Animate real status changes; reduced-motion keeps every state static.
- Use quiet ochre errors with readable messages, field associations and recovery actions, not alarming red surfaces or shaking.
- Separate saved YAML and Back to draft buttons, keep review actions readable, and tighten the phone layout at 320/390px. Provider/model disclosure, review-before-save and no calls on typing are unchanged.
- Browser state tests use controlled model responses; this design release does not claim new live API or model quality coverage.

## 0.1.22 - 2026-10-12

- Complete background AI build split into isolated settings, appearance, nine prompts, API recommendations and inert helper drafts, followed by merged review.
- Working/done ring, close and reopen, cancel, bounded failed-part retry, and request-only microanimations across AI controls.
- Strict numeric validation on UI, HTTP, YAML and ZIP import paths.
- Deployment search and detailed selected-model plan, plus a prompt for any AI.
- Full portable appearance/prompt/helper restore. Optional sensitive key import/export is explicit; normal exports exclude keys.
- Optional OpenAI/Gemini image-capability detection with safe text-only fallback. Generated logos remain reviewable drafts.

## 0.1.19 - 2026-10-11

- Split paper sheets configuration: quiet controls sheet, wider right-side preview and slim section rail.
- Pinned main tabs and a visible-by-default preview with persistent hide/show.
- Responsive stacked preview on narrow screens and separated preview captions.
- Updated fresh-start commands to select 0.1.19.

## 0.1.18 - 2026-10-11

- Browser-style configuration tabs with contextual sections, phone layout, keyboard focus and hover.
- Useful everyday model/test/follow-up controls, conditional keys and accurate save-state warnings.
- Updated eight-step Configuration guide for current navigation, save scopes and bundle privacy.
- Local regression fixes for exports, conversation navigation, state compatibility and owner isolation.
- Fresh-start scripts select this release rather than the old 0.1.5 package.

# Changelog

## 0.1.16 - 2026-10-09

0.1.16 adds resizable settings columns and the private keys-only NewsNerd starter.

## Workspace layout
- Drag either divider to resize navigation, settings, and the preview or prompt/code editor. Widths stay in this browser. Arrow keys adjust; Home or double-click resets. Minimum widths keep each column usable.
- Hide/show chat preview reclaims the space and remembers the choice. Prompt/code editors remain available.
- Styled scrollbars match the workspace and chat. Compact/mobile layouts retain their existing flow without resize handles.

## Private custom source keys
- Sources and APIs now has private credential controls for native HTTP sources with declared header-to-environment mappings. Save/remove works without restarting or contacting the source; the field clears after saving and only presence is reported.
- Saved keys are bound to the source ID, environment label, and configured URL. Destination changes require a new saved key. Keys stay out of YAML, exports, prompts and status responses.
- Credential-bearing sources require HTTPS, reject redirects and fail before a request when a key is missing. Imported Python connector permissions are unchanged: bounded mode is NOT a security sandbox and does not receive API keys.
- HTTP article mapping handles a single author string and reports rejected or malformed responses instead of treating them as empty news.

## NewsNerd starter
Attached `newsnerd-ready-keys.zip` contains the active native NewsAPI connector, `gpt-4o-mini` provider configuration, all nine filled prompt texts, two filled inert code-helper reference drafts, wording, light/dark colors, retrieval, memory and budgets. No real keys, private saved looks, test-question history or chats are included.

1. Start CustomChat 0.1.16: `uvx --from customchat-app==0.1.16 customchat-app start`
2. Configuration > Load and share Nerds: choose the attached ZIP, review, Load and run, then Edit NewsNerd Ready configuration.
3. Model and key: save your OpenAI key. Sources and APIs > Custom source credentials: save your NewsAPI key.
4. Open the imported app's Chat and ask short keywords such as `AI regulation`.

This is configured for local development/testing, not production. NewsAPI Developer has a 24-hour delay and quota. Hosted OpenAI calls cost money when you ask questions. App question/model-call limits are not a dollar billing meter. Live news/model services were not called in verification; no correctness or live-key-validity claim is made. The preview conversation is a visual sample, not a generated news response.

Sources: https://newsapi.org/docs/authentication ; https://newsapi.org/docs/endpoints/everything ; https://newsapi.org/pricing ; https://developers.openai.com/api/docs/models/gpt-4o-mini


### 0.1.16 verification
- Source: 498 tests, 498 passed, no skips. Fresh installed wheel: 498 tests, 496 passed, 2 optional-dependency skips.
- Package checks, isolated install/demo/alias/conflict acceptance, and source/installed-wheel browser checks passed. Desktop/mobile screenshots inspected.
- Only fake service responses were used; no paid API calls.

## 0.1.15 - 2026-10-09

First release published to both GitHub and PyPI with the accepted configuration
work. 0.1.14 was published on GitHub only; its PyPI publish was cancelled, so
PyPI stayed on 0.1.13. 0.1.15 supersedes 0.1.14 everywhere.

Configuration page:

- Selected prompt and code-helper editors open in a right-side pane on desktop
  and inline on mobile, with compact helper descriptions.
- Source and additional fields save to the app file with revision checks.
  Reload shows the saved values, pending restart is labeled, and export is
  blocked until restart so a ZIP cannot contain stale settings.
- Stale concurrent edits are rejected instead of overwriting newer saves.
- Optional fields show a single "(not filled)" marker that tracks typing,
  clearing, image upload, save and reload.
- Provider fallback gets normal typed controls (enable, provider, model, base
  URL, environment variable name, temperature, timeout) with validation.
  Structured and empty values hydrate and persist; invalid blocks are rejected
  without overwriting the saved file.
- Numeric fields reject empty input instead of silently saving 0, and multiline
  text is preserved exactly.
- Articles-style JSON is rejected with a routing hint to Code helpers > Search
  connector > Match a real response instead of being imported or executed.
- Appearance Save is labeled to its scope, reset stays in the menu, and mobile
  layouts no longer clip the prompt placeholder or generation actions.

Emoji:

- 80 bundled static images (Google Noto Color Emoji, SIL OFL 1.1) render the
  supported picker and demo emoji without network fonts. Custom emoji still use
  native fonts.

Verification:

- 486 tests, 484 pass, 2 optional skips, on the source tree and on a fresh
  installed wheel.
- Independent retest of the exact change composition passed, including helper
  panes, offline emoji, blank-field markers, JSON routing, source save and
  restart-guarded export, fallback controls, and numeric/multiline boundaries.

## 0.1.14 - 2026-10-08

Configuration autofill acceptance: hydrated normal controls for the full app
schema, filled NewsNerd demo workspace, and end-to-end save/reload coverage.
Published on GitHub only.

## 0.1.13 - 2026-10-07

Hydrated normal configuration controls.

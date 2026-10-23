## 0.4.30
- PeaceChat uses ReliefWeb v2 report text with source organizations, dates and citation links. Requires an approved RELIEFWEB_APPNAME environment setting.

## 0.4.27

- The PyPI package now ships the example apps inside both the wheel and the sdist (apps/**: RecipeChat, PeaceChat, Formula One, DietChat, FitChat, SpaceChat, WirelessChat, the hosted Build app and the NewsNerd/DietChat samples, including the Python source adapters like peace_sources.py and recipe_sources.py)
- New `chatify examples` lists the bundled example apps; `chatify example <name>` copies one into a local folder, ready for `chatify run <name>/app.yaml` - runtime state (databases, guide markers, caches) is never copied

## 0.4.14

- Gallery: Chatify is now a featured "Build your own" panel above the grid, with a clear Build with AI action; the six example apps sit below under "Examples built with Chatify"
- Build with AI: leaving the page with unsaved setup work now opens a Chatify-styled Leave dialog instead of the browser's native prompt, and kept drafts no longer trigger it
- Build with AI: removed the "Selected model" note and the "Draft only" notice line; the draft notice only appears when there is something to report
- Build with AI: no more per-build call caps - builds and retries are unlimited within a conservative estimated $500/day spend cap per deployment (persisted across restarts), so a build can never stall at "Build paused" just because a counter ran out
- Build with AI: setup calls now run on gpt-6-luna, OpenAI's cheapest current model tier, when the account offers it (checked live against the provider's model list; otherwise the selected model is used)
- Build with AI reliability: a part that still fails after 8 attempts is filled with safe defaults and flagged for review in step 2, so builds complete instead of pausing forever
## 0.4.13

- Build with AI review follow-ups: the lower twinkle no longer clips the Start building button on desktop (moved to the empty strip below the copy), and every hero animation now pauses while the callout is scrolled offscreen; glint keeps its slow 6.5s sweep.
## 0.4.12

- Build with AI gains its glimmer: a diagonal light glint sweeps the callout on a loop and the title carries a continuous cream shine that glides through the serif letters, on top of the existing aurora drift, border comet, button sheen and sparkles. All of it freezes under reduced motion, no pink or purple anywhere

## 0.4.11

- Build with AI review fixes: the confirm note brightens to cream-green and the aurora's lightest stop deepens so text always reads on phones, sparkles move out of the text into the callout's corners and title gap (only one on mobile) with a softer peak, the traveling border comet thickens to 2px, and the button sheen is lighter with a subtle label lift so Start building stays crisp mid-sweep

## 0.4.10

- Build with AI goes bold within the site theme: the callout is a deep-pine aurora of drifting greens with a cream serif title, a lime comet travels its border on a loop, floating sparkles drift inside, and Start building is lime with a continuous sheen sweep - the feature always draws the eye. No pink, no purple, no glow, and every loop still stops under reduced motion. The focus ring is a crisp lime

## 0.4.9

- Loader polish from review: the progress bar is always filled with a dark band sweeping through it (shimmer visible from the first frame), the boot splash and the transition veil share the same geometry with a 64px mark and the serif Chatify wordmark (Georgia fallback before the webfont lands), and the veil only mounts after 160ms so fast page switches never flash a loader
- Build with AI hero: more air between the sparkle and the title, and on phones the callout trims to two lines - "Describe your app in plain words. AI drafts it, you review and save." - with the confirm note moving under the button
- The Loaded workspace bar loses its dead padding on desktop

## 0.4.8

- Gallery hosting sends cache-revalidation headers on every proxied response, so phones and returning browsers always pick up the latest pages and styles after a deploy instead of serving stale cached copies

## 0.4.7

- Switching screens is never blank: navigating between Chat, Configuration, About, Run locally and the gallery now shows a branded loading veil (bouncing Chatify mark, shimmering progress bar, "Opening Chat...") that covers the network wait, and if the demo host is asleep the message changes to "Waking up the server - the first visit can take up to a minute". A matching compact boot veil covers first paint on cold starts, and sibling pages are prefetched so warm transitions are near-instant
- The Build with AI callout keeps attention gently: its gradient drifts slowly, three small sparkles twinkle at different rhythms alongside the existing title spark and sheen, and Start building pulses a soft glow - all disabled under reduced motion
- Start building's focus ring is now a crisp accent-purple outline instead of a gray frame

## 0.4.6

- Configuration review follow-ups: the duplicate Build with AI button row is gone - the hero callout carries the "easier path" sentence and its Start building button is now the single primary action, Saved drafts becomes a quiet underlined link, and Ask AI next to Find a setting is an outline secondary button
- The gap under the Loaded workspace bar is tidied
- Mobile navigation is a deliberate 3-column grid instead of five tabs plus an orphaned Replay guide row, and the mobile header is a touch shorter so chat headings and the input stay clear of the quick tour
- The Build with AI sheen now sweeps behind the text and button, so it reads as a highlight instead of a streak over them

## 0.4.5

- Mobile navigation wraps: the tab bar no longer clips "Replay" on phones - tabs flow onto their own row under the brand instead of being cut off at a hard edge
- Run locally page: the install command box is readable again (light text on its dark panel instead of a washed-out pill), long commands wrap cleanly instead of scrolling off, and the copy steps no longer overflow on small screens
- Configuration greets you with a Build with AI hero: a soft indigo-to-mint callout under the Simple/Advanced toggle with a gentle continuous sparkle (disabled under reduced motion) and a Start building button that opens the existing builder - no model call until you ask
- Gallery: NewsNerd's wash moves toward olive so it no longer reads as Formula One's terracotta, the eyebrow dash matches its green text, and the mobile trust-chip row fades visibly at its right edge

## 0.4.4

- Gallery gets its color back without the top band: each card carries a soft per-app wash that fades to white, icon tiles and tag chips sit deeper in their accent, hover shadows pick up the card's hue, and the hero turns colorful too - indigo, green and magenta trust chips and an indigo-to-magenta eyebrow rule. Text contrast and the light theme are unchanged

## 0.4.3

- Gallery card follow-ups from review: the accent name dash grows to 30px so neighbouring hues (indigo, purple, magenta) read apart, the hover outline strengthens so bronze and teal stay visible on cream, cards get a real tap state on touch (accent outline, dash stretch, icon tilt), and the mobile chip row fades harder at its right edge

## 0.4.2

- Gallery cards drop the colored top band: each card's accent now shows as a short dash under the app name that stretches on hover, paired with an accent-tinted border on hover - the icon tile, tag chips, and arrow keep their accent treatment

## 0.4.1

- Gallery review polish: the About tile spans the free columns of the last row and carries an "informational only, not medical advice" line, FitChat's accent moves to magenta so it no longer reads as Formula One's terracotta, and the mobile trust chips fade at the scroll edge

## 0.4.0

- Gallery apps can now be redirects: an entry with a url instead of a dir makes /<slug>/ send visitors to that site and its card link straight out, so systems with their own homes (like DietChat on dietchat.org) no longer run twice on the host key. /api/health lists hosted apps and redirects separately
- Gallery cards get proper custom artwork: larger illustrated SVG icons per app (chat bubbles with a sparkle, a swaying leaf, a pulsing antenna, a waving flag, a printing newspaper, a heartbeat, a ringed planet) with subtle hover micro-animations and a staggered pop on entrance
- More gallery motion: the eyebrow rule draws in, trust chips stagger, the dot texture drifts slowly, icons draw and pulse - all skipped for visitors who prefer reduced motion
- The card top accent bar is now an inset shadow that follows the card's rounded corners exactly (it could bleed past the edge on phones), and mobile cards sit further apart
- Two new bundled apps: FitChat (exercise answers from public US health guidance) and SpaceChat (space answers from attributed public reference texts)

## 0.3.3

- Gallery review pass: the hero is shorter so the app cards start above the fold, the title no longer orphans a word, card arrows are always visible, tag text is darkened for contrast, the Chatify card is indigo so it no longer reads as DietChat's green, the About tile is a solid card instead of a dashed placeholder, and the duplicated app count and repeated privacy line are gone
- Error pages carry the Chatify brand mark, use the same icon weight as the gallery, space their buttons evenly, and the 404 copy no longer orphans a word

## 0.3.2

- The gallery home page is redesigned: a real hero with the gallery's promise and trust chips, richer app cards (per-app icon, accent color, tag chips, hover lift with a corner arrow, staggered entrance), an "About these demos" tile that fills out the grid, and a footer. It reads cleanly on phones too
- Gallery configs can set each card's icon, tags and accent color (icon, tags, accent on each app entry); the apps themselves keep their own branding
- Error pages always render in the product's light theme with the gallery's typography, so they match the gallery and the member apps

## 0.3.1

- Gallery member apps render in the light theme, so the gallery and every app share one consistent look

## 0.3.0

- Moving between pages now animates: a short fade-and-rise on the way out and in, instead of a hard jump. It is skipped entirely for visitors who prefer reduced motion, and it never touches first loads, external links, new tabs, or same-page anchors
- Designed pages for sign-in needed (401), not allowed (403), page not found (404), file too big (413), too many requests (429), server error (500), and waking up (503), each with its own animated artwork matching the rest of the app
- Browsers that hit the sign-in wall now get the designed 401 page instead of raw JSON
- Gallery mode: one server can now host many apps, each at its own endpoint (/dietchat/, /wirelesschat/, ...), with a designed gallery home page listing them all. A gallery config can force the host provider, daily caps and per-visitor isolation onto every member app, so a public host keeps its key server-side and shared across visitors safely. Member apps render in the light theme so the gallery and every app share one look

## 0.2.9

- Add a demo video to the README

## 0.2.7

- Chat names in the sidebar use their full width again instead of truncating to a few characters; pin, rename and delete actions overlay the end of the row on hover or focus, with the name fading underneath
- A failed question now shows a single error message with a Retry button instead of the same message in two places at once

## 0.2.6

- Answers use the full reading column on desktop instead of shrinking to their shortest line
- Composer footer no longer repeats itself: one sources-and-citations line, one disclaimer
- The no-evidence state is a small muted note with a small icon instead of a large heading
- Scroll-to-latest button no longer floats over the welcome screen; it only appears inside chats
- Repaired four more stale strict UI tests (answer undo, view routing, multi-topic cancel, icon targets) and the NewsNerd sample config

## 0.2.5

- Fix the version shown by `chatify --version`, which still read 0.2.3 in the 0.2.4 build, and add a test so the package version, project metadata and installer release can never drift apart again

## 0.2.4

- Composer actions swap by context: dictate button when the box is empty, send once you type (with a speech-capable browser), send always present while an answer streams
- Controls announce their current state: the source scope button and every custom dropdown now speak their value (for example, "Answer depth: Standard")
- Keyboard shortcuts are exposed to assistive technology with aria-keyshortcuts (send, previous/next question, chat search)
- Question box accessible name is now a full instruction; a sources-and-citations line joins the composer footer
- Answers now render fenced code blocks, each with its own Copy code button
- Repaired stale strict UI tests (stream stop/retry, chat lifecycle, deleted chat topics) to match the current toast and sidebar behaviour

## 0.2.3 - Complete the rename paths

Updated README documentation links and installer source pin to this Chatify release. Corrected stale release documentation and the historical rename command: use `uvx --from chatify-app chatify`, never bare `uvx chatify` (a different project). Added a release-pin regression check.
## 0.2.2 - Configuration compatibility

Keep the configuration page available when CHATIFY_CONFIG is set to on. Both the new and legacy environment names use the same lock parsing.

## 0.2.1 - Chatify screenshots and docs

README screenshots retaken from the renamed app, demo workspace now titled Chatify, and remaining docs references updated.

## 0.2.0 - Chatify

CustomChat is now Chatify. The PyPI package is `chatify-app` (`pip install chatify-app`, `uvx --from chatify-app chatify`), the command is `chatify`, and the repo is github.com/Harsh23Kashyap/Chatify. Old `customchat` / `customchat-app` commands keep working as aliases, and the old `CUSTOMCHAT_DB_URL`, `CUSTOMCHAT_CONFIG` and `CUSTOMCHAT_INSTALL_SOURCE` environment variables are still read as fallbacks.

## 0.1.36 - Rename notice

CustomChat is now Chatify. New installs and updates: `chatify-app` on PyPI (`pip install chatify-app` or `uvx --from chatify-app chatify`). This is the final `customchat-app` release; it stays installable for existing setups.

## 0.1.35 - Accessible history navigation

- Give Chats and Topics proper tab semantics, selected state and arrow/Home/End keyboard navigation.
- Keep the current layout and refresh regression checks for Guide, appearance, motion and workspace loading.
- Original Gemini error root cause and physical phone/screen-reader checks remain unverified.

## 0.1.34 - Chat rendering and app handoff

- Stream safe bold/code/table/list formatting instead of literal Markdown; keep numbered lists numbered.
- Profile, reading controls and chat Guide follow the active palette and fonts.
- Rename chats and conversations in an in-app form with validation, visible errors and updated active headings.
- Treat disconnected streaming clients as normal, close the generator and avoid a second error write to dead sockets.
- Start reviewed saved Build with AI apps in a separate local workspace through Use this app, without restarting the current server. Imported apps already use separate workspaces.
- Explain Build with AI near the start of Guide, including review, model-call costs and limits.
- Add a small startup/navigation loading line and view fade, with static reduced-motion behavior.
- Default to12 evidence passages; Deep uses twice the configured amount up to50. Ask for fuller source-backed answers and expose a4096-token output ceiling.

Local validation:794 Python tests passed,3 skipped; streamed formatting/palette, saved rename, scrolling, loading/navigation/Guide and Build handoff browser checks. Real gpt-4.1-mini Deep comparisons: F1 253 to295 words, Nutrition250 to443, Travel300 to345. Length is not a guaranteed target and live answers are not independently fact-checked. Free dated FIA snapshot sources were added to the separate Formula One sample workspace, not the package. Publication uses the reviewed GitHub/PyPI workflow.

## 0.1.33 - Tested API helpers and clearer setup

- Shorter API recommendation cards with expandable setup and reduced-motion-safe feedback.
- Preserve usable helper response data while rejecting explicit source errors.
- Forward only explicitly declared API-key environment names to reviewed imported apps and bounded connectors.
- Reuse accepted passages for a pure simplification without a fresh source request; new factual questions still retrieve and filter evidence.
- Retry transient arXiv and catalog errors, use verified HTTPS arXiv API transport, and avoid OpenAlex question-mark wildcard errors.
- Strengthen generated stage prompts and domain follow-up checks.

Validated locally with 805 tests and 483 subtests, ten app import/startup checks, and real two-turn checks for 40 included API integrations. Five card-required Brave picks were excluded from the example bundle. Integration success is not independent fact-checking of every answer or guaranteed source availability. No credentials are included.

## 0.1.32 - 2026-10-14

- Keep local model setup and download status truthful through late responses, cancellation failures and retries.
- Keep source filters accessible and show source/action loading failures beside their controls.
- Center history action icons and separate duplicate-chat times from touch controls.
- Wrap composer footer text as one flow, without orphan separators.
- Disable press displacement in no-motion modes. Track answer clipboard work and keep copy/delete failures readable and retryable.
- Distinguish model documentation links by their source and page.
- Expand fixture-only motion and accessibility checks. Update both launch scripts to 0.1.32; remaining campaign items are not claimed complete.

## 0.1.31 - 2026-10-14

- Keep long builder draft names from pushing configuration fields out of place.
- Fit answer action menus within the chat viewport and scroll when space is short.
- Keep empty-state headings and illustrations stationary, with short opacity-only entrances. Respect reduced-motion preferences.
- Expand fixture-only browser checks for button release, field focus, long configuration content, checkboxes and useful tooltip text.
- Update both launch scripts to 0.1.31. Motion and accessibility work continues; this release does not claim full coverage.

## 0.1.30 - 2026-10-14

- Fix compact picker labels and keyboard selection, keeping menus inside the viewport.
- Keep settings navigation, dialogs, preview updates and feedback quiet under None, Calm and device reduced motion.
- Prevent stale network responses from replacing newer settings, drafts or review results.
- Keep save, retry and proposed-source actions single-flight, with clear status and keyboard focus recovery.
- Expand browser regression coverage for motion, source tools, helpers, local downloads and builder review states.
- Update both launch scripts to 0.1.30. Motion and accessibility work continues; this release does not claim full coverage.

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

# Chatify deliverables - RECONSTRUCTED WORKING DRAFT

Not a completion report. Rebuilt Oct27 from preserved research File and repository evidence after the Oct26 workspace loss. Tests/hosted/release/video remain incomplete. No lost screenshot or test result is recreated as an observed pass.

## 1. A concise summary of the original design problems.

Original-brief baseline remains unbound: the surviving research images do not by themselves establish which revision was the starting point. A separate repository audit is dated October7 and must not be relabeled as the October25 baseline.

Re-inspected preserved research snapshots on October27: desktop settled chat (1278x899), desktop settings/build (1280x720), and mobile settled chat (390x844). Visible opportunities in those snapshots, not claims about today's product: mobile global navigation occupies roughly the first quarter of the viewport; the composer leaves only a shallow suggestion-reading region; desktop settings stacks a large heading, view switch, search and category cards before the working editor reaches the lower edge. The pine/cream/lime identity and serif display heading already exist in these images, so they cannot honestly be presented as entirely new work without the baseline comparison.

Evidence: recovered research source src/photos/audit-desktop-chat-settled.png, audit-desktop-settings.png, audit-desktop-build.png, audit-mobile-chat-default-settled.png. These are preserved snapshots, not current live visual verification. Original screenshots retained; final before/after comparisons still pending.

## 2. A research matrix covering all 15 references and the components worth adopting.

Preserved research source: https://files.instinct.com/jfjwqlfyzb4s-ui-reference-library-for-chatify . The entries below reproduce its recorded research, not a fresh live recheck of licensing or availability. Component adoption is not implied. Reference-only entries are not permission to copy source.

| Reference | Recorded stack / access | Candidate examples and sources | Recorded installation | License / restriction |
|---|---|---|---|---|
| termcn (https://termcn.dev) | Terminal UI (Ink/OpenTUI) - NOT web DOM | Chat Message (https://termcn.dev/r/ink_chat-message.json); Chat Thread (https://termcn.dev/r/ink_chat-thread.json); Code (https://termcn.dev/r/ink_code.json) | Terminal UI - renders to a TTY, not the DOM. | reference-only: no license found anywhere |
| audiocn (https://audiocn.dev) | React + shadcn audio components | Audio Device Select (https://audiocn.dev/r/audio-device-select.json); Audio Player (https://audiocn.dev/r/audio-player.json); Channel Toggle (https://audiocn.dev/r/channel-toggle.json) | shadcn-style audio component pages (use-microphone, bar-visualizer, meters). | reference-only: 'components you own' but no license named; repo not located |
| Arc UI (https://uiarc.dev) | React + CSS modules + Motion, shadcn registry | Action button (https://uiarc.dev/r/action-button.json); Button group (https://uiarc.dev/r/button-group.json); Button (https://uiarc.dev/r/button.json) | shadcn registry: pnpm dlx shadcn@latest add @uiarc/<name> (free items only; /r/pro/ token-gated, excluded). | cleared: MIT (free tier; 119 components+22 blocks free per site; Pro excluded, zero-overlap verified) |
| Beautiful UI (https://beautifului.dev) | AI-native interface primitives showcase, MIT license page | No component source preserved; catalog/marketing reference only. | MIT license page exists but no component source is published. | reference-only: MIT license page exists but no source published |
| 23rd (https://23rd.dev) | React + shaders/backgrounds, shadcn registry | ASCII Fluid (https://23rd.dev/r/ascii-fluid.json); ASCII Logo (https://23rd.dev/r/ascii-logo.json); Dither Scan (https://23rd.dev/r/dither-scan.json) | Site lists install commands; all-rights-reserved by default (no LICENSE). | reference-only: no LICENSE in repo (radiumcoders/23rd.dev) - all rights reserved by default |
| Bencho (https://bencho.dev) | Interactive React micro-interactions; account wall | No component source preserved; catalog/marketing reference only. | Source behind account creation; no signup performed (no authority). | reference-only: source behind account wall; MIT claim unverified |
| BoardUI (https://boardui.com) | React + Tailwind v4 + React Aria, dashboards/agentic | Agent Chat (https://boardui.com/r/agent-chat.json); Button Group (https://boardui.com/r/button-group.json); Button (https://boardui.com/r/button.json) | shadcn-compatible registry CLI per component page; agent-chat block pulls ai-sdk deps. | cleared: free tier per boardui.com/license (free source owned); Pro templates excluded |
| Tailgrids (https://tailgrids.com) | React + Tailwind; MIT essentials + paid Pro | Card With Badge Preview (https://tailgrids.com); Code Block Card (https://tailgrids.com); Command Dialog Preview (https://tailgrids.com) | Copy-paste Tailwind blocks from site/repo (TailGrids/tailgrids). | cleared: MIT free Essentials (repo LICENSE.md); Pro blocks excluded |
| Opensource UI (https://opensourceui.in) | React/Next.js copy-paste, MIT | Chat Bubble Notification Banner (https://opensourceui.in); Contact Profile Card (https://opensourceui.in); Copy Button (https://opensourceui.in) | Copy-paste from site/repo (bidyut10/opensourceui). | cleared: MIT (repo LICENSE) |
| Transitions.dev (https://transitions.dev) | Vanilla CSS/JS + React transition snippets | 3D Tilt (https://transitions.dev); Accordion (https://transitions.dev); Avatar Group Hover (https://transitions.dev) | Vanilla CSS/JS snippets with copy buttons on public pages. | reference-only-for-product: free transitions served with source on public pages (copy affordance); no formal license/permission text located - usable as design reference, NOT cleared for product integration until explicit terms found |
| HeroUI v3 (https://heroui.com) | React + Tailwind, Apache-2.0 design system | Accordion (https://heroui.com); Alert Dialog (https://heroui.com); Avatar (https://heroui.com) | npm @heroui/react (v3); a real dependency, which Chatify cannot take (no bundler). | cleared: Apache-2.0 (repo LICENSE) |
| Reverse UI (https://reverseui.com) | React + Framer Motion animated; free tier commercial OK | Aurora Footer (https://reverseui.com); Bars Loader (https://reverseui.com); Cool Badge (https://reverseui.com) | Copy from component pages (Tailwind/MUI tabs) in browser; retro-terminal login-gated in practice despite free listing. | cleared: free tier incl. commercial use per pricing page; 19/20 extracted |
| Magic UI (https://magicui.design) | React + Tailwind, landing-page components | Theme Toggler (https://magicui.design/r/animated-theme-toggler.json); Scroll Progress (https://magicui.design/r/scroll-progress.json); Comic Text (https://magicui.design/r/comic-text.json) | npx shadcn@latest add https://magicui.design/r/<name>.json; free components only (Pro templates excluded). | cleared: MIT (github.com/magicuidesign/magicui, 22.8k stars) |
| Aceternity UI (https://ui.aceternity.com) | React/Next.js + Tailwind v4 + Framer Motion | File Upload (https://ui.aceternity.com/registry/file-upload.json); Tooltip Card (https://ui.aceternity.com/registry/tooltip-card.json); Text Reveal Card (https://ui.aceternity.com/registry/text-reveal-card.json) | Copy-paste from component pages; do not integrate until license resolves. | reference-only: no license page/repo license found |
| Motion Primitives (https://motion-primitives.com) | React + Motion animation primitives | Accordion (https://motion-primitives.com); Button (https://motion-primitives.com); Card Example Landing (https://motion-primitives.com) | Copy-paste from docs pages; npm i motion in a React project. | cleared: MIT (repo LICENCE.md) |

## 3. The major visual and interaction improvements implemented.

Source-backed changes in bounded October25 v2-to-current window, not a claim every feature originated during this brief:

- Chat: welcome kicker/rule, measured introduction, compact tools, evidence cards, busy-answer skeleton, quieter thread texture and active-chat marker (42fcc2c). Composer/answer hierarchy and mobile single-row chrome followed (1c034fe,92ae6de).
- Settings: configuration-home build prompt with visible cost/review notice and separate manual entry; interactive sample preview labeled as sample, not a live model result. Actual current screenshots show these surfaces at1280/768/390.
- Navigation/controls: explicit Manual-view activation fixes detached-menu navigation; Remaining-work node retained during unchanged poll updates so native smooth scrolling is not cancelled. Source/mechanism evidence in FLAKE_QUALIFICATION.md. These are actual product changes, unlike the later harness observation repairs.
- Reduced motion, quiet states, focus/inert, singleflight and shell geometry receive targeted test coverage. Runtime active-retirement quiet-event full-matrix coverage remains blocked; do not present this as universally qualified accessibility/motion.

No source component from a reference library is claimed as adopted without a corresponding code/import provenance. The matrix describes research candidates, not proof of component installation.

## 4. The exact files and components changed.

A complete mission-wide inventory remains to be reconstructed. A reproducible **technical comparison window**, 42fcc2c^..c6b60e5, starts before the October25 09:16 v2 chat-treatment commit. It is NOT established as the original mission baseline. UI/package paths changed in that window:

- Chat and answer reading: chatify/web/app.js, index.html, style.css, pipeline.js, reading.js.
- Builder and settings: chatify/web/appbuilder.js, appearanceextras.js, builderstudio.css, configurationhome.css, settings.css, settings.js, settingsguide.js, settingstabs.css, settingstop.js.
- Shared interaction styling: chatify/web/components.css, loading.css, motion.css, navigation.css, refinements.css.
- Font assets/notices: chatify/web/fonts/FONTS.md, NotoNaskhArabic[wght].ttf, NotoSansHebrew[wdth,wght].ttf, NotoSansMath-OFL.txt.
- Installation metadata: pyproject.toml, requirements.txt.

This list is an exact path diff for that bounded window, not every earlier or backend file. The source-backed October25 09:16 commit 42fcc2c adds welcome hierarchy, compact Chat tools chips, evidence cards, busy answer skeleton, dotted thread surface and sidebar active marker (app.js/style.css plus font license notices). A current visual comparison is still required before claiming the delivered result.

Current post-rebuild changes are separately reproducible with git diff a8ce3fd..HEAD and predominantly concern qualification/test evidence; that is not the full redesign diff.

## 5. New dependencies and installation details.

Current source inventory, not yet a mission-wide additions diff or registry verification:

- pyproject.toml: chatify-app0.4.32, Python>=3.10, PyYAML>=6.0.3,<7 base dependency; setuptools>=61 build backend.
- Optional documents extra: pypdf>=4, fpdf2>=2.8, uharfbuzz>=0.39. Optional semantic extra: sentence-transformers>=3.
- requirements.txt for deployed images additionally lists pypdf/fpdf2/uharfbuzz, onnxruntime==1.31.0 for Python>=3.11 or ==1.23.2 for Python<3.11, and tokenizers==0.23.3. Its PyYAML floor is >=6.0, unlike the package metadata. These are different installation surfaces, not interchangeable lockfiles.
- The browser UI is shipped as static assets; the research matrix's React/Tailwind/shadcn commands are reference instructions, not commands to install into Chatify. Playwright and axe-core are qualification tooling, not product runtime additions.

Installation/fresh-computer verification must still be reconciled with current artifacts. No build/install success is inferred from dependency declarations.

## 6. Test, lint, type-check, and build results.

Preserved census:469 unique keys latestPASS, followed by117-key post-change rerun coverage. Coverage is distinct from qualification. Stability campaign finished:18of19cases have five completed solo PASSes, with sidebar's externally interrupted partial fourth invocation retained as a campaign caveat. Runtime active-retirement quiet-transition fullmatrix remains BLOCKED/UNQUALIFIED after unchanged160ms fallback expired before observation, including a fresh repaired-dispatch attempt. Choice's original unexplained intermittent remains residual risk. No full qualification or hosted release verdict.

Final command checks recorded October27 in tests/census/2026-10-27-final/RESULTS.md and unit-reconciliation.json:1102distinct unit IDs all exercised through per-ID chunks (1104 chunk executions plus5alias verification executions),0failures/0errors/1skip. Monolithic discovery was interrupted and is NOT called a pass. Top-level UIJS syntax and Python bytecompile exit0, not lint/typechecks. Wheel build exit0 at0.4.32, no publication. No dedicated lint/typecheck project command found.

Actual current local offline-fixture screenshots: chat/settings/build x1280/768/390, all nine inspected; no pageerror events and no document horizontal overflow in these captures. Static screenshot review does not verify motion timing or real model answers. Research/before screenshots are not revision-bound to original baseline. Build/install/hosted release qualification remains incomplete.

## 7. Any inaccessible references, licensing limitations, unfinished tasks, or remaining visual weaknesses.

Reference-only licensing/access limits are in matrix above. Remaining: runtime full active-retirement quiet-event coverage blocked; retained historical risk and sidebar interrupted-campaign caveat; complete original-baseline attribution and mission-wide file inventory; hosted builder/preview-scroll and data-backup checks; backup/informed-loss gate before destructive deployment; release/install matrix, PyPI release and instructional video. Local static visual weaknesses: configuration mobile still spends about150px on global navigation; tablet configuration has a narrow two-column prompt/preview composition; mobile chat toolbar extends beyond visible card width and needs horizontal affordance verification, despite document having no horizontal overflow. Current visual review covers local offline fixture, not production, dark theme or answer-quality proof. Additional requested scenarios are queued separately, not automatically counted as executed coverage.

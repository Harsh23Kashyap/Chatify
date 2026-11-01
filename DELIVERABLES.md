# Chatify design deliverables
31 October 2026. Current qualified product revision: `768e1a178709b1e4b08f9add21adb711b1cd5976`.

The current product is deployed at https://chatify-demo-779c.onrender.com/chatify/settings.html. This report reconciles the seven requested outputs. It does not declare all broader Chatify work finished or turn fixture tests into real-provider evidence. Historical dated audit files are retained, not silently rewritten as current results.

## 1. Original design problems

The original request described the website as bland. The exact original-brief screenshot/revision baseline is not established. October 7 audit screenshots and later preserved research snapshots must not be relabeled as the October 25 starting point. Pine/cream/lime identity and serif headings already existed in the preserved snapshots.

The October 27 source-desk audit identified oversized repeated headings, bulky pill controls, nested surfaces, dense tablet headers and competing configuration paths. These are dated observations, not claims that every issue survives today. Current work keeps stable named navigation, clearer reading hierarchy and a focused configuration workspace rather than importing a generic template.

## 2. All 15-reference research matrix

[Current matrix](docs/design/2026-10-31-reference-matrix.md) records exact candidates, component/doc links, compatibility, installation examples, adopt/adapt/reject decisions and access/license limits. The October 27 component/demo observations are distinguished from the October 31 source/license recheck. All 15 own sites were re-read; not every demo in every catalog was tested.

Strongest native adaptations: Arc quiet button hierarchy, BoardUI stationary active underline, BeautifulUI task/source grouping, audiocn explicit label/value controls and Motion Primitives restrained disclosure. These are interaction/design references, not a claim that vendor component code was installed. React/Tailwind/Motion registries were rejected as runtime migrations for this vanilla-JavaScript application. Docks, shader backgrounds, decorative counters and unrelated charts were not added.

Material corrections to the reconstructed draft: termcn has MIT repository evidence; HeroUI is Apache-2.0, not the later matrix's MIT; audiocn's old license URL now 404s but its actual repository license is MIT with an excluded sound; 23rd's current license remains unresolved; BoardUI's own page contains conflicting source-redistribution language. Tailgrids restricts builder/UI-generator use. No paid/premium source was copied.

## 3. Implemented visual and interaction changes

- Chat work surface: quieter surfaces, measured introduction, compact tool metadata, evidence/source hierarchy, reading controls and a less dominant composer. Retained real streaming and source state machines.
- Shared shell: pine/lime identity, semantic surfaces, text navigation with stationary active rule, focus/pressed feedback and bounded motion with reduced-motion behavior. Existing orbit loader remains; no progress-bar replacement.
- Configuration: existing idea tool beside a video, existing Build status window, and actual proposed-app sample preview before explicit Apply. Sample chat is labeled; it makes no model call. Review/save/launch remain explicit. The separate wizard prototype is not the chosen flow.
- Async behavior: visible server-stage status and success/error states, source inspection, disclosure affordances and focus return. No fabricated progress or fake success.
- How-to: bundled feature stories, Paperworks and narrated Signal Desk walkthroughs. Selected feature story autoplays with muted fallback and Turn sound on when needed; walkthrough playback stays manual. Selection/off-route handling prevents overlapping playback. The requested whole caption was removed.
- Product regressions repaired during qualification: restored-scroll settings alignment, editor caret visibility at native 400% zoom, streamed-answer anchoring and timer cleanup. Test-only changes are not presented as visual upgrades.

These improvements span several requests and commits. Their presence today is not proof that every feature originated in the design brief.

## 4. Exact changed files and components

The reproducible technical window is `42fcc2c^..768e1a1`, beginning immediately before the October 25 v2 chat-treatment commit. It is **not** a proven mission baseline. [Full status/path inventory](docs/design/2026-10-31-changed-files.tsv) lists1352 paths:1125 tests,202 chatify,11 apps,6 docs,3 workflow and5 root/schema paths. This includes later qualification, source and media work, not1352 design-only changes.

Core UI paths: `chatify/web/app.js`, `index.html`, `style.css`, `pipeline.js`, `reading.js`; shell `product.css`, `product.js`, `workspace.css`, `workspace.js`, `navigation.css`, `navflow.js`, `motion.css`, `components.css`, `loading.css`, `loading.js`, `refinements.css`; configuration/build `settings.html`, `settings.js`, `settings.css`, `settingstabs.css`, `settingstop.js`, `settingsguide.js`, `configurationhome.css`, `appbuilder.js`, `builderstudio.css`, `build.html`, `build.js`, `build.css`; route/help `about.html`, `run-locally.html`, `tour.js`, `videobreak.js`, `configstate.js`, `appearanceextras.js`, `theme.js`. Fonts/media/manifest and backend/test paths are individually listed in the inventory.

Current documentation changes are separate from that frozen product inventory. Reproduce with `git diff --name-status 42fcc2c^..768e1a1`. The old reconstructed document remains recoverable in git history.

## 5. Dependencies and installation

[Exact metadata delta](docs/design/2026-10-31-dependency-delta.patch) uses the same technical window. No React, Tailwind, shadcn or vendor UI runtime was added.

- Package remains `chatify-app 0.4.32`, Python>=3.10, setuptools>=61, base `PyYAML>=6.0.3,<7`.
- Documents extra adds `fpdf2>=2.8` and `uharfbuzz>=0.39` alongside `pypdf>=4`; semantic extra remains `sentence-transformers>=3`.
- Deployed requirements add ONNX Runtime 1.31.0 on Python>=3.11 /1.23.2 on older Python, plus tokenizers 0.23.3. Requirements' PyYAML floor remains>=6.0, distinct from package metadata.
- Package-data now includes font and nested story/media assets. No claim that dependency declarations alone verify fresh installation.
- Source installation: `python -m pip install '.[documents]'`; optional semantic extra is separate. Research matrix registry commands are reference instructions, not Chatify installation steps.

PyPI publication and final release version remain separate work. A green wheel build is not publication.

## 6. Test, syntax, install and build results

Fresh attempt 1 CI for the exact qualified revision, rechecked October 31:

| Gate | Result and scope | Evidence |
|---|---|---|
| Python tests | success on 3.10/3.11/3.12; monolithic unittest discovery plus app/gallery validation | https://github.com/Harsh23Kashyap/Chatify/actions/runs/41192959254 |
| Offline browser | all 12shards success, plus syntax/package job; synthetic/mock paths are not live answer-quality proof | https://github.com/Harsh23Kashyap/Chatify/actions/runs/41192959248 |
| Installer | Ubuntu, Windows, macOS matrix success; wheel build, repeated shared installer scenarios, platform entrypoint and fresh uvx bootstrap | https://github.com/Harsh23Kashyap/Chatify/actions/runs/41192959265 |
| Syntax/package | Python compileall, top-level web JS node --check, suite-orchestration tests, wheel build and packaged-font regression | included in browser run above |
| Dedicated lint/typecheck | no configured standalone project gate identified; syntax is not lint/type analysis | current workflows |

The historical October 27 blocked runtime census is not the current overall verdict. Preserve its failures as history, but do not present them as still-blocking after the later complete green run. Reconstructed-fixture/mock-path tests establish harness coverage, not independent proof of the original product contract or real model answers.

Current public Chromium verification: actual Paperworks playback advanced, sought 45 seconds, reached ended, and recovered with Retry after a forced abort. Direct/mounted full bytes and206bounded/suffix/416behavior were checked. Selected story autoplay/muted fallback/unmute/off-route stop was exercised, Signal Desk playback checked, and60 story range/ftyp probes passed. Those probes do not mean every soundtrack was auditioned. Current live screenshots were inspected; static pixels alone do not prove motion or playback.

## 7. Limits and remaining work

- No honest original-baseline before/after attribution. Historical screenshots are dated evidence only.
- Reference depth is per-row in the matrix. termcn Card and23rd canvases did not produce qualified demos; dock expansion and reference Disclosure interaction were not fully exercised. Current policy/source reads do not imply fresh all-demo visual inspection.
- No Safari-engine qualification. WebKit launch was unavailable in the environment; current live playback checks were Chromium.
- Subjective soundtrack/mix review across all 60stories remains separate. The original lost Signal Desk artifact was not recovered; the current narrated walkthrough is a reconstruction.
- PyPI publication, real-provider answer-quality/source-freshness improvements, and Agriculture scenario completion remain separate outcomes. Mock answers do not prove quality. No guessed global fertilizer dosage.
- Current priority is desktop. Existing responsive behavior was preserved and tested in earlier/broad gates, but a new mobile polish campaign is not a completion requirement.
- No new paid service, premium asset or deployment is part of this documentation reconciliation. No user data or account secrets are included in this report.

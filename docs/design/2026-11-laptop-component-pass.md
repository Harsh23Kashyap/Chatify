# Laptop component and illustration pass, 11 November 2026

## Scope

Follow-up to the earlier design pass. Laptop-first, with the existing vermilion/sand identity, public read-only configuration and shared demo keys unchanged. No backend, account, workspace, provider or paid-service changes.

The requested anti-slop reference was https://github.com/Appllama/appllama-skills. Its transferable rules informed the audit: one accent and neutral family, a stated radius scale, meaningful illustrations, no fake progress, full states, reduced-motion support and direct screenshot inspection. Native-mobile implementation instructions do not apply to this web app. The later component-polish request used Airbnb as a reference for rounded surfaces, restrained depth and clear hierarchy, not for its colors, assets or marketplace layout. Public reference inspected: https://www.airbnb.co.in/?locale=en.

## Findings and changes

- Selected manual-settings links had surviving inset accent rails. Selection now uses a full neutral surface and weight. Keyboard focus remains visible.
- About instructions retained a green left border and green surface. They now use the approved tokens and a uniform border.
- Decorative physical/logical left borders also survived on cost notices, completion/error/provenance notices, draft notices, help text and Run locally tips. Removed them at their definitions, including dormant legacy rules. Error wording, symbols and uniform error borders stay intact.
- Populated chat history and highlighted citations were already rail-free. Rechecked those states with synthetic responses rather than claiming another fix.
- All 23 About entries now use 22 distinct flat drawings, with the two export entries intentionally sharing one. Added meaningful text, evidence, waveform, setup and connector details. Removed repeated halos and invented slider/progress tracks.
- Removed decorative sparkles/trails from main chat and sparkles/gradient mist from temporary chat. Kept document/citation and conversation/clock concepts.
- Laptop showcase scale: 12px controls, 16px illustration wells, 20px panels. Dense manual-editing panels keep their existing 16px/no-shadow contract. Warm solid surfaces and low neutral shadows distinguish an editing panel from its background.
- Feature illustrations respond to hover with a 3px/140ms movement; people cards lift 2px. No idle loops. None/Calm and system reduced-motion suppress movement. Existing action and tab behavior stays intact.

## Verification

Actual before/after laptop pixels inspected in light and dark. Local checks use offline fixture providers and synthetic source/history responses. They establish UI behavior, not model answer quality or real-provider service health.

Original regression scripts passed after component polish:

1. design_shell_layout_browser.cjs
2. about_feature_states_browser.cjs
3. about_all_features_idle_motion_browser.cjs
4. about_continuity_browser.cjs
5. about_team_browser.cjs
6. source_panel_runtime_quiet_browser.cjs
7. builder_library_error_recovery_motion_browser.cjs
8. builder_entry_warm_ui_browser.cjs
9. tabs_design_browser.cjs
10. settings_help_cost_disclosure_browser.cjs
11. suggestion_press_motion_audit_browser.cjs

New contracts registered in the CI manifest:

- laptop_no_accent_rails_browser.cjs: 1280/1440 light/dark, manual selections, cost notices, all23 SVG/caption/ARIA states, Run locally, populated source/history selection and keyboard focus.
- laptop_component_polish_browser.cjs: Full/None/Calm with normal/reduced motion, hover and pointer-exit behavior, no idle loops and computed panel shape/depth.

The existing manifest-count assertion is updated from495 to497 for these two added scripts; no product assertions are weakened. Earlier About geometry checks also passed across five widths and two motion states. Mobile was not redesigned in this pass.

Release gate: all exact-commit CI workflows green, then deploy the same commit and verify the live public app and read-only lock. Do not infer deployment or live success from these local checks.

## CI follow-up

The first full browser run passed all shards except the existing editing_surface_tokens contract. Restored the dense manual editor panels to their original16px/no-shadow design instead of weakening that regression. Showcase and builder surfaces keep the requested soft depth.

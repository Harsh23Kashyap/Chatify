# Offline regression contract corrections, 2026-11-10

These changes distinguish product fixes from stale fixture and visual expectations.
The first verification commit is not a full-suite green claim.

## Product defects
- Cloud-model selection widened its button and reflowed the card. Reserve desktop button width. The existing four-combination recommendation test is unchanged.
- History hover reduced title width and changed line geometry. Use 76px two-line rows, with a reserved timestamp/action row and always-accessible existing controls. The existing rename persistence test now passes without changes.
- Supporting settings preview started below the editor. Remove its extra top padding; retain the existing alignment assertions.
- The manual step-picker cue had an accessible name but no title. Add its title; retain the icon inventory audit.

## Grounded UI contracts
- The user accepted the earlier manual layout with the Prompts card grid replaced by one step picker and numbered editor on November 6. Selector changes exercise the real picker, not direct hidden-node clicks.
- The user requested fixing history, mode selection and settings hierarchy with ChatGPT recommendations on November 10. Text-only consultation recommended two-line 76px history, state-based selected modes without a moving pill, and 20px/28px primary headings with flat bordered cards. Existing history action buttons are preserved instead of adding a new menu.
- Mode tests retain ARIA exclusivity, color transition, caption, motion preference and no-translation checks. They assert selected background/state, not the retired moving indicator.
- History skeletons match 76px rows. Title/action non-overlap checks use the dedicated title line.

## Test updates, not product defects
- Category tabs already use a vermilion 2px underline, transparent background and no inset shadow. Test those boundaries instead of the old filled/inset style. Preserve ARIA selection, focus, keyboard, minimum targets, overflow and destination checks.
- At 320px, wrapping configuration chrome puts the advanced preset at document y=1036px, but only 223px below its own panel. Replace the arbitrary absolute 1000px cutoff with a 300px panel-relative bound and explicit scroll/visibility checks. Preserve all navigation, target, overflow and dialog checks. This is not a claim of a mobile product fix.

## Fixture correctness
- Retained/completed draft fixtures must exist in the genuine same-owner store before real review. Seed them through the public draft endpoint with the fixture request's owner cookie. Do not mock review or bypass provenance.
- A newer edit must not inherit an earlier Saved label or confirmation animation.
- Use the configured Playwright module rather than a machine-specific path.
- Split long checklist and prompt-geometry scripts into explicit canonical variants. The runner still requires all variants; a single variant is never an aggregate pass.
- Checklist tests abort only external Google Fonts requests to keep this lane offline and avoid network-dependent page-load timeouts. All review, ownership, keyboard, focus and accessibility checks remain active.

Original failure logs and interrupted-run history are preserved outside the repository. Failed, interrupted and partially verified matrices must not be reported as a full pass.

## Full-suite follow-up
- Seven saved-history lifecycle/export tests now click the title, not the geometric center of the row, which may be an explicit Pin/Rename/Delete control in the new reserved action row. Their original lifecycle/export assertions remain unchanged.
- The prompt picker paints above compacted help, preventing real pointer interception.
- Runtime source-panel tests pause opening animations when created, rather than trying to catch a short animation after a browser round trip. Runtime cancellation, retained content, focus restoration and quiet-mode checks remain unchanged.
- Builder conversation navigation checks the actual open button's visibility before choosing Build with AI. Checking only the hero's own display misses a hidden ancestor after the preceding width's ZIP route. Conversation, selected model, consent, edit, review, save and ZIP assertions are unchanged.

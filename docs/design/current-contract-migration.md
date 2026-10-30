# Retained native design contracts

This is a contract migration, not an exact-styling user approval. The renewed October 29 implementation brief delegates routine design choices, preserving functionality, accessibility and verification. Retain the current native product.css treatment instead of reverting it to older assertions:

- Selected global navigation has one stationary 3px brand-colored bar, no transform/animation. Inactive links have no bar and share neutral colors. Navigation remains text-only.
- About/settings paper is #f4f3eb.
- Selected manual category uses #eaf0e2 with a 2px inset pine rule and zero border width. Single selection, aria, keyboard focus, 44px minimum targets, group routing, reduced motion and small-screen editing remain asserted.
- Mobile global navigation tests open the actual current menu before inspecting hidden links. Keyboard focus checks use Tab/Shift+Tab so :focus-visible is exercised rather than mouse modality.

No product code is changed by this migration. Existing shell stationary/motion, route count, neutral inactive links, category decorative-icon, destination, keyboard, bounds and short-screen save-reach checks remain. This does not resolve public video integration, seeded-chat harness, zoom, or remaining browser CI issues.

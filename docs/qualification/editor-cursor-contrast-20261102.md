# Dark editor custom cursor contrast

Base: released main 78b686c148b60e2a853d93bd47b3a36046e3bf37.

The existing native browser 400% zoom test passes on the released base, including its delayed-frame variant and restored end-selection check. This does not reproduce a remaining clipping failure. The repaired settings.js from earlier work is already in the integrated base.

Actual pixels showed the custom CodeMirror cursor was black on the dark editor. Its native content caret is deliberately transparent because CodeMirror paints a separate cursor. A focused rendered-style probe confirmed black against rgb(15,27,22), approximately 1.19:1 contrast. Text itself remained readable. The scoped CSS correction sets custom cursor and drop-cursor border color to the existing light editor text color, rgb(223,233,226), approximately 14.21:1. No editor behavior or persistence changes.

Qualification:

- New custom-cursor regression fails on unchanged base CSS and passes corrected CSS, desktop 1280x900 normal/reduced motion. It checks actual custom cursor style, painted dimensions, contrast and preserved typed text. Screenshot blink is frozen only after assertions for decisive visual evidence.
- Existing native headed Chrome 400% tab-order script passes default and delayed-frame variants, 356 checks each. No geometry assertion changed.
- Separate native 400% caret Home/End/type/Tab script passes.
- Helper editor keyboard-choice script passes.
- Actual screenshots inspected: light custom cursor at restored end selection at 400%; light cursor and readable typed text at desktop 100%, normal/reduced motion.
- Four scoped browser scripts, five executions. Manifest now classifies 483 scripts; this is not an all-483 run.
- Clean full Python suite: 1386 passed, 1 skipped, 540 subtests, eight serial groups across 219 test files. An earlier interrupted group0 run is excluded; every counted group has a completed result.

Limits: local product UI using offline app fixture, not hosted acceptance or an all-browser claim. Does not qualify semantic answers, free-source availability, Recipe comparison relevance, original large-logo hosted performance or reload-safe draft retries. Recipe defensive checkpoint remains separate and is not included.

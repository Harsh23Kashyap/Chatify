# Confirmed builder and preview flow
29 October 2026. Local-only implementation and verification. No deployment or publication.

## User-selected surface
Keep Configuration's pine idea tool beside a right-hand video, not the separate six-step guided Build page. Build opens the existing status window. Step two shows the actual proposed app in an interactive sample chat before validation and explicit Apply. The prior guided-page side-panel experiment is not part of this change.

## Changes
- Existing left idea tool and its consent/model checks retained.
- Right optional video: two locally bundled silent excerpts, user-initiated play/pause/next, no autoplay/loop/remote embed. Pause on opening Build, terminal build state, hidden page or leaving the AI view. Playback sequence guards prevent a cancelled play promise overwriting a later video error.
- Existing progress window: one primary completed-area/model-request count line, area-state totals, real server phase, inspectable received drafts. No fake interpolation or extra model requests. Avoid redundant model-availability warning when inspecting an existing running/completed job. Local controls remain responsible for authorizing a new build.
- Step two: existing real draft preview is full width and leads the review. Same app renderer and proposed appearance, explicitly sample chat/no model request. Technical configuration and API cards remain available below. Review/save/launch paths and authority are unchanged.
- Progress colors meet existing contrast assertions. Group geometry remains stable through running/partial states, including font stress.
- Media globs included in wheel and sdist. No dependency changes.

## Verified locally
Existing browser assertions passed: state matrix, progress truth, review accessibility, actual local Apply/reload, lifecycle, final failure/retry, import route, draft loading, mounted preview root and /chatify/, density, long configuration geometry, font stress, focus motion, scope clarity and toolbar. New classified CI case passes 320/390/1280: keyboard/user video play, next, video error, left idea click -> mocked start -> running window -> completed real draft parse/preview -> interactive sample chat. No implicit save or launch. Backend: 67 tests and 4 subtests pass. Syntax, diff whitespace, wheel/sdist build and twine checks pass. Installed wheel source and media checked independently.

The Apply test uses an offline surviving fixture with actual local parse/review/save/reload, not a real model result or production action. The new flow test mocks model job replies. This is not new real-provider end-to-end qualification or a claim that every existing browser script was rerun.

## Preserved failures
Progress redesign initially failed the original orbit/group contrast assertions; colors corrected, assertions unchanged. Font-stress test caught a 2px title shift when partial state lost the running-only card rules; styles now also apply to retained builds. Video-error test caught an asynchronous rejected play promise replacing the error label; sequence guard corrected. One Apply invocation pointed at a nonexistent fixture, then reran against the surviving builder-trip fixture. A broad sequential batch exceeded the command timeout; finished logs inspected and only unfinished cases continued. Earlier logs retained separately. None of these failures establishes a production/provider failure.

## Media source and rights
Official source ZIP: https://download.blender.org/peach/bigbuckbunny_movies/BigBuckBunny_320x180.mp4.zip
Official download page: https://peach.blender.org/download/
Official reuse/excerpt permission: https://peach.blender.org/about/
CC BY 3.0 attribution and transformations recorded in web/media/README.md. Excerpts 00:56-01:20 and 00:32-00:56, silent, re-encoded. Opening title treatment deliberately excluded.

## Release boundary
Integration is being prepared on an isolated branch only. No main-branch push, deployment or publication. Active hosted user job/draft has not been changed. Running jobs are process-memory objects; saved drafts/checkpoints depend on storage persistence. Do not restart the hosted service without confirming the active app is backed up or the user accepts loss. Version-only 0.4.33 preparation predates this change and does not qualify it. Separate final design documentation remains to update after the chosen implementation is accepted and released.

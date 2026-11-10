# Story audio level pass, 10 November 2026

30 quiet non-pulse stories now have gain-only variants. The manifest selects them. All 60 original MP4 files remain at their original paths, with no deletion or overwrite. The other 30 manifest entries are unchanged.

Target: -24 LUFS integrated, selected from the measured louder-group median (-24.08). True-peak ceiling: -2 dBTP. References are levels only: corgi-preview (-24.22), deer-readiness (-24.32), fox-sources (-23.99). This is level matching, not musical approval.

Processing: fixed `volume` gain, AAC re-encode at 128 kb/s, original sample rate/channel count, copied video stream. No loudnorm processing, compressor, limiter or silence trimming. loudnorm was used ONLY as a measurement filter to a null output. The measured gain had more than 2.5 dB true-peak headroom; otherwise the script would stop rather than compress.

Before and after metrics, original/variant SHA256, duration and video packet stream hashes are in the adjacent JSON. All 30 outputs decoded without errors, measured within 0.25 LU of target and below the peak ceiling. Both video stream hashes are compared during generation; identical packet hashes are recorded. AAC lossy re-encoding is not a mathematical PCM gain identity and is not represented as one.

All eight pulse stories are excluded from the batch. Three of those are also quiet: elephant-memory, ant-fallback, panda-export. The remaining five are mouse-mic, hedgehog-prompt, llama-local, duck-temporary, chameleon-palette. No compression was applied to hedgehog-prompt's 15.2 LU range. Audition is required before changing these tracks.

Subjective listening remains 0/60. This pass does not qualify narration/music balance, musical taste, composition, pulse intent, fatigue or background-video usefulness. Harsh's priority listening is a separate gate. Original level audit covered the existing public story URLs under https://chatify-demo-779c.onrender.com/chatify/media/stories/ ; asset names and hashes are retained in the JSON.

## Wheel delivery

Baseline wheel measured 115,882,260 bytes before the level pass. Bundling originals plus variants grew it to 150,629,642 bytes; selecting only manifest stories would still be too large. Wheel installs now retain the manifest, all 60 posters and the two walkthrough videos, while story MP4s stream from the canonical existing host. This needs internet for story playback and is not an offline-video claim. Source/Render deployments keep local files and serve them first. Only a missing manifest-selected story video may redirect; unknown paths do not redirect, and the canonical host itself cannot redirect to itself. No model/key/private chat data is sent to the story host.

Actual post-fix wheel inspection: 33,012,597 bytes, 60 manifest entries, 60 posters, zero story MP4s, Paperworks/Signal Desk walkthroughs retained. This is a local artifact check, not a PyPI publication claim. The manifest loader accepts only the original or approved gain24 filename for each story ID. Desktop runtime checks verify all 60 options, gain-variant playback, native controls and audio-policy fallback.

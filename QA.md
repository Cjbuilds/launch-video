# QA record

Verified 2026-09-13. The representative workflow used the packaged skill with an original fictional Relay product: brief, designed storyboard, explicit approval, animation, HyperFrames checks, MP4 export, frame inspection, and browser playback.

## Actual export

| Check | Result |
| --- | --- |
| HyperFrames CLI | 0.8.37 |
| GSAP | 3.14.2, local pinned file |
| Format | MP4, H.264 High, yuv420p |
| Size | 1920×1080, 16:9 |
| Timing | 30.000 seconds, 30 fps, 900 frames |
| Audio | No audio stream, as approved |
| File | 4,525,115 bytes, approximately 1.207 Mbps |
| SHA-256 | `1c4f7bf7f77ae69c54f98a83f9db392f6206db391768afeff0059ab1dbd07575` |

The source and CLI binding are in [upstream.md](skills/launch-video/references/upstream.md). The MP4's upstream `hyperframes_version` metadata says `0.0.0-dev`; CLI identity was verified separately as 0.8.37. That placeholder tag is not version attestation.

The export is below X's published 140-second/512 MB non-Premium limit. Dimensions, frame rate, and bitrate were checked against [X's current official guidance](https://help.x.com/en/using-x/x-videos). No X upload or publication was performed.

## Checks performed

- `python3 -m unittest discover -s tests -v`: 16 passed. Render calls are mocked in these unit tests.
- Skill creator's `quick_validate.py skills/launch-video`: passed, including a project-local installed copy in a disposable forward test. This is not proof of implicit skill discovery.
- `python3 skills/launch-video/scripts/launch_video.py check-approval examples/relay`: passed against the unchanged approved HTML version.
- `npx --yes hyperframes@0.8.37 lint` and `check`: passed through the render helper. Runtime and motion checks were clean. All 122 sampled text contrast checks passed. Narrow rotated-card overlap annotations document visually checked bounding-box false positives; transient entrance diagnostics remain informational.
- `npx --yes hyperframes@0.8.37 snapshot --at 2.5,4.9,5.2,8.5,9.9,10.2,15,16.9,17.2,22,23.9,24.2,28,29.9`: every scene and cut inspected before final MP4 review.
- `python3 skills/launch-video/scripts/launch_video.py render examples/relay --output output/relay-v1.mp4`: passed. This runs the approval/fidelity guards, lint/check, pinned render, and ffprobe.
- `ffmpeg -v error -i examples/relay/output/relay-v1.mp4 -f null -`: full decode passed.
- Nineteen frames were extracted from the **actual MP4**, including scene midpoints, both sides of every cut, and frame 899. Headline/copy, assets, layout, clipping, and ending checked against the approved storyboard.
- Normal-speed browser playback completed to `ended=true`, `currentTime=30`, with no media error. Root and independent reviewer checked playback and representative frames. Screenshots do not measure smoothness continuously or prove aesthetic quality on every project.

The approved storyboard version is `ecb344ba5277e2b2105a6403843c856ee78fdcfa983c7dd247df3ece85242e17`; HTML SHA-256 is `3e18405d5c9ed9b96a372c96bc79db3996951ae6e7ee72585967a9efef45baf3`. CJ's explicit approval was recorded privately before animation. No approval record is distributed for another user to reuse.

## Forward test and repaired failures

A disposable project-local installation produced a designed fictional Cinder storyboard from sparse facts. Missing assets stopped generation. A copy revision preserved the prior storyboard and simulated fixture approval while requiring new approval. Simulated approval was confined to that disposable fixture.

Independent review found two asset-guard gaps: unquoted image `src` and external SVG resource references. Both now fail before storyboard generation and have regression coverage. Integration also added matching mount/subcomposition-ID checks to prevent blank scenes, and excluded document titles from visible-copy comparison.

The first storyboard clipped UI panels at smaller sizes. Fixed-canvas scaling repaired it. Initial animation checks found contrast, seek-baseline, clip-ID, and overlap findings. Secondary gray labels and button visibility were repaired; GSAP baselines and IDs corrected. Rotated-card text was visually clear, so only the specifically reported header/badge bounds were annotated. No broad checker suppression was added.

## Limits and environment

Tested on macOS arm64, Node 22.23.2, Python 3.14, FFmpeg/ffprobe 8.0.1. Basic code uses Python 3.9-compatible APIs; older supported Python versions were not separately run. Initial browser checks needed permission to bind localhost. First engine setup downloaded approximately 93 MB of Chrome; the compiler may cache fonts. Network access can be needed for npm/browser/font setup.

A separate neutral one-second render first proved the engine path. Upstream capture/packet tests passed 10/10. Thirteen upstream audio tests failed because URL pathname encoding mishandled the workspace's spaces; production audio, optional providers, and website capture remain unverified. Relay is a silent fictional UI demo, not a running product or real customer result.

Approval records are local bookkeeping, not identity authentication. The static-frame loader supports the documented asset forms; it is not a general HTML sanitizer. Asset/layout meaning and actual playback require review. No time/token-saving benchmark or universal quality guarantee is claimed.

The README banner was checked visually and with local Vision OCR; all seven intended strings matched. It uses CJ's approved black ASCII style.

## Published release verification

[Release v0.1.0](https://github.com/Cjbuilds/launch-video/releases/tag/v0.1.0) targets source commit `3d754b80187dfdd691e4128adcb0f6fa90feeccc`. Both README download URLs returned HTTP 200, and GitHub's asset digests matched the verified MP4 and approved HTML hashes above.

A fresh public checkout passed all 16 tests, validated the full scene graph, and regenerated the exact approved storyboard hash. Private approval receipts were absent. The initial packaging omission of `index.html` was corrected in a separate commit before the release tag was created.

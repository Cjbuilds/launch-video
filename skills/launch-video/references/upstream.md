# Verified HyperFrames binding

Verified 2026-09-13. Engine: HeyGen's [HyperFrames](https://github.com/heygen-com/hyperframes), Apache-2.0. Use CLI `hyperframes@0.8.37`, Node 22+, Python 3.9+, Git, and FFmpeg/ffprobe. First render may download headless Chrome (93 MB observed). Local rendering needed no paid account or API key in the neutral probe. Capture, media catalogs, TTS, and optional providers have their own requirements. Do not expose authentication output containing credentials.

Source commit: `e30992fdb8c6278db6afde2b5deeb7908835c524`.
Product skill SHA-256: `c3f83d1e61d5362dc8c815ccc2f23bee00c6d7bff221654ca69618c64624d4d4`.
Upstream manifest short hash: `b1597ed153cafcc7` (not a full file SHA-256).

Obtain a separate local source checkout, once, using an unused directory:

```sh
git clone https://github.com/heygen-com/hyperframes.git hyperframes-source
git -C hyperframes-source checkout --detach e30992fdb8c6278db6afde2b5deeb7908835c524
git -C hyperframes-source rev-parse HEAD
git -C hyperframes-source status --porcelain
shasum -a 256 hyperframes-source/skills/product-launch-video/SKILL.md
npx --yes hyperframes@0.8.37 --version
```

Require that exact commit, a clean checkout, the exact SHA above, and CLI version 0.8.37. If they differ, stop to inspect the drift. Do not run `skills update`: it pulls current main, not this pin. Use `HYPERFRAMES_SKIP_SKILLS=1` when scaffolding with the pinned CLI to avoid global skill refreshes. Never overwrite an existing project with init:

```sh
HYPERFRAMES_SKIP_SKILLS=1 npx --yes hyperframes@0.8.37 init videos/product-name --non-interactive --example=blank --skill=product-launch-video
```

`npx` can still require registry access after caching. Provision the exact dependency locally if offline operation is required; do not substitute `latest`. Localhost binding and browser execution permissions are required. `--skill=product-launch-video` is attribution telemetry, not an approval lock.

## Read the smallest relevant source

Paths below are relative to the pinned source's `skills/` directory:

- `product-launch-video/SKILL.md`: source workflow, capture hard stops, setup and composition helpers.
- `hyperframes-creative/references/story-spine.md`, `design-spec.md`, and `frame-presets/`: story and brand-aware composition.
- `product-launch-video/references/visual-design.md` and `motion-language.md`: time-coded direction and meaningful motion.
- `hyperframes-animation/blueprints-index.md` and `rules-index.md`: select a shot/rule, then read that recipe only.
- `hyperframes-core/references/frame-worker-core.md`: composition/background and seek-safe authoring contract.
- `hyperframes-cli/references/preview-render.md`, `lint-validate-inspect.md`, and CLI help: seek diagnostics and rendering.
- `media-use/` and `product-launch-video/scripts/audio.mjs`: only when approved audio/media is needed.

This skill adapts the upstream workflow, rather than installing its orchestrator unchanged. It combines the plan and layout review into one designed HTML storyboard approval. It does not inherit upstream's autonomous bypass, automatic global updates, mandatory provider sign-in for a silent project, or extra approval questions. The user's approval of the designed storyboard authorizes production and routine QA; ask again only for material revisions or an explicit user review requirement. Reuse upstream technical contracts and helpers where they fit; do not introduce duplicate timing/render infrastructure.

For URL capture, use `npx --yes hyperframes@0.8.37 capture <URL> -o ./capture --json`. A failed command, `ok:false`, or `capture/BLOCKED.md` blocks that capture path. Little text plus an empty asset catalog is not usable evidence. Continue using a supplied brief/assets only when that was already the source or the user chooses that fallback. Honor denied access.

For an upstream silent project use `music: none` in `STORYBOARD.md` and no `SCRIPT.md`; this is upstream's canonical no-audio marker. Keep `project.json` as the approval source of truth and synchronize any upstream helper inputs from it. An audio duration change affects approval; do not silently overwrite approved timing after TTS.

## Verified command surface

From the video project directory:

```sh
npx --yes hyperframes@0.8.37 lint
npx --yes hyperframes@0.8.37 check
npx --yes hyperframes@0.8.37 keyframes . --json
npx --yes hyperframes@0.8.37 snapshot --at 2.5,4.9,5.2
npx --yes hyperframes@0.8.37 preview --background
```

Choose snapshot times for the actual scene midpoints, each cut just before/after, first frame, and ending. Final render is called by the approval helper using `render --quality high --fps <approved-fps> --output <new-path>`. The output check uses ffprobe. No render command itself authenticates storyboard approval.

## Evidence and limits

A neutral one-second local composition passed lint, runtime/layout/motion checks and rendering: H.264/yuv420p, 1920×1080, 30 fps, 30 frames, 1.000 seconds. It verifies the engine path, not a finished product film. Upstream capture/packet tests passed 10/10. Thirteen upstream audio tests failed from a space-containing workspace because their URL pathname kept `%20`; audio quality and provider operation remain unverified. Do not claim those tests passed or infer a general audio engine defect.

The framework is Apache-2.0; its dependency licenses still apply. The separate [HyperFrames launch showcase](https://github.com/heygen-com/hyperframes-launch-video/tree/930f89186b8e155d632d9afe49054c02d4d7d85a) is reference-only and has no root license. Do not copy its code or media. This package contains original helper code and fictional UI, not redistributed upstream source.

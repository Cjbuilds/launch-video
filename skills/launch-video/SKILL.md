---
name: launch-video
description: Create a product launch video from a URL, product brief, or supplied assets using HeyGen HyperFrames. Research the product and brand, write a short script, show designed HTML storyboard frames for explicit approval, then animate, render, and inspect the MP4. Use for launch videos, SaaS promos, feature reveals, and product demos; do not use for general video editing.
---

# Launch video

Turn a real product into a clear visual story: what hurts, what changes, how it works, and what to do next. Use HyperFrames as the engine. Keep the user's selected model as the manager. Do not replace the engine or create a video editor, template library, or animation framework.

## 1. Ground the brief

Read the user's supplied brief, product, assets, and existing project first. Resume existing work. Ask only for missing facts that would change the video; do not repeat answered questions. A product name alone is insufficient evidence for feature claims. With sparse input, resolve the audience, useful promise, and closing action before writing the storyboard.

For a supplied URL, inspect the actual product and official brand sources. Use HyperFrames capture where appropriate; follow the pinned capture failure rules in [upstream.md](references/upstream.md). Never invent a replacement site when capture fails. For a show-it-as-is video, use the actual screen as the base. Preserve exact supplied copy unless editing is authorized. Record claims, sources, asset rights, and any assumptions in a short `BRIEF.md` in the video project. Never include private material in a public demo without authorization.

Use the product's colors, type, density, and actual UI. Choose a specific visual direction with meaningful movement, readable type, and deliberate pacing. Read the upstream creative and motion references selectively. The [reference study](references/reference-study.md) illustrates techniques, not a mandatory house style. A fictional example must be explicitly labeled; do not turn it into an implied real customer result.

## 2. Prepare the project

Read [upstream.md](references/upstream.md) and verify the pinned source and CLI before relying on them. Use the upstream HTML composition contract, diagnostics, and rendering. Read only the needed domain references; do not copy the whole source tree into the deliverable or silently refresh to latest.

Create a dedicated video project. Define `project.json` using [project-format.md](references/project-format.md). Agree output dimensions, frame rate, duration, and audio choice in the storyboard. For X, verify the current official upload requirements before selecting the export. Default to a short, sound-off-friendly film; do not buy media or invoke a paid voice provider without authorization. Missing assets require a local, licensed replacement consistent with the brief or a concrete question, never a broken placeholder.

## 3. Design, show, and obtain approval

Write a lean script: one clear idea per scene, real product evidence, a useful payoff. Create a complete **static, designed HTML frame** for every scene with the actual proposed copy, layout, palette, and assets. Text descriptions and wireframe boxes alone are not the review artifact. Keep one continuous product example through the film. Show important UI at a readable scale and leave time to understand each action.

Each frame must be self-contained static HTML with inline CSS. Use local, declared image/font assets; see the format reference. Check the frames at full output size and at feed scale. Include exact headline, optional narration, duration, and intended motion in `project.json`, then run:

```sh
python3 <SKILL_DIR>/scripts/launch_video.py storyboard <PROJECT_DIR>
```

Open the resulting `storyboard.html` for the user. Review every frame yourself first. Ask for approval of the displayed version, or scene-specific changes. **Wait for explicit user approval before full animation or rendering.** Silence, a generic earlier “yes,” acceptance of the build idea, and automatic mode do not approve an unseen storyboard. A neutral technical renderer probe is allowed before this gate.

Only after the user approves the displayed version, record their actual decision:

```sh
python3 <SKILL_DIR>/scripts/launch_video.py record-approval <PROJECT_DIR> \
  --version <DISPLAYED_SHA256> --approver <USER_NAME> --decision '<ACTUAL_APPROVAL_TEXT>'
python3 <SKILL_DIR>/scripts/launch_video.py check-approval <PROJECT_DIR>
```

The receipt binds the manifest, frame bytes, assets, and generated storyboard. It records a human decision; it does not authenticate the speaker or interpret whether arbitrary text means approval. Never fabricate a receipt. Keep approval records private by default.

## 4. Animate the approved story

Use the pinned HyperFrames animation rules and blueprints. Reuse the approved designed frames as the composition basis. Each scene should reveal an actual action and result; movement must support the story. Use seek-safe timelines. Read the relevant upstream rule before implementing a technique. Match position, scale, direction, and opacity across a continuous transition. Avoid motion that obscures the product or flashes rapidly.

Create `index.html` and one subcomposition per approved scene as specified in the format reference. Keep IDs/order, exact text, timing, dimensions, and asset identity faithful to the approved board. The helper checks structure, text, and timing; inspect visuals and assets yourself. It cannot prove semantic fidelity from source alone. Do not edit approved frames to conceal drift.

A requested story, copy, asset, layout, duration, or audio change requires a revised storyboard and renewed approval. Preserve the previous version. Motion repairs that implement the already approved intent can proceed, then rerun the affected checks. If working with agents, give each one an exact scene and nonoverlapping file ownership; the manager owns composition and QA.

## 5. Inspect, render, and deliver

Use the pinned CLI from the project directory for `lint`, `check`, `keyframes . --json`, and `snapshot --at <scene-midpoints-and-transition-boundaries>`. Inspect every scene, the beginning/end, and both sides of each cut. Open `preview --background` and watch the complete motion at normal speed. Check readability, timing, overlap, clipping, asset loading, transition continuity, and sound-off comprehension. For audio, also check rights, sync, clipping, and the ending. Passing static checks does not prove visual quality.

After approval and pre-render visual QA, render through the helper:

```sh
python3 <SKILL_DIR>/scripts/launch_video.py render <PROJECT_DIR> --output output/video.mp4
```

This invokes HyperFrames 0.8.37 and ffprobe, checks the export against the approved dimensions/fps/duration/audio, and writes a `.qa.json` receipt. Its visual QA status remains pending: inspect the **actual MP4**, extract representative frames, and watch complete playback before delivery. Report evidence separately from judgment. Do not mark the result finished because encoding succeeded.

On failure, read the error, fix its concrete cause, and repeat the affected check. Preserve existing videos; choose a new output path after inspecting a partial failed render. Never switch engines, use old output as a new result, or hide a missing capability. If blocked, state what remains and provide the reviewable work already completed.

Deliver the MP4, designed storyboard, scene IDs for revisions, dimensions/duration/audio, reproducible commands, and honest QA notes. Publish only when requested. Do not promise “viral,” one-shot quality, or unmeasured time/token savings.

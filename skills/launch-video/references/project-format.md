# Video project contract

The bundled helper uses Python's standard library. `<SKILL_DIR>` is the installed `launch-video` directory; `<PROJECT_DIR>` is your dedicated video directory. Quote paths containing spaces. Do not put generated videos inside the installed skill.

Minimal `project.json` (replace the fictional facts and actual designed frame):

```json
{
  "schemaVersion": 1,
  "product": {
    "name": "Example",
    "fictional": true,
    "summary": "An explicitly fictional product for a demonstration.",
    "audience": "Small product teams",
    "promise": "One clear next step",
    "cta": "Try Example"
  },
  "direction": "Warm white, ink type, one blue action, readable product UI.",
  "brand": {
    "basis": "Original fictional brand",
    "colors": {"ink": "#111111", "paper": "#FFFFFF", "accent": "#2457FF"},
    "font": "Arial, sans-serif"
  },
  "video": {"width": 1920, "height": 1080, "fps": 30, "audio": "none"},
  "scenes": [
    {
      "id": "hook",
      "duration": 4,
      "copy": "One clear next step.",
      "narration": "",
      "motion": "Bring the customer note into focus, then reveal the next action.",
      "frame": "frames/01-hook.html",
      "assets": []
    }
  ]
}
```

Every scene needs a unique stable ID, duration greater than zero and at most 180 seconds, exact headline present in its frame, and a concrete motion description. `narration` may be empty for a silent film. `audio` is `none` or `included`; included audio needs documented sources/rights and visual script review. Total duration is the sum of scenes. Choose export specifications for the actual destination, not a guessed platform limit. Check [X’s official video guidance](https://help.x.com/en/using-x/x-videos) for X exports. On 2026-09-13 it listed a web maximum of 1920×1200 (1200×1900 portrait), 40 fps, and 25 Mbps; verify again when delivering. The Relay proposal uses 1920×1080 at 30 fps.

Frames are complete static HTML pages with inline CSS. Design at the export aspect ratio and scale the whole composition proportionally in the storyboard. Check the headline and important UI at feed size. Do not hide important text below an overflow boundary. Use original HTML/CSS for product UI and diagrams; use licensed assets for images, logos, and photography.

Asset paths in `assets` and `frame` are project-relative. References inside a frame resolve relative to that HTML file. The helper embeds **quoted `src` attributes and CSS `url(...)`** from the declared assets as data URIs. Use these supported forms; no unquoted resource attributes, external stylesheets, scripts, embeds, `srcset`, CSS imports, external SVG image/use/filter references (only same-document fragments are supported), or remote images. Inline styles and local font files are supported. The resulting storyboard is sandboxed static HTML, not a full HTML security sanitizer. Open only project content you have inspected, and verify that it works offline.

Example: `frames/01-hook.html` uses `<img src="../assets/logo.png">` and the scene lists `"assets": ["assets/logo.png"]`. Missing or undeclared resources stop generation. Hashes include every declared asset's bytes.

## Files and revisions

- `BRIEF.md`: source facts, exact user scope, references, rights, and assumptions.
- `project.json`, `frames/`, `assets/`: canonical designed storyboard input.
- `storyboard.html`: current complete HTML review artifact.
- `storyboards/<version>.html`: immutable generated versions; keep approved history.
- `approvals/<version>.json`: local human decision receipt. Keep private by default.
- `index.html`, `compositions/`: approved animated HyperFrames output, created after approval.
- `output/`: new MP4s and technical `.qa.json` receipts.

The manifest, frames, and assets determine the version. A generator change that alters HTML for an existing version stops rather than overwriting its archive. Preserve the reviewed artifact; migrate it deliberately and obtain renewed approval. Do not hand-edit the current generated HTML.

## Animated composition contract

Use the pinned engine's real composition contract. The root `index.html` needs `data-composition-id`, `data-start="0"`, total `data-duration`, and approved `data-width`/`data-height`. Add one timeline child per approved scene, in order:

```html
<div id="hook" class="clip" data-composition-id="hook" data-start="0" data-duration="4"
     data-track-index="1" data-composition-src="compositions/01-hook.html"></div>
```

The next scene starts at the previous end. Each subcomposition uses the same approved text as its designed frame and the engine's required root/timeline attributes. Document titles are metadata and are excluded from the visible-copy comparison. Put full-bleed grounds on a full-duration clip, following upstream, so clip gating does not create black flashes. Use upstream seek-safe animation APIs and inspect actual rendering.

The helper compares root dimensions/total duration, scene IDs/order/timing, matching mount/subcomposition IDs, and normalized body text against the approved frames. It does **not** prove layout, asset identity, animation semantics, audio content, or absence of hidden text. Check those through source review, snapshots, and playback. The render receipt's visual QA is deliberately pending until that work is done.

A failed render preserves any partial output. Inspect it, repair the cause, and select a new output filename. An existing output is never overwritten. A video that fails ffprobe checks has no success QA receipt.

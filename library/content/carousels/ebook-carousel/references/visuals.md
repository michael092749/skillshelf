# Designer / GPT Image agent

Use the installed imagegen skill and built-in GPT Image tool. This is a still-image
workflow, not HyperFrames/video production. Read brand/style-guide.md and inspect
the actual candidate files under references/characters/, references/layouts/ and
references/ctas/ with the available image viewer. Copy only used references into
the project's assets/references/ and identify their roles in the prompts.

## Art direction

Use the project palette; optional defaults are warm ivory (#eee9e0), forest green
(#344236) and dark ink (#252923). Keep generous
space, editorial serif headlines and clear sans-serif body copy. Use the project's authorized
character reference when a person helps the story. If none exists, use objects,
diagrams and typography rather than requiring a private character sheet. Identity consistency does
not mean pasting the same portrait into every slide.

Plan visual variety before generation. Examples include three-quarter or profile
views, hands performing an ordinary routine, overhead objects, ingredient still
life, annotated collage, an explanatory diagram, or a sourced chart. Select the
forms that explain the lesson; not every slide needs a face. Change framing,
camera distance and placement while keeping the series coherent. Avoid repeating
one face crop or one layout across the entire carousel.

Use a real verified book cover if accessible and authorized by the store ownership.
If a cover mockup is needed, label it as a mockup in the project and avoid invented
edition details or reader outcomes. Illustrative portraits are not evidence of
results. Never fabricate before/after images, data, charts, credentials or studies.
Numerical charts require a source and units; otherwise use a clearly conceptual
diagram without made-up quantities. Essential chart/label accuracy must survive
visual inspection; simplify if the generator cannot render it reliably.

## Per-slide prompt contract

Write idea/image-prompts.md before generating. Every slide needs its own detailed,
coherent specification, rather than a generic style paragraph reused six times:

1. Slide's learning goal and role in the sequence.
2. Exact reference paths, roles (identity/layout/palette) and identity invariants.
3. Scene, subject/action, camera viewpoint/distance, expression where applicable,
   environment, lighting and material/texture treatment.
4. Layout: headline/body/visual placement, hierarchy, generous text-safe margins,
   whitespace, sequence marker and how this differs from adjacent slides.
5. Palette and typography direction consistent with the brand.
6. Exact approved text, punctuation, labels and CTA quoted verbatim. No additional
   slogans or “helpful” medical statements generated inside the image.
7. Diagram/chart source values and labels when present; distinguish conceptual
   visuals from quantitative claims.
8. Canvas: portrait 9:16, with final exports at 1080 × 1920, matching every slide.
   A larger generation canvas is fine; request the composition ratio in the prompt.
   Tool parameters must follow the live tool schema; do not invent size arguments.
9. Acceptance criteria: legible on a phone, complete copy, correct reading order,
   natural anatomy, reference consistency, no clipping or unintended logos.

Supply reference images through the tool's supported reference mechanism, after
viewing them. Text naming a path alone does not attach that reference. Generate
separate slides, not a contact sheet that must be cut apart. For tools with only
recent-image references, include the smallest set covering the intended inputs.

## Slideshow canvas and publishing route

Default: one consistent **1080 × 1920 portrait 9:16** set for Instagram and TikTok
photo slideshows. This is the project's shared design target, not a claim about a
platform's maximum ratio. Keep important text about 6% inside the canvas, with
extra room near the bottom; confirm actual UI overlays in a publisher preview
when available. At phone width, favor a short headline and compact body over
shrinking text. PNG masters use RGB; every slide has the same dimensions. The helper converts
mode, not ICC color profiles; use sRGB sources or verify color management when
a source has another embedded profile.

Use the shared 9:16 masters for both platforms. Keep delivery-format derivatives
in separate platform folders and review their actual files.

Publishing format depends on the actual route. The [TikTok photo API media guide](https://developers.tiktok.com/docs/en/content-posting-api-media-transfer-guide)
was checked 2026-10-02: it lists JPEG/WebP and a 20 MB per-image limit. Therefore
PNG masters alone are not API-upload-ready. If that route is intended, make a
separate JPEG set, inspect it and record file sizes. Native-app acceptance can
differ; inspect its current requirements rather than assuming the API's limits.
For Instagram, [photo-resolution help](https://help.instagram.com/1631821640426723)
was rate-limited during this skill review; 9:16 remains our production choice.
TikTok's [carousel ad playbook](https://ads.tiktok.com/business/library/Image_Ads_Carousel_Ads_Playbook.pdf) favors
9:16 and safe zones for ads; it is not an organic-photo requirement.

## Generation, export normalization and delivery

Each worker gets one initial call per assigned slide. Save the actual returned
originals in assets/generated/, plus job IDs, prompts, copy revision and paths.
Use explicit reference paths when supported; inspect those references first.
Review generated copy and visuals before accepting an image for export.

Normalize small canvas rounding differences as a deterministic export operation,
using scripts/normalize_slides.py. Preserve the original pixels in assets/; write
new RGB PNG files in exports/. Proportional fitting plus minimal ivory padding
preserves content; no stretching, content cropping or upscaling. The default
helper rejects ratio mismatches greater than 1% and undersized originals so a
wrong composition goes back to design rather than being disguised by padding.
A 1122 × 1995 generation is a routine normalization case, not a creative failure.
Record source/output dimensions, hashes and transform in run.json or a linked
export report. Reinspect the final file after normalization.

Run with the same selected originals for each delivery format, for example:

```bash
python3 "$SKILL_DIR/scripts/normalize_slides.py" "$PROJECT/assets/generated" "$PROJECT/exports"
python3 "$SKILL_DIR/scripts/normalize_slides.py" "$PROJECT/assets/generated" "$PROJECT/exports/tiktok" --format jpeg
```

Run the second command only when a JPEG delivery set is needed. Input and output
directories must be non-overlapping; do not use exports/ as input for its own
nested tiktok/ output. Keep rejected generations and repair alternatives outside
the selected originals directory. Use --help for current options.

The helper requires Pillow; use an available
project environment or an isolated tooling environment, and report a missing
dependency. This workflow explicitly calls for local sizing/format preparation;
creative edits remain with imagegen. Respect any stricter active tool/runtime
restriction and disclose it if it prevents normalization. Do not run an identical
creative size retry when the tool has already demonstrated the same limitation.

Exports stay numbered in slide order: exports/01-topic.png through NN-topic.png.
For a publisher-compatible JPEG set, use a separate folder such as
exports/tiktok/ and list its profile/files in run.json. Preserve current output
before replacement; the helper refuses to overwrite an existing delivery set.
Parent merges worker results, normalizes, then performs [image review](review.md).
At most two creative repairs are shared across the run. No external paid-provider
fallback is implied. A genuine unresolved visual or export blocker keeps draft.

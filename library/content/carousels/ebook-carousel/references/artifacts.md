# Artifact contract

One project per selected idea. Use the next unused three-digit ID across both
production folders and content-tracker.csv; keep the ID after publication. A
parent checks availability again immediately before making the new directory.
Concurrent agents do not allocate IDs or edit the tracker.

```text
carousels/NNN-topic/
  README.md
  run.json
  qa.md
  reviews/
    01-review.json ... NN-review.json  hash-bound final-image checks
  research/
    performance.json
    performance-review.md
    metricool/                      relevant raw responses and field definitions
    sources.json
    findings.md
    candidates.md
    tag-rationale.md
  idea/
    brief.md
    storyline.md
    funnel.md
    image-prompts.md
  assets/
    references/
    generated/
  captions/
    instagram-description.txt
    tiktok-description.txt
    tiktok-title.txt                 optional
  exports/
    01-topic.png ... NN-topic.png
    tiktok/                         optional JPEG delivery set for API routes
    contact-sheet.jpg               optional; inline multi-image preview also works
  archive/                          create only when superseding files
```

README links to the final image folder, caption folder, source packet and selected product.
It states file readiness, actual publishing state and any bio-link setup needed.
Do not confuse a generated mockup with a product asset or an image with a video.

## run.json

Use this minimal shape, with real run values. Paths are relative to the project.
Optional fields can record references, provider jobs, superseded versions and
parent/child handoffs. All timestamps use ISO 8601 with timezone.

```json
{
  "schema_version": 1,
  "content_id": "005",
  "format": "carousel",
  "status": "draft",
  "copy_revision": "v1",
  "export_profile": {"width": 1080, "height": 1350, "format": "png", "mode": "RGB"},
  "publishing_routes": {"tiktok": "unselected"},
  "topic": "Selected original angle",
  "audience": "Audience and language from the project brief",
  "merchant_hosts": ["publisher.example"],
  "product": {
    "title": "Exact verified ebook title",
    "url": "https://publisher.example/",
    "observed_at": "2026-10-02T12:00:00Z",
    "source_id": "P01"
  },
  "funnel": {
    "destination_url": "https://publisher.example/",
    "platforms": {
      "instagram": {"account": "your-instagram-account", "bio_link_verified": false, "observed_url": null, "observed_at": null},
      "tiktok": {"account": "your-tiktok-account", "bio_link_verified": false, "observed_url": null, "observed_at": null}
    }
  },
  "publication_prerequisites": {
    "instagram": ["Set or verify the account bio link before publishing."],
    "tiktok": ["Set or verify the account bio link before publishing."]
  },
  "stages": {
    "performance": "complete",
    "research": "complete",
    "writing": "complete",
    "images": "pending",
    "captions": "pending",
    "review": "pending"
  },
  "generation": {
    "provider": "built-in GPT Image",
    "initial_calls": 0,
    "repair_calls": 0,
    "jobs": []
  },
  "slides": [],
  "review": {
    "all_images_inspected": false,
    "copy_verified": false,
    "claims_verified": false,
    "funnel_verified": false,
    "reference_consistency": false,
    "visual_variety": false,
    "mobile_readability": false
  }
}
```

The values above explain the shape, not evidence of a completed run. Replace the
example product URL with the actual canonical ebook page. `funnel_verified` means
the chosen destination resolves to the appropriate public product/library and
matches the CTA; it does not mean a purchase was made or a bio changed.

Bio verification is per platform. A checked Instagram bio does not verify TikTok.
For each platform store the account, observed link and timestamp, or a specific
publication prerequisite. Account names above are examples; verify the configured account before relying
on any profile evidence.

Each final slide entry contains `path`, `sha256`, and `review_path`. Number in
slide order, e.g. `{"path": "exports/01-topic.png", "sha256": "actual digest",
"review_path": "reviews/01-review.json"}`. The review binds to that exact path
and hash; its shape is defined in [review.md](review.md). Transforming or replacing
an export requires a fresh review. Record copy revision and per-slide assignments
in run.json before dispatching; only parent merges worker results.

Record the export profile (default 1080 × 1350 RGB PNG), source/output dimensions
and hashes, normalization report path and any publisher-specific set in run.json.
Declare `publishing_routes.tiktok` as `api`, `native_app`, or `unselected`.
`unselected` means the publishing route is a handoff prerequisite, not that PNG
masters are proven accepted by every route. For `api`, the validator requires
`delivery_sets.tiktok = {"format": "jpeg", "slides": [...]}`. Each entry has
`path` (`exports/tiktok/01-topic.jpg` etc.), `sha256`, `source_sha256` (the matching
canonical PNG hash), and `review_path` (`reviews/01-tiktok-review.json` etc.).
Record conversion provenance separately; a source hash mapping identifies the
canonical slide, not proof of equivalent pixels. Inspect each JPEG's copy and
visuals, and record its own path/hash in the review. Validation requires Pillow
for declared API JPEG sets, RGB, matching canvas and at most 20 MB per image.

Canonical exports default to exact 1080 × 1350. If the user explicitly requests
larger 4:5 files, declare width/height in export_profile and validate against that
profile; the normalization helper itself deliberately targets 1080 × 1350.
Two or three slides are permitted for an explicit shorter brief; normal runs use
4–6. A 9:16 variant requires a separate profile/validator adaptation. Keep originals under assets/generated/ and edits under archive/ when
superseded. reviews/ contains only current checks; historical reviews go to archive/.
Research stage completes only after live Exa MCP research and explicit reporting
of inaccessible sources; images completes only after actual files exist. Keep
status draft on failure; ready is for prepared files, never implicit publication.

## sources.json

Top-level object: `queries` array and `sources` array. Each query has `query`,
`provider`, `observed_at` and optional filters/run ID. Each source has a stable
packet `id`, canonical `url` or existing `local_path`, `provider`, `observed_at`,
`published_at` (null if unknown), `access` and `supports`.

For live Exa results, use provider `exa-mcp`; distinguish supplemental web/browser
and local/wiki records. Keep exact locators/excerpts, field-level metrics and
limitations when available. For social examples add platform, account, format,
observed hook/CTA, disclosure and unknown-as-null metrics. Record keywords/tags
with evidence type, geography/window and source IDs in findings.md/tag-rationale.md.
Exa discovery followed by a browser fetch should retain both steps, not relabel
the browser's data as an Exa extraction.

Every factual slide statement maps to source IDs in storyline.md. Product.source_id
resolves to the freshly inspected product record. Findings include novelty checks
and explain which facts are verified, inferred, historical or unavailable.

## performance.json

Object with `observed_at`, `window` (`from`, `to`, `timezone`) and `platforms`.
Both `instagram` and `tiktok` entries contain `status` (`ok`, `no_data`, or
`unavailable`), `attempted_at`, `account`, `brand_id`, `metrics` and `rows` arrays.
An `ok` entry has actual rows and requested metric definitions/order; the others
contain a nonempty `reason`. Use null for missing measurements. Store relevant raw
responses under research/metricool/ and link them; exclude tokens and unrelated
account personal data. Record connector scope and actual observation timestamps. Per platform, an
`analysis` object records `decision` (`analyze`, `skipped_low_views`,
`skipped_sparse_sample`, or `skipped_unavailable`), `reason`, `min_views_per_post`,
`min_comparable_posts`, `comparable_posts` and the chosen views field ID. Skipping
analysis does not change genuine raw `status=ok` to a connection failure. A short
skip report completes performance setup; no detailed analytics is required.
`stages.performance=complete` means a real attempt and decision brief were saved,
including an unavailable-data outcome. It never means all funnel data was available.

## QA and delivery

qa.md records the reviewer, observation timestamp, all-slide inspection, claim
checks, dimensions, text legibility, reference/shot variety, destination check,
caption/tag checks, plain-language edit mode, unresolved issues and validator
result. Set review flags only after performing the corresponding checks.

The final handoff is the project folder name/path, with two clearly linked folders:
exports/ contains the ordered final images; captions/ contains copy-ready platform
descriptions and hashtags. Keep hashtags in each platform description TXT so the
whole post can be copied at once. Keep research and working assets in their own
project folders. Do not create or return a ZIP. Historical archives are preserved.

Ready completion updates content-tracker.csv (`format=carousel`, platforms
`Instagram; TikTok`, status `ready`, actual project_path and actionable next_action).
Do not append a publication log row until separately authorized publishing has
returned an actual platform URL and date. Every new run starts with the Metricool
review above; it must not invent analytics or automatically republish.

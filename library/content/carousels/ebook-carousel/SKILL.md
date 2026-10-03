---
name: ebook-carousel
description: Research and produce a ebook image carousel with five or six slides and Instagram/TikTok captions. Use for a new carousel or revision, including evidence, writing, image generation, visual review, and slideshow export preparation.
---

# Ebook Carousel

When the workspace has its own `skills/ebook-carousel/SKILL.md`, read and follow
that project entrypoint instead of this portable edition. Its references own the
project templates, render profiles, learning loop and publishing integrations.
Keep this catalogue installation separate from that project-owned bundle.

Choose one fresh, researched idea and deliver a ready-to-publish image carousel.
Use the user-selected publisher and verified public catalogue as product sources.
Read [setup.md](references/setup.md) on first use or in a new workspace; it defines
the required brand inputs, optional analytics/wiki inputs and tool dependencies.
Finish files; publication and profile changes are separate tasks.

## Defaults and capabilities

- Use the configured audience, language and topic priorities. Choose a life stage
  only when supported by the brief and evidence.
- Normally deliver 5–6 ordered still images, never more than six, plus separate Instagram
  and TikTok captions. Default shared slideshow export: **1080 × 1920 (9:16)**.
- Use the project brand guide and authorized references with varied layouts. The
  included neutral ivory/forest-green palette is an optional starting point.
- Use live **Exa MCP** for research and built-in **GPT Image** via `imagegen` for
  creative generation. One initial call per slide, at most two targeted creative
  repairs per run. Routine export sizing is a separate step; see visuals.md.
- Use available subagents for research, writing, image work, captions and review.
  This skill authorizes delegation within those tasks. Read
  [parallel handoffs](references/orchestration.md) when dispatching work.
- Discover actual tools and schemas at runtime. Skills supply instructions;
  `agents/openai.yaml` supplies discovery/UI metadata, not running agents or tools.
  Missing analytics permits a cold start; missing Exa or image generation leaves
  the affected production stage draft. Report exact limitations.

## Context and routing

Locate the workspace through README.md and content-tracker.csv. Read workspace
instructions, publication reports/log, brand/style-guide.md, research/README.md
and relevant collection index when present. Fresh workspaces follow setup.md.
Read an existing production's README and local instructions before editing it.
Freshly inspect the configured publisher catalogue; older local product notes may be stale. Store outcome
claims are marketing claims, not clinical evidence.

If the user supplies an existing wiki vault, consult its instructions and index
read-only, then use its installed query skill/tooling. A wiki is optional; continue
with project research when absent. Do not assume a home-directory path, create a
vault or ingest sources as a side effect.

Load [skill-map.md](references/skill-map.md) only for the current stage's references,
including the optional founder-skills resources. For skill maintenance, it also
links the packaging standards. Do not load entire libraries into each agent.

## Production workflow

For a visual overview of stages, parallel work and repair paths, see the
[workflow flowchart](references/workflow.md).

1. **Parent — analytics triage.** Read [performance.md](references/performance.md).
   Fetch a fresh minimal account/post snapshot. When views are low, **skip detailed
   performance analysis**, save the reason and proceed with research. This never
   skips image review. Save the run-specific snapshot and a short creative test.
2. **Researcher.** Read [research.md](references/research.md). Use Exa MCP to verify
   the catalogue, audience question, clinical claims when relevant, competitor
   examples and keyword evidence. Return a source packet and 3–5 ranked angles,
   with access gaps and the triage brief. Completion requires live evidence.
3. **Parent — select and allocate.** Check novelty against actual hooks/captions,
   unpublished productions and known live posts. A renamed lesson is not new.
   Allocate the next unused three-digit ID across reels/, carousels/ and tracker.
   Create carousels/NNN-topic/, persist the [artifact contract](references/artifacts.md),
   add a draft tracker row and save reusable evidence upstream without overwriting.
4. **Writer.** Read [writing.md](references/writing.md). Write the exact slide text,
   source mapping, product bridge and CTA into idea/. Parent checks claims and
   locks one copy revision before image calls. Routine approval stays with parent.
5. **Image workers and caption writer — parallel after copy lock.** Read
   [visuals.md](references/visuals.md) and the caption section of writing.md.
   A design lead resolves shared styling and per-slide prompts. Distribute
   independent slides across available agents; captions can run alongside them.
   Persist each returned image and its provenance before another generation.
6. **Export preparation.** Follow visuals.md to preserve originals and normalize
   selected slides to one slideshow canvas. Small pixel-rounding differences
   are export issues; avoid repeated creative generations for them. Inspect the
   actual final files, including any changed by normalization.
7. **Image reviewer, then parent.** Follow [review.md](references/review.md).
   Review every slide at full resolution and phone scale, then the ordered story.
   A separate reviewer can inspect completed slides while others generate.
   Parent reconciles findings, claims, captions, offer and final files. Repairs
   invalidate affected reviews; only parent allocates the shared repair budget.
8. **Validate and hand off.** Run the validator below. Mark ready only after the
   artifact and factual/visual checks pass. Update tracker next_action with
   publication and any platform-specific bio/disclosure prerequisites. Link the
   project, exports/ and captions/; no ZIP, scheduling, publishing or DMs.

## State and revisions

Use run.json for stages, copy revision, assignments, source timestamps, generation
jobs, export transformations and review results. The parent owns shared files;
workers own only assigned paths. Resume the first incomplete stage and preserve
accepted artifacts. Check existing generation jobs before retrying.

Changed sources invalidate dependent claims; changed slide text invalidates that
slide and affected captions. Archive replaced files and recheck local paths.
Create a new ID for a new idea, never overwrite a posted production. If a stage
cannot complete, preserve the work as draft and name the missing dependency.

## Validation

Resolve SKILL_DIR to this skill's actual folder, then run:

```bash
python3 "$SKILL_DIR/scripts/validate_carousel.py" /absolute/path/to/carousels/NNN-topic
```

It checks artifacts, ordered unique PNGs, dimensions, review flags and captions.
It cannot judge claims, readability, identity or aesthetics; review.md supplies
that gate. Skill maintenance uses offline tests and the skill-creator validator;
it does not require live generation or publication.

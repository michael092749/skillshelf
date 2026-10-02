# Stage references and runtime discovery

Read only references useful to the current stage. Discover installed skill paths
from the host catalog; no absolute home-directory paths are assumed. Referenced
skills and repositories are optional guidance, not proof of available tools.

| Stage | Optional reference | Scope |
| --- | --- | --- |
| Research | Catalog research/exa/company-research | Evidence grounding and continuation of an existing Exa run; preserve live Exa MCP search/fetch requirements |
| Writing | Catalog content/writing skills | Story beats and progression; do not import a full article interview |
| Offer bridge | Catalog sales-and-marketing/hormozi-offer | Audience/problem/benefit heuristics; use only verified existing offers |
| Images | Host-installed imagegen skill, when present | Built-in generation and image inspection; use live schemas |
| Wiki | User-designated vault's local query skill | Read-only retrieval under its own contract |
| Editing | Installed no-ai-slop, when present | Otherwise apply writing.md's explicit plain-language pass |

These optional dependencies are not automatically installed by the carousel bundle.
If a reference is absent, the local stage briefs remain sufficient; missing Exa
or image tools are handled separately in [setup.md](setup.md).

## Founder-skills — optional stage references

Checked upstream at commit `a45931cad934dc6243a68f905485467935a4ad9a` on
2026-10-02. These three skills exist in the repository but were not found in the
local skill catalog or installed skill paths. Consult the specific source below
when useful; a link is not an installed capability. Use available fetch/browser
access; if unavailable, retain this workflow's local briefs and disclose the gap.

- **Researcher:** [competitor-intel](https://github.com/ognjengt/founder-skills/blob/a45931cad934dc6243a68f905485467935a4ad9a/skills/competitor-intel/SKILL.md)
  — dated competitor evidence, explicit unknowns and defensible comparisons.
  Apply to relevant carousel examples; retain this workflow's Exa MCP requirement.
- **Writer and caption writer:** [brand-copywriter](https://github.com/ognjengt/founder-skills/blob/a45931cad934dc6243a68f905485467935a4ad9a/skills/brand-copywriter/SKILL.md)
  — audience-aware framework selection, concrete benefits, one CTA and concise
  copy. Load its linked framework/style references only when selecting or editing
  that aspect of the narrative. Specificity must come from verified facts.
- **Researcher/parent selecting an angle:** [marketing-ideas](https://github.com/ognjengt/founder-skills/blob/a45931cad934dc6243a68f905485467935a4ad9a/skills/marketing-ideas/SKILL.md)
  — filter ideas for audience, goal, feasibility and product fit. Consult only the
  relevant portion of its linked idea database; our output remains one carousel.

Read these as scoped references, not a second orchestration workflow. Their full
procedures include argument-gathering pauses, broad company research and SaaS
assumptions that are unnecessary here. brand/style-guide.md, verified product
facts and the selected evidence packet supply the context. Do not invent numbers,
call an untested idea proven, create FOUNDER_CONTEXT.md, or install a pack merely
because it is referenced. A future user request to install skills is separate.

## Packaging and capabilities

Primary standards checked 2026-10-02:
[Agent Skills specification](https://agentskills.io/specification) and
[OpenAI skill documentation](https://learn.chatgpt.com/docs/build-skills).
The installed skill-creator instructions and its openai_yaml reference guide
Codex-specific metadata; use them when maintaining this bundle.

This bundle uses required SKILL.md frontmatter (`name`, `description`), optional
agents/openai.yaml for UI/invocation metadata, references/ for staged instructions,
and scripts/ for repeatable validation/export work. Project assets belong in the
production folder; there is no need for a skill assets/ directory without reusable
output assets. Keep the entrypoint short and link each reference by its trigger.
There is no need to split each worker role into a separately installed skill.

Agent parallelism is runtime behavior described in orchestration.md. Metadata
cannot grant tool permissions, spawn agents, install MCPs or enable unavailable
image capabilities. Discover actual callable tools and use their current schema.
Avoid unsupported frontmatter keys copied from another agent's skill dialect.

## Location and discovery

Canonical catalog path: `library/content/carousels/ebook-carousel`. Use the catalog
installer with `--skill content/carousels/ebook-carousel` to copy the complete
folder into a project's `.agents/skills/` (Codex), `.claude/skills/` (Claude), or
both. Keep the catalog itself outside discovery paths. Never assume a particular
clone location or write through read-only discovery mounts.

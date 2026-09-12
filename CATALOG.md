# Catalog map

The catalog contains 81 imported runtime skills, three catalog-authored skills
(the n8n router, the project skill picker, and the Karpathy guidelines), and one
preserved source variant. Only skills explicitly copied into a project's host discovery
directory become discoverable there.

| Domain | Canonical skills | Source/use |
| --- | ---: | --- |
| `engineering/` | 27 | Existing engineering tree, quality review, Claude-only engineering workflows, and LLM coding guidelines |
| `productivity/` | 9 | Handoffs, questioning, teaching, loops, and agent-facing writing |
| `google-workspace/` | 18 | Calendar, Docs, Drive, Gmail, Sheets, and cross-app workflows |
| `research/exa/` | 4 | Exa search, contents, API building, and company research |
| `research/knowledge/` | 1 | Knowledge graph visualization |
| `sales-and-marketing/` | 4 | Offers, lead generation, idea validation, and SEO auditing |
| `content/writing/` | 3 | Fragments, beats, and shape workflows |
| `media/video/` | 1 | Video shot planning assets and workflow (local-only; excluded from this repository) |
| `automation/n8n/` | 16 | Fifteen imported n8n skills plus the context-light router |
| `meta/` | 1 | Interactive picker that installs catalog skills into a project |

`variants/project-a/engineering/thermo-nuclear-code-quality-review` preserves a
newline-only source divergence. The canonical `library/engineering` copy is the
default and both are recorded in `SOURCES.toml`.

The default `n8n` bundle discovers only `n8n-project-router`; its 14 specialist
skills are vendored under `.agent-setup/references/n8n/`. Choose `n8n-full` only
when autonomous specialist discovery is worth the larger startup footprint.

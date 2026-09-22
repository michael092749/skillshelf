# Skills catalog index

This repository is a dormant catalog. Install only the skills a project needs;
the deterministic workflow is in [`SETUP.md`](SETUP.md), and the CLI's
`--help` is authoritative.

## Select and install

```bash
rtk python scripts/install_skills.py list types
rtk python scripts/install_skills.py list skills --type engineering --brief
rtk python scripts/install_skills.py install --project /path/to/project --host both --skill engineering/tdd --dry-run
rtk python scripts/install_mcp.py list --for-type automation/n8n
rtk python scripts/install_mcp.py install --project /path/to/project --host both --server exa --dry-run
```

Use `--host codex` for `<project>/.agents/skills/`, `--host claude` for
`<project>/.claude/skills/`, or `--host both`. Select exact catalog IDs with
`--skill` or complete types with `--type`; both options are repeatable.

## Selectable skill types

### `automation/n8n` (16)

Workflow design, nodes, code, expressions, agents, validation, MCP use, and
self-hosting.

`n8n-agents`, `n8n-binary-and-data`, `n8n-code-javascript`, `n8n-code-python`,
`n8n-code-tool`, `n8n-error-handling`, `n8n-expression-syntax`,
`n8n-mcp-tools-expert`, `n8n-multi-instance`, `n8n-node-configuration`,
`n8n-project-router`, `n8n-self-hosting`, `n8n-subworkflows`,
`n8n-validation-expert`, `n8n-workflow-patterns`, `using-n8n-mcp-skills`

### `content/writing` (3)

Writing fragments, beats, and article shape.

`writing-beats`, `writing-fragments`, `writing-shape`

### `engineering` (27)

Planning, implementation, debugging, testing, review, architecture, coding
guidelines, and repository setup.

`ask-matt`, `code-review`, `codebase-design`, `diagnosing-bugs`,
`domain-modeling`, `git-guardrails-claude-code`, `grill-with-docs`, `implement`,
`implement-spec`, `improve-codebase-architecture`, `karpathy-guidelines`,
`migrate-to-shoehorn`,
`prototype`, `research`, `resolving-merge-conflicts`, `retro`,
`scaffold-exercises`, `setup-matt-pocock-skills`, `setup-pre-commit`,
`setup-ts-deep-modules`, `tdd`, `thermo-nuclear-code-quality-review`, `to-spec`,
`to-tickets`, `triage`, `wayfinder`, `wizard`

### `google-workspace` (18)

Calendar, Docs, Drive, Gmail, Sheets, and cross-app workflows.

`gws-calendar`, `gws-calendar-agenda`, `gws-calendar-insert`, `gws-docs`,
`gws-docs-write`, `gws-drive`, `gws-drive-upload`, `gws-gmail`,
`gws-gmail-forward`, `gws-gmail-read`, `gws-gmail-reply`,
`gws-gmail-reply-all`, `gws-gmail-send`, `gws-gmail-triage`, `gws-gmail-watch`,
`gws-sheets`, `gws-sheets-read`, `gws-workflow-email-to-task`

### `media/video` (1)

Cinematic product-video planning and production with Remotion:
`video-shotcraft`

Vendored in full from the upstream Apache-2.0 repository at a pinned revision,
including its audio assets (their terms are listed in `assets/audio/ATTRIBUTION.md`).

### `meta` (1)

Interactive catalog picker that installs skills into a project:
`setup-project-skills`

### `productivity` (9)

Handoffs, interviews, teaching, loops, and agent-facing writing.

`claude-handoff`, `grill-me`, `grilling`, `handoff`, `loop-me`, `teach`,
`to-questionnaire`, `wait-what`, `writing-for-agents`

### `research/exa` (4)

Exa search, contents extraction, company research, and API integration.

`build-with-exa`, `company-research`, `exa-contents`, `exa-search`

### `research/knowledge` (1)

Knowledge-graph visualization: `graphify`

### `sales-and-marketing` (4)

Offer design, idea validation, lead generation, and SEO auditing.

`hormozi-offer`, `idea-validator`, `lead-generation`, `seo-audit`

### `second-brain-ingest` (1)

Always installed by the project picker, and deliberately its own type so no
category sweep can pull it in by accident:
`second-brain-ingest`

Run `list skills --type <type>` for exact IDs and current frontmatter
descriptions, adding `--brief` for one-line summaries. There are 85 selectable canonical skills across 11 types.

## Repository map

- `library/` — canonical selectable skill directories; each ID is its path
  below `library/`, such as `engineering/tdd`.
- `variants/` — preserved alternate implementations; opt in deliberately.
- `bundles/` — small project-profile manifests containing explicit skill
  selections.
- `integrations/` — `servers.toml`, the host-neutral MCP server registry
  (with a gitignored `servers.local.toml` overlay for personal entries), plus
  per-service trust, scope, and verification notes.
- `scripts/install_skills.py` — validated listing, selection, dry-run, and
  whole-directory copying.
- `scripts/install_mcp.py` — MCP server listing and merges into a project's
  `.mcp.json` and `.codex/config.toml`.
- `scripts/audit_catalog.py` — catalog integrity and context-footprint checks.
- `CATALOG.md` and `SOURCES.toml` — catalog summary and imported provenance.
- `reports/`, `templates/`, and `tests/` — measurements, setup templates, and
  deterministic checks.

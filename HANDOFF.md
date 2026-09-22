# Handoff: skillshelf — project-scoped agent skill catalog

**Generated**: 2026-09-12 22:08 UTC
**Branch**: `main` (clean, pushed to `origin/main`)
**Repo**: https://github.com/michael092749/skillshelf (PUBLIC)
**Status**: Ready for Review — shipped, three small follow-ups open

## Goal

A root-level catalog of agent skills that stays outside Codex/Claude discovery
paths, plus **one installed skill** the user runs at the start of a project that
asks which categories/skills they want and copies them into `.agents/skills/`
(Codex) and/or `.claude/skills/` (Claude). Published to GitHub with a README
that sells the idea.

## Completed

- [x] `library/meta/setup-project-skills/SKILL.md` — the interactive picker.
      Installed globally to `~/.agents/skills/` and `~/.claude/skills/`.
- [x] Sales/marketing consolidated: `marketing/seo/seo-audit` → `sales-and-marketing/`.
      Removed empty `library/marketing/`, `business/offers/`, `research/market/`, `quality/`.
- [x] Deleted an **untracked duplicate** `library/research/lead-generation/`
      (byte-identical to the sales-and-marketing copy) that was breaking the CLI.
- [x] `library/engineering/karpathy-guidelines/SKILL.md` (MIT, user-supplied text).
- [x] `list skills --brief` flag + test.
- [x] README rewritten as a product pitch (hook → problem → aims → install → use).
- [x] Scrubbed a private project name → `project-a` and `/home/dev/` → `~/` across
      `SOURCES.toml`, `MIGRATE.md`, `AGENTS.md`, `CATALOG.md`, `reports/`, `tests/`.
- [x] `library/media/video/video-shotcraft` vendored in full from upstream (Apache-2.0,
      pinned revision `5e71af3`), including audio assets; provenance in `SOURCES.toml`.
- [x] History squashed to one commit, pushed.

## Not Yet Done

- [ ] `README.md:141` still says `git clone https://github.com/<you>/skills.git ~/skills`
      → should be `michael092749/skillshelf`.
- [ ] Repo has **no description and no topics**. Command ready to run:
      ```bash
      gh repo edit michael092749/skillshelf \
        --description "Keep every agent skill in a library that costs nothing, then run one skill at the start of a project to install just what it needs — into Codex and Claude in one step." \
        --add-topic claude-code --add-topic codex --add-topic agent-skills \
        --add-topic ai-agents --add-topic developer-tools --add-topic context-engineering
      ```
- [ ] **No root LICENSE** over 82 skills imported from other people's repos/plugins.
      Only `karpathy-guidelines` (MIT frontmatter) and the vendored `video-shotcraft`
      (bundled Apache-2.0 LICENSE) declare terms. User has been told twice; it is their call.
- [ ] `/home/dev/test` was never set up. The picker questions were asked and cancelled.

## Failed Approaches (Don't Repeat These)

- **Do NOT trust `find`/`ls` output in this environment.** A hook rewrites shell
  commands through `rtk` (a token-reducing proxy), and it **silently dropped lines**.
  An early `find library/research -maxdepth 3` omitted `library/research/lead-generation/`
  entirely, which hid a duplicate skill that was failing catalog validation.
  Cross-check directory listings with Python:
  ```bash
  python3 -c "from pathlib import Path; [print(p.parent) for p in sorted(Path('library').rglob('SKILL.md'))]"
  ```
- **Do NOT document `conflict` as a dry-run output line.** The first draft of
  `setup-project-skills/SKILL.md` said conflicts print as `conflict<TAB>host<TAB>…` rows.
  They don't — the CLI raises, exits 2, prints only the conflicting paths, and copies
  nothing. Caught by actually running a conflict test, not by reading the code.
- **Do NOT scrub the working tree and push without rewriting history.** The scrub
  was done, committed, and *would still have leaked* — the two prior commits
  (`f6a114f`, `c61f9a9`) contained the private project name in 5 files (7 hits in
  `SOURCES.toml`).
  Fixed with `git checkout --orphan` + `git branch -M`, verified the tree hash was
  unchanged before pushing.
- **Do NOT gitignore `library/media/` to keep the repo small.** An earlier attempt left
  `index.md` documenting a type a fresh clone lacked and needed a special index marker.
  The tree is now vendored in full at a pinned upstream revision instead.

## Key Decisions

| Decision | Rationale |
|---|---|
| Picker lives in its own `meta/` type | Installing `--type productivity` shouldn't drag the bootstrapper into every project |
| One global copy of the picker | Chicken-and-egg: it must be discoverable before a project has skills. Deliberate exception to "catalog stays out of discovery paths" |
| Skill queries the CLI every run, never a memorized list | The index test can't catch drift *inside* a SKILL.md; live queries can't go stale |
| `--brief` instead of printing full descriptions | Descriptions are trigger-keyword paragraphs (seo-audit's is ~700 chars) and bury the choice |
| `karpathy-guidelines` in `engineering/`, not its own category | It's about writing code; a category of one costs a type in every listing |
| Private project name → `project-a`, not deletion | Preserves provenance traceability in `SOURCES.toml` without shipping a private name |
| `python3` (not `rtk python`) inside SKILL.md and README | The skill runs in other projects and the README is public; `rtk` is a machine-local proxy |
| Squash history rather than force-push later | Nothing had been pushed, so rewriting was free and total |

## Current State

**Working**: Everything. `audit_catalog.py catalog` clean; 15/15 tests pass.

- Local checkout and fresh clone are identical: **85 skills / 11 types**, including
  the vendored `media/video/video-shotcraft` (~54 MB / 970 tracked files).

**Broken**: Nothing.

**Uncommitted Changes**: None. `main` is clean and matches `origin/main`.
This `HANDOFF.md` is untracked — decide whether to commit or gitignore it.

## Files to Know

| File | Why It Matters |
|---|---|
| `library/meta/setup-project-skills/SKILL.md` | The deliverable. Question-first wrapper around the CLI |
| `scripts/install_skills.py` | `list types` / `list skills [--type] [--search] [--brief]` / `install` |
| `scripts/audit_catalog.py` | Structure + duplicate-name validation; `catalog_skills()` maps ID → Skill |
| `tests/test_install_skills.py` | Index-drift test (line ~38) |
| `index.md` | Human map. **Must** stay in sync or tests fail |
| `SOURCES.toml` | Import provenance; already scrubbed |
| `.gitignore` | Credentials and the personal MCP overlay only; nothing under `library/` is ignored |

## Code Context

**Skill ID → destination.** A skill's catalog ID is its path under `library/`;
the *runtime name* is its frontmatter `name`, and that is the installed directory:

```
library/sales-and-marketing/seo-audit/SKILL.md   # id: sales-and-marketing/seo-audit
  → <project>/.agents/skills/seo-audit/          # --host codex
  → <project>/.claude/skills/seo-audit/          # --host claude
```

**Duplicate runtime names are fatal catalog-wide.** `checked_catalog()` raises and
*every* CLI subcommand fails, including `list types`. This is how the stray
`research/lead-generation` was found:

```
ERROR: catalog validation failed:
  duplicate canonical runtime name lead-generation: research/lead-generation, sales-and-marketing/lead-generation
```

**Three install outcomes.** `copy` and `unchanged` print as rows; **conflict does not**:

```bash
$ python3 scripts/install_skills.py install --project . --host both --type sales-and-marketing --dry-run
ERROR: existing destinations differ or are not plain directories; nothing was copied:
  /path/.claude/skills/lead-generation
# exit 2, nothing copied — not even the skills that were fine
```

**`brief()` in `scripts/install_skills.py`** — first sentence, `>= 40` chars guards
against cutting at `e.g.`, then capped at 110 with an ellipsis:

```python
SENTENCE_END = re.compile(r"(?<=[.!?])\s")

def brief(description: str, limit: int = 110) -> str:
    text = " ".join(description.split())
    ends = [m.start() for m in SENTENCE_END.finditer(text)]
    cut = next((e for e in ends if e >= 40), ends[0] if ends else len(text))
    ...
```

**Index header format.** Each type header is `### `media/video` (1)`; the index test
parses the type and count from that header and compares against `list types`.

## Resume Instructions

1. Confirm the baseline:
   ```bash
   cd ~/skills
   python3 scripts/audit_catalog.py catalog
   python3 -m unittest discover -s tests -v
   ```
   - Expected: `canonical_skills=85 variants=1 bundles=10`, then `OK` (30 tests).
   - If a duplicate-name error appears: an untracked skill dir was added under
     `library/`. Find it with the Python `rglob` one-liner in Failed Approaches.

2. Fix the README clone URL (`README.md:141`), then commit and push.
   - Expected: `git push` succeeds; repo is already tracked to `origin/main`.

3. Set the repo description and topics with the `gh repo edit` command above.
   - Expected: `gh repo view michael092749/skillshelf --json description` is non-empty.

4. If asked to set up `/home/dev/test`: run the picker, or directly —
   ```bash
   python3 ~/skills/scripts/install_skills.py install \
     --project /home/dev/test --host both --type engineering --dry-run
   ```
   - Expected: 27 `copy` lines per host, then `would_copy skills=27 hosts=2 copies=54 unchanged=0`.

## Edge Cases & Error Handling

- **Editing a skill then reinstalling** → aborts as a conflict. Installs never
  overwrite. Delete the stale destination first, including the picker's own copies
  in `~/.agents/skills/setup-project-skills` and `~/.claude/skills/setup-project-skills`.
- **Adding a skill to `library/`** → `index.md` and `CATALOG.md` must be updated in
  the same change or the index test fails. Counts live in the `### \`type\` (N)` header.
- **Adding a skill to `engineering/`** → also update the hardcoded
  `self.assertIn("engineering\t27\n", ...)` at `tests/test_install_skills.py:29`.
- **Uninstall** → no command exists. Delete the directory from the project.
- **Symlinked destination** → treated as a conflict, never followed.

## Warnings

- **The repo is PUBLIC.** Anything committed is indexed and cached. Re-scrub before
  committing provenance, reports, or migration notes that reference real projects.
- **`library/media/` is tracked (~54 MB / 970 files).** Re-sync it only from the pinned
  upstream revision recorded in `SOURCES.toml`, never from an unpinned checkout.
- **`AGENTS.md` mandates prefixing shell commands with `rtk`** inside this repo. That
  rule does **not** apply to the contents of SKILL.md files or the README, which run
  or are read elsewhere. Keep those on plain `python3`.
- **`video-shotcraft` audio assets** (bgm/sfx mp3s) are not Apache-2.0; each follows its own
  terms in `assets/audio/ATTRIBUTION.md`, and some sfx rows are marked untraceable.
- The user's own examples use `~/skills`. Keep that as the documented catalog path;
  the CLI also honours `${SKILLS_CATALOG}`.

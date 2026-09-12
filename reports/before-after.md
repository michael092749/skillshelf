# Before and after: skill context footprint

Measured 2026-09-12 before modifying any source discovery directory. The dormant
`~/skills` catalog itself contributes zero startup context because neither host
discovers that path.

## Current personal discovery

| Host | Entries | Parsed name + description | Approx. tokens |
| --- | ---: | ---: | ---: |
| Codex `~/.agents/skills` | 50 | 7,523 chars | 1,881 |
| Claude `~/.claude/skills` | 46 | 9,066 chars | 2,267 |

The two hosts contain 96 discovery entries but only 65 unique runtime names; 31
overlaps are byte-identical. Full skill bodies are excluded because hosts load
them progressively rather than at startup.

The existing global instruction files are intentionally unchanged: Codex
`AGENTS.md` is 3,757 bytes and Claude's `CLAUDE.md` pointer file is eight bytes.
Their saving is zero in this rollout. Claude expands its import target at startup,
so the pointer size is not a claim about Claude's total instruction context.

## Project profiles after global cutover

| Project selection | Discovered skills | Metadata chars | Approx. tokens | Saved vs Codex globals | Codex path proxy |
| --- | ---: | ---: | ---: | ---: | ---: |
| Unrelated project | 0 | 0 | 0 | 100% | 0 |
| `coding` | 10 | 2,195 | 549 | 70.8% | 2,740 chars; 73.5% saved |
| Optimized `n8n` | 1 | 198 | 50 | 97.4% | 258 chars; 97.5% saved |
| `coding` + optimized `n8n` | 11 | 2,393 | 599 | 68.2% | 2,998 chars; 71.0% saved |
| `n8n-full` | 15 | 10,486 | 2,622 | 39.4% larger | 11,385 chars; 9.9% larger |

The optimized n8n profile vendors 14 specialist skill directories as
non-discovered references. The router reads only the specialists relevant to the
current task. This retains project-local knowledge without paying for 15 long
descriptions on every turn.

Against Claude's 46-entry raw inventory, the same profiles save 75.8% (`coding`),
97.8% (optimized `n8n`), and 73.6% (combined). Claude currently marks 22 personal
skills as manual-only, so its actual startup description load can be lower than
the all-entry raw comparison.

## Current-state boundary

The personal discovery directories have not been removed. Therefore existing
Codex and Claude sessions have not yet realized these projected savings. The new
catalog adds no load, but live savings begin only after projects are migrated and
the personal directories are archived as described in `MIGRATE.md`.

`~/project-a` was read only. Its 16 Codex project skills and two Claude
project entries remain unchanged. If personal globals are later retired, its raw
metadata would project from 66 to 16 Codex entries (75.8% fewer entries and 40.2%
fewer metadata characters) and from 48 to two Claude entries (95.8% fewer entries
and 90.2% fewer metadata characters), without deleting its local files.

## Method

The reproducible semantic measure is:

```text
entry = name + ": " + description + "\n"
approximate tokens = ceil(characters / 4)
```

The Codex comparison proxy additionally renders:

```text
- NAME: DESCRIPTION (file: NORMALIZED_PATH)
```

Run:

```bash
rtk python scripts/audit_catalog.py measure \
  --scope codex=~/.agents/skills \
  --scope claude=~/.claude/skills
rtk python scripts/audit_catalog.py compare --bundle coding
rtk python scripts/audit_catalog.py compare --bundle n8n
rtk python scripts/audit_catalog.py compare --bundle coding --bundle n8n
rtk python scripts/audit_catalog.py compare --bundle n8n-full
```

Character-to-token conversion and host framing are approximations. Codex also
caps, shortens, or omits entries when its skill list is large, so these numbers
measure comparable metadata rather than claiming exact whole-prompt token usage.

# Project-scoped agent skills

### Stop re-installing the same skills into every project, for every agent.

You have probably seen a dozen skills worth stealing this month — a sharp
code-review workflow, someone's SEO audit, a whole n8n pack. And you have two
options for each one: install it globally and pay for it in **every** project
forever, or bookmark it and forget it exists by Thursday.

A library is the third option. Add it once; it costs nothing sitting there; it
is one question away the day a project actually needs it.

Set your skills up **once**. Then, at the start of any project, run one skill:
it asks what this project needs and installs exactly that — for Codex, Claude,
or both, in a single step.

- **No manual copying.** No hunting for where the good version of a skill lives.
- **No doing it twice.** Codex reads `.agents/skills/`, Claude reads
  `.claude/skills/`. One answer sets up both.
- **No context bloat.** Skills arrive in packs — one plugin can add sixteen at
  once — and every one of them loads into every session forever. Here, a
  TypeScript repo does not pay for eighteen Google Workspace skills.
- **Nothing to remember.** The menu is generated from the catalog every time.
  Add a skill, it shows up. There is nothing to register or maintain.

```
you: set up skills for this project

     engineering (27)
       tdd              Test-driven development.
       code-review      Review changes since a fixed point.
       diagnosing-bugs  Diagnosis loop for hard bugs and perf regressions.
       ... 24 more

     sales-and-marketing (4)
       hormozi-offer    Build a Grand Slam Offer from any idea or service.
       seo-audit        Audit, review, or diagnose SEO issues on a site.
       ... 2 more

     Which categories? Which agent?

you: engineering, both

     ✓ 27 skills → .agents/skills/ and .claude/skills/
```

One exchange, at the start of the project. Then you get on with the work.

[Install it →](#install)

## The problem

Managing skills by hand does not scale, in two directions at once.

**Per project, it is pure toil.** Every new repo means finding the skills you
want, copying them in, and then copying them *again* because Codex reads
`.agents/skills/` and Claude reads `.claude/skills/`. Miss one and that agent
silently has no skills. Three months later you cannot remember what you
installed or where the good version lives, so you start over, or you give up
and work without them.

**So you take the shortcut — install everything globally.** One setup, every
agent has everything, done. But skill metadata loads into context at the start
of **every session in every project**, whether or not that project will ever use
it. Measured on the machine this catalog was built from:

| Discovery directory | Entries | Metadata | Approx. tokens, every session |
| --- | ---: | ---: | ---: |
| Codex `~/.agents/skills` | 50 | 7,523 chars | 1,881 |
| Claude `~/.claude/skills` | 46 | 9,066 chars | 2,267 |

96 entries, only 65 unique — 31 were the same skill installed under both hosts.
Among them, eighteen Google Workspace skills that every repository paid for
whether or not it had ever touched Gmail.

**And it escalates on its own.** Skills do not arrive one at a time; they
arrive in packs. Install one plugin for a tool you use occasionally and it adds
a dozen or sixteen skills at once — some marketplaces ship over a hundred. A
specialised pack is exactly the kind you want available *sometimes* and
invisible the rest of the time, but global discovery has no such setting. You
never chose those skills individually, so you will never prune them
individually, and the list only grows.

The cost is not only tokens. A long menu of vaguely relevant skills makes the
agent's choice of *which* skill to use worse — the useful skill for this repo
is now competing with ninety that have nothing to do with it.

Neither option works. Per-project setup is correct and nobody sustains it;
global install is effortless and quietly degrades every project you own.

## What this aims to achieve

**Keep a library instead of an installation.**

The distinction is the whole idea. An *installed* skill is one every session
pays for. A skill in a **library** is inert: the catalog lives outside both
agents' discovery paths, so nothing reads it until a project asks. Adding to it
costs nothing, anywhere — which means the library can hold everything you have
ever collected, plugin packs and specialised bundles included, without any of
it taxing a single project.

Projects then pull what they need. One installed skill —
`setup-project-skills` — is the entire interface: it reads the library live,
shows what each category contains, and copies your selection into both agents'
directories in one step.

Collect freely. Load deliberately. You stop managing skills and just answer a
question at the start of a project.

What that buys, measured against the same globals:

| Project selection | Skills | Approx. tokens | vs. Codex globals |
| --- | ---: | ---: | --- |
| A project that needs none | 0 | 0 | 100% saved |
| `coding` profile | 10 | 549 | 70.8% saved |
| n8n router only | 1 | 50 | 97.4% saved |
| All 15 n8n skills | 15 | 2,622 | 39.4% *worse* |

That last row is the honest one: selecting is what helps, not this repo.
Installing everything into a project is worse than leaving it global.

Three properties make it safe to rely on:

- **Explicit.** Nothing installs itself. A skill reaches a project because you
  named it.
- **Non-destructive.** Copies are verified by hash. A destination that differs
  from the catalog aborts the whole operation before anything is written, so
  local edits are never silently overwritten.
- **Self-checking.** The catalog validates its own structure, and the tests
  fail if the human-readable index drifts from what the CLI reports.

## Install

Requires **Python 3.11+** (for `tomllib`). No third-party dependencies.

**1. Clone the catalog somewhere your agents do _not_ scan.** `~/skills` works,
because neither Codex nor Claude looks there. Cloning it inside a project
defeats the point.

```bash
git clone https://github.com/<you>/skills.git ~/skills
```

**2. Install the one skill that does everything else.**

```bash
python3 ~/skills/scripts/install_skills.py install \
  --project ~ --host both --skill meta/setup-project-skills
```

That puts a single skill — and only one — in `~/.agents/skills/` and
`~/.claude/skills/`. It is the deliberate exception to keeping the catalog out
of discovery paths, and it is what makes the catalog reachable from a project
that has nothing in it yet.

That is the whole setup. You should not need to run the CLI again by hand.

## Use it

In any project, tell your agent:

> set up skills for this project

The skill queries the catalog live — it never works from a memorized list — then
shows every category with a one-line description of each skill inside it, asks
which ones you want and which agent to set up, previews the copy, and installs.
Running it again later to add a category is safe: anything already present and
identical is left alone.

Adding a skill to the catalog makes it appear in that menu automatically. There
is nothing to register.

### Driving it directly

The skill is a conversation wrapped around one CLI, which you can also use for
scripting or CI:

```bash
# What categories exist?
python3 ~/skills/scripts/install_skills.py list types

# What is in one, one line each?
python3 ~/skills/scripts/install_skills.py list skills --type engineering --brief

# Find something by keyword
python3 ~/skills/scripts/install_skills.py list skills --search seo --brief

# Preview, then copy
python3 ~/skills/scripts/install_skills.py install \
  --project /path/to/project --host both --type engineering --dry-run
```

`--host codex` writes to `<project>/.agents/skills/`, `--host claude` writes to
`<project>/.claude/skills/`, `--host both` writes to both. `--type` and
`--skill` are repeatable and combine, so one command can take a whole category
plus a few individual skills.

Descriptions are written to *trigger* a skill, not to be read — they run to
paragraphs of keywords. `--brief` trims each to its first sentence so a listing
stays scannable.

### What the output means

A dry run prints one line per skill per host:

- `copy` — will be created.
- `unchanged` — already present and byte-identical; the real run is a no-op, so
  rerunning to add a category is always safe.

A **conflict** is different: if any destination exists with different contents,
or is a file or symlink instead of a directory, the command exits non-zero,
names only the conflicting paths, and **copies nothing at all**. That usually
means the project has a locally customized copy of that skill. Resolve it
deliberately rather than deleting the destination.

There is no uninstall command. Removing a skill from a project is deleting its
directory.

### Updating a skill

Installs never overwrite, so after editing a skill in `library/`, delete the
stale installed copy before reinstalling — including the picker's own copy in
`~/.agents/skills/` and `~/.claude/skills/`.

## Layout

```text
library/      canonical skills, grouped by domain; a skill's ID is its path here
              (e.g. engineering/tdd), and its directory is copied whole
variants/     preserved alternate versions of same-named skills; never implicit
bundles/      small TOML project profiles naming explicit skill selections
integrations/ MCP, plugin, and credential recipes — named env vars, never values
scripts/      install_skills.py (list/select/copy) and audit_catalog.py (validate/measure)
tests/        deterministic checks, including index-vs-catalog drift
index.md      human-readable map of every type and skill
SOURCES.toml  where each imported skill came from
reports/      the measurements quoted above
```

Skill directories are copied intact — references, scripts, and assets included.

## Verify

```bash
python3 scripts/audit_catalog.py catalog        # structure, duplicate names, bundles
python3 -m unittest discover -s tests -v        # includes index-vs-catalog drift
```

`audit_catalog.py` rejects duplicate runtime names across the whole catalog,
because two skills with the same name are ambiguous once they land in the same
project directory.

## Provenance and licensing

`SOURCES.toml` records where each imported skill came from. Most of this
catalog was **imported, not authored here** — from plugins, marketplaces, and
other people's repositories. Check the license on anything you redistribute;
skills carrying their own `LICENSE` file or `license:` frontmatter keep it.

---
name: setup-project-skills
description: Interactive picker that installs skills from the personal skills catalog into the current project for Codex and/or Claude. Ask which categories or individual skills are wanted, preview the copy, then copy whole skill directories into .agents/skills/ and .claude/skills/. Use this at the start of a project, and whenever the user says "set up skills", "install skills", "which skills do I have", "add skills to this project", "bootstrap this repo's skills", "pull in the engineering skills", "give this project the n8n skills", or names a catalog category (engineering, productivity, automation/n8n, google-workspace, research, sales-and-marketing, content/writing, media/video). Also use when a project is missing a skill the user expected to be there.
---

# Set up this project's skills

Agent skills load their name and description into every session's context. A
global install of everything is a permanent tax on every project, so this
catalog stays dormant and each project gets only the skills it needs. This skill
is the front door: it asks what the project needs, then copies those skill
directories in.

Two things make the conversation worth having rather than guessing: only the
user knows what the project is for, and an unwanted skill is invisible clutter
that nobody removes later. So ask, then install exactly what was asked for.

## The catalog and its CLI

The catalog lives at `${SKILLS_CATALOG:-$HOME/skills}` and every operation goes
through one script:

```bash
CATALOG="${SKILLS_CATALOG:-$HOME/skills}"
python3 "$CATALOG/scripts/install_skills.py" --help
```

If `$CATALOG/scripts/install_skills.py` does not exist, stop and tell the user
where you looked. Do not copy skill directories by hand — the script validates
the catalog, refuses to overwrite divergent directories, and verifies every copy
by hash. Hand-copying loses all of that.

Never recite a category list from memory, including the one in this file's
description. The catalog changes; ask it what it holds:

```bash
python3 "$CATALOG/scripts/install_skills.py" list types
python3 "$CATALOG/scripts/install_skills.py" list skills --type engineering --brief
python3 "$CATALOG/scripts/install_skills.py" list skills --search seo --brief
```

`list types` prints `type<TAB>count`. `list skills` prints
`id<TAB>runtime-name<TAB>description`. The `id` column is what `--skill` takes;
the type column from `list types` is what `--type` takes.

Use `--brief` for anything you show the user. Full descriptions are written to
trigger the skill, not to be read — they run to whole paragraphs of keywords,
and a screen of them buries the choice you are asking them to make. `--brief`
cuts each to its first sentence, which is the part a human actually reads.
Read the full description yourself only when you need to judge a specific
skill's fit.

## Workflow

### 1. Confirm the project

The project is the current working directory unless the user names another one.
Say which directory you are about to write into before you write to it — people
run this from the wrong terminal tab more often than you would think.

### 2. Read the catalog, then ask

Run `list types` first so the choices you offer are real, then run
`list skills --type <type> --brief` for each type. A bare category name is not
enough to choose on — `content/writing` and `productivity` mean nothing until
you see what is inside them — so show the contents before asking, not after.

Render one block per category: the type, its count, and each skill's runtime
name with its brief description. Something like:

```text
sales-and-marketing (4)
  hormozi-offer    Build a Grand Slam Offer from any idea, product, or service.
  idea-validator   Validate a startup idea against the real market using Exa.
  lead-generation  Generate enriched lead lists using Exa Agent.
  seo-audit        Audit, review, or diagnose SEO issues on a site.
```

For a large type, listing all twenty-six lines is still better than hiding
them — the user is choosing whether to load these into every future session and
deserves to see what they are signing up for. Group or lead with the highlights
if it helps, but do not silently drop skills from the display.

Then ask two things:

- **Which skills?** Offer the types as the primary unit — most people think in
  categories ("the engineering ones"), and a type is one `--type` flag. Offer
  individual skills too, for people who want three things rather than
  twenty-six; `--skill` and `--type` combine in one command.
- **Which host?** `codex` writes to `<project>/.agents/skills/`, `claude` writes
  to `<project>/.claude/skills/`, `both` writes to both. If the project already
  has one of those directories, that is a strong hint — mention it rather than
  asking blind.

Use `AskUserQuestion` with `multiSelect: true` for the category choice when it
is available. When it is not (Codex and most non-Claude-Code hosts have no such
tool), print a numbered list and ask the user to reply with numbers — same
information, same decision, no tool dependency.

If the user already told you what they want ("install the n8n skills for
Claude"), skip straight to the dry run. Re-asking a question they already
answered is friction, not diligence.

### 3. Dry run, then show the plan

```bash
python3 "$CATALOG/scripts/install_skills.py" install \
  --project . --host both \
  --type engineering --skill automation/n8n/n8n-project-router \
  --dry-run
```

`--type` and `--skill` are both repeatable and combine, so one command covers
"all of engineering plus these two other things".

A successful dry run prints one `state<TAB>host<TAB>id<TAB>destination` line
per skill per host, then a summary:

- `copy` — will be created.
- `unchanged` — already there, byte-identical; the real run is a no-op.

Report those counts rather than pasting every line.

A **conflict** is the third outcome and it does not appear as a line. If any
destination already exists with different contents — or is a file or a symlink
instead of a plain directory — the command exits non-zero, lists only the
conflicting paths, and copies nothing at all, not even the skills that were
fine. Treat that output as the signal it is: the project has a locally
customized copy of that skill, and forcing the copy would silently destroy
someone's edits. Resolve it with the user — drop that skill from the selection
and keep theirs, or have them move theirs aside — then rerun. Do not delete the
destination to push the install through unless they explicitly ask for that.

### 4. Install

Rerun the identical command without `--dry-run`. Then tell the user what landed
where, and that the skills become discoverable in their next session in that
project — a running session will not see them.

## Adding to a project that already has skills

Rerunning is safe: identical directories report `unchanged`, so the natural way
to add a category later is to run the same install again with the extra
`--type`. There is no uninstall command — removing a skill is deleting its
directory from `.agents/skills/` or `.claude/skills/`, which you can do directly
when asked.

## What this skill does not do

Copying a skill directory does not install MCP servers, plugins, credentials, or
agent instruction files. Those live in `$CATALOG/integrations/` as separate
recipes and are only ever set up when the user asks for them by name. If a
skill the user just installed needs an MCP server to be useful, say so and point
at the matching integration recipe — but do not start configuring it uninvited.

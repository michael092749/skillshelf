---
name: setup-project-skills
description: Interactive picker that installs skills and MCP servers from the personal catalog into the current project for Codex and/or Claude. Ask which categories or individual skills are wanted, then which MCP servers, preview both, then copy skill directories into .agents/skills/ and .claude/skills/ and merge server entries into .mcp.json and .codex/config.toml. Use this at the start of a project, and whenever the user says "set up skills", "install skills", "which skills do I have", "add skills to this project", "bootstrap this repo's skills", "pull in the engineering skills", "give this project the n8n skills", "set up MCP", "add MCP servers", "which MCPs do I have", "configure .mcp.json", "wire up codex config", or names a catalog category (engineering, productivity, automation/n8n, google-workspace, research, sales-and-marketing, content/writing, media/video). Also use when a project is missing a skill or an MCP server the user expected to be there.
---

# Set up this project's skills

Agent skills load their name and description into every session's context, and
every connected MCP server loads its whole tool list. A global install of
everything is a permanent tax on every project, so this catalog stays dormant
and each project gets only what it needs. This skill is the front door: it asks
what the project needs, copies those skill directories in, and wires up the MCP
servers that go with them.

Two things make the conversation worth having rather than guessing: only the
user knows what the project is for, and an unwanted skill or server is invisible
clutter that nobody removes later. So ask, then install exactly what was asked
for.

## The one standing exception

`second-brain-ingest` is installed into every project, always, without asking.
It sits at the root of the catalog rather than in a category so that no
`--type` sweep can pull it in by accident and no category choice can leave it
out.

This contradicts the dormant-catalog rule above, deliberately. Any project can
turn out to hold something worth compiling into the user's wiki — notes, a
transcript, a spec, a thread — and the cost of the skill being absent at that
moment is that the material is summarized into a session and lost. One skill's
name and description is a cheap standing tax against that.

Add `--skill second-brain-ingest` to every install command, including the dry
run. Do not raise it as a choice in step 2; mention it in the plan you show in
step 3 so the extra line in the output is not a surprise.

## The catalog and its two CLIs

The catalog lives at `${SKILLS_CATALOG:-$HOME/skills}`. Skills go through one
script and MCP servers through another:

```bash
CATALOG="${SKILLS_CATALOG:-$HOME/skills}"
python3 "$CATALOG/scripts/install_skills.py" --help   # skill directories
python3 "$CATALOG/scripts/install_mcp.py" --help      # MCP server entries
```

If either script does not exist, stop and tell the user where you looked. Do not
copy skill directories or hand-edit `.mcp.json` and `.codex/config.toml`
yourself — the scripts validate the catalog, refuse to overwrite anything that
diverges, and verify every write. Doing it by hand loses all of that.

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
  asking blind. The same answer is reused for MCP servers in step 5, so ask it
  once.

Leave MCP servers out of this question. Which servers are worth connecting
depends on which skills land, and a single question mixing twenty-six skills
with sixteen servers is one the user cannot answer well.

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
  --skill second-brain-ingest \
  --dry-run
```

`--type` and `--skill` are both repeatable and combine, so one command covers
"all of engineering plus these two other things".

`second-brain-ingest` is on that line whatever the user picked — see the
standing exception above.

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

### 5. Ask which MCP servers the project needs

A skill is instructions; an MCP server is the live connection those instructions
often assume. The n8n skills can describe a node from memory but cannot read the
user's actual workflows without the n8n server, and `seo-audit` cannot pull real
Search Console numbers without one either. So ask — once, after the skills are
in, not before the user has seen what they picked.

Ask the registry what exists rather than naming servers from memory:

```bash
python3 "$CATALOG/scripts/install_mcp.py" list
python3 "$CATALOG/scripts/install_mcp.py" list --for-type automation/n8n
python3 "$CATALOG/scripts/install_mcp.py" list --server n8n
```

`list` prints `name<TAB>transport<TAB>required-env<TAB>description`. Run
`--for-type` for each type just installed and lead with what it returns — those
are the servers that pair with the skills the user already chose. Then show the
rest, because the pairing hints are a convenience, not a whitelist: a project
can want the Stripe server with none of the Stripe skills.

Show the required-env column when you ask. "Wire up n8n" reads differently once
you can see it needs `N8N_API_URL` and `N8N_API_KEY` exported, and the answer is
sometimes "not yet, I don't have the key here".

Same tooling as before: `AskUserQuestion` with `multiSelect: true` where it
exists, a numbered list to reply to where it does not. If the user wants no
servers, say so plainly and stop — this step is genuinely optional.

### 6. Configure the servers

```bash
python3 "$CATALOG/scripts/install_mcp.py" install \
  --project . --host both --server n8n --server exa --dry-run
```

`--server` is repeatable and `--host` means the same thing it does for skills:
`claude` writes `<project>/.mcp.json`, `codex` writes
`<project>/.codex/config.toml`, `both` writes both. Each file is **merged**, not
replaced — unrelated keys, other servers, and Codex's comments survive
untouched.

The output is `state<TAB>host<TAB>server<TAB>path`, where `add` is a new entry
and `unchanged` is one already there and identical. Then one
`env_required<TAB>VARIABLE<TAB>set|unset` row per variable. Rerun without
`--dry-run` to write.

A **conflict** behaves exactly like the skill installer's: if the project
already defines that server differently, the command exits 2, names the entry,
and writes nothing anywhere. The project's version is there for a reason —
resolve it with the user rather than overwriting it.

Nothing this command writes is a secret. Registry entries name environment
variables: Claude gets `"${N8N_API_KEY}"` to expand at run time, Codex gets
`env_vars = ["N8N_API_KEY"]` and reads it from the process environment. So
report the `unset` rows as the real remaining work — the config is correct and
the server still will not start until those are exported from the user's shell
profile. Never offer to paste a key into either file.

Then name the two human gates, because neither is something you can do for them:

- **Codex** only applies a project's `.codex/config.toml` once that project is
  trusted; an untrusted project loads the layer and ignores it. Trust is granted
  from Codex itself, per project.
- **Claude** asks the user to approve each new server in `.mcp.json` the first
  time it starts in that project.

Both hosts pick the servers up at the start of the next session, not this one.

If the server the user wants is not in the registry, do not invent an entry
inline. The registry is `$CATALOG/integrations/servers.toml` (public) with
`servers.local.toml` beside it for machine-specific and personal ones, which is
gitignored; `$CATALOG/integrations/<name>/README.md` holds the trust, scope, and
verification notes for the bigger ones. Adding an entry there is a catalog
change, so offer it as a follow-up rather than doing it mid-install.

## Adding to a project that already has skills

Rerunning is safe: identical directories and identical server entries report
`unchanged`, so the natural way to add a category later is to run the same
install again with the extra `--type`, and the same for `--server`. A project that
already has `second-brain-ingest` reports it `unchanged`, so carrying the flag
on every rerun costs nothing. There is no
uninstall command for either — removing a skill is deleting its directory from
`.agents/skills/` or `.claude/skills/`, and removing a server is deleting its
entry from `.mcp.json` or `.codex/config.toml`. Do both directly when asked.

## What this skill does not do

It writes configuration, never credentials. It does not export environment
variables, read them out of the user's other projects, or copy a key from a
global config into a project file — it reports which variables are missing and
stops there.

It does not start, authenticate, or smoke-test a server. "Configured" means the
entry is on disk and parses; whether the process launches and the API accepts
the token is a separate question, answered in the next session, by the host.

It does not install plugins or write agent instruction files (`AGENTS.md`,
`CLAUDE.md`). Those stay separate and only happen when asked for by name.

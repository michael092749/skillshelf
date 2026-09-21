# Deterministic project skill setup

Use `~/skills/scripts/install_skills.py`; its `--help` output is the source of
truth. The user selects exact skill IDs or types and the target host. Do not audit
the repository or recommend a selection unless the user separately asks for it.

The script copies complete canonical skill directories directly:

```text
--host codex   -> <project>/.agents/skills/<runtime-name>/
--host claude  -> <project>/.claude/skills/<runtime-name>/
--host both    -> both destinations
```

Run `list types`, then `list skills --type <type> --brief` when the user wants
to browse; `--brief` trims each trigger-oriented description to its first
sentence so a listing stays readable.
Run `install --dry-run` before copying when they ask for a preview. Existing
identical directories are successful no-ops; divergent destinations stop the
whole command before any copies begin.

Copying a skill does not configure plugins, credentials, or agent instruction
files. Those remain separate, explicitly requested workflows under
`integrations/`.

## MCP servers

`~/skills/scripts/install_mcp.py` is the matching CLI for host connections; its
`--help` output is the source of truth. Servers are defined once, host-neutrally,
in `integrations/servers.toml` — plus a gitignored `integrations/servers.local.toml`
for machine-specific and personal entries — and rendered per host:

```text
--host claude  -> <project>/.mcp.json            "mcpServers.<name>"
--host codex   -> <project>/.codex/config.toml   [mcp_servers.<name>]
--host both    -> both files
```

```bash
rtk python ~/skills/scripts/install_mcp.py list --for-type automation/n8n
rtk python ~/skills/scripts/install_mcp.py install \
  --project /path/to/project --host both --server n8n --dry-run
```

Both files are merged, never replaced: unrelated keys and existing servers are
preserved, an identical entry is a no-op, and an entry that differs stops the
whole command before anything is written. Registry values name environment
variables and never hold a credential, so a successful write reports which
variables are still unset. Codex additionally requires the project to be trusted
before a project-level config layer applies, and Claude asks the user to approve
each server on first use.

## Interactive selection

`library/meta/setup-project-skills` wraps the same CLI in a question-first
workflow for use inside a project. It needs one globally installed copy to be
discoverable before a project has any skills:

```bash
rtk python ~/skills/scripts/install_skills.py install \
  --project ~ --host both --skill meta/setup-project-skills
```

That single installed copy is the deliberate exception to keeping this
repository outside agent discovery paths; the repository itself stays out.

Installs never overwrite. After editing a skill in `library/`, an installed copy
is divergent and the command above aborts; delete the stale destination first —
`~/.agents/skills/setup-project-skills` and `~/.claude/skills/setup-project-skills`
here — then reinstall. The same holds for every skill copied into a project.

# Staged global-to-project migration

The end state is no user-added skills or integrations enabled globally. Reach it
without silently breaking existing repositories.

1. Keep `~/.agents/skills` and `~/.claude/skills` read-only while the catalog and
   disposable-project flow are validated.
2. For each existing repository, use `scripts/install_skills.py` to copy the
   user's selection, then verify both hosts from that repository.
3. Record repositories that still rely on personal skill discovery or
   user-enabled plugins. Global cleanup is blocked while this list is non-empty.
4. Once dependencies reach zero, archive only the individual user-added entries
   inventoried in `SOURCES.toml` under
   `~/.local/state/agent-skill-migration/<UTC timestamp>/`; leave reserved,
   synced, marketplace, built-in, default, and system entries in place. Disable
   only inventoried user-added plugins.
5. Start fresh Codex and Claude sessions in migrated repositories and verify
   project discovery. Retain the archive until the user gives a separate explicit
   deletion confirmation.

`~/project-a` is excluded from migration until the user explicitly
authorizes changes there. Therefore global cleanup remains deferred in the
initial rollout.

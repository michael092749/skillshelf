# Catalog rules

- Prefix every shell command with `rtk`.
- For catalog navigation or skill selection, read `index.md`; use
  `scripts/install_skills.py --help` and `scripts/install_mcp.py --help` as the
  command reference.
- Keep this repository outside agent discovery paths; project exposure happens
  only through an explicit `scripts/install_skills.py install` or
  `scripts/install_mcp.py install` command.
- Treat `library/` as canonical and `variants/` as opt-in conflict storage.
- Keep bundle membership explicit and minimal. A bundle cannot contain duplicate runtime skill names.
- Preserve complete skill directories, including referenced files, scripts, and assets.
- Record imported provenance in `SOURCES.toml`; never silently replace a divergent skill.
- Keep credentials out of this repository. Integration recipes and `integrations/servers.toml` name environment variables, never values; machine-specific or personal entries go in the gitignored `servers.local.toml`.
- Run `rtk python scripts/audit_catalog.py catalog` and `rtk python -m unittest discover -s tests -v` after catalog changes.
- Treat `~/project-a` as a read-only import source unless the user explicitly authorizes project changes.

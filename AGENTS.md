# Catalog rules

- Prefix every shell command with `rtk`.
- For catalog navigation or skill selection, read `index.md`; use
  `scripts/install_skills.py --help` as the command reference.
- Keep this repository outside agent discovery paths; project exposure happens
  only through an explicit `scripts/install_skills.py install` command.
- Treat `library/` as canonical and `variants/` as opt-in conflict storage.
- Keep bundle membership explicit and minimal. A bundle cannot contain duplicate runtime skill names.
- Preserve complete skill directories, including referenced files, scripts, and assets.
- Record imported provenance in `SOURCES.toml`; never silently replace a divergent skill.
- Keep credentials out of this repository. Integration recipes name environment variables, never values.
- Run `rtk python scripts/audit_catalog.py catalog` and `rtk python -m unittest discover -s tests -v` after catalog changes.
- Treat `~/project-a` as a read-only import source unless the user explicitly authorizes project changes.

# Exa project integration

Use for selected Exa-backed skills only when no already-connected Exa capability
is available. Verify the current endpoint or package against official Exa
documentation at setup time and record its exact version or URL in the project
manifest.

- Keep `EXA_API_KEY` environment-backed; never write its value to project files.
- Configure Codex through trusted-project `.codex/config.toml`.
- Configure Claude through project `.mcp.json`; use `${EXA_API_KEY}` expansion.
- Prefer one Exa MCP connection over separate connections for search, contents,
  company research, and lead generation.
- Verify with a read-only search and cite the returned source independently from
  connection success.

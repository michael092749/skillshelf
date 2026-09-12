# Google Workspace project integration

The imported `gws-*` skills rely on Google Workspace tooling and authenticated
account access. Before selecting this bundle:

1. Inspect the chosen skills for their actual command/MCP dependency.
2. Prefer an already connected capability. Otherwise use the smallest supported
   project-scoped connection and inspect requested permissions.
3. Keep OAuth tokens and credentials in the host/user credential store, not in
   `.agent-setup.toml`, `.mcp.json`, or repository environment files.
4. Request only the scopes required by the selected Calendar, Docs, Drive, Gmail,
   or Sheets operations.
5. Verify identity and a read-only list/get before any create, send, share, or
   delete action.

Claude project plugin scope is supported but still requires workspace trust and
approval of any plugin-provided MCP server. Codex plugins are user-scoped, so use
a project MCP or standalone project skills when possible and disclose any
user-scope installation before applying it.

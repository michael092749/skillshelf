# Cloudflare project integration

Select only when Wrangler or Cloudflare Worker/Pages configuration is present.
Resolve the current official MCP/plugin option at setup time and inspect its
permissions before proposing it.

- Prefer project MCP plus project skills over a Codex user-scoped plugin.
- Keep API tokens environment-backed and scoped to the minimum account/resources.
- Do not deploy, change DNS, rotate secrets, or mutate account settings during
  bootstrap.
- Verify configuration, authentication, and read-only account/project discovery
  separately from deployment.

# n8n project integration

Select this integration only when the repository contains n8n work and the task
needs live schemas, validation, or instance access.

## Required decision

Prefer hosted OAuth when the selected n8n MCP service supports it. For a
self-hosted stdio adapter, resolve and pin an exact reviewed `n8n-mcp` package
version. Required secret-backed environment names are:

- `N8N_API_URL`
- `N8N_API_KEY`

Any credential previously printed or exposed must be rotated before authenticated
verification. Never copy a value from personal or project configuration.

## Codex project scope

Merge an entry like this into trusted-project `.codex/config.toml`, replacing the
version placeholder before writing:

```toml
[mcp_servers.n8n]
command = "npx"
args = ["-y", "n8n-mcp@PINNED_VERSION"]
env_vars = ["N8N_API_URL", "N8N_API_KEY"]

[mcp_servers.n8n.env]
MCP_MODE = "stdio"
LOG_LEVEL = "error"
DISABLE_CONSOLE_OUTPUT = "true"
```

Codex must trust the project before this layer is active.

## Claude project scope

Merge an entry like this into root `.mcp.json`, replacing the version placeholder:

```json
{
  "mcpServers": {
    "n8n": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "n8n-mcp@PINNED_VERSION"],
      "env": {
        "MCP_MODE": "stdio",
        "LOG_LEVEL": "error",
        "DISABLE_CONSOLE_OUTPUT": "true",
        "N8N_API_URL": "${N8N_API_URL}",
        "N8N_API_KEY": "${N8N_API_KEY}"
      }
    }
  }
}
```

Claude workspace trust and per-server approval remain human gates.

## Verification

Report these states separately: config parses, project trusts it, process starts,
instance authentication succeeds, and a read-only workflow listing succeeds.
Never treat a health/list command as proof that a write or customer workflow ran.

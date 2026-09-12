---
name: n8n-project-router
description: Route n8n workflow building, editing, validation, code, expressions, agents, files, errors, subworkflows, MCP tools, and self-hosting to the relevant project-vendored reference.
---

# n8n project router

Use live n8n schemas and tools as the current truth. Before acting, locate the
nearest `.agent-setup/references/n8n/` directory and read the specialist named
below. These references are vendored but deliberately absent from host skill
discovery, so they add no startup metadata.

| Work | Read |
| --- | --- |
| MCP operations, credentials, security, templates | `n8n-mcp-tools-expert/SKILL.md` |
| Workflow design and topology | `n8n-workflow-patterns/SKILL.md` |
| Node fields and live schemas | `n8n-node-configuration/SKILL.md` |
| Expressions and data mapping | `n8n-expression-syntax/SKILL.md` |
| Validation errors and review | `n8n-validation-expert/SKILL.md` |
| JavaScript or Python Code nodes | `n8n-code-javascript/SKILL.md` or `n8n-code-python/SKILL.md` |
| AI-agent callable code | `n8n-code-tool/SKILL.md` |
| Error paths and retries | `n8n-error-handling/SKILL.md` |
| Files and binary data | `n8n-binary-and-data/SKILL.md` |
| AI agents, tools, memory, RAG | `n8n-agents/SKILL.md` |
| Reusable subworkflows | `n8n-subworkflows/SKILL.md` |
| Multiple n8n instances | `n8n-multi-instance/SKILL.md` |
| Deployment and self-hosting | `n8n-self-hosting/SKILL.md` |

Read every specialist whose row applies. For workflow writes, validate before
activation and read the deployed workflow back afterward. Treat test execution
as side-effectful unless proven otherwise. Keep secrets in n8n credentials or
environment-backed MCP configuration.

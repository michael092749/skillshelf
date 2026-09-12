# Stripe project integration

Select only when Stripe dependencies, API calls, webhooks, or payment-domain code
are present. At setup time, verify the current official Stripe integration and
host instructions rather than copying an existing global plugin configuration.

- Prefer project MCP plus project skills over a Codex user-scoped plugin.
- Inspect permissions and distinguish test from live mode.
- Keep API keys and webhook secrets environment-backed.
- Never change credentials, webhook registrations, or live account state during
  project bootstrap.
- Verification is config parsing and read-only identity/capability checks; payment
  creation, delivery, settlement, and webhook receipt require separate approval.

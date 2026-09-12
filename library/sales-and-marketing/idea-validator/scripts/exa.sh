#!/usr/bin/env bash
# Post a request body to the Exa API.
#   exa.sh search   '{"query":"...","type":"auto"}'
#   exa.sh contents '{"urls":["exa.ai"],"text":true}'
# Bodies for every lookup live in ../references/exa-recipes.md
set -uo pipefail

endpoint="${1:-}"
body="${2:-}"

case "$endpoint" in
  search|contents|findSimilar) ;;
  "") echo "usage: exa.sh <search|contents|findSimilar> '<json>'" >&2; exit 2 ;;
  *)  echo "exa.sh: unknown endpoint '$endpoint' (want search, contents, or findSimilar)" >&2; exit 2 ;;
esac

if [ -z "$body" ]; then
  echo "exa.sh: missing JSON body" >&2; exit 2
fi

if [ -z "${EXA_API_KEY:-}" ]; then
  echo "exa.sh: EXA_API_KEY is not set. Get one at https://dashboard.exa.ai/api-keys" >&2
  exit 3
fi

# Fail early on malformed JSON rather than reading it back as a 400 from Exa.
if command -v python3 >/dev/null 2>&1; then
  if ! printf '%s' "$body" | python3 -c 'import json,sys; json.load(sys.stdin)' 2>/dev/null; then
    echo "exa.sh: request body is not valid JSON" >&2; exit 2
  fi
fi

response=$(printf '%s' "$body" | curl -sS --fail-with-body \
  --max-time 60 \
  -X POST "https://api.exa.ai/${endpoint}" \
  -H "x-api-key: ${EXA_API_KEY}" \
  -H "content-type: application/json" \
  --data-binary @-)
status=$?

if [ $status -ne 0 ]; then
  echo "exa.sh: request failed (curl exit $status)" >&2
  [ -n "$response" ] && printf '%s\n' "$response" >&2
  exit 1
fi

# Pretty-print when possible; fall back to raw so output is never swallowed.
if command -v python3 >/dev/null 2>&1; then
  printf '%s' "$response" | python3 -m json.tool 2>/dev/null || printf '%s\n' "$response"
else
  printf '%s\n' "$response"
fi

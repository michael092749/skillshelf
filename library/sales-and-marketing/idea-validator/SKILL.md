---
name: idea-validator
description: Validate a startup idea against the real market, or research a company end to end, using Exa's web index. Use when the user describes a startup/product idea and wants to know if it exists, who else is doing it, or whether it's worth pursuing ("is this idea taken", "who are my competitors", "validate this idea", "is this market crowded"), or when they name a company/URL and want a full profile (funding, founders, news, socials, financials, competitors). Reverse-engineered from exa-labs/startup-idea-validator.
---

# Idea Validator & Company Researcher

Two workflows over Exa's index. Both end in a written assessment, not a dump of links.

## Setup

Needs `EXA_API_KEY` (get one at https://dashboard.exa.ai/api-keys). Check once:

```bash
[ -n "$EXA_API_KEY" ] && echo "ready" || echo "missing"
```

If missing: ask the user for a key, or say you're falling back to `WebSearch`/`WebFetch` and proceed. The fallback works but is noticeably weaker — Exa's `category: "company"` search and its entity metadata (funding totals, headcount, founded year) have no WebSearch equivalent, so competitor discovery gets shallower and the funding/traffic numbers disappear. Name that tradeoff once; don't re-raise it.

All Exa calls go through `scripts/exa.sh <search|contents> '<json>'`, which posts the JSON body verbatim to `api.exa.ai`. Paths here are relative to this skill's own directory (by default `~/.claude/skills/idea-validator/`) — not the working directory, so prefix them accordingly. Request bodies for every lookup are in `references/exa-recipes.md`; read that file before running any lookup other than the two inline below.

## Workflow A — validate an idea

1. **Find who already does this.** Search the idea text directly; Exa's neural search matches on meaning, so pass the user's own phrasing rather than keywords you invent.

```bash
scripts/exa.sh search '{"query":"IDEA TEXT HERE","category":"company","type":"auto","numResults":10,"contents":{"text":{"maxCharacters":500}}}'
```

2. **Read the entity metadata**, not just the blurbs. Each result may carry `entities[0].properties` with `foundedYear`, `workforce.total`, `financials.fundingTotal`, `financials.fundingLatestRound`, and `webTraffic.visitsMonthly`. That's what separates "three funded competitors with real traffic" from "three abandoned side projects" — a distinction the titles alone will not give you.

3. **Assess.** Write it yourself from the results; there is no scoring endpoint. Cover:
   - **Market overview** — 2-3 sentences on the shape of the space.
   - **Key players** — 3-5, one line each on what makes them relevant.
   - **Gaps** — 2-4 openings the user could actually exploit.
   - **Uniqueness score, 1-10** — 10 is genuinely novel, 1 is saturated. State what drove the number.
   - **Recommendation** — go / no-go with reasoning.

Be honest and specific. If the idea exists in many forms, say so plainly and early; a validator that congratulates every idea is worthless. If the search returns few real competitors, consider the likelier explanations before calling it a green field — the phrasing may be too niche to match, or the market may be small for a reason. Say which one you think it is.

## Workflow B — research a company

Start from the URL. Step 1 feeds step 2, so those are ordered; everything after is independent and should be batched in parallel.

1. **Get the one-line description** — `contents` on the URL with a summary query (recipe: `describe`). This yields a short, name-free description of what the company does.

2. **Find competitors by semantic similarity** — search using *that description* as the query, excluding the company's own domain (recipe: `competitors`). Searching the description rather than the company name is what surfaces functional competitors instead of press mentions. Don't skip step 1 to save a call; passing the company name here returns coverage of that company, not rivals.

3. **Fan out** — every remaining lookup in `references/exa-recipes.md` is independent. Run them in parallel and expect some to come back empty; a private company has no 10-K, most have no Tracxn page. Empty is a normal result, not an error. Never fill a gap with a plausible guess — an invented funding round is worse than an absent one.

4. **Write the profile.** Lead with what the company does and its current position, then funding, founders, traction, and competitors. Cite the source URL for every non-obvious claim, especially numbers.

## Output

Prose with headers, in the conversation. Reach for the `Artifact` tool only if the user asks for something shareable, or the research spans enough sources that scrollback would bury it.

Numbers age badly. When you report funding, headcount, or traffic, give the figure with its source and, where the result exposes one, its date.

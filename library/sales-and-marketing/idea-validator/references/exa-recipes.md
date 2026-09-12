# Exa request cookbook

Every lookup, as a ready request body for `scripts/exa.sh`. Lifted from the route handlers of `exa-labs/startup-idea-validator`; the query strings and filters are tuned, so change them only deliberately.

`{{URL}}` is a **bare domain** — `exa.ai`, not `https://exa.ai/`. It gets used inside `includeDomains` and `includeText`, both of which expect a bare host. Substitute before sending.

Two conventions carry most of the precision here:

- **`includeText: ["{{URL}}"]`** forces the domain to appear in the page body. This is the anti-hallucination filter: without it a search for `stripe.com crunchbase page:` cheerfully returns a competitor's Crunchbase profile. Keep it.
- **`type: "keyword"`** is used for every lookup that hunts for a *specific known page* (the Crunchbase profile, the Wikipedia article). `type: "neural"` / `"auto"` is for lookups that hunt by *meaning* (competitors, the idea search). Swapping them degrades both.

`livecrawl: "always"` fetches the page fresh instead of serving Exa's cached copy. It costs latency and is set only where staleness would be misleading — news, funding, financials, socials.

---

## Core

### `describe` — one-line description of the company
`contents`. Run this first in company research; its summary is the query for `competitors`.

```json
{"urls":["{{URL}}"],"text":true,"summary":{"query":"Describe what the company does in few word. It should be very simple and explicity tell what does the company do/is. Do not include the name of the company at all. Make sure never to include the name of the company in the summary."}}
```

The "never include the name" instruction is load-bearing, not stylistic — the output is fed straight into the competitor search below, and a company name in that query pulls back articles *about* the company instead of companies *like* it.

### `competitors` — semantically similar companies
`search`. Put the `describe` summary in `query`.

```json
{"query":"SUMMARY TEXT FROM describe","type":"auto","excludeText":["{{URL}}"],"excludeDomains":["{{URL}}","*.{{URL}}"],"contents":{"livecrawl":"fallback","summary":{"query":"Explain in one/two lines what does this company do in simple english. Don't use any diffcult words."}}}
```

### `subpages` — about / pricing / FAQ / blog
`search`. One call retrieves the marketing surface; usually the richest single source for a summary.

```json
{"query":"{{URL}}","category":"company","type":"neural","numResults":1,"includeDomains":["{{URL}}"],"contents":{"text":true,"livecrawl":"always","subpages":4,"subpageTarget":["about","pricing","faq","blog"]}}
```

### `idea-search` — companies matching an idea (Workflow A)
`search`. Query is the user's idea text, verbatim.

```json
{"query":"IDEA TEXT","category":"company","type":"auto","numResults":10,"contents":{"text":{"maxCharacters":500}}}
```

Results may include `entities[0].properties`: `name`, `description`, `foundedYear`, `workforce.total`, `headquarters.{city,country}`, `financials.{revenueAnnual,fundingTotal,fundingLatestRound}`, `webTraffic.visitsMonthly`. Read it — it is the difference between a funded rival and a dead side project.

---

## Money

### `funding`
`search`. The "reply NO" instruction gives you a clean sentinel instead of a hedged paragraph when there's nothing to report — treat a `NO` summary as absent, and say so rather than reaching for a guess.

```json
{"query":"{{URL}} Funding:","type":"keyword","numResults":1,"includeText":["{{URL}}"],"contents":{"text":true,"livecrawl":"always","summary":{"query":"Tell me all about the funding (and if available, the valuation) of this company in detail. Do not tell me about the company, just give all the funding information in detail. If funding or valuation info is not preset, just reply with one word \"NO\"."}}}
```

### `financials` — 10-K and filings
`search`. Public companies only; empty for everyone else.

```json
{"query":"{{URL}} 10k financial report:","type":"keyword","category":"financial report","includeText":["{{URL}}"],"contents":{"text":true,"livecrawl":"always"}}
```

### `crunchbase` / `pitchbook` / `tracxn`
`search`. Same shape, three databases — swap the domain and the noun.

```json
{"query":"{{URL}} crunchbase page:","type":"keyword","numResults":1,"includeDomains":["crunchbase.com"],"includeText":["{{URL}}"]}
```
```json
{"query":"{{URL}} pitchbook profile:","type":"keyword","numResults":1,"includeDomains":["pitchbook.com"],"includeText":["{{URL}}"]}
```
```json
{"query":"{{URL}} tracxn profile:","type":"keyword","numResults":1,"includeDomains":["tracxn.com"],"includeText":["{{URL}}"]}
```

---

## People

### `founders` — founder LinkedIn profiles
`search`. Note there is deliberately no `includeText` filter here; founder profiles often never mention the company domain.

```json
{"query":"{{URL}} founder's Linkedin page:","type":"keyword","numResults":2,"includeDomains":["linkedin.com"]}
```

### `linkedin` — company page
`search`.

```json
{"query":"{{URL}} company Linkedin profile:","numResults":1,"includeDomains":["linkedin.com"],"contents":{"text":true}}
```

---

## Press & reference

### `news`
`search`. Excludes the company's own domain, so you get coverage rather than its press releases.

```json
{"query":"{{URL}} Latest News:","category":"news","type":"keyword","numResults":10,"includeText":["{{URL}}"],"excludeDomains":["{{URL}}"],"contents":{"text":true,"livecrawl":"always"}}
```

### `wikipedia`
`search`.

```json
{"query":"{{URL}} company wikipedia page:","type":"keyword","numResults":1,"includeDomains":["wikipedia.org"],"includeText":["{{URL}}"],"contents":{"text":true,"livecrawl":"always"}}
```

---

## Social

### `twitter-profile`
`search`.

```json
{"query":"{{URL}} Twitter (X) profile:","type":"keyword","numResults":1,"includeText":["{{URL}}"],"includeDomains":["x.com","twitter.com"],"contents":{"text":true,"livecrawl":"always"}}
```

### `recent-tweets`
`search`. Needs the handle from `twitter-profile`, not the domain. Substitute `{{HANDLE}}` and set the dates to a real window — the app uses the last 90 days through tomorrow. `date -u` will generate them.

```json
{"query":"from:{{HANDLE}}","type":"keyword","category":"tweet","includeDomains":["twitter.com"],"includeText":["{{HANDLE}}"],"startPublishedDate":"{{90_DAYS_AGO_ISO}}","endPublishedDate":"{{TOMORROW_ISO}}","contents":{"livecrawl":"always"}}
```

### `reddit` — unfiltered user sentiment
`search`. Often the most candid source in the set, and the one most worth quoting.

```json
{"query":"{{URL}}","type":"keyword","includeDomains":["reddit.com"],"includeText":["{{URL}}"]}
```

### `github`
`search`.

```json
{"query":"{{URL}} Github:","type":"keyword","numResults":1,"includeDomains":["github.com"]}
```

---

## Not covered here

The original app also pulls YouTube and TikTok, but those hit the YouTube Data API and TikTok's oEmbed endpoint rather than Exa, and need their own keys. Skip them unless the user asks and supplies credentials.

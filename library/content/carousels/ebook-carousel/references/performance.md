# Start every run with a short Metricool triage

This is a read-only setup stage before Exa research and idea selection. Its output
is observed performance plus an explicit next test, not a claim that a particular
hook caused sales. Use the connected Metricool MCP; discover current tool schemas
and metrics rather than hard-coding IDs or reading credentials into prompts.

## Pull and preserve

1. If Metricool is unavailable or no accounts are configured, record status
   `unavailable`, the attempted tool-discovery time and reason; continue cold-start.
   Otherwise call getBrandSettings. Match the intended Instagram and TikTok accounts, get
   the brand ID and timezone, and retain only relevant account metadata. Use
   the intended account names supplied in the project brief.
   Resolve an ambiguous account before querying it; do not mix brands.
2. Call getAnalyticsAvailableMetrics for each relevant network/connector. Start
   with posts, which includes TikTok photo posts; inspect returned types. Query
   other supported connectors separately for account or link data. Request only
   current non-deprecated fields. A listed field need not have account data.
3. Call getAnalyticsDataByMetrics over the last 30 days through now, using explicit
   offsets and the brand timezone. Inspect a 7-day subset for recent context. Apply
   the low-view gate below before more calls. Only on the analyze branch, extend
   discovery to 90 days when useful; label mixed post ages.
4. Request post ID/URL, publication timestamp, format and caption alongside reach,
   views, likes, comments, saves, shares and follows where supported. Keep field
   IDs, definitions/units, request parameters and returned column order with raw
   results. Keep nulls and explicit zeros distinct. Returned zeros may still be
   affected by syncing or coverage limits; report them as provider observations.
5. Match posts to local production IDs by canonical URL or stable platform ID.
   Remove tracking query parameters only for matching, preserving original URLs.
   Caption/title similarity is a candidate match, not identity proof. Keep
   unmatched posts in the inventory to prevent accidental reuse of their ideas.
6. On the analyze branch only, discover account profile visits and bio/SmartLink clicks where available, and
   inspect only existing link destinations. Do not create links, edit bios, publish
   or schedule posts. Do not use deprecated profile/click metrics just because a
   previous run used them. Empty data is not proof of zero activity.

Store a run-specific staging snapshot before allocation. Once an idea is selected,
move it into research/performance.json, research/performance-review.md and
research/metricool/ within the project. Copy/link a dated immutable snapshot and
summary into shared research/performance/; update its index and research/README.md.
Never overwrite a previous observation. Refresh a resumed snapshot if its date
window is stale for the decision, recording the replacement as a new observation.

## Low-view gate: skip analysis, continue production

Evaluate each platform and comparable image-carousel cohort separately. Default
operational gate: at least **three posts with 100 or more views each** before
spending time on detailed performance analysis. User-specified thresholds take
precedence. This is a configurable time-saving rule, **not statistical evidence**
that a larger sample establishes a winner. Record the threshold used.

If the gate fails, views are unavailable, or coverage is clearly incomplete:

- Keep the minimal fresh snapshot, post inventory and exact-URL novelty matches.
- Set `analysis.decision` to `skipped_low_views`, `skipped_sparse_sample`, or
  `skipped_unavailable`, with reason, comparable count, view field and threshold.
  Platform data status remains `ok`, `no_data`, or `unavailable` as appropriate.
- Skip 90-day expansion, account/link metric exploration, rates, rankings and
  extended keep/change analysis. Do not retry merely to find nonzero data.
- Write a short review: observed counts/limits, “performance analysis skipped,”
  and one research-led creative hypothesis with a future 48h/7d measurement plan.
  Competitor/audience research proceeds; a fabricated winning pattern does not.

A platform with sufficient evidence can be analyzed while the other is skipped.
Low views never skip product verification, medical evidence, image review,
caption checks or final validation. Profile/bio verification for the chosen CTA
is still a publication prerequisite, separate from analytics exploration.

## Interpret the funnel honestly

Keep these distinct:

| Stage | Useful observations | Limits |
| --- | --- | --- |
| Discovery | Reach, views and relevant search/source data | Views are not unique people or completion. |
| Content value | Saves, shares, substantive comments | These are engagement proxies, not carousel completion. |
| Intent | Profile visits, relevant product requests, bio/link clicks | Account totals cannot be assigned to one post without attribution. |
| Purchase | Attributed checkout purchases/revenue/refunds | Only use an existing authorized analytics source that actually records them; Metricool does not imply checkout access. |

For image carousels, completion/slide drop-off remains unknown unless that exact
metric is exposed for that format. Video watch-time/completion is only applicable
to videos; analyze older reels separately as qualitative context. Never apply
TikTok's video completion fields to PHOTO rows. Do not infer sales from comments,
clicks, or the presence of a purchase CTA.

Compare within platform, format, organic/paid scope and similar time since posting.
Use prior 48-hour/7-day snapshots for matched-age comparisons when available. A
date filter may select publication dates while metrics remain lifetime totals;
preserve that distinction. Never sum repeated cumulative snapshots. With only
current snapshots, show post age and label comparisons provisional.

Compute rates only when the numerator and nonzero denominator have matching
scope: e.g. saves per 1,000 reached or shares per 1,000 views, naming the denominator.
Do not compare unlike platform engagement formulas. With tiny reach, absent
attribution, or sparse posts, state insufficient evidence and avoid declaring
winning hooks/tags or identifying a supposedly proven conversion bottleneck.

## Feed the next creative decision

For the analyze branch, write performance-review.md with:

- coverage and missing fields, observation time, post ages and relevant snapshot links;
- observed content/CTA patterns and the associated post URLs;
- **Keep:** a useful pattern supported by available evidence, with confidence;
- **Change:** one specific concern worth testing, not a causal diagnosis;
- **Test:** one primary creative variable for this run (hook, payoff order,
  product bridge or CTA), a measurable outcome, and review at 48h and 7d after
  publication. If the metric is unavailable, propose the tracking prerequisite;
  do not pretend it is already installed;
- **Sales/retention gaps:** explicit unknowns and what data would resolve them.

The researcher uses this brief to shape Exa questions, not to repeat the highest-
view post. The writer records which observation informed the hook/sequence/CTA in
idea/brief.md and idea/funnel.md. Competitor evidence and current audience needs
can justify a new hypothesis when account data is inconclusive.

Connection errors, missing accounts or absent analytics produce status
`unavailable` or `no_data`, a specific reason and an attempted_at timestamp per
platform. Continue with Exa evidence and a clearly labeled cold-start hypothesis.
The setup stage is complete when the attempt, limitations and decision brief are
saved; success is not defined as receiving nonzero metrics. No extra scheduled
monitoring, website analytics installation or publication is authorized by this stage.

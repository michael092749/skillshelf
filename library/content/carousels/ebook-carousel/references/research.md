# Researcher handoff

Return an evidence packet and recommended idea, not a production or an ebook offer
invented from the topic. Keep research separate from original marketing copy.

For competitor comparisons and angle selection, consult the relevant founder-skills
references in [skill-map.md](skill-map.md) when helpful; these are optional, scoped
references, not required installations.

Start from research/performance-review.md (or its staging path) produced by the
Metricool setup step. Turn its keep/change/test decision into specific Exa research
questions. When analysis was skipped for low views, use the recorded research-led
hypothesis without inventing a performance observation. Use cold-start hypotheses when the saved review says data is unavailable
or too sparse. Map the chosen idea to this brief without repeating a posted lesson.

## Discover the current product and question

1. Inspect the configured catalogue URL and its ebook/product links. Use Exa MCP
   search and page extraction; discover the available Exa tools rather than assume
   a fixed namespace. The Exa Agent can handle multi-source competitor research;
   continue its returned run ID instead of launching duplicate runs. Use focused
   Exa search/fetch calls for remaining gaps.
2. If the catalogue needs JavaScript, use an available browser or permitted public
   page retrieval to inspect the rendered catalogue. Label this supplemental
   provider. Never invent book slugs from titles, submit a checkout, or buy a book.
3. For candidate ebooks, record exact title, canonical URL, format, available
   contents/preview, audience fit, visible price/currency if relevant, availability,
   observed_at and access limits. A working homepage does not verify a product or
   its contents. Do not fabricate guarantees, credentials or reader results.
4. Query project research and relevant wiki evidence. Older material is a starting
   point, not evidence that a keyword is trending today or a product is still in
   development. Reconcile new observations with dated local notes explicitly.

## Current social and keyword evidence

Use Exa MCP for the required live research; a local-only result is incomplete.
Start with a recent 30-day window and the configured geography and language. Expand to 90 days or
older durable examples when coverage is thin and label the difference. Use
site/platform query terms or supported tool filters, not fabricated arguments.

Research both Instagram and TikTok: relevant ebook publishers, educators,
creators and adjacent product brands. Start with 3–5 relevant competitors and
6–10 useful examples across platforms; these are search targets, not quotas to
fill with poor evidence. Compare content with similar topic, audience, format and
age where possible. Exa gaps are expected, especially for TikTok and Instagram.

For each selected example, record:

- source ID, query, retrieval provider/tool, canonical URL, creator/platform;
- publication date if available, observation timestamp, format and duration;
- access level: full post/video, readable caption, indexed snippet, or unavailable;
- hook/CTA actually observed, with locator or timestamp; distinguish caption hook
  from an on-screen hook and a transcript from footage actually inspected;
- available views, likes, comments, saves and shares, keeping unknowns null;
- paid/affiliate disclosure when visible; known comparability limits;
- pattern worth testing, labeled as interpretation rather than measured causation.

For keyword/tag recommendations, preserve exact wording, platform, country/window
when known, source and evidence type. Use `measured_trend` only for dated regional
time-series/ranking evidence supporting change or popularity. Repeated mentions
are `observed_theme`; proposed terms are `editorial_hypothesis`. Search rank,
visibility and hashtag appearance do not establish trend volume. An inaccessible
platform yields a documented gap, not invented counts or a silent provider swap.

For health/nutrition claims, obtain current primary clinical/public-health evidence
appropriate to the exact statement and population, using Exa and primary pages.
Competitor claims, testimonials and product sales pages are marketing evidence,
not proof of treatment outcomes. Choose an educational alternative if evidence
cannot support the stronger claim.

## Select one fresh idea

Build 3–5 candidate angles internally. Evaluate evidence quality, configured audience
fit, product fit, novelty against the tracker/posted history, and usefulness within
six slides. These are editorial judgments, not numerical engagement predictions.
Recommend one. Never claim the choice is the best-performing without comparable
dated performance evidence.

Record the duplicate check: nearest existing projects, overlapping lesson/claim,
and the substantive new benefit. Read the workspace's current hooks, lessons and
CTAs; do not repackage an existing lesson with a new headline. Consider ready/draft projects as well as confirmed publications.

Deliver sources.json, findings.md, candidates.md and the chosen product record
to the parent. Before a project ID exists, use a run-specific workspace staging
folder under tmp/; move the accepted packet into the allocated project's research/.

## Shared evidence update — parent only

Use the existing relevant collection under research/, or add a clearly named
collection with a brief index for a genuinely new topic. Store each run's reusable
findings under a dated/ID-specific filename, link the project research packet and
canonical sources, and update the collection index plus research/README.md when
needed. Preserve original citations, conflicting observations and old publication
dates. This is not authorization to ingest the repository into the wiki.

# Carousel workflow flowchart

This diagram summarizes [the skill](../SKILL.md). The stage references remain
authoritative for thresholds, artifact fields and tool instructions.

```mermaid
flowchart TD
    Start([Run ebook-carousel]) --> Context[Read workspace, brand, production history and relevant evidence]
    Context --> Snapshot[Parent: fetch fresh minimal Metricool snapshot]
    Snapshot --> Enough{Enough comparable views and usable data?}
    Enough -->|Yes| Analyze[Analyze performance and choose a creative test]
    Enough -->|Low views, sparse or unavailable| Skip[Record why analysis is skipped; choose a research-led hypothesis]
    Analyze --> Research
    Skip --> Research

    Research[Researcher: Exa MCP product, audience, competitor and claim research] --> Evidence{Required evidence and product verified?}
    Evidence -->|No| Draft[Preserve completed work as draft; record blocker]
    Evidence -->|Yes| Select[Parent: select one fresh idea, allocate ID and create draft project]
    Select --> Write[Writer: exact slide copy, claim sources and ebook CTA]
    Write --> Lock{Parent approves claims and locks copy?}
    Lock -->|Revise| Write
    Lock -->|Yes| Design
    Lock -->|Yes| Captions

    subgraph Parallel[Parallel work after copy lock]
        Design[Design lead: shared style, references and per-slide prompts]
        Design --> WorkerA[Image worker A: assigned slides]
        Design --> WorkerB[Image worker B: different assigned slides]
        Captions[Caption writer: Instagram and TikTok descriptions and tags]
    end

    WorkerA --> Export
    WorkerB --> Export
    Export[Parent: preserve originals; normalize selected slides to 1080 x 1350; JPEG set for TikTok API] --> Review
    Review[Reviewer: inspect each final image at full size and phone scale] --> Merge
    Captions --> Merge
    Merge[Parent: review complete sequence, captions, claims and destination] --> Valid[Run artifact validator]
    Valid --> Pass{All required checks pass?}
    Pass -->|Yes| Ready[Mark ready; update tracker and publication prerequisites]
    Ready --> Handoff([Deliver image and caption folders; stop before publishing])
    Pass -->|No| Fix{What needs correction?}
    Fix -->|Copy, captions or evidence| Revise[Update affected inputs and copy revision]
    Revise --> Write
    Fix -->|Sizing, format or artifact records| Export
    Fix -->|Creative image defect| Budget{Repair budget remains?}
    Budget -->|Yes| Repair[Parent assigns targeted image repair]
    Repair --> Export
    Budget -->|No| Draft
    Fix -->|Required dependency unavailable| Draft
```

- **Low views skip detailed analytics only.** Every final image still receives
  visual review. See [performance triage](performance.md).
- **Parallel work has dependencies.** Image workers use the same locked copy and
  design plan, own different slides, and return results to the parent. Review can
  begin on finished exports while other slides generate; final acceptance waits
  for the complete set and captions. With fewer slots, queue roles; with no
  subagents, run the same roles sequentially. See [handoffs](orchestration.md).
- **Repair scope stays small.** Regenerate only affected slides; update affected
  captions and re-review changed outputs. Two creative repair calls are shared
  across the whole run. Export normalization does not consume that budget.
- **Ready means prepared files.** The handoff includes any bio-link and disclosure
  prerequisites. It does not publish, schedule posts or change profiles.

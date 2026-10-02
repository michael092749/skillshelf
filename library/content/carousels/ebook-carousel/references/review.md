# Image review gate

Every production receives visual review, regardless of account views or analytics
availability. Structural validation cannot substitute for looking at images.
Use a reviewer other than the image generator when agent capacity permits; the
parent always reviews the whole final sequence. With no subagents, perform a
separate review pass against the locked copy and evidence and record the fallback.

## Per-slide review

Open the actual final file, not just the prompt or provider thumbnail. Inspect at
native resolution for details and at approximately 360–430 CSS-pixel width for
phone reading. A browser/viewer zoom suffices; no contact sheet is required.

Check each item and record a finding for any failure:

- All exact copy, punctuation, folios, labels and CTA match the locked revision.
- Factual qualifiers remain readable. Diagram labels, arrows and any numbers
  match the source and do not imply a diagnosis, outcome or measurement.
- Text is legible without zoom; adequate contrast, line breaks and margins keep
  it clear of the edges and the intended platform's interface overlays.
- Character identity is coherent; anatomy, hands, objects and crops are natural.
  No fabricated testimonials, before/after proof, credentials or unwanted logos.
- Actual dimensions, orientation, format and compression suit the export profile.
  Export normalization has not clipped content, distorted proportions or damaged
  text. Inspect converted JPEGs as well when delivering a publisher-specific set.

Write `reviews/NN-review.json` with slide ID, final relative path, SHA-256, reviewer,
copy revision (`copy_revision`, matching run.json), inspected_at, full_resolution_checked, phone_scale_checked,
verdict (`pass`/`repair`) and findings (`severity`, `location`, `issue`, `action`).
Only record checks actually performed. Agents can review disjoint slides in
parallel; parent combines their results without replacing contrary findings.

## Sequence and repairs

View every final slide in order. Check the opening promise is fulfilled, each
slide advances the lesson, layouts vary purposefully, product bridge is accurate
and there is one primary action. Reconcile the captions with actual image text.
Save sequence findings in qa.md, with reviewer names and unresolved issues.

Missing or incorrect copy, unsupported claims, unreadable text, severe anatomy or
wrong export dimensions block readiness. Small aesthetic preferences are optional
improvements; do not consume generations merely to vary already acceptable art.
Parent assigns the smallest necessary repair under the shared two-call budget.

A new image, changed copy or transformed export invalidates its earlier hash-based
review. Reopen that final file and refresh the affected review and sequence check.
Preserve previous originals and reviews in archive/ when replaced. Set run.json
review flags only after the corresponding final checks pass. If a blocker remains,
keep draft and identify it precisely; low views never waive this gate.

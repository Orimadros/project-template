---
paths:
  - "docs/deliverables/articles/**/*.tex"
  - "docs/deliverables/slides/**/*.tex"
  - "code/**/*.R"
  - "code/**/*.py"
  - "code/**/*.sh"
  - "Makefile"
---

# Quality Gates & Scoring Rubric

## Thresholds

- **80/100 = Commit**
- **90/100 = PR / serious internal review**
- **95/100 = Submission/excellence candidate**

A submission/excellence score requires the aggregate score to be at least 95 and every component to be at least 80.

## Weighted Paper Components

| Component | Weight | Minimum for submission | Examples |
|-----------|--------|------------------------|----------|
| Literature | 10% | 80 | coverage, citation fidelity, contribution positioning |
| Data | 10% | 80 | source clarity, sample construction, measurement, Provenance Ledger coverage |
| Identification | 25% | 80 | estimand, assumptions, threats, robustness |
| Code | 15% | 80 | reproducibility, paths, seeds, output contracts |
| Paper | 25% | 80 | argument, structure, claims, tables/figures |
| Polish | 10% | 80 | grammar, notation, formatting, style fidelity |
| Replication | 5% | 80 | rerunnable pipeline, README/checks, output traceability |

## Severity Gradient

- Discovery: encouraging; surface options and uncertainty.
- Strategy: constructive; stress-test feasibility and identification.
- Execution: strict; block broken code, untraceable claims, or compile failures.
- Peer Review: adversarial; behave like a skeptical referee.
- Presentation: professional; prioritize the slide-writing principles, opening architecture, empirical graphics credibility, clarity, pacing, and audience cognition.

## Blocking Issues

- Runtime or LaTeX compile failure.
- Hardcoded absolute paths in code.
- Generated numbers in the paper that do not match `results/`.
- Missing or stale Asset Graph identity/lineage for governed pipeline code, explorations, data, or results; or missing queryable variable/code/layer provenance.
- Causal claim without identification support.
- Missing or fabricated citation.
- Slide claim that contradicts the paper.
- Talk deck that fails basic slide-writing principles: missing opening architecture, unreadable labels, misleading data graphics, overcrowded frames, inaccessible color encodings, or dense material kept out of backup slides.

## Output Locations

- Review reports: `docs/work/reviews/`
- Revision plans: `docs/work/plans/` (includes Clarity Status + requirements per `docs/work/templates/plan.md`)
- Merge reports: `docs/work/merge_reports/`

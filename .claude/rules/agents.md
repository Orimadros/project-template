---
paths:
  - ".claude/agents/**/*.md"
  - ".claude/skills/**/*.md"
---

# Worker/Critic Separation

This template uses a selective clo-author-style multi-agent system.

## Core Rule

- Worker agents create, implement, draft, or propose.
- Critic agents evaluate, score, stress-test, and request revisions.
- Creators never self-score their own work.
- Critics never rewrite the deliverable directly unless explicitly asked to switch roles.

## Worker/Critic Pairs

| Worker | Critic | Scope |
|--------|--------|-------|
| librarian | librarian-critic | Literature coverage and citation fidelity |
| explorer | explorer-critic | Exploratory analysis and diagnostics |
| strategist | strategist-critic | Research design and identification |
| coder | coder-critic | Reproducible analysis implementation |
| writer | writer-critic | Paper drafting and claim discipline |
| storyteller | storyteller-critic | Beamer talks derived from the paper and slide-writing principles |

## Standalone Roles

- `data-engineer`: data ingestion, cleaning, schemas, pipeline contracts.
- `domain-referee`: field-level substantive review.
- `methods-referee`: identification, estimation, and inference review.
- `editor`: aggregates reviews and makes accept/minor/major/reject-style decisions.
- `orchestrator`: routes tasks and keeps the loop moving.
- `verifier`: checks that claims, code, and outputs line up.

## Escalation

After three unresolved critic findings in the same area, stop and ask the user whether to narrow scope, revise the design, or accept the limitation explicitly in the paper.

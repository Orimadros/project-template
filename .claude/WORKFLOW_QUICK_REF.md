# Workflow Quick Reference

**Mode:** Paper-centric empirical research contractor (plan -> implement -> verify -> review)

## Loop

```text
Instruction
  -> Plan (if multi-step)
  -> Implement in code/ or docs/deliverables/articles/
  -> Verify (make target / make articles / make slides / make latex)
  -> Critic review
  -> Report
```

## Core Entry Points

- Paper: `docs/deliverables/articles/main/main.tex`
- Paper sections: `docs/deliverables/articles/main/sections/`
- Root slide decks: `docs/deliverables/slides/<deck>/<deck>.tex`
- Sources and bibliography: `docs/sources/`
- Pipeline: `make setup`, `make fetch`, `make build`, `make analysis`, `make all`
- Documents: `make articles`, `make slides`, `make latex`
- Reviews: `docs/work/reviews/`
- Checkpoints: `docs/work/checkpoints/`

## Quality Gates

| Score | Action |
|-------|--------|
| >= 80 | Ready to commit |
| >= 90 | Ready for review/PR |
| >= 95 | Submission/excellence candidate |
| < 80 | Fix blockers first |

## Non-Negotiables

- The paper `docs/deliverables/articles/main/main.tex` is the source of truth for the research argument.
- Talks in `docs/deliverables/slides/<deck>/<deck>.tex` derive from the paper.
- Slide writing follows `.claude/rules/slide-writing-principles.md`: sparse, visual, readable, color-conscious, and backup-heavy for dense detail.
- Scripts are staged: `code/00_fetch` -> `01_build` -> `02_analyze`.
- Raw data in `data/raw/` is immutable by default.
- Generated files belong in `data/clean/`, `data/tmp/`, and `results/`.
- Worker agents create; critic agents evaluate; creators never self-score.
- Always verify after edits.

## Session Logging

Update `docs/work/session_logs/`:
1. right after plan approval,
2. during key decisions,
3. before session close.

---
name: review
description: Run paper-centric worker/critic or simulated referee review over the canonical paper, code outputs, or talks.
allowed-tools: ["Read", "Grep", "Glob", "Write", "Task", "Bash"]
---

# Review

Use this for structured review. Reviews are read-only unless the user explicitly asks to implement fixes.

**Arguments:** [paper|section|code|talk|peer] [optional target]

## Modes

- `paper`: writer-critic plus domain/methods referee as needed.
- `peer`: domain-referee + methods-referee + editor decision.
- `code`: coder-critic + verifier.
- `literature`: librarian-critic.
- `talk`: storyteller-critic plus slide/pedagogy reviewers, using `.claude/rules/slide-writing-principles.md` for opening architecture, empirical graphics credibility, accessibility, pacing, and backup placement.

## Workflow

1. Resolve the target. Default paper target is `docs/deliverables/articles/main/main.tex`.
2. Load domain and style references where relevant.
3. For talks, load the slide-writing principles before running critics.
4. Run the appropriate critic/referee agents.
5. Save reports to `docs/work/reviews/`.
6. If review creates a non-trivial fix sequence, write a plan in `docs/work/plans/`.

## Output

- Review report path
- Overall score or recommendation
- Blocking findings first
- Suggested next verification command

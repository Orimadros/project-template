---
paths:
  - "code/99_explorations/**"
---

# Exploration Fast-Track

**Lightweight workflow for experimental work.** Quality threshold: 60/100 (vs 80 for production). No planning needed.

## Steps

1. **Research value check** -- Does this improve the project? If NO, don't build it.
2. **Create folder** -- `mkdir -p code/99_explorations/[name]/{R,checks,output}` + README + SESSION_LOG.md
3. **Code immediately** -- no plan needed. Must-haves: code runs, results correct, goal documented. Not needed: Roxygen docs, full tests, perfect style.
4. **Log progress** -- append 2-3 lines to SESSION_LOG.md as you work
5. **Maintain identity** -- every file in `code/99_explorations/` is Asset Graph-governed even while experimental; record new IDs, moves/deletions, and manually inspected direct dependencies
6. **Decision point** -- keep exploring, graduate to production (upgrade to 80/100), or archive with brief explanation; preserve IDs when moving the same logical files

## When to Stop (Kill Switch)

At any point: stop, archive with note ("Attempted X, hit blocker Y"), move on. No guilt -- exploration is inherently uncertain.

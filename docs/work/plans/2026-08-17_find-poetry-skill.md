# Add `find-poetry` Skill

**Date:** 2026-08-17  
**Status:** DRAFT

---

## Objective

Add a reusable project skill that finds, verifies, and frames culturally resonant references that can open or clarify a research-paper presentation.

---

## Clarity Status

| Aspect | Status | Notes |
|--------|--------|-------|
| Skill purpose | CLEAR | The user specified culturally resonant, forceful references that encapsulate a paper's core idea. |
| Source scope | ASSUMED | Search literature, history, art, film, journalism, speeches, and other cultural material; privilege material that can be sourced and quoted accurately. |
| Deliverable | ASSUMED | Return a ranked, presentation-ready shortlist with verified wording, translation/edition details where applicable, a precise thematic fit, and slide-use guidance. |
| Installation | CLEAR | Create the canonical skill in `.agents/skills/` and the matching `.claude/skills/` symlink used by this project. |

## Requirements

### MUST Have (Non-Negotiable)

- [ ] Add a discoverable skill named `find-poetry` to the project.
- [ ] Direct the skill to ground its search in the canonical paper and project materials, not a vague topic label alone.
- [ ] Require source verification for quotations, translations, authorship, dates, and context; never fabricate a quotation or attribution.
- [ ] Make the output useful for a talk: rank candidates, explain the exact conceptual correspondence, and distinguish a citation/reference from the proposed spoken or slide wording.

### SHOULD Have (Preferred)

- [ ] Include search heuristics for analogies such as compression, scale, representation, contagion, coordination, unintended consequences, absence, and measurement.
- [ ] Screen out merely decorative, overfamiliar, misleading, ethically distracting, or contextually inappropriate references.
- [ ] Add concise UI metadata and a linked Claude-facing skill path, matching the project's existing skill conventions.

### MAY Have (Optional, If Time)

- [ ] Include a compact one-line example request in the UI metadata.

---

## Approach

1. Initialize `.agents/skills/find-poetry/` with the project-local skill convention and UI metadata.
2. Write a concise workflow that extracts a paper's conceptual kernel, builds multiple search angles, searches primary/reliable sources, verifies candidates, and returns a presentation-ready ranked shortlist.
3. Create `.claude/skills/find-poetry` as a symlink to the canonical `.agents` skill, preserving cross-harness parity.
4. Validate the generated skill metadata and structure with the skill-creator validator; inspect the symlink and diff.

## Files Expected To Change

- `.agents/skills/find-poetry/SKILL.md`
- `.agents/skills/find-poetry/agents/openai.yaml`
- `.claude/skills/find-poetry` (symlink)
- `docs/work/plans/2026-08-17_find-poetry-skill.md`
- `docs/work/session_logs/2026-08-17_find-poetry-skill.md`

## Verification

- [ ] Run `quick_validate.py` on `.agents/skills/find-poetry`.
- [ ] Confirm `.claude/skills/find-poetry` resolves to the canonical skill folder.
- [ ] Review the resulting diff for valid frontmatter, exact workflow steps, and no unrelated changes.

## Provenance Ledger Impact

- **Affected assets:** N/A — this task creates guidance only, not data-bearing assets.
- **Nested records required:** N/A
- **Expected status:** N/A

---

## Approval

[ ] User approved: [Date]

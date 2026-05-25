---
name: devils-advocate
description: Challenge a talk deck or paper's design with 5-7 hard questions. Checks ordering, prerequisites, argument gaps, and cognitive load.
argument-hint: "[deck or manuscript path]"
allowed-tools: ["Read", "Grep", "Glob"]
---

# Devil's Advocate Review

Critically examine a talk deck or paper and challenge its design with 5-7 specific questions.

**Philosophy:** "We arrive at the best possible talk or paper through active dialogue."

---

## Setup

1. **Read the target file** (the deck or paper being challenged)
2. **Read the knowledge base** in `.claude/rules/` for notation conventions and narrative arc
3. For decks, **read `.claude/rules/slide-writing-principles.md`** and challenge against that standard
4. If applicable, **read related deliverables** for continuity

---

## Challenge Categories

Generate 5-7 challenges from these categories:

### 1. Ordering Challenges
> "Could the audience follow this better if we showed X before Y?"

### 2. Prerequisite Challenges
> "Does the audience have the background for this notation at this point?"

### 3. Gap Challenges
> "Should we include an intuitive example before this formal result?"

### 4. Alternative Presentation Challenges
> "Here are 2 other ways to visualize/present this concept."

### 5. Notation Conflict Challenges
> "This symbol conflicts with earlier usage in this work."

### 6. Cognitive Load Challenges
> "This slide/section has too many new symbols. Can we split it?"

### 7. Standalone / Publication Challenges
> "If this becomes a paper section or chapter, does it stand on its own?"

### 8. Beamer-Tips Challenges
> "Could this slide make one point more clearly with less text, a central graphic, or a backup slide?"

### 9. Seminar Opening Challenges
> "Does the opening answer the Big 5 quickly enough, or are we making the audience wait for the question, contribution, answer, or main threat?"

### 10. Evidence Display Challenges
> "Would the key result be more credible with a cleaner chart type, direct labels, fewer digits, or a clearer statement of units, variation, and uncertainty?"

---

## Output Format

```markdown
# Devil's Advocate: [Deck/Paper Title]

## Challenges

### Challenge 1: [Category] — [Short title]
**Question:** [The specific question]
**Why it matters:** [What could go wrong]
**Suggested resolution:** [Specific action]
**Location:** [Slides or sections affected]
**Severity:** [High / Medium / Low]

[Repeat for 5-7 challenges]

## Summary Verdict
**Strengths:** [2-3 things done well]
**Critical changes:** [0-2 changes before presenting or submitting]
**Suggested improvements:** [2-3 nice-to-have changes]
```

---

## Principles

- **Be specific:** Reference exact slides/sections and notation
- **Be constructive:** Every challenge has a suggested resolution
- **Be honest:** If the deck or paper is good, say so
- **Prioritize:** Notation conflicts and argument gaps > missed metaphors
- **Think like the audience / a referee:** Where do they get lost or push back?
- **For decks:** Apply the slide-writing principles: Big 5 opening, substantive titles, intuition bridge, sparse text, credible data graphics, accessible color, controlled builds, final takeaway, and backup slides for dense material

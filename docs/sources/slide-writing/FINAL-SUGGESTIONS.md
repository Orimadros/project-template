# Final Suggestions For The Slide-Writing Framework

- Source pool: `01-*` through `08-*` reports in `docs/sources/slide-writing/`
- Baseline checked: `.claude/rules/slide-writing-principles.md`, `docs/deliverables/preambles/beamer-preamble.tex`, and the current talk/storyteller/slide-auditor/pedagogy agents and skills
- Date: 2026-05-25
- Status: recommendations only; no framework edits implemented yet

## Executive Recommendation

Keep the current Beamer-tips foundation: 16:9, one point per slide, sparse text, readable labels, restrained semantic color, controlled builds, transition macros, and backup slides. The source pool does not overturn that framework. It sharpens it in two directions:

1. Economics research talks need a stronger opening architecture.
2. Empirical result slides need a stronger data-graphics and credibility standard.

The best update is not a large new theory of slides. It is a set of concrete rules that make agents build talks as seminars: state the question immediately, reveal the answer early, orient the skeptical audience, show evidence without chartjunk, and move documentation to backup.

## Recommended Additions

### 1. Add A Named Opening Standard

Add a "Big 5 / first-five-minutes" opening rule to `.claude/rules/slide-writing-principles.md` and to the storyteller/talk skills.

The opening of a full research seminar should answer, before dense technical detail:

- What is the research question?
- Why does it matter?
- What gap or unresolved problem remains in existing work?
- What does this paper do differently?
- What is the headline answer or takeaway?
- What is the main credibility threat, and how will the talk address it?

For shorter talks, compress this into fewer frames rather than skipping it. The exact number of frames should vary with talk length.

Sources supporting this: Davis, Shapiro, Bellemare, Cox/Pischke, and EC501.

### 2. Require Substantive Frame Titles

Add a rule that frame titles should usually state the slide's claim, object, or question, not just the section label. Good titles look like:

- `Question: do transfers persist across generations?`
- `Identification comes from staggered adoption`
- `Takeaway: effects are concentrated among new entrants`

Generic titles such as `Introduction`, `Data`, `Model`, and `Results` are acceptable only for true section dividers or when the frame content already has a visible claim header.

Sources supporting this: Ruhl and Cox/Pischke.

### 3. Add An "Intuition Bridge" Before Technical Density

After the opening and before the first dense equation, regression table, or complex chart, add a bridge that explains the core mechanism or empirical idea in simple terms. This can be:

- a recurring example;
- a minimal schematic;
- a one-cell version of the identification idea;
- a verbal/no-slide moment;
- a stripped-down equation before the full model.

This should be encoded in the storyteller and pedagogy-reviewer agents as a thing to look for, not as a mandatory slide macro.

Sources supporting this: Cox/Pischke, Ruhl, Shapiro, Bellemare, and EC501.

### 4. Strengthen Empirical Credibility Slides

Add a section to the slide-writing principles for empirical-talk credibility:

- Data slides should state each important variable's source, level of measurement, and definition.
- Identification slides should name the source of variation.
- Model/equation slides should define notation and connect the coefficient or estimand to the substantive quantity.
- Major threats should be acknowledged early and revisited with evidence, not hidden until Q&A.
- Work-in-progress talks should include an early feedback frame with 2-3 concrete questions for the audience.

This belongs in `.claude/rules/slide-writing-principles.md`, storyteller agents, pedagogy-reviewer agents, and slide-excellence review.

Sources supporting this: Shapiro and EC501, with reinforcement from Davis and Cox/Pischke.

### 5. Add A Data-Graphics Checklist

Add a compact data-graphics checklist under Visuals/Tables:

- Show the data needed for the claim.
- Reduce clutter: remove redundant gridlines, borders, legends, labels, 3D effects, gradients, and decorative marks.
- Integrate labels with the plotted marks when possible.
- Use direct labels instead of legends for simple two- or three-series figures.
- Use small multiples for heterogeneity, event studies, robustness panels, or repeated group comparisons when comparison is the point.
- Match chart type to comparison task: avoid pie charts for most category comparisons; use horizontal bars for long labels; use dot plots, coefficient plots, slope charts, or compact tables when they fit better.
- Use zero baselines for bars and area encodings; do not force zero into every line chart when it destroys relevant context.
- Make transformations, units, sample restrictions, and uncertainty visible when they affect interpretation.

This should also become part of slide-auditor checks.

Sources supporting this: Tufte and Schwabish, reinforced by Ruhl and Shapiro.

### 6. Add Color And Accessibility Verification

The current framework already says color should be color-blind-conscious. Strengthen it:

- Main comparisons should not rely on hue alone.
- Pair color with position, label, line style, marker shape, or annotation when the distinction is load-bearing.
- Figures should remain legible in grayscale or weak projector conditions.
- Avoid red/green and red/blue-only contrasts for essential comparisons.

This belongs in slide-writing principles, slide-auditor agents, and visual-audit skills.

Sources supporting this: Schwabish and Ruhl.

### 7. Strengthen Table And Result-Slide Rules

Add concrete table rules:

- Slide tables are not paper tables.
- Show the coefficient, row, cell, or comparison the audience needs.
- Use few significant digits; round to the precision needed for the claim.
- Align numeric columns on decimals, preferably with `siunitx`.
- Treat roughly 18 pt as a practical floor for central slide tables, with about 22 pt preferable when the table is the slide's main object.
- Move full regression output, robustness tables, and control lists to backup.
- Results frames should foreground a qualitative or quantitative bottom line.

Recommended preamble change: add `\usepackage{siunitx}` and define a local table-column convention for slide tables. Keep `booktabs`; consider de-emphasizing `dcolumn` over time.

Sources supporting this: Ruhl, EC501, Bellemare, Shapiro, Tufte, and Schwabish.

### 8. Add Talk-Length Budgeting

Add planning guidance:

- Short talks should be shorter talks, not seminar decks delivered faster.
- For short conference talks, one slide per minute is an upper bound, not a target.
- For full seminars, expect fewer core slides than minutes because interruptions and explanation take time; Ruhl's two-to-three minutes per core slide is a useful planning heuristic.
- Shorter versions should cut claims and details, not shrink fonts or keep every section.

This belongs in talk skills, storyteller agents, and README/user-guide guidance for asking agents to build a Beamer talk.

Sources supporting this: Bellemare, Ruhl, and Shapiro.

### 9. Tighten Literature And Contribution Slides

Add a rule against standalone literature-review sections in research talks unless the talk is explicitly a literature review.

Instead:

- fold closest antecedents into the opening;
- name two to four closest papers or literatures;
- state exactly what remains unresolved and what this paper adds;
- keep citations visually secondary with `\smallcitation{...}` when they are trailing references.

Sources supporting this: Bellemare, Davis, Cox/Pischke, and EC501.

### 10. Improve Endings

Add two conclusion rules:

- The last substantive slide should say how the audience's view should change.
- Do not use a standalone `Questions?` or `Thank you` slide as the only ending. Those can be spoken, or placed after the final takeaway if needed.

Sources supporting this: Davis and Bellemare.

### 11. Add Delivery Robustness Checks

Add a lightweight delivery QA rule:

- Decks should not depend on visible buttons, mouse access, or live interaction during the main talk.
- Optional detail should usually be in adjacent skippable frames or backup slides.
- For important talks, test the compiled PDF in full-screen mode and inspect figures at reduced scale or from the back of the room.
- Record seminar comments and revise before the next presentation.

Sources supporting this: Ruhl and EC501.

## Recommended Target Files For Implementation

Update these first:

- `.claude/rules/slide-writing-principles.md`
- `docs/deliverables/preambles/beamer-preamble.tex`
- `.agents/skills/talk/SKILL.md`
- `.claude/skills/talk/SKILL.md`
- `.agents/skills/visual-audit/SKILL.md`
- `.claude/skills/visual-audit/SKILL.md`
- `.agents/skills/slide-excellence/SKILL.md`
- `.claude/skills/slide-excellence/SKILL.md`
- `.codex/agents/storyteller.toml`
- `.claude/agents/storyteller.md`
- `.codex/agents/slide-auditor.toml`
- `.claude/agents/slide-auditor.md`
- `.codex/agents/pedagogy-reviewer.toml`
- `.claude/agents/pedagogy-reviewer.md`

Then update higher-level orientation docs:

- `AGENTS.md`
- `CLAUDE.md`
- `README.md`
- `docs/sources/USER-GUIDE.md`

## Suggested Framework Structure

If approved, refactor `.claude/rules/slide-writing-principles.md` into these sections:

1. Baseline slide discipline
2. Research-talk opening
3. Narrative and pacing
4. Empirical credibility
5. Visuals and data graphics
6. Tables and results
7. Citations and related work
8. Color, type, and accessibility
9. Builds, backups, and delivery robustness
10. Audit questions

This keeps the rule readable while making the newer seminar-architecture and empirical-graphics rules first-class.

## Do Not Add

The source pool includes advice that should not become rigid project rules:

- Do not require exactly one slide per minute.
- Do not require exactly five separate Big 5 slides in every talk.
- Do not ban all Beamer links or appendix navigation; just avoid main-talk dependence on mouse interaction.
- Do not require a visible outline slide if section structure is already clear.
- Do not maximize data density for live slides; projection and audience processing limits matter.
- Do not ban pie charts absolutely, but treat them as rare and usually inferior for research comparisons.
- Do not require every limitation in the opening; name the highest-stakes threat and route the rest to the relevant section or backup.

## Source-To-Recommendation Map

- Tufte: graphical integrity, chartjunk, data-ink discipline, small multiples, table-vs-chart judgment, direct integration of words and graphics.
- Schwabish: show data, reduce clutter, integrate labels with graphs, chart-type selection, accessibility and color checks, backup for exact lookup.
- Ruhl: substantive titles, answer early, recurring example, direct labels, minimal digits, delivery robustness, 16:9 confirmation.
- Davis: skeptical-referee opening, concise question, why care, contribution, credibility preview, conclusion as belief change.
- Shapiro: stakes-first opening, findings preview, data/source/level clarity, identification/model clarity, key vulnerabilities, talk length discipline.
- Bellemare: hook/question/antecedents/value-added/roadmap/results preview, no standalone literature review, backup convention, no final empty questions slide.
- Cox/Pischke: Big 5 opening, first-five-minutes priority, anti-mystery structure, intuition bridge, early caveat, avoiding too much too soon.
- EC501: immediate question slide, first-five-minutes checklist, table legibility targets, early weaknesses, empirical deck checklist, work-in-progress feedback frame.

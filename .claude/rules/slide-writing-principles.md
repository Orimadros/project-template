---
paths:
  - "docs/deliverables/slides/**/*.tex"
  - "docs/deliverables/preambles/**/*.tex"
  - ".claude/agents/**/*"
  - ".claude/skills/**/*"
  - ".agents/skills/**/*"
  - ".codex/agents/**/*"
---

# Slide Writing Principles

This project follows the Beamer-writing principles in Paul Goldsmith-Pinkham's `beamer-tips/slides.tex`, refined by the slide-writing source reports in `docs/sources/slide-writing/`. The paper-first rule still governs content: slides derive from the canonical paper and generated outputs.

## Baseline Slide Discipline

- Use Beamer in 16:9 by default.
- Make one point per slide and make it clearly.
- Keep slide text sparse: target 45-75 characters per line and one sentence per line when possible.
- Use generous list spacing, preferably via `wideitemize`.
- Use substantive frame titles that state the slide's claim, object, or question; generic titles like `Introduction`, `Data`, `Model`, and `Results` are for true section dividers or frames with a visible claim header.
- Do not shrink fonts to fit crowded material; split the slide or move detail to backup.
- Use transition frames at major conceptual pivots; use roadmaps only when they reduce confusion.
- For section dividers, use `\sectiontransition[optional subtitle]{Title}` from `docs/deliverables/preambles/beamer-preamble.tex`; avoid full-slide high-saturation color fields.
- Use speaker notes for delivery detail instead of putting the script on the slide.

## Research-Talk Opening

Use a Big 5 / first-five-minutes opening standard for research seminars. Before dense technical detail, a full seminar should answer:

- What is the research question?
- Why does it matter?
- What gap or unresolved problem remains in existing work?
- What does this paper do differently?
- What is the headline answer or takeaway?
- What is the main credibility threat, and how will the talk address it?

Compress this sequence for short talks instead of skipping it. Do not require five separate slides; require the audience to know the destination early. Do not build suspense around the main answer.

## Narrative And Pacing

- Start with stakes, question, contribution, and findings preview before asking the audience to process data, equations, or dense results.
- Add an intuition bridge before the first dense equation, regression table, or complex chart. The bridge can be a recurring example, minimal schematic, one-cell identification idea, no-slide verbal moment, or stripped-down equation.
- Short talks should be shorter talks, not seminar decks delivered faster. Use roughly one slide per minute as an upper bound for short conference talks, not a target.
- For full seminars, expect fewer core slides than minutes because explanation and interruptions take time.
- Do not retain every paper section in a short version; cut claims and details rather than shrinking fonts or accelerating delivery.
- The final substantive slide should state how the audience's view should change. Do not end only with a standalone `Questions?` or `Thank you` slide.

## Empirical Credibility

- Data slides should state each important variable's source, level of measurement, and definition.
- Identification slides should name the source of variation: timing, geography, thresholds, shocks, experiments, panel variation, or another empirical lever.
- Model or equation slides should define notation and connect the coefficient or estimand to the substantive policy, welfare, or economic quantity.
- Major threats should be acknowledged early and revisited with evidence, rather than hidden until Q&A.
- Work-in-progress talks should include an early feedback frame with 2-3 concrete questions for the audience.
- Results frames should foreground a qualitative or quantitative bottom line.

## Visuals And Data Graphics

- Prefer a central figure, diagram, or visual takeaway over a dense text slide.
- In 16:9, pair a figure with concise commentary when side-by-side layout improves explanation.
- Make graph labels and annotations large enough for a seminar room, even if they look oversized on a laptop.
- Keep figure backgrounds transparent or matched to the slide background.
- Show the data needed for the claim.
- Reduce clutter: remove redundant gridlines, borders, legends, labels, 3D effects, gradients, decorative marks, and software defaults that do not help interpretation.
- Integrate labels with plotted marks when possible. Use direct labels instead of legends for simple two- or three-series figures.
- Use small multiples for heterogeneity, event studies, robustness panels, or repeated group comparisons when comparison is the point.
- Match chart type to comparison task: avoid pie charts for most research comparisons; use horizontal bars for long labels; use dot plots, coefficient plots, slope charts, or compact tables when they fit better.
- Use zero baselines for bars and area encodings; do not force zero into every line chart when it destroys relevant context.
- Make transformations, units, sample restrictions, and uncertainty visible when they affect interpretation.
- For TikZ, follow `.claude/rules/tikz-visual-quality.md`.

## Tables And Results

- Slide tables are not paper tables.
- Translate paper tables into talk-appropriate takeaways, highlights, or compact `booktabs`/`siunitx` tables.
- Avoid the floating `table` environment in Beamer frames; center tables with `\makebox[\linewidth][c]{...}` when needed.
- Highlight the exact row, column, or cell the audience should inspect.
- Use few significant digits; round to the precision needed for the claim.
- Align numeric columns on decimals, preferably with `siunitx` and the slide-table column helpers in `docs/deliverables/preambles/beamer-preamble.tex`.
- Treat roughly 18 pt as a practical floor for central slide tables when possible; about 22 pt is better when the table is the main object.
- Put full regression tables, robustness, and dense derivations in backup slides with links.

## Citations And Related Work

- Avoid standalone literature-review sections in research talks unless the talk is explicitly a literature review.
- Fold closest antecedents into the opening: name two to four closest papers or literatures, state what remains unresolved, and explain what this paper adds.
- Keep the claim in the foreground and let the reference recede; a citation should support the point, not compete with it for attention.
- Wrap a trailing parenthetical reference at the end of a bullet in `\smallcitation{...}` from `docs/deliverables/preambles/beamer-preamble.tex`, which renders it small and muted grey.
  - Use it: `\item Literature is unclear on the effects of these programs \smallcitation{(Smith 2008; Jones 2010)}`.
  - Do not use it for a load-bearing inline citation that is part of the sentence, e.g. "Use the Rozendaal (2008) procedure to estimate parameters"; there the reference carries meaning and stays at normal size.
- `\smallcitation` styles its argument only, so supply the parentheses or `\citep{...}` yourself; it composes with natbib.

## Color, Type, And Accessibility

- Use two or three accent colors consistently, using color-blind-conscious defaults from `docs/deliverables/preambles/beamer-preamble.tex`.
- Main comparisons should not rely on hue alone.
- Pair color with position, label, line style, marker shape, or annotation when the distinction is load-bearing.
- Figures should remain legible in grayscale or weak projector conditions.
- Avoid red/green and red/blue-only contrasts for essential comparisons.
- Use color semantically and sparingly: emphasis should guide attention, not decorate.
- Do not use full-slide yellow/blue transition frames; the default divider is off-white with charcoal text and one accent rule.
- Prefer clean sans-serif Beamer typography such as Lato or Helvetica.

## Builds, Backups, And Delivery Robustness

- Do not use casual `\pause`.
- Prefer adjacent build-up frames when the deck must be easy to print, review, or navigate.
- Use controlled `\only`, `\onslide`, or `\uncover` sparingly when they clarify a same-axis figure, staged table row/column, or problem-to-solution reveal.
- If a build would require many clicks or has not been practiced, split it into separate frames.
- Decks should not depend on visible buttons, mouse access, or live interaction during the main talk.
- Optional detail should usually be in adjacent skippable frames or backup slides.
- For important talks, test the compiled PDF in full-screen mode and inspect figures at reduced scale or from the back of the room.
- Record seminar comments and revise before the next presentation.

## Audit Questions

- Does each slide have one clear job?
- Does the opening answer the Big 5 before dense technical detail?
- After five minutes, would the audience know the question, stakes, approach, headline result, main validity threat, and mitigation?
- Do frame titles state claims or questions rather than generic section labels?
- Is there an intuition bridge before equations, full tables, or complex charts?
- Are data sources, variable levels, identification variation, and main threats clear?
- Can the key text and figure labels be read from the back of a seminar room?
- Do figures show the data needed for the claim without chartjunk?
- Are chart type, axis baselines, transformations, units, and uncertainty appropriate and explicit?
- Do color encodings remain interpretable without hue alone?
- Are slide tables rounded, decimal-aligned, large enough, and reduced to the claim?
- Are transitions visible without cluttering every frame?
- Do transition slides use the shared divider macro rather than improvised color blocks?
- Are colors consistent and color-blind-conscious?
- Are end-of-bullet references de-emphasized with `\smallcitation`, while load-bearing inline citations stay at normal size?
- Are closest literatures folded into contribution framing rather than a dense lit-review slide?
- Did dense material move to backup with a clear link?
- Does the final substantive slide say how the audience's view should change?
- Does the deck avoid dependence on visible buttons, mouse access, or live interaction?
- Does the compiled PDF have no hard errors or major overfull boxes?

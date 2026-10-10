# Beamer talk principles

Talks derive from the canonical paper and generated results. They can simplify and
reorder the argument for an audience, but they do not introduce independent claims.
Use this as the shared standard for writing and reviewing talks.

## Structure and pacing

- Default to 16:9 Beamer. Give each slide one clear job and use a title that states its
  claim, object, or question. Generic titles such as “Data” or “Results” belong on
  section dividers or frames with a visible claim header.
- Keep slide text sparse, usually one sentence per line and roughly 45–75 characters
  per line. Use generous list spacing and speaker notes for delivery detail.
- In the opening, establish the research question, stakes, gap, contribution, headline
  answer, and main credibility threat before dense technical detail. Compress this
  sequence for short talks; do not hide the answer to create suspense.
- Add an intuition bridge before the first dense equation, regression table, or complex
  chart. A concrete example, small schematic, one-cell identification idea, or plain
  language explanation can do the job.
- Short talks should cut claims and detail rather than rush through a seminar deck or
  shrink its fonts. Use transition frames at major conceptual pivots; use roadmaps only
  when they reduce confusion.
- For work in progress, surface two or three concrete questions where audience feedback
  would help. The final substantive slide should state how the audience's view should
  change; do not end only with “Questions?” or “Thank you.”

## Empirical credibility

- State important variables' source, measurement level, and definition. Name the source
  of identifying variation, define notation, and connect estimates to their substantive
  quantity.
- Surface the main threats early and revisit them with evidence. Keep the paper's
  assumptions and limitations visible; do not make the slide deck sound more certain
  than the manuscript.
- Foreground the qualitative or quantitative result. Show units, transformations,
  sample restrictions, baselines, and uncertainty when they affect interpretation.
- Put closest antecedents in the contribution framing: usually two to four papers or
  literatures paired with the specific margin this paper adds. Avoid a long literature
  tour unless the talk is itself a literature review.

## Figures, tables, and visual access

- Prefer a central figure or diagram over a dense text slide. Choose a chart for the
  comparison at hand, remove marks that do not aid interpretation, and label series
  directly when practical.
- Make labels readable from the back of a seminar room. Re-export figures for
  presentation size when needed, with a transparent or matching background.
- Use compact `booktabs`/`siunitx` tables, highlight the row or cell that matters, and
  round to the precision the claim needs. Avoid floating `table` environments inside
  Beamer frames. Put full regression tables, robustness detail, and dense derivations
  in linked backup slides.
- Use a consistent, color-blind-conscious palette. Pair load-bearing color with
  position, shape, line style, or direct labels so meaning does not depend on hue.
- For section dividers, use `\sectiontransition[optional subtitle]{Title}` from
  `docs/deliverables/preambles/beamer-preamble.tex`. Avoid full-slide, high-saturation
  color blocks.
- Keep citations visually secondary when they trail a bullet: use
  `\smallcitation{(Author Year)}`. Keep inline citations at normal size when the
  reference is part of the sentence's meaning.

## Builds and interaction

- Avoid casual `\pause`. Use adjacent build-up frames when a deck should be easy to
  print and navigate. Use `\only`, `\onslide`, or `\uncover` sparingly when a reveal
  clarifies a figure or table.
- Keep the main talk independent of visible buttons, mouse access, and live
  interaction. Put optional material in skippable frames or backup.
- Inspect the compiled PDF for errors, overfull frames, and presentation-size legibility.
  For TikZ, also use `tikz-visual-quality.md` when creating or reviewing diagrams.

## Source basis

The baseline draws on Paul Goldsmith-Pinkham's [Beamer tips (2018)](https://paulgp.com/2018/04/30/beamer-tips.html)
and the [EC501 presentation guidelines](https://personal.lse.ac.uk/fischerg/Assets/EC501PresentationGuidelines.pdf)
by O. Bandiera, T. Besley, G. Bryan, R. Burgess, G. Fischer, M. Ghatak, and G. Padro.
Project-specific synthesis and further source notes are in `docs/sources/slide-writing/`.

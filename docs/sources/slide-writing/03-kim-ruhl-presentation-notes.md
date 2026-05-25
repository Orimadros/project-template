# Kim Ruhl, Presentation Notes

- Source: [Kim J. Ruhl, "Presentation notes"](https://www.kimjruhl.com/presentation-notes)
- Access status: Accessible directly from Kim Ruhl's website on 2026-05-25.
- Report date: 2026-05-25

## Core Slide-Writing Principles

### Direct source claims

- Ruhl frames the main goal as making slides clear while using limited screen space well, and as making the deck robust to imperfect rooms, projectors, remotes, operating systems, and Zoom setups. Source: [Ruhl, "Presentation notes"](https://www.kimjruhl.com/presentation-notes).
- Each slide should aim for one idea, and an hour-long talk may need only about 20 slides if each slide takes roughly two to three minutes. Source: [Ruhl, "Presentation notes"](https://www.kimjruhl.com/presentation-notes).
- Slide titles should communicate substance rather than label sections generically; examples include titles that name the decision problem or empirical fact. Source: [Ruhl, "Presentation notes"](https://www.kimjruhl.com/presentation-notes).
- A research talk should not hide the answer like a mystery. Even for a puzzle paper, the audience should know early where the argument is going. Source: [Ruhl, "Presentation notes"](https://www.kimjruhl.com/presentation-notes).
- A presenter should choose and prepare an example before the talk, then use the same example consistently across motivation, mechanism, and conclusion. Source: [Ruhl, "Presentation notes"](https://www.kimjruhl.com/presentation-notes).
- Ruhl recommends 16:9 Beamer slides, specifically `\documentclass[aspectratio=169]{beamer}`, because most projectors now support that format. Source: [Ruhl, "Presentation notes"](https://www.kimjruhl.com/presentation-notes).
- Figures need larger labels than paper figures, fewer panels and series when possible, and a projection test from the back of a room. Source: [Ruhl, "Presentation notes"](https://www.kimjruhl.com/presentation-notes).
- Figures should not rely on color alone; red-green contrasts should be avoided, and markers or line styles should help distinguish series when projectors or room conditions are weak. Source: [Ruhl, "Presentation notes"](https://www.kimjruhl.com/presentation-notes).
- With only two or three clearly distinct lines, direct labels on the figure may be better than a legend. Ruhl also suggests checking whether a figure would be clearer in logs or normalized by a relevant scale variable. Source: [Ruhl, "Presentation notes"](https://www.kimjruhl.com/presentation-notes).
- Visible slide buttons are risky because the presenter may not have convenient mouse access, and buttons can distract the audience. Ruhl prefers inserting optional slides that can be skipped when not needed. Source: [Ruhl, "Presentation notes"](https://www.kimjruhl.com/presentation-notes).
- Tables should use as few significant digits as the claim allows, and LaTeX `siunitx` can align numeric columns on decimal points. Source: [Ruhl, "Presentation notes"](https://www.kimjruhl.com/presentation-notes).

### Interpretation for economic research talks

- Treat each slide as a unit of argument, not a storage place for paper content. In a seminar, the core deck should be paced around explanation and interruption, not around reproducing every paper section.
- Frame titles should often state the economic object, empirical fact, model force, or identification point the audience should retain.
- For job-market and seminar talks, the introduction should reveal the central answer and contribution early enough that the audience can evaluate the evidence rather than guess the destination.
- A recurring example is useful for economic mechanisms because it reduces switching costs when moving from facts to model intuition to empirical interpretation.
- Figures should be rebuilt for the talk, not copied mechanically from the paper. In particular, font sizes, line widths, legends, color encodings, transformations, and normalization choices should be audited for live presentation.
- Optional detail should behave like skippable content in the deck, not like an interaction that depends on mouse control or a working hyperlink.

## Beamer-Specific Implications

- Use 16:9 Beamer as the default for research talks:

```tex
\documentclass[aspectratio=169]{beamer}
```

- Prefer informative frame titles such as `Fact 1: exporters are larger before entry`, `Model force: fixed costs create selection`, or `Identification comes from staggered adoption`, rather than `Introduction`, `Model`, or `Results`.
- Budget the main talk around roughly two to three minutes per core frame. For a 60-minute seminar, this implies a lean main deck with details moved into backup or skippable appendix frames.
- Put the answer and contribution near the front. A Beamer introduction should make the research question, answer, mechanism, and evidence path visible before the audience sees dense results.
- Use one recurring economic example when the paper's mechanism is abstract. In Beamer terms, this can be a repeated short label, firm/country/household example, or schematic that reappears at major transitions.
- Re-export or rebuild figures for slides with presentation-scale fonts, thicker lines, high-contrast labels, and color-independent encodings. For `pgfplots`, TikZ, R, Stata, or Python exports, tune label size and line width for the projected slide, not the paper PDF.
- Prefer direct line labels over legends when a figure has only a few series and the labels fit cleanly. When legends remain necessary, make them large and unambiguous.
- Use `siunitx` `S` columns or equivalent decimal alignment for compact numeric tables, and round estimates to the precision needed for the talk's claim.
- Avoid prominent Beamer navigation buttons on content slides. If navigation is necessary, use unobtrusive text links or place optional material as adjacent or backup frames that can be skipped with a remote.
- Add a delivery QA step for important talks: open the compiled PDF in a standard PDF viewer, enter full-screen mode, test keyboard/remote advancement, check Zoom focus if relevant, and inspect figures from the back of a room or at reduced scale.

## What This Would Change In Our Current Framework

- Add a rule that frame titles should be substantive claims or objects, not generic section labels.
- Add a talk-structure rule to disclose the answer and contribution early, especially for puzzle-style papers.
- Add guidance to use one prepared recurring example across motivation, mechanism, and conclusion when the talk relies on an abstract economic mechanism.
- Add a robustness rule for delivery: decks should not depend on visible buttons, mouse access, or live interaction; optional detail should usually be represented as skippable or backup frames.
- Add table guidance on minimal significant digits and decimal alignment with `siunitx`.
- Sharpen the existing visual guidance by recommending direct line labels instead of legends for simple two- or three-series figures, and by explicitly requiring non-color encodings such as markers or line styles where series must be distinguished.
- Add a loose pacing heuristic: a standard seminar main deck should be short enough for two to three minutes per core slide, with dense detail moved to backup.

## Tensions Or Caveats

- Ruhl explicitly says some advice is idiosyncratic, so the notes should be treated as practical heuristics rather than universal rules.
- The 16:9 recommendation already matches the current project framework; it confirms rather than changes that default.
- The "about 20 slides for an hour" heuristic depends on audience interruptions, slide density, field norms, and whether the talk includes theory, data description, or live derivations.
- Direct labels can outperform legends in simple figures, but they can clutter a graph when labels overlap or when many series are present.
- The warning against buttons is in tension with Beamer appendix navigation. A conservative synthesis is not to ban links, but to avoid visible buttons or interactions that require mouse access during the main talk.
- Some delivery logistics, especially Zoom controls and local PDF viewer behavior, are environment-specific and may age faster than the slide-writing principles.

## Source Notes

- This report uses the original web page only: [Kim J. Ruhl, "Presentation notes"](https://www.kimjruhl.com/presentation-notes).
- No archived or secondary reconstruction was needed because the source was accessible on 2026-05-25.
- No BibTeX entry was added. The assigned source is a presentation-advice webpage, and the current task is to extract slide-writing principles rather than add a research citation.

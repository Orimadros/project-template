# Marc F. Bellemare blog post 10053

- Source: Marc F. Bellemare, ["22 Tips for Conference and Seminar Presentations"](https://marcfbellemare.com/wordpress/10053)
- Access status: Live source accessible on 2026-05-25. Page lists publication date as April 8, 2014 and last update as May 24, 2015.
- Report date: 2026-05-25

## Core Slide-Writing Principles

Direct source claims:

- Talk length should govern deck size and content selection. Bellemare treats one slide per minute as a useful upper-bound heuristic, especially for short conference talks, while noting that longer seminars need not literally have one slide per minute. Source: [Bellemare](https://marcfbellemare.com/wordpress/10053).
- The shorter the talk, the more concentrated the motivation must be. In short conference slots, the introduction should quickly answer why the audience should care. Source: [Bellemare](https://marcfbellemare.com/wordpress/10053).
- The technical level should be pitched to smart economists who are not necessarily specialists in the narrow field. Motivation, intuition, and plain-English definitions should carry the talk; technical material should not be used mainly to impress. Source: [Bellemare](https://marcfbellemare.com/wordpress/10053).
- Some technical loss is inevitable in theory, empirical-framework, or identification slides, but the speaker should explain those pieces in plain English and bring the audience back at the conclusion. Source: [Bellemare](https://marcfbellemare.com/wordpress/10053).
- A talk should give the audience an outline or visible navigation, unless the Beamer theme already makes the section structure clear. It should also preview the results early rather than withhold them. Source: [Bellemare](https://marcfbellemare.com/wordpress/10053).
- Bellemare recommends an economics introduction sequence attributed to Keith Head: hook, research question, antecedents, value added, and roadmap. Source: [Bellemare](https://marcfbellemare.com/wordpress/10053).
- Slides should not contain a standalone literature review. The closest prior studies belong in the introduction as antecedents and value added, not as a full lit-review section. Source: [Bellemare](https://marcfbellemare.com/wordpress/10053).
- After the introduction, Bellemare's default order is theoretical framework, empirical framework, data, results, limitations, and conclusion, with compression depending on available time. Source: [Bellemare](https://marcfbellemare.com/wordpress/10053).
- Backup slides are a deliberate design device: descriptive statistics, robustness checks, proofs, full results, and extra graphs can sit after the main deck for use during questions. Source: [Bellemare](https://marcfbellemare.com/wordpress/10053).
- In empirical papers with a theory component, if the model is not the main contribution, the main deck may only need assumptions and testable predictions; the full model can go to backup. Source: [Bellemare](https://marcfbellemare.com/wordpress/10053).
- The presentation should generally follow the paper's order and can reuse polished paper language, but the slide version should still be tailored to time and audience. Source: [Bellemare](https://marcfbellemare.com/wordpress/10053).
- When a graph or picture can tell the story, it should be used. For empirical results, tables should foreground the coefficient or coefficients of interest and move full regression output to backup. Source: [Bellemare](https://marcfbellemare.com/wordpress/10053).
- Fieldwork photos and maps should be included only when they help the audience understand a necessary point, such as a spatial source of variation; otherwise they belong in backup or should be omitted. Source: [Bellemare](https://marcfbellemare.com/wordpress/10053).
- A final one-word "Questions?" or "Thank You!" slide is not necessary; thanks can be spoken at the beginning or end. Source: [Bellemare](https://marcfbellemare.com/wordpress/10053).

Interpretation for Beamer/economic research talks:

- The post is less a visual-design manual than a talk-architecture memo for economists: it prioritizes timing, audience orientation, contribution framing, and separating main-deck claims from backup evidence.
- Bellemare's advice supports a paper-first workflow, but not a paper-dump workflow. The talk can follow the manuscript's logic while compressing exposition, translating tables, and moving low-priority proof or robustness detail to backup.
- The core audience-management principle is early orientation: state the question, locate the contribution, show where the talk is going, and preview results before asking the audience to process methods or identification details.

## Beamer-Specific Implications

- Build the main deck against the allotted speaking time. For a 15-minute conference slot, the main section should be capped near 15 slides and often below that if slides contain dense figures, methods, or expected interruptions.
- Use Beamer structure intentionally: a compact outline frame or visible section navigation should appear early, but a separate outline is optional if the theme already displays section progress clearly.
- In the introduction, create distinct but short frames for hook, research question, closest antecedents/value added, roadmap, and results preview. Avoid a section titled "Literature Review."
- Put `\appendix` or the project's backup-slide mechanism immediately after the final substantive takeaway, then place descriptive statistics, robustness tables, proofs, extra maps, full regression tables, and model derivations there.
- For empirical result frames, replace full paper regression tables with compact Beamer tables or visuals: coefficient of interest, standard error or confidence interval, sample size if needed, and yes/no rows for controls or fixed effects.
- For empirical papers with auxiliary theory, keep the main deck to assumptions, mechanism, and testable predictions; reserve derivations, propositions, and proofs for backup.
- Treat maps, field photographs, and context images as evidence or explanation, not decoration. In Beamer terms, include them only when the frame's claim depends on them.
- End with a conclusion/takeaway frame that re-states the answer and contribution. Do not spend a final frame only on "Questions?" or "Thank You!"
- Use speaker notes or rehearsal notes for delivery language. The slides should cue a conversational explanation rather than contain a script to be read.

## What This Would Change In Our Current Framework

- Add an economics-talk introduction recipe to the slide-writing rules: hook, research question, closest antecedents, value added, roadmap, and early results preview.
- Add a rule against standalone literature-review sections in talks; closest studies should be folded into the value-added frame or a very compact antecedents frame.
- Add a planning rule that main-deck slide count should be budgeted against talk length, with roughly one slide per minute as an upper bound for short conference presentations.
- Add a Beamer backup convention: main deck first, then appendix slides for full tables, robustness checks, descriptive statistics, proofs, derivations, and extra context.
- Add a results-table convention for talks: foreground coefficients of interest and summarize controls/fixed effects with compact indicator rows, leaving full regressions for backup.
- Add a closing-slide preference: use a substantive conclusion or takeaway slide rather than a standalone "Questions?" or "Thank You!" slide.

## Tensions Or Caveats

- The one-slide-per-minute heuristic is a planning bound, not a universal target. Dense figures, live discussion, and seminar interruptions can require fewer slides.
- Bellemare's "no literature review" rule should not be read as "no citations." For economic research talks, the closest antecedents still matter, but they should support the contribution claim rather than become a separate tour of the literature.
- Following the paper's order can conflict with talk clarity when the paper has a long institutional background or technical setup. The safer interpretation is to preserve the argument's dependency order while compressing or relocating detail.
- The advice is a 2014 individual blog post, not a formal design standard. Some delivery recommendations, such as the advice on jokes, are speaker- and audience-dependent.
- Bellemare's preference for Beamer/PDF over PowerPoint is still relevant for LaTeX-heavy economics talks, but the software comparison is less important than the underlying robustness principle: use a format that preserves equations and compiles reliably.

## Source Notes

- This report uses the live Marc F. Bellemare page only; no archived reconstruction or secondary source was needed.
- Source title on page: "22 Tips for Conference and Seminar Presentations."
- The post covers preparation, delivery, posters, and question handling. This report extracts only the portions relevant to Beamer slides, economics seminar structure, and empirical research-talk design.
- The source cites other resources, including William Thomson's guide and Keith Head's introduction formula, but those linked resources were not independently reviewed for this single-source report.

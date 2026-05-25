# LSE EC501 Presentation Guidelines PDF

- Source: [EC501 Development and Growth PhD seminar, "Guidelines for Presentations"](https://personal.lse.ac.uk/fischerg/Assets/EC501PresentationGuidelines.pdf)
- Access status: Direct PDF accessible from the assigned LSE URL on 2026-05-25; downloaded with `curl` and text-extracted locally. No secondary or mirrored source was needed.
- Report date: 2026-05-25

## Core Slide-Writing Principles

### Direct source claims

- The document treats professional presentation as a core research skill for PhD students, not as cosmetic packaging around the paper. Source: [PDF, p. 1](https://personal.lse.ac.uk/fischerg/Assets/EC501PresentationGuidelines.pdf#page=1).
- The seminar strongly prefers concision over rambling, and even failed or unstable results should be presented by focusing on what went wrong, next steps, and where feedback would help. Source: [PDF, p. 1](https://personal.lse.ac.uk/fischerg/Assets/EC501PresentationGuidelines.pdf#page=1).
- For all papers, the research question should appear clearly on one slide and should appear immediately. Source: [PDF, p. 1](https://personal.lse.ac.uk/fischerg/Assets/EC501PresentationGuidelines.pdf#page=1).
- The speaker should motivate why the question is interesting, relevant, or important. Source: [PDF, p. 1](https://personal.lse.ac.uk/fischerg/Assets/EC501PresentationGuidelines.pdf#page=1).
- The speaker should know the related literature well and state the contribution clearly, but the audience does not need long summaries of existing work. Source: [PDF, p. 1](https://personal.lse.ac.uk/fischerg/Assets/EC501PresentationGuidelines.pdf#page=1).
- Slides and tables should be readable from the back of the room. The source warns that journal-ready tables can still be poor slide tables, suggests about 18 pt as a lower bound and 22 pt as better, and recommends distilling tables to key outcomes or using handouts. Source: [PDF, p. 1](https://personal.lse.ac.uk/fischerg/Assets/EC501PresentationGuidelines.pdf#page=1).
- Speakers should be upfront about weaknesses, preferably in the introduction, and should not hide them. Source: [PDF, p. 1](https://personal.lse.ac.uk/fischerg/Assets/EC501PresentationGuidelines.pdf#page=1).
- Speakers should write down comments and address them before later presentations. Source: [PDF, p. 1](https://personal.lse.ac.uk/fischerg/Assets/EC501PresentationGuidelines.pdf#page=1).
- The first five minutes should give the audience the question, importance, approach, headline findings, main validity threats, and mitigation strategy. Source: [PDF, p. 1](https://personal.lse.ac.uk/fischerg/Assets/EC501PresentationGuidelines.pdf#page=1).
- For work-in-process talks, the introduction can tell the audience where feedback would be most useful. Source: [PDF, p. 1](https://personal.lse.ac.uk/fischerg/Assets/EC501PresentationGuidelines.pdf#page=1).
- For empirical papers, the speaker should provide a basic theoretical framework and explain how theory maps into the empirical analysis. Source: [PDF, p. 2](https://personal.lse.ac.uk/fischerg/Assets/EC501PresentationGuidelines.pdf#page=2).
- Empirical talks should be clear about data sources, variable definitions, descriptive statistics for main variables, identification strategy, sources of variation, the estimated model, variable inclusion choices, and confounding issues. Source: [PDF, p. 2](https://personal.lse.ac.uk/fischerg/Assets/EC501PresentationGuidelines.pdf#page=2).
- For theoretical papers, the document emphasizes environment, notation, assumptions, main results, intuition, and examples or graphs, while discouraging technical proof detail unless it is itself insightful. Source: [PDF, p. 2](https://personal.lse.ac.uk/fischerg/Assets/EC501PresentationGuidelines.pdf#page=2).

### Interpretation for economic research talks

- The opening should be built as an argument checkpoint, not as administrative front matter. A serious economics seminar should make the research question, stakes, contribution, method, result, and credibility limits visible before the audience reaches the detailed evidence.
- The contribution slide should be selective and contrastive. It should show that the presenter understands the nearest literature, but it should not become a miniature literature review.
- The source is unusually explicit that weaknesses belong early. For empirical talks, that means identification threats, data limitations, and unresolved confounds should be framed as part of the credibility argument rather than saved for defensive Q&A.
- Slide tables need to be redesigned for the room. A table can satisfy journal conventions and still fail as a Beamer object if the audience cannot read it quickly from a distance.
- Work-in-process decks should not pretend to be finished papers. They should direct the audience toward the dimensions where feedback can most improve the project.
- The empirical-talk checklist implies a minimum sequence: theory or framework, data and measurement, descriptive facts, identification and variation, estimating equation, threats, and results. Not every item requires a long section, but each needs enough visibility for the audience to trust the findings.
- The theory guidance transfers to empirical Beamer talks when the mechanism is model-based: define the environment and notation only as much as needed, state assumptions, show the main result, then spend time on intuition and examples rather than proof mechanics.

## Beamer-Specific Implications

- Start with a direct question frame. The first substantive Beamer frame should state the research question in one compact slide, not wait until after background, agenda, or literature slides.
- Design the first five minutes as a visible mini-talk: question, motivation, contribution, approach, headline result, and the main validity concern with its mitigation. In a 60- or 90-minute seminar, later sections can expand each element.
- Use a short contribution frame rather than a dense related-work frame. A useful pattern is two to four closest literatures or papers, each paired with the specific margin of contribution, with citations visually secondary.
- Add an early "Weaknesses / Threats" moment for empirical decks. It can be a short frame in the introduction or a clearly signposted preview that returns later with diagnostics and robustness evidence.
- For work-in-process Beamer decks, include an early feedback frame with two or three concrete questions for the audience, such as measurement, identification threat, mechanism interpretation, or next empirical test.
- Rebuild paper tables for slides. Prefer compact `booktabs` tables, large numeric text, few columns, highlighted key rows or cells, and moved robustness/detail to backup. Treat 18 pt as a practical floor and 22 pt as a better target when the table is central.
- Use handouts, appendix frames, or backup slides for full tables that cannot be made legible without losing the main point.
- For empirical talks, include dedicated frames for data provenance and measurement: data source, unit of observation, variable definition, and descriptive statistics for main variables.
- Make the identification frame name the source of variation. The audience should know whether the design uses timing, geography, thresholds, shocks, experiments, panel variation, or another empirical lever.
- Put the estimated model on a slide only if the notation is defined and the included or excluded variables can be justified. Otherwise, the equation becomes decoration rather than evidence.
- For theory-heavy sections, use Beamer frames in this order: environment, key notation, assumptions, main result, intuition, example or graph. Keep proof detail in backup unless the proof step is part of the insight.
- Maintain a post-talk comment log and revise the deck before the next presentation. This is not a Beamer macro issue, but it is a concrete talk-development workflow implied by the source.

## What This Would Change In Our Current Framework

- Add a first-five-minutes audit question to `.claude/rules/slide-writing-principles.md`: after five minutes, would the audience know the question, stakes, approach, headline result, main validity threat, and mitigation?
- Add an opening rule that the research question should appear immediately on one slide.
- Add a work-in-process rule: if the project is unfinished, include an early frame that tells the audience what kind of feedback would be most useful.
- Add an empirical deck checklist covering theoretical framework, data sources, variable definitions, descriptive statistics, identification/source of variation, estimating model, variable choices, and confounding threats.
- Add a table-legibility rule with a practical font-size target: avoid slide tables below roughly 18 pt when possible, prefer about 22 pt for central tables, and move full journal tables to backup or handouts.
- Add a credibility rule that major weaknesses or threats should be acknowledged early and then revisited with evidence, rather than hidden until questions.
- Add a light process rule to record seminar comments and address them before the next presentation version.

## Tensions Or Caveats

- The source is a PhD seminar handout and a minimal-requirements checklist, not a full slide-design manual. It gives strong structure and presentation norms but little detail on color, typography, overlays, graphics, or Beamer implementation.
- The first-five-minutes standard is demanding. For short conference talks, it should be compressed into an opening sequence rather than interpreted as a requirement to show every caveat in detail.
- The advice to acknowledge weaknesses early is valuable, but the opening can become overloaded if every possible limitation is listed. The conservative Beamer translation is to name the highest-stakes threats early and move secondary threats to the relevant section or backup.
- The table font-size guidance is a rule of thumb. Some equations, diagrams, and compact result summaries may need different sizing, but the underlying requirement is room-level legibility.
- The empirical checklist is not the same as a required visible table of contents. In a polished talk, some items can be merged if the audience still understands the design and evidence.
- The source includes theory-paper guidance. For this empirical project template, the theory-specific sequence matters mainly when the empirical paper uses a formal model, conceptual framework, or mechanism section.

## Source Notes

- The primary source was accessible at the assigned URL: [https://personal.lse.ac.uk/fischerg/Assets/EC501PresentationGuidelines.pdf](https://personal.lse.ac.uk/fischerg/Assets/EC501PresentationGuidelines.pdf).
- Local `pdfinfo` reports a 3-page A4 PDF titled "EC501 Development and Growth- PhD seminar," created with Microsoft Word 2010 on 2012-10-09. The PDF metadata lists `Author: Suntory`; the visible document header lists O. Bandiera, T. Besley, G. Bryan, R. Burgess, G. Fischer, M. Ghatak, and G. Padro.
- The PDF itself lists additional outside resources on presentations and job-market advice, but this report does not use those sources because the assigned task was to work only on the LSE EC501 guideline PDF.
- No bibliography entry was added. The task requested a source report, and the available document is an online course/seminar handout rather than a conventional bibliographic publication.

---
name: discover
description: Map the literature, source evidence, and data feasibility for a research question.
disable-model-invocation: true
---

# Discover research terrain

Use this when Leo asks for a source-grounded map of a topic, literature, paper, or
potential data source. The purpose is to surface evidence and open questions. Leo owns
the research question, contribution, data choices, and other substantive decisions.

## Workflow

1. Parse the requested question, topic, paper, or source. Check `CONTEXT.md`, relevant
   material in `docs/sources/`, `docs/sources/references.bib`, and the canonical paper
   when one exists. Reuse the project's source material before expanding the search.
2. Search authoritative scholarly sources for relevant work. Verify each source's
   title, authors, year, publication or working-paper status, and persistent identifier
   from a publisher, journal, working-paper series, or author source. Treat a search
   snippet as a lead, not verification. Cover recent work and retain older papers when
   they remain foundational. Use current sources for claims about the latest state of a
   literature or data availability.
3. Read local PDFs using `../../references/pdf-source-reading.md`. Distinguish a paper's
   reported result from your synthesis or inference. Identify disagreement, differences
   in settings or methods, and limits of what the available sources establish.
4. If data feasibility is in scope, report the source, unit, period, coverage, access
   terms, and known measurement limits only when verified. Leave dataset selection,
   combinations, and research use to Leo.
5. Return a concise map with the closest literature, main findings and disagreements,
   candidate gaps or questions, relevant data evidence, and unresolved facts. Label
   inferences and uncertainties, and link each source-backed claim to its source.
   Include verified BibTeX entries when useful; identify duplicate or incomplete
   entries rather than inventing fields. Never fabricate citation details.

## Boundaries and completion

Do not turn a candidate gap into a settled contribution or select a research design.
Do not download, alter, or register data unless Leo explicitly asks for that separate
work. Do not edit the bibliography or save a memo unless requested. When asked to save,
use the requested path or propose a concise file in `docs/work/reviews/`.

The work is complete when every material literature claim has a verified source, the
status of working papers versus published versions is clear, and remaining evidence
gaps are stated.

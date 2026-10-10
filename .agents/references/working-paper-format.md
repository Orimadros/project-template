# Working-paper defaults

Use these as starting conventions when the project has not specified a different
format. They do not replace target-journal instructions or author decisions.

- The canonical article is `docs/deliverables/articles/main/main.tex`; its section
  files live under `docs/deliverables/articles/main/sections/`.
- Keep article-specific source files together under
  `docs/deliverables/articles/<name>/`. Shared LaTeX setup belongs in
  `docs/deliverables/preambles/`, references in `docs/sources/references.bib`, and
  generated empirical outputs in `results/`.
- A common article sequence is title and author block, abstract, keywords and JEL
  codes, introduction, background and related literature, data, empirical strategy,
  results, conclusion, and references. Adapt it to the paper and venue.
- Follow the existing document's compiler and bibliography system. The template
  default is XeLaTeX with BibTeX; shared style belongs in the preambles. Prefer
  `booktabs` for tables and `cleveref` for cross-references when those packages are
  already part of the project setup.
- Compile root article documents with `make articles`. Do not compile section
  fragments as stand-alone documents.
- Read `.claude/references/journal-profiles.md` only when a venue matters. Its
  placeholders are not journal requirements; verify current requirements from the
  journal before treating them as binding.

The canonical paper is the authority for the project's argument, notation, claims,
tables, and figures. See `CONTEXT.md` for the current repository map.

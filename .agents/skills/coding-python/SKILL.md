---
name: coding-python
description: Python coding preferences and input-registration guidance for approved project work.
disable-model-invocation: true
---

# Python coding preferences

This is supporting context for an approved Python implementation or Python code
review. Supply it deliberately to the worker or reviewer; it does not authorize a
change. The researcher's settled choices govern the analysis. Return any new choice
about the estimand, sample, variable construction, model, inference, or interpretation
to Leo.

- Keep imports at the top of the file. Use project-relative paths and declare fixed
  input and output paths in the source. Pipeline entry points take no path arguments.
  Read the current repository map and naming convention from `CONTEXT.md` and
  `AGENTS.md`.
- Start an entry script with a concise purpose and data-flow comment. Keep its main
  execution path readable; move repeated or multi-step mechanics into well-named
  functions. Use descriptive names and comments for substantive sample,
  transformation, or modeling choices.
- Make outputs deterministic when possible and set explicit seeds for stochastic
  procedures. Keep long-lived notebook logic in scripts under `code/` when the task
  calls for a reproducible pipeline.
- Write derived data to `data/clean/` or `data/tmp/`; write generated tables, figures,
  and model outputs under `results/`. Change the code that generates an output instead
  of hand-editing a generated file.
- Use `code/lib/project_io.py` for registered local inputs and run records. Wrap the
  script's work in `with RunRecord(script=__file__, outputs=[...]) as run:` and call
  `run.input_file(declaration)` before the ordinary reader. A declaration can register
  one file, a direct directory, or a filename glob in one directory. The helper records
  registered paths and observed modification times; it does not find hidden reads or
  verify file contents. Follow the module's examples for the exact call shape. If the
  module is absent, report the dependency instead of inventing a parallel recorder.
- Keep a script's input and output paths fixed in its source. For pending work, point
  candidate outputs inside that issue's `pending-approval/` folder; use the agreed
  production path after shipping.

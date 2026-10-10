---
name: coding-r
description: R coding preferences and input-registration guidance for approved project work.
disable-model-invocation: true
---

# R coding preferences

This is supporting context for an approved R implementation or R code review. Supply
this file deliberately to the worker or reviewer; it does not authorize a change.
The researcher's settled choices govern the analysis. Return any new choice about the
estimand, sample, variable construction, model, inference, or interpretation to Leo.

- Put package imports at the top of the script using `library()`; avoid `require()`.
- Use project-relative paths and declare fixed input and output paths in the source.
  Pipeline entry points take no path arguments. Read the current repository map and
  naming convention from `CONTEXT.md` and `AGENTS.md`.
- Start an entry script with a concise purpose and data-flow comment. Keep the top-level
  code readable as a sequence of named steps; put repeated or multi-step logic in
  clearly named functions. Use `snake_case`, descriptive names, explicit returns, and
  comments for substantive sample, transformation, or modeling choices.
- Set `set.seed()` once when a stochastic procedure needs it. Keep deterministic
  outputs when the task permits.
- Write derived data to `data/clean/` or `data/tmp/`; write generated tables, figures,
  and model outputs under `results/`. Change the code that generates an output instead
  of hand-editing a generated file.
- Use `code/lib/project_io.R` for registered local inputs and run records. Source the
  module, declare outputs in the script, and wrap the run in `with_run_record()`; call
  `run$input_file(declaration)` inside its callback before the ordinary reader. A
  declaration can register one file, a direct directory, or a filename glob in one
  directory. The helper records registered paths and observed modification times; it
  does not find hidden reads or verify file contents. Follow the module's examples for
  the exact call shape. If the module is absent, report the dependency instead of
  inventing a parallel recorder.
- Keep a script's input and output paths fixed in its source. For pending work, point
  candidate outputs inside that issue's `pending-approval/` folder; use the agreed
  production path after shipping.
- Keep mathematical lines longer than 100 characters only when splitting them would
  harm readability; explain the operation in a nearby comment.

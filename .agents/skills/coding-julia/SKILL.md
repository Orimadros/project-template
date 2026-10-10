---
name: coding-julia
description: Julia coding preferences and input-registration guidance for approved project work.
disable-model-invocation: true
---

# Julia coding preferences

This is supporting context for an approved Julia implementation or Julia code review.
Supply it deliberately to the worker or reviewer; it does not authorize a change.
The researcher's settled choices govern the analysis. Return any new choice about the
estimand, sample, variable construction, model, inference, or interpretation to Leo.

- Keep package imports at the top. Use project-relative paths and declare fixed input
  and output paths in the source. Pipeline entry points take no path arguments. Read
  the current repository map and naming convention from `CONTEXT.md` and `AGENTS.md`.
- Start an entry script with a concise purpose and data-flow comment. Keep its main
  execution path readable; move repeated or multi-step mechanics into clearly named
  functions. Use descriptive names and comments for substantive sample,
  transformation, or modeling choices.
- Set explicit seeds for stochastic procedures and keep outputs deterministic enough
  for the project's Make checks.
- Write derived data to `data/clean/` or `data/tmp/`; write generated tables, figures,
  and model outputs under `results/`. Change the code that generates an output instead
  of hand-editing a generated file.
- Use `code/lib/project_io.jl` for registered local inputs and run records. Include the
  module, use `.ProjectIO`, and wrap the script in the documented
  `run_record(@__FILE__, outputs) do run` form. Call `input_file(run, declaration)`
  before the ordinary reader. A declaration can register one file, a direct directory,
  or a filename glob in one directory. The helper records registered paths and
  observed modification times; it does not find hidden reads or verify file contents.
  Follow the module's examples for the exact call shape. If the module is absent,
  report the dependency instead of inventing a parallel recorder.
- Keep a script's input and output paths fixed in its source. For pending work, point
  candidate outputs inside that issue's `pending-approval/` folder; use the agreed
  production path after shipping.

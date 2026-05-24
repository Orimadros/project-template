# Julia Coding Standards

- Use relative paths rooted at the project directory.
- Keep package imports at the top of the file.
- Set seeds for stochastic procedures.
- Write generated analysis outputs to `results/` and derived data to `data/clean/` or `data/tmp/`.
- Keep script outputs deterministic enough to be checked by Make targets.

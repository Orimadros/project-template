# R Coding Standards

- Put all packages at the top of the script.
- Use relative paths rooted at the project directory.
- Use `set.seed()` once when stochastic procedures are used.
- Write generated datasets to `data/clean/` or `data/tmp/`.
- Write generated tables, figures, and model outputs to `results/`.
- Prefer explicit file contracts in script headers: inputs, outputs, and purpose.
- Avoid hidden global state; make transformations reproducible from the Make target.

# Python Coding Standards

- Use relative paths rooted at the project directory.
- Keep imports at the top of the file.
- Prefer deterministic outputs and explicit seeds when randomness is used.
- Write generated analysis outputs to `results/` and derived data to `data/clean/` or `data/tmp/`.
- Keep notebooks reproducible; long-lived logic should graduate to scripts under `code/`.

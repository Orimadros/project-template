# Meta-Governance: Working Project + Reusable Template

This repository serves two roles at once:

1. A working empirical project scaffold
2. A reusable template for future projects

## Decision Rule

When editing infrastructure, ask:

- Is this **generic** across projects? Commit it.
- Is this **project-specific** (data paths, one-off hacks, local credentials)? Keep it local.

## Generic (Commit)

- Folder conventions (`code/00_fetch`, `01_build`, `02_analyze`)
- Make orchestration patterns (host-run staged pipeline)
- Verification and quality-gate rules
- Session logging/templates

## Project-Specific (Do not generalize)

- One project's raw data idiosyncrasies
- Machine-specific paths and local workarounds
- Institutional formatting requirements

## Memory Policy

- `MEMORY.md` stores transferable learnings.
- Local machine-specific notes should stay outside commits unless intentionally promoted into the template.

## Maintenance Checklist

- Keep instructions consistent across `AGENTS.md`, `CLAUDE.md`, and `README.md`.
- Keep examples placeholder-based so the repo remains a template.
- When workflow philosophy changes, update rules and Make scaffolding together.

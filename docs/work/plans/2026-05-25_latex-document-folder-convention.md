# LaTeX Document Folder Convention

Status: IN_PROGRESS
Date: 2026-05-25

## Goal

Make every compilable article or slide deck live in its own folder, add Make targets that compile every root `.tex` document under `docs/deliverables/articles/` and `docs/deliverables/slides/`, and update agent/skill instructions to use the new layout.

## Target Convention

- Root article documents live at `docs/deliverables/articles/<name>/<name>.tex`.
- Root slide decks live at `docs/deliverables/slides/<name>/<name>.tex`.
- Supporting fragments, such as article section files, live inside the owning document folder and are not standalone compile roots.
- Make compiles root `.tex` files by detecting `\documentclass`, so section fragments are not compiled as documents.

## Tasks

- [x] Move the canonical paper to `docs/deliverables/articles/main/main.tex` and move sections under that folder.
- [x] Add root Makefile targets for all LaTeX, articles only, and slides only.
- [x] Update repo docs and instructions to the folder-per-document convention.
- [x] Update Claude/Codex skills and agents to the new paths and Make targets.
- [x] Verify Makefile syntax, root `.tex` detection, and article compilation.

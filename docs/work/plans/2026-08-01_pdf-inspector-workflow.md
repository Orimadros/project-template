# Plan: Replace MarkItDown with pdf-inspector

**Status:** COMPLETED — implemented and verified on 2026-08-01.

## Goal

Replace the template's MarkItDown-first PDF-reading workflow with Firecrawl
pdf-inspector, while preserving the rule that source PDFs are first converted to
searchable Markdown and that layout-sensitive content is inspected visually.

## Approach

1. Replace the Python dependency with `pdf-inspector` and regenerate `uv.lock`.
2. Add a project-local conversion wrapper that uses the package's `process_pdf`
   API, writes Markdown beside or at a requested output path, and reports
   classification/partial-extraction warnings.
3. Rewrite the shared PDF-processing rule around the wrapper and
   pdf-inspector's text-based/scanned/image-based/mixed routing.
4. Update both hook copies, both instruction files, mirrored skills, and the
   librarian agent instructions so every agent receives the same command.
5. Verify lockfile consistency, syntax, hook messages, conversion behavior on a
   text PDF, and that no live MarkItDown references remain (except historical
   plans).

## Files Expected to Change

- `pyproject.toml`, `uv.lock`
- `code/03_quality/pdf_to_markdown.py`
- `.claude/rules/pdf-processing.md`
- `.claude/hooks/pdf-read-guard.py`, `.codex/hooks/pdf-read-guard.py`
- `AGENTS.md`, `CLAUDE.md`
- `.claude/skills/{discover,lit-review,review-paper}/SKILL.md` and their
  byte-identical `.agents/skills/` counterparts
- `.claude/agents/librarian.md`, `.codex/agents/librarian.toml`

## Verification

- Run `uv lock --check` and execute the wrapper against a representative
  text-based PDF.
- Run the wrapper against an intentionally invalid/scanned classification path
  where practical, and confirm its diagnostics are useful.
- Feed source-PDF and non-source-PDF hook payloads to both hook copies.
- Check JSON/TOML/Python syntax and scan live template files for stale
  MarkItDown commands or dependencies.

## Verification Completed

- `uv lock --check` and `uv sync --frozen` completed with
  `pdf-inspector==0.2.6`.
- The wrapper produced Markdown from the repository's native-text fixture and
  exited `2` without output for an encoding-corrupted fixture that requires OCR.
- Both PDF guard copies reject a source PDF with the new command and allow a
  compiled PDF outside `docs/sources/`.
- Python, JSON, and TOML syntax checks passed; the Claude/Codex skill copies
  remain byte-identical and no live MarkItDown reference remains.

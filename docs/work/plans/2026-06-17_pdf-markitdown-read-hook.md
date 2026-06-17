# Plan: MarkItDown PDF Read Hook

## Goal

Add Claude and Codex hook guardrails so agents do not directly read source PDFs
under `docs/sources/` when a MarkItDown Markdown conversion should be used first.

## Steps

1. Add a reusable PDF read guard hook for Claude and Codex.
2. Wire the hook into each tool's `PreToolUse` configuration for `Read`.
3. Verify JSON/TOML syntax and hook behavior with representative hook payloads.
4. Commit and push the branch.

## Design

- Block direct `Read` calls only for PDFs under `docs/sources/`.
- Leave PDFs elsewhere alone, especially compiled deliverables and visual QA outputs.
- In the block message, tell the agent to run:
  `uv run markitdown "path/to/file.pdf" -o "path/to/file.md"`
- Preserve the exception: inspect the original PDF or page images when visual,
  layout, scan, equation, complex table, or pagination information is essential.

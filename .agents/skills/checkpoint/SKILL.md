---
name: checkpoint
description: Write a structured resumable state snapshot to docs/work/checkpoints/.
argument-hint: "[slug]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash"]
---

# Checkpoint

Use this before stopping, handing off, or after a major state change.

## Purpose

A checkpoint is a compact state snapshot for resuming work. It is not a narrative session log.

## Workflow

1. Determine a short slug from `$ARGUMENTS` or the active task.
2. Inspect current git status, active plans, recent reviews, and relevant files.
3. Write `docs/work/checkpoints/YYYY-MM-DD_slug.md`.

## Required Sections

- Current objective
- Current repo state
- Files changed or important files
- Decisions made
- Commands run and verification status
- Next actions
- Known blockers or risks

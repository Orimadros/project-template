---
name: sitrep
description: Report open issue progress, recently closed issues, and recent session logs.
disable-model-invocation: true
---

# Sitrep

When Leo invokes `/sitrep`, read all open GitHub issues and [the progress
rules](../../references/issue-progress.md). For each open issue with a spec,
inspect every component path and relevant diff or history. Report components
already shipped, pending approval, not yet written, or unclear. State the
reason for each unclear component. For an issue without a spec, report its
deliverable and say when completion cannot be checked from repository files.

Also name the titles of the three most recently closed GitHub issues. Read the
three newest dated files in `docs/work/session_logs/` and summarize what was
done, decided, or discovered. If GitHub or a log is unavailable, state which
part could not be checked. Do not create or update a progress file.

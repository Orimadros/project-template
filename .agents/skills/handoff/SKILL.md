---
name: handoff
description: Write a compact session handoff to the operating system's temporary directory and return its path.
argument-hint: What will the next session be used for?
disable-model-invocation: true
---

# Handoff

Write a concise, resumable account of the current task outside the repository, in the operating system's temporary directory. Use a unique Markdown filename and never overwrite an existing handoff. A short focus supplied by Leo determines what the next session should emphasize.

Inspect the current repository state and conversation. Include the objective, current state, important decisions, changed files, checks and results, blockers, and the next useful action. Add a **Suggested skills** section with the exact relevant skill names and file paths for the next agent to read. Mention only skills that fit the next action.

Point to existing issues, specs, ADRs, commits, diffs, and outputs by path or link instead of copying their contents. Keep factual handoff details separate from durable preferences. Remove secrets and sensitive personal information. Do not write a session log or repository file.

Create the file using the host's OS temporary-directory facility. Confirm the write succeeded and capture its exact absolute path. Immediately tell Leo that path in the response; do no further task work between writing the file and reporting it.

**Done:** a unique handoff exists outside the workspace, its saved contents are safe and actionable, and Leo has received its exact path immediately after the write.

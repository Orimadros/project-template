---
name: close-issue
description: Commit and push a completed issue's files, then close its GitHub issue.
disable-model-invocation: true
---

# Close issue

Use this only when Leo invokes `/close-issue` for a named GitHub issue. Read the
issue and [the progress rules](../../references/issue-progress.md).

1. If the issue has a spec, verify every component is in production, no
   candidate code or output remains, the applicable checks pass, and no state
   is unclear. Move the unchanged spec from the issue folder to
   `docs/work/specs/archive/issue-<number>-<slug>.md`. If the issue has no spec,
   check its stated deliverable and Leo's completion statement; do not claim
   off-repository work is done from an empty folder.
2. Inspect `git status` and `git diff`. Stage only files belonging to this
   issue, including the archived spec and any production run records. Leave
   unrelated work untouched. If files or paths overlap another open issue,
   return the conflict to Leo before committing.
3. Commit the staged issue files, push the current branch, and close the GitHub
   issue. A completed no-spec issue with no repository changes closes without
   an empty commit. Verify the push and issue state, then report the commit and
   issue URL. If the push or close fails, leave the issue open, report exactly
   which step completed, and retry from that state when Leo invokes this skill
   again. If the commit exists but the push failed, retry the push without an
   empty second commit; if only GitHub closure failed, verify the push and
   retry closure without committing again. An archived spec may therefore belong to an open issue; the progress
   rules cover that case. Write a factual session log at the end of substantial
   work.

An incomplete or unclear component leaves the issue open; report the exact
remaining work so Leo can choose what to do next.

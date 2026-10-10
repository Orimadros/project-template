---
name: open-issue
description: Create a concise GitHub issue for work Leo wants tracked.
disable-model-invocation: true
---

# Open an issue

Create one GitHub issue when Leo invokes this skill to track a task.

First determine whether the request is one coherent deliverable. Read the relevant repository context and search open issues for an existing issue covering the same work. Do not create a duplicate. A small exact edit or an exploratory session can proceed without an issue; create one only when Leo asks to track that work.

Write a short title and issue body that state the problem, the requested outcome, and concrete completion conditions grounded in Leo's request. Keep implementation choices out unless Leo has already made them. If the request contains unrelated deliverables or lacks a completion condition that materially affects scope, present the smallest set of proposed splits or questions and wait for Leo before creating anything.

An issue may be opened before Leo settles its research or implementation choices;
those choices belong to the later conversation and spec. Ask first only when the
open choice prevents a clear single deliverable or completion condition.

When the scope is atomic and clear, create the issue in the current repository with the available GitHub CLI or connector. Use only labels or milestones that already exist and clearly apply. Return the issue number, title, and link. Do not create a specification, start implementation, or commit repository changes.

For example, tracking a defined set of placebo checks can be one issue when the outcome and completion conditions are clear. A request to redesign the analysis, rebuild the data, and rewrite the paper may need a scope decision before an issue is opened.

**Done:** one issue exists for the agreed atomic task, or no issue was created because a duplicate, split, or unresolved scope needs Leo's decision.

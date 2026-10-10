---
name: grill-to-spec
description: Interview me about a difficult tracked change, teach relevant concepts, and write its specification after I settle the choices.
disable-model-invocation: true
---

# Interview for a change specification

Use this only when Leo explicitly asks for a thorough design interview before a tracked change. It leads an iterative conversation, then writes the same single issue-linked delta contract as `to-spec` after all consequential choices are settled.

**Input:** an existing GitHub issue and a difficult or technically demanding change.

Read the issue and relevant code, data definitions, project context, and prior decisions. Confirm there is no existing or archived spec for the issue. Map the choices that could change research meaning, identification, data construction, numerical accuracy, outputs, or acceptance. Include likely hidden choices and dependencies between choices. Separate required decisions from details that prewritten standards let an implementer choose without changing meaning.

Interview Leo one decision at a time, or in a small batch when choices are independent. For each consequential choice, state why it matters and what remains undecided. When Leo needs background, explain only the concept needed to choose, then give practical options, their tradeoffs, and a reasoned recommendation. The recommendation is advice; Leo makes every substantive choice. Wait for his answer before treating a choice as settled. Do not use a quiz or make understanding a condition for proceeding.

For example, a numerical dynamic model may require decisions about which integrals can be solved analytically, which need numerical integration, the quadrature rule, and how the state space and value function will be represented and solved. Explain each concept when it matters, show relevant options and tradeoffs, recommend an approach with reasons, and wait for Leo's choices.

Once all required choices are settled, read `.agents/skills/to-spec/SKILL.md` as a file and follow its issue checks, format, paths, and completion criteria. Do not depend on a Skill tool or automatic loading of that user-invoked skill. Write exactly one `pending-approval/issue-<number>-<slug>/spec.md`. If a required choice remains open, write no ready spec; report the remaining choice and wait. Create no separate plan, ADR, glossary, or interview document.

**Done:** Leo has settled the consequential choices and the issue has one complete spec, or the interview is paused with the unresolved decision made explicit and no ready spec written.

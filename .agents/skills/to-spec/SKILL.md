---
name: to-spec
description: Write an issue-linked change specification from decisions already settled in the conversation.
disable-model-invocation: true
---

# Write the change specification

Turn settled decisions into the issue's single delta contract. This skill records decisions; it does not interview, teach, recommend substantive choices, or convert an assumption into a requirement.

**Input:** an existing GitHub issue and the conversation in which Leo settled the change.

Read the issue, relevant repository files, and the conversation. Confirm that the issue exists, that it has no specification already, and that the required research and design choices are settled. Check both `pending-approval/issue-<number>-<slug>/spec.md` and `docs/work/specs/archive/issue-<number>-<slug>.md`; an existing contract means this issue cannot receive another. If the issue and conversation disagree, or a consequential choice remains open, describe the mismatch or gap and ask Leo. Do not write a ready-to-implement spec until it is resolved.

Create `pending-approval/issue-<number>-<slug>/spec.md`. Capture only the agreed change, with:

- the issue number and link, and the accepted repository base commit (`git rev-parse HEAD`);
- the problem and the specific change being requested;
- settled substantive choices and constraints, with source links or paths where needed;
- independently shippable component IDs, and for every changed file or output its candidate path (or `—` for a deletion), intended production path, action, and dependencies on other components;
- acceptance conditions and the relevant verification commands or observable results.

Keep it delta-based: describe what this issue changes and why, not a standing manual for how each script currently works. Use the issue's already agreed scope. Do not add an unapproved implementation requirement. The candidate and production paths must match the issue folder and the chosen production destinations; identify component dependencies so partial shipment can be checked. Record no open substantive choices in a ready spec.

For example, if the request allows either county-level or state-level estimates and the discussion never chose a level, write neither a default nor a ready spec. Report the unresolved geographic unit and ask Leo to settle it.

Write exactly one spec for the issue and leave it unchanged once implementation starts. Do not create an extra plan, ADR, glossary, or status file. Report the spec path and the decisions it records. If no spec was written, name the unresolved choice or conflict and the answer needed from Leo.

**Done:** one complete `spec.md` exists for the existing issue, or no file was written because the issue, uniqueness, or settled-decision condition failed.

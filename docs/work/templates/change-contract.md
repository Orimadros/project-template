# Issue #[number]: [change]

Issue: [GitHub issue URL]
Starting revision: [Git commit, including for add-only changes]

## Decisions

- [Leo's agreed research, data, model, and presentation choices. State units and observation levels where relevant.]

## Change

[Describe only what this issue changes and why. Keep current behavior in the affected source files, not here.]

## Components

Each ID is a subset Leo may ship on its own. Put files that must ship together under
one ID. Name every candidate file and its intended production path, including
generated outputs. Use one row per file. For a deletion, write `—` in the
candidate-path column and name the existing production file to remove. Each
generated output's `.run.tsv` record follows it to the matching production
path when the component ships; a deletion removes its adjacent record too.

| ID | Action | Role | Candidate path | Production path | Requires component |
|---|---|---|---|---|---|
| A | add/modify/delete | script/output/data | `pending-approval/issue-[number]-[slug]/...` or `—` for delete | `code/...` or `results/...` | none |

## Checks

- [Command and observable result required before review.]
- [What Leo should inspect in the candidate code and output.]

## Open decisions

None. A decision still needed from Leo means this contract is a draft and cannot
be handed to `implement`.

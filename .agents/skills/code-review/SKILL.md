---
name: code-review
description: Independently review candidate code against its specification and relevant standards without editing it.
disable-model-invocation: true
---

# Code review

Review without changing files. Delegate to the named `code-reviewer` agent in one fresh context in the active harness, separate from implementation reasoning. Give it the accepted repository, candidate, user-directed follow-ups, relevant coding preferences and helpers, and the universal `unslop` standard for its report. Read the preference and helper files and pass their needed content directly; do not depend on a Skill tool or automatic loading of explicit-only skills.

**Input:** an issue candidate with its spec, or a direct edit and Leo's exact request.

For a candidate, verify that `pending-approval/issue-<number>-<slug>/spec.md` is the issue's sole contract and that its accepted base commit is available. Compare the candidate against that fixed base and the production files named by the spec. Also inspect current accepted files and relevant inputs for changes since the base or candidate run. Report conflicts or uncertainty; file existence or matching timestamps alone do not prove that a change is accepted or that input contents are unchanged.

Inspect every candidate component and its recorded checks. Read the relevant language coding preference, shared helper interface, and only the additional references needed for the changed files. Check that direct local inputs are registered, candidate outputs stay in the issue folder, downstream candidate steps use candidate-built data where specified, and the run record reports what was registered without claiming automatic discovery. Consider both code and generated outputs.

For a deletion row, compare the named production file with the spec's starting revision. Review the effect on dependent code, paper, and outputs. Record its current SHA-256 digest and the digest of any adjacent run record slated for removal. If the file is already absent, report the conflict instead of approving a pending deletion. A deletion has no candidate file; list it by component ID and production path in the review report.

Return two separate finding groups:

1. **Specification adherence:** whether each component, path, dependency, acceptance condition, and requested follow-up matches the contract.
2. **Standards and research correctness:** correctness, reproducibility, data/input handling, code quality, and domain or research-logic issues within the review scope.

For each finding, give severity, file and line or output, evidence, and a concrete correction. Put blocking findings first. Distinguish a confirmed defect from a question Leo must answer. Do not make a substantive research choice or silently widen review scope. If no findings exist, say so and state the checks and outputs actually inspected. Do not assign a universal score or edit the candidate.

Save candidate findings to `pending-approval/issue-<number>-<slug>/review.md`. Include reviewed component IDs; each candidate file, generated output, and run record with its observed modification time and SHA-256 digest; checks and results; and findings. Calculate these digests at review time, outside the input-registration helper. This lets shipping verify it is moving the bytes actually reviewed. For a direct edit, save the report under `docs/work/reviews/` with a dated, descriptive filename and review it against Leo's exact request. Return the report path and any choices that need Leo.

For example, a review of a post-ship label edit checks the changed line against Leo's exact request and applicable code standards; it does not require inventing a spec or opening an issue.

**Done:** the comparison has been made against the fixed accepted base and applicable standards, both finding groups are reported, and the review record identifies exactly what was reviewed.

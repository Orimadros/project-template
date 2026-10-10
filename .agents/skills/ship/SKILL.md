---
name: ship
description: Move the approved subset of an issue's reviewed candidate into production.
disable-model-invocation: true
---

# Ship

Leo's invocation must identify the issue and the subset of pending component
IDs or files to ship. Read the issue, `pending-approval/issue-<number>-<slug>/spec.md`,
its review report, and [the progress rules](../../references/issue-progress.md).
If the subset is unclear or omitted, list the pending choices and ask Leo to name
one; do not infer that he meant everything.

1. Match the requested files to whole component IDs in the spec. Check that all
   required components are already shipped or included in this request. Confirm
   no still-pending script depends on a candidate path that this shipment would
   remove. If one does, explain the dependency and ask Leo whether to ship the
   linked components together or defer this shipment. Do not strand a pending
   script or silently change its inputs.
   Confirm
   the review covers these candidate files and their latest changes. Recompute
   the SHA-256 digest of each requested candidate file, generated output, and
   run record; compare each one with the review before moving anything. Confirm
   the spec's checks passed, registered direct inputs still have the same observed
   modification times as at the candidate run, and the production paths have no
   conflicting or unrelated work. Stop and report the exact gap if any check
   cannot be resolved. Leo decides any substantive conflict.
2. For the named components only, move reviewed candidate files to their
   production paths. Move each generated output's adjacent `.run.tsv` sidecar
   with it. Append `production_output<TAB>[production path]` to that record,
   preserving its original `output`, `script`, and `input` entries. Use the
   record's existing path escaping when writing the added field. For a deletion
   row, verify the named production file and adjacent run record still match
   their reviewed digests against the spec's starting revision, then remove the file and any adjacent
   run record named by the spec. Keep a backup until checks pass.
3. Change fixed paths in shipped scripts from the candidate locations to the
   corresponding production paths in the spec, including inputs made by other
   components. Compare the script with its reviewed candidate: only these path
   substitutions may differ. Keep a copy or diff long enough to make that
   comparison. Back up any production file that this component intentionally
   replaces before moving the candidate. Run safe syntax and relevant checks
   without regenerating the reviewed output. If a move or check fails, restore
   the candidate and production files to their prior locations before
   reporting the failure.
4. Re-read the spec's components and current files using the progress rules.
   Report what was shipped, what remains pending approval, what is unwritten,
   and what is unclear. Suggest `/close-issue` only when every component is
   verifiably shipped. Write a factual session log at the end of substantial
   work under `docs/work/session_logs/YYYY-MM-DD_<topic>.md`.

Shipping does not commit, push, or close the issue. A later substantive change
needs a new issue and delta spec; a small explicit edit can use `/implement`
directly in the working copy.

# Read an issue's progress from files

Open the GitHub issue and its `pending-approval/issue-<number>-<slug>/spec.md`.
If closure was interrupted after the spec was archived, read
`docs/work/specs/archive/issue-<number>-<slug>.md` instead and report that
the GitHub issue is still open.
The spec's component IDs are the units Leo can ship. Each file row gives an
action, candidate path, and production path. Check every row of a component.

For an added file, the candidate path alone means pending approval; the
production path alone means shipped only when the file can be tied to this
issue. Neither path means unwritten. Both paths mean the transfer needs
inspection. For a modified or deleted file, production-path existence alone
proves nothing: compare its diff with the spec's starting revision and the
reviewed candidate. For a deletion, the production file and no deletion review
means unwritten; a reviewed deletion while the file remains means pending
approval; absence means shipped only when the diff or history ties the removal
to this issue. Use Git history after a commit. If the evidence cannot
settle the state, report `unclear` with the specific reason. Do not keep a
separate status file or checklist.

Before shipping, check the review report in the candidate folder, its covered
component IDs, reviewed file digests and modification times, the spec's checks, current
production files, and the input modification times recorded beside generated
outputs. A changed candidate needs another review; a changed input needs a
fresh run and review or Leo's explicit decision about the stale output.
Matching input times do not prove unchanged contents. A production path
claimed by another open issue needs Leo's decision before either issue ships.

For an issue with no spec, inspect its stated deliverable and available files.
Off-repository completion cannot be inferred from the workspace; ask Leo when
closure depends on it.

# Fixed paths and light input records

**Status:** Accepted 2026-10-05. Supersedes the run-time output-path decision in ADR 0003 and extends ADR 0004.

Scripts name their input and output paths in their source. A candidate writes
inside its issue's `pending-approval/` folder. When Leo ships a component, the
agent moves the exact output he reviewed to the production path named in the
spec, then changes only the candidate paths in the script to the corresponding
production paths. It checks that path rewrite and keeps the original run record.

The shared input helper can register one file, or expand one fixed pattern or
directory into individual files. It records each direct file's path and local
modification time from filesystem metadata. It does not read or hash those files
to make the record. A successful run writes a small record beside its output.
Moving the output preserves the candidate-run facts and adds the new production
location. Later runs write new records.

Code review records a SHA-256 digest for each candidate file and output. Before
shipping, the agent checks those digests so the moved bytes match what was
reviewed. This reads candidate outputs during review and shipping; the input
helper still reads only filesystem metadata for data inputs.

This gives Leo the reviewed output and a practical way to find its direct inputs
without maintaining a historical asset graph. The record covers registered
inputs only. A matching modification time does not prove unchanged contents.

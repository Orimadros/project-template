# Review code and outputs together before acceptance

**Status:** Superseded in part by [ADR 0005](0005-fixed-paths-and-run-records.md).

Each proposed change has a folder under `pending-approval/` containing its spec,
candidate scripts, generated outputs, and verification results. Leo reviews these
together before the change enters the accepted project. Existing inputs are read
from approved canonical datasets; datasets newly built by the candidate stay in
its folder and are used by subsequent candidate scripts.

The original decision used run-time output destinations. Leo later chose fixed
paths in script source and a narrow path rewrite during shipping. ADR 0005 records
that change. The spec is archived unchanged after acceptance, as in ADR 0002.

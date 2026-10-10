# Register input files through shared helpers

**Status:** Extended by [ADR 0005](0005-fixed-paths-and-run-records.md).

Project scripts use a shared `input_file()` helper when reading data and
configuration files. The helper records the file path and its filesystem
last-modified time before returning the path to the ordinary reader. Provide
matching modules for R, Python, and Julia, and include their use in the coding
preferences supplied to implementers and code reviewers.

This replaces universal manually maintained file identities and lineage with
small generated run records and code review. Coverage depends on scripts
registering their direct inputs. ADR 0005 adds one call for a fixed file pattern
or directory containing many files. The helper does not discover arbitrary
internal reads or preserve historical data.

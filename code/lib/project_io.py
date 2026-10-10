"""Small, explicit input registration and per-output run records.

Usage::

    from project_io import RunRecord

    INPUTS = "data/raw/*.csv"       # declared here, not passed on the CLI
    OUTPUT = "results/panel.csv"

    with RunRecord(script=__file__, outputs=[OUTPUT]) as run:
        input_paths = run.input_file(INPUTS)  # always returns list[str]
        # Read input_paths with the project's ordinary readers, then write OUTPUT.

An input declaration may name one existing file, a directory, or a glob over
filenames in one explicitly named directory. A directory or glob expands to
sorted, immediate regular-file paths; it never walks subdirectories. Only
``*`` and ``?`` are supported in the filename pattern. Each resolved input's
filesystem modification time is captured with ``stat`` before this method
returns. The helper does not open, read, or hash input contents.

For every declared output, the context manager writes an adjacent
``<output>.run.tsv`` record. Records share the ``project-io-run-v1`` TSV format
across Python, R, and Julia. Starting a run first removes any old success
markers and writes ``status\trunning``. Normal exit writes ``success``;
exceptions write ``failed`` and are re-raised. A hard interruption can leave
``running``, which is deliberately not a success marker.

Declared outputs must be regular files. Before writing ``success``, the helper
checks that each output exists and its modification time is at least the run's
start time; directory outputs are unsupported.

Rows have the fields ``format``, ``status``, ``script``, ``started_at``, and
``completed_at``, followed by zero or more ``input<TAB>path<TAB>mtime`` rows,
one ``output<TAB>path`` row per declared output, and an optional ``error`` row.
Path and error values escape percent, tab, LF, and CR as ``%25``, ``%09``,
``%0A``, and ``%0D``. Shipping may append a ``production_output<TAB>path``
row while preserving the original run facts.

Relative paths are resolved from the process working directory. Paths inside
the repository are recorded relative to its root; external paths stay
absolute. Input rows store modification times as Unix seconds using the full
observed floating-point precision. Registered paths are evidence of the
explicit declarations made through this helper, not automatic discovery of
every file a script may read.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re
import stat as stat_module
import time
from typing import Iterable


_FORMAT = "project-io-run-v1"
_WILDCARD = re.compile(r"[*?]")
_REPO_ROOT = Path(__file__).resolve().parents[2]


def _absolute(path: str | Path) -> Path:
    return Path(path).expanduser().absolute()


def _record_path(path: str | Path) -> str:
    resolved = _absolute(path)
    try:
        return resolved.relative_to(_REPO_ROOT).as_posix()
    except ValueError:
        return str(resolved)


def _encode(value: str) -> str:
    """Escape TSV delimiters while preserving ordinary UTF-8 text."""
    return value.replace("%", "%25").replace("\t", "%09").replace("\n", "%0A").replace("\r", "%0D")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _filename_matches(pattern: str, filename: str) -> bool:
    expression = "^" + re.escape(pattern).replace(r"\*", ".*").replace(r"\?", ".") + "$"
    return re.match(expression, filename) is not None


def _expand_input(declaration: str | Path) -> list[Path]:
    """Expand one file, direct directory, or basename glob without recursion."""
    declared = _absolute(declaration)
    if declared.is_file():
        return [declared]
    if declared.is_dir():
        matches = sorted((entry.absolute() for entry in declared.iterdir() if entry.is_file()), key=str)
    else:
        parent = declared.parent
        filename_pattern = declared.name
        if not _WILDCARD.search(filename_pattern):
            raise FileNotFoundError(f"input file does not exist: {declared}")
        if _WILDCARD.search(str(parent)):
            raise ValueError("glob wildcards are allowed only in the filename; declare its directory explicitly")
        if not parent.is_dir():
            raise FileNotFoundError(f"input directory does not exist: {parent}")
        matches = sorted(
            (entry.absolute() for entry in parent.iterdir() if entry.is_file() and _filename_matches(filename_pattern, entry.name)),
            key=str,
        )

    if not matches:
        raise FileNotFoundError(f"input declaration matched no files: {declared}")
    return matches


@dataclass(frozen=True)
class _Input:
    path: str
    mtime: float


class RunRecord:
    """Register direct file inputs and record one script run beside each output."""

    def __init__(self, *, script: str | Path, outputs: Iterable[str | Path]):
        self.script = _record_path(script)
        self.output_paths = list(dict.fromkeys(str(_absolute(output)) for output in outputs))
        self.outputs = [_record_path(output) for output in self.output_paths]
        if not self.outputs:
            raise ValueError("RunRecord requires at least one declared output")
        self.inputs: list[_Input] = []
        self._input_paths: set[str] = set()
        self.started_at = _utc_now()
        self.started_epoch = 0.0
        self._entered = False

    def __enter__(self) -> "RunRecord":
        if self._entered:
            raise RuntimeError("a RunRecord cannot be entered more than once")
        self._entered = True
        self.started_at = _utc_now()
        self.started_epoch = time.time()
        # Remove old success records first, so even an interruption while
        # writing the new running records cannot leave an old run looking new.
        for output in self.output_paths:
            sidecar = Path(output + ".run.tsv")
            sidecar.parent.mkdir(parents=True, exist_ok=True)
            sidecar.unlink(missing_ok=True)
        self._write("running")
        return self

    def __exit__(self, exc_type, exc, traceback) -> bool:
        if exc_type is None:
            try:
                self._validate_outputs()
            except Exception as error:
                self._write("failed", completed_at=_utc_now(), error=str(error))
                raise
            self._write("success", completed_at=_utc_now())
        else:
            self._write("failed", completed_at=_utc_now(), error=str(exc))
        return False

    def _validate_outputs(self) -> None:
        for output in self.output_paths:
            path = Path(output)
            try:
                metadata = path.stat()
            except FileNotFoundError as error:
                raise RuntimeError(
                    f"declared output was not written or updated during this run: {output}"
                ) from error
            if not stat_module.S_ISREG(metadata.st_mode) or metadata.st_mtime < self.started_epoch:
                raise RuntimeError(
                    f"declared output was not written or updated during this run: {output}"
                )

    def input_file(self, declaration: str | Path) -> list[str]:
        """Register a file, immediate directory, or filename glob and return paths.

        The list contains absolute individual file paths in sorted order. The
        filesystem metadata read occurs here, before the caller's data reader.
        """
        if not self._entered:
            raise RuntimeError("input_file() must be called inside the RunRecord context")
        matches = _expand_input(declaration)
        paths: list[str] = []
        for path in matches:
            observed = _Input(_record_path(path), path.stat().st_mtime)
            paths.append(str(path))
            if observed.path not in self._input_paths:
                self.inputs.append(observed)
                self._input_paths.add(observed.path)
        # Keep the running record current if the process is interrupted later.
        self._write("running")
        return paths

    def _record_text(self, status: str, *, completed_at: str = "", error: str = "") -> str:
        rows = [
            ("format", _FORMAT),
            ("status", status),
            ("script", _encode(self.script)),
            ("started_at", self.started_at),
            ("completed_at", completed_at),
        ]
        rows.extend(("input", _encode(item.path), repr(item.mtime)) for item in self.inputs)
        rows.extend(("output", _encode(output)) for output in self.outputs)
        if error:
            rows.append(("error", _encode(error)))
        return "".join("\t".join(row) + "\n" for row in rows)

    def _write(self, status: str, *, completed_at: str = "", error: str = "") -> None:
        content = self._record_text(status, completed_at=completed_at, error=error)
        for output in self.output_paths:
            sidecar = Path(output + ".run.tsv")
            temporary = sidecar.with_name(sidecar.name + ".tmp")
            temporary.write_text(content, encoding="utf-8", newline="")
            temporary.replace(sidecar)


__all__ = ["RunRecord"]

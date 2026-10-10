"""Focused behavior tests for shared, metadata-only input registration."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
LIBRARY_DIR = REPOSITORY_ROOT / "code" / "lib"
if str(LIBRARY_DIR) not in sys.path:
    sys.path.insert(0, str(LIBRARY_DIR))

from project_io import RunRecord


def parse_record(path: Path) -> dict[str, list[list[str]]]:
    result: dict[str, list[list[str]]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        fields = line.split("\t")
        result.setdefault(fields[0], []).append(fields[1:])
    return result


def r_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


class ProjectIOTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.inputs = self.root / "inputs"
        self.inputs.mkdir()
        (self.inputs / "b.csv").write_text("b\n", encoding="utf-8")
        (self.inputs / "a.csv").write_text("a\n", encoding="utf-8")
        nested = self.inputs / "nested"
        nested.mkdir()
        (nested / "hidden.csv").write_text("nested\n", encoding="utf-8")
        self.output = self.root / "outputs" / "result.csv"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_file_directory_and_glob_register_direct_paths_with_mtimes(self) -> None:
        expected = sorted([str((self.inputs / "a.csv").absolute()), str((self.inputs / "b.csv").absolute())])
        original_open = Path.open
        input_files = {Path(path) for path in expected}

        def deny_input_open(path: Path, *args, **kwargs):
            if path.absolute() in input_files:
                raise AssertionError(f"input contents were opened: {path}")
            return original_open(path, *args, **kwargs)

        with patch.object(Path, "open", deny_input_open):
            with RunRecord(script=__file__, outputs=[self.output]) as run:
                self.assertEqual(run.input_file(self.inputs), expected)
                self.assertEqual(run.input_file(self.inputs / "*.csv"), expected)
                self.assertEqual(run.input_file(self.inputs / "a.csv"), [expected[0]])
                run.input_file(LIBRARY_DIR / "project_io.py")
                self.output.write_text("result\n", encoding="utf-8")

        record = parse_record(Path(str(self.output) + ".run.tsv"))
        self.assertEqual(record["format"], [["project-io-run-v1"]])
        self.assertEqual(record["status"], [["success"]])
        self.assertEqual(record["script"], [["code/03_quality/tests/test_project_io.py"]])
        self.assertEqual(len(record["input"]), 3)
        self.assertEqual(
            {row[0] for row in record["input"]},
            set(expected) | {"code/lib/project_io.py"},
        )
        for path_text, mtime_text in record["input"]:
            input_path = Path(path_text)
            if not input_path.is_absolute():
                input_path = REPOSITORY_ROOT / input_path
            self.assertEqual(float(mtime_text), input_path.stat().st_mtime)
        self.assertEqual(record["output"], [[str(self.output.absolute())]])

    def test_failed_run_replaces_old_success_marker(self) -> None:
        sidecar = Path(str(self.output) + ".run.tsv")
        with RunRecord(script=__file__, outputs=[self.output]):
            self.output.write_text("first\n", encoding="utf-8")
        self.assertEqual(parse_record(sidecar)["status"], [["success"]])

        with self.assertRaisesRegex(RuntimeError, "deliberate failure"):
            with RunRecord(script=__file__, outputs=[self.output]) as run:
                run.input_file(self.inputs / "a.csv")
                raise RuntimeError("deliberate failure")

        record = parse_record(sidecar)
        self.assertEqual(record["status"], [["failed"]])
        self.assertEqual(record["error"], [["deliberate failure"]])
        self.assertNotEqual(record["started_at"], [])

    def test_missing_input_and_directory_component_glob_are_rejected(self) -> None:
        with RunRecord(script=__file__, outputs=[self.output]) as run:
            with self.assertRaises(FileNotFoundError):
                run.input_file(self.inputs / "absent.csv")
            with self.assertRaises(ValueError):
                run.input_file(self.root / "*" / "*.csv")
            self.output.parent.mkdir(parents=True, exist_ok=True)
            self.output.write_text("created after validation errors\n", encoding="utf-8")

    def test_missing_or_stale_output_cannot_be_recorded_as_success(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "not written or updated"):
            with RunRecord(script=__file__, outputs=[self.output]):
                pass
        record = parse_record(Path(str(self.output) + ".run.tsv"))
        self.assertEqual(record["status"], [["failed"]])

        self.output.write_text("stale\n", encoding="utf-8")
        old_time = time.time() - 10
        os.utime(self.output, (old_time, old_time))
        with self.assertRaisesRegex(RuntimeError, "not written or updated"):
            with RunRecord(script=__file__, outputs=[self.output]):
                pass
        record = parse_record(Path(str(self.output) + ".run.tsv"))
        self.assertEqual(record["status"], [["failed"]])

    @unittest.skipUnless(shutil.which("Rscript"), "Rscript is unavailable")
    def test_r_success_and_failure_records_match_shared_format(self) -> None:
        self._run_language_example("Rscript", ".R", self._r_program)

    @unittest.skipUnless(shutil.which("julia"), "Julia is unavailable")
    def test_julia_success_and_failure_records_match_shared_format(self) -> None:
        self._run_language_example("julia", ".jl", self._julia_program)

    def _run_language_example(self, executable: str, suffix: str, program_builder) -> None:
        script = self.root / ("example" + suffix)
        good_output = self.root / "outputs" / ("good" + suffix + ".txt")
        failed_output = self.root / "outputs" / ("failed" + suffix + ".txt")
        stale_output = self.root / "outputs" / ("stale" + suffix + ".txt")
        stale_output.parent.mkdir(parents=True, exist_ok=True)
        stale_output.write_text("previous run\n", encoding="utf-8")
        old_time = time.time() - 10
        os.utime(stale_output, (old_time, old_time))
        script.write_text(
            program_builder(script, good_output, failed_output, stale_output), encoding="utf-8"
        )
        completed = subprocess.run(
            [executable, str(script)], capture_output=True, text=True, check=False, timeout=60
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

        good_record = parse_record(Path(str(good_output) + ".run.tsv"))
        self.assertEqual(good_record["format"], [["project-io-run-v1"]])
        self.assertEqual(good_record["status"], [["success"]])
        self.assertEqual(good_record["script"], [[str(script.absolute())]])
        self.assertEqual(good_record["output"], [[str(good_output.absolute())]])
        registered = {row[0]: row[1] for row in good_record["input"]}
        expected_inputs = {
            str((self.inputs / "a.csv").absolute()),
            str((self.inputs / "b.csv").absolute()),
            f"code/lib/project_io{suffix}",
        }
        self.assertEqual(set(registered), expected_inputs)
        for path_text, mtime_text in good_record["input"]:
            input_path = Path(path_text)
            if not input_path.is_absolute():
                input_path = REPOSITORY_ROOT / input_path
            self.assertEqual(float(mtime_text), input_path.stat().st_mtime)

        failed_record = parse_record(Path(str(failed_output) + ".run.tsv"))
        self.assertEqual(failed_record["status"], [["failed"]])
        self.assertIn("deliberate failure", failed_record["error"][0][0])

        stale_record = parse_record(Path(str(stale_output) + ".run.tsv"))
        self.assertEqual(stale_record["status"], [["failed"]])
        self.assertIn("not written or updated", stale_record["error"][0][0])

    def _r_program(
        self, script: Path, good_output: Path, failed_output: Path, stale_output: Path
    ) -> str:
        module = LIBRARY_DIR / "project_io.R"
        return f"""source({r_string(str(module))})
with_run_record(script = {r_string(str(script))}, outputs = {r_string(str(good_output))},
                code = function(run) {{
  paths <- run$input_file({r_string(str(self.inputs))})
  module_paths <- run$input_file({r_string(str(module))})
  stopifnot(length(paths) == 2L, length(module_paths) == 1L)
  writeLines("ok", {r_string(str(good_output))})
}})
tryCatch(
  with_run_record(script = {r_string(str(script))}, outputs = {r_string(str(failed_output))},
                  code = function(run) stop("deliberate failure")),
  error = function(error) invisible(NULL)
)
tryCatch(
  with_run_record(script = {r_string(str(script))}, outputs = {r_string(str(stale_output))},
                  code = function(run) invisible(NULL)),
  error = function(error) invisible(NULL)
)
"""

    def _julia_program(
        self, script: Path, good_output: Path, failed_output: Path, stale_output: Path
    ) -> str:
        module = LIBRARY_DIR / "project_io.jl"
        return f"""include({r_string(str(module))})
using .ProjectIO
run_record({r_string(str(script))}, [{r_string(str(good_output))}]) do run
    paths = input_file(run, {r_string(str(self.inputs))})
    module_paths = input_file(run, {r_string(str(module))})
    @assert length(paths) == 2 && length(module_paths) == 1
    write({r_string(str(good_output))}, "ok")
end
try
    run_record({r_string(str(script))}, [{r_string(str(failed_output))}]) do run
        error("deliberate failure")
    end
catch
end
try
    run_record({r_string(str(script))}, [{r_string(str(stale_output))}]) do run
        nothing
    end
catch
end
"""


if __name__ == "__main__":
    unittest.main()

"""The raw-data hook allows new files and blocks direct changes to existing ones."""

import importlib.util
import tempfile
import unittest
from pathlib import Path


HOOK = Path(__file__).resolve().parents[3] / ".agents/hooks/guard_raw_data.py"
SPEC = importlib.util.spec_from_file_location("guard_raw_data", HOOK)
assert SPEC and SPEC.loader
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)


class RawGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        raw = self.root / "data/raw"
        raw.mkdir(parents=True)
        (raw / "existing.csv").write_text("a,b\n1,2\n")

    def check(self, tool, data):
        return guard.check({"tool_name": tool, "tool_input": data, "cwd": str(self.root)}, self.root)

    def test_file_tool_allows_new_file_and_blocks_existing(self):
        self.assertIsNone(self.check("Write", {"file_path": "data/raw/new.csv"}))
        self.assertIsNotNone(self.check("Write", {"file_path": "data/raw/existing.csv"}))
        self.assertIsNotNone(self.check("apply_patch", {"command": "*** Update File: data/raw/existing.csv"}))

    def test_shell_reads_and_new_downloads_are_allowed(self):
        self.assertIsNone(self.check("Bash", {"command": "cat data/raw/existing.csv"}))
        self.assertIsNone(self.check("Bash", {"command": "curl -o data/raw/new.csv https://example.org/data"}))

    def test_shell_mutations_are_blocked(self):
        for command in (
            "rm data/raw/existing.csv",
            "chmod a-w data/raw/existing.csv",
            "cp other.csv data/raw/existing.csv",
            "rm -rf data/raw/*",
            "find data/raw -type f -delete",
        ):
            with self.subTest(command=command):
                self.assertIsNotNone(self.check("Bash", {"command": command}))


if __name__ == "__main__":
    unittest.main()

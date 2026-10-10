"""Citation checks catch missing keys across paper and slides."""

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "check_bibliography.py"
SPEC = importlib.util.spec_from_file_location("check_bibliography", SCRIPT)
assert SPEC and SPEC.loader
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class BibliographyTests(unittest.TestCase):
    def test_reports_missing_and_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bib = root / "docs/sources/references.bib"
            bib.parent.mkdir(parents=True)
            bib.write_text("@article{known, title={A}}\n@book{known, title={B}}\n")
            paper = root / "docs/deliverables/articles/main/main.tex"
            paper.parent.mkdir(parents=True)
            paper.write_text(r"\citep{known,missing} % \citep{commented}")
            problems = checker.check(root)
            self.assertTrue(any("duplicate BibTeX key: known" in item for item in problems))
            self.assertTrue(any("missing BibTeX key missing" in item for item in problems))
            self.assertFalse(any("commented" in item for item in problems))


if __name__ == "__main__":
    unittest.main()

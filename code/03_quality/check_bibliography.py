#!/usr/bin/env python3
"""Check that citations in article, appendix, and slide sources exist in the BibTeX file."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


CITATION = re.compile(r"\\(?:cite\w*|autocite|parencite|textcite|nocite)\s*(?:\[[^]]*\]\s*){0,2}\{([^}]*)\}")
ENTRY = re.compile(r"@\s*(?!comment\b|string\b|preamble\b)\w+\s*\{\s*([^,\s]+)\s*,", re.IGNORECASE)


def citations(source: str) -> set[str]:
    visible = re.sub(r"(?<!\\)%.*$", "", source, flags=re.MULTILINE)
    return {
        key.strip()
        for group in CITATION.findall(visible)
        for key in group.split(",")
        if key.strip() and key.strip() != "*"
    }


def check(root: Path) -> list[str]:
    bibliography = root / "docs/sources/references.bib"
    if not bibliography.is_file():
        return [f"missing {bibliography.relative_to(root)}"]
    keys = ENTRY.findall(bibliography.read_text(encoding="utf-8"))
    problems = [f"duplicate BibTeX key: {key}" for key in sorted(set(keys)) if keys.count(key) > 1]
    known = set(keys)
    for area in ("articles", "appendices", "slides"):
        for tex in sorted((root / "docs/deliverables" / area).rglob("*.tex")):
            for key in sorted(citations(tex.read_text(encoding="utf-8")) - known):
                problems.append(f"{tex.relative_to(root)}: missing BibTeX key {key}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    problems = check(args.root.resolve())
    if problems:
        for problem in problems:
            print(f"[ERROR] {problem}")
        return 1
    print("Bibliography keys: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

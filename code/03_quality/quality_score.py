#!/usr/bin/env python3
"""
Minimal quality scorer for paper-centric empirical project templates.

Usage:
  python3 code/03_quality/quality_score.py docs/deliverables/articles/main.tex
  python3 code/03_quality/quality_score.py docs/deliverables/slides/talk.tex
  python3 code/03_quality/quality_score.py code/01_build/00_clean_data.R
  python3 code/03_quality/quality_score.py code/02_analyze/model.py --summary
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class Finding:
    severity: str  # critical | major | minor
    message: str


@dataclass
class ScoreReport:
    path: Path
    score: int
    findings: List[Finding]


# Fast heuristic scorer. The authoritative weighted rubric lives in
# .claude/rules/quality-gates.md; these flat penalties catch obvious blockers.
PENALTIES = {
    "critical": 40,
    "major": 10,
    "minor": 3,
}


def run_cmd(cmd: List[str]) -> tuple[int, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, (proc.stdout + "\n" + proc.stderr).strip()


def score_tex(path: Path, text: str) -> List[Finding]:
    findings: List[Finding] = []

    is_slide = "docs/deliverables/slides" in path.as_posix()
    is_article = "docs/deliverables/articles" in path.as_posix()

    if is_slide and "\\pause" in text:
        findings.append(Finding("major", "Uses \\pause in a Beamer talk; use separate frames or visual emphasis."))

    if text.count("{") != text.count("}"):
        findings.append(Finding("critical", "Unbalanced braces detected."))

    has_citations = len(re.findall(r"\\cite\w*\{[^}]*\}", text)) > 0
    has_bibliography = bool(re.search(r"\\(bibliography|addbibresource)\b|\\begin\{thebibliography\}", text))
    if has_citations and not has_bibliography:
        findings.append(Finding("minor", "Citations present but no bibliography command found in this file."))

    if is_article:
        if "\\begin{abstract}" not in text:
            findings.append(Finding("major", "Paper main file should include an abstract."))
        if "\\bibliography{references}" not in text and "\\addbibresource" not in text:
            findings.append(Finding("major", "Paper should use docs/sources/references.bib as the canonical bibliography."))
        if "sections/" not in text:
            findings.append(Finding("minor", "Paper is not split into section files under docs/deliverables/articles/sections/."))

    if re.search(r"(?i)\b(obviously|clearly|prove that|causal effect)\b", text) and "identif" not in text.lower():
        findings.append(Finding("minor", "Potentially strong claim; ensure identification support is explicit."))

    return findings


def score_r(path: Path, text: str) -> List[Finding]:
    findings: List[Finding] = []

    rc, out = run_cmd(["Rscript", "-e", f"parse(file='{path.as_posix()}')"])
    if rc != 0:
        findings.append(Finding("critical", f"R parse failed: {out.splitlines()[-1] if out else 'unknown error'}"))

    rng_calls = ("runif(", "rnorm(", "sample(", "rbinom(", "rpois(", "rbeta(", "rgamma(")
    if "set.seed(" not in text and any(call in text for call in rng_calls):
        findings.append(Finding("major", "Potential stochastic code without set.seed()."))

    if re.search(r"['\"]/Users/|['\"]/home/", text):
        findings.append(Finding("critical", "Hardcoded absolute path detected."))

    if "results/" not in text and path.as_posix().startswith("code/02_analyze"):
        findings.append(Finding("minor", "Analysis script does not appear to write or reference results/."))

    return findings


def score_python(path: Path, text: str) -> List[Finding]:
    findings: List[Finding] = []

    rc, out = run_cmd([sys.executable, "-m", "py_compile", str(path)])
    if rc != 0:
        findings.append(Finding("critical", f"Python compile failed: {out.splitlines()[-1] if out else 'unknown error'}"))

    if re.search(r"['\"]/Users/|['\"]/home/", text):
        findings.append(Finding("critical", "Hardcoded absolute path detected."))

    return findings


def score_shell(path: Path, text: str) -> List[Finding]:
    findings: List[Finding] = []

    rc, out = run_cmd(["bash", "-n", str(path)])
    if rc != 0:
        findings.append(Finding("critical", f"Shell syntax check failed: {out.splitlines()[-1] if out else 'unknown error'}"))

    return findings


def build_report(path: Path) -> ScoreReport:
    text = path.read_text(encoding="utf-8", errors="replace")
    findings: List[Finding] = []

    suffix = path.suffix.lower()
    if suffix == ".tex":
        findings.extend(score_tex(path, text))
    elif suffix == ".r":
        findings.extend(score_r(path, text))
    elif suffix == ".py":
        findings.extend(score_python(path, text))
    elif suffix == ".sh":
        findings.extend(score_shell(path, text))
    else:
        findings.append(Finding("minor", f"No scorer configured for {suffix}; score is informational."))

    score = 100
    for finding in findings:
        score -= PENALTIES.get(finding.severity, 0)

    return ScoreReport(path=path, score=max(score, 0), findings=findings)


def print_report(report: ScoreReport, summary: bool) -> None:
    if summary:
        print(f"{report.path}: {report.score}/100")
        return

    print(f"File: {report.path}")
    print(f"Score: {report.score}/100")

    if not report.findings:
        print("Findings: none")
        return

    print("Findings:")
    for finding in report.findings:
        print(f"- [{finding.severity.upper()}] {finding.message}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Quality scorer for paper-centric empirical project files.")
    parser.add_argument("path", type=Path, help="File path to score")
    parser.add_argument("--summary", action="store_true", help="Print one-line summary")
    args = parser.parse_args()

    if not args.path.exists():
        print(f"Error: file not found: {args.path}", file=sys.stderr)
        return 1

    report = build_report(args.path)
    print_report(report, args.summary)

    # Mirror quality gate semantics: non-zero exit for score below commit threshold.
    return 0 if report.score >= 80 else 2


if __name__ == "__main__":
    raise SystemExit(main())

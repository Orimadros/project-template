"""Command-line interface for validating and inspecting the Asset Graph."""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path
from typing import Any

from .formatting import to_agent, to_dot, to_json, to_toml
from .graph import AmbiguousReferenceError, AssetGraph, UnknownReferenceError
from .loader import load_ledger
from .validation import Finding, governed_files, stale_findings, validate_ledger


QUERY_COMMANDS = {
    "show", "path-history", "upstream", "downstream", "lineage", "raw-sources",
    "producers", "script-io", "impact", "rebuildability", "orphans", "unresolved", "export",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and query the repository Asset Graph.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Project root (default: current directory)")
    parser.add_argument("--allow-stale", action="store_true", help="Return explicitly non-authoritative last-known query data")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Run all graph and asset checks")
    validate.add_argument("--format", choices=("text", "json"), default="text")
    validate.add_argument("--hook", action="store_true", help="Run maintenance-oriented checks and emit hook-friendly findings")

    coverage = subparsers.add_parser("coverage", help="Report governed files and coverage findings")
    coverage.add_argument("--format", choices=("text", "json"), default="text")

    hash_command = subparsers.add_parser("hash", help="Print a file SHA-256 for ledger maintenance")
    hash_command.add_argument("reference")

    for name in ("show", "path-history", "raw-sources", "producers", "script-io", "rebuildability"):
        command = subparsers.add_parser(name)
        command.add_argument("reference")
        _add_query_format(command, allow_as_of=name == "show")

    for name in ("upstream", "downstream"):
        command = subparsers.add_parser(name)
        command.add_argument("reference")
        command.add_argument("--depth", default="1", type=_depth)
        _add_query_format(command, allow_as_of=True)

    lineage = subparsers.add_parser("lineage")
    lineage.add_argument("reference")
    _add_query_format(lineage, allow_as_of=True)

    impact = subparsers.add_parser("impact")
    impact.add_argument("reference")
    impact.add_argument("--include-historical", action="store_true")
    _add_query_format(impact)

    for name in ("orphans", "unresolved"):
        command = subparsers.add_parser(name)
        _add_query_format(command)

    export = subparsers.add_parser("export")
    export.add_argument("--format", choices=("json", "dot"), required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    ledger = load_ledger(args.root)
    if args.command == "validate":
        return _validation_result(validate_ledger(ledger, hook=args.hook), args.format, ledger.enforcement)
    if args.command == "coverage":
        findings = [finding for finding in validate_ledger(ledger, hook=True) if finding.code in {
            "coverage_missing", "active_path_missing", "node_outside_governance", "root_outside_scope", "logical_asset_masks_file",
        }]
        payload = {"governed_files": governed_files(ledger), "findings": [finding.to_dict() for finding in findings]}
        if args.format == "json":
            sys.stdout.write(to_json(payload))
        else:
            print(f"Governed files: {len(payload['governed_files'])}")
            _print_findings(findings)
        return 2 if any(finding.severity == "error" for finding in findings) else 0
    if args.command == "hash":
        return _hash_result(ledger.root, args.reference)

    findings = validate_ledger(ledger, hook=True)
    warnings = [finding for finding in findings if finding.severity == "warning"]
    structural_errors = [
        finding for finding in findings
        if finding.severity == "error" and not finding.stale
    ]
    if structural_errors:
        payload = {
            "status": "invalid",
            "authoritative": False,
            "message": "Asset Graph validation failed; repair the ledger before querying.",
            "findings": [finding.to_dict() for finding in structural_errors],
        }
        sys.stderr.write(to_json(payload))
        return 4
    stale = stale_findings(findings)
    if stale and not args.allow_stale:
        payload = {
            "status": "stale",
            "authoritative": False,
            "message": "Asset Graph is stale; update it with the provenance-ledger workflow before querying.",
            "findings": [finding.to_dict() for finding in stale],
        }
        sys.stderr.write(to_json(payload))
        return 3

    graph = AssetGraph(ledger)
    try:
        result = _run_query(graph, args)
    except (UnknownReferenceError, AmbiguousReferenceError, ValueError) as exc:
        print(f"Asset Graph query error: {exc}", file=sys.stderr)
        return 2
    if stale:
        result = {
            "authoritative": False,
            "warning": "Last-known graph data; the committed graph is stale.",
            "stale_findings": [finding.to_dict() for finding in stale],
            "validation_warnings": [finding.to_dict() for finding in warnings],
            "result": result,
        }
    elif warnings:
        result = {
            "authoritative": False,
            "warning": "Graph query completed with declared provenance limitations.",
            "validation_warnings": [finding.to_dict() for finding in warnings],
            "result": result,
        }
    output_format = args.format
    if output_format == "json":
        sys.stdout.write(to_json(result))
    elif output_format == "toml":
        sys.stdout.write(to_toml(result))
    elif output_format == "dot":
        sys.stdout.write(to_dot(result))
    else:
        sys.stdout.write(to_agent(result))
    return 0


def _run_query(graph: AssetGraph, args: argparse.Namespace) -> dict[str, Any]:
    command = args.command
    as_of = getattr(args, "as_of", None)
    if command == "show":
        return graph.show(args.reference, as_of=as_of)
    if command == "path-history":
        return graph.path_history(args.reference)
    if command == "upstream":
        return graph.upstream(args.reference, args.depth, as_of=as_of)
    if command == "downstream":
        return graph.downstream(args.reference, args.depth, as_of=as_of)
    if command == "lineage":
        return graph.lineage(args.reference, as_of=as_of)
    if command == "raw-sources":
        return graph.raw_sources(args.reference)
    if command == "producers":
        return graph.producers(args.reference)
    if command == "script-io":
        return graph.script_io(args.reference)
    if command == "impact":
        return graph.impact(args.reference, include_historical=args.include_historical)
    if command == "rebuildability":
        return graph.rebuildability(args.reference)
    if command == "orphans":
        return graph.orphans()
    if command == "unresolved":
        return graph.unresolved()
    if command == "export":
        return graph.export()
    raise ValueError(f"unsupported command: {command}")


def _validation_result(findings: list[Finding], output_format: str, enforcement: str) -> int:
    errors = sum(finding.severity == "error" for finding in findings)
    warnings = sum(finding.severity == "warning" for finding in findings)
    status = "fail" if errors else ("pass-with-warnings" if warnings else "pass")
    payload = {
        "status": status,
        "enforcement": enforcement,
        "errors": errors,
        "warnings": warnings,
        "findings": [finding.to_dict() for finding in findings],
    }
    if output_format == "json":
        sys.stdout.write(to_json(payload))
    else:
        _print_findings(findings)
        print(f"Asset Graph: {status.upper()} ({errors} error(s), {warnings} warning(s))")
    return 2 if errors else 0


def _print_findings(findings: list[Finding]) -> None:
    if not findings:
        print("No findings.")
    for finding in findings:
        location = f" [{finding.path or finding.node_id}]" if finding.path or finding.node_id else ""
        print(f"[{finding.severity.upper()}] {finding.code}{location}: {finding.message}")


def _hash_result(root: Path, reference: str) -> int:
    project_root = root.resolve()
    raw_path = Path(reference)
    candidate = raw_path if raw_path.is_absolute() else project_root / raw_path
    # Normalize `..` lexically without dereferencing the final symlink. Symlink
    # nodes are governed files in their own right, so their digest is the link
    # target text rather than the bytes of the target file.
    path = Path(os.path.abspath(candidate))
    try:
        path.relative_to(project_root)
    except ValueError:
        print("hash target must be inside the project root", file=sys.stderr)
        return 2
    if not (path.is_file() or path.is_symlink()):
        print(f"not a file: {reference}", file=sys.stderr)
        return 2
    digest = hashlib.sha256()
    if path.is_symlink():
        digest.update(path.readlink().as_posix().encode("utf-8"))
    else:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    print("sha256:" + digest.hexdigest())
    return 0


def _add_query_format(parser: argparse.ArgumentParser, *, allow_as_of: bool = False) -> None:
    parser.add_argument("--format", choices=("agent", "json", "toml", "dot"), default="agent")
    if allow_as_of:
        parser.add_argument("--as-of", help="Reconstruct paths and relationships at an ISO date/time")


def _depth(value: str) -> int | str:
    if value == "all":
        return value
    try:
        depth = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("depth must be a positive integer or 'all'") from exc
    if depth < 1:
        raise argparse.ArgumentTypeError("depth must be at least 1")
    return depth

#!/usr/bin/env python3
"""
Validate the project Provenance Ledger.

The checker is intentionally conservative: it verifies coverage and required
fields, while substantive truth remains the responsibility of source-grounded
agent work and review.
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


LEDGER_PATH = Path("docs/data/provenance-ledger/index.toml")
DATA_ROOTS = (Path("data/raw"), Path("data/tmp"), Path("data/clean"), Path("results"))
IGNORED_NAMES = {".gitkeep", ".DS_Store"}
VALID_STATUSES = {"complete", "partial-flagged", "missing-blocker", "accepted-limited"}
WARN_STATUSES = {"partial-flagged", "accepted-limited"}
FAIL_STATUSES = {"missing-blocker"}

INDEX_REQUIRED_FIELDS = {"asset_id", "path", "metadata", "dossier", "status"}
ASSET_REQUIRED_FIELDS = {
    "asset_id",
    "asset_name",
    "path",
    "asset_type",
    "stage",
    "format",
    "status",
    "created_or_downloaded_at",
    "producer_scripts",
    "upstream_assets",
    "source_documents",
    "reproduction_command",
    "dossier",
    "last_updated",
}
VARIABLE_REQUIRED_FIELDS = {
    "id",
    "name",
    "kind",
    "data_type",
    "description",
    "unit",
    "missing_value_codes",
    "allowed_values",
    "derivation",
    "source_evidence",
    "status",
}

STRUCTURED_FORMATS = {
    "csv",
    "tsv",
    "txt",
    "json",
    "jsonl",
    "ndjson",
    "parquet",
    "feather",
    "arrow",
    "dta",
    "sav",
    "rds",
    "rda",
    "xlsx",
    "xls",
    "geojson",
    "gpkg",
    "shp",
    "tif",
    "tiff",
    "vrt",
    "nc",
    "netcdf",
}
STRUCTURED_TYPES = {"dataset", "table", "panel", "raster", "vector", "geospatial", "model-output", "figure-data"}
CODE_KINDS = {"categorical", "category", "code", "class", "factor", "enum", "raster-class", "classification"}
CODE_NAME_HINTS = ("code", "class", "category", "cover_id", "coverid", "type_id", "status_id")


@dataclass
class Finding:
    severity: str
    message: str


def load_toml(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, "file not found"
    except tomllib.TOMLDecodeError as exc:
        return None, f"TOML parse error: {exc}"
    except OSError as exc:
        return None, f"could not read file: {exc}"


def is_ignored(path: Path) -> bool:
    return any(part in IGNORED_NAMES for part in path.parts) or path.name.startswith(".~")


def data_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for base in DATA_ROOTS:
        full_base = root / base
        if not full_base.exists():
            continue
        for path in full_base.rglob("*"):
            if path.is_file() and not is_ignored(path):
                files.append(path.relative_to(root))
    return sorted(files)


def path_exists(root: Path, value: str) -> bool:
    return (root / value).exists()


def strip_fragment(value: str) -> str:
    return value.split("#", 1)[0]


def is_url(value: str) -> bool:
    scheme = urlparse(value).scheme
    return scheme in {"http", "https", "doi"}


def looks_like_local_path(value: str) -> bool:
    if is_url(value):
        return False
    clean_value = strip_fragment(value)
    if clean_value.startswith(("./", "../", "data/", "results/", "docs/", "code/")):
        return True
    return "/" in clean_value or Path(clean_value).suffix != ""


def validate_path_list(root: Path, label: str, field: str, values: Any) -> list[Finding]:
    findings: list[Finding] = []
    if not isinstance(values, list):
        findings.append(Finding("error", f"{label}: {field} must be a list"))
        return findings

    for value in values:
        if not isinstance(value, str):
            findings.append(Finding("error", f"{label}: {field} contains a non-string reference"))
            continue
        if not looks_like_local_path(value):
            continue
        path_value = strip_fragment(value)
        if not path_exists(root, path_value):
            findings.append(Finding("error", f"{label}: {field} reference does not exist: {value}"))

    return findings


def validate_upstream_assets(
    root: Path,
    label: str,
    values: Any,
    known_asset_ids: set[str],
) -> list[Finding]:
    findings: list[Finding] = []
    if not isinstance(values, list):
        return [Finding("error", f"{label}: upstream_assets must be a list")]

    for value in values:
        if not isinstance(value, str):
            findings.append(Finding("error", f"{label}: upstream_assets contains a non-string reference"))
            continue
        if value in known_asset_ids:
            continue
        if looks_like_local_path(value) and path_exists(root, strip_fragment(value)):
            continue
        findings.append(Finding("error", f"{label}: upstream_assets references unknown asset or path: {value}"))

    return findings


def is_under(path: Path, candidate_parent: Path) -> bool:
    try:
        path.relative_to(candidate_parent)
        return True
    except ValueError:
        return False


def missing_fields(record: dict[str, Any], required: set[str]) -> list[str]:
    return sorted(field for field in required if field not in record)


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def status_findings(label: str, status: Any) -> list[Finding]:
    if not isinstance(status, str):
        return [Finding("error", f"{label}: status is missing or not a string")]
    if status not in VALID_STATUSES:
        return [Finding("error", f"{label}: invalid status {status!r}")]
    if status in FAIL_STATUSES:
        return [Finding("error", f"{label}: status is {status}")]
    if status in WARN_STATUSES:
        return [Finding("warning", f"{label}: status is {status}")]
    return []


def is_structured_asset(asset: dict[str, Any]) -> bool:
    asset_type = str(asset.get("asset_type", "")).lower()
    fmt = str(asset.get("format", "")).lower().lstrip(".")
    return asset_type in STRUCTURED_TYPES or fmt in STRUCTURED_FORMATS


def looks_code_like(variable: dict[str, Any]) -> bool:
    kind = str(variable.get("kind", "")).lower()
    name = str(variable.get("name", "")).lower()
    return kind in CODE_KINDS or any(hint in name for hint in CODE_NAME_HINTS)


def validate_variable(root: Path, asset_id: str, variable: Any, index: int) -> list[Finding]:
    label = f"{asset_id} variable #{index + 1}"
    findings: list[Finding] = []
    if not isinstance(variable, dict):
        return [Finding("error", f"{label}: variable entry is not a table")]

    for field in missing_fields(variable, VARIABLE_REQUIRED_FIELDS):
        findings.append(Finding("error", f"{label}: missing required field {field}"))

    findings.extend(status_findings(label, variable.get("status")))
    findings.extend(validate_path_list(root, label, "source_evidence", variable.get("source_evidence", [])))

    if looks_code_like(variable):
        allowed_values = as_list(variable.get("allowed_values"))
        status = variable.get("status")
        if not allowed_values and status == "complete":
            findings.append(
                Finding(
                    "error",
                    f"{label}: code-like variable is complete but allowed_values is empty",
                )
            )
        elif not allowed_values:
            findings.append(
                Finding(
                    "warning",
                    f"{label}: code-like variable has no allowed_values and is flagged {status!r}",
                )
            )

    return findings


def validate_asset_file(root: Path, metadata_path: Path, known_asset_ids: set[str]) -> list[Finding]:
    findings: list[Finding] = []
    asset, error = load_toml(root / metadata_path)
    if error:
        return [Finding("error", f"{metadata_path}: {error}")]
    assert asset is not None

    asset_id = str(asset.get("asset_id", metadata_path.stem))
    for field in missing_fields(asset, ASSET_REQUIRED_FIELDS):
        findings.append(Finding("error", f"{metadata_path}: missing required field {field}"))

    findings.extend(status_findings(asset_id, asset.get("status")))

    asset_path = asset.get("path")
    if isinstance(asset_path, str) and not path_exists(root, asset_path):
        findings.append(Finding("error", f"{asset_id}: path does not exist: {asset_path}"))

    dossier = asset.get("dossier")
    if isinstance(dossier, str) and not path_exists(root, dossier):
        findings.append(Finding("error", f"{asset_id}: dossier does not exist: {dossier}"))

    findings.extend(validate_path_list(root, asset_id, "producer_scripts", asset.get("producer_scripts", [])))
    findings.extend(validate_path_list(root, asset_id, "source_documents", asset.get("source_documents", [])))
    findings.extend(validate_upstream_assets(root, asset_id, asset.get("upstream_assets", []), known_asset_ids))

    variables = as_list(asset.get("variables"))
    if is_structured_asset(asset) and not variables:
        findings.append(Finding("error", f"{asset_id}: structured asset has no [[variables]] entries"))

    for index, variable in enumerate(variables):
        findings.extend(validate_variable(root, asset_id, variable, index))

    return findings


def validate_index(root: Path) -> tuple[list[dict[str, Any]], list[Finding]]:
    index, error = load_toml(root / LEDGER_PATH)
    if error:
        return [], [Finding("error", f"{LEDGER_PATH}: {error}")]
    assert index is not None

    assets = index.get("assets", [])
    if not isinstance(assets, list):
        return [], [Finding("error", f"{LEDGER_PATH}: assets must be an array of tables")]

    findings: list[Finding] = []
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    known_asset_ids = {entry.get("asset_id") for entry in assets if isinstance(entry, dict)}
    known_asset_ids = {asset_id for asset_id in known_asset_ids if isinstance(asset_id, str)}

    for entry in assets:
        if not isinstance(entry, dict):
            findings.append(Finding("error", f"{LEDGER_PATH}: asset entry is not a table"))
            continue

        asset_id = str(entry.get("asset_id", "<missing asset_id>"))
        for field in missing_fields(entry, INDEX_REQUIRED_FIELDS):
            findings.append(Finding("error", f"{LEDGER_PATH}: {asset_id} missing required field {field}"))

        if asset_id in seen_ids:
            findings.append(Finding("error", f"{LEDGER_PATH}: duplicate asset_id {asset_id}"))
        seen_ids.add(asset_id)

        path_value = entry.get("path")
        if isinstance(path_value, str):
            if path_value in seen_paths:
                findings.append(Finding("error", f"{LEDGER_PATH}: duplicate path {path_value}"))
            seen_paths.add(path_value)
            if not path_exists(root, path_value):
                findings.append(Finding("error", f"{asset_id}: indexed path does not exist: {path_value}"))

        metadata = entry.get("metadata")
        if isinstance(metadata, str):
            metadata_path = Path(metadata)
            if not path_exists(root, metadata):
                findings.append(Finding("error", f"{asset_id}: metadata does not exist: {metadata}"))
            else:
                findings.extend(validate_asset_file(root, metadata_path, known_asset_ids))

        dossier = entry.get("dossier")
        if isinstance(dossier, str) and not path_exists(root, dossier):
            findings.append(Finding("error", f"{asset_id}: dossier does not exist: {dossier}"))

        findings.extend(status_findings(asset_id, entry.get("status")))

    return assets, findings


def validate_coverage(root: Path, assets: list[dict[str, Any]]) -> list[Finding]:
    findings: list[Finding] = []
    files = data_files(root)
    asset_paths = [Path(entry["path"]) for entry in assets if isinstance(entry, dict) and isinstance(entry.get("path"), str)]

    for file_path in files:
        if any(file_path == asset_path or is_under(file_path, asset_path) for asset_path in asset_paths):
            continue
        findings.append(Finding("error", f"{file_path}: no Provenance Ledger asset entry covers this file"))

    return findings


def print_findings(findings: list[Finding]) -> None:
    if not findings:
        print("Provenance Ledger: PASS")
        return

    for finding in findings:
        print(f"[{finding.severity.upper()}] {finding.message}")

    errors = sum(1 for finding in findings if finding.severity == "error")
    warnings = sum(1 for finding in findings if finding.severity == "warning")
    print(f"Provenance Ledger: {errors} error(s), {warnings} warning(s)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate docs/data/provenance-ledger.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Project root")
    args = parser.parse_args()

    root = args.root.resolve()
    assets, findings = validate_index(root)
    findings.extend(validate_coverage(root, assets))
    print_findings(findings)

    return 2 if any(finding.severity == "error" for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())

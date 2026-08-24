"""Mechanical validation for the manually authored Asset Graph and data assets."""

from __future__ import annotations

import fnmatch
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .graph import AssetGraph
from .loader import Ledger
from .model import Activity, Edge, Node


ALLOWED_GOVERNANCE_ROOTS = (
    "code/00_fetch",
    "code/01_build",
    "code/02_analyze",
    "code/99_explorations",
    "data",
    "results",
)
VALID_NODE_TYPES = {
    "file", "symlink", "expected_file", "logical_asset", "pattern",
    "external_source", "external_package", "unresolved",
}
VALID_NODE_STATES = {"active", "retired"}
VALID_GRAPH_STATUSES = {"complete", "partial-flagged", "missing-blocker", "accepted-limited"}
VALID_PROVENANCE_STATUSES = VALID_GRAPH_STATUSES | {"not-applicable"}
VALID_EVENT_TYPES = {"created", "moved", "deleted", "restored", "superseded"}
VALID_EDGE_STATUSES = {"active", "historical"}
ACTIVITY_RELATIONSHIPS = {
    "production", "data_read", "local_import", "source_include", "configuration",
    "invocation", "generation_input", "generation_code", "generation_config",
}
CAUSAL_RELATIONSHIPS = {"production", "data_read", "generation_input", "generation_code", "generation_config"}
VALID_RELATIONSHIPS = CAUSAL_RELATIONSHIPS | {
    "local_import", "source_include", "configuration", "invocation",
    "pinning", "membership", "alias", "defines", "supersedes",
}
VALID_EDGE_CLASSES = {"causal", "contextual", "structural", "semantic", "organizational"}
STRUCTURED_FORMATS = {
    "csv", "tsv", "json", "jsonl", "ndjson", "parquet", "feather", "arrow", "dta",
    "sav", "rds", "rda", "xlsx", "xls", "geojson", "gpkg", "shp", "tif", "tiff",
    "vrt", "nc", "netcdf",
}
STRUCTURED_TYPES = {
    "dataset", "table", "panel", "raster", "vector", "geospatial", "model-output", "figure-data",
}
CODE_KINDS = {"categorical", "category", "code", "class", "factor", "enum", "raster-class", "classification"}
NODE_ID_PATTERN = re.compile(
    r"^(file|symlink|expected_file|logical_asset|pattern|external_source|external_package|unresolved)_"
    r"[0-9a-f]{8}_[0-9a-f]{4}_[1-5][0-9a-f]{3}_[89ab][0-9a-f]{3}_[0-9a-f]{12}$"
)
EVENT_ID_PATTERN = re.compile(r"^event_[0-9a-f]{8}_[0-9a-f]{4}_[1-5][0-9a-f]{3}_[89ab][0-9a-f]{3}_[0-9a-f]{12}$")
EDGE_ID_PATTERN = re.compile(r"^edge_[0-9a-f]{8}_[0-9a-f]{4}_[1-5][0-9a-f]{3}_[89ab][0-9a-f]{3}_[0-9a-f]{12}$")
SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    path: str | None = None
    node_id: str | None = None
    stale: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def validate_ledger(ledger: Ledger, *, hook: bool = False) -> list[Finding]:
    """Return deterministic findings; validation never changes the ledger."""

    if ledger.version != 2:
        return [Finding("error", "unsupported_version", "Asset Graph validation requires ledger_version = 2")]

    findings: list[Finding] = [
        Finding("error", "load_error", message) for message in ledger.load_errors
    ]
    graph = AssetGraph(ledger)
    findings.extend(_validate_policy(ledger))
    findings.extend(_validate_scope(ledger))
    findings.extend(_validate_nodes(ledger))
    findings.extend(_validate_coverage_and_hashes(ledger, use_cache=hook))
    findings.extend(_validate_events(ledger))
    findings.extend(_validate_activities(ledger))
    findings.extend(_validate_edges(ledger, graph))
    findings.extend(_validate_cycles(graph))
    findings.extend(_validate_assets(ledger))

    if ledger.enforcement == "advisory":
        findings = [
            Finding("warning", finding.code, finding.message, finding.path, finding.node_id, finding.stale)
            if finding.stale and finding.severity == "error"
            else finding
            for finding in findings
        ]
    return sorted(findings, key=lambda finding: (finding.severity, finding.code, finding.path or "", finding.node_id or "", finding.message))


def stale_findings(findings: Iterable[Finding]) -> list[Finding]:
    return [finding for finding in findings if finding.stale]


def governance_roots(ledger: Ledger) -> list[str]:
    governance = ledger.index.get("governance", {})
    roots: Any = None
    if isinstance(governance, dict):
        for key in ("roots", "additional_roots", "governed_roots"):
            if isinstance(governance.get(key), list):
                roots = governance[key]
                break
    if roots is None:
        roots = ledger.index.get("asset_roots", [])
    return sorted({str(value).rstrip("/") for value in roots if isinstance(value, str) and value.rstrip("/")})


def governed_files(ledger: Ledger) -> list[str]:
    roots = governance_roots(ledger)
    exclusions = exclusion_patterns(ledger)
    candidates: set[str] = set()
    for root_value in roots:
        base = ledger.root / root_value
        if not base.exists():
            continue
        if base.is_file() or base.is_symlink():
            candidates.add(root_value)
            continue
        for path in base.rglob("*"):
            if path.is_file() or path.is_symlink():
                candidates.add(path.relative_to(ledger.root).as_posix())

    # Include tracked files even if absent so deletions surface as missing nodes/paths.
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z", "--", *roots], cwd=ledger.root,
            check=False, capture_output=True,
        )
        if result.returncode == 0:
            candidates.update(
                value.decode("utf-8") for value in result.stdout.split(b"\0") if value
            )
    except OSError:
        pass
    return sorted(path for path in candidates if not _excluded(path, exclusions))


def exclusion_patterns(ledger: Ledger) -> list[str]:
    values = ledger.index.get("exclusions", [])
    patterns: list[str] = []
    if isinstance(values, list):
        for value in values:
            if isinstance(value, str):
                patterns.append(value)
            elif isinstance(value, dict) and isinstance(value.get("pattern"), str):
                patterns.append(value["pattern"])
    return patterns


def _validate_scope(ledger: Ledger) -> list[Finding]:
    findings: list[Finding] = []
    roots = governance_roots(ledger)
    for root in sorted(set(ALLOWED_GOVERNANCE_ROOTS) - set(roots)):
        findings.append(Finding(
            "error", "missing_governance_root",
            f"required data/code/results governance root is missing: {root}", path=root,
        ))
    for root in roots:
        if not any(root == allowed or root.startswith(allowed + "/") for allowed in ALLOWED_GOVERNANCE_ROOTS):
            findings.append(Finding(
                "error", "root_outside_scope",
                f"governance root is outside the data/code/results Asset Graph scope: {root}", path=root,
            ))
    for pattern in exclusion_patterns(ledger):
        for root in roots:
            probes = (f"{root}/asset_graph_probe", f"{root}/nested/asset_graph_probe")
            if all(_excluded(probe, [pattern]) for probe in probes):
                findings.append(Finding(
                    "error", "overbroad_exclusion",
                    f"exclusion can conceal arbitrary governed files beneath {root}: {pattern}", path=root,
                ))
                break
    return findings


def _validate_policy(ledger: Ledger) -> list[Finding]:
    findings: list[Finding] = []
    if ledger.index.get("edge_direction") != "upstream_to_downstream":
        findings.append(Finding("error", "invalid_edge_direction", "edge_direction must be upstream_to_downstream"))
    if ledger.index.get("enforcement") not in {"advisory", "strict"}:
        findings.append(Finding("error", "invalid_enforcement", "enforcement must be advisory or strict"))
    governance = ledger.index.get("governance")
    if not isinstance(governance, dict):
        findings.append(Finding("error", "missing_governance", "index must contain a [governance] table"))
        return findings
    if governance.get("mode") != "tracked-plus-roots":
        findings.append(Finding("error", "invalid_governance_mode", "governance.mode must be tracked-plus-roots"))
    for field in ("retain_retired_nodes", "retain_historical_edges"):
        if governance.get(field) is not True:
            findings.append(Finding("error", "invalid_retention_policy", f"governance.{field} must be true"))
    storage = ledger.index.get("storage")
    if not isinstance(storage, dict):
        findings.append(Finding("error", "missing_storage_policy", "index must contain a [storage] table"))
        return findings
    for field in ("manifests", "dependencies", "history"):
        values = storage.get(field)
        if not isinstance(values, list) or not values or any(not isinstance(value, str) for value in values):
            findings.append(Finding("error", "invalid_storage_policy", f"storage.{field} must be a nonempty list of repository-relative TOML paths"))
    asset_directory = storage.get("asset_metadata_directory")
    if not isinstance(asset_directory, str) or not asset_directory.startswith("docs/data/provenance-ledger/"):
        findings.append(Finding("error", "invalid_storage_policy", "storage.asset_metadata_directory must remain beneath docs/data/provenance-ledger/"))
    declared_sets = {
        "valid_node_types": VALID_NODE_TYPES,
        "valid_node_states": VALID_NODE_STATES,
        "valid_graph_statuses": VALID_GRAPH_STATUSES,
        "valid_provenance_statuses": VALID_PROVENANCE_STATUSES,
        "valid_event_types": VALID_EVENT_TYPES,
    }
    for field, expected in declared_sets.items():
        value = ledger.index.get(field)
        if value is not None and (not isinstance(value, list) or set(value) != expected):
            findings.append(Finding("error", "schema_policy_mismatch", f"index {field} does not match the v2 validator contract"))
    return findings


def _validate_nodes(ledger: Ledger) -> list[Finding]:
    findings: list[Finding] = []
    roots = governance_roots(ledger)
    id_counts = Counter(node.id for node in ledger.nodes if node.id)
    path_counts = Counter(node.current_path for node in ledger.nodes if node.state == "active" and node.current_path)
    for node_id, count in id_counts.items():
        if count > 1:
            findings.append(Finding("error", "duplicate_node_id", f"node ID occurs {count} times: {node_id}", node_id=node_id))
    for path, count in path_counts.items():
        if count > 1:
            findings.append(Finding("error", "duplicate_active_path", f"active path is assigned to {count} nodes: {path}", path=path))

    for node in ledger.nodes:
        label = node.id or "<missing ID>"
        if not node.id:
            findings.append(Finding("error", "missing_node_id", "node is missing immutable ID"))
        elif not NODE_ID_PATTERN.fullmatch(node.id):
            findings.append(Finding("error", "invalid_node_id", f"node ID is not a typed UUID: {node.id}", node_id=node.id))
        elif not node.id.startswith(node.node_type + "_"):
            findings.append(Finding(
                "error", "node_id_type_mismatch",
                f"{label}: immutable ID prefix does not match node_type {node.node_type!r}",
                node_id=node.id,
            ))
        if node.node_type not in VALID_NODE_TYPES:
            findings.append(Finding("error", "invalid_node_type", f"{label}: invalid node_type {node.node_type!r}", node_id=node.id))
        if node.state not in VALID_NODE_STATES:
            findings.append(Finding("error", "invalid_node_state", f"{label}: invalid state {node.state!r}", node_id=node.id))
        if node.state == "active" and node.node_type in {"file", "symlink", "expected_file"} and not node.current_path:
            findings.append(Finding("error", "missing_current_path", f"{label}: active filesystem node lacks current_path", node_id=node.id, stale=True))
        required_fields = [
            "node_type", "state", "file_type", "stage", "role", "lifecycle", "presence_policy",
            "graph_status", "provenance_status", "created_at",
        ] if node.node_type in {"file", "symlink", "expected_file"} else ["node_type", "state", "graph_status", "provenance_status", "created_at"]
        if node.node_type in {"file", "symlink", "expected_file"} and node.state == "active":
            required_fields.extend((
                "last_reviewed", "last_known_git_commit", "review_method",
                "inspection_profile", "inspection_evidence",
            ))
        for field in required_fields:
            value = node.raw.get(field)
            if value is None or value == "" or (field == "inspection_profile" and not isinstance(value, list)):
                findings.append(Finding(
                    "error", "missing_node_field", f"{label}: missing required field {field}",
                    path=node.display_path, node_id=node.id,
                ))
        profile = node.raw.get("inspection_profile")
        if profile is not None and (not isinstance(profile, list) or any(not isinstance(item, str) for item in profile)):
            findings.append(Finding("error", "invalid_inspection_profile", f"{label}: inspection_profile must be a list of strings", path=node.display_path, node_id=node.id))
        created_at = node.raw.get("created_at")
        if not isinstance(created_at, str) or _parse_time(created_at) is None:
            findings.append(Finding("error", "invalid_node_time", f"{label}: created_at must be an ISO timestamp string", path=node.display_path, node_id=node.id))
        if node.node_type in {"file", "symlink", "expected_file"} and node.state == "active":
            last_reviewed = node.raw.get("last_reviewed")
            if not isinstance(last_reviewed, str) or _parse_time(last_reviewed) is None:
                findings.append(Finding("error", "invalid_review_date", f"{label}: last_reviewed must be an ISO date string", path=node.display_path, node_id=node.id))
            revision = node.raw.get("last_known_git_commit")
            if not isinstance(revision, str) or not revision.strip():
                findings.append(Finding("error", "invalid_git_revision", f"{label}: last_known_git_commit must be a nonempty string", path=node.display_path, node_id=node.id))
            if _is_data_code_path(node.current_path or "") and node.raw.get("review_method") != "manual-source-inspection":
                findings.append(Finding(
                    "error", "invalid_manual_review",
                    f"{label}: executable data code requires review_method = manual-source-inspection",
                    path=node.display_path, node_id=node.id,
                ))
        if node.state == "retired":
            missing_blocker = node.raw.get("graph_status") == "missing-blocker"
            tombstone_fields = ["last_known_path", "retired_at"]
            if not missing_blocker:
                tombstone_fields.append("last_known_git_commit")
            for field in tombstone_fields:
                if not node.raw.get(field):
                    findings.append(Finding("error", "incomplete_tombstone", f"{label}: retired node lacks {field}", node_id=node.id))
            retired_at = node.raw.get("retired_at")
            if not isinstance(retired_at, str) or _parse_time(retired_at) is None:
                findings.append(Finding("error", "invalid_retirement_time", f"{label}: retired_at must be an ISO timestamp string", node_id=node.id))
            revision = node.raw.get("last_known_git_commit")
            if not missing_blocker and (not isinstance(revision, str) or not revision.strip()):
                findings.append(Finding("error", "invalid_git_revision", f"{label}: last_known_git_commit must be a nonempty string", node_id=node.id))
            digest = node.raw.get("last_reviewed_sha256", node.raw.get("reviewed_sha256"))
            if not missing_blocker and (not isinstance(digest, str) or not SHA256_PATTERN.fullmatch(digest)):
                findings.append(Finding("error", "incomplete_tombstone", f"{label}: retired node lacks a valid last reviewed SHA-256", node_id=node.id))
            findings.extend(_validate_tombstone_recovery(ledger, node))
            successor = node.raw.get("superseded_by")
            if successor is not None and (not isinstance(successor, str) or successor not in id_counts or successor == node.id):
                findings.append(Finding("error", "invalid_tombstone_successor", f"{label}: superseded_by must reference a different registered node", node_id=node.id))
        graph_status = node.raw.get("graph_status")
        if graph_status is not None and graph_status not in VALID_GRAPH_STATUSES:
            findings.append(Finding("error", "invalid_graph_status", f"{label}: invalid graph_status {graph_status!r}", node_id=node.id))
        elif graph_status in {"partial-flagged", "missing-blocker", "accepted-limited"}:
            severity = "error" if graph_status == "missing-blocker" else "warning"
            findings.append(Finding(severity, "incomplete_node_provenance", f"{label}: graph_status is {graph_status}", path=node.display_path, node_id=node.id))
        provenance_status = node.raw.get("provenance_status")
        if provenance_status not in VALID_PROVENANCE_STATUSES:
            findings.append(Finding("error", "invalid_provenance_status", f"{label}: invalid provenance_status {provenance_status!r}", node_id=node.id))
        elif provenance_status in {"partial-flagged", "missing-blocker", "accepted-limited"}:
            severity = "error" if provenance_status == "missing-blocker" else "warning"
            findings.append(Finding(
                severity, "incomplete_node_provenance",
                f"{label}: provenance_status is {provenance_status}",
                path=node.display_path, node_id=node.id,
            ))

        if node.node_type in {"file", "symlink", "expected_file"}:
            local_path = node.current_path or node.last_known_path
            if local_path and not _path_under_roots(local_path, roots):
                findings.append(Finding(
                    "error", "local_node_outside_scope",
                    f"{label}: local node path is outside configured data/code/results roots: {local_path}",
                    path=local_path, node_id=node.id,
                ))
            if node.raw.get("lifecycle") in {"control", "documentation"}:
                findings.append(Finding(
                    "error", "non_asset_local_node",
                    f"{label}: documentation and repository-control files must be explicitly excluded, not registered",
                    path=local_path, node_id=node.id,
                ))
            if node.node_type == "expected_file":
                if node.raw.get("presence_policy") != "expected-output":
                    findings.append(Finding("error", "invalid_expected_file", f"{label}: expected_file requires presence_policy = expected-output", path=local_path, node_id=node.id))
                if node.raw.get("last_observed_presence") not in {"present", "absent"}:
                    findings.append(Finding("error", "invalid_expected_file", f"{label}: expected_file requires last_observed_presence", path=local_path, node_id=node.id))
            elif node.raw.get("presence_policy") != "required":
                findings.append(Finding(
                    "error", "invalid_presence_policy",
                    f"{label}: file and symlink nodes require presence_policy = required",
                    path=local_path, node_id=node.id,
                ))
        elif node.current_path or node.last_known_path:
            findings.append(Finding(
                "error", "non_file_node_has_path",
                f"{label}: {node.node_type} nodes may not claim a repository file path",
                path=node.display_path, node_id=node.id,
            ))
        if node.node_type == "pattern":
            for field in ("pattern", "base_path", "resolution_status", "matches"):
                if field not in node.raw:
                    findings.append(Finding("error", "missing_pattern_field", f"{label}: pattern node lacks {field}", node_id=node.id))
            pattern = node.raw.get("pattern")
            if (
                not isinstance(pattern, str)
                or not pattern
                or Path(pattern).is_absolute()
                or ".." in Path(pattern).parts
            ):
                findings.append(Finding("error", "unsafe_pattern", f"{label}: pattern must be a nonempty relative glob without '..'", node_id=node.id))
            if node.raw.get("base_path") and not _path_under_roots(str(node.raw["base_path"]), roots):
                findings.append(Finding("error", "pattern_outside_scope", f"{label}: pattern base_path is outside governed roots", node_id=node.id))
            if node.raw.get("resolution_status") not in {"resolved", "partial", "unresolved"}:
                findings.append(Finding("error", "invalid_pattern_status", f"{label}: invalid resolution_status", node_id=node.id))
            if node.raw.get("resolution_status") in {"partial", "unresolved"} and node.raw.get("graph_status") == "complete":
                findings.append(Finding("error", "inconsistent_pattern_status", f"{label}: incomplete pattern resolution cannot have graph_status complete", node_id=node.id))
            matches = node.raw.get("matches")
            if not isinstance(matches, list) or any(match not in id_counts for match in matches):
                findings.append(Finding("error", "invalid_pattern_matches", f"{label}: matches must contain registered node IDs", node_id=node.id))
            elif node.id in matches:
                findings.append(Finding("error", "invalid_pattern_matches", f"{label}: a pattern may not match itself", node_id=node.id))
            elif isinstance(pattern, str) and pattern and isinstance(node.raw.get("base_path"), str):
                base_path = Path(node.raw["base_path"])
                node_map = {candidate.id: candidate for candidate in ledger.nodes}
                for match_id in matches:
                    match = node_map.get(match_id)
                    match_path = Path(match.display_path) if match and match.display_path else None
                    if not match or match.node_type not in {"file", "symlink", "expected_file"} or match_path is None:
                        findings.append(Finding("error", "invalid_pattern_match", f"{label}: {match_id} is not a local file identity", node_id=node.id))
                        continue
                    try:
                        relative_match = match_path.relative_to(base_path)
                    except ValueError:
                        findings.append(Finding("error", "invalid_pattern_match", f"{label}: {match_id} is outside base_path", node_id=node.id))
                        continue
                    if not relative_match.match(pattern):
                        findings.append(Finding("error", "invalid_pattern_match", f"{label}: {match_path.as_posix()} does not satisfy {pattern!r}", node_id=node.id))
        elif node.node_type == "external_source":
            source_uri = node.raw.get("source_uri")
            if not isinstance(source_uri, str) or not _is_external(source_uri):
                findings.append(Finding("error", "missing_external_source_uri", f"{label}: external_source requires an http(s) or doi source_uri", node_id=node.id))
        elif node.node_type == "external_package" and not node.raw.get("package_name"):
            findings.append(Finding("error", "missing_external_package_name", f"{label}: external_package lacks package_name", node_id=node.id))
        elif node.node_type == "unresolved" and not node.raw.get("description"):
            findings.append(Finding("error", "missing_unresolved_description", f"{label}: unresolved node lacks description", node_id=node.id))
        if node.node_type == "unresolved" and node.raw.get("graph_status") == "complete":
            findings.append(Finding("error", "inconsistent_unresolved_status", f"{label}: unresolved node cannot have graph_status complete", node_id=node.id))
    return findings


def _validate_coverage_and_hashes(ledger: Ledger, *, use_cache: bool = False) -> list[Finding]:
    findings: list[Finding] = []
    hash_cache = _load_hash_cache(ledger.root) if use_cache else {}
    cache_changed = False

    def digest(path: Path, relative: str) -> str:
        nonlocal cache_changed
        cache_key = _hash_cache_key(path)
        cached = hash_cache.get(relative)
        if isinstance(cached, dict) and cached.get("stat") == cache_key and isinstance(cached.get("sha256"), str):
            return cached["sha256"]
        value = _sha256(path)
        if use_cache:
            hash_cache[relative] = {"stat": cache_key, "sha256": value}
            cache_changed = True
        return value
    governed = governed_files(ledger)
    active_by_path = {
        node.current_path: node for node in ledger.nodes
        if node.state == "active" and node.current_path
    }
    governed_set = set(governed)
    retired_paths = {
        node.last_known_path for node in ledger.nodes
        if node.state == "retired" and node.last_known_path
    }
    uncovered: list[str] = []
    for path in governed:
        node = active_by_path.get(path)
        if not node:
            if not (ledger.root / path).exists() and path in retired_paths:
                continue
            uncovered.append(path)
            findings.append(Finding("error", "coverage_missing", f"governed file has no active node: {path}", path=path, stale=True))
            continue
        if node.node_type == "logical_asset":
            findings.append(Finding("error", "logical_asset_masks_file", f"logical asset cannot satisfy file coverage: {path}", path=path, node_id=node.id))

    for node in ledger.nodes:
        if node.state != "active" or node.node_type not in {"file", "symlink", "expected_file"} or not node.current_path:
            continue
        absolute = ledger.root / node.current_path
        present = absolute.exists() or absolute.is_symlink()
        if not present:
            if node.node_type == "expected_file" or node.raw.get("presence_policy") == "expected-output":
                if node.raw.get("last_observed_presence") == "present":
                    findings.append(Finding("error", "expected_output_disappeared", f"expected output was present at review but is now absent: {node.current_path}", path=node.current_path, node_id=node.id, stale=True))
                continue
            findings.append(Finding("error", "active_path_missing", f"active required node path is absent: {node.current_path}", path=node.current_path, node_id=node.id, stale=True))
            continue
        if node.node_type == "symlink" and not absolute.is_symlink():
            findings.append(Finding("error", "symlink_type_mismatch", f"symlink node path is not a symlink: {node.current_path}", path=node.current_path, node_id=node.id, stale=True))
        if node.node_type == "file" and absolute.is_symlink():
            findings.append(Finding("error", "symlink_type_mismatch", f"symlink path must use node_type = symlink: {node.current_path}", path=node.current_path, node_id=node.id, stale=True))
        if node.current_path not in governed_set:
            findings.append(Finding("error", "node_outside_governance", f"active filesystem node is outside configured graph roots: {node.current_path}", path=node.current_path, node_id=node.id))
            continue
        if (node.node_type == "expected_file" or node.raw.get("presence_policy") == "expected-output") and node.raw.get("last_observed_presence") == "absent":
            findings.append(Finding("error", "expected_output_appeared", f"expected output was absent at review but is now present: {node.current_path}", path=node.current_path, node_id=node.id, stale=True))
        reviewed = node.raw.get("reviewed_sha256")
        actual = digest(absolute, node.current_path)
        if not isinstance(reviewed, str) or not SHA256_PATTERN.fullmatch(reviewed):
            findings.append(Finding("error", "missing_review_hash", f"node lacks a valid reviewed_sha256: {node.current_path}", path=node.current_path, node_id=node.id, stale=True))
        elif reviewed != actual:
            findings.append(Finding("error", "hash_mismatch", f"content changed since graph review: {node.current_path}", path=node.current_path, node_id=node.id, stale=True))

        if _is_data_code_path(node.current_path):
            profile = node.raw.get("inspection_profile")
            if not isinstance(profile, list) or not profile:
                findings.append(Finding("error", "missing_inspection_profile", f"pipeline script lacks inspection_profile: {node.current_path}", path=node.current_path, node_id=node.id, stale=True))
            if not node.raw.get("last_reviewed") or not node.raw.get("review_method"):
                findings.append(Finding("error", "missing_inspection_attestation", f"pipeline script lacks review date/method: {node.current_path}", path=node.current_path, node_id=node.id, stale=True))

    # A matching reviewed digest is evidence for an agent to consider a move;
    # it is never used to reassign the immutable ID automatically.
    uncovered_hashes: dict[str, list[str]] = defaultdict(list)
    for path in uncovered:
        absolute = ledger.root / path
        if absolute.is_file() or absolute.is_symlink():
            uncovered_hashes[digest(absolute, path)].append(path)
    for node in ledger.nodes:
        absolute = ledger.root / node.current_path if node.current_path else None
        if node.state != "active" or not node.current_path or (absolute is not None and (absolute.exists() or absolute.is_symlink())):
            continue
        reviewed = node.raw.get("reviewed_sha256")
        if isinstance(reviewed, str):
            for candidate in uncovered_hashes.get(reviewed, []):
                findings.append(Finding("error", "candidate_move", f"missing path {node.current_path} and new path {candidate} share the reviewed content hash; agent confirmation is required", path=candidate, node_id=node.id, stale=True))
    if use_cache and cache_changed:
        _save_hash_cache(ledger.root, hash_cache)
    return findings


def _validate_events(ledger: Ledger) -> list[Finding]:
    findings: list[Finding] = []
    node_map = {node.id: node for node in ledger.nodes}
    node_ids = set(node_map)
    roots = governance_roots(ledger)
    id_counts = Counter(event.id for event in ledger.file_events if event.id)
    for event_id, count in id_counts.items():
        if count > 1:
            findings.append(Finding("error", "duplicate_event_id", f"file event ID occurs {count} times: {event_id}"))

    grouped: dict[str, list[Any]] = defaultdict(list)
    for event in ledger.file_events:
        grouped[event.node_id].append(event)
        if not event.id:
            findings.append(Finding("error", "missing_event_id", "file event is missing ID", node_id=event.node_id))
        elif not EVENT_ID_PATTERN.fullmatch(event.id):
            findings.append(Finding("error", "invalid_event_id", f"event ID is not a UUID-backed ID: {event.id}", node_id=event.node_id))
        if event.node_id not in node_ids:
            findings.append(Finding("error", "unknown_event_node", f"event references unknown node: {event.node_id}", node_id=event.node_id))
        if event.event not in VALID_EVENT_TYPES:
            findings.append(Finding("error", "invalid_event_type", f"{event.id}: invalid event {event.event!r}", node_id=event.node_id))
        if not event.occurred_at:
            findings.append(Finding("error", "missing_event_time", f"{event.id}: missing occurred_at", node_id=event.node_id))
        elif _parse_time(event.occurred_at) is None:
            findings.append(Finding("error", "invalid_event_time", f"{event.id}: occurred_at is not an ISO timestamp", node_id=event.node_id))
        observed_commit = event.raw.get("observed_commit")
        if not isinstance(observed_commit, str) or not observed_commit.strip():
            findings.append(Finding("error", "missing_event_revision", f"{event.id}: observed_commit must be a nonempty string", node_id=event.node_id))
        required_paths = {
            "created": ("to_path",),
            "restored": ("to_path",),
            "moved": ("from_path", "to_path"),
            "deleted": ("from_path",),
            "superseded": ("from_path",),
        }.get(event.event, ())
        for field in required_paths:
            if not event.raw.get(field):
                findings.append(Finding("error", "incomplete_event", f"{event.id}: {event.event} event lacks {field}", node_id=event.node_id))
        if event.event in {"deleted", "superseded"} and not event.raw.get("reason"):
            findings.append(Finding("error", "missing_event_reason", f"{event.id}: {event.event} event lacks reason", node_id=event.node_id))
        if event.event == "superseded" and not event.raw.get("successor_id"):
            findings.append(Finding("error", "missing_event_successor", f"{event.id}: superseded event lacks successor_id", node_id=event.node_id))
        elif event.event == "superseded":
            successor = event.raw.get("successor_id")
            if successor not in node_ids or successor == event.node_id:
                findings.append(Finding("error", "invalid_event_successor", f"{event.id}: successor_id must reference a different registered node", node_id=event.node_id))
            node = node_map.get(event.node_id)
            if node and node.raw.get("superseded_by") != successor:
                findings.append(Finding("error", "event_successor_mismatch", f"{event.id}: successor_id disagrees with node superseded_by", node_id=event.node_id))
        for path in (event.from_path, event.to_path):
            if path and not _path_under_roots(path, roots):
                findings.append(Finding(
                    "error", "event_path_outside_scope",
                    f"{event.id}: lifecycle path is outside configured data/code/results roots: {path}",
                    path=path, node_id=event.node_id,
                ))

    occupancy: dict[str, list[tuple[datetime, datetime | None, str]]] = defaultdict(list)
    for node in ledger.nodes:
        node_events = grouped.get(node.id, [])
        timestamp_counts = Counter(
            event.occurred_at for event in node_events if _parse_time(event.occurred_at) is not None
        )
        for occurred_at, count in timestamp_counts.items():
            if count > 1:
                findings.append(Finding(
                    "error", "ambiguous_event_order",
                    f"{node.id}: {count} lifecycle events share occurred_at {occurred_at}; use distinct timestamps",
                    node_id=node.id,
                ))
        events = sorted(node_events, key=lambda item: (_time_sort_key(item.occurred_at), item.id))
        if node.node_type in {"file", "symlink", "expected_file"} and not events:
            findings.append(Finding("error", "missing_file_history", f"filesystem node has no lifecycle event: {node.id}", path=node.display_path, node_id=node.id, stale=True))
            continue
        path: str | None = None
        path_started: datetime | None = None
        for event in events:
            occurred = _parse_time(event.occurred_at)
            if event.event == "created":
                if path is not None:
                    findings.append(Finding("error", "invalid_file_history", f"{event.id}: created event occurs while node already has a path", node_id=node.id))
                path = event.to_path
                path_started = occurred
            elif event.event == "moved":
                if event.from_path != path:
                    findings.append(Finding("error", "event_from_path_mismatch", f"{event.id}: from_path {event.from_path!r} does not match reconstructed path {path!r}", path=event.from_path, node_id=node.id, stale=True))
                if path and path_started and occurred:
                    occupancy[path].append((path_started, occurred, node.id))
                path = event.to_path
                path_started = occurred
            elif event.event == "deleted":
                if event.from_path != path:
                    findings.append(Finding("error", "event_from_path_mismatch", f"{event.id}: deleted from_path {event.from_path!r} does not match reconstructed path {path!r}", path=event.from_path, node_id=node.id, stale=True))
                if path and path_started and occurred:
                    occupancy[path].append((path_started, occurred, node.id))
                path = None
                path_started = None
            elif event.event == "restored":
                if path is not None:
                    findings.append(Finding("error", "invalid_file_history", f"{event.id}: restored event occurs while node has a path", node_id=node.id))
                path = event.to_path
                path_started = occurred
            elif event.event == "superseded" and event.from_path:
                if path != event.from_path:
                    findings.append(Finding("error", "event_from_path_mismatch", f"{event.id}: superseded path does not match reconstructed path", path=event.from_path, node_id=node.id, stale=True))
                if path and path_started and occurred:
                    occupancy[path].append((path_started, occurred, node.id))
                path = None
                path_started = None

        if path and path_started:
            occupancy[path].append((path_started, None, node.id))

        if node.state == "active" and events and path != node.current_path:
            findings.append(Finding("error", "event_state_mismatch", f"{node.id}: history ends at {path!r}, current_path is {node.current_path!r}", path=node.current_path, node_id=node.id, stale=True))
        if node.state == "retired" and events:
            final_known = next((event.from_path for event in reversed(events) if event.event in {"deleted", "superseded"}), None)
            if path is not None or (final_known and final_known != node.last_known_path):
                findings.append(Finding("error", "event_state_mismatch", f"{node.id}: tombstone disagrees with lifecycle history", path=node.last_known_path, node_id=node.id, stale=True))
        if events:
            first = events[0]
            if first.event != "created":
                findings.append(Finding("error", "invalid_file_history", f"{node.id}: first lifecycle event must be created", node_id=node.id))
            created_at = node.raw.get("created_at")
            if isinstance(created_at, str) and _parse_time(created_at) != _parse_time(first.occurred_at):
                findings.append(Finding("error", "created_at_mismatch", f"{node.id}: created_at disagrees with the first lifecycle event", node_id=node.id))
            if node.state == "retired":
                terminal = events[-1]
                if terminal.event not in {"deleted", "superseded"}:
                    findings.append(Finding("error", "invalid_retirement_event", f"{node.id}: retired history must end in deleted or superseded", node_id=node.id))
                if _parse_time(str(node.raw.get("retired_at", ""))) != _parse_time(terminal.occurred_at):
                    findings.append(Finding("error", "retired_at_mismatch", f"{node.id}: retired_at disagrees with the terminal lifecycle event", node_id=node.id))
                observed_commit = terminal.raw.get("observed_commit")
                if node.raw.get("graph_status") != "missing-blocker" and node.raw.get("last_known_git_commit") != observed_commit:
                    findings.append(Finding("error", "retirement_revision_mismatch", f"{node.id}: last_known_git_commit disagrees with retirement evidence", node_id=node.id))
    for path, intervals in occupancy.items():
        ordered = sorted(intervals, key=lambda value: (value[0], value[2]))
        for index, (start, end, node_id) in enumerate(ordered):
            for other_start, other_end, other_id in ordered[index + 1:]:
                if other_id == node_id:
                    continue
                if end is not None and other_start >= end:
                    break
                if other_end is None or start < other_end:
                    findings.append(Finding(
                        "error", "overlapping_path_identity",
                        f"path is assigned to different immutable IDs during overlapping intervals: {node_id}, {other_id}",
                        path=path,
                    ))
    return findings


def _validate_activities(ledger: Ledger) -> list[Finding]:
    findings: list[Finding] = []
    node_map = {node.id: node for node in ledger.nodes}
    revision_counts = Counter(activity.revision_id for activity in ledger.activities if activity.revision_id)
    for revision_id, count in revision_counts.items():
        if count > 1:
            findings.append(Finding("error", "duplicate_activity_revision", f"activity revision occurs {count} times: {revision_id}"))
    reference_fields = ("reads", "imports", "sources", "includes", "configures", "writes", "invoked_by")
    revisions_by_activity: dict[str, list[Any]] = defaultdict(list)
    for activity in ledger.activities:
        revisions_by_activity[activity.id].append(activity)
        if not activity.id or not activity.revision_id or not activity.producer:
            findings.append(Finding("error", "incomplete_activity", f"activity lacks id, revision_id, or producer: {activity.raw}"))
            continue
        for field in ("kind", "status", "valid_from", "graph_status", "reviewed_at", "review_method", "evidence", "reproduction_command", "producer_sha256", "producer_revision"):
            if not activity.raw.get(field):
                findings.append(Finding("error", "missing_activity_field", f"{activity.revision_id}: missing required field {field}"))
        if activity.valid_from and _parse_time(activity.valid_from) is None:
            findings.append(Finding("error", "invalid_activity_time", f"{activity.revision_id}: invalid valid_from"))
        if activity.valid_to and _parse_time(activity.valid_to) is None:
            findings.append(Finding("error", "invalid_activity_time", f"{activity.revision_id}: invalid valid_to"))
        if _invalid_interval(activity.valid_from, activity.valid_to):
            findings.append(Finding("error", "invalid_activity_interval", f"{activity.revision_id}: valid_to must follow valid_from"))
        refs = [activity.producer]
        for field in reference_fields:
            if field not in activity.raw:
                findings.append(Finding("error", "missing_activity_field", f"{activity.revision_id}: missing required list {field}"))
            values = activity.raw.get(field, [])
            if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
                findings.append(Finding("error", "invalid_activity_field", f"{activity.revision_id}: {field} must be a list of node IDs"))
                continue
            refs.extend(values)
        for node_id in refs:
            if node_id not in node_map:
                findings.append(Finding("error", "unknown_activity_node", f"{activity.revision_id}: unknown node {node_id}", node_id=node_id))
        if activity.valid_from:
            for node_id in [activity.producer, *[
                value
                for field in ("reads", "imports", "sources", "includes", "configures", "invoked_by")
                for value in activity.raw.get(field, [])
                if isinstance(value, str)
            ]]:
                if node_id in node_map and not _node_active_at_time(ledger, node_map[node_id], activity.valid_from):
                    findings.append(Finding(
                        "error", "activity_node_outside_lifetime",
                        f"{activity.revision_id}: {node_id} is not active at valid_from",
                        node_id=node_id,
                    ))
        if activity.status == "historical" and activity.valid_to:
            for output_id in activity.raw.get("writes", []):
                output = node_map.get(output_id) if isinstance(output_id, str) else None
                if output and not _node_created_by_time(ledger, output, activity.valid_to):
                    findings.append(Finding(
                        "error", "activity_output_outside_lifetime",
                        f"{activity.revision_id}: output {output.id} did not exist by valid_to",
                        node_id=output.id,
                    ))
        producer = node_map.get(activity.producer)
        if producer and not _valid_producer_node(producer):
            findings.append(Finding(
                "error", "invalid_activity_producer",
                f"{activity.revision_id}: producer must be registered executable data code",
                path=producer.display_path, node_id=producer.id,
            ))
        if not activity.raw.get("writes"):
            findings.append(Finding("error", "activity_without_outputs", f"{activity.revision_id}: production activity has no writes"))
        if activity.raw.get("review_method") != "manual-source-inspection":
            findings.append(Finding(
                "error", "invalid_manual_review",
                f"{activity.revision_id}: activities require review_method = manual-source-inspection",
            ))
        producer_sha = activity.raw.get("producer_sha256")
        if producer_sha and (not isinstance(producer_sha, str) or not SHA256_PATTERN.fullmatch(producer_sha)):
            findings.append(Finding("error", "invalid_activity_hash", f"{activity.revision_id}: producer_sha256 is invalid"))
        if producer and isinstance(producer_sha, str) and activity.status == "active":
            reviewed = producer.raw.get("reviewed_sha256", producer.raw.get("last_reviewed_sha256"))
            if reviewed and producer_sha != reviewed:
                findings.append(Finding("error", "activity_producer_hash_mismatch", f"{activity.revision_id}: producer_sha256 does not match the producer node attestation", node_id=producer.id))
            if activity.raw.get("producer_revision") != producer.raw.get("last_known_git_commit"):
                findings.append(Finding("error", "activity_producer_revision_mismatch", f"{activity.revision_id}: producer_revision does not match the active producer node attestation", node_id=producer.id))
        if producer and isinstance(producer_sha, str) and activity.status == "historical":
            findings.extend(_validate_historical_activity_blob(ledger, activity, producer, producer_sha))
        evidence = activity.raw.get("evidence")
        if evidence is not None and not isinstance(evidence, (str, list)):
            findings.append(Finding("error", "invalid_activity_evidence", f"{activity.revision_id}: evidence must be a string or list"))
        if activity.status == "active" and producer and producer.state == "retired":
            findings.append(Finding("error", "active_activity_retired_producer", f"{activity.revision_id}: active activity has retired producer", node_id=producer.id))
        if activity.status not in VALID_EDGE_STATUSES:
            findings.append(Finding("error", "invalid_activity_status", f"{activity.revision_id}: invalid status {activity.status!r}"))
        if activity.status == "historical" and not activity.valid_to:
            findings.append(Finding("error", "open_historical_activity", f"{activity.revision_id}: historical revision lacks valid_to"))
        if activity.status == "active" and activity.valid_to:
            findings.append(Finding("error", "closed_active_activity", f"{activity.revision_id}: active revision may not have valid_to"))
        graph_status = activity.raw.get("graph_status")
        if graph_status not in VALID_GRAPH_STATUSES:
            findings.append(Finding("error", "invalid_activity_graph_status", f"{activity.revision_id}: invalid graph_status {graph_status!r}"))
        elif graph_status in {"partial-flagged", "missing-blocker", "accepted-limited"}:
            severity = "error" if graph_status == "missing-blocker" else "warning"
            findings.append(Finding(
                severity, "incomplete_activity_provenance",
                f"{activity.revision_id}: graph_status is {graph_status}",
            ))

    for activity_id, revisions in revisions_by_activity.items():
        active_count = sum(revision.status == "active" for revision in revisions)
        if active_count > 1:
            findings.append(Finding("error", "multiple_active_activity_revisions", f"{activity_id}: {active_count} active revisions"))
        intervals = sorted(
            (
                (_parse_time(revision.valid_from), _parse_time(revision.valid_to), revision.revision_id)
                for revision in revisions
                if _parse_time(revision.valid_from) is not None
            ),
            key=lambda value: (value[0], value[2]),
        )
        for index, (start, end, revision_id) in enumerate(intervals):
            assert start is not None
            for other_start, other_end, other_id in intervals[index + 1:]:
                assert other_start is not None
                if end is not None and other_start >= end:
                    break
                if other_end is None or start < other_end:
                    findings.append(Finding("error", "overlapping_activity_revisions", f"{activity_id}: revisions overlap: {revision_id}, {other_id}"))
    return findings


def _validate_edges(ledger: Ledger, graph: AssetGraph) -> list[Finding]:
    findings: list[Finding] = []
    node_map = graph.nodes_by_id
    edge_id_counts = Counter(edge.id for edge in graph.edges if edge.id)
    relation_counts = Counter((edge.upstream, edge.downstream, edge.relationship, edge.valid_from, edge.valid_to) for edge in graph.edges)
    for edge_id, count in edge_id_counts.items():
        if count > 1:
            findings.append(Finding("error", "duplicate_edge_id", f"edge ID occurs {count} times: {edge_id}"))
    for relation, count in relation_counts.items():
        if count > 1:
            findings.append(Finding("error", "duplicate_relation", f"canonical relationship occurs {count} times: {relation}"))

    for edge in graph.edges:
        upstream = node_map.get(edge.upstream)
        downstream = node_map.get(edge.downstream)
        if not edge.id:
            findings.append(Finding("error", "missing_edge_id", f"edge lacks ID: {edge.upstream} -> {edge.downstream}"))
        elif edge.projected_from is None and not EDGE_ID_PATTERN.fullmatch(edge.id):
            findings.append(Finding("error", "invalid_edge_id", f"authored edge ID is not a UUID-backed ID: {edge.id}"))
        for endpoint, node_id in (("upstream", edge.upstream), ("downstream", edge.downstream)):
            if node_id not in node_map:
                findings.append(Finding("error", "unknown_edge_node", f"{edge.id}: unknown {endpoint} node {node_id}", node_id=node_id))
        if edge.status not in VALID_EDGE_STATUSES:
            findings.append(Finding("error", "invalid_edge_status", f"{edge.id}: invalid status {edge.status!r}"))
        if edge.relationship not in VALID_RELATIONSHIPS:
            findings.append(Finding("error", "invalid_relationship", f"{edge.id}: unsupported relationship {edge.relationship!r}"))
        if edge.projected_from is None and edge.relationship in ACTIVITY_RELATIONSHIPS:
            findings.append(Finding(
                "error", "authored_activity_relationship",
                f"{edge.id}: {edge.relationship} must be recorded through an activity revision",
            ))
        if edge.edge_class not in VALID_EDGE_CLASSES:
            findings.append(Finding("error", "invalid_edge_class", f"{edge.id}: invalid edge_class {edge.edge_class!r}"))
        if edge.relationship == "production" and upstream and not _valid_producer_node(upstream):
            findings.append(Finding(
                "error", "invalid_production_upstream",
                f"{edge.id}: production upstream must be registered executable data code",
                path=upstream.display_path, node_id=upstream.id,
            ))
        if edge.valid_from and _parse_time(edge.valid_from) is None:
            findings.append(Finding("error", "invalid_edge_time", f"{edge.id}: invalid valid_from"))
        if edge.valid_to and _parse_time(edge.valid_to) is None:
            findings.append(Finding("error", "invalid_edge_time", f"{edge.id}: invalid valid_to"))
        if _invalid_interval(edge.valid_from, edge.valid_to):
            findings.append(Finding("error", "invalid_edge_interval", f"{edge.id}: valid_to must follow valid_from"))
        if edge.projected_from is None:
            for field in ("upstream", "downstream", "relationship", "edge_class", "valid_from", "status", "provenance_relevance", "operational_relevance", "evidence"):
                if field not in edge.raw or edge.raw.get(field) is None or edge.raw.get(field) == "":
                    findings.append(Finding("error", "missing_edge_field", f"{edge.id}: missing required field {field}"))
            if edge.status == "historical" and not edge.raw.get("evidence_revision"):
                findings.append(Finding("error", "missing_edge_field", f"{edge.id}: historical edge lacks evidence_revision"))
            if edge.valid_from:
                for endpoint in (upstream, downstream):
                    if endpoint and not _node_active_at_time(ledger, endpoint, edge.valid_from):
                        findings.append(Finding(
                            "error", "edge_node_outside_lifetime",
                            f"{edge.id}: endpoint {endpoint.id} is not active at valid_from",
                            node_id=endpoint.id,
                        ))
        for field in ("provenance_relevance", "operational_relevance"):
            if not isinstance(edge.raw.get(field), bool):
                findings.append(Finding("error", "invalid_edge_boolean", f"{edge.id}: {field} must be a boolean"))
        if edge.status == "active" and edge.operational_relevance and (
            (upstream and upstream.state == "retired") or (downstream and downstream.state == "retired")
        ):
            findings.append(Finding("error", "active_edge_retired_node", f"{edge.id}: active operational edge references a retired node"))
        if edge.status == "historical" and not edge.valid_to:
            findings.append(Finding("error", "open_historical_edge", f"{edge.id}: historical edge lacks valid_to"))
        if edge.status == "historical" and edge.operational_relevance:
            findings.append(Finding("error", "historical_edge_operational", f"{edge.id}: historical edge cannot be operationally relevant"))
        if edge.status == "active" and edge.valid_to:
            findings.append(Finding("error", "closed_active_edge", f"{edge.id}: active edge may not have valid_to"))

    active_paths = {
        node.current_path: node for node in ledger.nodes
        if node.state == "active" and node.current_path
    }
    for node in ledger.nodes:
        if node.state != "active":
            continue
        if node.node_type == "symlink" and node.current_path:
            alias_edges = [
                edge for edge in graph.incoming.get(node.id, [])
                if edge.relationship == "alias" and edge.status == "active"
            ]
            if len(alias_edges) != 1:
                findings.append(Finding(
                    "error", "invalid_symlink_alias",
                    f"symlink node requires exactly one active target -> symlink alias edge; found {len(alias_edges)}",
                    path=node.current_path, node_id=node.id,
                ))
            absolute = ledger.root / node.current_path
            if absolute.is_symlink():
                target_absolute = (absolute.parent / absolute.readlink()).resolve(strict=False)
                try:
                    target_path = target_absolute.relative_to(ledger.root.resolve()).as_posix()
                except ValueError:
                    findings.append(Finding("error", "symlink_target_outside_scope", f"symlink target is outside the repository: {node.current_path}", path=node.current_path, node_id=node.id))
                else:
                    target_node = active_paths.get(target_path)
                    if target_node is None:
                        findings.append(Finding("error", "unregistered_symlink_target", f"symlink target has no active node: {target_path}", path=node.current_path, node_id=node.id))
                    elif len(alias_edges) == 1 and alias_edges[0].upstream != target_node.id:
                        findings.append(Finding("error", "symlink_alias_target_mismatch", f"alias edge does not reference the symlink's registered target: {target_path}", path=node.current_path, node_id=node.id))
        elif node.node_type == "pattern":
            memberships = {
                edge.upstream for edge in graph.incoming.get(node.id, [])
                if edge.relationship == "membership" and edge.status == "active"
            }
            declared = set(node.raw.get("matches", [])) if isinstance(node.raw.get("matches"), list) else set()
            if memberships != declared:
                findings.append(Finding(
                    "error", "pattern_membership_mismatch",
                    f"pattern matches must equal active member-to-pattern edges: {node.id}",
                    node_id=node.id,
                ))
        elif node.node_type == "logical_asset":
            memberships = [
                edge for edge in graph.incoming.get(node.id, [])
                if edge.relationship == "membership" and edge.status == "active"
            ]
            if not memberships:
                findings.append(Finding("error", "logical_asset_without_members", f"logical asset has no active membership edges: {node.id}", node_id=node.id))

    # Generated/intermediate/data-result nodes require source origin or producer.
    for node in ledger.nodes:
        if node.state != "active" or node.node_type not in {"file", "expected_file"}:
            continue
        path = node.current_path or ""
        is_output = node.raw.get("lifecycle") != "control" and Path(path).name != ".gitkeep" and (
            node.raw.get("lifecycle") in {"intermediate", "generated"}
            or node.raw.get("stage") in {"tmp", "clean", "result", "results"}
            or path.startswith(("data/tmp/", "data/clean/", "results/"))
        )
        if is_output and not any(edge.relationship == "production" for edge in graph.incoming.get(node.id, [])):
            findings.append(Finding("error", "output_without_producer", f"generated node has no current or historical producer: {path or node.id}", path=path or None, node_id=node.id))
    return findings


def _validate_cycles(graph: AssetGraph) -> list[Finding]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in graph.edges:
        if edge.relationship in CAUSAL_RELATIONSHIPS:
            adjacency[edge.upstream].add(edge.downstream)
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []
    findings: list[Finding] = []

    def visit(node_id: str) -> None:
        if node_id in visited:
            return
        if node_id in visiting:
            start = stack.index(node_id)
            cycle = stack[start:] + [node_id]
            findings.append(Finding("error", "causal_cycle", "prohibited causal cycle: " + " -> ".join(cycle), node_id=node_id))
            return
        visiting.add(node_id)
        stack.append(node_id)
        for child in sorted(adjacency.get(node_id, ())):
            visit(child)
        stack.pop()
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in sorted(graph.nodes_by_id):
        visit(node_id)
    # Collapse duplicate reports for the same rendered cycle.
    return list({finding.message: finding for finding in findings}.values())


def _validate_assets(ledger: Ledger) -> list[Finding]:
    findings: list[Finding] = []
    node_ids = {node.id for node in ledger.nodes}
    node_map = {node.id: node for node in ledger.nodes}
    assets_by_node = Counter(asset.node_id for asset in ledger.assets if asset.node_id)
    asset_ids = Counter(asset.asset_id for asset in ledger.assets if asset.asset_id)
    for asset_id, count in asset_ids.items():
        if count > 1:
            findings.append(Finding("error", "duplicate_asset_id", f"asset ID occurs {count} times: {asset_id}"))
    for node in ledger.nodes:
        if not _is_data_bearing_node(node):
            continue
        count = assets_by_node.get(node.id, 0)
        if count == 0:
            findings.append(Finding(
                "error", "missing_asset_overlay",
                f"data-bearing node has no asset overlay: {node.display_path or node.id}",
                path=node.display_path, node_id=node.id, stale=True,
            ))
        elif count > 1:
            findings.append(Finding(
                "error", "duplicate_node_asset",
                f"data-bearing node has {count} asset overlays: {node.display_path or node.id}",
                path=node.display_path, node_id=node.id,
            ))
    for asset in ledger.assets:
        label = asset.asset_id or (asset.source.as_posix() if asset.source else "<asset>")
        if not asset.asset_id:
            findings.append(Finding("error", "missing_asset_id", f"{label}: missing asset_id"))
        if not asset.node_id:
            findings.append(Finding("error", "missing_asset_node", f"{label}: missing node_id"))
        elif asset.node_id not in node_ids:
            findings.append(Finding("error", "unknown_asset_node", f"{label}: unknown node_id {asset.node_id}", node_id=asset.node_id))
        status = asset.raw.get("status")
        if status not in VALID_GRAPH_STATUSES:
            findings.append(Finding("error", "invalid_asset_status", f"{label}: invalid status {status!r}"))
        elif status in {"partial-flagged", "missing-blocker", "accepted-limited"}:
            severity = "error" if status == "missing-blocker" else "warning"
            findings.append(Finding(severity, "incomplete_asset_provenance", f"{label}: status is {status}", node_id=asset.node_id))
        dossier = asset.raw.get("dossier")
        if not isinstance(dossier, str) or not dossier:
            findings.append(Finding("error", "missing_asset_dossier", f"{label}: missing dossier path", node_id=asset.node_id))
        elif not _safe_repo_path(dossier) or not dossier.startswith("docs/data/provenance-ledger/assets/"):
            findings.append(Finding("error", "invalid_asset_dossier", f"{label}: dossier must be repository-relative under docs/data/provenance-ledger/assets/: {dossier}", path=dossier, node_id=asset.node_id))
        elif not (ledger.root / dossier).is_file():
            findings.append(Finding("error", "missing_asset_dossier", f"{label}: dossier does not exist: {dossier}", path=dossier, node_id=asset.node_id))
        elif not _nonempty_text_file(ledger.root / dossier):
            findings.append(Finding("error", "empty_asset_dossier", f"{label}: dossier is empty: {dossier}", path=dossier, node_id=asset.node_id))
        for field in ("asset_name", "asset_type", "format", "status", "created_or_downloaded_at", "dossier", "last_updated"):
            if not asset.raw.get(field):
                findings.append(Finding("error", "missing_asset_field", f"{label}: missing required field {field}", node_id=asset.node_id))
        asset_type = str(asset.raw.get("asset_type", "")).lower()
        fmt = str(asset.raw.get("format", "")).lower().lstrip(".")
        linked_node = node_map.get(asset.node_id or "")
        node_format = str(linked_node.raw.get("file_type", "")).lower().lstrip(".") if linked_node else ""
        if node_format and fmt and node_format != fmt:
            findings.append(Finding(
                "error", "asset_format_mismatch",
                f"{label}: overlay format {fmt!r} disagrees with node file_type {node_format!r}",
                node_id=asset.node_id,
            ))
        variables = asset.raw.get("variables", [])
        if not isinstance(variables, list):
            findings.append(Finding("error", "invalid_variables", f"{label}: variables must be an array of tables"))
        if asset_type in STRUCTURED_TYPES or fmt in STRUCTURED_FORMATS or node_format in STRUCTURED_FORMATS:
            if not isinstance(variables, list) or not variables:
                findings.append(Finding("error", "structured_asset_without_variables", f"{label}: structured asset has no [[variables]] entries"))
        if isinstance(variables, list):
            variable_ids = Counter(
                variable.get("id") for variable in variables
                if isinstance(variable, dict) and isinstance(variable.get("id"), str) and variable.get("id")
            )
            variable_names = Counter(
                variable.get("name") for variable in variables
                if isinstance(variable, dict) and isinstance(variable.get("name"), str) and variable.get("name")
            )
            for variable_id, count in variable_ids.items():
                if count > 1:
                    findings.append(Finding(
                        "error", "duplicate_variable_id",
                        f"{label}: variable ID occurs {count} times: {variable_id}",
                        node_id=asset.node_id,
                    ))
            for variable_name, count in variable_names.items():
                if count > 1:
                    findings.append(Finding(
                        "error", "duplicate_variable_name",
                        f"{label}: variable name occurs {count} times: {variable_name}",
                        node_id=asset.node_id,
                    ))
            for index, variable in enumerate(variables):
                if not isinstance(variable, dict):
                    findings.append(Finding("error", "invalid_variable", f"{label}: variable #{index + 1} is not a table"))
                    continue
                for field in ("id", "name", "kind", "data_type", "description", "unit", "missing_value_codes", "allowed_values", "derivation", "source_evidence", "status"):
                    if field not in variable:
                        findings.append(Finding("error", "missing_variable_field", f"{label} variable #{index + 1}: missing {field}"))
                for field in ("id", "name", "kind", "data_type", "description", "unit", "derivation", "status"):
                    if field in variable and not isinstance(variable[field], str):
                        findings.append(Finding("error", "invalid_variable_field", f"{label} variable #{index + 1}: {field} must be a string"))
                for field in ("missing_value_codes", "allowed_values", "source_evidence"):
                    if field in variable and not isinstance(variable[field], list):
                        findings.append(Finding("error", "invalid_variable_field", f"{label} variable #{index + 1}: {field} must be a list"))
                if variable.get("status") not in VALID_GRAPH_STATUSES:
                    findings.append(Finding("error", "invalid_variable_status", f"{label} variable #{index + 1}: invalid status {variable.get('status')!r}"))
                elif variable.get("status") in {"partial-flagged", "missing-blocker", "accepted-limited"}:
                    severity = "error" if variable.get("status") == "missing-blocker" else "warning"
                    findings.append(Finding(
                        severity,
                        "incomplete_variable_provenance",
                        f"{label} variable {variable.get('name', index + 1)}: status is {variable.get('status')}",
                        node_id=asset.node_id,
                    ))
                if variable.get("status") == "complete":
                    for field in ("id", "name", "kind", "data_type", "description", "unit", "derivation"):
                        value = variable.get(field)
                        if not isinstance(value, str) or not value.strip():
                            findings.append(Finding(
                                "error", "empty_variable_field",
                                f"{label} variable #{index + 1}: complete provenance requires nonempty {field}",
                                node_id=asset.node_id,
                            ))
                    evidence_values = variable.get("source_evidence")
                    if (
                        not isinstance(evidence_values, list)
                        or not evidence_values
                        or any(not isinstance(value, str) or not value.strip() for value in evidence_values)
                    ):
                        findings.append(Finding(
                            "error", "missing_variable_evidence",
                            f"{label} variable #{index + 1}: complete provenance requires source_evidence",
                            node_id=asset.node_id,
                        ))
                kind = str(variable.get("kind", "")).lower()
                name = str(variable.get("name", "")).lower()
                code_like = kind in CODE_KINDS or any(hint in name for hint in ("code", "class", "category", "type_id", "status_id"))
                if code_like and not variable.get("allowed_values") and variable.get("status") == "complete":
                    findings.append(Finding("error", "coded_variable_without_values", f"{label} variable {variable.get('name', index + 1)} is complete but has no allowed_values"))
                for evidence in variable.get("source_evidence", []) if isinstance(variable.get("source_evidence"), list) else []:
                    if isinstance(evidence, str) and not _is_external(evidence):
                        local = evidence.split("#", 1)[0]
                        if local and not _safe_repo_path(local):
                            findings.append(Finding("error", "invalid_source_evidence", f"{label}: source evidence must be repository-relative: {evidence}"))
                        elif local and not (ledger.root / local).exists():
                            findings.append(Finding("error", "missing_source_evidence", f"{label}: source evidence does not exist: {evidence}"))
    return findings


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    if path.is_symlink():
        digest.update(path.readlink().as_posix().encode("utf-8"))
    else:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _nonempty_text_file(path: Path) -> bool:
    try:
        return bool(path.read_text(encoding="utf-8").strip())
    except (OSError, UnicodeError):
        return False


def _is_pipeline_script(path: str) -> bool:
    return _is_data_code_path(path) and Path(path).suffix in {
        ".py", ".R", ".r", ".jl", ".sh", ".bash", ".zsh", ".sql",
        ".do", ".sas", ".ipynb",
    }


def _is_data_code_path(path: str) -> bool:
    return path.startswith((
        "code/00_fetch/", "code/01_build/", "code/02_analyze/",
        "code/99_explorations/",
    ))


def _valid_producer_node(node: Node) -> bool:
    path = node.display_path or ""
    if node.node_type not in {"file", "symlink"}:
        return False
    if not path.startswith(("code/00_fetch/", "code/01_build/", "code/02_analyze/", "code/99_explorations/")):
        return False
    return _is_pipeline_script(path) or node.raw.get("role") in {"pipeline-entry", "producer"}


def _node_created_by_time(ledger: Ledger, node: Node, timestamp: str) -> bool:
    cutoff = _parse_time(timestamp)
    if cutoff is None:
        return False
    events = sorted(
        (event for event in ledger.file_events if event.node_id == node.id),
        key=lambda event: (_time_sort_key(event.occurred_at), event.id),
    )
    first_created = next((event for event in events if event.event == "created"), None)
    created_at = _parse_time(first_created.occurred_at) if first_created else _parse_time(node.raw.get("created_at"))
    return created_at is not None and created_at <= cutoff


def _excluded(path: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        clean = pattern.rstrip("/")
        if fnmatch.fnmatch(path, pattern) or Path(path).match(pattern):
            return True
        if pattern.endswith("/**") and (path == clean[:-3] or path.startswith(clean[:-3] + "/")):
            return True
    return False


def _is_external(value: str) -> bool:
    return value.startswith(("http://", "https://", "doi:"))


def _path_under_roots(path: str, roots: list[str]) -> bool:
    candidate = Path(path)
    if candidate.is_absolute() or ".." in candidate.parts:
        return False
    normalized = candidate.as_posix().removeprefix("./").rstrip("/")
    return any(normalized == root or normalized.startswith(root + "/") for root in roots)


def _is_data_bearing_node(node: Node) -> bool:
    path = node.display_path or ""
    if Path(path).name == ".gitkeep" or node.raw.get("lifecycle") == "control":
        return False
    return (
        node.node_type == "logical_asset"
        or path.startswith(("data/", "results/"))
        or node.raw.get("lifecycle") in {"raw", "intermediate", "generated"}
        or node.raw.get("stage") in {"raw", "tmp", "clean", "result", "results"}
    )


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _time_sort_key(value: str | None) -> datetime:
    return _parse_time(value) or datetime.max.replace(tzinfo=timezone.utc)


def _invalid_interval(valid_from: str | None, valid_to: str | None) -> bool:
    start = _parse_time(valid_from)
    end = _parse_time(valid_to)
    return start is not None and end is not None and end <= start


def _validate_tombstone_recovery(ledger: Ledger, node: Node) -> list[Finding]:
    if node.raw.get("graph_status") == "missing-blocker":
        return []
    commit = node.raw.get("last_known_git_commit")
    path = node.last_known_path
    if not isinstance(commit, str) or not commit or not path:
        return []
    git_marker = ledger.root / ".git"
    if not git_marker.exists():
        return []
    actual, error = _git_blob_sha256(ledger.root, f"{commit}:{path}")
    if error:
        return [Finding(
            "error", "unrecoverable_tombstone",
            f"{node.id}: Git cannot recover {path} at {commit}; use missing-blocker if no evidence survives",
            path=path, node_id=node.id,
        )]
    expected = node.raw.get("last_reviewed_sha256", node.raw.get("reviewed_sha256"))
    if actual != expected:
        return [Finding(
            "error", "tombstone_hash_mismatch",
            f"{node.id}: last reviewed hash does not match {commit}:{path}",
            path=path, node_id=node.id,
        )]
    return []


def _validate_historical_activity_blob(
    ledger: Ledger,
    activity: Activity,
    producer: Node,
    expected_sha256: str,
) -> list[Finding]:
    if not (ledger.root / ".git").exists():
        return []
    revision = activity.raw.get("producer_revision")
    if not isinstance(revision, str) or not revision:
        return []
    path = activity.raw.get("producer_path")
    if not isinstance(path, str) or not path:
        path = _historical_path_at(
            ledger,
            producer.id,
            activity.valid_to or activity.valid_from,
            before=activity.valid_to is not None,
        )
    if not path:
        return [Finding(
            "error", "unrecoverable_activity_producer",
            f"{activity.revision_id}: cannot reconstruct producer path at the historical revision",
            node_id=producer.id,
        )]
    actual, error = _git_blob_sha256(ledger.root, f"{revision}:{path}")
    if error:
        return [Finding(
            "error", "unrecoverable_activity_producer",
            f"{activity.revision_id}: Git cannot recover {path} at {revision}",
            path=path, node_id=producer.id,
        )]
    if actual != expected_sha256:
        return [Finding(
            "error", "historical_activity_hash_mismatch",
            f"{activity.revision_id}: producer_sha256 does not match {revision}:{path}",
            path=path, node_id=producer.id,
        )]
    return []


def _historical_path_at(ledger: Ledger, node_id: str, as_of: str | None, *, before: bool = False) -> str | None:
    cutoff = _parse_time(as_of)
    if cutoff is None:
        return None
    path: str | None = None
    events = sorted(
        (event for event in ledger.file_events if event.node_id == node_id),
        key=lambda event: (_time_sort_key(event.occurred_at), event.id),
    )
    for event in events:
        occurred = _parse_time(event.occurred_at)
        if occurred is None or occurred > cutoff or (before and occurred == cutoff):
            break
        if event.event in {"created", "restored", "moved"}:
            path = event.to_path
        elif event.event in {"deleted", "superseded"}:
            path = None
    return path


def _node_active_at_time(ledger: Ledger, node: Node, as_of: str) -> bool:
    cutoff = _parse_time(as_of)
    if cutoff is None:
        return False
    events = [event for event in ledger.file_events if event.node_id == node.id]
    if not events:
        created = _parse_time(str(node.raw.get("created_at", "")))
        retired = _parse_time(str(node.raw.get("retired_at", "")))
        return (created is None or created <= cutoff) and (retired is None or cutoff < retired)
    state = "not-yet-created"
    for event in sorted(events, key=lambda item: (_time_sort_key(item.occurred_at), item.id)):
        occurred = _parse_time(event.occurred_at)
        if occurred is None or occurred > cutoff:
            break
        if event.event in {"created", "restored", "moved"}:
            state = "active"
        elif event.event in {"deleted", "superseded"}:
            state = "retired"
    return state == "active"


def _git_blob_sha256(root: Path, object_spec: str) -> tuple[str | None, bool]:
    try:
        process = subprocess.Popen(
            ["git", "show", object_spec],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        return None, True
    assert process.stdout is not None
    digest = hashlib.sha256()
    try:
        for chunk in iter(lambda: process.stdout.read(1024 * 1024), b""):
            digest.update(chunk)
        returncode = process.wait(timeout=30)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
        return None, True
    if returncode != 0:
        return None, True
    return "sha256:" + digest.hexdigest(), False


def _hash_cache_key(path: Path) -> list[int | str]:
    stat = path.lstat()
    target = path.readlink().as_posix() if path.is_symlink() else ""
    return [stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns, stat.st_ino, stat.st_mode, target]


def _load_hash_cache(root: Path) -> dict[str, Any]:
    cache_path = root / ".cache/asset-graph/hash-cache-v1.json"
    try:
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    entries = payload.get("entries") if isinstance(payload, dict) else None
    return entries if isinstance(entries, dict) else {}


def _save_hash_cache(root: Path, entries: dict[str, Any]) -> None:
    cache_path = root / ".cache/asset-graph/hash-cache-v1.json"
    temporary = cache_path.with_suffix(".tmp")
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_text(
            json.dumps({"version": 1, "entries": entries}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(cache_path)
    except OSError:
        # Cache failure never changes validation correctness; the next hook
        # simply performs the uncached digest work again.
        return


def _safe_repo_path(value: str) -> bool:
    path = Path(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts

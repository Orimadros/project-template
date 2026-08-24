"""Load Provenance Ledger v2 grouped TOML without inferring dependencies."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from .model import Activity, Asset, Edge, FileEvent, Node


INDEX_PATH = Path("docs/data/provenance-ledger/index.toml")


@dataclass
class Ledger:
    root: Path
    index_path: Path
    index: dict[str, Any]
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    activities: list[Activity] = field(default_factory=list)
    file_events: list[FileEvent] = field(default_factory=list)
    assets: list[Asset] = field(default_factory=list)
    loaded_files: list[Path] = field(default_factory=list)
    load_errors: list[str] = field(default_factory=list)

    @property
    def version(self) -> int:
        value = self.index.get("ledger_version", 1)
        return int(value) if isinstance(value, int) else 1

    @property
    def enforcement(self) -> str:
        return str(self.index.get("enforcement", "strict" if self.version == 1 else "advisory"))


def read_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def load_ledger(root: Path | str = Path("."), index_path: Path = INDEX_PATH) -> Ledger:
    """Load the v2 registry, or enough of v1 for its legacy checker.

    File discovery is confined to the ledger directory and explicit include paths.
    It never inspects source code and never creates relationships.
    """

    project_root = Path(root).resolve()
    absolute_index = project_root / index_path
    try:
        index = read_toml(absolute_index)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return Ledger(project_root, index_path, {}, load_errors=[f"{index_path}: {exc}"])

    ledger = Ledger(project_root, index_path, index, loaded_files=[index_path])
    if ledger.version < 2:
        return ledger

    source_files, source_errors = _source_files(project_root, index_path.parent, index)
    ledger.load_errors.extend(source_errors)
    for relative_path in source_files:
        try:
            document = read_toml(project_root / relative_path)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            ledger.load_errors.append(f"{relative_path}: {exc}")
            continue
        ledger.loaded_files.append(relative_path)
        _append_records(ledger, document, relative_path)

    # Allow small registries to place v2 records directly in index.toml.
    _append_records(ledger, index, index_path)
    return ledger


def _source_files(root: Path, ledger_dir: Path, index: dict[str, Any]) -> tuple[list[Path], list[str]]:
    candidates: set[Path] = set()
    explicit: set[Path] = set()
    errors: list[str] = []

    def add_explicit(path: Path) -> None:
        if path.suffix != ".toml":
            return
        if not _safe_ledger_path(path, ledger_dir):
            errors.append(f"unsafe ledger include outside {ledger_dir}: {path}")
            return
        explicit.add(path)

    # Explicit lists are authoritative when supplied. Both legacy top-level
    # keys and the v2 [storage] table are accepted.
    for key in ("manifest_files", "dependency_files", "history_files", "asset_files", "includes"):
        for value in _strings(index.get(key)):
            add_explicit(Path(value))
    storage = index.get("storage")
    if isinstance(storage, dict):
        for key in ("manifests", "dependencies", "history", "asset_files", "includes"):
            for value in _strings(storage.get(key)):
                add_explicit(Path(value))
        asset_directory = storage.get("asset_metadata_directory")
        if isinstance(asset_directory, str):
            relative_directory = Path(asset_directory)
            if not _safe_ledger_path(relative_directory, ledger_dir):
                errors.append(f"unsafe asset metadata directory outside {ledger_dir}: {asset_directory}")
            else:
                directory = root / relative_directory
                if directory.exists():
                    candidates.update(path.relative_to(root) for path in directory.rglob("*.toml") if path.is_file())

    if explicit:
        candidates.update(explicit)
        for dirname in ("manifests", "dependencies", "history"):
            directory = root / ledger_dir / dirname
            if not directory.exists():
                continue
            for discovered in directory.rglob("*.toml"):
                relative = discovered.relative_to(root)
                if discovered.is_file() and relative not in explicit:
                    errors.append(f"unlisted ledger TOML is not in authoritative [storage] lists: {relative}")
    else:
        # Conventional grouped layout remains the fallback for portable small
        # registries and test fixtures without [storage].
        for dirname in ("manifests", "dependencies", "history", "assets"):
            directory = root / ledger_dir / dirname
            if directory.exists():
                candidates.update(path.relative_to(root) for path in directory.rglob("*.toml") if path.is_file())

    candidates.discard(ledger_dir / "index.toml")
    return sorted(candidates, key=lambda path: path.as_posix()), errors


def _safe_ledger_path(path: Path, ledger_dir: Path) -> bool:
    if path.is_absolute() or ".." in path.parts:
        return False
    try:
        path.relative_to(ledger_dir)
    except ValueError:
        return False
    return True


def _strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)


def _append_records(ledger: Ledger, document: dict[str, Any], source: Path) -> None:
    record_types = {
        "nodes": (Node, ledger.nodes),
        "edges": (Edge, ledger.edges),
        "activities": (Activity, ledger.activities),
        "file_events": (FileEvent, ledger.file_events),
        "assets": (Asset, ledger.assets),
    }
    for key, (record_type, destination) in record_types.items():
        if key not in document:
            continue
        value = document[key]
        if not isinstance(value, list):
            ledger.load_errors.append(f"{source}: {key} must be an array of tables")
            continue
        malformed = sum(not isinstance(item, dict) for item in value)
        if malformed:
            ledger.load_errors.append(f"{source}: {key} contains {malformed} non-table record(s)")
        destination.extend(
            record_type.from_dict(record, source)
            for record in value
            if isinstance(record, dict)
        )

    # Assets can be arrays in a grouped file or a single overlay per file.
    if "asset_id" in document and not isinstance(document.get("assets"), list):
        ledger.assets.append(Asset.from_dict(document, source))

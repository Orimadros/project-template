"""Typed in-memory records used by the asset-graph loader and query engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Node:
    id: str
    node_type: str
    state: str
    current_path: str | None
    last_known_path: str | None
    raw: dict[str, Any] = field(compare=False, hash=False, repr=False)
    source: Path | None = field(default=None, compare=False, hash=False, repr=False)

    @classmethod
    def from_dict(cls, record: dict[str, Any], source: Path | None = None) -> "Node":
        return cls(
            id=str(record.get("id", "")),
            node_type=str(record.get("node_type", "")),
            state=str(record.get("state", "active")),
            current_path=_string_or_none(record.get("current_path", record.get("path"))),
            last_known_path=_string_or_none(record.get("last_known_path")),
            raw=dict(record),
            source=source,
        )

    @property
    def display_path(self) -> str | None:
        return self.current_path or self.last_known_path


@dataclass(frozen=True)
class Edge:
    id: str
    upstream: str
    downstream: str
    relationship: str
    edge_class: str
    status: str
    provenance_relevance: bool
    operational_relevance: bool
    valid_from: str | None
    valid_to: str | None
    raw: dict[str, Any] = field(compare=False, hash=False, repr=False)
    source: Path | None = field(default=None, compare=False, hash=False, repr=False)
    projected_from: str | None = None

    @classmethod
    def from_dict(
        cls,
        record: dict[str, Any],
        source: Path | None = None,
        projected_from: str | None = None,
    ) -> "Edge":
        status = str(record.get("status", "active"))
        return cls(
            id=str(record.get("id", "")),
            upstream=str(record.get("upstream", "")),
            downstream=str(record.get("downstream", "")),
            relationship=str(record.get("relationship", "")),
            edge_class=str(record.get("edge_class", "causal")),
            status=status,
            provenance_relevance=bool(record.get("provenance_relevance", True)),
            operational_relevance=bool(record.get("operational_relevance", status == "active")),
            valid_from=_temporal_string(record.get("valid_from")),
            valid_to=_temporal_string(record.get("valid_to")),
            raw=dict(record),
            source=source,
            projected_from=projected_from,
        )


@dataclass(frozen=True)
class Activity:
    id: str
    revision_id: str
    producer: str
    status: str
    valid_from: str | None
    valid_to: str | None
    raw: dict[str, Any] = field(compare=False, hash=False, repr=False)
    source: Path | None = field(default=None, compare=False, hash=False, repr=False)

    @classmethod
    def from_dict(cls, record: dict[str, Any], source: Path | None = None) -> "Activity":
        return cls(
            id=str(record.get("id", "")),
            revision_id=str(record.get("revision_id", record.get("id", ""))),
            producer=str(record.get("producer", "")),
            status=str(record.get("status", "active")),
            valid_from=_temporal_string(record.get("valid_from")),
            valid_to=_temporal_string(record.get("valid_to")),
            raw=dict(record),
            source=source,
        )


@dataclass(frozen=True)
class FileEvent:
    id: str
    node_id: str
    event: str
    occurred_at: str
    from_path: str | None
    to_path: str | None
    raw: dict[str, Any] = field(compare=False, hash=False, repr=False)
    source: Path | None = field(default=None, compare=False, hash=False, repr=False)

    @classmethod
    def from_dict(cls, record: dict[str, Any], source: Path | None = None) -> "FileEvent":
        return cls(
            id=str(record.get("id", "")),
            node_id=str(record.get("node_id", "")),
            event=str(record.get("event", "")),
            occurred_at=_temporal_string(record.get("occurred_at")) or "",
            from_path=_string_or_none(record.get("from_path")),
            to_path=_string_or_none(record.get("to_path")),
            raw=dict(record),
            source=source,
        )


@dataclass(frozen=True)
class Asset:
    asset_id: str
    node_id: str | None
    raw: dict[str, Any] = field(compare=False, hash=False, repr=False)
    source: Path | None = field(default=None, compare=False, hash=False, repr=False)

    @classmethod
    def from_dict(cls, record: dict[str, Any], source: Path | None = None) -> "Asset":
        return cls(
            asset_id=str(record.get("asset_id", "")),
            node_id=_string_or_none(record.get("node_id")),
            raw=dict(record),
            source=source,
        )


def _string_or_none(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _temporal_string(value: Any) -> str | None:
    if value is None:
        return None
    return value.isoformat() if hasattr(value, "isoformat") else str(value)

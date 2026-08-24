"""Deterministic graph projection and read-only lineage queries."""

from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, time, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

from .loader import Ledger
from .model import Activity, Edge, FileEvent, Node


PROJECTION_RULES: tuple[tuple[str, str, bool], ...] = (
    ("reads", "data_read", False),
    ("imports", "local_import", False),
    ("sources", "source_include", False),
    ("includes", "source_include", False),
    ("configures", "configuration", False),
    ("invoked_by", "invocation", False),
)

OUTPUT_PROJECTION_RULES: tuple[tuple[str, str], ...] = (
    ("reads", "generation_input"),
    ("imports", "generation_code"),
    ("sources", "generation_code"),
    ("includes", "generation_code"),
    ("configures", "generation_config"),
)

SCRIPT_SUFFIXES = {".py", ".r", ".R", ".jl", ".sh", ".do", ".sas"}


class UnknownReferenceError(LookupError):
    """A query path or immutable ID does not identify a node."""


class AmbiguousReferenceError(LookupError):
    """A historical path identifies more than one node."""


class StaleGraphError(RuntimeError):
    """The committed graph is stale and cannot answer authoritatively."""


class AssetGraph:
    """An immutable query view over authored and activity-projected edges."""

    def __init__(self, ledger: Ledger):
        self.ledger = ledger
        self.nodes_by_id = {node.id: node for node in ledger.nodes if node.id}
        self.events_by_node: dict[str, list[FileEvent]] = defaultdict(list)
        for event in ledger.file_events:
            self.events_by_node[event.node_id].append(event)
        for events in self.events_by_node.values():
            events.sort(key=lambda event: (_time_sort_key(event.occurred_at), event.id))

        self.edges = sorted(
            [*ledger.edges, *self._project_activities(ledger.activities)],
            key=lambda edge: (edge.upstream, edge.downstream, edge.relationship, edge.id),
        )
        self.incoming: dict[str, list[Edge]] = defaultdict(list)
        self.outgoing: dict[str, list[Edge]] = defaultdict(list)
        for edge in self.edges:
            self.incoming[edge.downstream].append(edge)
            self.outgoing[edge.upstream].append(edge)

        self._active_paths: dict[str, list[str]] = defaultdict(list)
        self._historical_paths: dict[str, list[str]] = defaultdict(list)
        for node in ledger.nodes:
            if node.state == "active" and node.current_path:
                self._active_paths[node.current_path].append(node.id)
            for path in self.paths_for(node.id):
                self._historical_paths[path].append(node.id)

    def _project_activities(self, activities: Iterable[Activity]) -> list[Edge]:
        projected: list[Edge] = []
        for activity in activities:
            raw = activity.raw
            producer = activity.producer
            if not producer:
                continue
            common = {
                "edge_class": "causal",
                "status": activity.status,
                "provenance_relevance": True,
                "operational_relevance": activity.status == "active",
                "valid_from": activity.valid_from,
                "valid_to": activity.valid_to,
            }
            for field, relationship, _ in PROJECTION_RULES:
                for upstream in _string_list(raw.get(field)):
                    projected.append(
                        self._projected_edge(activity, upstream, producer, relationship, common)
                    )
            for output in _string_list(raw.get("writes")):
                projected.append(
                    self._projected_edge(activity, producer, output, "production", common)
                )
                for field, relationship in OUTPUT_PROJECTION_RULES:
                    for upstream in _string_list(raw.get(field)):
                        projected.append(
                            self._projected_edge(activity, upstream, output, relationship, common)
                        )
        return projected

    @staticmethod
    def _projected_edge(
        activity: Activity,
        upstream: str,
        downstream: str,
        relationship: str,
        common: dict[str, Any],
    ) -> Edge:
        edge_id = ":".join(
            ("projected", activity.revision_id, relationship, upstream, downstream)
        )
        raw = {
            "id": edge_id,
            "upstream": upstream,
            "downstream": downstream,
            "relationship": relationship,
            **common,
        }
        return Edge.from_dict(raw, activity.source, projected_from=activity.revision_id)

    def resolve(self, reference: str, *, as_of: str | None = None) -> Node:
        if reference in self.nodes_by_id:
            return self.nodes_by_id[reference]
        normalized = Path(reference).as_posix().removeprefix("./")
        if as_of:
            matches = [
                node.id
                for node in self.nodes_by_id.values()
                if self.path_at(node.id, as_of) == normalized
            ]
        else:
            matches = list(self._active_paths.get(normalized, []))
            if not matches:
                matches = list(dict.fromkeys(self._historical_paths.get(normalized, [])))
        if not matches:
            raise UnknownReferenceError(f"unknown asset graph path or ID: {reference}")
        if len(matches) > 1:
            raise AmbiguousReferenceError(
                f"historical path {reference!r} identifies multiple nodes; query by immutable ID: "
                + ", ".join(sorted(matches))
            )
        return self.nodes_by_id[matches[0]]

    def paths_for(self, node_id: str) -> list[str]:
        node = self.nodes_by_id.get(node_id)
        paths: list[str] = []
        if node:
            paths.extend(path for path in (node.current_path, node.last_known_path) if path)
            paths.extend(_string_list(node.raw.get("former_paths")))
        for event in self.events_by_node.get(node_id, []):
            paths.extend(path for path in (event.from_path, event.to_path) if path)
        return list(dict.fromkeys(paths))

    def path_at(self, node_id: str, as_of: str) -> str | None:
        events = self.events_by_node.get(node_id, [])
        if not events:
            node = self.nodes_by_id.get(node_id)
            return node.display_path if node else None
        cutoff = _as_of_time(as_of)
        path: str | None = None
        for event in events:
            occurred = _parse_time(event.occurred_at)
            if occurred is None or occurred > cutoff:
                break
            if event.event in {"created", "restored", "moved"}:
                path = event.to_path
            elif event.event in {"deleted", "superseded"}:
                path = None
        return path

    def state_at(self, node_id: str, as_of: str) -> str:
        events = self.events_by_node.get(node_id, [])
        if not events:
            node = self.nodes_by_id.get(node_id)
            return node.state if node else "unknown"
        cutoff = _as_of_time(as_of)
        state = "not-yet-created"
        for event in events:
            occurred = _parse_time(event.occurred_at)
            if occurred is None or occurred > cutoff:
                break
            if event.event in {"created", "restored", "moved"}:
                state = "active"
            elif event.event in {"deleted", "superseded"}:
                state = "retired"
        return state

    def path_history(self, reference: str) -> dict[str, Any]:
        node = self.resolve(reference)
        return {
            "node": self.node_view(node),
            "events": [self.event_view(event) for event in self.events_by_node.get(node.id, [])],
        }

    def show(self, reference: str, *, as_of: str | None = None) -> dict[str, Any]:
        node = self.resolve(reference, as_of=as_of)
        incoming = self._filtered_edges(self.incoming.get(node.id, []), as_of=as_of)
        outgoing = self._filtered_edges(self.outgoing.get(node.id, []), as_of=as_of)
        return {
            "node": self.node_view(node, as_of=as_of),
            "immediate_upstream": [self.edge_view(edge, neighbor=edge.upstream, as_of=as_of) for edge in incoming],
            "immediate_downstream": [self.edge_view(edge, neighbor=edge.downstream, as_of=as_of) for edge in outgoing],
        }

    def upstream(self, reference: str, depth: int | str = 1, *, as_of: str | None = None) -> dict[str, Any]:
        node = self.resolve(reference, as_of=as_of)
        return self._traverse(node, "upstream", depth, as_of=as_of, provenance=True)

    def downstream(self, reference: str, depth: int | str = 1, *, as_of: str | None = None) -> dict[str, Any]:
        node = self.resolve(reference, as_of=as_of)
        return self._traverse(node, "downstream", depth, as_of=as_of, provenance=True)

    def lineage(self, reference: str, *, as_of: str | None = None) -> dict[str, Any]:
        return self.upstream(reference, "all", as_of=as_of)

    def raw_sources(self, reference: str, *, as_of: str | None = None) -> dict[str, Any]:
        lineage = self.upstream(reference, "all", as_of=as_of)
        sources = [
            node for node in lineage["nodes"]
            if node.get("node_type") == "external_source"
            or node.get("lifecycle") == "raw"
            or node.get("stage") == "raw"
            or str(node.get("path", "")).startswith("data/raw/")
        ]
        return {"root": lineage["root"], "sources": sources, "edges": lineage["edges"]}

    def producers(self, reference: str, *, as_of: str | None = None) -> dict[str, Any]:
        lineage = self.upstream(reference, "all", as_of=as_of)
        producers = [node for node in lineage["nodes"] if self._is_script_node(node)]
        producer_ids = {node["id"] for node in producers}
        relevant_edges = [
            edge for edge in lineage["edges"]
            if edge["upstream"] in producer_ids or edge["downstream"] in producer_ids
        ]
        return {"root": lineage["root"], "producers": producers, "edges": relevant_edges}

    def script_io(self, reference: str, *, as_of: str | None = None) -> dict[str, Any]:
        node = self.resolve(reference, as_of=as_of)
        incoming = self._filtered_edges(self.incoming.get(node.id, []), as_of=as_of)
        outgoing = self._filtered_edges(self.outgoing.get(node.id, []), as_of=as_of)
        current_incoming = [edge for edge in incoming if edge.status == "active"]
        current_outgoing = [edge for edge in outgoing if edge.status == "active"]
        historical_incoming = [edge for edge in incoming if edge.status == "historical"]
        historical_outgoing = [edge for edge in outgoing if edge.status == "historical"]
        return {
            "script": self.node_view(node, as_of=as_of),
            "reads": self._neighbors(current_incoming, {"data_read"}, as_of),
            "imports": self._neighbors(current_incoming, {"local_import"}, as_of),
            "sources": self._neighbors(current_incoming, {"source_include"}, as_of),
            "configurations": self._neighbors(current_incoming, {"configuration"}, as_of),
            "invokers": self._neighbors(current_incoming, {"invocation"}, as_of),
            "writes": self._neighbors(current_outgoing, {"production"}, as_of, downstream=True),
            "historical_reads": self._neighbors(historical_incoming, {"data_read"}, as_of),
            "historical_imports": self._neighbors(historical_incoming, {"local_import"}, as_of),
            "historical_sources": self._neighbors(historical_incoming, {"source_include"}, as_of),
            "historical_configurations": self._neighbors(historical_incoming, {"configuration"}, as_of),
            "historical_invokers": self._neighbors(historical_incoming, {"invocation"}, as_of),
            "historical_writes": self._neighbors(historical_outgoing, {"production"}, as_of, downstream=True),
        }

    def impact(self, reference: str, *, include_historical: bool = False) -> dict[str, Any]:
        node = self.resolve(reference)
        edge_filter = (
            (lambda edge: edge.provenance_relevance)
            if include_historical
            else (lambda edge: edge.operational_relevance and edge.status == "active")
        )
        return self._traverse(node, "downstream", "all", edge_filter=edge_filter)

    def rebuildability(self, reference: str) -> dict[str, Any]:
        node = self.resolve(reference)
        lineage = self.upstream(node.id, "all")
        current = self._traverse(
            node,
            "upstream",
            "all",
            edge_filter=lambda edge: edge.status == "active" and edge.operational_relevance,
        )
        blockers: list[dict[str, Any]] = []
        current_nodes = [current["root"], *current["nodes"]]
        for candidate in current_nodes:
            if candidate.get("node_type") == "unresolved":
                blockers.append({"node": candidate, "reason": "unresolved dependency"})
            elif candidate.get("presence_policy") == "required" and candidate.get("present") is False:
                blockers.append({"node": candidate, "reason": "required dependency is absent"})
            elif candidate.get("graph_status") == "missing-blocker":
                blockers.append({"node": candidate, "reason": "dependency provenance is blocked"})

        historical_only_producers: list[dict[str, Any]] = []
        for candidate in current_nodes:
            candidate_id = candidate["id"]
            if not self._requires_producer(candidate):
                continue
            active_production = [
                edge for edge in self.incoming.get(candidate_id, [])
                if edge.relationship == "production"
                and edge.status == "active"
                and edge.operational_relevance
            ]
            if active_production:
                continue
            historical_production = [
                edge for edge in self.incoming.get(candidate_id, [])
                if edge.relationship == "production" and edge.provenance_relevance
            ]
            if historical_production:
                producers = [
                    self.node_view(self.nodes_by_id[edge.upstream])
                    for edge in historical_production
                    if edge.upstream in self.nodes_by_id
                ]
                historical_only_producers.extend(producers)
                blockers.append({
                    "node": candidate,
                    "reason": "only historical production is known",
                    "historical_producers": producers,
                })

        production_edges = [edge for edge in current["edges"] if edge["relationship"] == "production"]
        if blockers:
            status = "blocked"
        elif not production_edges and (
            node.raw.get("stage") == "raw" or node.raw.get("lifecycle") in {"raw", "source"}
        ):
            status = "source-origin"
        else:
            status = "rebuildable"
        return {
            "node": self.node_view(node),
            "status": status,
            "blockers": blockers,
            "historical_only_producers": sorted(
                {producer["id"]: producer for producer in historical_only_producers}.values(),
                key=_node_sort_key,
            ),
            "historical_provenance_known": bool(lineage["edges"]),
        }

    @staticmethod
    def _requires_producer(node: dict[str, Any]) -> bool:
        path = str(node.get("path") or "")
        return Path(path).name != ".gitkeep" and (
            node.get("lifecycle") in {"intermediate", "generated"}
            or node.get("stage") in {"tmp", "clean", "result", "results"}
            or path.startswith(("data/tmp/", "data/clean/", "results/"))
        )

    def orphans(self) -> dict[str, Any]:
        nodes = [
            self.node_view(node)
            for node in self.nodes_by_id.values()
            if node.state == "active"
            and not self.incoming.get(node.id)
            and not self.outgoing.get(node.id)
        ]
        return {"nodes": sorted(nodes, key=_node_sort_key)}

    def unresolved(self) -> dict[str, Any]:
        nodes = [
            self.node_view(node)
            for node in self.nodes_by_id.values()
            if node.node_type == "unresolved"
            or node.raw.get("graph_status") in {"partial-flagged", "missing-blocker"}
        ]
        return {"nodes": sorted(nodes, key=_node_sort_key)}

    def export(self) -> dict[str, Any]:
        return {
            "nodes": sorted((self.node_view(node) for node in self.nodes_by_id.values()), key=_node_sort_key),
            "edges": [self.edge_view(edge) for edge in self.edges],
            "activities": [dict(activity.raw) for activity in sorted(self.ledger.activities, key=lambda item: (item.id, item.revision_id))],
            "file_events": [self.event_view(event) for event in sorted(self.ledger.file_events, key=lambda item: (item.occurred_at, item.id))],
        }

    def _traverse(
        self,
        node: Node,
        direction: str,
        depth: int | str,
        *,
        as_of: str | None = None,
        provenance: bool = False,
        edge_filter: Callable[[Edge], bool] | None = None,
    ) -> dict[str, Any]:
        max_depth = None if depth == "all" else int(depth)
        queue: deque[tuple[str, int]] = deque([(node.id, 0)])
        visited = {node.id}
        collected_edges: dict[str, Edge] = {}
        adjacency = self.incoming if direction == "upstream" else self.outgoing
        while queue:
            current, current_depth = queue.popleft()
            if max_depth is not None and current_depth >= max_depth:
                continue
            edges = self._filtered_edges(adjacency.get(current, []), as_of=as_of)
            for edge in edges:
                if edge_filter and not edge_filter(edge):
                    continue
                if provenance and not edge.provenance_relevance:
                    continue
                neighbor = edge.upstream if direction == "upstream" else edge.downstream
                collected_edges[edge.id] = edge
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, current_depth + 1))
        visited.discard(node.id)
        nodes = [
            self.node_view(self.nodes_by_id[node_id], as_of=as_of)
            for node_id in visited
            if node_id in self.nodes_by_id
        ]
        return {
            "root": self.node_view(node, as_of=as_of),
            "direction": direction,
            "nodes": sorted(nodes, key=_node_sort_key),
            "edges": [self.edge_view(edge, as_of=as_of) for edge in sorted(collected_edges.values(), key=lambda item: (item.upstream, item.downstream, item.relationship, item.id))],
        }

    def _filtered_edges(self, edges: Iterable[Edge], *, as_of: str | None = None) -> list[Edge]:
        return [edge for edge in edges if self.edge_is_visible(edge, as_of)]

    @staticmethod
    def edge_is_visible(edge: Edge, as_of: str | None) -> bool:
        if as_of is None:
            return True
        cutoff = _as_of_time(as_of)
        valid_from = _parse_time(edge.valid_from)
        valid_to = _parse_time(edge.valid_to)
        if valid_from and valid_from > cutoff:
            return False
        if valid_to and valid_to <= cutoff:
            return False
        return True

    def _neighbors(
        self,
        edges: Iterable[Edge],
        relationships: set[str],
        as_of: str | None,
        *,
        downstream: bool = False,
    ) -> list[dict[str, Any]]:
        records = []
        for edge in edges:
            if edge.relationship not in relationships:
                continue
            node_id = edge.downstream if downstream else edge.upstream
            node = self.nodes_by_id.get(node_id)
            if node:
                records.append(self.node_view(node, as_of=as_of) | {
                    "relationship": edge.relationship,
                    "edge_status": edge.status,
                    "operational_relevance": edge.operational_relevance,
                    "valid_from": edge.valid_from,
                    "valid_to": edge.valid_to,
                })
        return sorted(records, key=_node_sort_key)

    @staticmethod
    def _is_script_node(node: dict[str, Any]) -> bool:
        path = str(node.get("path") or node.get("current_path") or node.get("last_known_path") or "")
        role = str(node.get("role", ""))
        return (
            node.get("node_type") in {"file", "symlink"}
            and (Path(path).suffix in SCRIPT_SUFFIXES or role in {"pipeline-entry", "helper-module", "producer"})
        )

    def node_view(self, node: Node, *, as_of: str | None = None) -> dict[str, Any]:
        view = dict(node.raw)
        view.setdefault("id", node.id)
        view.setdefault("node_type", node.node_type)
        if as_of:
            view["materialized_current_path"] = node.current_path
            view["materialized_state"] = node.state
            view["state"] = self.state_at(node.id, as_of)
        else:
            view.setdefault("state", node.state)
        path = self.path_at(node.id, as_of) if as_of else node.display_path
        if as_of:
            view["current_path"] = path if view["state"] == "active" else None
        view["path"] = path
        if path and node.node_type in {"file", "symlink", "expected_file"}:
            if as_of:
                view["present"] = None
                view["presence_note"] = "Historical filesystem presence is not reconstructed."
            else:
                absolute = self.ledger.root / path
                view["present"] = absolute.exists() or absolute.is_symlink()
        if not as_of and node.state == "retired" and node.last_known_path and node.raw.get("last_known_git_commit"):
            view["recovery_command"] = (
                f"git show {node.raw['last_known_git_commit']}:{node.last_known_path}"
            )
        return view

    def edge_view(self, edge: Edge, *, neighbor: str | None = None, as_of: str | None = None) -> dict[str, Any]:
        view = dict(edge.raw)
        view.update(
            {
                "id": edge.id,
                "upstream": edge.upstream,
                "downstream": edge.downstream,
                "relationship": edge.relationship,
                "status": edge.status,
                "provenance_relevance": edge.provenance_relevance,
                "operational_relevance": edge.operational_relevance,
            }
        )
        if edge.projected_from:
            view["projected_from"] = edge.projected_from
        if neighbor and neighbor in self.nodes_by_id:
            view["node"] = self.node_view(self.nodes_by_id[neighbor], as_of=as_of)
        return view

    @staticmethod
    def event_view(event: FileEvent) -> dict[str, Any]:
        return dict(event.raw)


def _string_list(value: Any) -> list[str]:
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def _node_sort_key(node: dict[str, Any]) -> tuple[str, str]:
    return (str(node.get("path") or ""), str(node.get("id") or ""))


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


def _as_of_time(value: str) -> datetime:
    parsed = _parse_time(value)
    if parsed is None:
        raise ValueError(f"invalid as-of date/time: {value}")
    if len(value) == 10:
        return datetime.combine(parsed.date(), time.max, tzinfo=timezone.utc)
    return parsed

"""Stable agent, JSON, TOML, and DOT representations for graph query results."""

from __future__ import annotations

import json
from typing import Any


def to_json(value: Any) -> str:
    return json.dumps(_plain(value), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def to_toml(value: dict[str, Any]) -> str:
    lines: list[str] = []
    _emit_table(lines, [], _plain(value), header=False)
    return "\n".join(lines).rstrip() + "\n"


def to_agent(value: Any) -> str:
    lines: list[str] = []
    _agent_lines(_compact_agent(_plain(value)), lines, 0)
    return "\n".join(lines).rstrip() + "\n"


def to_dot(value: dict[str, Any]) -> str:
    nodes = _collect_nodes(value)
    edges = _collect_edges(value)
    lines = ["digraph asset_graph {", "  rankdir=LR;"]
    for node_id, node in sorted(nodes.items()):
        path = node.get("path") or node.get("last_known_path") or node_id
        state = node.get("state", "active")
        label = f"{path}\\n[{state}]" if state != "active" else str(path)
        style = ', style="dashed"' if state == "retired" else ""
        lines.append(f'  "{_dot_escape(node_id)}" [label="{_dot_escape(label)}"{style}];')
    for edge in sorted(edges, key=lambda item: (str(item.get("upstream")), str(item.get("downstream")), str(item.get("relationship")))):
        upstream = str(edge.get("upstream", ""))
        downstream = str(edge.get("downstream", ""))
        if not upstream or not downstream:
            continue
        label = str(edge.get("relationship", ""))
        style = ', style="dashed"' if edge.get("status") == "historical" else ""
        lines.append(f'  "{_dot_escape(upstream)}" -> "{_dot_escape(downstream)}" [label="{_dot_escape(label)}"{style}];')
    lines.append("}")
    return "\n".join(lines) + "\n"


def _plain(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _compact_agent(value: Any) -> Any:
    """Keep agent output lineage-complete without repeating full attestations.

    JSON/TOML remain lossless. The default agent view carries only identity,
    path/state, relationship/temporal status, and recovery/blocker fields so a
    graph query is a compact reference rather than a manifest dump.
    """

    if isinstance(value, list):
        return [_compact_agent(item) for item in value]
    if not isinstance(value, dict):
        return value
    if isinstance(value.get("id"), str) and isinstance(value.get("node_type"), str):
        return _node_agent_summary(value)
    if all(isinstance(value.get(key), str) for key in ("id", "upstream", "downstream", "relationship")):
        parts = [
            f"{value['relationship']} [{value.get('status', 'active')}]",
            f"{value['upstream']} -> {value['downstream']}",
        ]
        if value.get("valid_from") or value.get("valid_to"):
            parts.append(f"valid={value.get('valid_from', '?')}..{value.get('valid_to') or 'open'}")
        if value.get("operational_relevance"):
            parts.append("operational")
        if value.get("projected_from"):
            parts.append(f"activity={value['projected_from']}")
        if isinstance(value.get("node"), dict):
            parts.append("neighbor=" + _node_agent_summary(value["node"]))
        return " | ".join(parts)
    if isinstance(value.get("event"), str) and isinstance(value.get("node_id"), str):
        path = value.get("to_path") or value.get("from_path") or "?"
        return f"{value['event']} | {value.get('occurred_at', '?')} | {path} | {value.get('observed_commit', '?')}"
    return {key: _compact_agent(item) for key, item in value.items()}


def _node_agent_summary(node: dict[str, Any]) -> str:
    parts = [str(node.get("id", "?"))]
    path = node.get("path") or node.get("last_known_path")
    if path:
        parts.append(str(path))
    parts.append(str(node.get("state", "active")))
    if node.get("node_type"):
        parts.append(str(node["node_type"]))
    for key in ("role", "stage", "graph_status"):
        if node.get(key):
            parts.append(f"{key}={node[key]}")
    if node.get("present") is False:
        parts.append("absent")
    if node.get("retired_at"):
        parts.append(f"retired_at={node['retired_at']}")
    if node.get("last_known_git_commit"):
        parts.append(f"git={node['last_known_git_commit']}")
    if node.get("superseded_by"):
        parts.append(f"successor={node['superseded_by']}")
    if node.get("recovery_command"):
        parts.append(f"recovery={node['recovery_command']}")
    if node.get("relationship"):
        parts.append(f"relationship={node['relationship']}[{node.get('edge_status', '?')}]" )
    return " | ".join(parts)


def _emit_table(lines: list[str], prefix: list[str], table: dict[str, Any], *, header: bool) -> None:
    if header:
        lines.extend((["", f"[{'.'.join(_toml_key(key) for key in prefix)}]"]))
    for key in sorted(table):
        value = table[key]
        if value is None or isinstance(value, dict) or _is_table_array(value):
            continue
        lines.append(f"{_toml_key(key)} = {_toml_value(value)}")
    for key in sorted(table):
        value = table[key]
        if isinstance(value, dict):
            _emit_table(lines, [*prefix, key], value, header=True)
        elif _is_table_array(value):
            for item in value:
                lines.extend(("", f"[[{'.'.join(_toml_key(part) for part in [*prefix, key])}]]"))
                _emit_array_item(lines, [*prefix, key], item)


def _emit_array_item(lines: list[str], prefix: list[str], item: dict[str, Any]) -> None:
    for key in sorted(item):
        value = item[key]
        if value is None or isinstance(value, dict) or _is_table_array(value):
            continue
        lines.append(f"{_toml_key(key)} = {_toml_value(value)}")
    for key in sorted(item):
        value = item[key]
        if isinstance(value, dict):
            _emit_table(lines, [*prefix, key], value, header=True)
        elif _is_table_array(value):
            for child in value:
                lines.extend(("", f"[[{'.'.join(_toml_key(part) for part in [*prefix, key])}]]"))
                _emit_array_item(lines, [*prefix, key], child)


def _toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return repr(value)
    if isinstance(value, list):
        return "[" + ", ".join(_toml_value(item) for item in value) + "]"
    return json.dumps(str(value), ensure_ascii=False)


def _toml_key(value: str) -> str:
    return value if value.replace("_", "a").replace("-", "a").isalnum() else json.dumps(value)


def _is_table_array(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, dict) for item in value)


def _agent_lines(value: Any, lines: list[str], indent: int) -> None:
    prefix = "  " * indent
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}{key}:")
                _agent_lines(item, lines, indent + 1)
            else:
                lines.append(f"{prefix}{key}: {item}")
    elif isinstance(value, list):
        if not value:
            lines.append(f"{prefix}(none)")
        for item in value:
            if isinstance(item, dict):
                identity = item.get("path") or item.get("id") or item.get("relationship")
                lines.append(f"{prefix}- {identity or ''}".rstrip())
                for key, child in item.items():
                    if key in {"path", "id"} and identity == child:
                        continue
                    if isinstance(child, (dict, list)):
                        lines.append(f"{prefix}  {key}:")
                        _agent_lines(child, lines, indent + 2)
                    else:
                        lines.append(f"{prefix}  {key}: {child}")
            else:
                lines.append(f"{prefix}- {item}")
    else:
        lines.append(f"{prefix}{value}")


def _collect_nodes(value: Any) -> dict[str, dict[str, Any]]:
    nodes: dict[str, dict[str, Any]] = {}
    def walk(item: Any) -> None:
        if isinstance(item, dict):
            if isinstance(item.get("id"), str) and isinstance(item.get("node_type"), str):
                nodes[item["id"]] = item
            for child in item.values():
                walk(child)
        elif isinstance(item, list):
            for child in item:
                walk(child)
    walk(value)
    return nodes


def _collect_edges(value: Any) -> list[dict[str, Any]]:
    edges: dict[str, dict[str, Any]] = {}
    def walk(item: Any) -> None:
        if isinstance(item, dict):
            if all(isinstance(item.get(key), str) for key in ("id", "upstream", "downstream", "relationship")):
                edges[item["id"]] = item
            for child in item.values():
                walk(child)
        elif isinstance(item, list):
            for child in item:
                walk(child)
    walk(value)
    return list(edges.values())


def _dot_escape(value: Any) -> str:
    return str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")

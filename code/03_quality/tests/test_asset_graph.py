"""End-to-end tests for durable Asset Graph identity, history, and queries."""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


QUALITY_DIR = Path(__file__).resolve().parents[1]
if str(QUALITY_DIR) not in sys.path:
    sys.path.insert(0, str(QUALITY_DIR))

from asset_graph_lib.cli import main as cli_main
from asset_graph_lib.formatting import to_agent, to_dot, to_json, to_toml
from asset_graph_lib.graph import AssetGraph
from asset_graph_lib.loader import load_ledger
from asset_graph_lib.validation import validate_ledger


IDS = {
    "raw": "file_00000000_0000_4000_8000_000000000001",
    "builder": "file_00000000_0000_4000_8000_000000000002",
    "helper": "file_00000000_0000_4000_8000_000000000003",
    "panel": "file_00000000_0000_4000_8000_000000000004",
    "analysis": "file_00000000_0000_4000_8000_000000000005",
    "table": "file_00000000_0000_4000_8000_000000000006",
}


def event_id(number: int) -> str:
    return f"event_00000000_0000_4000_8000_{number:012d}"


class FixtureRepository:
    def __init__(self, root: Path):
        self.root = root
        self._write("data/raw/source.csv", "firm_id,value\n1,10\n")
        self._write("code/01_build/panel_helpers.py", "def clean(value):\n    return value\n")
        self._write("data/clean/analysis_panel.parquet", "fixture panel bytes\n")
        self._write("code/02_analyze/01_estimate_models.py", "# manually inspected fixture\n")
        self._write("results/regression_table.csv", "term,estimate\nx,1.5\n")
        self._write_index()
        self._write_manifests()
        self._write_dependencies()
        self._write_history()
        self._write_assets()

    def _write(self, relative: str, content: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def append(self, relative: str, content: str) -> None:
        path = self.root / relative
        path.write_text(path.read_text(encoding="utf-8") + content, encoding="utf-8")

    def digest(self, relative: str) -> str:
        return "sha256:" + hashlib.sha256((self.root / relative).read_bytes()).hexdigest()

    def _write_index(self) -> None:
        self._write(
            "docs/data/provenance-ledger/index.toml",
            """ledger_version = 2
edge_direction = "upstream_to_downstream"
enforcement = "strict"

[governance]
mode = "tracked-plus-roots"
roots = ["code/00_fetch", "code/01_build", "code/02_analyze", "code/99_explorations", "data", "results"]
retain_retired_nodes = true
retain_historical_edges = true

[[exclusions]]
pattern = "**/__pycache__/**"
reason = "cache"

[storage]
manifests = ["docs/data/provenance-ledger/manifests/code.toml"]
dependencies = ["docs/data/provenance-ledger/dependencies/pipeline.toml"]
history = ["docs/data/provenance-ledger/history/file-events-2026.toml"]
asset_metadata_directory = "docs/data/provenance-ledger/assets"
""",
        )

    def _write_manifests(self) -> None:
        node_template = """
[[nodes]]
id = "{id}"
node_type = "file"
file_type = "{file_type}"
stage = "{stage}"
role = "{role}"
lifecycle = "{lifecycle}"
presence_policy = "required"
graph_status = "complete"
provenance_status = "{provenance_status}"
created_at = "{created_at}"
current_path = "{path}"
state = "active"
reviewed_sha256 = "{digest}"
last_reviewed = "2026-08-19"
last_known_git_commit = "abc123"
review_method = "manual-source-inspection"
inspection_profile = {profile}
inspection_evidence = "Entire fixture inspected."
"""
        records = [
            node_template.format(id=IDS["raw"], file_type="csv", stage="raw", role="source-data", lifecycle="raw", provenance_status="complete", created_at="2024-12-01T00:00:00Z", path="data/raw/source.csv", digest=self.digest("data/raw/source.csv"), profile='["metadata"]'),
            node_template.format(id=IDS["helper"], file_type="python", stage="build", role="helper-module", lifecycle="source", provenance_status="not-applicable", created_at="2024-12-01T00:00:00Z", path="code/01_build/panel_helpers.py", digest=self.digest("code/01_build/panel_helpers.py"), profile='["imports", "reads", "writes", "dynamic-paths"]'),
            node_template.format(id=IDS["panel"], file_type="parquet", stage="clean", role="intermediate-dataset", lifecycle="intermediate", provenance_status="complete", created_at="2025-02-01T00:00:00Z", path="data/clean/analysis_panel.parquet", digest=self.digest("data/clean/analysis_panel.parquet"), profile='["metadata"]'),
            node_template.format(id=IDS["analysis"], file_type="python", stage="analysis", role="pipeline-entry", lifecycle="source", provenance_status="not-applicable", created_at="2026-01-01T00:00:00Z", path="code/02_analyze/01_estimate_models.py", digest=self.digest("code/02_analyze/01_estimate_models.py"), profile='["imports", "reads", "writes", "invocations", "dynamic-paths"]'),
            node_template.format(id=IDS["table"], file_type="csv", stage="results", role="result-table", lifecycle="generated", provenance_status="complete", created_at="2026-01-01T00:00:00Z", path="results/regression_table.csv", digest=self.digest("results/regression_table.csv"), profile='["metadata"]'),
        ]
        retired = f"""
[[nodes]]
id = "{IDS['builder']}"
node_type = "file"
file_type = "python"
stage = "build"
role = "pipeline-entry"
lifecycle = "source"
presence_policy = "required"
graph_status = "complete"
provenance_status = "not-applicable"
created_at = "2025-01-01T00:00:00Z"
state = "retired"
last_known_path = "code/01_build/02_construct_analysis_panel.py"
retired_at = "2026-06-01T00:00:00Z"
last_reviewed_sha256 = "sha256:{'1' * 64}"
last_known_git_commit = "deadbeef"
superseded_by = "{IDS['analysis']}"
"""
        self._write("docs/data/provenance-ledger/manifests/code.toml", "".join(records) + retired)

    def _write_dependencies(self) -> None:
        self._write(
            "docs/data/provenance-ledger/dependencies/pipeline.toml",
            f"""
[[activities]]
id = "activity_construct_panel"
revision_id = "activity_revision_historical"
kind = "transformation"
status = "historical"
valid_from = "2025-01-01T00:00:00Z"
valid_to = "2026-06-01T00:00:00Z"
producer = "{IDS['builder']}"
reads = ["{IDS['raw']}"]
imports = ["{IDS['helper']}"]
sources = []
includes = []
configures = []
writes = ["{IDS['panel']}"]
invoked_by = []
reproduction_command = "git checkout deadbeef && make build"
graph_status = "complete"
reviewed_at = "2026-06-01"
review_method = "manual-source-inspection"
producer_sha256 = "sha256:{'1' * 64}"
producer_revision = "deadbeef"
evidence = "Historical fixture producer contract."

[[activities]]
id = "activity_estimate_models"
revision_id = "activity_revision_current"
kind = "analysis"
status = "active"
valid_from = "2026-06-01T00:00:00Z"
producer = "{IDS['analysis']}"
reads = ["{IDS['panel']}"]
imports = []
sources = []
includes = []
configures = []
writes = ["{IDS['table']}"]
invoked_by = []
reproduction_command = "make analysis"
graph_status = "complete"
reviewed_at = "2026-08-19"
review_method = "manual-source-inspection"
producer_sha256 = "{self.digest('code/02_analyze/01_estimate_models.py')}"
producer_revision = "abc123"
evidence = "Current fixture producer contract."
""",
        )

    def _write_history(self) -> None:
        created = {
            "raw": ("data/raw/source.csv", "2024-12-01T00:00:00Z"),
            "helper": ("code/01_build/panel_helpers.py", "2024-12-01T00:00:00Z"),
            "analysis": ("code/02_analyze/01_estimate_models.py", "2026-01-01T00:00:00Z"),
            "table": ("results/regression_table.csv", "2026-01-01T00:00:00Z"),
        }
        events = []
        for index, (name, (path, created_at)) in enumerate(created.items(), start=1):
            events.append(f"""
[[file_events]]
id = "event_00000000_0000_4000_8000_{index:012d}"
node_id = "{IDS[name]}"
event = "created"
occurred_at = "{created_at}"
to_path = "{path}"
observed_commit = "abc123"
""")
        events.append(f"""
[[file_events]]
id = "event_00000000_0000_4000_8000_000000000010"
node_id = "{IDS['builder']}"
event = "created"
occurred_at = "2025-01-01T00:00:00Z"
to_path = "code/01_build/01_construct_panel.py"
observed_commit = "aaa111"

[[file_events]]
id = "event_00000000_0000_4000_8000_000000000011"
node_id = "{IDS['builder']}"
event = "moved"
occurred_at = "2025-07-01T00:00:00Z"
from_path = "code/01_build/01_construct_panel.py"
to_path = "code/01_build/02_construct_analysis_panel.py"
observed_commit = "bbb222"

[[file_events]]
id = "event_00000000_0000_4000_8000_000000000012"
node_id = "{IDS['builder']}"
event = "deleted"
occurred_at = "2026-06-01T00:00:00Z"
from_path = "code/01_build/02_construct_analysis_panel.py"
observed_commit = "deadbeef"
reason = "Replaced by the current analysis path."

[[file_events]]
id = "event_00000000_0000_4000_8000_000000000013"
node_id = "{IDS['panel']}"
event = "created"
occurred_at = "2025-02-01T00:00:00Z"
to_path = "data/tmp/analysis_panel.parquet"
observed_commit = "ccc333"

[[file_events]]
id = "event_00000000_0000_4000_8000_000000000014"
node_id = "{IDS['panel']}"
event = "moved"
occurred_at = "2026-02-01T00:00:00Z"
from_path = "data/tmp/analysis_panel.parquet"
to_path = "data/clean/analysis_panel.parquet"
observed_commit = "abc123"
""")
        self._write("docs/data/provenance-ledger/history/file-events-2026.toml", "".join(events))

    def _write_assets(self) -> None:
        for name, asset_type, fmt, variable in (
            ("raw", "dataset", "csv", "firm_id"),
            ("panel", "panel", "parquet", "firm_id"),
            ("table", "table", "csv", "estimate"),
        ):
            dossier = f"docs/data/provenance-ledger/assets/asset_{name}.md"
            self._write(dossier, f"# {name} fixture provenance\n")
            self._write(
                f"docs/data/provenance-ledger/assets/asset_{name}.toml",
                f"""asset_id = "asset_{name}"
node_id = "{IDS[name]}"
asset_name = "{name}"
asset_type = "{asset_type}"
format = "{fmt}"
status = "complete"
created_or_downloaded_at = "2026-01-01T00:00:00Z"
dossier = "{dossier}"
last_updated = "2026-08-19"

[[variables]]
id = "var_{name}"
name = "{variable}"
kind = "continuous"
data_type = "string"
description = "Fixture variable."
unit = "fixture"
missing_value_codes = []
allowed_values = []
derivation = "Defined by the fixture source."
source_evidence = ["https://example.com/codebook"]
status = "complete"
""",
            )


class AssetGraphTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.fixture = FixtureRepository(self.root)
        self.ledger = load_ledger(self.root)
        self.graph = AssetGraph(self.ledger)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_fixture_is_strictly_valid(self) -> None:
        findings = validate_ledger(self.ledger)
        self.assertEqual([], findings, [finding.to_dict() for finding in findings])

    def test_activity_projection_and_reverse_adjacency(self) -> None:
        panel = self.graph.show(IDS["panel"])
        upstream = {(edge["upstream"], edge["relationship"]) for edge in panel["immediate_upstream"]}
        self.assertIn((IDS["builder"], "production"), upstream)
        self.assertIn((IDS["raw"], "generation_input"), upstream)
        self.assertIn((IDS["helper"], "generation_code"), upstream)
        downstream = {(edge["downstream"], edge["relationship"]) for edge in panel["immediate_downstream"]}
        self.assertIn((IDS["analysis"], "data_read"), downstream)
        self.assertIn((IDS["table"], "generation_input"), downstream)

    def test_retired_producer_remains_in_lineage_and_blocks_rebuild(self) -> None:
        producer_ids = {node["id"] for node in self.graph.producers(IDS["panel"])["producers"]}
        self.assertEqual({IDS["builder"], IDS["helper"]}, producer_ids)
        retired = next(node for node in self.graph.producers(IDS["panel"])["producers"] if node["id"] == IDS["builder"])
        self.assertEqual("retired", retired["state"])
        self.assertIn("git show deadbeef:", retired["recovery_command"])
        rebuild = self.graph.rebuildability(IDS["panel"])
        self.assertEqual("blocked", rebuild["status"])
        historical_ids = {
            producer["id"]
            for item in rebuild["blockers"]
            for producer in item.get("historical_producers", [])
        }
        self.assertIn(IDS["builder"], historical_ids)

    def test_move_preserves_id_and_as_of_path(self) -> None:
        history = self.graph.path_history(IDS["panel"])
        self.assertEqual(IDS["panel"], history["node"]["id"])
        self.assertEqual("data/tmp/analysis_panel.parquet", self.graph.path_at(IDS["panel"], "2025-12-31"))
        self.assertEqual("data/clean/analysis_panel.parquet", self.graph.path_at(IDS["panel"], "2026-08-19"))
        self.assertEqual(IDS["panel"], self.graph.resolve("data/tmp/analysis_panel.parquet").id)

    def test_raw_sources_and_historical_impact(self) -> None:
        sources = self.graph.raw_sources(IDS["table"])["sources"]
        self.assertEqual([IDS["raw"]], [node["id"] for node in sources])
        current_impact = {node["id"] for node in self.graph.impact(IDS["helper"])["nodes"]}
        self.assertEqual(set(), current_impact)
        historical_impact = {node["id"] for node in self.graph.impact(IDS["helper"], include_historical=True)["nodes"]}
        self.assertTrue({IDS["builder"], IDS["panel"], IDS["analysis"], IDS["table"]}.issubset(historical_impact))

    def test_script_io(self) -> None:
        io_record = self.graph.script_io(IDS["analysis"])
        self.assertEqual([IDS["panel"]], [node["id"] for node in io_record["reads"]])
        self.assertEqual([IDS["table"]], [node["id"] for node in io_record["writes"]])
        historical = self.graph.script_io(IDS["builder"])
        self.assertEqual([], historical["reads"])
        self.assertEqual([IDS["raw"]], [node["id"] for node in historical["historical_reads"]])

    def test_as_of_reconstructs_state_without_claiming_historical_presence(self) -> None:
        historical = self.graph.show(IDS["builder"], as_of="2025-12-31")["node"]
        self.assertEqual("active", historical["state"])
        self.assertEqual("code/01_build/02_construct_analysis_panel.py", historical["current_path"])
        self.assertIsNone(historical["present"])
        self.assertEqual("retired", self.graph.show(IDS["builder"])["node"]["state"])

    def test_restoration_reactivates_the_same_identity(self) -> None:
        self.fixture.append(
            "docs/data/provenance-ledger/history/file-events-2026.toml",
            f"""
[[file_events]]
id = "{event_id(20)}"
node_id = "{IDS['helper']}"
event = "deleted"
occurred_at = "2026-03-01T00:00:00Z"
from_path = "code/01_build/panel_helpers.py"
observed_commit = "ddd444"
reason = "Temporary removal in the fixture."

[[file_events]]
id = "{event_id(21)}"
node_id = "{IDS['helper']}"
event = "restored"
occurred_at = "2026-04-01T00:00:00Z"
to_path = "code/01_build/panel_helpers.py"
observed_commit = "eee555"
""",
        )
        graph = AssetGraph(load_ledger(self.root))
        self.assertIsNone(graph.path_at(IDS["helper"], "2026-03-15"))
        self.assertEqual("code/01_build/panel_helpers.py", graph.path_at(IDS["helper"], "2026-04-15"))
        self.assertEqual(IDS["helper"], graph.resolve("code/01_build/panel_helpers.py").id)
        self.assertEqual([], validate_ledger(load_ledger(self.root)))

    def test_path_reuse_gets_a_new_identity_and_overlap_is_rejected(self) -> None:
        replacement_id = "file_00000000_0000_4000_8000_000000000007"
        replacement_path = "code/01_build/02_construct_analysis_panel.py"
        self.fixture._write(replacement_path, "# unrelated replacement\n")
        digest = self.fixture.digest(replacement_path)
        self.fixture.append(
            "docs/data/provenance-ledger/manifests/code.toml",
            f"""
[[nodes]]
id = "{replacement_id}"
node_type = "file"
file_type = "python"
stage = "build"
role = "helper-module"
lifecycle = "source"
presence_policy = "required"
graph_status = "complete"
provenance_status = "not-applicable"
created_at = "2026-07-01T00:00:00Z"
current_path = "{replacement_path}"
state = "active"
reviewed_sha256 = "{digest}"
last_reviewed = "2026-08-19"
last_known_git_commit = "fff666"
review_method = "manual-source-inspection"
inspection_profile = ["imports", "reads", "writes"]
inspection_evidence = "Entire replacement fixture inspected."
""",
        )
        self.fixture.append(
            "docs/data/provenance-ledger/history/file-events-2026.toml",
            f"""
[[file_events]]
id = "{event_id(22)}"
node_id = "{replacement_id}"
event = "created"
occurred_at = "2026-07-01T00:00:00Z"
to_path = "{replacement_path}"
observed_commit = "fff666"
""",
        )
        ledger = load_ledger(self.root)
        self.assertEqual([], validate_ledger(ledger))
        graph = AssetGraph(ledger)
        self.assertEqual(replacement_id, graph.resolve(replacement_path).id)
        self.assertEqual(IDS["builder"], graph.resolve(replacement_path, as_of="2026-05-01").id)

        history_path = self.root / "docs/data/provenance-ledger/history/file-events-2026.toml"
        history_path.write_text(history_path.read_text(encoding="utf-8").replace(
            'occurred_at = "2026-07-01T00:00:00Z"\nto_path = "code/01_build/02_construct_analysis_panel.py"',
            'occurred_at = "2026-05-01T00:00:00Z"\nto_path = "code/01_build/02_construct_analysis_panel.py"',
        ), encoding="utf-8")
        findings = validate_ledger(load_ledger(self.root))
        self.assertTrue(any(finding.code == "overlapping_path_identity" for finding in findings))

    def test_active_replacement_makes_current_output_rebuildable(self) -> None:
        replacement_id = "file_00000000_0000_4000_8000_000000000008"
        path = "code/01_build/03_construct_panel.py"
        self.fixture._write(path, "# current builder\n")
        digest = self.fixture.digest(path)
        self.fixture.append("docs/data/provenance-ledger/manifests/code.toml", f"""
[[nodes]]
id = "{replacement_id}"
node_type = "file"
file_type = "python"
stage = "build"
role = "pipeline-entry"
lifecycle = "source"
presence_policy = "required"
graph_status = "complete"
provenance_status = "not-applicable"
created_at = "2026-06-01T00:00:00Z"
current_path = "{path}"
state = "active"
reviewed_sha256 = "{digest}"
last_reviewed = "2026-08-19"
last_known_git_commit = "abc999"
review_method = "manual-source-inspection"
inspection_profile = ["imports", "reads", "writes"]
inspection_evidence = "Entire current builder fixture inspected."
""")
        self.fixture.append("docs/data/provenance-ledger/history/file-events-2026.toml", f"""
[[file_events]]
id = "{event_id(23)}"
node_id = "{replacement_id}"
event = "created"
occurred_at = "2026-06-01T00:00:00Z"
to_path = "{path}"
observed_commit = "abc999"
""")
        self.fixture.append("docs/data/provenance-ledger/dependencies/pipeline.toml", f"""
[[activities]]
id = "activity_construct_panel"
revision_id = "activity_revision_replacement"
kind = "transformation"
status = "active"
valid_from = "2026-06-01T00:00:00Z"
producer = "{replacement_id}"
reads = ["{IDS['raw']}"]
imports = ["{IDS['helper']}"]
sources = []
includes = []
configures = []
writes = ["{IDS['panel']}"]
invoked_by = []
reproduction_command = "make build"
producer_sha256 = "{digest}"
producer_revision = "abc999"
graph_status = "complete"
reviewed_at = "2026-08-19"
review_method = "manual-source-inspection"
evidence = "Replacement builder fixture contract."
""")
        ledger = load_ledger(self.root)
        self.assertEqual([], validate_ledger(ledger))
        rebuild = AssetGraph(ledger).rebuildability(IDS["panel"])
        self.assertEqual("rebuildable", rebuild["status"])
        self.assertEqual([], rebuild["blockers"])

    def test_json_toml_and_dot_are_deterministic_and_parseable(self) -> None:
        result = self.graph.show(IDS["panel"])
        self.assertEqual(to_json(result), to_json(result))
        parsed = tomllib.loads(to_toml(result))
        self.assertEqual(IDS["panel"], parsed["node"]["id"])
        dot = to_dot(self.graph.lineage(IDS["table"]))
        self.assertIn("digraph asset_graph", dot)
        self.assertIn(IDS["builder"], dot)
        compact = to_agent(result)
        self.assertLess(len(compact.splitlines()), 80)
        self.assertIn(IDS["panel"], compact)

    def test_stale_graph_fails_query_and_hook_json_identifies_path(self) -> None:
        (self.root / "data/raw/source.csv").write_text("changed\n", encoding="utf-8")
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            query_code = cli_main(["--root", str(self.root), "show", IDS["table"], "--format", "json"])
        self.assertEqual(3, query_code)
        query_error = json.loads(stderr.getvalue())
        self.assertEqual("stale", query_error["status"])
        self.assertTrue(any(item["code"] == "hash_mismatch" for item in query_error["findings"]))

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            validate_code = cli_main(["--root", str(self.root), "validate", "--format", "json", "--hook"])
        self.assertEqual(2, validate_code)
        hook = json.loads(stdout.getvalue())
        mismatch = next(item for item in hook["findings"] if item["code"] == "hash_mismatch")
        self.assertEqual("data/raw/source.csv", mismatch["path"])
        self.assertTrue(mismatch["stale"])

    def test_structural_error_fails_queries(self) -> None:
        self.fixture.append("docs/data/provenance-ledger/dependencies/pipeline.toml", f"""
[[edges]]
id = "edge_00000000_0000_4000_8000_000000000001"
upstream = "{IDS['raw']}"
downstream = "file_00000000_0000_4000_8000_999999999999"
relationship = "documentation"
edge_class = "contextual"
valid_from = "2026-01-01T00:00:00Z"
status = "active"
provenance_relevance = true
operational_relevance = false
evidence = "Intentional invalid endpoint fixture."
""")
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = cli_main(["--root", str(self.root), "show", IDS["table"], "--format", "json"])
        self.assertEqual(4, code)
        payload = json.loads(stderr.getvalue())
        self.assertEqual("invalid", payload["status"])
        self.assertFalse(payload["authoritative"])
        self.assertTrue(any(item["code"] == "unknown_edge_node" for item in payload["findings"]))

    def test_query_carries_declared_provenance_warnings(self) -> None:
        dependency = self.root / "docs/data/provenance-ledger/dependencies/pipeline.toml"
        dependency.write_text(dependency.read_text(encoding="utf-8").replace(
            'graph_status = "complete"', 'graph_status = "partial-flagged"', 1,
        ), encoding="utf-8")
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = cli_main(["--root", str(self.root), "show", IDS["table"], "--format", "json"])
        self.assertEqual(0, code)
        payload = json.loads(stdout.getvalue())
        self.assertFalse(payload["authoritative"])
        self.assertTrue(any(
            finding["code"] == "incomplete_activity_provenance"
            for finding in payload["validation_warnings"]
        ))
        self.assertEqual(IDS["table"], payload["result"]["node"]["id"])

    def test_missing_asset_overlay_and_missing_blocker_are_reported(self) -> None:
        (self.root / "docs/data/provenance-ledger/assets/asset_panel.toml").unlink()
        findings = validate_ledger(load_ledger(self.root))
        missing = next(finding for finding in findings if finding.code == "missing_asset_overlay")
        self.assertTrue(missing.stale)

        self.fixture._write_assets()
        asset_path = self.root / "docs/data/provenance-ledger/assets/asset_panel.toml"
        asset_path.write_text(
            asset_path.read_text(encoding="utf-8").replace('status = "complete"', 'status = "missing-blocker"', 1),
            encoding="utf-8",
        )
        findings = validate_ledger(load_ledger(self.root))
        self.assertTrue(any(finding.code == "incomplete_asset_provenance" and finding.severity == "error" for finding in findings))

        self.fixture._write_assets()
        asset_text = asset_path.read_text(encoding="utf-8")
        variable_status = asset_text.rfind('status = "complete"')
        asset_path.write_text(
            asset_text[:variable_status] + 'status = "missing-blocker"' + asset_text[variable_status + len('status = "complete"'):],
            encoding="utf-8",
        )
        findings = validate_ledger(load_ledger(self.root))
        self.assertTrue(any(finding.code == "incomplete_variable_provenance" and finding.severity == "error" for finding in findings))

        self.fixture._write_assets()
        asset_text = asset_path.read_text(encoding="utf-8")
        asset_path.write_text(asset_text.replace(
            'description = "Fixture variable."', 'description = ""', 1,
        ), encoding="utf-8")
        self.assertTrue(any(
            finding.code == "empty_variable_field"
            for finding in validate_ledger(load_ledger(self.root))
        ))

        self.fixture._write_assets()
        self.fixture._write("docs/data/provenance-ledger/assets/asset_panel.md", "   \n")
        self.assertTrue(any(
            finding.code == "empty_asset_dossier"
            for finding in validate_ledger(load_ledger(self.root))
        ))

        self.fixture._write_assets()
        asset_text = asset_path.read_text(encoding="utf-8")
        asset_text = asset_text.replace('asset_type = "panel"', 'asset_type = "binary-blob"', 1)
        asset_text = asset_text.replace('format = "parquet"', 'format = "opaque"', 1)
        asset_path.write_text(asset_text.split("\n[[variables]]", 1)[0] + "\n", encoding="utf-8")
        findings = validate_ledger(load_ledger(self.root))
        self.assertTrue(any(finding.code == "asset_format_mismatch" for finding in findings))
        self.assertTrue(any(finding.code == "structured_asset_without_variables" for finding in findings))

        self.fixture._write_assets()
        asset_text = asset_path.read_text(encoding="utf-8")
        variable_block = asset_text[asset_text.index("[[variables]]"):]
        asset_path.write_text(asset_text + "\n" + variable_block, encoding="utf-8")
        findings = validate_ledger(load_ledger(self.root))
        self.assertTrue(any(finding.code == "duplicate_variable_id" for finding in findings))
        self.assertTrue(any(finding.code == "duplicate_variable_name" for finding in findings))

    def test_symlink_has_own_identity_alias_edge_and_link_hash(self) -> None:
        target_id = "file_00000000_0000_4000_8000_000000000009"
        link_id = "symlink_00000000_0000_4000_8000_000000000010"
        target_path = "code/01_build/helper_target.py"
        link_path = "code/01_build/helper_alias.py"
        self.fixture._write(target_path, "# target helper\n")
        (self.root / link_path).symlink_to("helper_target.py")
        target_digest = self.fixture.digest(target_path)
        link_digest = "sha256:" + hashlib.sha256(b"helper_target.py").hexdigest()
        self.fixture.append("docs/data/provenance-ledger/manifests/code.toml", f"""
[[nodes]]
id = "{target_id}"
node_type = "file"
file_type = "python"
stage = "build"
role = "helper-module"
lifecycle = "source"
presence_policy = "required"
graph_status = "complete"
provenance_status = "not-applicable"
created_at = "2026-08-01T00:00:00Z"
current_path = "{target_path}"
state = "active"
reviewed_sha256 = "{target_digest}"
last_reviewed = "2026-08-19"
last_known_git_commit = "target1"
review_method = "manual-source-inspection"
inspection_profile = ["imports", "reads", "writes"]
inspection_evidence = "Target fixture inspected."

[[nodes]]
id = "{link_id}"
node_type = "symlink"
file_type = "symlink"
stage = "build"
role = "alias"
lifecycle = "source"
presence_policy = "required"
graph_status = "complete"
provenance_status = "not-applicable"
created_at = "2026-08-01T00:00:01Z"
current_path = "{link_path}"
state = "active"
reviewed_sha256 = "{link_digest}"
last_reviewed = "2026-08-19"
last_known_git_commit = "target1"
review_method = "manual-source-inspection"
inspection_profile = ["alias-target"]
inspection_evidence = "Symlink target inspected."
""")
        self.fixture.append("docs/data/provenance-ledger/history/file-events-2026.toml", f"""
[[file_events]]
id = "{event_id(24)}"
node_id = "{target_id}"
event = "created"
occurred_at = "2026-08-01T00:00:00Z"
to_path = "{target_path}"
observed_commit = "target1"

[[file_events]]
id = "{event_id(25)}"
node_id = "{link_id}"
event = "created"
occurred_at = "2026-08-01T00:00:01Z"
to_path = "{link_path}"
observed_commit = "target1"
""")
        self.fixture.append("docs/data/provenance-ledger/dependencies/pipeline.toml", f"""
[[edges]]
id = "edge_00000000_0000_4000_8000_000000000002"
upstream = "{target_id}"
downstream = "{link_id}"
relationship = "alias"
edge_class = "structural"
valid_from = "2026-08-01T00:00:01Z"
status = "active"
provenance_relevance = true
operational_relevance = false
evidence = "The symlink text names the registered target."
""")
        self.assertEqual([], validate_ledger(load_ledger(self.root)))
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = cli_main(["--root", str(self.root), "hash", link_path])
        self.assertEqual(0, code)
        self.assertEqual(link_digest, stdout.getvalue().strip())

    def test_expected_output_can_be_absent_and_appearance_is_stale(self) -> None:
        expected_id = "expected_file_00000000_0000_4000_8000_000000000011"
        expected_path = "results/expected_table.csv"
        self.fixture.append("docs/data/provenance-ledger/manifests/code.toml", f"""
[[nodes]]
id = "{expected_id}"
node_type = "expected_file"
file_type = "csv"
stage = "results"
role = "result-table"
lifecycle = "generated"
presence_policy = "expected-output"
last_observed_presence = "absent"
graph_status = "complete"
provenance_status = "complete"
created_at = "2026-08-19T00:00:00Z"
current_path = "{expected_path}"
state = "active"
last_reviewed = "2026-08-19"
last_known_git_commit = "abc123"
review_method = "manual-contract-inspection"
inspection_profile = ["expected-output"]
inspection_evidence = "Declared output of the analysis activity."
""")
        self.fixture.append("docs/data/provenance-ledger/history/file-events-2026.toml", f"""
[[file_events]]
id = "{event_id(26)}"
node_id = "{expected_id}"
event = "created"
occurred_at = "2026-08-19T00:00:00Z"
to_path = "{expected_path}"
observed_commit = "abc123"
""")
        dependency_path = self.root / "docs/data/provenance-ledger/dependencies/pipeline.toml"
        dependency_path.write_text(dependency_path.read_text(encoding="utf-8").replace(
            f'writes = ["{IDS["table"]}"]',
            f'writes = ["{IDS["table"]}", "{expected_id}"]',
        ), encoding="utf-8")
        dossier = "docs/data/provenance-ledger/assets/asset_expected.md"
        self.fixture._write(dossier, "# Expected table\n")
        self.fixture._write("docs/data/provenance-ledger/assets/asset_expected.toml", f"""asset_id = "asset_expected"
node_id = "{expected_id}"
asset_name = "Expected table"
asset_type = "table"
format = "csv"
status = "complete"
created_or_downloaded_at = "2026-08-19T00:00:00Z"
dossier = "{dossier}"
last_updated = "2026-08-19"

[[variables]]
id = "var_expected"
name = "estimate"
kind = "continuous"
data_type = "float"
description = "Expected estimate."
unit = "coefficient"
missing_value_codes = []
allowed_values = []
derivation = "Produced by the fixture analysis."
source_evidence = ["https://example.com/codebook"]
status = "complete"
""")
        self.assertEqual([], validate_ledger(load_ledger(self.root)))
        self.fixture._write(expected_path, "estimate\n1.0\n")
        findings = validate_ledger(load_ledger(self.root))
        self.assertTrue(any(finding.code == "expected_output_appeared" and finding.stale for finding in findings))

    def test_shared_hook_reports_and_blocks_on_stale_graph(self) -> None:
        repository_root = QUALITY_DIR.parents[1]
        self.fixture._write("AGENTS.md", "# Fixture project\n")
        quality = self.root / "code/03_quality"
        quality.mkdir(parents=True, exist_ok=True)
        (quality / "asset_graph.py").symlink_to(repository_root / "code/03_quality/asset_graph.py")
        (quality / "asset_graph_lib").symlink_to(repository_root / "code/03_quality/asset_graph_lib", target_is_directory=True)
        (self.root / "data/raw/source.csv").write_text("changed outside the agent\n", encoding="utf-8")
        hook = repository_root / ".agents/hooks/provenance-reminder.py"

        prompt_result = subprocess.run(
            [sys.executable, str(hook)],
            cwd=self.root,
            input=json.dumps({"hook_event_name": "UserPromptSubmit", "cwd": str(self.root)}),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, prompt_result.returncode)
        prompt_payload = json.loads(prompt_result.stdout)
        self.assertIn("ASSET GRAPH MAINTENANCE REQUIRED", prompt_payload["hookSpecificOutput"]["additionalContext"])

        stop_result = subprocess.run(
            [sys.executable, str(hook)],
            cwd=self.root,
            input=json.dumps({"hook_event_name": "Stop", "cwd": str(self.root), "stop_hook_active": False}),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, stop_result.returncode)
        stop_payload = json.loads(stop_result.stdout)
        self.assertEqual("block", stop_payload["decision"])

    def test_shared_hook_honors_governed_tool_workdir(self) -> None:
        repository_root = QUALITY_DIR.parents[1]
        self.fixture._write("AGENTS.md", "# Fixture project\n")
        quality = self.root / "code/03_quality"
        quality.mkdir(parents=True, exist_ok=True)
        (quality / "asset_graph.py").symlink_to(repository_root / "code/03_quality/asset_graph.py")
        (quality / "asset_graph_lib").symlink_to(repository_root / "code/03_quality/asset_graph_lib", target_is_directory=True)
        self.fixture._write("data/raw/new.csv", "x\n1\n")
        hook = repository_root / ".agents/hooks/provenance-reminder.py"
        result = subprocess.run(
            [sys.executable, str(hook)],
            cwd=self.root,
            input=json.dumps({
                "hook_event_name": "PostToolUse",
                "cwd": str(self.root),
                "tool_input": {"cmd": "touch new.csv", "workdir": str(self.root / "data/raw")},
            }),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertIn("ASSET GRAPH MAINTENANCE REQUIRED", payload["hookSpecificOutput"]["additionalContext"])

    def test_invalid_policy_and_malformed_registry_fail_validation(self) -> None:
        index = self.root / "docs/data/provenance-ledger/index.toml"
        index.write_text(index.read_text(encoding="utf-8").replace(
            'edge_direction = "upstream_to_downstream"', 'edge_direction = "sideways"',
        ), encoding="utf-8")
        self.fixture._write("docs/data/provenance-ledger/manifests/code.toml", 'nodes = "not-an-array"\n')
        findings = validate_ledger(load_ledger(self.root))
        self.assertTrue(any(finding.code == "invalid_edge_direction" for finding in findings))
        self.assertTrue(any(finding.code == "load_error" and "nodes must be an array" in finding.message for finding in findings))

    def test_strict_semantic_contract_guards(self) -> None:
        manifest = self.root / "docs/data/provenance-ledger/manifests/code.toml"
        dependency = self.root / "docs/data/provenance-ledger/dependencies/pipeline.toml"
        history = self.root / "docs/data/provenance-ledger/history/file-events-2026.toml"
        manifest_original = manifest.read_text(encoding="utf-8")
        dependency_original = dependency.read_text(encoding="utf-8")
        history_original = history.read_text(encoding="utf-8")

        manifest.write_text(manifest_original.replace(
            'presence_policy = "required"', 'presence_policy = "expected-output"', 1,
        ), encoding="utf-8")
        self.assertTrue(any(
            finding.code == "invalid_presence_policy"
            for finding in validate_ledger(load_ledger(self.root))
        ))

        manifest.write_text(manifest_original.replace(
            'provenance_status = "complete"', 'provenance_status = "missing-blocker"', 1,
        ), encoding="utf-8")
        self.assertTrue(any(
            finding.code == "incomplete_node_provenance" and finding.severity == "error"
            for finding in validate_ledger(load_ledger(self.root))
        ))

        manifest.write_text(manifest_original.replace(
            f'id = "{IDS["raw"]}"',
            'id = "symlink_00000000_0000_4000_8000_000000000001"',
            1,
        ), encoding="utf-8")
        self.assertTrue(any(
            finding.code == "node_id_type_mismatch"
            for finding in validate_ledger(load_ledger(self.root))
        ))

        manifest.write_text(manifest_original.replace(
            'last_known_git_commit = "deadbeef"', 'last_known_git_commit = 123', 1,
        ), encoding="utf-8")
        history.write_text(history_original.replace(
            'observed_commit = "deadbeef"', 'observed_commit = 123', 1,
        ), encoding="utf-8")
        findings = validate_ledger(load_ledger(self.root))
        self.assertTrue(any(finding.code == "invalid_git_revision" for finding in findings))
        self.assertTrue(any(finding.code == "missing_event_revision" for finding in findings))

        manifest.write_text(manifest_original, encoding="utf-8")
        history.write_text(history_original, encoding="utf-8")
        dependency.write_text(dependency_original.replace(
            'graph_status = "complete"', 'graph_status = "missing-blocker"', 1,
        ), encoding="utf-8")
        self.assertTrue(any(
            finding.code == "incomplete_activity_provenance" and finding.severity == "error"
            for finding in validate_ledger(load_ledger(self.root))
        ))

        manifest.write_text(manifest_original.replace(
            'review_method = "manual-source-inspection"',
            'review_method = "automated-parser"',
        ), encoding="utf-8")
        dependency.write_text(dependency_original.replace(
            'review_method = "manual-source-inspection"',
            'review_method = "automated-parser"',
        ), encoding="utf-8")
        self.assertTrue(any(
            finding.code == "invalid_manual_review"
            for finding in validate_ledger(load_ledger(self.root))
        ))

        manifest.write_text(manifest_original, encoding="utf-8")

        dependency.write_text(dependency_original.replace(
            'valid_to = "2026-06-01T00:00:00Z"',
            'valid_to = "2025-01-15T00:00:00Z"',
            1,
        ), encoding="utf-8")
        self.assertTrue(any(
            finding.code == "activity_output_outside_lifetime"
            for finding in validate_ledger(load_ledger(self.root))
        ))

        dependency.write_text(dependency_original + f"""
[[edges]]
id = "edge_00000000_0000_4000_8000_000000000005"
upstream = "{IDS['analysis']}"
downstream = "{IDS['panel']}"
relationship = "production"
edge_class = "causal"
valid_from = "2026-06-01T00:00:00Z"
status = "active"
provenance_relevance = true
operational_relevance = true
evidence = "Intentional invalid authored production edge."
""", encoding="utf-8")
        self.assertTrue(any(
            finding.code == "authored_activity_relationship"
            for finding in validate_ledger(load_ledger(self.root))
        ))

        dependency.write_text(dependency_original, encoding="utf-8")
        history.write_text(history_original.replace(
            'occurred_at = "2026-02-01T00:00:00Z"',
            'occurred_at = "2025-02-01T00:00:00Z"',
            1,
        ), encoding="utf-8")
        self.assertTrue(any(
            finding.code == "ambiguous_event_order"
            for finding in validate_ledger(load_ledger(self.root))
        ))

    def test_virtual_node_contracts_support_patterns_sources_and_logical_assets(self) -> None:
        source_id = "external_source_00000000_0000_4000_8000_000000000012"
        pattern_id = "pattern_00000000_0000_4000_8000_000000000013"
        logical_id = "logical_asset_00000000_0000_4000_8000_000000000014"
        self.fixture.append("docs/data/provenance-ledger/manifests/code.toml", f"""
[[nodes]]
id = "{source_id}"
node_type = "external_source"
state = "active"
graph_status = "complete"
provenance_status = "complete"
created_at = "2024-01-01T00:00:00Z"
source_uri = "https://example.com/source"

[[nodes]]
id = "{pattern_id}"
node_type = "pattern"
state = "active"
graph_status = "complete"
provenance_status = "complete"
created_at = "2026-08-19T00:00:00Z"
pattern = "*.csv"
base_path = "data/raw"
resolution_status = "resolved"
matches = ["{IDS['raw']}"]

[[nodes]]
id = "{logical_id}"
node_type = "logical_asset"
state = "active"
graph_status = "complete"
provenance_status = "complete"
created_at = "2026-08-19T00:00:00Z"
""")
        self.fixture.append("docs/data/provenance-ledger/dependencies/pipeline.toml", f"""
[[edges]]
id = "edge_00000000_0000_4000_8000_000000000003"
upstream = "{IDS['raw']}"
downstream = "{logical_id}"
relationship = "membership"
edge_class = "organizational"
valid_from = "2026-08-19T00:00:00Z"
status = "active"
provenance_relevance = true
operational_relevance = false
evidence = "The logical collection contains the registered raw file."

[[edges]]
id = "edge_00000000_0000_4000_8000_000000000004"
upstream = "{IDS['raw']}"
downstream = "{pattern_id}"
relationship = "membership"
edge_class = "organizational"
valid_from = "2026-08-19T00:00:00Z"
status = "active"
provenance_relevance = true
operational_relevance = false
evidence = "The manually resolved glob contains the registered raw file."
""")
        dossier = "docs/data/provenance-ledger/assets/asset_logical.md"
        self.fixture._write(dossier, "# Logical collection\n")
        self.fixture._write("docs/data/provenance-ledger/assets/asset_logical.toml", f"""asset_id = "asset_logical"
node_id = "{logical_id}"
asset_name = "Logical collection"
asset_type = "dataset"
format = "csv"
status = "complete"
created_or_downloaded_at = "2026-08-19T00:00:00Z"
dossier = "{dossier}"
last_updated = "2026-08-19"

[[variables]]
id = "var_logical"
name = "firm_id"
kind = "identifier"
data_type = "string"
description = "Logical fixture identifier."
unit = "firm"
missing_value_codes = []
allowed_values = []
derivation = "Inherited from the member file."
source_evidence = ["https://example.com/codebook"]
status = "complete"
""")
        self.assertEqual([], validate_ledger(load_ledger(self.root)))
        manifest = self.root / "docs/data/provenance-ledger/manifests/code.toml"
        manifest.write_text(manifest.read_text(encoding="utf-8").replace(
            'pattern = "*.csv"', 'pattern = "../../docs/*"', 1,
        ), encoding="utf-8")
        self.assertTrue(any(
            finding.code == "unsafe_pattern"
            for finding in validate_ledger(load_ledger(self.root))
        ))

    def test_docs_are_outside_coverage_and_new_data_is_not(self) -> None:
        self.fixture._write("docs/ignored.md", "not in graph scope\n")
        self.assertFalse(any(finding.path == "docs/ignored.md" for finding in validate_ledger(load_ledger(self.root))))
        self.fixture._write("data/raw/new.csv", "x\n1\n")
        findings = validate_ledger(load_ledger(self.root))
        self.assertTrue(any(finding.code == "coverage_missing" and finding.path == "data/raw/new.csv" for finding in findings))

    def test_hash_match_suggests_move_without_reassigning_id(self) -> None:
        old = self.root / "code/01_build/panel_helpers.py"
        new = self.root / "code/01_build/moved_helpers.py"
        old.rename(new)
        findings = validate_ledger(load_ledger(self.root), hook=True)
        self.assertTrue(any(finding.code == "candidate_move" and finding.node_id == IDS["helper"] for finding in findings))
        self.assertEqual(IDS["helper"], self.graph.resolve("code/01_build/panel_helpers.py").id)


if __name__ == "__main__":
    unittest.main()

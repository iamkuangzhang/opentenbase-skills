import importlib.util
import contextlib
import io
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "system-entry" / "scripts" / "discover_environment.py"
spec = importlib.util.spec_from_file_location("discover_environment", SCRIPT)
discover = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(discover)


class DiscoverEnvironmentTests(unittest.TestCase):
    def test_plain_postgresql_versions_do_not_prove_opentenbase(self):
        result = discover.detection_summary(
            server_version="PostgreSQL 16.3 on x86_64-pc-linux-gnu",
            psql_version="psql (PostgreSQL) 16.3",
            postgres_binary_version="postgres (PostgreSQL) 16.3",
            pg_config_version="PostgreSQL 16.3",
            config_paths=[],
            processes=[],
            topology={"coordinators": [], "datanodes": [], "gtm": []},
        )
        self.assertFalse(result["detected"])
        self.assertEqual(result["confidence"], "none")
        self.assertIn("仅发现 PostgreSQL 工具版本", result["evidence"][0])

    def test_server_version_proves_opentenbase_with_high_confidence(self):
        result = discover.detection_summary(
            server_version="PostgreSQL 11.0 @ OpenTenBase_v5.21.8.11",
            psql_version="psql (PostgreSQL) 11.0",
            postgres_binary_version="unknown",
            pg_config_version="unknown",
            config_paths=[],
            processes=[],
            topology={"coordinators": [], "datanodes": [], "gtm": []},
        )
        self.assertTrue(result["detected"])
        self.assertEqual(result["confidence"], "high")

    def test_port_lines_are_not_cn_candidates(self):
        rows = [{"line": "LISTEN 0 244 127.0.0.1:30004 0.0.0.0:* users:(('postgres',pid=1,fd=3))"}]
        self.assertEqual(discover.listener_ports(rows), set())
        rows = [{"line": "LISTEN 0 244 127.0.0.1:30004 0.0.0.0:* users:(('postgres',pid=1,fd=3))", "ports": ["30004"]}]
        self.assertEqual(discover.listener_ports(rows), {"30004"})
        self.assertFalse(hasattr(discover, "coordinator_candidates_from_ports"))

    def test_parse_pgxc_config_roles(self):
        text = """
coordNames=(coord1 coord2)
coordMasterServers=(otb130 otb132)
coordPorts=(30004 30005)
datanodeNames=(dn1 dn2)
datanodeMasterServers=(otb130 otb132)
datanodePorts=(40004 40005)
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pgxc_ctl.conf"
            path.write_text(text, encoding="utf-8")
            parsed = discover.parse_pgxc_configs([str(path)])
        self.assertEqual(len(parsed["coordinators"]), 2)
        self.assertEqual(len(parsed["datanodes"]), 2)
        self.assertEqual(parsed["coordinators"][0]["port"], "30004")

    def test_command_record_contains_timing_and_purpose(self):
        result = discover.command_record(["python", "-c", "print('ok')"], purpose="测试命令证据")
        self.assertEqual(result["returncode"], 0)
        self.assertEqual(result["stdout"], "ok")
        self.assertEqual(result["purpose"], "测试命令证据")
        self.assertIn("duration_ms", result)
        self.assertIn("started_at", result)
        self.assertIn("finished_at", result)

    def test_parse_args_requires_host_and_port_together(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                discover.parse_args(["--cn-host", "127.0.0.1"])


if __name__ == "__main__":
    unittest.main()

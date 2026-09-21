from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "install_mcp.py"
SPEC = importlib.util.spec_from_file_location("install_mcp", SCRIPT)
mcp = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = mcp
SPEC.loader.exec_module(mcp)


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def server(**fields) -> "mcp.Server":
    base = {"name": "demo", "description": "A demo server.", "transport": "http", "url": "https://example.test/mcp"}
    return mcp.Server(**(base | fields))


class RegistryTests(unittest.TestCase):
    def test_public_registry_loads_without_the_local_overlay(self) -> None:
        # A fresh clone has no servers.local.toml; the catalog must still work.
        original = mcp.LOCAL_REGISTRY
        mcp.LOCAL_REGISTRY = ROOT / "integrations" / "does-not-exist.toml"
        try:
            servers = mcp.load_registry()
        finally:
            mcp.LOCAL_REGISTRY = original
        self.assertIn("n8n", servers)
        for name, entry in servers.items():
            self.assertEqual(entry.origin, "servers.toml", name)

    def test_every_registry_entry_names_variables_instead_of_secrets(self) -> None:
        for name, entry in mcp.load_registry().items():
            for host in entry.hosts:
                rendered = json.dumps(mcp.render(entry, host))
                self.assertIsNone(mcp.SECRET_RE.search(rendered), f"{name} ({host}): {rendered}")
                for variable in entry.required_env:
                    self.assertIn(variable, rendered, name)

    def test_rejects_a_value_shaped_like_a_credential(self) -> None:
        with self.assertRaises(ValueError) as caught:
            mcp._parse_server(
                "leaky",
                {
                    "description": "Leaks a token.",
                    "transport": "http",
                    "url": "https://example.test/mcp?api_key=abc123def456",
                },
                "servers.toml",
            )
        self.assertIn("credential", str(caught.exception))

    def test_rejects_unknown_fields_and_mismatched_transports(self) -> None:
        with self.assertRaises(ValueError):
            mcp._parse_server("x", {"description": "d", "transport": "http", "url": "u", "nope": 1}, "t")
        with self.assertRaises(ValueError):
            mcp._parse_server("x", {"description": "d", "transport": "stdio", "url": "u"}, "t")


class RenderTests(unittest.TestCase):
    def test_stdio_secrets_expand_for_claude_and_stay_names_for_codex(self) -> None:
        entry = server(
            transport="stdio",
            url="",
            command="npx",
            args=("-y", "thing@1.0.0"),
            env=(("LOG_LEVEL", "error"),),
            secret_env=("THING_API_KEY",),
        )
        self.assertEqual(
            mcp.render(entry, "claude"),
            {
                "type": "stdio",
                "command": "npx",
                "args": ["-y", "thing@1.0.0"],
                "env": {"LOG_LEVEL": "error", "THING_API_KEY": "${THING_API_KEY}"},
            },
        )
        self.assertEqual(
            mcp.render(entry, "codex"),
            {
                "command": "npx",
                "args": ["-y", "thing@1.0.0"],
                "env_vars": ["THING_API_KEY"],
                "env": {"LOG_LEVEL": "error"},
            },
        )

    def test_codex_reads_headers_from_env_var_names(self) -> None:
        entry = server(
            secret_headers=(("Authorization", "Bearer ${T_KEY}"), ("locationId", "${T_LOCATION}")),
        )
        self.assertEqual(
            mcp.render(entry, "codex"),
            {
                "url": "https://example.test/mcp",
                "bearer_token_env_var": "T_KEY",
                "env_http_headers": {"locationId": "T_LOCATION"},
            },
        )
        self.assertEqual(
            mcp.render(entry, "claude")["headers"],
            {"Authorization": "Bearer ${T_KEY}", "locationId": "${T_LOCATION}"},
        )

    def test_codex_rejects_what_it_cannot_express(self) -> None:
        interpolated = server(url="https://example.test/mcp?api_key=${T_KEY}")
        with self.assertRaises(ValueError) as caught:
            mcp.render(interpolated, "codex")
        self.assertIn("does not expand", str(caught.exception))

        composed = server(secret_headers=(("X-Key", "id-${T_KEY}-suffix"),))
        with self.assertRaises(ValueError):
            mcp.render(composed, "codex")

        claude_only = server(hosts=("claude",))
        with self.assertRaises(ValueError) as caught:
            mcp.render(claude_only, "codex")
        self.assertIn("not configurable for codex", str(caught.exception))

    def test_toml_tables_render_last_so_the_block_stays_valid(self) -> None:
        block = {"command": "npx", "env_vars": ["A_KEY"], "env": {"LOG_LEVEL": "error"}}
        text = mcp.render_toml("demo", block)
        self.assertEqual(tomllib.loads(text)["mcp_servers"]["demo"], block)
        self.assertLess(text.index("env_vars"), text.index("[mcp_servers.demo.env]"))


class InstallTests(unittest.TestCase):
    def test_writes_both_hosts_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            args = ("install", "--project", str(project), "--host", "both", "--server", "n8n")

            first = run_cli(*args)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertIn("configured servers=1 hosts=2 added=2 unchanged=0", first.stdout)
            self.assertIn("env_required\tN8N_API_KEY\t", first.stdout)

            expected = mcp.render(mcp.load_registry()["n8n"], "claude")
            written = json.loads((project / ".mcp.json").read_text(encoding="utf-8"))
            self.assertEqual(written["mcpServers"]["n8n"], expected)

            config = tomllib.loads((project / ".codex/config.toml").read_text(encoding="utf-8"))
            self.assertEqual(
                config["mcp_servers"]["n8n"], mcp.render(mcp.load_registry()["n8n"], "codex")
            )

            second = run_cli(*args)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertIn("configured servers=1 hosts=2 added=0 unchanged=2", second.stdout)

    def test_merges_without_disturbing_existing_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            (project / ".mcp.json").write_text(
                json.dumps({"mcpServers": {"kept": {"type": "http", "url": "https://kept.test"}}})
                + "\n",
                encoding="utf-8",
            )
            (project / ".codex").mkdir()
            (project / ".codex/config.toml").write_text(
                '# keep me\n[projects."/somewhere"]\ntrust_level = "trusted"\n', encoding="utf-8"
            )

            result = run_cli(
                "install", "--project", str(project), "--host", "both", "--server", "exa"
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            written = json.loads((project / ".mcp.json").read_text(encoding="utf-8"))
            self.assertEqual(written["mcpServers"]["kept"]["url"], "https://kept.test")
            self.assertIn("exa", written["mcpServers"])

            text = (project / ".codex/config.toml").read_text(encoding="utf-8")
            self.assertIn("# keep me", text)
            config = tomllib.loads(text)
            self.assertEqual(config["projects"]["/somewhere"]["trust_level"], "trusted")
            self.assertIn("exa", config["mcp_servers"])

    def test_divergent_entry_aborts_before_any_write(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            mcp_json = project / ".mcp.json"
            mcp_json.write_text(
                json.dumps({"mcpServers": {"exa": {"type": "http", "url": "https://local.test"}}})
                + "\n",
                encoding="utf-8",
            )
            before = mcp_json.read_bytes()

            result = run_cli(
                "install",
                "--project",
                str(project),
                "--host",
                "claude",
                "--server",
                "exa",
                "--server",
                "stripe",
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("nothing was written", result.stderr)
            self.assertEqual(mcp_json.read_bytes(), before)

    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            result = run_cli(
                "install",
                "--project",
                str(project),
                "--host",
                "both",
                "--server",
                "n8n",
                "--dry-run",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("would_write servers=1 hosts=2 added=2 unchanged=0", result.stdout)
            self.assertFalse((project / ".mcp.json").exists())
            self.assertFalse((project / ".codex").exists())

    def test_refuses_unknown_servers_and_filesystem_roots(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            unknown = run_cli(
                "install", "--project", raw, "--host", "claude", "--server", "nope"
            )
            self.assertEqual(unknown.returncode, 2)
            self.assertIn("unknown server(s): nope", unknown.stderr)

        root = run_cli(
            "install", "--project", Path.cwd().anchor, "--host", "claude", "--server", "exa"
        )
        self.assertEqual(root.returncode, 2)
        self.assertIn("cannot be a filesystem root", root.stderr)


class ListTests(unittest.TestCase):
    def test_lists_rows_and_filters_by_suggested_type(self) -> None:
        listing = run_cli("list")
        self.assertEqual(listing.returncode, 0, listing.stderr)
        rows = [line.split("\t") for line in listing.stdout.splitlines()]
        self.assertTrue(all(len(row) == 4 for row in rows))
        self.assertIn("n8n", {row[0] for row in rows})

        filtered = run_cli("list", "--for-type", "automation/n8n")
        self.assertEqual(filtered.returncode, 0, filtered.stderr)
        names = {line.split("\t")[0] for line in filtered.stdout.splitlines()}
        self.assertIn("n8n", names)
        self.assertNotIn("chrome-devtools", names)

    def test_detail_reports_the_environment_variables_a_server_needs(self) -> None:
        detail = run_cli("list", "--server", "n8n")
        self.assertEqual(detail.returncode, 0, detail.stderr)
        fields = dict(line.split("\t", 1) for line in detail.stdout.splitlines())
        self.assertEqual(fields["transport"], "stdio")
        self.assertEqual(fields["required_env"], "N8N_API_URL,N8N_API_KEY")
        self.assertEqual(fields["recipe"], "integrations/n8n/README.md")


if __name__ == "__main__":
    unittest.main()

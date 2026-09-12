from __future__ import annotations

import importlib.util
import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_catalog.py"
SPEC = importlib.util.spec_from_file_location("audit_catalog", SCRIPT)
audit = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = audit
SPEC.loader.exec_module(audit)


def write_skill(path: Path, name: str, description: str = "A focused test skill.") -> Path:
    path.mkdir(parents=True, exist_ok=True)
    skill = path / "SKILL.md"
    skill.write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n\n# {name}\n",
        encoding="utf-8",
    )
    return skill


class FrontmatterTests(unittest.TestCase):
    def test_parses_folded_description(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            path.write_text(
                "---\nname: folded\ndescription: >-\n  First branch.\n  Second branch.\n"
                "disable-model-invocation: true\n---\n",
                encoding="utf-8",
            )
            skill = audit.parse_skill(path)
            self.assertEqual(skill.description, "First branch. Second branch.")
            self.assertTrue(skill.disable_model_invocation)

    def test_rejects_missing_description(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            path.write_text("---\nname: broken\n---\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                audit.parse_skill(path)


class CatalogTests(unittest.TestCase):
    def make_catalog(self, root: Path) -> None:
        write_skill(root / "library" / "engineering" / "demo", "demo")
        (root / "bundles").mkdir(parents=True)
        (root / "integrations" / "example").mkdir(parents=True)
        (root / "integrations" / "example" / "README.md").write_text("# Example\n")
        (root / "bundles" / "demo.toml").write_text(
            'version = 1\nid = "demo"\ndescription = "Test"\n'
            'skills = ["engineering/demo"]\nreference_skills = []\n'
            'integrations = ["example"]\n',
            encoding="utf-8",
        )

    def test_valid_catalog_and_bundle_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_catalog(root)
            issues, skills = audit.catalog_issues(root)
            self.assertEqual(issues, [])
            self.assertEqual(set(skills), {"engineering/demo"})
            selected = audit.resolve_bundles(["demo"], root)
            self.assertEqual([item.name for item in selected], ["demo"])

    def test_duplicate_runtime_name_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_catalog(root)
            write_skill(root / "library" / "other" / "demo-copy", "demo")
            issues, _ = audit.catalog_issues(root)
            self.assertTrue(any("duplicate canonical runtime name demo" in item for item in issues))

    def test_tree_hash_tracks_content_not_mtime(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "skill"
            skill = write_skill(directory, "demo")
            before = audit.tree_hash(directory)
            skill.touch()
            self.assertEqual(audit.tree_hash(directory), before)
            skill.write_text(skill.read_text() + "changed\n", encoding="utf-8")
            self.assertNotEqual(audit.tree_hash(directory), before)


class ProjectTests(unittest.TestCase):
    def test_valid_vendored_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vendor = root / ".agent-setup" / "skills" / "demo"
            write_skill(vendor, "demo")
            for host in (".agents", ".claude"):
                native = root / host / "skills" / "demo"
                native.parent.mkdir(parents=True)
                native.symlink_to(Path("../../.agent-setup/skills/demo"))
            digest = audit.tree_hash(vendor)
            context_file = root / "AGENTS.md"
            context_file.write_text("# Project rules\n", encoding="utf-8")
            config_file = root / ".mcp.json"
            config_file.write_text(
                json.dumps({"mcpServers": {"demo": {"type": "stdio", "command": "demo"}}}),
                encoding="utf-8",
            )
            config_value = {"type": "stdio", "command": "demo"}
            (root / ".agent-setup.toml").write_text(
                'version = 1\nmode = "vendor"\ntargets = ["codex", "claude"]\n'
                '[[skills]]\nruntime_name = "demo"\nid = "engineering/demo"\n'
                f'sha256 = "{digest}"\n'
                '[[owned_files]]\nkind = "context"\npath = "AGENTS.md"\n'
                f'sha256 = "{audit.file_hash(context_file)}"\n'
                '[[config_ownership]]\nhost = "claude"\nfile = ".mcp.json"\n'
                'key = "mcpServers.demo"\n'
                f'sha256 = "{audit.canonical_value_hash(config_value)}"\n',
                encoding="utf-8",
            )
            result = audit.cmd_project(SimpleNamespace(root=root))
            self.assertEqual(result, 0)

            config_file.write_text(json.dumps({"mcpServers": {"demo": {"command": "changed"}}}))
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(audit.cmd_project(SimpleNamespace(root=root)), 1)

    def test_actual_coding_and_n8n_bundle_is_project_scoped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["rtk", "git", "init", "-q"], cwd=root, check=True)
            selected = audit.resolve_bundles(["coding", "n8n"], audit.CATALOG)
            bundle = audit.load_bundle(audit.CATALOG / "bundles" / "n8n.toml")
            catalog = audit.catalog_skills(audit.CATALOG)
            manifest = [
                "version = 1",
                'catalog = "~/skills"',
                'mode = "vendor"',
                'targets = ["codex", "claude"]',
                'bundles = ["coding", "n8n"]',
                "",
            ]
            for skill in selected:
                skill_id = skill.path.parent.relative_to(audit.CATALOG / "library").as_posix()
                vendor = root / ".agent-setup" / "skills" / skill.name
                shutil.copytree(skill.path.parent, vendor)
                for host in (".agents", ".claude"):
                    native = root / host / "skills" / skill.name
                    native.parent.mkdir(parents=True, exist_ok=True)
                    native.symlink_to(Path(f"../../.agent-setup/skills/{skill.name}"))
                manifest.extend([
                    "[[skills]]",
                    f'id = "{skill_id}"',
                    f'runtime_name = "{skill.name}"',
                    f'sha256 = "{audit.tree_hash(vendor)}"',
                    "",
                ])
            for skill_id in bundle["reference_skills"]:
                skill = catalog[skill_id]
                owned = f".agent-setup/references/n8n/{skill.name}"
                target = root / owned
                shutil.copytree(skill.path.parent, target)
                manifest.extend([
                    "[[references]]",
                    'bundle = "n8n"',
                    f'id = "{skill_id}"',
                    f'runtime_name = "{skill.name}"',
                    f'owned_path = "{owned}"',
                    f'sha256 = "{audit.tree_hash(target)}"',
                    "",
                ])
            (root / ".agent-setup.toml").write_text("\n".join(manifest), encoding="utf-8")

            self.assertEqual(audit.cmd_project(SimpleNamespace(root=root)), 0)
            self.assertEqual(len(audit.discover_skills(root / ".agents" / "skills")), 11)
            self.assertEqual(len(audit.discover_skills(root / ".agent-setup" / "references")), 14)
            self.assertFalse((root / ".agents" / "skills" / "n8n-workflow-patterns").exists())


if __name__ == "__main__":
    unittest.main()

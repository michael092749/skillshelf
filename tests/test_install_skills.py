from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "install_skills.py"
INDEX = ROOT / "index.md"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        text=True,
        capture_output=True,
        check=False,
    )


class ListTests(unittest.TestCase):
    def test_lists_types_and_filters_skills(self) -> None:
        types = run_cli("list", "types")
        self.assertEqual(types.returncode, 0, types.stderr)
        self.assertIn("engineering\t27\n", types.stdout)
        self.assertIn("automation/n8n\t16\n", types.stdout)

        skills = run_cli("list", "skills", "--type", "content/writing")
        self.assertEqual(skills.returncode, 0, skills.stderr)
        lines = skills.stdout.splitlines()
        self.assertEqual(len(lines), 3)
        self.assertTrue(all(line.startswith("content/writing/") for line in lines))

    def test_brief_shortens_descriptions_without_losing_rows(self) -> None:
        full = run_cli("list", "skills", "--type", "sales-and-marketing")
        short = run_cli("list", "skills", "--type", "sales-and-marketing", "--brief")
        self.assertEqual(short.returncode, 0, short.stderr)

        full_rows = [line.split("\t") for line in full.stdout.splitlines()]
        short_rows = [line.split("\t") for line in short.stdout.splitlines()]
        self.assertEqual([row[:2] for row in full_rows], [row[:2] for row in short_rows])

        for (_, name, description) in short_rows:
            self.assertLessEqual(len(description), 111, name)
            self.assertNotIn("\n", description)
        longest = max(full_rows, key=lambda row: len(row[2]))
        brief_longest = next(row for row in short_rows if row[1] == longest[1])
        self.assertLess(len(brief_longest[2]), len(longest[2]))

    def test_index_matches_every_catalog_type_and_runtime_name(self) -> None:
        text = INDEX.read_text(encoding="utf-8")
        section_pattern = re.compile(
            r"^### `([^`]+)` \((\d+)(, local-only)?\)\n\n(.*?)(?=^### |^Run `list)",
            re.MULTILINE | re.DOTALL,
        )
        indexed = {
            match.group(1): (
                int(match.group(2)),
                set(re.findall(r"`([a-z0-9-]+)`", match.group(4))),
                bool(match.group(3)),
            )
            for match in section_pattern.finditer(text)
        }

        types = run_cli("list", "types")
        self.assertEqual(types.returncode, 0, types.stderr)
        expected_counts = {
            skill_type: int(count)
            for skill_type, count in (line.split("\t") for line in types.stdout.splitlines())
        }
        # A local-only section documents a skill excluded from this repository, so
        # it is absent from a fresh clone but present in the author's checkout.
        local_only = {name for name, (_, _, is_local) in indexed.items() if is_local}
        self.assertEqual(set(indexed) - local_only, set(expected_counts) - local_only)
        for skill_type, count in expected_counts.items():
            skills = run_cli("list", "skills", "--type", skill_type)
            self.assertEqual(skills.returncode, 0, skills.stderr)
            expected_names = {line.split("\t")[1] for line in skills.stdout.splitlines()}
            indexed_count, indexed_names, _ = indexed[skill_type]
            self.assertEqual(indexed_count, count)
            self.assertEqual(indexed_names, expected_names)


class InstallTests(unittest.TestCase):
    def test_copies_to_selected_host_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            args = (
                "install",
                "--project",
                str(project),
                "--host",
                "codex",
                "--skill",
                "productivity/writing-for-agents",
            )
            first = run_cli(*args)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertIn("installed skills=1 hosts=1 copies=1 unchanged=0", first.stdout)
            self.assertTrue((project / ".agents/skills/writing-for-agents/SKILL.md").is_file())
            self.assertTrue(
                (project / ".agents/skills/writing-for-agents/SKILL-MECHANICS.md").is_file()
            )
            self.assertFalse((project / ".claude/skills/writing-for-agents").exists())

            second = run_cli(*args)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertIn("installed skills=1 hosts=1 copies=0 unchanged=1", second.stdout)

    def test_type_can_copy_to_both_hosts(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            result = run_cli(
                "install",
                "--project",
                str(project),
                "--host",
                "both",
                "--type",
                "content/writing",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("installed skills=3 hosts=2 copies=6 unchanged=0", result.stdout)
            for host in (".agents", ".claude"):
                discovered = sorted((project / host / "skills").glob("*/SKILL.md"))
                self.assertEqual(len(discovered), 3)

    def test_conflict_aborts_all_copies(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            conflict = project / ".agents/skills/tdd"
            conflict.mkdir(parents=True)
            (conflict / "SKILL.md").write_text("different\n", encoding="utf-8")

            result = run_cli(
                "install",
                "--project",
                str(project),
                "--host",
                "both",
                "--skill",
                "engineering/tdd",
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("nothing was copied", result.stderr)
            self.assertFalse((project / ".claude/skills/tdd").exists())

    def test_dry_run_does_not_create_host_directories(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            result = run_cli(
                "install",
                "--project",
                str(project),
                "--host",
                "claude",
                "--skill",
                "engineering/tdd",
                "--dry-run",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("would_copy skills=1 hosts=1 copies=1 unchanged=0", result.stdout)
            self.assertFalse((project / ".claude").exists())

    def test_rejects_a_filesystem_root_as_the_project(self) -> None:
        result = run_cli(
            "install",
            "--project",
            Path.cwd().anchor,
            "--host",
            "codex",
            "--skill",
            "engineering/tdd",
            "--dry-run",
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("cannot be a filesystem root", result.stderr)


if __name__ == "__main__":
    unittest.main()

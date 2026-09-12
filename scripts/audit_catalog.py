#!/usr/bin/env python3
"""Validate the dormant catalog and measure project-scoped context metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


CATALOG = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")


@dataclass(frozen=True)
class Skill:
    path: Path
    name: str
    description: str
    disable_model_invocation: bool = False

    @property
    def core_chars(self) -> int:
        return len(self.name) + 2 + len(self.description) + 1


def _scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value[1:-1]
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def parse_skill(path: Path) -> Skill:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path}: missing YAML frontmatter")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise ValueError(f"{path}: unclosed YAML frontmatter") from exc

    values: dict[str, str] = {}
    i = 1
    while i < end:
        line = lines[i]
        if line.startswith((" ", "\t")) or ":" not in line:
            i += 1
            continue
        key, raw = line.split(":", 1)
        key = key.strip()
        raw = raw.strip()
        if raw in {">", ">-", ">+", "|", "|-", "|+"}:
            block: list[str] = []
            i += 1
            while i < end and (not lines[i].strip() or lines[i].startswith((" ", "\t"))):
                block.append(lines[i].strip())
                i += 1
            values[key] = ("\n" if raw.startswith("|") else " ").join(block).strip()
            continue
        values[key] = _scalar(raw)
        i += 1

    name = values.get("name", "")
    description = values.get("description", "")
    if not name or not description:
        raise ValueError(f"{path}: frontmatter requires name and description")
    return Skill(
        path=path,
        name=name,
        description=description,
        disable_model_invocation=values.get("disable-model-invocation", "").lower() == "true",
    )


def discover_skills(base: Path) -> list[Skill]:
    found: list[Skill] = []

    def visit(directory: Path, ancestors: frozenset[tuple[int, int]]) -> None:
        try:
            stat = directory.stat()
        except (FileNotFoundError, PermissionError):
            return
        inode = (stat.st_dev, stat.st_ino)
        if inode in ancestors:
            return
        skill_file = directory / "SKILL.md"
        if skill_file.is_file():
            found.append(parse_skill(skill_file))
            return
        try:
            children = sorted(p for p in directory.iterdir() if p.is_dir())
        except PermissionError:
            return
        next_ancestors = ancestors | {inode}
        for child in children:
            if child.name == ".git":
                continue
            visit(child, next_ancestors)

    if base.exists():
        visit(base, frozenset())
    return found


def tree_hash(directory: Path) -> str:
    digest = hashlib.sha256()
    entries = sorted(
        p for p in directory.rglob("*")
        if ".git" not in p.relative_to(directory).parts
    )
    for path in entries:
        relative = path.relative_to(directory).as_posix().encode()
        if path.is_symlink():
            digest.update(b"L\0" + relative + b"\0" + os.readlink(path).encode() + b"\0")
        elif path.is_file():
            digest.update(b"F\0" + relative + b"\0")
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
            digest.update(b"\0")
    return digest.hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_value_hash(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(encoded).hexdigest()


def dotted_value(document: dict, key: str) -> object:
    value: object = document
    for part in key.split("."):
        if not isinstance(value, dict) or part not in value:
            raise KeyError(key)
        value = value[part]
    return value


def safe_project_path(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"manifest path escapes project: {relative}")
    return path


def catalog_skills(root: Path = CATALOG) -> dict[str, Skill]:
    library = root / "library"
    return {
        skill.path.parent.relative_to(library).as_posix(): skill
        for skill in discover_skills(library)
    }


def load_bundle(path: Path) -> dict:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def catalog_issues(root: Path = CATALOG) -> tuple[list[str], dict[str, Skill]]:
    issues: list[str] = []
    skills = catalog_skills(root)
    by_name: dict[str, list[str]] = {}
    for skill_id, skill in skills.items():
        by_name.setdefault(skill.name, []).append(skill_id)
        if not NAME_RE.fullmatch(skill.name):
            issues.append(f"invalid runtime name {skill.name!r}: {skill_id}")
    for name, ids in sorted(by_name.items()):
        if len(ids) > 1:
            issues.append(f"duplicate canonical runtime name {name}: {', '.join(ids)}")

    integration_ids = {
        path.parent.name for path in (root / "integrations").glob("*/README.md")
    }
    for path in sorted((root / "bundles").glob("*.toml")):
        try:
            bundle = load_bundle(path)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            issues.append(f"invalid bundle {path.name}: {exc}")
            continue
        if bundle.get("id") != path.stem:
            issues.append(f"bundle id mismatch: {path.name}")
        selected = list(bundle.get("skills", []))
        references = list(bundle.get("reference_skills", []))
        for skill_id in selected + references:
            if skill_id not in skills:
                issues.append(f"{path.name}: missing skill {skill_id}")
        selected_names = [skills[item].name for item in selected if item in skills]
        duplicates = sorted({name for name in selected_names if selected_names.count(name) > 1})
        if duplicates:
            issues.append(f"{path.name}: duplicate selected names {', '.join(duplicates)}")
        overlap = sorted(set(selected) & set(references))
        if overlap:
            issues.append(f"{path.name}: selected and reference overlap {', '.join(overlap)}")
        for integration in bundle.get("integrations", []):
            if integration not in integration_ids:
                issues.append(f"{path.name}: missing integration {integration}")
    return issues, skills


def metric(
    skills: Iterable[Skill],
    path_prefix: str | None = None,
    path_base: Path | None = None,
) -> dict[str, int]:
    items = list(skills)
    core = sum(skill.core_chars for skill in items)
    result = {
        "skills": len(items),
        "core_chars": core,
        "approx_tokens": math.ceil(core / 4),
    }
    if path_prefix is not None:
        rendered: list[str] = []
        for skill in items:
            if path_base is None:
                relative = f"{skill.name}/SKILL.md"
            else:
                relative = skill.path.relative_to(path_base).as_posix()
            rendered.append(
                f"- {skill.name}: {skill.description} (file: {path_prefix}/{relative})\n"
            )
        proxy = sum(len(item) for item in rendered)
        result["path_proxy_chars"] = proxy
        result["path_proxy_tokens"] = math.ceil(proxy / 4)
    return result


def resolve_bundles(bundle_ids: list[str], root: Path = CATALOG) -> list[Skill]:
    skills = catalog_skills(root)
    selected: dict[str, Skill] = {}
    for bundle_id in bundle_ids:
        path = root / "bundles" / f"{bundle_id}.toml"
        if not path.is_file():
            raise ValueError(f"unknown bundle: {bundle_id}")
        bundle = load_bundle(path)
        for skill_id in bundle.get("skills", []):
            skill = skills[skill_id]
            previous = selected.get(skill.name)
            if previous and previous.path != skill.path:
                raise ValueError(f"bundle union duplicates runtime name: {skill.name}")
            selected[skill.name] = skill
    return [selected[name] for name in sorted(selected)]


def cmd_catalog(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    issues, skills = catalog_issues(root)
    variants = discover_skills(root / "variants")
    bundles = sorted((root / "bundles").glob("*.toml"))
    print(f"canonical_skills={len(skills)} variants={len(variants)} bundles={len(bundles)}")
    print(f"canonical_metadata_chars={metric(skills.values())['core_chars']}")
    for issue in issues:
        print(f"ERROR: {issue}", file=sys.stderr)
    return 1 if issues else 0


def cmd_measure(args: argparse.Namespace) -> int:
    for raw in args.scope:
        if "=" not in raw:
            raise ValueError("--scope must be LABEL=PATH")
        label, value = raw.split("=", 1)
        skills = discover_skills(Path(value).expanduser())
        unique = len({skill.name for skill in skills})
        data = metric(skills)
        print(f"{label}: entries={data['skills']} unique_names={unique} "
              f"metadata_chars={data['core_chars']} approx_tokens={data['approx_tokens']}")
    return 0


def _saving(before: int, after: int) -> str:
    if before == 0:
        return "n/a"
    return f"{before - after} ({(before - after) * 100 / before:.1f}%)"


def cmd_compare(args: argparse.Namespace) -> int:
    codex = discover_skills(args.before_codex.expanduser())
    claude = discover_skills(args.before_claude.expanduser())
    selected = resolve_bundles(args.bundle, args.root.resolve())
    rows = [
        ("before_codex_global", metric(codex, "~/.agents/skills", args.before_codex.expanduser())),
        ("before_claude_global", metric(claude)),
        ("after_project", metric(selected, "<repo>/.agents/skills")),
    ]
    for label, data in rows:
        proxy = f" path_proxy_chars={data['path_proxy_chars']}" if "path_proxy_chars" in data else ""
        print(f"{label}: skills={data['skills']} metadata_chars={data['core_chars']} "
              f"approx_tokens={data['approx_tokens']}{proxy}")
    after = rows[-1][1]["core_chars"]
    print(f"saved_vs_codex_metadata={_saving(rows[0][1]['core_chars'], after)}")
    print(f"saved_vs_claude_metadata={_saving(rows[1][1]['core_chars'], after)}")
    print("reference_skills_excluded_from_startup=true")
    codex_path = args.codex_instructions.expanduser()
    claude_path = args.claude_instructions.expanduser()
    codex_bytes = codex_path.stat().st_size if codex_path.is_file() else 0
    claude_bytes = claude_path.stat().st_size if claude_path.is_file() else 0
    print(f"unchanged_instruction_file_bytes=codex:{codex_bytes},claude_pointer:{claude_bytes}")
    return 0


def cmd_project(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    manifest_path = root / ".agent-setup.toml"
    if not manifest_path.is_file():
        print(f"ERROR: missing {manifest_path}", file=sys.stderr)
        return 1
    with manifest_path.open("rb") as handle:
        manifest = tomllib.load(handle)
    issues: list[str] = []
    warnings: list[str] = []

    for entry in manifest.get("skills", []):
        name = entry["runtime_name"]
        vendor = root / ".agent-setup" / "skills" / name
        if not vendor.is_dir():
            issues.append(f"missing vendored skill: {name}")
            continue
        if tree_hash(vendor) != entry.get("sha256"):
            issues.append(f"hash mismatch: {name}")
        for native in (root / ".agents" / "skills" / name, root / ".claude" / "skills" / name):
            if not native.is_symlink() or native.resolve() != vendor.resolve():
                issues.append(f"invalid host link: {native.relative_to(root)}")

    for entry in manifest.get("references", []):
        path = root / entry["owned_path"]
        if not path.is_dir():
            issues.append(f"missing reference skill: {entry['id']}")
        elif tree_hash(path) != entry.get("sha256"):
            issues.append(f"reference hash mismatch: {entry['id']}")

    for entry in manifest.get("integrations", []):
        for name in entry.get("required_env", []):
            if name not in os.environ:
                warnings.append(f"missing required environment variable: {name}")

    for entry in manifest.get("owned_files", []):
        path = safe_project_path(root, entry["path"])
        if not path.is_file():
            issues.append(f"missing owned file: {entry['path']}")
        elif file_hash(path) != entry.get("sha256"):
            issues.append(f"owned file drift: {entry['path']}")

    for path in (root / ".mcp.json", root / ".claude" / "settings.json"):
        if path.is_file():
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                issues.append(f"invalid JSON {path.relative_to(root)}: {exc}")
    codex_config = root / ".codex" / "config.toml"
    if codex_config.is_file():
        try:
            tomllib.loads(codex_config.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            issues.append(f"invalid TOML .codex/config.toml: {exc}")

    for entry in manifest.get("config_ownership", []):
        path = safe_project_path(root, entry["file"])
        if not path.is_file():
            issues.append(f"missing owned config: {entry['file']}")
            continue
        try:
            if path.suffix == ".json":
                document = json.loads(path.read_text(encoding="utf-8"))
            elif path.suffix == ".toml":
                document = tomllib.loads(path.read_text(encoding="utf-8"))
            else:
                raise ValueError(f"unsupported owned config format: {entry['file']}")
            value = dotted_value(document, entry["key"])
        except (json.JSONDecodeError, tomllib.TOMLDecodeError, KeyError, ValueError) as exc:
            issues.append(f"cannot resolve owned config {entry['file']}:{entry['key']}: {exc}")
            continue
        if canonical_value_hash(value) != entry.get("sha256"):
            issues.append(f"owned config drift: {entry['file']}:{entry['key']}")

    for warning in warnings:
        print(f"WARN: {warning}")
    for issue in issues:
        print(f"ERROR: {issue}", file=sys.stderr)
    if not issues:
        print(f"project_ok skills={len(manifest.get('skills', []))} "
              f"references={len(manifest.get('references', []))} "
              f"integrations={len(manifest.get('integrations', []))}")
    return 1 if issues else 0


def parser() -> argparse.ArgumentParser:
    top = argparse.ArgumentParser(description=__doc__)
    sub = top.add_subparsers(dest="command", required=True)

    catalog = sub.add_parser("catalog", help="validate catalog structure and bundles")
    catalog.add_argument("--root", type=Path, default=CATALOG)
    catalog.set_defaults(func=cmd_catalog)

    measure = sub.add_parser("measure", help="measure discovered skill metadata")
    measure.add_argument("--scope", action="append", required=True, metavar="LABEL=PATH")
    measure.set_defaults(func=cmd_measure)

    compare = sub.add_parser("compare", help="compare global discovery with selected bundles")
    compare.add_argument("--root", type=Path, default=CATALOG)
    compare.add_argument("--before-codex", type=Path, default=Path("~/.agents/skills"))
    compare.add_argument("--before-claude", type=Path, default=Path("~/.claude/skills"))
    compare.add_argument("--codex-instructions", type=Path, default=Path("~/.codex/AGENTS.md"))
    compare.add_argument("--claude-instructions", type=Path, default=Path("~/.claude/CLAUDE.md"))
    compare.add_argument("--bundle", action="append", required=True)
    compare.set_defaults(func=cmd_compare)

    project = sub.add_parser("project", help="validate a configured project")
    project.add_argument("--root", type=Path, required=True)
    project.set_defaults(func=cmd_project)
    return top


def main() -> int:
    try:
        args = parser().parse_args()
        return args.func(args)
    except (OSError, KeyError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

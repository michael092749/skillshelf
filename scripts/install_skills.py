#!/usr/bin/env python3
"""List and copy catalog skills into a project's agent discovery folders."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

import audit_catalog as audit


CATALOG = Path(__file__).resolve().parents[1]
HOST_PATHS = {
    "codex": Path(".agents/skills"),
    "claude": Path(".claude/skills"),
}


SENTENCE_END = re.compile(r"(?<=[.!?])\s")


def brief(description: str, limit: int = 110) -> str:
    """One-line gist: the first real sentence, capped so a listing stays scannable."""
    text = " ".join(description.split())
    ends = [match.start() for match in SENTENCE_END.finditer(text)]
    # Skip boundaries inside abbreviations ("e.g.", "Dr.") by requiring some substance.
    cut = next((end for end in ends if end >= 40), ends[0] if ends else len(text))
    text = text[:cut].rstrip()
    if len(text) > limit:
        text = text[: limit - 1].rstrip(" ,;:-") + "\u2026"
    return text


def skill_types(skills: dict[str, audit.Skill]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    for skill_id in sorted(skills):
        skill_type = skill_id.rsplit("/", 1)[0]
        grouped.setdefault(skill_type, []).append(skill_id)
    return grouped


def checked_catalog() -> dict[str, audit.Skill]:
    issues, skills = audit.catalog_issues(CATALOG)
    if issues:
        raise ValueError("catalog validation failed:\n  " + "\n  ".join(issues))
    return skills


def resolve_selection(
    skills: dict[str, audit.Skill],
    skill_ids: list[str],
    selected_types: list[str],
) -> list[tuple[str, audit.Skill]]:
    grouped = skill_types(skills)
    selected: set[str] = set()

    for skill_id in skill_ids:
        if skill_id not in skills:
            raise ValueError(f"unknown skill: {skill_id}")
        selected.add(skill_id)
    for skill_type in selected_types:
        normalized = skill_type.strip("/")
        if normalized not in grouped:
            raise ValueError(f"unknown skill type: {skill_type}")
        selected.update(grouped[normalized])

    if not selected:
        raise ValueError("select at least one --skill or --type")
    return [(skill_id, skills[skill_id]) for skill_id in sorted(selected)]


def selected_hosts(host: str) -> list[str]:
    return list(HOST_PATHS) if host == "both" else [host]


def _nearest_existing(path: Path) -> Path:
    current = path
    while not os.path.lexists(current):
        if current == current.parent:
            break
        current = current.parent
    return current


def destination_for(project: Path, host: str, skill: audit.Skill) -> Path:
    destination = project / HOST_PATHS[host] / skill.name
    ancestor = _nearest_existing(destination.parent)
    if not ancestor.resolve().is_relative_to(project):
        raise ValueError(f"destination escapes project through a symlink: {destination}")
    return destination


def destination_state(source: Path, destination: Path) -> str:
    if not os.path.lexists(destination):
        return "copy"
    if destination.is_symlink() or not destination.is_dir():
        return "conflict"
    return "unchanged" if audit.tree_hash(source) == audit.tree_hash(destination) else "conflict"


def copy_skill(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".skill-copy-", dir=destination.parent) as raw:
        staged = Path(raw) / destination.name
        shutil.copytree(source, staged, symlinks=True)
        if audit.tree_hash(source) != audit.tree_hash(staged):
            raise OSError(f"staged copy hash mismatch: {destination}")
        staged.rename(destination)


def cmd_list(args: argparse.Namespace) -> int:
    skills = checked_catalog()
    grouped = skill_types(skills)
    if args.list_kind == "types":
        for skill_type, ids in grouped.items():
            print(f"{skill_type}\t{len(ids)}")
        return 0

    candidates = sorted(skills.items())
    if args.type:
        normalized = args.type.strip("/")
        if normalized not in grouped:
            raise ValueError(f"unknown skill type: {args.type}")
        allowed = set(grouped[normalized])
        candidates = [(skill_id, skill) for skill_id, skill in candidates if skill_id in allowed]
    if args.search:
        query = args.search.casefold()
        candidates = [
            (skill_id, skill)
            for skill_id, skill in candidates
            if query in " ".join((skill_id, skill.name, skill.description)).casefold()
        ]
    for skill_id, skill in candidates:
        description = brief(skill.description) if args.brief else skill.description
        print(f"{skill_id}\t{skill.name}\t{description}")
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    project = args.project.expanduser().resolve()
    if not project.is_dir():
        raise ValueError(f"project directory does not exist: {project}")
    if project == Path(project.anchor):
        raise ValueError("project directory cannot be a filesystem root")

    skills = checked_catalog()
    selection = resolve_selection(skills, args.skill, args.type)
    operations: list[tuple[str, str, audit.Skill, Path, str]] = []
    conflicts: list[Path] = []
    for host in selected_hosts(args.host):
        for skill_id, skill in selection:
            destination = destination_for(project, host, skill)
            state = destination_state(skill.path.parent, destination)
            operations.append((host, skill_id, skill, destination, state))
            if state == "conflict":
                conflicts.append(destination)

    if conflicts:
        rendered = "\n  ".join(str(path) for path in conflicts)
        raise ValueError(
            "existing destinations differ or are not plain directories; nothing was copied:\n  "
            + rendered
        )

    for host, skill_id, skill, destination, state in operations:
        if args.dry_run:
            print(f"{state}\t{host}\t{skill_id}\t{destination}")
            continue
        if state == "copy":
            copy_skill(skill.path.parent, destination)
            if destination_state(skill.path.parent, destination) != "unchanged":
                raise OSError(f"copy verification failed: {destination}")
            print(f"copied\t{host}\t{skill_id}\t{destination}")
        else:
            print(f"unchanged\t{host}\t{skill_id}\t{destination}")

    action = "would_copy" if args.dry_run else "installed"
    copies = sum(state == "copy" for *_, state in operations)
    unchanged = sum(state == "unchanged" for *_, state in operations)
    print(
        f"{action} skills={len(selection)} hosts={len(selected_hosts(args.host))} "
        f"copies={copies} unchanged={unchanged}"
    )
    return 0


def parser() -> argparse.ArgumentParser:
    top = argparse.ArgumentParser(description=__doc__)
    sub = top.add_subparsers(dest="command", required=True)

    listing = sub.add_parser("list", help="list available skill types or individual skills")
    listing_sub = listing.add_subparsers(dest="list_kind", required=True)
    types = listing_sub.add_parser("types", help="list selectable skill categories")
    types.set_defaults(func=cmd_list, brief=False, type=None, search=None)
    skills = listing_sub.add_parser("skills", help="list individual skill IDs")
    skills.add_argument("--type", help="limit output to one exact type from 'list types'")
    skills.add_argument("--search", help="case-insensitive search over IDs, names, and descriptions")
    skills.add_argument(
        "--brief",
        action="store_true",
        help="shorten each description to its first sentence for readable listings",
    )
    skills.set_defaults(func=cmd_list)

    install = sub.add_parser("install", help="copy selected skills into a project")
    install.add_argument("--project", type=Path, required=True)
    install.add_argument("--host", choices=["codex", "claude", "both"], required=True)
    install.add_argument("--skill", action="append", default=[], help="exact skill ID; repeatable")
    install.add_argument("--type", action="append", default=[], help="exact type; repeatable")
    install.add_argument("--dry-run", action="store_true", help="show copies without writing")
    install.set_defaults(func=cmd_install)
    return top


def main() -> int:
    try:
        args = parser().parse_args()
        return args.func(args)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

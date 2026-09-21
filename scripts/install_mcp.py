#!/usr/bin/env python3
"""List registry MCP servers and merge them into a project's host configuration."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


CATALOG = Path(__file__).resolve().parents[1]
REGISTRY = CATALOG / "integrations" / "servers.toml"
LOCAL_REGISTRY = CATALOG / "integrations" / "servers.local.toml"

HOST_FILES = {
    "claude": Path(".mcp.json"),
    "codex": Path(".codex/config.toml"),
}

NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
ENV_RE = re.compile(r"^[A-Z][A-Z0-9_]{0,63}$")
PLACEHOLDER_RE = re.compile(r"\$\{([A-Z][A-Z0-9_]*)\}")
# A registry value is a shape, never a credential. These are the shapes credentials take.
SECRET_RE = re.compile(r"eyJ[A-Za-z0-9_-]{10,}|(?i:bearer)\s+(?!\$\{)\S{16,}|(?i:[?&](api[_-]?)?key=)(?!\$\{)")

TRANSPORTS = {"stdio", "http"}
KNOWN_FIELDS = {
    "description",
    "transport",
    "command",
    "args",
    "env",
    "secret_env",
    "url",
    "secret_headers",
    "hosts",
    "suggested_by",
    "docs",
    "recipe",
}


@dataclass(frozen=True)
class Server:
    """One host-neutral MCP server definition, as written in the registry."""

    name: str
    description: str
    transport: str
    command: str = ""
    args: tuple[str, ...] = ()
    env: tuple[tuple[str, str], ...] = ()
    secret_env: tuple[str, ...] = ()
    url: str = ""
    secret_headers: tuple[tuple[str, str], ...] = ()
    hosts: tuple[str, ...] = ("claude", "codex")
    suggested_by: tuple[str, ...] = ()
    docs: str = ""
    recipe: str = ""
    origin: str = "servers.toml"

    @property
    def required_env(self) -> tuple[str, ...]:
        """Every variable the host must find in the environment for this server to work."""
        names = list(self.secret_env)
        for _, template in self.secret_headers:
            names.extend(PLACEHOLDER_RE.findall(template))
        names.extend(PLACEHOLDER_RE.findall(self.url))
        return tuple(dict.fromkeys(names))


@dataclass
class Operation:
    host: str
    server: Server
    path: Path
    state: str
    rendered: dict = field(default_factory=dict)


def _parse_server(name: str, raw: dict, origin: str) -> Server:
    def fail(message: str) -> ValueError:
        return ValueError(f"{origin}: server {name}: {message}")

    if not NAME_RE.match(name):
        raise fail("name must be alphanumeric with . _ -")
    unknown = sorted(set(raw) - KNOWN_FIELDS)
    if unknown:
        raise fail(f"unknown field(s): {', '.join(unknown)}")

    transport = raw.get("transport", "")
    if transport not in TRANSPORTS:
        raise fail(f"transport must be one of {sorted(TRANSPORTS)}")
    description = str(raw.get("description", "")).strip()
    if not description:
        raise fail("description is required")

    hosts = tuple(raw.get("hosts", ("claude", "codex")))
    for host in hosts:
        if host not in HOST_FILES:
            raise fail(f"unknown host: {host}")
    if not hosts:
        raise fail("hosts cannot be empty")

    env = tuple((str(key), str(value)) for key, value in dict(raw.get("env", {})).items())
    secret_env = tuple(str(value) for value in raw.get("secret_env", ()))
    secret_headers = tuple(
        (str(key), str(value)) for key, value in dict(raw.get("secret_headers", {})).items()
    )

    if transport == "stdio":
        if not raw.get("command"):
            raise fail("stdio servers need a command")
        if raw.get("url") or secret_headers:
            raise fail("url and secret_headers are http-only")
    else:
        if not raw.get("url"):
            raise fail("http servers need a url")
        if raw.get("command") or raw.get("args") or env:
            raise fail("command, args, and env are stdio-only")

    server = Server(
        name=name,
        description=description,
        transport=transport,
        command=str(raw.get("command", "")),
        args=tuple(str(value) for value in raw.get("args", ())),
        env=env,
        secret_env=secret_env,
        url=str(raw.get("url", "")),
        secret_headers=secret_headers,
        hosts=hosts,
        suggested_by=tuple(str(value) for value in raw.get("suggested_by", ())),
        docs=str(raw.get("docs", "")),
        recipe=str(raw.get("recipe", "")),
        origin=origin,
    )

    for variable in server.required_env:
        if not ENV_RE.match(variable):
            raise fail(f"environment variable names are UPPER_SNAKE_CASE: {variable}")
    for header, template in secret_headers:
        if not PLACEHOLDER_RE.search(template):
            raise fail(f"header {header} must reference a ${{VARIABLE}}")
    for text in (server.url, *(value for _, value in env), *(value for _, value in secret_headers)):
        if SECRET_RE.search(text):
            raise fail("value looks like a credential; registries name variables, not secrets")
    return server


def load_registry() -> dict[str, Server]:
    """Public registry, then the gitignored local overlay of personal servers."""
    servers: dict[str, Server] = {}
    for path in (REGISTRY, LOCAL_REGISTRY):
        if not path.exists():
            if path == REGISTRY:
                raise ValueError(f"registry not found: {path}")
            continue
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        for name, raw in dict(data.get("servers", {})).items():
            servers[name] = _parse_server(name, dict(raw), path.name)
    if not servers:
        raise ValueError(f"{REGISTRY}: no servers defined")
    return dict(sorted(servers.items()))


def render(server: Server, host: str) -> dict:
    """The exact value written under mcpServers.<name> or [mcp_servers.<name>]."""
    if host not in server.hosts:
        raise ValueError(
            f"server {server.name} is not configurable for {host}"
            f" (registry declares hosts = {list(server.hosts)})"
        )

    if host == "claude":
        if server.transport == "stdio":
            env = {key: value for key, value in server.env}
            env.update({name: f"${{{name}}}" for name in server.secret_env})
            block: dict = {"type": "stdio", "command": server.command}
            if server.args:
                block["args"] = list(server.args)
            if env:
                block["env"] = env
            return block
        block = {"type": "http", "url": server.url}
        if server.secret_headers:
            block["headers"] = {header: template for header, template in server.secret_headers}
        return block

    if server.transport == "stdio":
        block = {"command": server.command}
        if server.args:
            block["args"] = list(server.args)
        if server.secret_env:
            block["env_vars"] = list(server.secret_env)
        if server.env:
            block["env"] = {key: value for key, value in server.env}
        return block

    if PLACEHOLDER_RE.search(server.url):
        raise ValueError(
            f"server {server.name}: Codex does not expand ${{VARIABLE}} in a url;"
            " declare hosts = [\"claude\"] or use secret_headers"
        )
    block = {"url": server.url}
    for header, template in server.secret_headers:
        bearer = re.fullmatch(r"(?i:bearer)\s+\$\{([A-Z][A-Z0-9_]*)\}", template)
        whole = re.fullmatch(r"\$\{([A-Z][A-Z0-9_]*)\}", template)
        if header.lower() == "authorization" and bearer:
            block["bearer_token_env_var"] = bearer.group(1)
        elif whole:
            block.setdefault("env_http_headers", {})[header] = whole.group(1)
        else:
            raise ValueError(
                f"server {server.name}: Codex reads a header from one variable;"
                f" header {header} must be \"${{VARIABLE}}\" or \"Bearer ${{VARIABLE}}\""
            )
    return block


def _toml_value(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return "[" + ", ".join(_toml_value(item) for item in value) + "]"
    return json.dumps(str(value))


def render_toml(name: str, block: dict) -> str:
    """A `[mcp_servers.<name>]` table, tables-last so appending stays valid TOML."""
    scalars = {key: value for key, value in block.items() if not isinstance(value, dict)}
    tables = {key: value for key, value in block.items() if isinstance(value, dict)}
    lines = [f"[mcp_servers.{name}]"]
    lines.extend(f"{key} = {_toml_value(value)}" for key, value in scalars.items())
    for table, entries in tables.items():
        lines.append("")
        lines.append(f"[mcp_servers.{name}.{table}]")
        lines.extend(f"{key} = {_toml_value(value)}" for key, value in entries.items())
    return "\n".join(lines) + "\n"


def _read_existing(path: Path, host: str) -> dict:
    if path.is_symlink():
        raise ValueError(f"refusing to write through a symlink: {path}")
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    if host == "claude":
        document = json.loads(text) if text.strip() else {}
        if not isinstance(document, dict):
            raise ValueError(f"{path}: expected a JSON object at the top level")
        servers = document.get("mcpServers", {})
        if not isinstance(servers, dict):
            raise ValueError(f"{path}: mcpServers must be an object")
        return servers
    return dict(tomllib.loads(text).get("mcp_servers", {}))


def plan(project: Path, hosts: list[str], servers: list[Server]) -> list[Operation]:
    operations: list[Operation] = []
    conflicts: list[str] = []
    for host in hosts:
        path = project / HOST_FILES[host]
        existing = _read_existing(path, host)
        for server in servers:
            rendered = render(server, host)
            current = existing.get(server.name)
            if current is None:
                state = "add"
            elif current == rendered:
                state = "unchanged"
            else:
                state = "conflict"
                conflicts.append(f"{path}: {server.name}")
            operations.append(Operation(host, server, path, state, rendered))
    if conflicts:
        raise ValueError(
            "existing entries differ from the registry; nothing was written:\n  "
            + "\n  ".join(conflicts)
            + "\nKeep the project's version by dropping that server, or remove the entry first."
        )
    return operations


def _write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        handle.write(text)
        staged = Path(handle.name)
    staged.replace(path)


def apply_claude(path: Path, additions: list[Operation]) -> None:
    document: dict = {}
    if path.exists():
        text = path.read_text(encoding="utf-8")
        document = json.loads(text) if text.strip() else {}
    servers = dict(document.get("mcpServers", {}))
    for operation in additions:
        servers[operation.server.name] = operation.rendered
    document["mcpServers"] = servers
    candidate = json.dumps(document, indent=2) + "\n"

    verify = json.loads(candidate)["mcpServers"]
    for operation in additions:
        if verify.get(operation.server.name) != operation.rendered:
            raise OSError(f"write verification failed: {path}: {operation.server.name}")
    _write_atomic(path, candidate)


def apply_codex(path: Path, additions: list[Operation]) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if text and not text.endswith("\n"):
        text += "\n"
    blocks = "\n".join(render_toml(op.server.name, op.rendered) for op in additions)
    candidate = f"{text}\n{blocks}" if text else blocks

    # The append is only safe if the file still parses and says what we meant.
    parsed = tomllib.loads(candidate).get("mcp_servers", {})
    for operation in additions:
        if parsed.get(operation.server.name) != operation.rendered:
            raise OSError(f"write verification failed: {path}: {operation.server.name}")
    _write_atomic(path, candidate)


def cmd_list(args: argparse.Namespace) -> int:
    servers = load_registry()
    if args.server:
        if args.server not in servers:
            raise ValueError(f"unknown server: {args.server}")
        server = servers[args.server]
        print(f"name\t{server.name}")
        print(f"transport\t{server.transport}")
        print(f"hosts\t{','.join(server.hosts)}")
        print(f"required_env\t{','.join(server.required_env) or '-'}")
        print(f"suggested_by\t{','.join(server.suggested_by) or '-'}")
        print(f"docs\t{server.docs or '-'}")
        print(f"recipe\t{server.recipe or '-'}")
        print(f"origin\t{server.origin}")
        print(f"description\t{server.description}")
        return 0

    for server in servers.values():
        if args.for_type and not any(
            hint == args.for_type or hint.startswith(f"{args.for_type}/")
            for hint in server.suggested_by
        ):
            continue
        env = ",".join(server.required_env) or "-"
        print(f"{server.name}\t{server.transport}\t{env}\t{server.description}")
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    project = args.project.expanduser().resolve()
    if not project.is_dir():
        raise ValueError(f"project directory does not exist: {project}")
    if project == Path(project.anchor):
        raise ValueError("project directory cannot be a filesystem root")

    registry = load_registry()
    unknown = [name for name in args.server if name not in registry]
    if unknown:
        raise ValueError(f"unknown server(s): {', '.join(unknown)}")
    if not args.server:
        raise ValueError("select at least one --server")
    selection = [registry[name] for name in dict.fromkeys(args.server)]
    hosts = list(HOST_FILES) if args.host == "both" else [args.host]

    operations = plan(project, hosts, selection)
    for operation in operations:
        if args.dry_run:
            print(f"{operation.state}\t{operation.host}\t{operation.server.name}\t{operation.path}")

    if not args.dry_run:
        for host in hosts:
            additions = [op for op in operations if op.host == host and op.state == "add"]
            if not additions:
                continue
            path = project / HOST_FILES[host]
            (apply_claude if host == "claude" else apply_codex)(path, additions)
        for operation in operations:
            verb = "wrote" if operation.state == "add" else "unchanged"
            print(f"{verb}\t{operation.host}\t{operation.server.name}\t{operation.path}")

    for variable in dict.fromkeys(name for server in selection for name in server.required_env):
        print(f"env_required\t{variable}\t{'set' if os.environ.get(variable) else 'unset'}")

    action = "would_write" if args.dry_run else "configured"
    added = sum(operation.state == "add" for operation in operations)
    unchanged = sum(operation.state == "unchanged" for operation in operations)
    print(
        f"{action} servers={len(selection)} hosts={len(hosts)} "
        f"added={added} unchanged={unchanged}"
    )
    return 0


def parser() -> argparse.ArgumentParser:
    top = argparse.ArgumentParser(description=__doc__)
    sub = top.add_subparsers(dest="command", required=True)

    listing = sub.add_parser("list", help="list registry servers, or one server in detail")
    listing.add_argument("--for-type", help="only servers suggested for a catalog type or skill ID")
    listing.add_argument("--server", help="print one server's full entry instead of the table")
    listing.set_defaults(func=cmd_list)

    install = sub.add_parser("install", help="merge selected servers into a project's host config")
    install.add_argument("--project", type=Path, required=True)
    install.add_argument("--host", choices=["codex", "claude", "both"], required=True)
    install.add_argument("--server", action="append", default=[], help="registry name; repeatable")
    install.add_argument("--dry-run", action="store_true", help="show the merge without writing")
    install.set_defaults(func=cmd_install)
    return top


def main() -> int:
    try:
        args = parser().parse_args()
        return args.func(args)
    except (OSError, ValueError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

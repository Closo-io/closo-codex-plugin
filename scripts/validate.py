"""Проверки репозитория плагина: JSON, навыки, имена инструментов, секреты, README на двух языках.

Запуск: ``python validate.py <каталог плагина> [--tools data/mcp_tools.json]``. Код возврата 0 — всё чисто.
Те же проверки входят в CI каждого публичного репозитория.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Слова с подчёркиванием в навыках, которые не инструменты, а параметры и поля ответов.
PARAMS = {
    "expected_sha", "dialog_id", "agent_id", "task_id", "skill_id", "job_id", "resource_type", "resource_id", "time_type", "skip_condition",
    "end_at", "start_at", "injection_warning", "untrusted_data", "access_denied", "task_type_id", "not_available_yet",
}
SECRET_PATTERNS = [
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}")),
    ("api key", re.compile(r"\b(?:sk|pk|rk)-[A-Za-z0-9_-]{16,}\b")),
    ("bot token", re.compile(r"\b\d{6,12}:[A-Za-z0-9_-]{30,}\b")),
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("long hex", re.compile(r"\b[0-9a-fA-F]{40,}\b")),
    ("aws key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("bearer value", re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}")),
]
INTERNAL = [
    ("internal ip", re.compile(r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|203\.161\.56\.57)\b")),
    ("internal host", re.compile(r"\b(?:dev|stage|stg)-(?:api|app|mcp|ml)\.closo\.io\b")),
]
TEXT_SUFFIXES = {".md", ".json", ".yml", ".yaml", ".txt", ".toml", ".py", ".sh"}


def _text_files(root: Path):
    for p in sorted(root.rglob("*")):
        if p.is_file() and ".git" not in p.parts and p.suffix in TEXT_SUFFIXES | {""}:
            yield p


def check_json(root: Path) -> list[str]:
    errors = []
    for p in root.rglob("*.json"):
        if ".git" in p.parts:
            continue
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except ValueError as exc:
            errors.append(f"{p.relative_to(root)}: invalid JSON ({exc})")
    return errors


def _frontmatter(text: str) -> tuple[dict[str, str], str]:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip().strip('"')
    return meta, m.group(2)


def check_skills(root: Path, tools: set[str]) -> list[str]:
    errors = []
    skills = sorted(list((root / "skills").glob("*/SKILL.md")) + list(root.glob("plugins/*/skills/*/SKILL.md")))
    if not skills:
        return ["skills/: no skills found"]
    prefixes = {t.split("_")[0] for t in tools}
    for path in skills:
        rel = path.relative_to(root)
        meta, body = _frontmatter(path.read_text(encoding="utf-8"))
        if meta.get("name") != path.parent.name:
            errors.append(f"{rel}: frontmatter name must equal the directory name")
        description = meta.get("description", "")
        if not description or len(description) > 1024:
            errors.append(f"{rel}: description is required and must be at most 1024 characters")
        if len(body.strip()) < 200:
            errors.append(f"{rel}: skill body is too short")
        for token in set(re.findall(r"`([a-z]+(?:_[a-z]+)+)`", body)):
            if token in PARAMS or token in tools:
                continue
            if token.split("_")[0] in prefixes:
                errors.append(f"{rel}: `{token}` is not an MCP tool of the server (data/mcp_tools.json)")
    return errors


def check_secrets(root: Path) -> list[str]:
    errors = []
    for p in _text_files(root):
        text = p.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in SECRET_PATTERNS + INTERNAL:
            if pattern.search(text):
                errors.append(f"{p.relative_to(root)}: looks like a {label}")
    return errors


def check_readme(root: Path) -> list[str]:
    readme = root / "README.md"
    if not readme.exists():
        return ["README.md is missing"]
    text = readme.read_text(encoding="utf-8")
    errors = [f"README.md: missing section '{h}'" for h in ("Русский", "English") if not re.search(rf"^#+\s*{h}\b", text, re.M)]
    for path in (root / "LICENSE",):
        if not path.exists():
            errors.append(f"{path.name} is missing")
    return errors


def validate(root: Path, tools: set[str]) -> list[str]:
    return check_json(root) + check_skills(root, tools) + check_secrets(root) + check_readme(root)


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if "--tools" in argv:
        tools_path = Path(argv[argv.index("--tools") + 1])
    else:  # рядом со скриптом: в источнике data/, в собранном репозитории scripts/
        here = Path(__file__).parent
        tools_path = here / "mcp_tools.json" if (here / "mcp_tools.json").exists() else here / "data" / "mcp_tools.json"
    args = [a for a in args if a != str(tools_path)]
    root = Path(args[0]) if args else Path(".")
    tools = set(json.loads(tools_path.read_text(encoding="utf-8"))["tools"])
    problems = validate(root, tools)
    for p in problems:
        print("ERROR:", p)
    print("OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

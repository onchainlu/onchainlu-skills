#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
ALLOWED_FRONTMATTER_KEYS = {
    "allowed-tools",
    "description",
    "license",
    "metadata",
    "name",
}
GITHUB_AUTH_SKILLS = {
    "cpr",
    "pr-ready",
    "pr-triage",
    "pr-update",
    "stacked-pr",
    "ticket-ship",
}
TRIGGER_OWNERS = {
    "/clean": "clean",
    '"clean it up"': "clean",
    '"tidy this"': "clean",
    "$smells": "smells",
    "/smells": "smells",
}
FORBIDDEN_STATE_NAMES = {
    ".env",
    ".git-credentials",
    "credentials.json",
    "session.json",
    "token.json",
    "wallet.json",
}


def fail(errors: list[str], path: Path, message: str) -> None:
    errors.append(f"{path.relative_to(ROOT)}: {message}")


def read_frontmatter(path: Path, errors: list[str]) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---(?:\n|$)", text, re.DOTALL)
    if not match:
        fail(errors, path, "missing or malformed YAML frontmatter")
        return "", ""

    lines = match.group(1).splitlines()
    top_level_keys = {
        key_match.group(1)
        for line in lines
        if (key_match := re.match(r"^([A-Za-z0-9_-]+):", line))
    }
    unexpected = sorted(top_level_keys - ALLOWED_FRONTMATTER_KEYS)
    if unexpected:
        fail(errors, path, f"unexpected frontmatter keys: {', '.join(unexpected)}")

    name = ""
    description_parts: list[str] = []
    collecting_description = False
    for line in lines:
        if line.startswith("name:"):
            name = line.split(":", 1)[1].strip().strip('"\'')
            collecting_description = False
            continue
        if line.startswith("description:"):
            value = line.split(":", 1)[1].strip()
            collecting_description = value in {"|", "|-", ">", ">-"}
            if value and not collecting_description:
                description_parts.append(value.strip('"\''))
            continue
        if collecting_description:
            if line.startswith((" ", "\t")):
                description_parts.append(line.strip())
                continue
            collecting_description = False

    description = " ".join(description_parts).strip()
    if not name:
        fail(errors, path, "missing name")
    elif not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        fail(errors, path, f"invalid skill name: {name}")
    if not description:
        fail(errors, path, "missing description")
    elif len(description) > 1024:
        fail(errors, path, "description exceeds 1024 characters")
    return name, description


def quoted_yaml_value(text: str, key: str) -> str | None:
    match = re.search(rf'^\s+{re.escape(key)}:\s+"((?:[^"\\]|\\.)*)"\s*$', text, re.MULTILINE)
    if not match:
        return None
    return json.loads(f'"{match.group(1)}"')


def validate_openai_yaml(
    skill_dir: Path, skill_name: str, errors: list[str]
) -> None:
    path = skill_dir / "agents" / "openai.yaml"
    if not path.is_file():
        fail(errors, path, "missing OpenAI interface metadata")
        return
    text = path.read_text(encoding="utf-8")
    if not text.startswith("interface:\n"):
        fail(errors, path, "must start with interface")

    display_name = quoted_yaml_value(text, "display_name")
    short_description = quoted_yaml_value(text, "short_description")
    default_prompt = quoted_yaml_value(text, "default_prompt")
    if not display_name:
        fail(errors, path, "missing quoted display_name")
    if not short_description:
        fail(errors, path, "missing quoted short_description")
    elif not 25 <= len(short_description) <= 64:
        fail(errors, path, "short_description must be 25-64 characters")
    if not default_prompt:
        fail(errors, path, "missing quoted default_prompt")
    elif f"${skill_name}" not in default_prompt:
        fail(errors, path, f"default_prompt must mention ${skill_name}")


def markdown_local_targets(text: str) -> list[str]:
    """Return inline and reference-definition Markdown destinations."""
    targets: list[str] = []
    cursor = 0
    while True:
        start = text.find("](", cursor)
        if start < 0:
            break
        index = start + 2
        while index < len(text) and text[index].isspace():
            index += 1
        if index < len(text) and text[index] == "<":
            end = text.find(">", index + 1)
            if end >= 0:
                targets.append(text[index : end + 1])
                cursor = end + 1
                continue
        destination: list[str] = []
        depth = 0
        escaped = False
        while index < len(text):
            char = text[index]
            if escaped:
                destination.append(char)
                escaped = False
            elif char == "\\":
                destination.append(char)
                escaped = True
            elif char == "(":
                depth += 1
                destination.append(char)
            elif char == ")":
                if depth == 0:
                    break
                depth -= 1
                destination.append(char)
            elif char.isspace() and depth == 0:
                break
            else:
                destination.append(char)
            index += 1
        if destination:
            targets.append("".join(destination))
        cursor = max(index + 1, start + 2)
    targets.extend(
        re.findall(r"^\s{0,3}\[[^\]]+\]:\s*(<[^>]+>|\S+)", text, re.MULTILINE)
    )
    return targets


def decode_markdown_escapes(value: str) -> str:
    """Decode Markdown backslash escapes for ASCII punctuation only."""
    return re.sub(r"\\([!\"#$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~])", r"\1", value)


def validate_local_links(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for raw_target in markdown_local_targets(text):
        target = raw_target.strip().strip("<>").split("#", 1)[0].split("?", 1)[0]
        if not target or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE):
            continue
        if target in {"...", "…"}:
            continue
        resolved = (path.parent / unquote(decode_markdown_escapes(target))).resolve()
        try:
            resolved.relative_to(ROOT)
        except ValueError:
            fail(errors, path, f"local link escapes repository: {raw_target}")
            continue
        if not resolved.exists():
            fail(errors, path, f"missing local link target: {raw_target}")


def markdown_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.md") if ".git" not in path.parts)


def validate_public_content(errors: list[str]) -> None:
    forbidden_paths = (
        "/" + "Users/",
        "/" + "Users/Shared/",
        "/" + "opt/data/",
        "C:" + "\\Users\\",
        "hermes-enterprise-kit-" + "pilot-customer",
        "codex:" + "//threads/",
    )
    stale_phrases = (
        "Private source " + "of truth",
        "private " + "tap",
        "repository is " + "private",
    )
    secret_patterns = {
        "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        "GitHub token": re.compile(r"\b(?:gh[opsu]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,})\b"),
        "OpenAI-style secret": re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
        "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
        "Slack token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
        "JWT": re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
        "authenticated URL": re.compile(r"https?://[^\s/:]+:[^\s@]+@"),
    }
    machine_path_patterns = {
        "Linux user home": re.compile(r"(?<![A-Za-z0-9_])/home/[A-Za-z0-9._-]+/"),
    }

    paths = [path for path in ROOT.rglob("*") if ".git" not in path.parts]

    for path in paths:
        if not path.is_file():
            continue
        if path.name in FORBIDDEN_STATE_NAMES or path.name.startswith(".env."):
            fail(errors, path, "committed secret or runtime-state filename")
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for value in forbidden_paths:
            if value in text:
                fail(errors, path, f"contains private or machine-specific path marker: {value}")
        for phrase in stale_phrases:
            if phrase in text:
                fail(errors, path, f"contains stale public-repository wording: {phrase}")
        for label, pattern in machine_path_patterns.items():
            if pattern.search(text):
                fail(errors, path, f"contains machine-specific {label}")
        for label, pattern in secret_patterns.items():
            if pattern.search(text):
                fail(errors, path, f"contains possible {label}")


def main() -> int:
    errors: list[str] = []
    descriptions: dict[str, str] = {}
    skill_dirs = sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())
    if not skill_dirs:
        errors.append("skills: no skill directories found")

    for skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            fail(errors, skill_md, "missing SKILL.md")
            continue
        name, description = read_frontmatter(skill_md, errors)
        if name and name != skill_dir.name:
            fail(errors, skill_md, f"name {name} does not match directory {skill_dir.name}")
        if name:
            descriptions[name] = description
            validate_openai_yaml(skill_dir, name, errors)


    for owner_trigger, owner in TRIGGER_OWNERS.items():
        for skill_name, description in descriptions.items():
            contains = owner_trigger.lower() in description.lower()
            if skill_name == owner and not contains:
                errors.append(f"skills/{skill_name}/SKILL.md: description must own trigger {owner_trigger}")
            elif skill_name != owner and contains:
                errors.append(
                    f"skills/{skill_name}/SKILL.md: description conflicts with {owner} trigger {owner_trigger}"
                )

    auth_marker = "gh auth status -h github.com"
    for skill_name in sorted(GITHUB_AUTH_SKILLS):
        path = SKILLS_DIR / skill_name / "SKILL.md"
        if auth_marker not in path.read_text(encoding="utf-8"):
            fail(errors, path, "missing GitHub authentication preflight")

    visual_text = (SKILLS_DIR / "visual-verify" / "SKILL.md").read_text(encoding="utf-8")
    for requirement in ("narrow viewport", "horizontal overflow", "viewport clipping"):
        if requirement not in visual_text:
            errors.append(f"skills/visual-verify/SKILL.md: missing visual check: {requirement}")

    for path in markdown_files(ROOT):
        validate_local_links(path, errors)
    validate_public_content(errors)

    if errors:
        print("Skill validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(skill_dirs)} skills with metadata, references, safety, and trigger checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

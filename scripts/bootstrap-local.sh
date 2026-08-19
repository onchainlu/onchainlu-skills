#!/bin/sh

set -eu

repo_root=$(
  CDPATH=
  cd -- "$(dirname -- "$0")/.."
  pwd
)
expected_root="$HOME/.agents"

if [ "$repo_root" != "$expected_root" ]; then
  printf 'Expected this repository at %s, found %s\n' "$expected_root" "$repo_root" >&2
  exit 1
fi

mkdir -p "$HOME/.claude/skills"

for skill_md in "$repo_root"/skills/*/SKILL.md; do
  [ -f "$skill_md" ] || continue
  skill_dir=$(dirname -- "$skill_md")
  skill_name=$(basename -- "$skill_dir")
  claude_target="$HOME/.claude/skills/$skill_name"

  if [ -L "$claude_target" ]; then
    current_target=$(readlink "$claude_target")
    if [ "$current_target" = "$skill_dir" ]; then
      continue
    fi
    printf 'Skipped %s: existing symlink points to %s\n' "$skill_name" "$current_target" >&2
    continue
  fi

  if [ -e "$claude_target" ]; then
    printf 'Skipped %s: existing path is not a symlink\n' "$skill_name" >&2
    continue
  fi

  ln -s "$skill_dir" "$claude_target"
done

if command -v hermes >/dev/null 2>&1; then
  hermes config set skills.external_dirs "$repo_root/skills"
else
  printf 'Hermes is not installed; skipped Hermes configuration.\n' >&2
fi

printf 'Shared skills are available from %s\n' "$repo_root/skills"

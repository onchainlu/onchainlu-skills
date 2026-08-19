#!/bin/sh

set -eu

repo="onchainlu/onchainlu-skills"
repo_root=$(
  CDPATH=
  cd -- "$(dirname -- "$0")/.."
  pwd
)

if ! command -v hermes >/dev/null 2>&1; then
  printf 'Hermes is not installed in this environment.\n' >&2
  exit 1
fi

if [ -z "${GITHUB_TOKEN:-}" ]; then
  printf 'GITHUB_TOKEN is required with read-only access to %s.\n' "$repo" >&2
  exit 1
fi

hermes skills tap add "$repo"

for skill_md in "$repo_root"/skills/*/SKILL.md; do
  [ -f "$skill_md" ] || continue
  skill_name=$(basename -- "$(dirname -- "$skill_md")")
  hermes skills install "$repo/$skill_name" --yes
done

printf 'Installed shared skills from %s.\n' "$repo"

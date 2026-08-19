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

hermes skills tap add "$repo"

hermes_home=${HERMES_HOME:-"$HOME/.hermes"}
missing_skills=""

for skill_md in "$repo_root"/skills/*/SKILL.md; do
  [ -f "$skill_md" ] || continue
  skill_name=$(basename -- "$(dirname -- "$skill_md")")
  hermes skills install "$repo/$skill_name" --yes
  if [ ! -f "$hermes_home/skills/$skill_name/SKILL.md" ]; then
    if [ -n "$missing_skills" ]; then
      missing_skills="$missing_skills $skill_name"
    else
      missing_skills="$skill_name"
    fi
  fi
done

if [ -n "$missing_skills" ]; then
  printf 'Hermes did not install: %s\n' "$missing_skills" >&2
  printf 'Review the security findings; this script never bypasses a blocked verdict.\n' >&2
  exit 1
fi

printf 'Installed shared skills from %s.\n' "$repo"

#!/bin/sh

set -eu

repo_root=$(
  CDPATH=
  cd -- "$(dirname -- "$0")/.."
  pwd
)

python3 "$repo_root/scripts/validate-skills.py"

for shell_script in "$repo_root"/scripts/*.sh; do
  [ -f "$shell_script" ] || continue
  sh -n "$shell_script"
done

if ! command -v shellcheck >/dev/null 2>&1; then
  printf 'shellcheck is required to validate shell scripts.\n' >&2
  exit 1
fi

shellcheck "$repo_root"/scripts/*.sh
git -C "$repo_root" diff --check

printf 'Repository validation passed.\n'

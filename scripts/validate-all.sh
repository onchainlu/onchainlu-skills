#!/bin/sh

set -eu

repo_root=$(
  CDPATH=
  cd -- "$(dirname -- "$0")/.."
  pwd
)

tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT HUP INT TERM

python3 "$repo_root/scripts/test-validate-skills.py"
python3 "$repo_root/scripts/validate-skills.py"

shell_list="$tmp_dir/shell-scripts.txt"
find "$repo_root/scripts" "$repo_root/skills" -type f -name '*.sh' -print >"$shell_list"

while IFS= read -r shell_script; do
  [ -n "$shell_script" ] || continue
  IFS= read -r first_line <"$shell_script" || true
  case "$first_line" in
    *bash*) bash -n "$shell_script" ;;
    *) sh -n "$shell_script" ;;
  esac
done <"$shell_list"

version=0.10.0
expected=6c881ab0698e4e6ea235245f22832860544f17ba386442fe7e9d629f8cbedf87
shellcheck_bin=$(command -v shellcheck || true)
if [ -n "$shellcheck_bin" ] &&
   "$shellcheck_bin" --version | grep -q "^version: ${version}$"; then
  :
elif [ "$(uname -s)" = Linux ] && [ "$(uname -m)" = x86_64 ]; then
  archive="$tmp_dir/shellcheck.tar.xz"
  curl --fail --location --silent --show-error \
    --connect-timeout 15 --max-time 120 \
    "https://github.com/koalaman/shellcheck/releases/download/v${version}/shellcheck-v${version}.linux.x86_64.tar.xz" \
    --output "$archive"
  actual=$(sha256sum "$archive" | cut -d ' ' -f 1)
  if [ "$actual" != "$expected" ]; then
    printf 'shellcheck archive checksum mismatch.\n' >&2
    exit 1
  fi
  tar -xJf "$archive" -C "$tmp_dir"
  shellcheck_bin="$tmp_dir/shellcheck-v${version}/shellcheck"
else
  printf 'shellcheck %s is required on this platform.\n' "$version" >&2
  exit 1
fi

while IFS= read -r shell_script; do
  [ -n "$shell_script" ] || continue
  "$shellcheck_bin" "$shell_script"
done <"$shell_list"

git -C "$repo_root" diff --check
if [ "${CI:-}" = true ] && [ -n "${GITHUB_BASE_REF:-}" ]; then
  git -C "$repo_root" diff --check "origin/${GITHUB_BASE_REF}...HEAD"
fi

printf 'Repository validation passed.\n'

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
python3 "$repo_root/scripts/test-functional-test-env.py"
python3 "$repo_root/scripts/validate-skills.py"
python3 "$repo_root/scripts/run-functional-tests.py" \
  "$repo_root/skills/pdf/tests/test_pdf_skill.py" \
  "$repo_root/skills/xlsx/tests/test_xlsx_skill.py"

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
shellcheck_bin=$(command -v shellcheck || true)
if [ -n "$shellcheck_bin" ] &&
   "$shellcheck_bin" --version | grep -q "^version: ${version}$"; then
  :
else
  case "$(uname -s):$(uname -m)" in
    Linux:x86_64)
      target=linux.x86_64
      expected=6c881ab0698e4e6ea235245f22832860544f17ba386442fe7e9d629f8cbedf87
      ;;
    Linux:aarch64|Linux:arm64)
      target=linux.aarch64
      expected=324a7e89de8fa2aed0d0c28f3dab59cf84c6d74264022c00c22af665ed1a09bb
      ;;
    Darwin:x86_64)
      target=darwin.x86_64
      expected=ef27684f23279d112d8ad84e0823642e43f838993bbb8c0963db9b58a90464c2
      ;;
    Darwin:arm64|Darwin:aarch64)
      target=darwin.aarch64
      expected=bbd2f14826328eee7679da7221f2bc3afb011f6a928b848c80c321f6046ddf81
      ;;
    *)
      printf 'shellcheck %s is required on this platform.\n' "$version" >&2
      exit 1
      ;;
  esac
  archive="$tmp_dir/shellcheck.tar.xz"
  curl --fail --location --silent --show-error \
    --connect-timeout 15 --max-time 120 \
    "https://github.com/koalaman/shellcheck/releases/download/v${version}/shellcheck-v${version}.${target}.tar.xz" \
    --output "$archive"
  actual=$(python3 - "$archive" <<'PY'
import hashlib
import sys

with open(sys.argv[1], "rb") as archive_file:
    print(hashlib.file_digest(archive_file, "sha256").hexdigest())
PY
  )
  if [ "$actual" != "$expected" ]; then
    printf 'shellcheck archive checksum mismatch.\n' >&2
    exit 1
  fi
  tar -xJf "$archive" -C "$tmp_dir"
  shellcheck_bin="$tmp_dir/shellcheck-v${version}/shellcheck"
fi

while IFS= read -r shell_script; do
  [ -n "$shell_script" ] || continue
  "$shellcheck_bin" "$shell_script"
done <"$shell_list"

git -C "$repo_root" diff --check
if [ "${CI:-}" = true ]; then
  empty_tree=$(git -C "$repo_root" hash-object -t tree /dev/null)
  git -C "$repo_root" diff --check "$empty_tree" HEAD
fi

printf 'Repository validation passed.\n'

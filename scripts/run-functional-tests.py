#!/usr/bin/env python3
"""Run dependency-backed tests in a disposable, hash-locked environment."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence

INSTALL_TIMEOUT_SECONDS = 300
COMMAND_TIMEOUT_SECONDS = 300


def environment_python(environment: Path) -> Path:
    """Return the Python executable created by venv on POSIX or Windows."""
    candidates = (
        environment / "bin" / "python",
        environment / "Scripts" / "python.exe",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise RuntimeError("virtual environment did not provide Python")


def run(repo_root: Path, tests: Sequence[Path], base_python: str) -> None:
    """Create an isolated environment, install locked dependencies, and test."""
    environment = Path(tempfile.mkdtemp(prefix="onchainlu-skills-tests-"))
    try:
        subprocess.run(
            [base_python, "-m", "venv", str(environment)],
            check=True,
            timeout=60,
        )
        python = environment_python(environment)
        subprocess.run(
            [
                str(python),
                "-m",
                "pip",
                "--isolated",
                "install",
                "--require-virtualenv",
                "--disable-pip-version-check",
                "--no-input",
                "--require-hashes",
                "--timeout",
                "15",
                "--retries",
                "2",
                "-r",
                str(repo_root / "requirements-ci.txt"),
            ],
            check=True,
            timeout=INSTALL_TIMEOUT_SECONDS,
        )
        subprocess.run(
            [
                str(python),
                "-m",
                "pytest",
                "-q",
                "-p",
                "no:cacheprovider",
                *(str(test) for test in tests),
            ],
            check=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
    finally:
        shutil.rmtree(environment)


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    tests = [Path(argument).resolve() for argument in sys.argv[1:]]
    if not tests:
        print("functional test paths are required", file=sys.stderr)
        return 2
    base_python = os.environ.get("VALIDATION_PYTHON", sys.executable)
    try:
        run(repo_root, tests, base_python)
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"isolated test environment failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

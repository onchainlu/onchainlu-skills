#!/usr/bin/env python3
"""Regression tests for the isolated functional-test environment."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).with_name("run-functional-tests.py")
SPEC = importlib.util.spec_from_file_location("run_functional_tests", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class FunctionalTestEnvironmentTests(unittest.TestCase):
    def test_selects_posix_or_windows_environment_python(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            environment = Path(directory)
            posix_python = environment / "bin" / "python"
            posix_python.parent.mkdir()
            posix_python.touch()
            self.assertEqual(MODULE.environment_python(environment), posix_python)

            posix_python.unlink()
            windows_python = environment / "Scripts" / "python.exe"
            windows_python.parent.mkdir()
            windows_python.touch()
            self.assertEqual(MODULE.environment_python(environment), windows_python)

    def test_uses_selected_python_and_removes_environment(self) -> None:
        calls: list[tuple[list[str], dict[str, object]]] = []
        created_environment: Path | None = None

        def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            nonlocal created_environment
            calls.append((command, kwargs))
            if command[1:3] == ["-m", "venv"]:
                created_environment = Path(command[3])
                environment_python = created_environment / "bin" / "python"
                environment_python.parent.mkdir(parents=True)
                environment_python.touch()
            return subprocess.CompletedProcess(command, 0)

        with patch.object(MODULE.subprocess, "run", side_effect=fake_run):
            MODULE.run(Path("/repo"), [Path("one.py"), Path("two.py")], "chosen-python")

        self.assertIsNotNone(created_environment)
        assert created_environment is not None
        self.assertFalse(created_environment.exists())
        self.assertEqual(calls[0][0][0:3], ["chosen-python", "-m", "venv"])
        install = calls[1]
        self.assertEqual(install[0][0], str(created_environment / "bin" / "python"))
        self.assertIn("--require-hashes", install[0])
        self.assertEqual(install[1]["timeout"], MODULE.INSTALL_TIMEOUT_SECONDS)
        self.assertEqual(os.environ.get("PIP_REQUIRE_VIRTUALENV"), None)
        self.assertEqual(calls[2][0][1:5], ["-m", "pytest", "-q", "-p"])

    def test_removes_environment_when_installation_fails(self) -> None:
        created_environment: Path | None = None

        def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            nonlocal created_environment
            if command[1:3] == ["-m", "venv"]:
                created_environment = Path(command[3])
                environment_python = created_environment / "bin" / "python"
                environment_python.parent.mkdir(parents=True)
                environment_python.touch()
                return subprocess.CompletedProcess(command, 0)
            raise subprocess.CalledProcessError(1, command)

        with patch.object(MODULE.subprocess, "run", side_effect=fake_run):
            with self.assertRaises(subprocess.CalledProcessError):
                MODULE.run(Path("/repo"), [Path("test.py")], "python3")

        self.assertIsNotNone(created_environment)
        assert created_environment is not None
        self.assertFalse(created_environment.exists())

    def test_reports_missing_environment_python(self) -> None:
        def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(command, 0)

        with patch.object(MODULE.subprocess, "run", side_effect=fake_run):
            with self.assertRaisesRegex(RuntimeError, "virtual environment did not provide Python"):
                MODULE.run(Path("/repo"), [Path("test.py")], "python3")


if __name__ == "__main__":
    unittest.main()

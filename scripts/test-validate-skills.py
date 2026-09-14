#!/usr/bin/env python3
"""Regression tests for repository skill validation."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).with_name("validate-skills.py")
SPEC = importlib.util.spec_from_file_location("validate_skills", SCRIPT)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class MarkdownLinkTests(unittest.TestCase):
    def test_nested_missing_link_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            nested = root / "skills" / "demo" / "references" / "nested.md"
            nested.parent.mkdir(parents=True)
            nested.write_text("[missing](../absent.md)\n", encoding="utf-8")
            errors: list[str] = []
            with patch.object(VALIDATOR, "ROOT", root):
                VALIDATOR.validate_local_links(nested, errors)
            self.assertEqual(len(errors), 1)
            self.assertIn("missing local link target", errors[0])

    def test_relative_encoded_and_reference_links_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            refs = root / "skills" / "demo" / "references"
            refs.mkdir(parents=True)
            (root / "skills" / "demo" / "target file.md").write_text("ok\n", encoding="utf-8")
            (refs / "sibling.md").write_text("ok\n", encoding="utf-8")
            nested = refs / "nested.md"
            nested.write_text(
                "[sibling](sibling.md)\n[parent](../target%20file.md)\n"
                "[reference][target]\n[target]: ../target%20file.md\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            with patch.object(VALIDATOR, "ROOT", root):
                VALIDATOR.validate_local_links(nested, errors)
            self.assertEqual(errors, [])

    def test_balanced_parentheses_in_destination_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            page = root / "docs" / "index.md"
            page.parent.mkdir(parents=True)
            (page.parent / "file_(v1).md").write_text("ok\n", encoding="utf-8")
            page.write_text("[version](file_(v1).md)\n", encoding="utf-8")
            errors: list[str] = []
            with patch.object(VALIDATOR, "ROOT", root):
                VALIDATOR.validate_local_links(page, errors)
            self.assertEqual(errors, [])

    def test_link_escape_fails_even_when_target_exists(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            nested = root / "skills" / "demo" / "nested.md"
            nested.parent.mkdir(parents=True)
            outside = root.parent / "outside.md"
            outside.write_text("outside\n", encoding="utf-8")
            nested.write_text("[outside](../../../outside.md)\n", encoding="utf-8")
            errors: list[str] = []
            with patch.object(VALIDATOR, "ROOT", root):
                VALIDATOR.validate_local_links(nested, errors)
            self.assertEqual(len(errors), 1)
            self.assertIn("escapes repository", errors[0])

    def test_encoded_link_escape_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            page = root / "docs" / "index.md"
            page.parent.mkdir(parents=True)
            (root.parent / "outside.md").write_text("outside\n", encoding="utf-8")
            page.write_text("[outside](%2e%2e/%2e%2e/outside.md)\n", encoding="utf-8")
            errors: list[str] = []
            with patch.object(VALIDATOR, "ROOT", root):
                VALIDATOR.validate_local_links(page, errors)
            self.assertEqual(len(errors), 1)
            self.assertIn("escapes repository", errors[0])

    def test_markdown_discovery_is_repository_wide(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            expected = {root / "AGENTS.md", root / "skills" / "demo" / "nested.md"}
            for path in expected:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("ok\n", encoding="utf-8")
            hidden = root / ".git" / "ignored.md"
            hidden.parent.mkdir()
            hidden.write_text("ignored\n", encoding="utf-8")
            self.assertEqual(set(VALIDATOR.markdown_files(root)), expected)


class PublicContentTests(unittest.TestCase):
    def test_unlisted_text_extension_is_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            marker = "/" + "opt/data/private/state"
            (root / "proof.toml").write_text(f'path = "{marker}"\n', encoding="utf-8")
            errors: list[str] = []
            with patch.object(VALIDATOR, "ROOT", root):
                VALIDATOR.validate_public_content(errors)
            self.assertEqual(len(errors), 1)
            self.assertIn("machine-specific path marker", errors[0])


if __name__ == "__main__":
    unittest.main()

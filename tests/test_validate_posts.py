"""Unit tests for scripts/validate_posts.py."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_posts import validate


class ValidatePostsTests(unittest.TestCase):
    def validate_value(self, value: object) -> list[str]:
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            path = Path(directory) / "posts.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            return validate(path)

    def test_accepts_required_fields_without_optional_sources(self) -> None:
        post = {"n": 1, "c": 1, "t": "Claim", "v": "Check"}

        self.assertEqual(self.validate_value([post]), [])

    def test_accepts_optional_http_and_https_sources(self) -> None:
        post = {
            "n": 2,
            "c": 3,
            "t": "Claim",
            "v": "Check",
            "s": ["https://example.com/source", "http://example.org/report"],
        }

        self.assertEqual(self.validate_value([post]), [])

    def test_accepts_empty_feed_and_unrecognized_extra_fields(self) -> None:
        post = {"n": 1, "c": 2, "t": "Claim", "v": "Check", "future": True}

        self.assertEqual(self.validate_value([]), [])
        self.assertEqual(self.validate_value([post]), [])

    def test_rejects_non_array_root_and_non_object_entries(self) -> None:
        root_errors = self.validate_value({})
        entry_errors = self.validate_value([None])

        self.assertTrue(any("top-level value must be an array" in error for error in root_errors))
        self.assertTrue(any("each post must be an object" in error for error in entry_errors))

    def test_requires_n_c_t_and_v(self) -> None:
        for field in ("n", "c", "t", "v"):
            with self.subTest(field=field):
                post = {"n": 1, "c": 1, "t": "Claim", "v": "Check"}
                del post[field]

                errors = self.validate_value([post])

                self.assertTrue(any(f"[0].{field}:" in error for error in errors))

    def test_rejects_unknown_candidate_and_check_values(self) -> None:
        for field, value in (("n", 3), ("c", 0)):
            with self.subTest(field=field, value=value):
                post = {"n": 1, "c": 1, "t": "Claim", "v": "Check"}
                post[field] = value
                self.assertTrue(self.validate_value([post]))

    def test_rejects_boolean_as_candidate_or_check_number(self) -> None:
        for field in ("n", "c"):
            with self.subTest(field=field):
                post = {"n": 1, "c": 1, "t": "Claim", "v": "Check"}
                post[field] = True
                self.assertTrue(self.validate_value([post]))

    def test_rejects_non_string_claim_or_verification(self) -> None:
        for field in ("t", "v"):
            with self.subTest(field=field):
                post = {"n": 1, "c": 1, "t": "Claim", "v": "Check"}
                post[field] = 42
                self.assertTrue(self.validate_value([post]))

    def test_optional_sources_must_be_an_array_of_valid_http_urls(self) -> None:
        invalid_sources = (
            "https://example.com",
            ["javascript:alert(1)"],
            ["https://"],
            ["https://example.com:99999/path"],
            [42],
        )
        for sources in invalid_sources:
            with self.subTest(sources=sources):
                post = {
                    "n": 1,
                    "c": 1,
                    "t": "Claim",
                    "v": "Check",
                    "s": sources,
                }
                self.assertTrue(self.validate_value([post]))

    def test_rejects_invalid_json_constants(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            path = Path(directory) / "posts.json"
            path.write_text("[NaN]", encoding="utf-8")

            errors = validate(path)

        self.assertTrue(any("could not read valid JSON" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

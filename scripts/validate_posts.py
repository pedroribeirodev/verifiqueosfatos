#!/usr/bin/env python3
"""Validate the shape of the site's posts.json using only the Python stdlib."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlsplit


VALID_CANDIDATES = {1, 2}
VALID_CHECKS = {1, 2, 3}


def reject_non_json_constant(value: str) -> None:
    raise ValueError(f"{value} is not a valid JSON value")


def valid_http_url(value: object) -> bool:
    if not isinstance(value, str) or any(character.isspace() for character in value):
        return False

    try:
        parsed = urlsplit(value)
        # Accessing .port also validates that a supplied port is numeric and in range.
        _ = parsed.port
    except ValueError:
        return False

    return parsed.scheme.lower() in {"http", "https"} and bool(parsed.hostname)


def validate(path: Path) -> list[str]:
    try:
        with path.open("r", encoding="utf-8") as source:
            posts = json.load(source, parse_constant=reject_non_json_constant)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        return [f"{path}: could not read valid JSON ({error})"]

    if not isinstance(posts, list):
        return [f"{path}: top-level value must be an array"]

    errors: list[str] = []
    for index, post in enumerate(posts):
        location = f"{path}[{index}]"
        if not isinstance(post, dict):
            errors.append(f"{location}: each post must be an object")
            continue

        candidate = post.get("n")
        if type(candidate) is not int or candidate not in VALID_CANDIDATES:
            errors.append(f"{location}.n: expected 1 (Lula) or 2 (Flávio)")

        check = post.get("c")
        if type(check) is not int or check not in VALID_CHECKS:
            errors.append(f"{location}.c: expected 1 (true), 2 (false), or 3 (partial)")

        for field in ("t", "v"):
            if not isinstance(post.get(field), str):
                errors.append(f"{location}.{field}: expected a string")

        if "s" in post:
            sources = post["s"]
            if not isinstance(sources, list):
                errors.append(f"{location}.s: expected an array of http(s) URLs")
            else:
                for source_index, url in enumerate(sources):
                    if not valid_http_url(url):
                        errors.append(
                            f"{location}.s[{source_index}]: expected a valid http(s) URL"
                        )

    return errors


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("posts.json")
    errors = validate(path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"{path}: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

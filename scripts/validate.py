#!/usr/bin/env python3
"""Validate Wineforge recipes against their versioned schema and invariants."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "v1" / "recipe.schema.json"
RECIPES_PATH = ROOT / "recipes" / "v1"


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def json_path(parts: list[Any]) -> str:
    if not parts:
        return "$"
    rendered = "$"
    for part in parts:
        rendered += f"[{part}]" if isinstance(part, int) else f".{part}"
    return rendered


def semantic_errors(recipe: dict[str, Any]) -> list[str]:
    """Check cross-field invariants JSON Schema cannot express clearly."""
    errors: list[str] = []

    source_ids = [source["id"] for source in recipe.get("sources", [])]
    duplicates = sorted({item for item in source_ids if source_ids.count(item) > 1})
    if duplicates:
        errors.append(f"$.sources: duplicate source ids: {', '.join(duplicates)}")

    available_sources = set(source_ids)
    for index, step in enumerate(recipe.get("install", [])):
        source = step.get("source")
        if source is not None and source not in available_sources:
            errors.append(
                f"$.install[{index}].source: unknown source id {source!r}"
            )

    variants = [
        (item["platform"], item["hostArchitecture"], item["translation"])
        for item in recipe.get("variants", [])
    ]
    duplicate_variants = sorted(
        {item for item in variants if variants.count(item) > 1}
    )
    for platform, architecture, translation in duplicate_variants:
        errors.append(
            "$.variants: duplicate target "
            f"{platform}/{architecture}/{translation}"
        )

    return errors


def validate_document(
    document: Any, validator: Draft202012Validator
) -> list[str]:
    errors = [
        f"{json_path(list(error.absolute_path))}: {error.message}"
        for error in sorted(validator.iter_errors(document), key=lambda item: list(item.path))
    ]
    if not errors and isinstance(document, dict):
        errors.extend(semantic_errors(document))
    return errors


def build_validator() -> Draft202012Validator:
    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args()

    try:
        validator = build_validator()
    except (OSError, json.JSONDecodeError, SchemaError) as error:
        print(f"schema error: {error}", file=sys.stderr)
        return 2

    paths = args.paths or sorted(RECIPES_PATH.glob("*.json"))
    if not paths:
        print("no recipe files found", file=sys.stderr)
        return 2

    failed = False
    for path in paths:
        try:
            document = load_json(path)
            errors = validate_document(document, validator)
        except (OSError, json.JSONDecodeError) as error:
            errors = [str(error)]

        if errors:
            failed = True
            print(f"FAIL {path}")
            for error in errors:
                print(f"  {error}")
        else:
            print(f"OK   {path}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())


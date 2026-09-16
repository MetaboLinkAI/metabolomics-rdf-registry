#!/usr/bin/env python3
"""Validate registry YAML files without probing external infrastructure."""

from __future__ import annotations

import glob
import json
import os
import sys
from collections import Counter
from pathlib import Path

import yaml
from jsonschema import Draft7Validator, FormatChecker

SCHEMA_PATH = Path("schema/endpoint.schema.json")
DATA_GLOB = "data/endpoints/*.yaml"
SKIP_FILES = {"example-endpoint.yaml"}


def format_path(error) -> str:
    path = ".".join(str(part) for part in error.absolute_path)
    return path or "<root>"


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft7Validator(schema, format_checker=FormatChecker())

    files = [
        Path(path)
        for path in sorted(glob.glob(DATA_GLOB))
        if os.path.basename(path) not in SKIP_FILES
    ]
    if not files:
        print("No endpoint files found under data/endpoints/.")
        return 1

    errors: list[str] = []
    ids: list[str] = []
    empty_namespace_count = 0
    unspecified_license_count = 0
    charted_without_map_count = 0

    for path in files:
        try:
            entry = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"{path}: invalid YAML: {exc}")
            continue

        if not isinstance(entry, dict):
            errors.append(f"{path}: document must be a YAML mapping/object")
            continue

        schema_errors = sorted(
            validator.iter_errors(entry),
            key=lambda error: list(error.absolute_path),
        )
        for error in schema_errors:
            errors.append(f"{path}: {format_path(error)}: {error.message}")

        entry_id = entry.get("id")
        if isinstance(entry_id, str):
            ids.append(entry_id)
            if path.stem != entry_id:
                errors.append(
                    f"{path}: filename must match id '{entry_id}' "
                    f"(expected data/endpoints/{entry_id}.yaml)"
                )

        # Legacy records may leave optional fields as empty strings. This is
        # accepted for now, but available resources must have a real URL.
        if entry.get("endpoint_available") and not entry.get("endpoint_url"):
            errors.append(f"{path}: endpoint_available is true but endpoint_url is empty")
        if entry.get("dump_available") and not entry.get("dump_url"):
            errors.append(f"{path}: dump_available is true but dump_url is empty")
        if not entry.get("endpoint_available") and not entry.get("dump_available"):
            errors.append(f"{path}: at least one RDF access route must be available")

        if entry.get("charted") and (not entry.get("map_rdf") or not entry.get("map_view")):
            charted_without_map_count += 1
        if not entry.get("namespace"):
            empty_namespace_count += 1
        if entry.get("license") == "unspecified":
            unspecified_license_count += 1

        if not schema_errors:
            print(f"OK  {path}")

    duplicates = [entry_id for entry_id, count in Counter(ids).items() if count > 1]
    for entry_id in sorted(duplicates):
        errors.append(f"duplicate id found: {entry_id}")

    if errors:
        print("\nValidation errors:")
        for error in errors:
            print(f"ERROR {error}")
        print(f"\n{len(errors)} validation error(s).")
        return 1

    print(f"\nValidated {len(files)} registry entries.")
    debt = []
    if charted_without_map_count:
        debt.append(f"{charted_without_map_count} charted entries without both published map links")
    if empty_namespace_count:
        debt.append(f"{empty_namespace_count} entries with an empty namespace")
    if unspecified_license_count:
        debt.append(f"{unspecified_license_count} entries with an unspecified dataset license")
    if debt:
        print("Non-blocking metadata debt: " + "; ".join(debt) + ".")
    return 0


if __name__ == "__main__":
    sys.exit(main())

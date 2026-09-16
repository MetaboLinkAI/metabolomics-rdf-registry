#!/usr/bin/env python3
"""
Compile all data/endpoints/*.yaml files into a single data.json used by index.html.

Usage:
    python scripts/build_site.py
"""
import glob
import json

import yaml

DATA_GLOB = "data/endpoints/*.yaml"
OUTPUT = "data.json"


def main():
    entries = []
    for path in sorted(glob.glob(DATA_GLOB)):
        if path.endswith("example-endpoint.yaml"):
            continue
        with open(path) as f:
            entry = yaml.safe_load(f)
            entries.append(entry)

    with open(OUTPUT, "w") as f:
        json.dump(entries, f, indent=2)

    print(f"Wrote {len(entries)} entries to {OUTPUT}")


if __name__ == "__main__":
    main()

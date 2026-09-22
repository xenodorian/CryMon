#!/usr/bin/env python3
"""Validate progression requirements referenced by Town Map edges.

Ensures that map requirements are declared consistently so generated maps do
not advertise unreachable destinations because of unknown progression flags.
"""

import json
import sys
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text())


def main():
    town_path = sys.argv[1] if len(sys.argv) > 1 else "content/town_map.json"
    town = load(town_path)

    errors = []
    requirements = set()

    for edge in town.get("edges", []):
        need = edge.get("need")
        if need:
            requirements.add(need)

    # Current progression registry. Future versions should move this into
    # canonical world data rather than maintaining it here.
    known_flags = {
        "beatCalder",
        "beatShin",
        "hasScroll",
        "choseHeavenfall",
    }

    for requirement in sorted(requirements):
        if requirement not in known_flags:
            errors.append(f"unknown progression requirement: {requirement}")

    print("PROGRESSION REQUIREMENT REPORT")
    print(f"Requirements found: {len(requirements)}")

    if errors:
        print("\nProblems:")
        for error in errors:
            print(f"- {error}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

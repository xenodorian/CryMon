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
    flags_path = sys.argv[2] if len(sys.argv) > 2 else "tools/world_graph/progression_flags.json"
    town = load(town_path)
    registry = load(flags_path)

    errors = []
    warnings = []
    requirements = set()

    for edge in town.get("edges", []):
        need = edge.get("need")
        if need:
            requirements.add(need)

    flag_entries = registry.get("flags", {})
    known_flags = set(flag_entries.keys())

    # Duplicate flag ids: two different flag names sharing the same
    # numeric id would mean the registry can't tell them apart.
    ids_seen = {}
    for name, flag_id in flag_entries.items():
        if flag_id in ids_seen:
            errors.append(
                f"duplicate progression flag id {flag_id}: {ids_seen[flag_id]!r} and {name!r}"
            )
        else:
            ids_seen[flag_id] = name

    for requirement in sorted(requirements):
        if requirement not in known_flags:
            errors.append(f"unknown progression requirement: {requirement}")

    # Unused: declared in the registry but never gates a Town Map edge.
    # Not necessarily dead in-game (a flag can gate a battle or dialogue
    # beat without gating a Town Map route) -- flagged as a warning, not
    # an error, so it doesn't block CI for a legitimately non-map flag.
    for name in sorted(known_flags - requirements):
        warnings.append(
            f"progression flag declared but not used by any Town Map edge: {name} "
            "(may still gate non-map content -- verify before removing)"
        )

    print("PROGRESSION REQUIREMENT REPORT")
    print(f"Registry flags: {len(known_flags)}")
    print(f"Town Map edge requirements: {len(requirements)}")

    if errors:
        print("\nProblems:")
        for error in errors:
            print(f"- {error}")

    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"- {warning}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

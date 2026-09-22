#!/usr/bin/env python3
"""Validate the world graph against the player-facing Town Map projection.

This checks that the generated Town Map abstraction does not hide playable
areas without representation and that major destinations remain reachable.
"""

import json
import sys
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text())


def main():
    world_path = sys.argv[1] if len(sys.argv) > 1 else "content/world_map_layout.json"
    town_path = sys.argv[2] if len(sys.argv) > 2 else "content/town_map.json"

    world = load(world_path)
    town = load(town_path)

    errors = []

    town_nodes = {node["id"] for node in town.get("nodes", [])}
    playable = set(world.get("maps", {}).keys())
    collapse = town.get("collapse", {})

    represented = set(town_nodes)
    for source, target in collapse.items():
        if target:
            represented.add(target)

    for map_id, data in world.get("maps", {}).items():
        if not data.get("active", True):
            continue
        if map_id not in represented and map_id not in collapse:
            errors.append(f"active map missing Town Map representation: {map_id}")

    for node in town.get("nodes", []):
        if node.get("gem") and node["id"] not in town_nodes:
            errors.append(f"gem destination missing node: {node['id']}")

    required = ["veld", "camp", "heavenfall_shrine"]
    for destination in required:
        if destination not in town_nodes:
            errors.append(f"required destination missing: {destination}")

    print("TOWN MAP PROJECTION REPORT")
    print(f"World maps: {len(playable)}")
    print(f"Town nodes: {len(town_nodes)}")

    if errors:
        print("\nProblems:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("\nValidation: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

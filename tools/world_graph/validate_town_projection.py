#!/usr/bin/env python3
"""Validate the world graph against the player-facing Town Map projection.

Checks that the generated Town Map abstraction does not hide playable areas,
that collapsed regions resolve correctly, and that visible destinations have
valid world graph support.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, deque


def load(path):
    return json.loads(Path(path).read_text())


def main():
    world_path = sys.argv[1] if len(sys.argv) > 1 else "content/world_map_layout.json"
    town_path = sys.argv[2] if len(sys.argv) > 2 else "content/town_map.json"

    world = load(world_path)
    town = load(town_path)

    errors = []
    warnings = []

    town_nodes = {node["id"] for node in town.get("nodes", [])}
    playable = set(world.get("maps", {}).keys())
    collapse = town.get("collapse", {})

    represented = set(town_nodes)
    for source, target in collapse.items():
        if target:
            represented.add(target)
            if target not in town_nodes:
                errors.append(f"collapse target missing Town Map node: {source} -> {target}")

    for map_id, data in world.get("maps", {}).items():
        if not data.get("active", True):
            continue
        if map_id not in represented and map_id not in collapse:
            errors.append(f"active map missing Town Map representation: {map_id}")

    collapsed_sources = set(collapse.keys())
    for node_id in town_nodes:
        if node_id not in playable and node_id not in collapsed_sources:
            warnings.append(f"Town Map node has no direct playable map or collapse source: {node_id}")

    # Validate visible graph endpoints.
    graph = defaultdict(set)
    for edge in town.get("edges", []):
        graph[edge["from"]].add(edge["to"])
        graph[edge["to"]].add(edge["from"])

    anchor = town.get("anchor", "veld")
    reachable = set()
    queue = deque([anchor])
    while queue:
        current = queue.popleft()
        if current in reachable:
            continue
        reachable.add(current)
        queue.extend(graph[current])

    for node_id in town_nodes:
        if node_id not in reachable:
            errors.append(f"Town Map node unreachable from anchor {anchor}: {node_id}")

    # Route nodes should not silently terminate unless they are intentional gems.
    for node in town.get("nodes", []):
        if not node.get("gem") and len(graph[node["id"]]) == 0:
            warnings.append(f"route has no connection: {node['id']}")

    required = ["veld", "camp", "heavenfall_shrine"]
    for destination in required:
        if destination not in town_nodes:
            errors.append(f"required destination missing: {destination}")

    print("TOWN MAP PROJECTION REPORT")
    print(f"World maps: {len(playable)}")
    print(f"Town nodes: {len(town_nodes)}")
    print(f"Reachable nodes: {len(reachable)}")

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

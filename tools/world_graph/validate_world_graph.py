#!/usr/bin/env python3
"""Validate CryMon world connectivity.

Initial foundation for procedural Town Map tooling.
The world layout remains the source of truth.
"""

import json
import sys
from pathlib import Path


def main():
    source = Path(sys.argv[1] if len(sys.argv) > 1 else "content/world_map_layout.json")
    world = json.loads(source.read_text())

    maps = world.get("maps", {})
    connections = world.get("connections", [])

    errors = []
    graph = {name: set() for name in maps}

    for edge in connections:
        a = edge.get("from")
        b = edge.get("to")
        if a not in maps:
            errors.append(f"missing map reference: {a}")
            continue
        if b not in maps:
            errors.append(f"missing map reference: {b}")
            continue
        graph[a].add(b)
        graph[b].add(a)

    start = world.get("playerMarker", {}).get("mapId", "veld")
    seen = set()
    queue = [start]

    while queue:
        current = queue.pop(0)
        if current in seen:
            continue
        seen.add(current)
        queue.extend(graph.get(current, []))

    for name, data in maps.items():
        if data.get("active", True) and name not in seen:
            errors.append(f"unreachable active map: {name}")

    print("WORLD GRAPH REPORT")
    print(f"Maps: {len(maps)}")
    print(f"Connections: {len(connections)}")
    print(f"Reachable from {start}: {len(seen)}")

    if errors:
        print("\nProblems:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("\nValidation: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

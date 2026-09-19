#!/usr/bin/env python3
"""Assemble content/world.json from content/world_parts/*.json.

Agents edit only their part file, then run this. Do not hand-edit world.json.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "content" / "world_parts"
OUT = ROOT / "content" / "world.json"

ORDER = ["meta", "map_meta", "encounters", "warps", "trainers", "npcs"]


def load(name: str) -> dict:
    path = PARTS / f"{name}.json"
    if not path.is_file():
        raise SystemExit(f"missing part {path}")
    return json.loads(path.read_text())


def main() -> None:
    world: dict = {}
    world.update(load("meta"))
    world.update(load("map_meta"))
    world["encounters"] = load("encounters")["encounters"]
    world["warps"] = load("warps")["warps"]
    world["trainers"] = load("trainers")["trainers"]
    world["npcs"] = load("npcs")["npcs"]
    OUT.write_text(json.dumps(world, indent=2) + "\n")
    print(f"wrote {OUT} npcs={len(world['npcs'])} warps={len(world['warps'])} encounters={len(world['encounters'])} trainers={len(world['trainers'])}")


if __name__ == "__main__":
    main()

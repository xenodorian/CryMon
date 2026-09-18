#!/usr/bin/env python3
"""Fail (or warn) when Dreamcast baked includes drift from content/*.json.

    python3 tools/check_sync.py           # web turn: warn on stale bake
    python3 tools/check_sync.py --strict  # DC turn / before CDI: exit 1
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from bake_content import PACK_FILES, pack_hash  # noqa: E402
from sprite_root import stray_sprite_dirs  # noqa: E402

INC_DIR = ROOT / "ports" / "dreamcast" / "src"
SPRITES = ROOT / "public" / "sprites"
CONTENT = ROOT / "content"
HASH_RE = re.compile(r"PACK_HASH=([0-9a-f]+)")


def baked_hash() -> str | None:
    sample = INC_DIR / "content_maps.inc"
    if not sample.is_file():
        return None
    m = HASH_RE.search(sample.read_text()[:400])
    return m.group(1) if m else None


def sprite_gaps() -> list[str]:
    catalog = json.loads((CONTENT / "sprites.json").read_text())
    missing: list[str] = []
    dirs = ("down", "up", "left", "right")

    def need(rel: str) -> None:
        if not (SPRITES / rel).is_file():
            missing.append(rel)

    for folder in catalog.get("walkers", {}).values():
        for d in dirs:
            for i in range(1, 5):
                need(f"{folder}/{d}-{i}.png")
    for n in catalog.get("npcs", []):
        for i in range(1, 5):
            need(f"npc/{n}-{i}.png")
    for m in catalog.get("monsters", []):
        for i in range(1, 5):
            need(f"monsters/{m}/{i}.png")
    for p in catalog.get("portraits", []):
        need(f"portraits/{p}.png")
    for it in catalog.get("items", []):
        need(f"items/{it}.png")
    for rel in catalog.get("props", {}).values():
        need(rel)
    for pair in catalog.get("extra", []):
        rel = pair[1].split("?")[0].lstrip("/")
        if rel.startswith("sprites/"):
            rel = rel[len("sprites/") :]
        need(rel)
    return missing


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    errors: list[str] = []
    warns: list[str] = []

    for name in PACK_FILES:
        if not (CONTENT / name).is_file():
            errors.append(f"missing content/{name}")

    want = pack_hash(CONTENT) if not errors else ""
    got = baked_hash()
    if got is None:
        warns.append("no ports/dreamcast/src/content_maps.inc — bake before a CDI")
    elif got != want:
        msg = f"stale DC bake PACK_HASH={got} (content is {want}). run tools/bake_content.py"
        if args.strict:
            errors.append(msg)
        else:
            warns.append(msg)

    missing = sprite_gaps()
    if missing:
        errors.append(f"{len(missing)} sprites.json paths missing under public/sprites/ (e.g. {missing[0]})")

    stray = stray_sprite_dirs()
    if stray:
        errors.append(
            "second art tree "
            + ", ".join(stray)
            + " — write sprites only to public/sprites/"
        )

    for w in warns:
        print(f"WARN  {w}")
    for e in errors:
        print(f"FAIL  {e}")
    if not warns and not errors:
        print(f"OK    PACK_HASH={want}  {len(PACK_FILES)} json  sprites catalog complete")
        return 0
    if errors:
        return 1
    print(f"OK    PACK_HASH={want} (bake stale, not --strict)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

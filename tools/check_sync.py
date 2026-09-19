#!/usr/bin/env python3
"""Fail when the pack, bake, IDs, or live tree drift from docs/CRYMON.md.

    python3 tools/check_sync.py           # same gates as --strict
    python3 tools/check_sync.py --strict  # alias (CDI / DC turn)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from bake_content import (  # noqa: E402
    PACK_FILES,
    bake_all,
    load_pack,
    merged_flags,
    pack_hash,
    talk_table,
)
from sprite_root import stray_sprite_dirs  # noqa: E402

INC_DIR = ROOT / "ports" / "dreamcast" / "src"
SPRITES = ROOT / "public" / "sprites"
CONTENT = ROOT / "content"
SRC = ROOT / "src"
MAIN_C = INC_DIR / "main.c"
TYPES = SRC / "game" / "types.ts"
DATA_TS = SRC / "game" / "data.ts"
INC_NAMES = [
    "content_maps.inc",
    "content_talk.inc",
    "content_species.inc",
    "content_items.inc",
    "content_logic.inc",
    "content_world.inc",
    "content_audio.inc",
    "content_save.inc",
]
LIVE_ROOTS = [
    ROOT / "src",
    ROOT / "tools",
    ROOT / "content",
    ROOT / "docs",
    ROOT / "ports" / "dreamcast",
    ROOT / "AGENTS.project.md",
    ROOT / "CLAUDE.md",
]
FORBIDDEN_DIRS = ["love", "native", "snes", "crymon-dreamcast", "assets"]
FORBIDDEN_TEXT = [
    r"BeelzFight",
    r"__gemwar",
    r"gemwar-app",
    r"CRYMON_SPRITES",
]
SKIP_NAME = {".git", "node_modules", ".vercel", "backups", "__pycache__", "placeholder_sprites"}
REQUIRED_TRAINERS = ["mason", "calder", "shinigami", "cathleen", "sentry", "conscript", "enforcer", "cross"]
REQUIRED_LOGIC = ["anneGift", "party", "runtimeFlags", "natures", "combat"]


def union_members(text: str, name: str) -> list[str]:
    m = re.search(rf"export type {name}\s*=\s*([^;]+);", text, re.S)
    if not m:
        return []
    return re.findall(r'"([a-zA-Z0-9]+)"', m.group(1))


def sprite_gaps(catalog: dict) -> list[str]:
    missing: list[str] = []
    dirs = ("down", "up", "left", "right")

    def need(rel: str) -> None:
        if not (SPRITES / rel).is_file():
            missing.append(rel)

    walkers = catalog.get("walkers") or {}
    for folder in walkers.values():
        if not isinstance(folder, str):
            folder = folder.get("folder", "")
        for d in dirs:
            for i in range(1, 5):
                need(f"{folder}/{d}-{i}.png")
    for n in catalog.get("npcs") or []:
        for i in range(1, 5):
            need(f"npc/{n}-{i}.png")
    for m in catalog.get("monsters") or []:
        for i in range(1, 5):
            need(f"monsters/{m}/{i}.png")
    for p in catalog.get("portraits") or []:
        need(f"portraits/{p}.png")
    for it in catalog.get("items") or []:
        need(f"items/{it}.png")
    for rel in (catalog.get("props") or {}).values():
        need(rel)
    for pair in catalog.get("extra") or []:
        rel = pair[1].split("?")[0].lstrip("/")
        if rel.startswith("sprites/"):
            rel = rel[len("sprites/") :]
        need(rel)
    return missing


def catalog_rels(catalog: dict) -> set[str]:
    rels: set[str] = set()
    dirs = ("down", "up", "left", "right")
    walkers = catalog.get("walkers") or {}
    for folder in walkers.values():
        if not isinstance(folder, str):
            folder = folder.get("folder", "")
        for d in dirs:
            for i in range(1, 5):
                rels.add(f"{folder}/{d}-{i}.png")
    for n in catalog.get("npcs") or []:
        for i in range(1, 5):
            rels.add(f"npc/{n}-{i}.png")
    for m in catalog.get("monsters") or []:
        for i in range(1, 5):
            rels.add(f"monsters/{m}/{i}.png")
    for p in catalog.get("portraits") or []:
        rels.add(f"portraits/{p}.png")
    for it in catalog.get("items") or []:
        rels.add(f"items/{it}.png")
    for rel in (catalog.get("props") or {}).values():
        rels.add(rel)
    for pair in catalog.get("extra") or []:
        rel = pair[1].split("?")[0].lstrip("/")
        if rel.startswith("sprites/"):
            rel = rel[len("sprites/") :]
        rels.add(rel)
    return rels


def extra_pngs(catalog: dict) -> list[str]:
    need = catalog_rels(catalog)
    extra = []
    for p in SPRITES.rglob("*.png"):
        rel = p.relative_to(SPRITES).as_posix()
        if rel not in need:
            extra.append(rel)
    return sorted(extra)


def forbidden_identity() -> list[str]:
    hits: list[str] = []
    rx = re.compile("|".join(FORBIDDEN_TEXT))
    files: list[Path] = []
    for root in LIVE_ROOTS:
        if root.is_file():
            files.append(root)
        elif root.is_dir():
            for p in root.rglob("*"):
                if not p.is_file():
                    continue
                if any(part in SKIP_NAME for part in p.parts):
                    continue
                if p.name in {"check_sync.py", "sprite_root.py"}:
                    continue
                if p.suffix.lower() not in {".ts", ".tsx", ".js", ".mjs", ".c", ".h", ".py", ".md", ".json", ".inc"} and p.name != "Makefile":
                    continue
                files.append(p)
    for p in files:
        try:
            text = p.read_text(errors="ignore")
        except OSError:
            continue
        if rx.search(text):
            hits.append(p.relative_to(ROOT).as_posix())
    return hits


def main_c_redefines() -> list[str]:
    if not MAIN_C.is_file():
        return ["missing ports/dreamcast/src/main.c"]
    text = MAIN_C.read_text()
    bad = []
    for m in re.finditer(r"^#define\s+(MAP_[A-Z0-9_]+|SP_[A-Z0-9_]+)\b", text, re.M):
        name = m.group(1)
        if name.startswith("MAP_BANNER"):
            continue
        bad.append(name)
    if re.search(r"^static const NatureDef NATURES", text, re.M):
        bad.append("NATURES table")
    return bad


def maps_object_keys(text: str) -> list[str]:
    m = re.search(r"export const MAPS\s*=\s*\{([^}]+)\}", text, re.S)
    if not m:
        return []
    return re.findall(r"^\s*([a-z0-9]+)\s*:", m.group(1), re.M)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="alias; all gates always run")
    args = ap.parse_args()  # noqa: F841
    errors: list[str] = []

    for name in PACK_FILES:
        if not (CONTENT / name).is_file():
            errors.append(f"missing content/{name}")
    if errors:
        for e in errors:
            print(f"FAIL  {e}")
        return 1

    data = load_pack(CONTENT)
    catalog = data["sprites"]
    want = pack_hash(CONTENT)

    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        bake_all(CONTENT, tdir)
        for name in INC_NAMES:
            got_p = INC_DIR / name
            fresh = tdir / name
            if not got_p.is_file():
                errors.append(f"missing {got_p.relative_to(ROOT)} — bake")
                continue
            if got_p.read_bytes() != fresh.read_bytes():
                errors.append(f"{name} does not match a fresh bake (hand-edit or stale)")

    missing = sprite_gaps(catalog)
    if missing:
        errors.append(f"{len(missing)} sprites.json paths missing under public/sprites/ (e.g. {missing[0]})")
    extra = extra_pngs(catalog)
    if extra:
        errors.append(f"{len(extra)} PNG not in sprites.json (e.g. {extra[0]})")

    stray = stray_sprite_dirs()
    if stray:
        errors.append("second art tree " + ", ".join(stray) + " — write sprites only to public/sprites/")

    for name in FORBIDDEN_DIRS:
        if (ROOT / name).exists():
            errors.append(f"abandoned tree {name}/ must not exist in the live checkout")

    ident = forbidden_identity()
    if ident:
        errors.append("forbidden Gemwar/BeelzFight identity in " + ", ".join(ident[:8]))

    redef = main_c_redefines()
    if redef:
        errors.append("main.c redefines baked symbols: " + ", ".join(redef))

    types = TYPES.read_text() if TYPES.is_file() else ""
    data_ts = DATA_TS.read_text() if DATA_TS.is_file() else ""
    map_ids = list(data["world"]["mapIds"])
    save_maps = list(data["save"]["mapOrder"])
    row_ids = list(data["maps"]["rows"].keys())
    if map_ids != save_maps:
        errors.append("world.mapIds must equal save.mapOrder (append-only, same sequence)")
    if set(map_ids) != set(row_ids):
        errors.append("world.mapIds must match maps.json rows keys")
    if set(union_members(types, "MapId")) != set(map_ids):
        errors.append("types.ts MapId union != world.mapIds")
    if set(maps_object_keys(data_ts)) != set(map_ids):
        errors.append("data.ts MAPS keys != world.mapIds")

    spec_ids = list(data["species"].keys())
    save_sp = list(data["save"]["speciesOrder"])
    spr_mon = list(catalog.get("monsters") or [])
    if spec_ids != save_sp:
        errors.append("species.json key order must equal save.speciesOrder")
    if spec_ids != spr_mon:
        errors.append("species.json key order must equal sprites.json monsters")
    if set(union_members(types, "SpeciesId")) != set(spec_ids):
        errors.append("types.ts SpeciesId union != species.json")

    speakers = list((data["dialogue"].get("speakers") or {}).keys())
    if set(union_members(types, "SpeakerId")) != set(speakers):
        errors.append("types.ts SpeakerId union != dialogue.speakers")

    items = list(data["items"]["order"])
    if items != list(data["save"]["itemOrder"]):
        errors.append("items.order must equal save.itemOrder")
    if set(union_members(types, "ItemId")) != set(items):
        errors.append("types.ts ItemId union != items.order")

    talk_keys = list(data["dialogue"]["talk"].keys())
    table_keys = [k for k, _ in talk_table(data)]
    if set(talk_keys) != set(table_keys):
        missing_t = [k for k in talk_keys if k not in table_keys]
        errors.append(f"talk keys not baked: {missing_t[:8]}")

    flags = merged_flags(data)
    save_flags = list(data["save"]["flags"])
    if any(f not in flags for f in save_flags):
        errors.append("every save.json flag must be in FLAG_* (merged_flags)")
    runtime = list(data["logic"].get("runtimeFlags") or [])
    for name in ("hasParty2", "hasCageKey"):
        if name not in runtime and name not in save_flags:
            errors.append(f"runtime flag {name} missing from logic.runtimeFlags")

    logic = data["logic"]
    for key in REQUIRED_LOGIC:
        if key not in logic:
            errors.append(f"logic.json missing {key}")
    party = logic.get("party") or {}
    for k in ("max", "release", "catchSwap", "keepLast"):
        if k not in party:
            errors.append(f"logic.party missing {k}")
    anne = logic.get("anneGift") or {}
    for k in ("afterBattles", "item", "qty", "map"):
        if k not in anne:
            errors.append(f"logic.anneGift missing {k}")
    mg = (logic.get("combat") or {}).get("minigame") or {}
    for k in ("perfectMin", "perfectMax", "perfectMul", "connectedMin", "connectedMax", "connectedMul", "fizzleMul", "needleSpeed"):
        if k not in mg:
            errors.append(f"logic.combat.minigame missing {k}")
    scale = catalog.get("drawScale") or {}
    if int(scale.get("mason") or 0) != 2:
        errors.append("sprites.json drawScale.mason must be 2")

    trainers = data["world"].get("trainers") or {}
    for k in REQUIRED_TRAINERS:
        if k not in trainers:
            errors.append(f"world.trainers missing {k}")
        else:
            kit = trainers[k]
            if "lead" not in kit:
                errors.append(f"world.trainers.{k} missing lead")
    if "forestSoldiers" not in trainers:
        errors.append("world.trainers.forestSoldiers missing")

    if "mason-" in (SRC / "game" / "engine.ts").read_text() and "w *= 2" in (SRC / "game" / "engine.ts").read_text():
        errors.append("engine.ts still hardcodes mason w *= 2 — use sprites.drawScale")

    for w in []:
        print(f"WARN  {w}")
    for e in errors:
        print(f"FAIL  {e}")
    if errors:
        return 1
    print(f"OK    PACK_HASH={want}  {len(PACK_FILES)} json  sprites catalog complete  gates green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Bake shared content/*.json into Dreamcast C includes.

Source of truth is the JSON pack (web loads it directly). This writer
upper-cases dialogue for the DC bitmap font and emits the C symbol
names main.c already references.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Workspace layout: /workspace/content  +  optional DC clone at --out
CONTENT = ROOT / "content"


SPEAKER = {
    "none": 0,
    "max": 1,
    "anne": 2,
    "mason": 3,
    "wren": 4,
    "mae": 5,
    "ivo": 6,
    "nell": 7,
    "pike": 8,
    "calder": 9,
    "bram": 10,
    "cathleen": 11,
    "shinigami": 12,
    "oren": 13,
    "tessa": 14,
    "birch": 15,
    "sable": 16,
    "cross": 17,
    "commander": 18,
    "conscript": 19,
    "enforcer": 20,
    "sentry": 21,
    "father": 22,
    "heavenfall": 23,
}

# JSON camelCase key -> existing main.c TALK_* symbol
# C symbol names that predate the JSON keys. Everything else is derived, so a
# new talk beat in dialogue.json needs no edit here.
TALK_ALIAS = {
    "commander": "TALK_CAMP_COMMANDER",
    "shinigamiAfter": "TALK_SHINIGAMI_WIN",
    "sentrySpot": "TALK_WSOLDIER_CLIFFS_SPOT",
    "sentryWin": "TALK_WSOLDIER_CLIFFS_WIN",
    "conscriptSpot": "TALK_WSOLDIER_CAMP1_SPOT",
    "conscriptWin": "TALK_WSOLDIER_CAMP1_WIN",
    "enforcerSpot": "TALK_WSOLDIER_CAMP2_SPOT",
    "enforcerWin": "TALK_WSOLDIER_CAMP2_WIN",
    "crossSpot": "TALK_WSOLDIER_GROVE_SPOT",
    "crossWin": "TALK_WSOLDIER_GROVE_WIN",
}


def talk_symbol(key: str) -> str:
    """dialogue.json key -> C symbol. reachBossSpotFather -> TALK_REACH_BOSS_SPOT_FATHER."""
    if key in TALK_ALIAS:
        return TALK_ALIAS[key]
    return "TALK_" + re.sub(r"(?<!^)(?=[A-Z])", "_", key).upper()

SPELL = {"firebolt": 0, "icebeam": 1, "lightning": 2, "manasurge": 3}

# Species and map order come from the pack itself. They used to be hand-kept
# lists here, which meant adding either one silently skipped the Dreamcast
# until somebody remembered to edit this file too.
def species_order(data: dict) -> list:
    return list(data["species"].keys())


def map_order(data: dict) -> list:
    return list(data["world"]["mapIds"])


def map_c(mid: str) -> str:
    return "MAP_" + mid.upper()


def c_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def dc_text(s: str) -> str:
    t = s.upper()
    t = t.replace("\u2014", ".").replace("\u2013", ".").replace("\u2018", "'").replace("\u2019", "'")
    t = t.replace('"', "").replace(":", ",").replace(";", ",")
    t = re.sub(r"\s+", " ", t).strip()
    return t


def load_pack(content: Path) -> dict:
    return {
        "species": json.loads((content / "species.json").read_text()),
        "items": json.loads((content / "items.json").read_text()),
        "maps": json.loads((content / "maps.json").read_text()),
        "dialogue": json.loads((content / "dialogue.json").read_text()),
        "world": json.loads((content / "world.json").read_text()),
        "logic": json.loads((content / "logic.json").read_text()),
    }


HEADER = "/* AUTO-GENERATED from the content pack - do not edit. python3 tools/bake_content.py */\n"


def bake_maps(data: dict, out: Path) -> None:
    maps = data["maps"]["rows"]
    names = data["world"]["mapNames"]
    order = map_order(data)
    lines = [HEADER]
    # Map ids are emitted here rather than hand-written in main.c, so adding a
    # map to world.json's mapIds is all it takes.
    for i, mid in enumerate(order):
        lines.append(f"#define {map_c(mid)} {i}")
    lines.append(f"#define MAP_COUNT {len(order)}")
    lines.append("")
    for mid in order:
        rows = maps[mid]
        lines.append(f"static const char *const map_{mid}_rows[] = {{")
        for r in rows:
            lines.append(f'    "{c_escape(r)}",')
        lines.append("};")
        lines.append("")
    lines.append("static const Map MAPS[MAP_COUNT] = {")
    for mid in order:
        rows = maps[mid]
        cols = max(len(r) for r in rows)
        lines.append(f"    {{ map_{mid}_rows, {cols}, {len(rows)} }},")
    lines.append("};")
    lines.append("")
    lines.append("static const char *const MAP_DISPLAY_NAME[MAP_COUNT] = {")
    lines.append("    " + ", ".join(f'"{c_escape(dc_text(names[m]))}"' for m in order) + ",")
    lines.append("};")
    lines.append("")
    out.write_text("\n".join(lines) + "\n")


def bake_talk(data: dict, out: Path) -> None:
    talk = data["dialogue"]["talk"]
    ending = data["dialogue"]["endingWin"]
    lines = [HEADER, "#if defined(__GNUC__)"]
    lines.append("#pragma GCC diagnostic ignored \"-Wunused-const-variable\"")
    lines.append("#endif")
    lines.append("")
    for key in talk:
        symbol = talk_symbol(key)
        beats = talk[key]
        lines.append(f"static const TalkBeat {symbol}[] = {{")
        for b in beats:
            sp = SPEAKER[b["speaker"]]
            text = dc_text(b["text"])
            lines.append(f'    {{ "{c_escape(text)}", {sp} }},')
        lines.append("};")
    lines.append("")
    lines.append("static const char *const DEMO_END[] = {")
    for s in ending:
        lines.append(f'    "{c_escape(dc_text(s))}",')
    lines.append("};")
    lines.append("")
    lines.append("#define TALK_LEN(arr) (int)(sizeof(arr) / sizeof((arr)[0]))")
    lines.append("")
    out.write_text("\n".join(lines) + "\n")


def bake_species(data: dict, out: Path) -> None:
    spec = data["species"]
    order = species_order(data)
    lines = [HEADER]
    for i, sid in enumerate(order):
        lines.append(f"#define SP_{sid.upper()} {i}")
    lines.append(f"#define SPECIES_COUNT {len(order)}")
    lines.append("")
    lines.append("static const Species SPECIES[SPECIES_COUNT] = {")
    for sid in order:
        s = spec[sid]
        spells = s.get("spells") or []
        ids = [SPELL[sp["id"]] for sp in spells]
        while len(ids) < 4:
            ids.append(0)
        n = len(spells)
        name = dc_text(s["name"])
        basic = dc_text(s["basic"])
        special = dc_text(s["special"])
        lines.append(
            f'    {{ "{c_escape(name)}", "{c_escape(basic)}", "{c_escape(special)}", '
            f'{s["maxHp"]}, {s["str"]}, {s["agl"]}, {s["spc"]}, {s["specialPp"]}, '
            f"{n}, {{{ids[0]},{ids[1]},{ids[2]},{ids[3]}}}, "
            f'NAT_{s["nature"].upper()} }},'
        )
    lines.append("};")
    lines.append("")
    out.write_text("\n".join(lines) + "\n")


def bake_logic(data: dict, out: Path) -> None:
    logic = data["logic"]
    ambush = logic["arrivals"]["masonAmbush"]
    rematch = logic["masonRematch"]
    fade = logic["screenFade"]
    lines = [HEADER]
    lines.append("/* Canonical rules from content/logic.json (Dreamcast spec). */")
    lines.append(f"#define LOGIC_FADE_OUT_FRAMES {max(1, int(round(fade['outSec'] * 60)))}")
    lines.append(f"#define LOGIC_FADE_HOLD_FRAMES {max(1, int(round(fade['holdSec'] * 60)))}")
    lines.append(f"#define LOGIC_FADE_IN_FRAMES {max(1, int(round(fade['inSec'] * 60)))}")
    lines.append(f"#define LOGIC_MASON_AMBUSH_NEED_PARTY {1 if ambush.get('needParty') else 0}")
    lines.append(f"#define LOGIC_MASON_AMBUSH_UNLESS_BEAT {1 if ambush.get('unless') == 'foughtMason' else 0}")
    maps = ", ".join(map_c(m) for m in rematch["maps"])
    lines.append(f"static const int LOGIC_MASON2_MAPS[] = {{ {maps} }};")
    lines.append(f"#define LOGIC_MASON2_MAP_N {len(rematch['maps'])}")
    lines.append("")

    # Crystal Natures. The ring and the multipliers are content, not engine
    # constants -- the web port reads the same numbers out of logic.json.
    nat = logic["natures"]
    ring = nat["ring"]
    lines.append("/* Crystal Natures (content/logic.json -> natures). */")
    for i, n in enumerate(ring):
        lines.append(f"#define NAT_{n.upper()} {i}")
    lines.append(f"#define NAT_COUNT {len(ring)}")
    lines.append(f"#define NAT_BEATS_AHEAD {nat['beatsAhead']}")
    lines.append(f"#define NATURE_STRONG_MUL {float(nat['strongMul'])}f")
    lines.append(f"#define NATURE_WEAK_MUL {float(nat['weakMul'])}f")
    names = ", ".join(f'"{c_escape(dc_text(n))}"' for n in ring)
    lines.append(f"static const char *const NATURE_NAME[NAT_COUNT] = {{ {names} }};")
    lines.append(f'#define NATURE_STRONG_TEXT "{c_escape(dc_text(nat["strongText"]))}"')
    lines.append(f'#define NATURE_WEAK_TEXT "{c_escape(dc_text(nat["weakText"]))}"')
    lines.append("")

    bench = logic["benchXp"]
    lines.append("/* Bench XP share (content/logic.json -> benchXp). */")
    lines.append(f"#define BENCH_XP_NUMERATOR {bench['numerator']}")
    lines.append(f"#define BENCH_XP_DENOMINATOR {bench['denominator']}")
    lines.append(f"#define BENCH_XP_REQUIRE_ALIVE {1 if bench.get('requireAlive') else 0}")
    lines.append("")

    dex = logic["dex"]
    lines.append("/* CryDex (content/logic.json -> dex). */")
    lines.append(f'#define DEX_UNKNOWN_TEXT "{c_escape(dc_text(dex["unknownText"]))}"')
    lines.append("")
    out.write_text("\n".join(lines) + "\n")


def bake_items(data: dict, out: Path) -> None:
    items = data["items"]
    order = items["order"]
    defs = items["defs"]
    lines = [HEADER, f"#define ITEM_COUNT {len(order)}", "static const ItemDef ITEMS[ITEM_COUNT] = {"]
    for iid in order:
        it = defs[iid]
        lines.append(f'    {{ "{c_escape(dc_text(it["name"]))}", {it["buy"]}, {it["sell"]} }},')
    lines.append("};")
    lines.append("")
    out.write_text("\n".join(lines) + "\n")


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--content", type=Path, default=CONTENT)
    ap.add_argument("--out", type=Path, default=None, help="Directory for *.inc")
    args = ap.parse_args()
    content = args.content
    data = load_pack(content)
    if args.out:
        outdir = args.out
    else:
        cand = ROOT / "ports" / "dreamcast" / "src"
        if not cand.is_dir():
            cand = Path("/tmp/beelz/repo/crymon-dreamcast/src")
        outdir = cand if cand.is_dir() else content.parent / "src"
    outdir.mkdir(parents=True, exist_ok=True)
    bake_maps(data, outdir / "content_maps.inc")
    bake_talk(data, outdir / "content_talk.inc")
    bake_species(data, outdir / "content_species.inc")
    bake_items(data, outdir / "content_items.inc")
    bake_logic(data, outdir / "content_logic.inc")
    print(f"baked maps/talk/species/items/logic -> {outdir}")


if __name__ == "__main__":
    main()

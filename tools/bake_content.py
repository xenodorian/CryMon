#!/usr/bin/env python3
"""Bake shared content/*.json into Dreamcast C includes.

Source of truth is the JSON pack (web loads it directly). This writer
upper-cases dialogue for the DC bitmap font and emits the C symbol
names main.c already references.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"

SPEAKER = {
    "none": 0, "max": 1, "anne": 2, "mason": 3, "wren": 4, "mae": 5,
    "ivo": 6, "nell": 7, "pike": 8, "calder": 9, "bram": 10, "cathleen": 11,
    "shinigami": 12, "oren": 13, "tessa": 14, "birch": 15, "sable": 16,
    "cross": 17, "commander": 18, "conscript": 19, "enforcer": 20,
    "sentry": 21, "father": 22, "heavenfall": 23,
}

TALK_C = {
    "father": "TALK_FATHER", "fatherAfter": "TALK_FATHER_AFTER", "bed": "TALK_BED",
    "shelf": "TALK_SHELF", "shelfEmpty": "TALK_SHELF_EMPTY", "crate": "TALK_CRATE",
    "crateEmpty": "TALK_CRATE_EMPTY", "doorLocked": "TALK_DOOR_LOCKED",
    "campLocked": "TALK_CAMP_LOCKED", "groveLocked": "TALK_GROVE_LOCKED",
    "cageLocked": "TALK_CAGE_LOCKED", "cageUnlock": "TALK_CAGE_UNLOCK",
    "cageOpen": "TALK_CAGE_OPEN", "masonFight": "TALK_MASON_FIGHT",
    "masonWin": "TALK_MASON_WIN", "masonFight2": "TALK_MASON_FIGHT2",
    "masonWin2": "TALK_MASON_WIN2", "wrenFirst": "TALK_WREN_FIRST",
    "wrenBeat": "TALK_WREN_BEAT", "wrenCart": "TALK_WREN_CART",
    "wrenHeal": "TALK_WREN_HEAL", "maeFirst": "TALK_MAE_FIRST",
    "maeAgain": "TALK_MAE_AGAIN", "ivoFirst": "TALK_IVO_FIRST",
    "ivoAgain": "TALK_IVO_AGAIN", "nellFirst": "TALK_NELL_FIRST",
    "nellBonus": "TALK_NELL_BONUS", "nellAgain": "TALK_NELL_AGAIN",
    "pikeFirst": "TALK_PIKE_FIRST", "pikeHelp": "TALK_PIKE_HELP",
    "pikeDone": "TALK_PIKE_DONE", "pikeHint": "TALK_PIKE_HINT",
    "herb": "TALK_HERB", "herbGone": "TALK_HERB_GONE", "gemPike": "TALK_GEM_PIKE",
    "gemWild": "TALK_GEM_WILD", "gemGone": "TALK_GEM_GONE", "stump": "TALK_STUMP",
    "stumpGone": "TALK_STUMP_GONE", "cart": "TALK_CART",
    "calderAfter": "TALK_CALDER_AFTER", "calderFight": "TALK_CALDER_FIGHT",
    "calderWin": "TALK_CALDER_WIN", "commander": "TALK_CAMP_COMMANDER",
    "cathleenSpot": "TALK_CATHLEEN_SPOT", "cathleenAfter": "TALK_CATHLEEN_AFTER",
    "cathleenGone": "TALK_CATHLEEN_GONE", "shinigamiSpot": "TALK_SHINIGAMI_SPOT",
    "shinigamiAfter": "TALK_SHINIGAMI_WIN", "shinigamiDone": "TALK_SHINIGAMI_DONE",
    "soldierSpot": "TALK_SOLDIER_SPOT", "soldierDone": "TALK_SOLDIER_DONE",
    "soldierAfter": "TALK_SOLDIER_AFTER", "bramOpen": "TALK_BRAM_OPEN",
    "sentrySpot": "TALK_WSOLDIER_CLIFFS_SPOT", "sentryWin": "TALK_WSOLDIER_CLIFFS_WIN",
    "conscriptSpot": "TALK_WSOLDIER_CAMP1_SPOT", "conscriptWin": "TALK_WSOLDIER_CAMP1_WIN",
    "enforcerSpot": "TALK_WSOLDIER_CAMP2_SPOT", "enforcerWin": "TALK_WSOLDIER_CAMP2_WIN",
    "crossSpot": "TALK_WSOLDIER_GROVE_SPOT", "crossWin": "TALK_WSOLDIER_GROVE_WIN",
    "orenOpen": "TALK_OREN_OPEN", "tessaFirst": "TALK_TESSA_FIRST",
    "tessaAgain": "TALK_TESSA_AGAIN", "birchFirst": "TALK_BIRCH_FIRST",
    "birchAgain": "TALK_BIRCH_AGAIN", "sableFirst": "TALK_SABLE_FIRST",
    "sableAgain": "TALK_SABLE_AGAIN", "chest": "TALK_CHEST",
    "chestEmpty": "TALK_CHEST_EMPTY", "anneGift": "TALK_ANNE_GIFT",
    "anneReturn": "TALK_ANNE_RETURN", "choiceFather": "TALK_CHOICE_FATHER",
    "choiceHeavenfall": "TALK_CHOICE_HEAVENFALL", "reachLocked": "TALK_REACH_LOCKED",
    "reachStone": "TALK_REACH_STONE", "reachAgain": "TALK_REACH_AGAIN",
}

SPELL = {"firebolt": 0, "icebeam": 1, "lightning": 2, "manasurge": 3}

FLAG_IDS = [
    "tookStarter", "lootedCrate", "foughtMason", "talkedFather", "talkedWren",
    "talkedMae", "talkedIvo", "talkedNell", "nellBonus", "talkedPike", "pikeHelped",
    "gotHerb", "gotFieldGem", "gotStump", "readCart", "beatCalder", "beatShinigami",
    "hasScroll", "cathleenCaught", "mason2", "gotChest", "cageOpen", "hasCageKey",
    "beatSentry", "beatConscript", "beatEnforcer", "beatCross", "birchGifted",
    "sableGifted", "tessaGifted", "talkedReach", "anneGifted",
]

def species_order(data):
    return list(data["save"]["speciesOrder"])
def map_order(data):
    return list(data["world"]["mapIds"])
def map_sym(mid):
    return "MAP_" + mid.upper()
def sp_sym(sid):
    return "SP_" + sid.upper()

PACK_FILES = ["species.json", "items.json", "maps.json", "dialogue.json", "world.json", "logic.json", "audio.json", "save.json", "sprites.json"]

def pack_hash(content):
    h = hashlib.sha256()
    for name in PACK_FILES:
        path = content / name
        h.update(name.encode()); h.update(b"\0")
        h.update(path.read_bytes() if path.is_file() else b"<missing>")
    return h.hexdigest()[:16]

def c_escape(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')
def dc_text(s):
    t = s.upper()
    t = t.replace("\u2014", ".").replace("\u2013", ".").replace("\u2018", "'").replace("\u2019", "'")
    t = t.replace('"', "").replace(":", ",").replace(";", ",")
    return re.sub(r"\s+", " ", t).strip()

def talk_table(data):
    talk = data["dialogue"]["talk"]
    out, seen = [], set()
    for key, sym in TALK_C.items():
        if key in talk and key not in seen:
            out.append((key, sym)); seen.add(key)
    for key in talk:
        if key not in seen:
            snake = re.sub(r"([A-Z])", r"_\1", key).upper().lstrip("_")
            out.append((key, "TALK_" + snake)); seen.add(key)
    return out

def merged_flags(data):
    out = []
    for name in FLAG_IDS:
        if name not in out: out.append(name)
    for name in data["save"].get("flags") or []:
        if name not in out: out.append(name)
    for name in data["logic"].get("runtimeFlags") or []:
        if name not in out: out.append(name)
    return out

def load_pack(content):
    pack = {
        "species": json.loads((content / "species.json").read_text()),
        "items": json.loads((content / "items.json").read_text()),
        "maps": json.loads((content / "maps.json").read_text()),
        "dialogue": json.loads((content / "dialogue.json").read_text()),
        "world": json.loads((content / "world.json").read_text()),
        "logic": json.loads((content / "logic.json").read_text()),
        "audio": json.loads((content / "audio.json").read_text()),
        "save": json.loads((content / "save.json").read_text()),
        "sprites": json.loads((content / "sprites.json").read_text()) if (content / "sprites.json").is_file() else {},
    }
    global FLAG_INDEX, TALK_KEYS_ORDER
    FLAG_INDEX = {name: i for i, name in enumerate(merged_flags(pack))}
    TALK_KEYS_ORDER = [k for k, _ in talk_table(pack)]
    return pack

TALK_KEYS_ORDER = []
HEADER = "/* AUTO-GENERATED from content/*.json — do not edit. python3 tools/bake_content.py */\n"
def set_header(h):
    global HEADER
    HEADER = f"/* AUTO-GENERATED from content/*.json PACK_HASH={h} — do not edit. python3 tools/bake_content.py */\n"

def bake_all(content, outdir):
    data = load_pack(content)
    h = pack_hash(content)
    set_header(h)
    outdir.mkdir(parents=True, exist_ok=True)
    bake_maps(data, outdir / "content_maps.inc")
    bake_talk(data, outdir / "content_talk.inc")
    bake_species(data, outdir / "content_species.inc")
    bake_items(data, outdir / "content_items.inc")
    bake_logic(data, outdir / "content_logic.inc")
    bake_world(data, outdir / "content_world.inc")
    bake_audio(data, outdir / "content_audio.inc")
    bake_save(data, outdir / "content_save.inc")
    return h

def bake_maps(data, out):
    maps, names, order = data["maps"]["rows"], data["world"]["mapNames"], map_order(data)
    lines = [HEADER]
    for i, mid in enumerate(order):
        lines.append(f"#define {map_sym(mid)} {i}")
    lines.append(f"#define MAP_N {len(order)}")
    lines.append("")
    for mid in order:
        lines.append(f"static const char *const map_{mid}_rows[] = {{")
        for r in maps[mid]:
            lines.append(f'    "{c_escape(r)}",')
        lines.append("};")
        lines.append("")
    lines.append(f"static const Map MAPS[MAP_N] = {{")
    for mid in order:
        rows = maps[mid]
        lines.append(f"    {{ map_{mid}_rows, {max(len(r) for r in rows)}, {len(rows)} }},")
    lines.append("};")
    lines.append("")
    lines.append(f"static const char *const MAP_DISPLAY_NAME[MAP_N] = {{")
    lines.append("    " + ", ".join(f'\"{c_escape(dc_text(names[m]))}\"' for m in order) + ",")
    lines.append("};")
    lines.append("")
    solid = data["maps"].get("solid", "#HWRBC^NKEVAQXUJISMGL89r")
    lines.append(f'static const char *const SOLID_TILES = "{c_escape(solid)}";')
    lines.append("")
    out.write_text("\n".join(lines) + "\n")

def bake_talk(data, out):
    talk, ending, table = data["dialogue"]["talk"], data["dialogue"]["endingWin"], talk_table(data)
    lines = [HEADER, "#if defined(__GNUC__)", "#pragma GCC diagnostic ignored \"-Wunused-const-variable\"", "#endif", ""]
    for key, symbol in table:
        lines.append(f"static const TalkBeat {symbol}[] = {{")
        for b in talk[key]:
            lines.append(f'    {{ "{c_escape(dc_text(b["text"]))}", {SPEAKER[b["speaker"]]} }},')
        lines.append("};")
    lines.append("")
    lines.append("static const char *const DEMO_END[] = {")
    for s in ending:
        lines.append(f'    "{c_escape(dc_text(s))}",')
    lines.append("};")
    lines.append("")
    lines.append("#define TALK_LEN(arr) (int)(sizeof(arr) / sizeof((arr)[0]))")
    lines.append("static const TalkBeat *const TALK_PTRS[] = {")
    for _, symbol in table:
        lines.append(f"    {symbol},")
    lines.append("};")
    lines.append("static const int TALK_COUNTS[] = {")
    for _, symbol in table:
        lines.append(f"    TALK_LEN({symbol}),")
    lines.append("};")
    lines.append(f"#define TALK_TABLE_N {len(table)}")
    lines.append("")
    out.write_text("\n".join(lines) + "\n")

def bake_species(data, out):
    spec, order = data["species"], species_order(data)
    lines = [HEADER]
    for i, sid in enumerate(order):
        lines.append(f"#define {sp_sym(sid)} {i}")
    lines.append(f"#define SPECIES_N {len(order)}")
    lines.append("")
    lines.append(f"static const Species SPECIES[SPECIES_N] = {{")
    for sid in order:
        s = spec[sid]
        spells = s.get("spells") or []
        ids = [SPELL[sp["id"]] for sp in spells]
        while len(ids) < 4: ids.append(0)
        bp = float(s.get("basicPower", 0.6)); bs = float(s.get("basicSpeed", 1.2))
        bst = 1 if s.get("basicStat") == "spc" else 0
        sp_ = float(s.get("specialPower", 1.0)); ss = float(s.get("specialSpeed", 0.8))
        sst = 1 if s.get("specialStat") == "spc" else 0
        lines.append(
            f'    {{ "{c_escape(dc_text(s["name"]))}", "{c_escape(dc_text(s["basic"]))}", "{c_escape(dc_text(s["special"]))}", '
            f'{s["maxHp"]}, {s["str"]}, {s["agl"]}, {s["spc"]}, {s["specialPp"]}, '
            f"{len(spells)}, {{{ids[0]},{ids[1]},{ids[2]},{ids[3]}}}, "
            f"{bp:.2f}f, {bs:.2f}f, {bst}, {sp_:.2f}f, {ss:.2f}f, {sst} }},"
        )
    lines.append("};")
    lines.append("")
    out.write_text("\n".join(lines) + "\n")

def bake_logic(data, out):
    logic = data["logic"]
    ambush, rematch, fade = logic["arrivals"]["masonAmbush"], logic["masonRematch"], logic["screenFade"]
    lines = [HEADER]
    lines.append("/* Canonical rules from content/logic.json (Dreamcast spec). */")
    lines.append(f"#define LOGIC_FADE_OUT_FRAMES {max(1, int(round(fade['outSec'] * 60)))}")
    lines.append(f"#define LOGIC_FADE_HOLD_FRAMES {max(1, int(round(fade['holdSec'] * 60)))}")
    lines.append(f"#define LOGIC_FADE_IN_FRAMES {max(1, int(round(fade['inSec'] * 60)))}")
    lines.append(f"#define LOGIC_MASON_AMBUSH_NEED_PARTY {1 if ambush.get('needParty') else 0}")
    lines.append(f"#define LOGIC_MASON_AMBUSH_UNLESS_BEAT {1 if ambush.get('unless') == 'foughtMason' else 0}")
    maps = ", ".join(map_sym(m) for m in rematch["maps"])
    lines.append(f"static const int LOGIC_MASON2_MAPS[] = {{ {maps} }};")
    lines.append(f"#define LOGIC_MASON2_MAP_N {len(rematch['maps'])}")
    lines.append("")
    natures = logic.get("natures") or []
    lines.append("typedef struct { const char *name; int str, agl, spc; } NatureDef;")
    lines.append(f"#define NATURE_N {len(natures)}")
    lines.append("static const NatureDef NATURES[NATURE_N] = {")
    for nat in natures:
        lines.append(f'    {{ "{c_escape(dc_text(nat["name"]))}", {int(nat.get("str") or 0)}, {int(nat.get("agl") or 0)}, {int(nat.get("spc") or 0)} }},')
    lines.append("};")
    lines.append("")
    party = logic.get("party") or {}
    lines.append(f"#define PARTY_MAX {int(party.get('max') or 6)}")
    lines.append(f"#define PARTY_RELEASE {1 if party.get('release') else 0}")
    lines.append(f"#define PARTY_CATCH_SWAP {1 if party.get('catchSwap') else 0}")
    lines.append(f"#define PARTY_KEEP_LAST {1 if party.get('keepLast', True) else 0}")
    anne = logic.get("anneGift") or {}
    lines.append(f"#define ANNE_GIFT_AFTER {int(anne.get('afterBattles') or 1)}")
    lines.append(f"#define ANNE_GIFT_QTY {int(anne.get('qty') or 5)}")
    scale = (data.get("sprites") or {}).get("drawScale") or {}
    lines.append(f"#define SPR_SCALE_MASON {int(scale.get('mason') or 1)}")
    lines.append("")
    combat = logic.get("combat") or {}
    toxic, dodge, block, barrier = combat.get("toxicBurst") or {}, combat.get("dodge") or {}, combat.get("block") or {}, combat.get("barrier") or {}
    lines.append("/* Combat: finalDamage = atkStat * power; finalSpeed = atkAgl * speed. */")
    lines.append(f"#define COMBAT_TOXIC_POWER {float(toxic.get('power', 0.5)):.2f}f")
    lines.append(f"#define COMBAT_TOXIC_SPEED {float(toxic.get('speed', 1.0)):.2f}f")
    lines.append(f"#define COMBAT_TOXIC_STAT {1 if toxic.get('stat') == 'spc' else 0}")
    lines.append(f"#define COMBAT_DODGE_MUL_MIN {float(dodge.get('defMulMin', 0.75)):.2f}f")
    lines.append(f"#define COMBAT_DODGE_MUL_MAX {float(dodge.get('defMulMax', 1.25)):.2f}f")
    lines.append(f"#define COMBAT_BLOCK_MUL_MIN {float(block.get('mulMin', 0.25)):.2f}f")
    lines.append(f"#define COMBAT_BLOCK_MUL_MAX {float(block.get('mulMax', 0.75)):.2f}f")
    lines.append(f"#define COMBAT_BARRIER_MUL_MIN {float(barrier.get('mulMin', 0.25)):.2f}f")
    lines.append(f"#define COMBAT_BARRIER_MUL_MAX {float(barrier.get('mulMax', 0.75)):.2f}f")
    lines.append(f"#define COMBAT_DISPLAY_SCALE {int(combat.get('displayScale', 10))}")
    lines.append("")
    out.write_text("\n".join(lines) + "\n")

NEED = {"tookStarter": 1, "beatCalder": 2, "beatShin": 3, "hasScroll": 4}
ARRIVE = {"masonAmbush": 1, "ensureSoldiers": 2}

def talk_id(key):
    try: return TALK_KEYS_ORDER.index(key)
    except ValueError: return -1

def bake_world(data, out):
    world, items, f = data["world"], data["items"], data["world"]["formulas"]
    lines = [HEADER]
    lines.append("/* Canonical world tables from content/world.json + items.json. */")
    for k, v in [("XP_BASE", f["xpBase"]), ("XP_PER_LEVEL", f["xpPerLevel"]), ("LEVEL_XP_MUL", f["levelXpMul"]),
                 ("LEVEL_CAP", f["levelCap"]), ("LEVEL_HP", f["levelHp"]), ("LEVEL_STAT", f["levelStat"]),
                 ("CAPTURE_AGL", f["captureAgl"]), ("CAPTURE_VULN", f["captureVulnerable"]),
                 ("SHINY_DENOM", f["shinyDenom"]), ("ENCOUNTER_PCT", f["encounterPercent"]),
                 ("GREATCRYSTAL_BONUS", f["greatcrystalBonus"]), ("BITTERROOT_STR", f["bitterrootStr"]),
                 ("WARROOT_AGL", f["warrootAgl"]), ("DUST_STR", f["dustStr"]), ("DUST_AGL", f["dustAgl"]),
                 ("DUST_SPC", f["dustSpc"]), ("START_MARKS", world["startMarks"])]:
        lines.append(f"#define {k} {int(v)}")
    lines.append(f"#define BENCH_XP_PCT {int(round(float(f.get('benchXpShare') or 0.5) * 100))}")
    order = items["order"]
    bag = world["startBag"]
    lines.append(f"#define START_BAG_INIT {{ {', '.join(str(int(bag.get(i, 0))) for i in order)} }}")
    lines.append("")
    lines.append("typedef struct { int from_map, to_map; char tile, spawn; int face_down, need, on_arrive, fail_talk; } WarpDef;")
    lines.append("static const WarpDef WARPS[] = {")
    for w in world["warps"]:
        fail = talk_id(w["failTalk"]) if w.get("failTalk") else -1
        lines.append(f"    {{ {map_sym(w['from'])}, {map_sym(w['to'])}, '{w['tile']}', '{w['spawn']}', "
                     f"{1 if w.get('dir') == 'down' else 0}, {NEED.get(w.get('need') or '', 0)}, "
                     f"{ARRIVE.get(w.get('onArrive') or '', 0)}, {fail} }},")
    lines.append("};")
    lines.append("#define WARP_N (int)(sizeof(WARPS)/sizeof(WARPS[0]))")
    lines.append("")
    out.write_text("\n".join(lines) + "\n")

def bake_audio(data, out):
    out.write_text(HEADER + "/* Audio from content/audio.json. */\n")

def _c_ident(name):
    return re.sub(r"[^A-Za-z0-9_]", "_", name).upper()

def bake_save(data, out):
    save, flags, items = data["save"], merged_flags(data), data["items"]["order"]
    lines = [HEADER, "#ifndef CONTENT_SAVE_INC", "#define CONTENT_SAVE_INC", ""]
    lines.append(f"#define SAVE_MAGIC 0x{int.from_bytes(b'CRYM', 'little'):08X}u")
    lines.append(f"#define SAVE_VERSION {int(save.get('version') or 1)}")
    lines.append(f"#define SAVE_SIZE {int(save.get('size') or 142)}")
    lines.append(f"#define SAVE_PARTY_SLOT {int(save.get('partySlot') or 16)}")
    lines.append("#define SAVE_PARTY_MAX 6")
    lines.append(f"#define SAVE_FLAG_N {len(flags)}")
    lines.append(f"#define SAVE_ITEM_N {len(items)}")
    for i, name in enumerate(flags):
        lines.append(f"#define SAVE_FLAG_{_c_ident(name)} {i}")
    lines.append("")
    lines.append("#endif")
    out.write_text("\n".join(lines) + "\n")

def bake_items(data, out):
    order, defs = data["items"]["order"], data["items"]["defs"]
    lines = [HEADER, f"#define ITEM_COUNT {len(order)}", "static const ItemDef ITEMS[ITEM_COUNT] = {"]
    for iid in order:
        it = defs[iid]
        lines.append(f'    {{ "{c_escape(dc_text(it["name"]))}", {it["buy"]}, {it["sell"]} }},')
    lines.append("};")
    lines.append("")
    out.write_text("\n".join(lines) + "\n")

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--content", type=Path, default=CONTENT)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    outdir = args.out or (ROOT / "ports" / "dreamcast" / "src")
    if not outdir.is_dir() and not args.out:
        raise SystemExit(f"no bake output dir: {outdir}")
    h = bake_all(args.content, outdir)
    print(f"baked maps/talk/species/items/logic/world/audio/save PACK_HASH={h} -> {outdir}")

if __name__ == "__main__":
    main()

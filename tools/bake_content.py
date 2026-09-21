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
    "ranger": 24,
    "scout": 25,
    "keeper": 26,
    "warden": 27,
    "quartz": 28,
    "bogwalker": 29,
    "reedguard": 30,
    "opal": 31,
    "driller": 32,
    "fenn": 33,
    "dray": 34,
    "lead": 35,
    "system": 36,
}

# JSON camelCase key -> existing main.c TALK_* symbol
TALK_C = {
    "father": "TALK_FATHER",
    "fatherAfter": "TALK_FATHER_AFTER",
    "fatherThanks": "TALK_FATHER_THANKS",
    "fatherAlive": "TALK_FATHER_ALIVE",
    "bed": "TALK_BED",
    "shelf": "TALK_SHELF",
    "shelfEmpty": "TALK_SHELF_EMPTY",
    "crate": "TALK_CRATE",
    "crateEmpty": "TALK_CRATE_EMPTY",
    "doorLocked": "TALK_DOOR_LOCKED",
    "campLocked": "TALK_CAMP_LOCKED",
    "groveLocked": "TALK_GROVE_LOCKED",
    "cageLocked": "TALK_CAGE_LOCKED",
    "cageUnlock": "TALK_CAGE_UNLOCK",
    "cageOpen": "TALK_CAGE_OPEN",
    "masonFight": "TALK_MASON_FIGHT",
    "masonWin": "TALK_MASON_WIN",
    "masonFight2": "TALK_MASON_FIGHT2",
    "masonWin2": "TALK_MASON_WIN2",
    "wrenFirst": "TALK_WREN_FIRST",
    "wrenBeat": "TALK_WREN_BEAT",
    "wrenCart": "TALK_WREN_CART",
    "wrenHeal": "TALK_WREN_HEAL",
    "maeFirst": "TALK_MAE_FIRST",
    "maeAgain": "TALK_MAE_AGAIN",
    "ivoFirst": "TALK_IVO_FIRST",
    "ivoAgain": "TALK_IVO_AGAIN",
    "nellFirst": "TALK_NELL_FIRST",
    "nellBonus": "TALK_NELL_BONUS",
    "nellAgain": "TALK_NELL_AGAIN",
    "pikeFirst": "TALK_PIKE_FIRST",
    "pikeHelp": "TALK_PIKE_HELP",
    "pikeDone": "TALK_PIKE_DONE",
    "pikeHint": "TALK_PIKE_HINT",
    "herb": "TALK_HERB",
    "herbGone": "TALK_HERB_GONE",
    "gemPike": "TALK_GEM_PIKE",
    "gemWild": "TALK_GEM_WILD",
    "gemGone": "TALK_GEM_GONE",
    "stump": "TALK_STUMP",
    "stumpGone": "TALK_STUMP_GONE",
    "cart": "TALK_CART",
    "calderAfter": "TALK_CALDER_AFTER",
    "calderFight": "TALK_CALDER_FIGHT",
    "calderWin": "TALK_CALDER_WIN",
    "commander": "TALK_CAMP_COMMANDER",
    "cathleenSpot": "TALK_CATHLEEN_SPOT",
    "cathleenAfter": "TALK_CATHLEEN_AFTER",
    "cathleenGone": "TALK_CATHLEEN_GONE",
    "shinigamiSpot": "TALK_SHINIGAMI_SPOT",
    "shinigamiAfter": "TALK_SHINIGAMI_WIN",
    "shinigamiDone": "TALK_SHINIGAMI_DONE",
    "soldierSpot": "TALK_SOLDIER_SPOT",
    "soldierDone": "TALK_SOLDIER_DONE",
    "soldierAfter": "TALK_SOLDIER_AFTER",
    "bramOpen": "TALK_BRAM_OPEN",
    "sentrySpot": "TALK_WSOLDIER_CLIFFS_SPOT",
    "sentryWin": "TALK_WSOLDIER_CLIFFS_WIN",
    "conscriptSpot": "TALK_WSOLDIER_CAMP1_SPOT",
    "conscriptWin": "TALK_WSOLDIER_CAMP1_WIN",
    "enforcerSpot": "TALK_WSOLDIER_CAMP2_SPOT",
    "enforcerWin": "TALK_WSOLDIER_CAMP2_WIN",
    "crossSpot": "TALK_WSOLDIER_GROVE_SPOT",
    "crossWin": "TALK_WSOLDIER_GROVE_WIN",
    "orenOpen": "TALK_OREN_OPEN",
    "tessaFirst": "TALK_TESSA_FIRST",
    "tessaAgain": "TALK_TESSA_AGAIN",
    "birchFirst": "TALK_BIRCH_FIRST",
    "birchAgain": "TALK_BIRCH_AGAIN",
    "sableFirst": "TALK_SABLE_FIRST",
    "sableAgain": "TALK_SABLE_AGAIN",
    "chest": "TALK_CHEST",
    "chestEmpty": "TALK_CHEST_EMPTY",
    "anneGift": "TALK_ANNE_GIFT",
    "anneReturn": "TALK_ANNE_RETURN",
    "choiceFather": "TALK_CHOICE_FATHER",
    "choiceHeavenfall": "TALK_CHOICE_HEAVENFALL",
    "reachLocked": "TALK_REACH_LOCKED",
    "reachStone": "TALK_REACH_STONE",
    "reachAgain": "TALK_REACH_AGAIN",
    "quartzSpot": "TALK_QUARTZ_SPOT",
    "quartzWin": "TALK_QUARTZ_WIN",
}

SPELL = {"firebolt": 0, "icebeam": 1, "lightning": 2, "manasurge": 3}


def species_order(data: dict) -> list[str]:
    return list(data["save"]["speciesOrder"])


def map_order(data: dict) -> list[str]:
    return list(data["world"]["mapIds"])


def map_sym(mid: str) -> str:
    return "MAP_" + mid.upper()


def sp_sym(sid: str) -> str:
    return "SP_" + sid.upper()


PACK_FILES = [
    "species.json",
    "items.json",
    "maps.json",
    "dialogue.json",
    "world.json",
    "logic.json",
    "audio.json",
    "save.json",
    "sprites.json",
]


def pack_hash(content: Path) -> str:
    h = hashlib.sha256()
    for name in PACK_FILES:
        path = content / name
        h.update(name.encode())
        h.update(b"\0")
        h.update(path.read_bytes() if path.is_file() else b"<missing>")
    return h.hexdigest()[:16]


def c_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def dc_text(s: str) -> str:
    t = s.upper()
    t = t.replace("\u2014", ".").replace("\u2013", ".").replace("\u2018", "'").replace("\u2019", "'")
    t = t.replace('"', "").replace(":", ",").replace(";", ",")
    t = re.sub(r"\s+", " ", t).strip()
    return t


def talk_table(data: dict) -> list[tuple[str, str]]:
    """Existing TALK_C order first (DC indices), then any new dialogue.talk keys."""
    talk = data["dialogue"]["talk"]
    out: list[tuple[str, str]] = []
    seen: set[str] = set()
    for key, sym in TALK_C.items():
        if key in talk and key not in seen:
            out.append((key, sym))
            seen.add(key)
    for key in talk:
        if key not in seen:
            snake = re.sub(r"([A-Z])", r"_\1", key).upper().lstrip("_")
            out.append((key, "TALK_" + snake))
            seen.add(key)
    return out


def merged_flags(data: dict) -> list[str]:
    """NPC FLAG_* index: baked FLAG_IDS order, then save.json flags, then runtimeFlags."""
    out: list[str] = []
    for name in FLAG_IDS:
        if name not in out:
            out.append(name)
    for name in data["save"].get("flags") or []:
        if name not in out:
            out.append(name)
    for name in data["logic"].get("runtimeFlags") or []:
        if name not in out:
            out.append(name)
    return out


def load_pack(content: Path) -> dict:
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


def bake_all(content: Path, outdir: Path) -> str:
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


TALK_KEYS_ORDER: list[str] = []
HEADER = "/* AUTO-GENERATED from content/*.json — do not edit. python3 tools/bake_content.py */\n"


def set_header(h: str) -> None:
    global HEADER
    HEADER = (
        f"/* AUTO-GENERATED from content/*.json PACK_HASH={h} "
        "— do not edit. python3 tools/bake_content.py */\n"
    )


def bake_maps(data: dict, out: Path) -> None:
    maps = data["maps"]["rows"]
    names = data["world"]["mapNames"]
    order = map_order(data)
    n = len(order)
    lines = [HEADER]
    for i, mid in enumerate(order):
        lines.append(f"#define {map_sym(mid)} {i}")
    lines.append(f"#define MAP_N {n}")
    lines.append("")
    for mid in order:
        rows = maps[mid]
        lines.append(f"static const char *const map_{mid}_rows[] = {{")
        for r in rows:
            lines.append(f'    "{c_escape(r)}",')
        lines.append("};")
        lines.append("")
    lines.append(f"static const Map MAPS[MAP_N] = {{")
    for mid in order:
        rows = maps[mid]
        cols = max(len(r) for r in rows)
        lines.append(f"    {{ map_{mid}_rows, {cols}, {len(rows)} }},")
    lines.append("};")
    lines.append("")
    lines.append(f"static const char *const MAP_DISPLAY_NAME[MAP_N] = {{")
    lines.append("    " + ", ".join(f'"{c_escape(dc_text(names[m]))}"' for m in order) + ",")
    lines.append("};")
    lines.append("")
    solid = data["maps"].get("solid", "#HWRBC^NKEVAQXUJISMGL89r")
    lines.append(f'static const char *const SOLID_TILES = "{c_escape(solid)}";')
    lines.append("")
    out.write_text("\n".join(lines) + "\n")


def bake_talk(data: dict, out: Path) -> None:
    talk = data["dialogue"]["talk"]
    ending = data["dialogue"]["endingWin"]
    ending_heavenfall = data["dialogue"].get("endingWinHeavenfall") or ending
    table = talk_table(data)
    lines = [HEADER, "#if defined(__GNUC__)"]
    lines.append("#pragma GCC diagnostic ignored \"-Wunused-const-variable\"")
    lines.append("#endif")
    lines.append("")
    for key, symbol in table:
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
    lines.append("static const char *const DEMO_END_HEAVENFALL[] = {")
    for s in ending_heavenfall:
        lines.append(f'    "{c_escape(dc_text(s))}",')
    lines.append("};")
    lines.append("")
    lines.append("#define TALK_LEN(arr) (int)(sizeof(arr) / sizeof((arr)[0]))")
    lines.append("")
    lines.append("static const TalkBeat *const TALK_PTRS[] = {")
    for _key, symbol in table:
        lines.append(f"    {symbol},")
    lines.append("};")
    lines.append("static const int TALK_COUNTS[] = {")
    for _key, symbol in table:
        lines.append(f"    TALK_LEN({symbol}),")
    lines.append("};")
    lines.append(f"#define TALK_TABLE_N {len(table)}")
    lines.append("")
    out.write_text("\n".join(lines) + "\n")


def nature_index(data: dict, species_entry: dict) -> int:
    """Index into logic.json `natures` for a species' crystal. A crystal is a
    property of the species, so this is looked up once at bake time rather
    than stored per monster."""
    ids = [n["id"] for n in (data["logic"].get("natures") or [])]
    nid = species_entry.get("nature")
    if nid is None:
        raise SystemExit(f"species {species_entry.get('id')!r} has no `nature`")
    if nid not in ids:
        raise SystemExit(
            f"species {species_entry.get('id')!r} nature {nid!r} is not in "
            f"logic.json natures {ids}"
        )
    return ids.index(nid)


ATK_STAT_SYM = {"str": "ATK_STR", "mag": "ATK_MAG"}


def atk_stat_sym(stat: str, where: str) -> str:
    if stat not in ATK_STAT_SYM:
        raise SystemExit(f"{where}: stat {stat!r} must be \"str\" or \"mag\"")
    return ATK_STAT_SYM[stat]


def bake_species(data: dict, out: Path) -> None:
    spec = data["species"]
    order = species_order(data)
    n = len(order)
    lines = [HEADER]
    for i, sid in enumerate(order):
        lines.append(f"#define {sp_sym(sid)} {i}")
    lines.append(f"#define SPECIES_N {n}")
    lines.append("")

    # Cathleen's spell kit is a fixed global table (4 ids, always the same
    # power/speed/stat) baked once here rather than per-species, since every
    # spell-casting species would otherwise repeat the same 4 rows.
    spell_defs: dict[int, dict] = {}
    for sid in order:
        for sp in spec[sid].get("spells") or []:
            idx = SPELL[sp["id"]]
            row = {"stat": sp["stat"], "power": sp["power"], "speed": sp["speed"]}
            prev = spell_defs.get(idx)
            if prev is not None and prev != row:
                raise SystemExit(
                    f"spell {sp['id']!r} has conflicting stat/power/speed "
                    f"across species: {prev} vs {row}"
                )
            spell_defs[idx] = row
    lines.append("static const SpellDef SPELLS[4] = {")
    for idx in range(4):
        row = spell_defs.get(idx, {"stat": "mag", "power": 1.0, "speed": 1.0})
        lines.append(
            f"    {{ {atk_stat_sym(row['stat'], 'spell ' + str(idx))}, "
            f"{float(row['power'])}f, {float(row['speed'])}f }},"
        )
    lines.append("};")
    lines.append("")

    lines.append(f"static const Species SPECIES[SPECIES_N] = {{")
    for sid in order:
        s = spec[sid]
        spells = s.get("spells") or []
        ids = [SPELL[sp["id"]] for sp in spells]
        while len(ids) < 4:
            ids.append(0)
        nsp = len(spells)
        evo = s.get("evolvesTo")
        if evo and evo not in spec:
            raise SystemExit(f"species {sid!r} evolvesTo {evo!r} is not a species")
        evo_to = order.index(evo) if evo else -1
        name = dc_text(s["name"])
        basic = dc_text(s["basic"])
        special = dc_text(s["special"])
        lines.append(
            f'    {{ "{c_escape(name)}", "{c_escape(basic)}", "{c_escape(special)}", '
            f'{s["maxHp"]}, {s["str"]}, {s["agl"]}, {s["spc"]}, {s["specialPp"]}, '
            f"{atk_stat_sym(s['basicStat'], sid + '.basicStat')}, "
            f"{atk_stat_sym(s['specialStat'], sid + '.specialStat')}, "
            f"{float(s['basicPower'])}f, {float(s['basicSpeed'])}f, "
            f"{float(s['specialPower'])}f, {float(s['specialSpeed'])}f, "
            f"{nsp}, {{{ids[0]},{ids[1]},{ids[2]},{ids[3]}}}, "
            f"{nature_index(data, s)}, {evo_to} }},"
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
    rep = logic.get("reputation") or {}
    lines.append(f"#define LOGIC_REP_MIN {int(rep.get('min', -100))}")
    lines.append(f"#define LOGIC_REP_MAX {int(rep.get('max', 100))}")
    lines.append(f"#define LOGIC_REP_FATHER_REVIVE {int(rep.get('fatherRevive', 25))}")
    kind = str(rep.get("kindName") or "Max")
    lines.append(f'#define LOGIC_REP_KIND_NAME "{c_escape(dc_text(kind))}"')
    lines.append(f"#define LOGIC_REP_PRICE_POS_PCT {int(rep.get('pricePosPct', 1))}")
    lines.append(f"#define LOGIC_REP_PRICE_NEG_PCT {int(rep.get('priceNegPct', 5))}")
    lines.append(f"#define LOGIC_REP_MIN_PRICE {int(rep.get('minPrice', 1))}")
    lines.append(f"#define LOGIC_REP_REFUSE_AT {int(rep.get('refuseAt', -100))}")
    lines.append(f"#define LOGIC_REP_FREE_AT {int(rep.get('freeAt', 100))}")
    lines.append(f"#define LOGIC_MASON_AMBUSH_NEED_PARTY {1 if ambush.get('needParty') else 0}")
    lines.append(f"#define LOGIC_MASON_AMBUSH_UNLESS_BEAT {1 if ambush.get('unless') == 'foughtMason' else 0}")
    maps = ", ".join(map_sym(m) for m in rematch["maps"])
    lines.append(f"static const int LOGIC_MASON2_MAPS[] = {{ {maps} }};")
    lines.append(f"#define LOGIC_MASON2_MAP_N {len(rematch['maps'])}")
    lines.append("")
    natures = logic.get("natures") or []
    # `ring` is the matchup order and is independent of this array's order,
    # which is frozen by the save layout (party slot byte 12 stores the index).
    types = logic.get("natureTypes") or {}
    ring = list(types.get("ring") or [])
    ids = [n["id"] for n in natures]
    if len(ids) != len(set(ids)):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        raise SystemExit(f"logic.json natures has duplicate id(s): {dupes}")
    if natures and not ring:
        raise SystemExit(
            "logic.json natureTypes.ring is missing -- every crystal needs a "
            "matchup position"
        )
    if ring:
        if len(ring) != len(set(ring)):
            dupes = sorted({i for i in ring if ring.count(i) > 1})
            raise SystemExit(f"logic.json natureTypes.ring has duplicate id(s): {dupes}")
        if len(ring) != len(ids):
            raise SystemExit(
                f"logic.json natureTypes.ring length {len(ring)} does not match "
                f"natures length {len(ids)}"
            )
        if sorted(ring) != sorted(ids):
            raise SystemExit(
                f"logic.json natureTypes.ring does not match natures ids: "
                f"{sorted(ring)} vs {sorted(ids)}"
            )
        for nat in natures:
            for stat in ("str", "agl", "spc"):
                v = nat.get(stat) or 0
                if v < 0:
                    raise SystemExit(
                        f"logic.json natures {nat.get('id')!r} has negative "
                        f"{stat} bonus {v} -- crystal stat bonuses must never "
                        f"be negative"
                    )
        strong_mul = types.get("strongMul")
        weak_mul = types.get("weakMul")
        if not isinstance(strong_mul, (int, float)) or strong_mul <= 0:
            raise SystemExit(f"logic.json natureTypes.strongMul must be a positive number, got {strong_mul!r}")
        if not isinstance(weak_mul, (int, float)) or weak_mul <= 0:
            raise SystemExit(f"logic.json natureTypes.weakMul must be a positive number, got {weak_mul!r}")
        beats_ahead = types.get("beatsAhead")
        if not isinstance(beats_ahead, int) or beats_ahead < 1 or beats_ahead * 2 >= len(ring):
            raise SystemExit(
                f"logic.json natureTypes.beatsAhead must be a positive int less "
                f"than half the ring length ({len(ring)}), got {beats_ahead!r}"
            )
    lines.append("typedef struct { const char *name; int str, agl, spc; int ring; } NatureDef;")
    lines.append(f"#define NATURE_N {len(natures)}")
    lines.append("static const NatureDef NATURES[NATURE_N] = {")
    for nat in natures:
        pos = ring.index(nat["id"]) if ring else 0
        lines.append(
            f'    {{ "{c_escape(dc_text(nat["name"]))}", '
            f'{int(nat.get("str") or 0)}, {int(nat.get("agl") or 0)}, '
            f'{int(nat.get("spc") or 0)}, {pos} }},'
        )
    lines.append("};")
    if ring:
        lines.append("/* Crystal matchups: each crystal splits the next")
        lines.append("   NATURE_BEATS_AHEAD around the ring and is split by the")
        lines.append("   previous that many. Derived, not a stored matrix. */")
        lines.append(f"#define NATURE_RING_N {len(ring)}")
        lines.append(f"#define NATURE_BEATS_AHEAD {int(types.get('beatsAhead') or 0)}")
        lines.append(f"#define NATURE_STRONG_MUL {float(types.get('strongMul') or 1.0)}f")
        lines.append(f"#define NATURE_WEAK_MUL {float(types.get('weakMul') or 1.0)}f")
        lines.append(
            f'#define NATURE_STRONG_TEXT "{c_escape(dc_text(types.get("strongText") or ""))}"')
        lines.append(
            f'#define NATURE_WEAK_TEXT "{c_escape(dc_text(types.get("weakText") or ""))}"')
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
    lines.append("/* Guard resolution -- see content/logic.json's combat block. */")
    lines.append(f"#define DODGE_DEF_RAND_MIN {float(combat.get('dodgeDefenderRandMin') or 1.0)}f")
    lines.append(f"#define DODGE_DEF_RAND_MAX {float(combat.get('dodgeDefenderRandMax') or 1.0)}f")
    lines.append(f"#define GUARD_RAND_MIN {float(combat.get('guardRandMin') or 1.0)}f")
    lines.append(f"#define GUARD_RAND_MAX {float(combat.get('guardRandMax') or 1.0)}f")
    lines.append(f"#define BARRIER_HEAL_DIVISOR {int(combat.get('barrierHealDivisor') or 1)}")
    lines.append(
        f'#define GUARD_PARRIED_TEXT "{c_escape(dc_text(combat.get("parriedText") or ""))}"')
    lines.append(
        f'#define GUARD_ABSORBED_TEXT "{c_escape(dc_text(combat.get("absorbedText") or ""))}"')
    mg = combat.get("minigame") or {}
    lines.append("/* Special timing bar -- logic.json combat.minigame. */")
    lines.append(f"#define SPEC_PERFECT_LO {float(mg.get('perfectMin') or 45)}f")
    lines.append(f"#define SPEC_PERFECT_HI {float(mg.get('perfectMax') or 55)}f")
    lines.append(f"#define SPEC_CONN_LO {float(mg.get('connectedMin') or 30)}f")
    lines.append(f"#define SPEC_CONN_HI {float(mg.get('connectedMax') or 70)}f")
    lines.append(f"#define SPEC_MUL_PERFECT {float(mg.get('perfectMul') or 2)}f")
    lines.append(f"#define SPEC_MUL_CONN {float(mg.get('connectedMul') or 1.5)}f")
    lines.append(f"#define SPEC_MUL_FIZZ {float(mg.get('fizzleMul') or 1)}f")
    lines.append(f"#define SPEC_NEEDLE_SPEED {float(mg.get('needleSpeed') or 110)}f")
    lines.append("")

    growth = logic.get("growth") or {}
    lines.append("/* Move unlocks + evolution -- logic.json growth. */")
    lines.append(f"#define LV_SECONDARY {int(growth.get('secondaryAt') or 5)}")
    lines.append(f"#define LV_SPECIAL {int(growth.get('specialAt') or 10)}")
    lines.append(f"#define LV_EVOLVE {int(growth.get('evolveAt') or 10)}")
    lines.append("")

    # Leg 2.11: stage-based stat drops (Proud Roar/Magebane/Slow Powder/
    # Overload) + real status conditions (Scorch/Blight/Bind/Veil, plus
    # Overload's Exhausted), replacing the old damage-dealing secondaries.
    lines.append("#define STAT_STR 0")
    lines.append("#define STAT_AGL 1")
    lines.append("#define STAT_SPC 2")
    lines.append("#define STATUS_NONE 0")
    lines.append("#define STATUS_BURNED 1")
    lines.append("#define STATUS_POISONED 2")
    lines.append("#define STATUS_CONFUSED 3")
    lines.append("#define STATUS_PARALYZED 4")
    lines.append("#define STATUS_EXHAUSTED 5")
    STAGE_STAT = {"str": 0, "agl": 1, "spc": 2}
    STATUS_ID = {"burned": 1, "poisoned": 2, "confused": 3, "paralyzed": 4, "exhausted": 5}

    def stage_stat_sym(s: str, where: str) -> int:
        if s not in STAGE_STAT:
            raise SystemExit(f"{where}: stat must be one of str/agl/spc, got {s!r}")
        return STAGE_STAT[s]

    def status_sym(s: str, where: str) -> int:
        if s not in STATUS_ID:
            raise SystemExit(f"{where}: status must be one of {sorted(STATUS_ID)}, got {s!r}")
        return STATUS_ID[s]

    stages = logic.get("statStages") or {}
    mult = stages.get("mult") or [1.0, 0.7, 0.4, 0.1, 0.0]
    lines.append(f"#define STAT_STAGE_MAX {int(stages.get('maxStage') or 4)}")
    lines.append(f"#define STAT_STAGE_FLOOR {int(stages.get('floorAtMaxStage') or 1)}")
    lines.append(f"#define STAT_STAGE_N {len(mult)}")
    lines.append(f"static const float STAT_STAGE_MULT[{len(mult)}] = {{ {', '.join(f'{float(x)}f' for x in mult)} }};")
    lines.append("")

    se = logic.get("statusEffects") or {}
    burned = se.get("burned") or {}
    poisoned = se.get("poisoned") or {}
    paralyzed = se.get("paralyzed") or {}
    lines.append(f"#define STATUS_BURN_PCT {int(burned.get('hpPercent') or 5)}")
    lines.append(f"#define STATUS_BURN_TURNS_MIN {int(burned.get('turnsMin') or 2)}")
    lines.append(f"#define STATUS_BURN_TURNS_MAX {int(burned.get('turnsMax') or 5)}")
    lines.append(f"#define STATUS_POISON_START_PCT {int(poisoned.get('startPercent') or 1)}")
    lines.append(f"#define STATUS_POISON_STEP_PCT {int(poisoned.get('stepPercent') or 1)}")
    lines.append(f"#define STATUS_PARALYZE_TURNS_MIN {int(paralyzed.get('turnsMin') or 1)}")
    lines.append(f"#define STATUS_PARALYZE_TURNS_MAX {int(paralyzed.get('turnsMax') or 5)}")
    lines.append("")

    shiny_move = logic.get("shinyMove") or {}
    lines.append("/* Overload -- universal shiny-exclusive move, not per-species. */")
    lines.append(f'#define SHINY_MOVE_NAME "{c_escape(dc_text(shiny_move.get("name") or "OVERLOAD"))}"')
    lines.append(
        f"#define SHINY_MOVE_STATUS {status_sym(shiny_move.get('status') or 'exhausted', 'shinyMove.status')}")
    lines.append(f"#define SHINY_MOVE_MAX_PP {int(shiny_move.get('maxPp') or 10)}")
    lines.append("")

    hype = logic.get("hypeUp") or {}
    lines.append("/* Hype Up -- learned on evolving, see bake_npc note / CURRENT_WORK 2.11. */")
    lines.append(f'#define HYPE_UP_NAME "{c_escape(dc_text(hype.get("name") or "HYPE UP"))}"')
    lines.append(f"#define HYPE_UP_PCT {int(hype.get('hypePercent') or 35)}")
    lines.append(f"#define HYPE_UP_MAX_PP {int(hype.get('maxPp') or 10)}")
    lines.append("")
    lines.append(f"#define STAT_MOVE_CAP {int(logic.get('statMoveCap') or 10)}")
    lines.append(f"#define STATUS_MOVE_CAP {int(logic.get('statusMoveCap') or 5)}")
    lines.append("")

    nmoves = logic.get("natureMoves") or []
    lines.append("typedef struct { const char *name; int kind; int stat; int status; int max_pp; } NatureMove;")
    lines.append("#define NMOVE_KIND_STAGE 0")
    lines.append("#define NMOVE_KIND_STATUS 1")
    lines.append(f"#define NATURE_MOVE_N {len(nmoves)}")
    lines.append("static const NatureMove NATURE_MOVES[NATURE_N] = {")
    by_nat = {m.get("nature"): m for m in nmoves}
    natures = logic.get("natures") or []
    if len(nmoves) != len(natures):
        raise SystemExit(f"logic.json natureMoves must have one entry per nature ({len(natures)}), got {len(nmoves)}")
    for nat in natures:
        m = by_nat.get(nat["id"])
        if not m:
            raise SystemExit(f"logic.json natureMoves missing nature {nat['id']!r}")
        where = "natureMoves." + nat["id"]
        kind = m.get("kind")
        if kind == "stage":
            kind_sym, stat, status = "NMOVE_KIND_STAGE", stage_stat_sym(m.get("stat") or "", where), 0
        elif kind == "status":
            kind_sym, stat, status = "NMOVE_KIND_STATUS", 0, status_sym(m.get("status") or "", where)
        else:
            raise SystemExit(f"{where}: kind must be 'stage' or 'status', got {kind!r}")
        max_pp = int(m.get("maxPp") or 0)
        lines.append(
            f'    {{ "{c_escape(dc_text(m.get("name") or "SECONDARY"))}", '
            f"{kind_sym}, {stat}, {status}, {max_pp} }},"
        )
    lines.append("};")
    lines.append("")
    out.write_text("\n".join(lines) + "\n")


NEED = {"tookStarter": 1, "beatCalder": 2, "beatShin": 3, "hasScroll": 4, "beatSentry": 5}
ARRIVE = {"masonAmbush": 1, "ensureSoldiers": 2}
ITEM_FX = {"heal": 1, "buff": 2, "debuff": 3, "capture": 4, "flee": 5}


def bake_world(data: dict, out: Path) -> None:
    world = data["world"]
    maps = data["maps"]
    items = data["items"]
    f = world["formulas"]
    lines = [HEADER]
    lines.append("/* Canonical world tables from content/world.json + items.json. */")
    lines.append(f"#define XP_BASE {int(f['xpBase'])}")
    lines.append(f"#define XP_PER_LEVEL {int(f['xpPerLevel'])}")
    lines.append(f"#define LEVEL_XP_MUL {int(f['levelXpMul'])}")
    lines.append(f"#define LEVEL_CAP {int(f['levelCap'])}")
    lines.append(f"#define WILD_LEVEL_CAP {int(f.get('wildLevelCap') or f['levelCap'])}")
    lines.append(f"#define LEVEL_HP {int(f['levelHp'])}")
    lines.append(f"#define LEVEL_STAT {int(f['levelStat'])}")
    lines.append(f"#define CAPTURE_AGL {int(f['captureAgl'])}")
    lines.append(f"#define CAPTURE_VULN {int(f['captureVulnerable'])}")
    lines.append(f"#define SHINY_DENOM {int(f['shinyDenom'])}")
    lines.append(f"#define ENCOUNTER_PCT {int(f['encounterPercent'])}")
    lines.append(f"#define GREATCRYSTAL_BONUS {int(f['greatcrystalBonus'])}")
    share = float(f.get("benchXpShare") or 0.5)
    lines.append(f"#define BENCH_XP_PCT {int(round(share * 100))}")
    lines.append(f"#define BITTERROOT_STR {int(f['bitterrootStr'])}")
    lines.append(f"#define WARROOT_AGL {int(f['warrootAgl'])}")
    lines.append(f"#define DUST_STR {int(f['dustStr'])}")
    lines.append(f"#define DUST_AGL {int(f['dustAgl'])}")
    lines.append(f"#define DUST_SPC {int(f['dustSpc'])}")
    lines.append(f"#define START_MARKS {int(world['startMarks'])}")
    order = items["order"]
    bag = world["startBag"]
    init = ", ".join(str(int(bag.get(i, 0))) for i in order)
    lines.append(f"#define START_BAG_INIT {{ {init} }}")
    lines.append("")
    lines.append("typedef struct {")
    lines.append("    int from_map, to_map;")
    lines.append("    char tile, spawn;")
    lines.append("    int face_down; /* 1 = arrive facing down (from south) */")
    lines.append("    int need;      /* 0 none, 1 tookStarter, 2 beatCalder, 3 beatShin, 4 hasScroll */")
    lines.append("    int on_arrive; /* 0 none, 1 masonAmbush, 2 ensureSoldiers */")
    lines.append("    int fail_talk; /* talk table index, -1 none */")
    lines.append("} WarpDef;")
    lines.append("static const WarpDef WARPS[] = {")
    for w in world["warps"]:
        frm = map_sym(w["from"])
        to = map_sym(w["to"])
        tile = w["tile"]
        spawn = w["spawn"]
        face = 1 if w.get("dir") == "down" else 0
        need = NEED.get(w.get("need") or "", 0)
        arr = ARRIVE.get(w.get("onArrive") or "", 0)
        fail = talk_id(w["failTalk"]) if w.get("failTalk") else -1
        lines.append(
            f"    {{ {frm}, {to}, '{tile}', '{spawn}', {face}, {need}, {arr}, {fail} }},"
        )
    lines.append("};")
    lines.append(f"#define WARP_N (int)(sizeof(WARPS)/sizeof(WARPS[0]))")
    lines.append("")
    sp = {s: i for i, s in enumerate(species_order(data))}
    # Sized from the data, not a guessed constant: gauntlet5's finale pool
    # (26 of 29 species) already blew past a hardcoded 8 once, silently
    # truncated by the C compiler's "excess elements in array initializer"
    # (a warning, not an error) with zero runtime signal that most of the
    # pool was gone. Never hardcode this again.
    pool_cap = max((len(e["pool"]) for e in world["encounters"]), default=1)
    lines.append("typedef struct {")
    lines.append("    int map_id;")
    lines.append("    char tile;")
    lines.append("    int rate;")
    lines.append(f"    int pool[{pool_cap}];")
    lines.append("    int pool_n;")
    lines.append("    int lv_min, lv_max;")
    lines.append("    int ty_bonus_gt; /* -1 none */")
    lines.append("} EncDef;")
    lines.append("static const EncDef ENCOUNTERS[] = {")
    enc_n = 0
    for e in world["encounters"]:
        pool = e["pool"]
        ids = [sp[s] for s in pool]
        while len(ids) < pool_cap:
            ids.append(0)
        ty = e.get("levelBonusIfTyGt")
        tyv = -1 if ty is None else int(ty)
        rate = int(round(float(e.get("rate", 0.18)) * 100))
        for mid in e["maps"]:
            plist = ",".join(str(x) for x in ids)
            lines.append(
                f"    {{ {map_sym(mid)}, '{e['tile']}', {rate}, {{ {plist} }}, {len(pool)}, "
                f"{int(e['levelMin'])}, {int(e['levelMax'])}, {tyv} }},"
            )
            enc_n += 1
    lines.append("};")
    lines.append(f"#define ENC_N {enc_n}")
    lines.append("")
    lines.append("typedef struct {")
    lines.append("    int lead_sp, lead_lv;")
    lines.append("    int bench_sp[2], bench_lv[2], bench_n;")
    lines.append("} TrainerKit;")
    kit_keys = ["sentry", "conscript", "enforcer", "cross",
                "forestRanger", "forestScout", "ruinsKeeper", "ruinsWarden", "quartz",
                "quarryDriller", "marshBog", "marshReed", "opal", "commanderFinal"]
    lines.append(f"static const TrainerKit TRAINER_KITS[{len(kit_keys)}] = {{")
    for k in kit_keys:
        t = world["trainers"][k]
        lead_sp, lead_lv = t["lead"]
        benches = t.get("bench") or []
        b0 = benches[0] if len(benches) > 0 else ["quillpup", 1]
        b1 = benches[1] if len(benches) > 1 else ["quillpup", 1]
        lines.append(
            f"    {{ {sp[lead_sp]}, {int(lead_lv)}, "
            f"{{ {sp[b0[0]]}, {sp[b1[0]]} }}, {{ {int(b0[1])}, {int(b1[1])} }}, {len(benches)} }},"
        )
    lines.append("};")
    for i, k in enumerate(kit_keys):
        lines.append(f"#define KIT_{_c_ident(k)} {i}")
    cath = world["trainers"]["cathleen"]["lead"]
    shin = world["trainers"]["shinigami"]
    shin_b = shin.get("bench") or []
    lines.append(f"#define KIT_CATHLEEN_LV {int(cath[1])}")
    lines.append(f"#define KIT_SHINIGAMI_LEAD_LV {int(shin['lead'][1])}")
    lines.append(f"#define KIT_SHINIGAMI_B0_LV {int(shin_b[0][1]) if shin_b else 14}")
    lines.append(f"#define KIT_SHINIGAMI_B1_LV {int(shin_b[1][1]) if len(shin_b) > 1 else 13}")
    lines.append("")
    # item effects in items.order
    lines.append("typedef struct { int kind, amount, str, agl, spc, base; } ItemFx;")
    lines.append("static const ItemFx ITEM_FX[] = {")
    for iid in order:
        e = items["defs"][iid].get("effect") or {}
        kind = ITEM_FX.get(e.get("kind"), 0)
        amount = int(e.get("amount") or 0)
        st = int(e.get("str") or 0)
        ag = int(e.get("agl") or 0)
        sc = int(e.get("spc") or 0)
        base = int(e["base"]) if e.get("base") is not None else 100
        lines.append(f"    {{ {kind}, {amount}, {st}, {ag}, {sc}, {base} }},")
    lines.append("};")
    lines.append("")
    # Leg 2.6: which capture-crystal tiers each shopkeeper sells, as a
    # bitmask over item indices (bit i set means ITEMS[i] is in stock).
    # SHOP_CRYSTAL_MASK is indexed by SHOP_IDS (see bake_npc_scripts,
    # which stashes that same index in each shop NpcStep's `pending`).
    item_i = {iid: i for i, iid in enumerate(order)}
    shops_cfg = (data["logic"].get("shops") or {}).get("crystalStock") or {}
    default_stock = shops_cfg.get("default") or []

    def _stock_mask(ids):
        mask = 0
        for iid in ids:
            if iid not in item_i:
                raise SystemExit(f"logic.json shops.crystalStock has unknown item {iid!r}")
            mask |= 1 << item_i[iid]
        return mask

    lines.append(f"#define SHOP_CRYSTAL_DEFAULT_MASK {_stock_mask(default_stock)}")
    lines.append("static const int SHOP_CRYSTAL_MASK[] = {")
    for name, idx in sorted(SHOP_IDS.items(), key=lambda kv: kv[1]):
        stock = shops_cfg.get(name, default_stock)
        lines.append(f"    {_stock_mask(stock)}, /* {idx}: {name} */")
    lines.append("};")
    lines.append(f"#define SHOP_CRYSTAL_MASK_N {len(SHOP_IDS)}")
    lines.append("")
    bake_npc_scripts(data, items, lines)
    out.write_text("\n".join(lines) + "\n")


FLAG_IDS = [
    "tookStarter",
    "talkedFather",
    "lootedCrate",
    "talkedWren",
    "beatCalder",
    "readCart",
    "talkedMae",
    "talkedIvo",
    "talkedNell",
    "nellBonus",
    "hasParty2",
    "gotFieldGem",
    "pikeHelped",
    "talkedPike",
    "gotHerb",
    "gotStump",
    "cathleenCaught",
    "beatShinigami",
    "beatCross",
    "beatConscript",
    "beatEnforcer",
    "beatSentry",
    "tessaGifted",
    "chestLooted",
    "birchGifted",
    "sableGifted",
    "cageOpen",
    "hasCageKey",
    "talkedReach",
]
FLAG_INDEX = {name: i for i, name in enumerate(FLAG_IDS)}

AFTER_IDS = {
    "bedHeal": 1,
    "shop": 2,
    "calder": 4,
    "cathleen": 5,
    "shinigami": 6,
    "wsoldier": 7,
}
# Shopkeeper ids referenced by world.json's "after": "shop:<id>" -- reuses
# the NpcStep.pending slot the same way NPC_AFTER_WSOLDIER reuses it for
# trainer identity, just under a different `after` code so the two
# namespaces never collide.
SHOP_IDS = {
    "bram": 0,
    "oren": 1,
    "fenn": 2,
    "dray": 3,
}
PENDING_IDS = {
    "cross": 0,
    "conscript": 1,
    "enforcer": 2,
    "sentry": 3,
    "forestRanger": 4,
    "forestScout": 5,
    "ruinsKeeper": 6,
    "ruinsWarden": 7,
    "quartz": 8,
    "marshBog": 9,
    "marshReed": 10,
    "opal": 11,
    "quarryDriller": 12,
    "commanderFinal": 13,
}


def flag_id(name) -> int:
    if not name:
        return -1
    if name not in FLAG_INDEX:
        raise SystemExit(f"unknown NPC flag {name!r}")
    return FLAG_INDEX[name]


def talk_id(key) -> int:
    if not key:
        return -1
    if key not in TALK_KEYS_ORDER:
        raise SystemExit(f"unknown talk key {key!r}")
    return TALK_KEYS_ORDER.index(key)


def _after_and_pending(after_raw, pending_raw) -> dict:
    after_raw = after_raw or ""
    if after_raw.startswith("shop:"):
        shop_name = after_raw[len("shop:"):]
        if shop_name not in SHOP_IDS:
            raise SystemExit(
                f"unknown shop id {shop_name!r} in 'after' -- add it to "
                f"tools/bake_content.py's SHOP_IDS"
            )
        return {"after": AFTER_IDS["shop"], "pending": SHOP_IDS[shop_name]}
    return {
        "after": AFTER_IDS.get(after_raw, 0),
        "pending": PENDING_IDS.get(pending_raw or "", -1),
    }


def bake_npc_scripts(data: dict, items: dict, lines: list[str]) -> None:
    world = data["world"]
    order = items["order"]
    item_i = {iid: i for i, iid in enumerate(order)}
    sp = {s: i for i, s in enumerate(species_order(data))}
    lines.append("/* NPC first-match scripts from content/world.json. */")
    flags = merged_flags(data)
    for i, name in enumerate(flags):
        lines.append(f"#define FLAG_{_c_ident(name)} {i}")
    lines.append(f"#define FLAG_N {len(flags)}")
    lines.append("#define NPC_AFTER_NONE 0")
    lines.append("#define NPC_AFTER_BED_HEAL 1")
    lines.append("#define NPC_AFTER_SHOP 2")
    lines.append("#define NPC_AFTER_CALDER 4")
    lines.append("#define NPC_AFTER_CATHLEEN 5")
    lines.append("#define NPC_AFTER_SHINIGAMI 6")
    lines.append("#define NPC_AFTER_WSOLDIER 7")
    lines.append("#define NPC_PENDING_CROSS 0")
    lines.append("#define NPC_PENDING_CONSCRIPT 1")
    lines.append("#define NPC_PENDING_ENFORCER 2")
    lines.append("#define NPC_PENDING_SENTRY 3")
    lines.append("#define NPC_PENDING_FOREST_RANGER 4")
    lines.append("#define NPC_PENDING_FOREST_SCOUT 5")
    lines.append("#define NPC_PENDING_RUINS_KEEPER 6")
    lines.append("#define NPC_PENDING_RUINS_WARDEN 7")
    lines.append("#define NPC_PENDING_QUARTZ 8")
    lines.append("#define NPC_PENDING_QUARRY_DRILLER 12")
    lines.append("#define NPC_PENDING_MARSH_BOG 9")
    lines.append("#define NPC_PENDING_MARSH_REED 10")
    lines.append("#define NPC_PENDING_OPAL 11")
    lines.append("#define NPC_PENDING_COMMANDER_FINAL 13")
    lines.append("typedef struct {")
    lines.append("    int if_flag, if_not, hide_if, set_flag;")
    lines.append("    int g_item[3], g_qty[3], g_n;")
    lines.append("    int g_sp, g_lv;")
    lines.append("    int talk, talk_if, talk_else;")
    lines.append("    int after, pending;")
    lines.append("    int heal, marks;")
    lines.append("    int take_item;")
    lines.append("} NpcStep;")
    lines.append("typedef struct {")
    lines.append("    int map_id;")
    lines.append("    char mark;")
    lines.append("    int step0, stepn;")
    lines.append("    int w, h;")
    lines.append("} NpcDef;")
    # Interact proximity is a box test against the target's own footprint
    # (see content/logic.json's interact block), not a radius: w/h come
    # from each npc entry (default defaultW/H, i.e. the human sprite size)
    # in this pack's 32px-tile space, scaled down to this port's 20px
    # tiles the same way try_npc_script's old radius constants were.
    interact_cfg = data["logic"].get("interact") or {}
    default_w = float(interact_cfg.get("defaultW") or 48)
    default_h = float(interact_cfg.get("defaultH") or 52)
    interact_buffer = float(interact_cfg.get("buffer") or 16)
    dc_scale = 20.0 / 32.0
    steps: list[dict] = []
    defs: list[tuple[str, str, int, int, int, int]] = []
    for npc in world.get("npcs") or []:
        script = npc.get("script") or []
        if not script:
            continue
        npc_w = round(float(npc.get("w") or default_w) * dc_scale)
        npc_h = round(float(npc.get("h") or default_h) * dc_scale)
        start = len(steps)
        for st in script:
            grants = list(st.get("grant") or [])
            g_item = [-1, -1, -1]
            g_qty = [0, 0, 0]
            for i, (iid, qty) in enumerate(grants[:3]):
                if iid not in item_i:
                    raise SystemExit(f"unknown grant item {iid!r}")
                g_item[i] = item_i[iid]
                g_qty[i] = int(qty)
            gm = st.get("grantMonster")
            g_sp, g_lv = (-1, 0)
            if gm:
                g_sp, g_lv = sp[gm[0]], int(gm[1])
            steps.append(
                {
                    "if_flag": flag_id(st.get("if")),
                    "if_not": flag_id(st.get("ifNot")),
                    "hide_if": flag_id(st.get("hideIf")),
                    "set_flag": flag_id(st.get("set")),
                    "g_item": g_item,
                    "g_qty": g_qty,
                    "g_n": min(3, len(grants)),
                    "g_sp": g_sp,
                    "g_lv": g_lv,
                    "talk": talk_id(st.get("talk")),
                    "talk_if": flag_id(st.get("talkIf")),
                    "talk_else": talk_id(st.get("talkElse")),
                    **_after_and_pending(st.get("after"), st.get("pending")),
                    "heal": 1 if st.get("heal") else 0,
                    "marks": int(st.get("marks") or 0),
                    "take_item": item_i[st["takeItem"]] if st.get("takeItem") else -1,
                }
            )
        n = len(steps) - start
        marks = npc.get("marks") or [npc["mark"]]
        for mark in marks:
            defs.append((npc["map"], mark, start, n, npc_w, npc_h))
    lines.append("static const NpcStep NPC_STEPS[] = {")
    for st in steps:
        gi = ",".join(str(x) for x in st["g_item"])
        gq = ",".join(str(x) for x in st["g_qty"])
        lines.append(
            f"    {{ {st['if_flag']}, {st['if_not']}, {st['hide_if']}, {st['set_flag']}, "
            f"{{ {gi} }}, {{ {gq} }}, {st['g_n']}, {st['g_sp']}, {st['g_lv']}, "
            f"{st['talk']}, {st['talk_if']}, {st['talk_else']}, {st['after']}, {st['pending']}, "
            f"{st['heal']}, {st['marks']}, {st['take_item']} }},"
        )
    lines.append("};")
    lines.append("static const NpcDef NPC_DEFS[] = {")
    for mid, mark, start, n, w, h in defs:
        lines.append(f"    {{ {map_sym(mid)}, '{mark}', {start}, {n}, {w}, {h} }},")
    lines.append("};")
    lines.append(f"#define NPC_DEF_N {len(defs)}")
    lines.append(f"#define INTERACT_BUFFER {round(interact_buffer * dc_scale)}")
    lines.append("")


def _c_ident(name: str) -> str:
    out = []
    for ch in name:
        if ch.isupper() and out:
            out.append("_")
        out.append(ch.upper())
    return "".join(out)


NOTE_OFF = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def parse_pattern(pattern: str, default_vol: int):
    events = []
    for raw in pattern.split():
        tok = raw
        vol = default_vol
        if "@" in tok:
            tok, vs = tok.rsplit("@", 1)
            vol = int(vs)
        if ":" in tok:
            name, fs = tok.split(":", 1)
            frames = max(1, int(fs))
        else:
            name, frames = tok, 8
        if name == "r":
            events.append((0, frames, 0))
            continue
        if name == "n":
            events.append((1, frames, vol))
            continue
        acc = 0
        letter = name[0]
        i = 1
        if len(name) > 1 and name[1] == "#":
            acc = 1
            i = 2
        elif len(name) > 1 and name[1] == "b":
            acc = -1
            i = 2
        elif len(name) > 1 and name[1] == "s":
            acc = 1
            i = 2
        octv = int(name[i:])
        midi = 12 * (octv + 1) + NOTE_OFF[letter] + acc
        events.append((midi, frames, vol))
    return events


WAVE_ID = {"pulse": 0, "tri": 1, "noise": 2}


def bake_track_arrays(prefix: str, tracks: list, lines: list[str]) -> None:
    for ti, tr in enumerate(tracks):
        ev = parse_pattern(tr["pattern"], int(tr.get("vol") or 8))
        lines.append(f"static const ChipEv {prefix}_t{ti}[] = {{")
        for midi, frames, vol in ev:
            lines.append(f"    {{ {midi}, {frames}, {vol} }},")
        if not ev:
            lines.append("    { 0, 1, 0 },")
        lines.append("};")
    lines.append(f"static const ChipTrack {prefix}_tr[] = {{")
    for ti, tr in enumerate(tracks):
        wave = WAVE_ID.get(tr.get("wave") or "pulse", 0)
        duty = int(tr.get("duty") or 0)
        vol = int(tr.get("vol") or 8)
        ev = parse_pattern(tr["pattern"], vol)
        n = max(1, len(ev))
        lines.append(f"    {{ {wave}, {duty}, {vol}, {prefix}_t{ti}, {n} }},")
    lines.append("};")


def bake_audio(data: dict, out: Path) -> None:
    audio = data["audio"]
    songs = audio["songs"]
    sfx = audio["sfx"]
    song_ids = list(songs.keys())
    sfx_ids = list(sfx.keys())
    lines = [HEADER, "#ifndef CONTENT_AUDIO_INC", "#define CONTENT_AUDIO_INC", ""]
    lines.append("typedef struct { unsigned char midi, frames, vol; } ChipEv;")
    lines.append("typedef struct {")
    lines.append("    unsigned char wave, duty, vol;")
    lines.append("    const ChipEv *ev;")
    lines.append("    int n;")
    lines.append("} ChipTrack;")
    lines.append("typedef struct { const ChipTrack *tr; int ntr; int loop; } ChipSong;")
    lines.append("")
    for i, sid in enumerate(song_ids):
        lines.append(f"#define SONG_{_c_ident(sid)} {i}")
    lines.append(f"#define SONG_N {len(song_ids)}")
    lines.append("")
    for i, sid in enumerate(sfx_ids):
        lines.append(f"#define SFX_{_c_ident(sid)} {i}")
    lines.append(f"#define SFX_N {len(sfx_ids)}")
    lines.append("")
    for sid, song in songs.items():
        bake_track_arrays(f"song_{sid}", song["tracks"], lines)
        lines.append("")
    for sid, s in sfx.items():
        bake_track_arrays(f"sfx_{sid}", s["tracks"], lines)
        lines.append("")
    lines.append("static const ChipSong CHIP_SONGS[SONG_N] = {")
    for sid, song in songs.items():
        ntr = len(song["tracks"])
        loop = 1 if song.get("loop", True) else 0
        lines.append(f"    {{ song_{sid}_tr, {ntr}, {loop} }},")
    lines.append("};")
    lines.append("static const ChipSong CHIP_SFX[SFX_N] = {")
    for sid, s in sfx.items():
        ntr = len(s["tracks"])
        lines.append(f"    {{ sfx_{sid}_tr, {ntr}, 0 }},")
    lines.append("};")
    lines.append("")
    map_songs = audio.get("mapSongs") or {}
    order = map_order(data)
    lines.append(f"#define MAP_SONG_N {len(order)}")
    lines.append("static const int MAP_SONG[MAP_SONG_N] = {")
    for mid in order:
        name = map_songs.get(mid, "overworld")
        idx = song_ids.index(name) if name in song_ids else 0
        lines.append(f"    SONG_{_c_ident(song_ids[idx])},")
    lines.append("};")
    title = audio.get("titleSong") or "title"
    battle = audio.get("battleSong") or "battle"
    trainer = audio.get("trainerSong") or "boss"
    ending = audio.get("endingSong") or "title"
    lines.append(f"#define SONG_ID_TITLE SONG_{_c_ident(title)}")
    lines.append(f"#define SONG_ID_BATTLE SONG_{_c_ident(battle)}")
    lines.append(f"#define SONG_ID_TRAINER SONG_{_c_ident(trainer)}")
    lines.append(f"#define SONG_ID_ENDING SONG_{_c_ident(ending)}")
    lines.append("")
    vol = audio.get("volume") or {}
    lines.append("/* Master volume scale. 1 = original, 2 = 2x that ceiling. */")
    lines.append(f"#define VOL_MIN {float(vol.get('min') if vol.get('min') is not None else 0)}f")
    lines.append(f"#define VOL_MAX {float(vol.get('max') if vol.get('max') is not None else 2)}f")
    lines.append(f"#define VOL_DEFAULT {float(vol.get('default') if vol.get('default') is not None else 1)}f")
    lines.append(f"#define VOL_STEP {float(vol.get('step') if vol.get('step') is not None else 0.1)}f")
    lines.append(f"#define BATTLE_MUSIC_MUL {float(audio.get('battleMusicMul') if audio.get('battleMusicMul') is not None else 0.5)}f")
    lines.append("")
    lines.append("#endif")
    out.write_text("\n".join(lines) + "\n")


def bake_save(data: dict, out: Path) -> None:
    save = data["save"]
    flags = save["flags"]
    items = save["itemOrder"]
    lines = [HEADER, "#ifndef CONTENT_SAVE_INC", "#define CONTENT_SAVE_INC", ""]
    lines.append(f"#define SAVE_VERSION {int(save['version'])}")
    lines.append(f"#define SAVE_SIZE {int(save['size'])}")
    lines.append(f"#define SAVE_PARTY_SLOT {int(save['partySlot'])}")
    lines.append(f"#define SAVE_PARTY_MAX 6")
    lines.append(f"#define SAVE_FLAG_N {len(flags)}")
    lines.append(f"#define SAVE_ITEM_N {len(items)}")
    for i, name in enumerate(flags):
        lines.append(f"#define SAVE_FLAG_{_c_ident(name)} {i}")
    lines.append("")
    lines.append("/* Blob layout (little-endian), shared with src/game/save.ts:")
    lines.append("   0 magic CRYM, 4 version, 5 map, 6 dir, 7 party_n,")
    lines.append("   8 x u16, 10 y u16, 12 marks u16, 14 lead, 15 battles,")
    lines.append("   16 mason2_map (0xFF none), 18 bag[10], 28 flags[8],")
    lines.append("   36 party[6]*16 (byte 12 = nature), 132 checksum u16,")
    lines.append("   134 dexSeen[4], 138 dexCaught[4]. Checksum is 0..131 only. */")
    layout = save.get("layout") or {}
    seen = layout.get("dexSeen") or [134, 4]
    caught = layout.get("dexCaught") or [138, 4]
    pnat = layout.get("partyNature") or 12
    lines.append(f"#define SAVE_DEX_SEEN {int(seen[0])}")
    lines.append(f"#define SAVE_DEX_CAUGHT {int(caught[0])}")
    lines.append(f"#define SAVE_DEX_BYTES {int(seen[1])}")
    lines.append(f"#define SAVE_PARTY_NATURE {int(pnat)}")
    lines.append("")
    lines.append("#endif")
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
    if args.out:
        outdir = args.out
    else:
        outdir = ROOT / "ports" / "dreamcast" / "src"
        if not outdir.is_dir():
            raise SystemExit(f"no bake output dir: {outdir} (pass --out)")
    h = bake_all(content, outdir)
    print(f"baked maps/talk/species/items/logic/world/audio/save PACK_HASH={h} -> {outdir}")


if __name__ == "__main__":
    main()

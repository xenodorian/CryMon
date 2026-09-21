#!/usr/bin/env python3
"""Leg 2.4 — gauntlet redesign (maps, warps, choice unlock, wipe regret, grave).

Does not rebuild CDI; run bake/check separately if needed.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GAUNTLET_IDS = [f"gauntlet{i}" for i in range(1, 7)]  # 1-5 grass, 6 grave


def maze(seed: int, exit_mark: str = "1", enter_mark: str = "2") -> list[str]:
    """Long thin maze: 16x36, tree walls, grass pockets, dead ends."""
    W, H = 16, 36
    rows = [["#"] * W for _ in range(H)]
    # vertical spine with alternating gap side
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            rows[y][x] = "."
    for y in range(4, H - 2, 4):
        side = (y // 4 + seed) % 2
        for x in range(1, W - 1):
            rows[y][x] = "#"
        gap0 = 2 if side == 0 else W - 5
        for x in range(gap0, min(gap0 + 3, W - 1)):
            rows[y][x] = "."
        # dead-end spur opposite gap
        spur = W - 3 if side == 0 else 2
        for yy in range(y - 2, y):
            if 1 <= yy < H - 1:
                rows[yy][spur] = "."
                rows[yy][spur + (1 if side == 0 else -1)] = "T"
    # grass bands
    for y in range(2, H - 2, 3):
        for x in (3, 7, 11):
            if rows[y][x] == ".":
                rows[y][x] = "T"
    rows[1][W // 2] = enter_mark
    rows[H - 2][W // 2] = exit_mark
    # clear path near entrance/exit
    for y in (1, 2, H - 3, H - 2):
        for x in range(W // 2 - 1, W // 2 + 2):
            if rows[y][x] == "#":
                rows[y][x] = "."
    rows[1][W // 2] = enter_mark
    rows[H - 2][W // 2] = exit_mark
    return ["".join(r) for r in rows]


def grave_map() -> list[str]:
    W, H = 16, 20
    rows = [["#"] * W for _ in range(H)]
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            rows[y][x] = "."
    rows[1][W // 2] = "2"  # enter from gauntlet5
    rows[H // 2][W // 2] = "G"  # gravestone interact mark
    rows[H - 2][W // 2] = "P"  # stand point
    return ["".join(r) for r in rows]


def main() -> None:
    # ---- maps.json ----
    mp = ROOT / "content" / "maps.json"
    maps = json.loads(mp.read_text())
    rows = maps["rows"]
    # keep legacy key 'gauntlet' as alias of gauntlet1 for old warps
    for i, mid in enumerate(GAUNTLET_IDS):
        if i < 5:
            rows[mid] = maze(i + 1)
        else:
            rows[mid] = grave_map()
    rows["gauntlet"] = [r for r in rows["gauntlet1"]]  # alias
    mp.write_text(json.dumps(maps, indent="\t") + "\n")
    print("maps.json", GAUNTLET_IDS)

    # ---- map_meta ----
    meta_p = ROOT / "content" / "world_parts" / "map_meta.json"
    meta = json.loads(meta_p.read_text())
    names = meta.setdefault("mapNames", {})
    ids = meta.setdefault("mapIds", [])
    for i, mid in enumerate(GAUNTLET_IDS):
        if i < 5:
            names[mid] = f"GAUNTLET {i + 1}"
        else:
            names[mid] = "THE GRAVE"
    names["gauntlet"] = "GAUNTLET 1"
    for mid in GAUNTLET_IDS:
        if mid not in ids:
            ids.append(mid)
    meta_p.write_text(json.dumps(meta, indent=2) + "\n")
    print("map_meta")

    # ---- save.json mapOrder ----
    sp = ROOT / "content" / "save.json"
    save = json.loads(sp.read_text())
    order = save.setdefault("mapOrder", [])
    for mid in GAUNTLET_IDS:
        if mid not in order:
            order.append(mid)
    flags = save.setdefault("flags", [])
    for fl in ("gauntletUnlocked", "gauntletWipeRegret", "titleSlayer", "titleTamer"):
        if fl not in flags:
            flags.append(fl)
    # version bump for new flags only is optional; flags append without version ok
    sp.write_text(json.dumps(save, indent=2) + "\n")
    print("save.json flags/maps")

    # ---- warps ----
    wp = ROOT / "content" / "world_parts" / "warps.json"
    warps = json.loads(wp.read_text())
    wlist = warps.setdefault("warps", [])
    # remove old direct gauntlet warps if any
    wlist[:] = [
        w
        for w in wlist
        if not (
            (w.get("to") == "gauntlet" and w.get("from") not in GAUNTLET_IDS)
            or (w.get("from") == "gauntlet" and w.get("to") not in GAUNTLET_IDS + ["grove"])
        )
    ]
    # Grove unlock entrance (mark G behind Shinigami area)
    wlist.append(
        {
            "from": "grove",
            "tile": "G",
            "to": "gauntlet1",
            "spawn": "2",
            "dir": "down",
            "oy": 40,
            "need": "choseHeavenfall",
            "failTalk": "gauntletLocked",
        }
    )
    wlist.append(
        {
            "from": "gauntlet1",
            "tile": "2",
            "to": "grove",
            "spawn": "G",
            "dir": "up",
            "oy": -32,
        }
    )
    for i in range(5):
        a = GAUNTLET_IDS[i]
        b = GAUNTLET_IDS[i + 1] if i < 5 else None
        if i < 4:
            wlist.append(
                {
                    "from": a,
                    "tile": "1",
                    "to": GAUNTLET_IDS[i + 1],
                    "spawn": "2",
                    "dir": "down",
                    "oy": 40,
                }
            )
            wlist.append(
                {
                    "from": GAUNTLET_IDS[i + 1],
                    "tile": "2",
                    "to": a,
                    "spawn": "1",
                    "dir": "up",
                    "oy": -32,
                }
            )
        else:
            # gauntlet5 -> grave
            wlist.append(
                {
                    "from": "gauntlet5",
                    "tile": "1",
                    "to": "gauntlet6",
                    "spawn": "2",
                    "dir": "down",
                    "oy": 40,
                }
            )
            wlist.append(
                {
                    "from": "gauntlet6",
                    "tile": "2",
                    "to": "gauntlet5",
                    "spawn": "1",
                    "dir": "up",
                    "oy": -32,
                }
            )
    wp.write_text(json.dumps(warps, indent=2) + "\n")
    print("warps")

    # ---- grove map: add G mark near bottom path behind shinigami (mark 9 area) ----
    grove = maps["rows"]["grove"]
    # put G on a walkable cell near lower area; row with 9 has ...9...
    new_grove = []
    placed = False
    for line in grove:
        if (not placed) and "9" in line:
            # place G one row conceptually — modify a side cell on this line if '.'
            chars = list(line)
            for i, ch in enumerate(chars):
                if ch == "." and i < len(chars) // 2:
                    chars[i] = "G"
                    placed = True
                    break
            new_grove.append("".join(chars))
        else:
            new_grove.append(line)
    if not placed:
        # fallback: second-to-last interior row mid
        line = list(new_grove[-3])
        mid = len(line) // 2
        if line[mid] in ".=T":
            line[mid] = "G"
            new_grove[-3] = "".join(line)
            placed = True
    maps["rows"]["grove"] = new_grove
    mp.write_text(json.dumps(maps, indent="\t") + "\n")
    print("grove G placed", placed)

    # ---- encounters ----
    ep = ROOT / "content" / "world_parts" / "encounters.json"
    enc = json.loads(ep.read_text())
    elist = enc.setdefault("encounters", [])
    # strip old gauntlet encounters
    elist[:] = [e for e in elist if "gauntlet" not in str(e.get("maps", []))]
    pools = [
        ["quillpup", "glimmoth", "peatling", "emberling"],
        ["razorbat", "briarfox", "fenwisp", "glowcap"],
        ["duskhorn", "mossback", "thornhide", "cindermite"],
        ["sableclaw", "stormwing", "ashenmaw", "gravelurk"],
    ]
    for i in range(4):
        elist.append(
            {
                "maps": [GAUNTLET_IDS[i]],
                "tile": "T",
                "rate": 0.22,
                "pool": pools[i],
                "levelMin": 8 + i * 2,
                "levelMax": 11 + i * 2,
            }
        )
    # map 5: almost every species except one-offs
    species = json.loads((ROOT / "content" / "species.json").read_text())
    all_ids = list(species.keys())
    exclude = {"cathleen", "heavenfall"}
    pool5 = [s for s in all_ids if s not in exclude]
    elist.append(
        {
            "maps": ["gauntlet5"],
            "tile": "T",
            "rate": 0.25,
            "pool": pool5,
            "levelMin": 16,
            "levelMax": 20,
        }
    )
    ep.write_text(json.dumps(enc, indent=2) + "\n")
    print("encounters", len(pool5), "on map5")

    # ---- trainers: remove commanderFinal from active use (leave JSON stub) ----
    # ---- npcs: strip commanderFinal overworld on gauntlet ----
    np = ROOT / "content" / "world_parts" / "npcs.json"
    npcs = json.loads(np.read_text())
    nlist = npcs if isinstance(npcs, list) else npcs.get("npcs", [])
    before = len(nlist)
    nlist[:] = [
        n
        for n in nlist
        if not (
            n.get("id") in ("commanderFinal", "commander")
            and n.get("map") in ("gauntlet", "gauntlet1", None)
        )
        and n.get("id") != "commanderFinal"
    ]
    # gravestone pseudo-npc on gauntlet6
    nlist.append(
        {
            "map": "gauntlet6",
            "mark": "G",
            "id": "gravestone",
            "sprite": "",
            "talk": "gauntletGraveNeedScroll",
            "script": [
                {"talk": "gauntletGraveNeedScroll", "unless": "hasScroll"},
                {
                    "talk": "gauntletGraveRise",
                    "if": "hasScroll",
                    "pending": "heavenfallGrave",
                },
            ],
        }
    )
    if isinstance(npcs, dict):
        npcs["npcs"] = nlist
        np.write_text(json.dumps(npcs, indent=2) + "\n")
    else:
        np.write_text(json.dumps(nlist, indent=2) + "\n")
    print("npcs removed", before - len(nlist) + 1, "added grave")

    # ---- dialogue snippets ----
    dp = ROOT / "content" / "dialogue.json"
    if not dp.exists():
        dp = ROOT / "content" / "world_parts" / "dialogue.json"
    # dialogue may be top-level content/dialogue.json
    for cand in (
        ROOT / "content" / "dialogue.json",
        ROOT / "content" / "talk.json",
    ):
        if cand.exists():
            dp = cand
            break
    if dp.exists():
        dia = json.loads(dp.read_text())
        talks = dia.get("talk") or dia.get("talks") or dia
        if not isinstance(talks, dict):
            talks = {}
            dia["talk"] = talks

        def lines(*msgs, speaker="max"):
            return [{"speaker": speaker, "text": m} for m in msgs]

        talks["gauntletLocked"] = lines(
            "The path behind Shinigami is sealed.",
            "Only those who sought Heavenfall may pass.",
            speaker="system",
        )
        talks["gauntletWipeRegret"] = lines(
            "I chose power over Father's life.",
            "I thought Heavenfall was worth any price.",
            "Now I walk this path alone.",
            "Father... I wish you were still here.",
        )
        talks["gauntletGraveNeedScroll"] = lines(
            "A cold gravestone. The runes itch for the scroll.",
            speaker="system",
        )
        talks["gauntletGraveRise"] = lines(
            "The scroll burns. The earth answers.",
            "Heavenfall rises.",
            speaker="system",
        )
        if "talk" in dia:
            dia["talk"] = talks
        elif "talks" in dia:
            dia["talks"] = talks
        else:
            dia = talks
        dp.write_text(json.dumps(dia, indent=2) + "\n")
        print("dialogue", dp)
    else:
        print("WARN no dialogue.json")

    # ---- trainers heavenfallGrave ----
    tp = ROOT / "content" / "world_parts" / "trainers.json"
    trainers = json.loads(tp.read_text())
    troot = trainers.get("trainers", trainers)
    troot["heavenfallGrave"] = {
        "title": "Heavenfall answers the scroll",
        "name": "Heavenfall",
        "winTalk": "gauntletGraveWin",
        "set": "beatHeavenfall",
        "party": [{"species": "heavenfall", "level": 20}],
    }
    if "trainers" in trainers:
        trainers["trainers"] = troot
        tp.write_text(json.dumps(trainers, indent=2) + "\n")
    else:
        tp.write_text(json.dumps(troot, indent=2) + "\n")
    print("trainer heavenfallGrave")

    if "beatHeavenfall" not in flags:
        flags.append("beatHeavenfall")
        sp.write_text(json.dumps(save, indent=2) + "\n")

    # ---- types.ts MapId ----
    typ = ROOT / "src" / "game" / "types.ts"
    if typ.exists():
        tt = typ.read_text()
        old = re.search(r'export type MapId = [^;]+;', tt)
        if old:
            parts = [
                '"house"',
                '"veld"',
                '"forest"',
                '"grove"',
                '"camp"',
                '"cliffs"',
                '"ruins"',
                '"reach"',
                '"marsh"',
                '"quarry"',
                '"gauntlet"',
            ] + [f'"{m}"' for m in GAUNTLET_IDS]
            neu = "export type MapId = " + " | ".join(parts) + ";"
            tt = tt[: old.start()] + neu + tt[old.end() :]
            typ.write_text(tt)
            print("types MapId")

    # ---- engine.ts critical flow ----
    eng = ROOT / "src" / "game" / "engine.ts"
    et = eng.read_text()

    # 1) ending afterTalk: no auto gauntlet warp
    et2 = et.replace(
        'if (next === "ending") {\n\t\t\t\tthis.warpTo("gauntlet", "2", "down");',
        'if (next === "ending") {\n\t\t\t\t/* 2.4: Father stays in world; Heavenfall path only unlocks gauntlet (choseHeavenfall). */\n\t\t\t\tif (this.choseHeavenfall) {\n\t\t\t\t\tthis.gauntletUnlocked = true;\n\t\t\t\t\tthis.note("A path opened behind Shinigami.");\n\t\t\t\t}',
    )
    if et2 == et:
        # alternate formatting
        et2 = et.replace(
            'this.warpTo("gauntlet", "2", "down");',
            'if (this.choseHeavenfall) { this.gauntletUnlocked = true; this.note("A path opened behind Shinigami."); }',
            1,
        )
    et = et2
    print("ending warp patched", "gauntletUnlocked" in et)

    # 2) fields
    if "gauntletUnlocked" not in et:
        et = et.replace(
            "choseHeavenfall = false;",
            "choseHeavenfall = false;\n\tgauntletUnlocked = false;\n\tgauntletWipeRegret = false;\n\ttitleSlayer = false;\n\ttitleTamer = false;",
            1,
        )
        et = et.replace(
            "this.choseHeavenfall = false;",
            "this.choseHeavenfall = false;\n\t\tthis.gauntletUnlocked = false;\n\t\tthis.gauntletWipeRegret = false;\n\t\tthis.titleSlayer = false;\n\t\tthis.titleTamer = false;",
            1,
        )

    # 3) party wipe from gauntlet maps -> regret once
    wipe_anchor = 'if (this.fade.action === "loss") {\n\t\t\tif (LOGIC.partyWipe.healParty) this.sleepHeal();'
    wipe_new = '''if (this.fade.action === "loss") {
			const fromGauntlet = String(this.world.mapId).startsWith("gauntlet");
			if (LOGIC.partyWipe.healParty) this.sleepHeal();
			if (fromGauntlet && this.choseHeavenfall && !this.gauntletWipeRegret) {
				this.gauntletWipeRegret = true;
				this.say(TALK.gauntletWipeRegret);
			}'''
    if wipe_anchor in et and "gauntletWipeRegret = true" not in et:
        et = et.replace(wipe_anchor, wipe_new, 1)
        print("wipe regret")
    elif "gauntletWipeRegret = true" in et:
        print("wipe regret already")
    else:
        print("WARN wipe anchor missing")

    # 4) playerDisplayName titles
    if "titleSlayer" not in et or "Heaven Slayer" not in et:
        et = et.replace(
            "if (this.revivedFather) return LOGIC.reputation?.kindName || \"Max The Kind\";\n\t\treturn SPEAKER_NAME.max || \"Max\";",
            "if (this.titleSlayer) return \"Heaven Slayer\";\n\t\tif (this.titleTamer) return \"Heaven Tamer\";\n\t\tif (this.revivedFather) return LOGIC.reputation?.kindName || \"Max The Kind\";\n\t\treturn SPEAKER_NAME.max || \"Max\";",
            1,
        )
        print("display names")

    # 5) snapshot flags for new fields — best-effort in flags object
    for fl, prop in [
        ("gauntletUnlocked", "gauntletUnlocked"),
        ("gauntletWipeRegret", "gauntletWipeRegret"),
        ("titleSlayer", "titleSlayer"),
        ("titleTamer", "titleTamer"),
        ("choseHeavenfall", "choseHeavenfall"),
    ]:
        pass  # engine already maps many flags via snapshot flags dict — ensure choseHeavenfall in flags

    # flag mapping often via this.flags or individual fields + snapshot
    # Patch applySave/snapshot if they list beatCommander style fields
    if "gauntletUnlocked: this.gauntletUnlocked" not in et:
        if "choseHeavenfall: this.choseHeavenfall" in et:
            et = et.replace(
                "choseHeavenfall: this.choseHeavenfall",
                "choseHeavenfall: this.choseHeavenfall,\n\t\t\t\tgauntletUnlocked: this.gauntletUnlocked,\n\t\t\t\tgauntletWipeRegret: this.gauntletWipeRegret,\n\t\t\t\ttitleSlayer: this.titleSlayer,\n\t\t\t\ttitleTamer: this.titleTamer",
                1,
            )
            print("snapshot fields")

    eng.write_text(et)
    print("engine written")

    # merge world if script exists
    merge = ROOT / "tools" / "merge_world.py"
    if merge.exists():
        import subprocess

        subprocess.check_call(["python3", str(merge)])
        print("merged world.json")

    print("DONE Leg 2.4 content pass")


if __name__ == "__main__":
    main()

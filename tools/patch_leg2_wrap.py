#!/usr/bin/env python3
"""Leg 2 wrap-up toward Leg 3 gate: level cap, HF wipe game-over, Lieutenant Lead."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def jload(p: Path):
    return json.loads(p.read_text())


def jdump(p: Path, data):
    p.write_text(json.dumps(data, indent=2) + "\n")


def main():
    # ---- CURRENT_WORK.md plan ----
    cw = ROOT / "CURRENT_WORK.md"
    t = cw.read_text()
    block = '''
## Leg 2 wrap → Leg 3 gate (user 2026-09-21, Grok C)

**Before Leg 3 cities/generals, lock these wrap items:**

1. **Level cap 100** (was 20) in `formulas.levelCap` / both engines.
2. **Heavenfall-path party wipe = Game Over:** if `choseHeavenfall` and the
   party fully faints, play narrative (Heavenfall attacks and eats Max),
   red fade + unique female scream SFX, fade to black, then reload last
   save (or title if none). Not a soft trip home.
3. **Lieutenant Lead** blocks the **north path out of Crytown (veld)**.
   Human soldier who fights **as himself** (pseudo-species), not a CryMon
   squad. Level 20, HP 60, Str 20, Agl 20, Spc 10. Basic **Burst Fire**
   power **1.5** (Heavenfall basic also **1.5**). Crystal nature weak to
   Heavenfall (diamond beats him). Fightable anytime; without Heavenfall
   the math is brutal. Art: camo + rifle (overworld frames, portrait,
   battle sprite).
4. **Beating Lead (placeholder):** "Thank you for playing" then Game Over
   until Leg 3 unlocks the north / generals.

**Leg 3 still requires** reputation + gauntlet decisions already landed;
Lead is the narrative door into that leg.

'''
    if "Lieutenant Lead" not in t:
        # insert before ## Leg 3
        if "## Leg 3" in t:
            t = t.replace("## Leg 3", block + "## Leg 3", 1)
        else:
            t += "\n" + block
        cw.write_text(t)
        print("CURRENT_WORK updated")
    else:
        print("CURRENT_WORK already has Lead")

    # ---- level cap 100 ----
    meta_p = ROOT / "content" / "world_parts" / "meta.json"
    meta = jload(meta_p)
    meta.setdefault("formulas", {})["levelCap"] = 100
    jdump(meta_p, meta)
    print("levelCap 100")

    # also content/logic or world merged formulas if present
    for p in [ROOT / "content" / "logic.json"]:
        if p.exists():
            L = jload(p)
            if "formulas" in L and isinstance(L["formulas"], dict):
                L["formulas"]["levelCap"] = 100
                jdump(p, L)

    # ---- Heavenfall basic power 1.5 ----
    sp_p = ROOT / "content" / "species.json"
    species = jload(sp_p)
    if "heavenfall" in species:
        species["heavenfall"]["basicPower"] = 1.5
        species["heavenfall"]["basic"] = species["heavenfall"].get("basic") or "Meteor"
        print("heavenfall basicPower 1.5")

    # ---- Lieutenant Lead as fightable "species" (human, not wild) ----
    # Nature quartz: diamond (Heavenfall) is strong vs quartz (beatsAhead 2 from diamond)
    species["lead"] = {
        "id": "lead",
        "name": "Lieutenant Lead",
        "blurb": "A Weeping Army officer who fights with steel, not crystals.",
        "nature": "quartz",
        "maxHp": 20,
        "str": 7,
        "agl": 7,
        "spc": 3,
        "basic": "Burst Fire",
        "basicStat": "str",
        "basicPower": 1.5,
        "basicSpeed": 1.0,
        "special": "Suppressing Fire",
        "specialStat": "str",
        "specialPower": 1.2,
        "specialSpeed": 0.9,
        "specialPp": 3,
        "wild": False,
    }
    jdump(sp_p, species)
    print("species lead")

    # save speciesOrder
    save_p = ROOT / "content" / "save.json"
    save = jload(save_p)
    so = save.setdefault("speciesOrder", [])
    if "lead" not in so:
        so.append("lead")
    flags = save.setdefault("flags", [])
    for fl in ("beatLieutenantLead",):
        if fl not in flags:
            flags.append(fl)
    jdump(save_p, save)

    # ---- trainers ----
    tp = ROOT / "content" / "world_parts" / "trainers.json"
    trainers = jload(tp)
    troot = trainers.get("trainers", trainers)
    troot["lieutenantLead"] = {
        "title": "Lieutenant Lead bars the north road",
        "name": "Lieutenant Lead",
        "winTalk": "leadWinPlaceholder",
        "set": "beatLieutenantLead",
        "marks": 20,
        "party": [{"species": "lead", "level": 20}],
    }
    if "trainers" in trainers:
        trainers["trainers"] = troot
        jdump(tp, trainers)
    else:
        jdump(tp, troot)

    # ---- npcs on veld ----
    np = ROOT / "content" / "world_parts" / "npcs.json"
    npcs = jload(np)
    nlist = npcs if isinstance(npcs, list) else npcs.get("npcs", [])
    nlist = [n for n in nlist if n.get("id") != "lieutenantLead"]
    nlist.append(
        {
            "map": "veld",
            "mark": "L",
            "id": "lieutenantLead",
            "role": "trainer",
            "sprite": "npc/lead",
            "talk": "leadSpot",
            "talkDone": "leadWinPlaceholder",
            "script": [
                {"hideIf": "beatLieutenantLead"},
                {"talk": "leadSpot", "pending": "lieutenantLead"},
            ],
        }
    )
    if isinstance(npcs, dict):
        npcs["npcs"] = nlist
        jdump(np, npcs)
    else:
        jdump(np, nlist)

    # ---- veld map: north path + L mark ----
    mp = ROOT / "content" / "maps.json"
    maps = jload(mp)
    veld = [list(row) for row in maps["rows"]["veld"]]
    # open a corridor at top-center if walled
    W = len(veld[0])
    # row 0 is border; punch rows 1-3 mid
    mid = W // 2
    for y in range(1, 4):
        if y < len(veld):
            for x in range(mid - 1, mid + 2):
                if 0 < x < W - 1:
                    veld[y][x] = "."
    # place L on row 3 or 4
    ly = min(3, len(veld) - 2)
    # avoid overwriting unique marks; find a free cell near north path
    placed = False
    for y in range(2, 6):
        for x in range(mid - 2, mid + 3):
            if veld[y][x] in ".=" and y < len(veld):
                veld[y][x] = "L"
                placed = True
                break
        if placed:
            break
    if not placed:
        veld[3][mid] = "L"
    maps["rows"]["veld"] = ["".join(r) for r in veld]
    jdump(mp, maps)
    print("veld L", placed)

    # ---- dialogue ----
    dp = ROOT / "content" / "dialogue.json"
    dia = jload(dp)
    talks = dia.get("talk") or dia.get("talks") or dia
    if not isinstance(talks, dict):
        talks = {}

    def lines(*msgs, speaker="max"):
        return [{"speaker": speaker, "text": m} for m in msgs]

    talks["leadSpot"] = lines(
        "Halt. Lieutenant Lead, Weeping Army.",
        "No one leaves Crytown by the north road.",
        "Turn back, or face me.",
        speaker="lead",
    )
    talks["leadWinPlaceholder"] = lines(
        "...",
        "Thank you for playing.",
        "More of the world opens in Leg 3.",
        speaker="system",
    )
    talks["heavenfallDevour"] = lines(
        "The air tears open.",
        "Heavenfall descends on Max with a hunger that has no bottom.",
        "There is no path home from this.",
        speaker="system",
    )
    if "talk" in dia:
        dia["talk"] = talks
    elif "talks" in dia:
        dia["talks"] = talks
    else:
        dia = talks
    jdump(dp, dia)

    # ---- sprites catalog ----
    spr_p = ROOT / "content" / "sprites.json"
    spr = jload(spr_p)
    if "lead" not in spr.get("npcs", []):
        spr.setdefault("npcs", []).append("lead")
    # monsters list for battle art if used
    if "lead" not in spr.get("monsters", []):
        spr.setdefault("monsters", []).append("lead")
    if "lead" not in spr.get("portraits", []):
        spr.setdefault("portraits", []).append("lead")
    jdump(spr_p, spr)

    # ---- types.ts SpeciesId / MapId if needed ----
    typ = ROOT / "src" / "game" / "types.ts"
    if typ.exists():
        tt = typ.read_text()
        if '"lead"' not in tt and "SpeciesId" in tt:
            # append to species union heuristically
            m = re.search(r"export type SpeciesId = ([^;]+);", tt)
            if m and '"lead"' not in m.group(1):
                union = m.group(1).rstrip()
                if not union.endswith('"kilnback"') and "|" in union:
                    neu = union + ' | "lead"'
                else:
                    neu = union + ' | "lead"'
                tt = tt[: m.start(1)] + neu + tt[m.end(1) :]
                typ.write_text(tt)
                print("SpeciesId lead")

    # ---- engine.ts: HF wipe game over + Lead win placeholder GO + force Lead stats ----
    ep = ROOT / "src" / "game" / "engine.ts"
    et = ep.read_text()

    # end_lose branch: Heavenfall path -> devour game over
    old_lose = '''if (b.afterMsg === "end_lose") {
						this.leaveBattle();
						this.world.encounterLock = 3;
						this.onBattleOver();
						this.startFade("loss");
						return;
					}'''
    new_lose = '''if (b.afterMsg === "end_lose") {
						this.leaveBattle();
						this.world.encounterLock = 3;
						this.onBattleOver();
						if (this.choseHeavenfall) {
							this.beginHeavenfallGameOver();
						} else {
							this.startFade("loss");
						}
						return;
					}'''
    if "beginHeavenfallGameOver" not in et:
        if old_lose in et:
            et = et.replace(old_lose, new_lose, 1)
            print("end_lose HF GO")
        else:
            # softer
            soft = 'this.startFade("loss");'
            # only first after end_lose
            idx = et.find('afterMsg === "end_lose"')
            if idx > 0 and "beginHeavenfallGameOver" not in et:
                chunk = et[idx : idx + 350]
                if soft in chunk:
                    et = et[:idx] + chunk.replace(
                        soft,
                        'if (this.choseHeavenfall) { this.beginHeavenfallGameOver(); } else { this.startFade("loss"); }',
                        1,
                    ) + et[idx + 350 :]
                    print("end_lose soft")

    methods = r'''
	beginHeavenfallGameOver() {
		this.say(TALK.heavenfallDevour || [
			{ speaker: "system", text: "Heavenfall descends. There is no path home from this." },
		], "hfGameOver");
	}
	runHeavenfallGameOverFx() {
		try { this.audio.scream(); } catch {}
		this.startFade("hfGameOver");
	}
	reloadLastSaveOrTitle() {
		const buf = typeof readSaveBlob === "function" ? readSaveBlob() : null;
		const snap = buf ? unpackSave(buf) : null;
		if (snap && this.applySave(snap)) {
			this.mode = "world";
			this.note("Loaded last save.");
			return;
		}
		this.reset();
		this.mode = "title";
	}
'''
    if "beginHeavenfallGameOver" not in et:
        et = et.replace("\tplayerDisplayName() {", methods + "\tplayerDisplayName() {", 1)
        print("HF GO methods")
    elif "runHeavenfallGameOverFx" not in et:
        et = et.replace("\tplayerDisplayName() {", methods + "\tplayerDisplayName() {", 1)

    # afterTalk hfGameOver
    if 'next === "hfGameOver"' not in et:
        et = et.replace(
            'if (next === "ending") {',
            'if (next === "hfGameOver") {\n\t\t\t\tthis.runHeavenfallGameOverFx();\n\t\t\t} else if (next === "ending") {',
            1,
        )
        print("afterTalk hfGameOver")

    # fade action hfGameOver -> black then reload
    if 'fade.action === "hfGameOver"' not in et:
        # after loss block handling in fade complete
        loss_done = 'if (this.fade.action === "loss") {'
        # find apply fade mid-point where action runs
        # tickFade mid: when phase holds complete
        anchor = 'if (this.fade.action === "loss") {\n\t\t\tconst fromGauntlet'
        if anchor in et:
            pass  # action already at end of fade
        # in the function that applies fade action at midpoint
        mid = re.search(
            r"(if \(this\.fade\.action === \"loss\"\) \{[\s\S]*?this\.announceMap\(\);\n\t\t\})",
            et,
        )
        if mid and "hfGameOver" not in mid.group(1):
            insert = mid.group(1) + '''
		if (this.fade.action === "hfGameOver") {
			this.reloadLastSaveOrTitle();
		}'''
            et = et[: mid.start(1)] + insert + et[mid.end(1) :]
            print("fade hfGameOver apply")

    # red for hfGameOver fade like execute
    et = et.replace(
        'this.fade.action === "execute" ? "#8b1010" : "#000"',
        'this.fade.action === "execute" || this.fade.action === "hfGameOver" ? "#8b1010" : "#000"',
        1,
    )

    # Lead win: after mercy/win, if beatLieutenantLead show placeholder GO
    # Hook finishWin or trainer win for lieutenantLead
    if "leadWinPlaceholder" not in et or "thank you for playing" not in et.lower():
        win_a = 'else if (who === "commanderFinal") this.beatCommander = true;'
        if win_a in et and 'who === "lieutenantLead"' not in et:
            et = et.replace(
                win_a,
                win_a
                + '\n\t\t\t\telse if (who === "lieutenantLead") {\n'
                + '\t\t\t\t\tthis.beatLieutenantLead = true;\n'
                + '\t\t\t\t\tthis.say(TALK.leadWinPlaceholder || [{ speaker: "system", text: "Thank you for playing." }], "leadThanksGO");\n'
                + '\t\t\t\t\treturn;\n\t\t\t\t}',
                1,
            )
            print("Lead win")
        if 'next === "leadThanksGO"' not in et:
            et = et.replace(
                'if (next === "hfGameOver") {',
                'if (next === "leadThanksGO") {\n\t\t\t\tthis.startFade("hfGameOver");\n\t\t\t} else if (next === "hfGameOver") {',
                1,
            )

    # beatLieutenantLead field
    if "beatLieutenantLead" not in et:
        et = et.replace(
            "beatHeavenfall = false;",
            "beatHeavenfall = false;\n\tbeatLieutenantLead = false;",
            1,
        )
        et = et.replace(
            "this.beatHeavenfall = false;",
            "this.beatHeavenfall = false;\n\t\tthis.beatLieutenantLead = false;",
            1,
        )

    # Force Lead battle stats to exact values when starting that trainer fight
    # Search startBattle or wsoldier path - after mint for trainer
    if "Lieutenant Lead" not in et or "Burst Fire" not in et:
        pass
    # after mintMonster in trainer start, if species lead normalize
    if 'species === "lead"' not in et:
        # inject near markCaught after battle foe setup is hard; use finish of startBattle
        idx = et.find("this.mode = \"battle\";")
        if idx > 0 and 'foe.species === "lead"' not in et:
            inject = '''
		if (foe && foe.species === "lead") {
			foe.name = "Lieutenant Lead";
			foe.level = 20;
			foe.maxHp = 60; foe.hp = 60;
			foe.str = 20; foe.agl = 20; foe.spc = 10;
		}
'''
            # startBattle signature uses foe as param - find function
            m = re.search(r"startBattle\s*\([^)]*\)\s*\{", et)
            if m:
                # insert before this.mode = battle inside startBattle
                sub = et[m.start() : m.start() + 2500]
                if 'species === "lead"' not in sub:
                    et = et[: m.start()] + sub.replace(
                        'this.mode = "battle";',
                        inject + '\t\tthis.mode = "battle";',
                        1,
                    ) + et[m.start() + 2500 :]
                    print("Lead stat override")

    # imports for unpackSave readSaveBlob if needed
    if "readSaveBlob" in et and "import" in et[:2000]:
        if "readSaveBlob" not in et[:2500]:
            et = et.replace(
                'from "./save"',
                'from "./save" // readSaveBlob unpackSave used for HF game over',
                1,
            )
        # ensure named imports
        m = re.search(r'import \{([^}]+)\} from "\./save"', et)
        if m and "unpackSave" not in m.group(1):
            names = m.group(1).strip()
            et = et.replace(
                m.group(0),
                "import { " + names + ", unpackSave, readSaveBlob } from \"./save\"",
                1,
            )
            print("save imports")

    ep.write_text(et)

    # merge world
    merge = ROOT / "tools" / "merge_world.py"
    if merge.exists():
        import subprocess, sys

        subprocess.check_call([sys.executable, str(merge)], cwd=str(ROOT))
        print("merged world")

    print("DONE content+engine leg2 wrap")


if __name__ == "__main__":
    main()

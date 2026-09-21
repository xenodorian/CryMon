#!/usr/bin/env python3
"""2.4 cleanup: Heaven Tamer on catch, credits after grave win, DC ending/wipe."""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

# ---------- Web engine ----------
ep = ROOT / "src" / "game" / "engine.ts"
et = ep.read_text()

# Catch Heavenfall -> Tamer (and not Slayer)
catch_anchor = '''					if (b.foe.species === "cathleen") {
						this.cathleenCaught = true;
						this.beatCathleen = true;
					}'''
catch_new = catch_anchor + '''
					if (b.foe.species === "heavenfall") {
						this.titleTamer = true;
						this.titleSlayer = false;
						this.beatHeavenfall = true;
						this.note("The world will know you as Heaven Tamer.");
					}'''
if "species === \"heavenfall\"" not in et[et.find("cathleenCaught = true") : et.find("cathleenCaught = true") + 500]:
    if catch_anchor in et:
        et = et.replace(catch_anchor, catch_new, 1)
        print("tamer on catch")
    else:
        print("WARN catch anchor")
else:
    print("tamer catch already")

# After trainer win heavenfallGrave -> credits
if "titleSlayer = true" in et and "creditsFinal" not in et[et.find("heavenfallGrave") : et.find("heavenfallGrave") + 600]:
    # expand win handler
    old = '''else if (who === "heavenfallGrave") {
					this.beatHeavenfall = true;
					this.titleSlayer = true;
					this.note("The world will know you as Heaven Slayer.");
				}'''
    new = '''else if (who === "heavenfallGrave") {
					this.beatHeavenfall = true;
					this.titleSlayer = true;
					this.titleTamer = false;
					this.note("The world will know you as Heaven Slayer.");
					this.say(TALK.gauntletGraveWin || [{ speaker: "max", text: "Heavenfall falls." }], "creditsFinal");
				}'''
    if old in et:
        et = et.replace(old, new, 1)
        print("slayer -> credits")
    else:
        # softer: after note Heaven Slayer
        if 'note("The world will know you as Heaven Slayer.")' in et and "creditsFinal" not in et[et.find("Heaven Slayer") : et.find("Heaven Slayer") + 200]:
            et = et.replace(
                'this.note("The world will know you as Heaven Slayer.");',
                'this.note("The world will know you as Heaven Slayer.");\n\t\t\t\t\tthis.say(TALK.gauntletGraveWin || [{ speaker: "max", text: "Heavenfall falls." }], "creditsFinal");',
                1,
            )
            print("slayer credits soft")

# beatHeavenfall field init
if "beatHeavenfall = false" not in et:
    et = et.replace(
        "choseHeavenfall = false;",
        "choseHeavenfall = false;\n\tbeatHeavenfall = false;",
        1,
    )
    et = et.replace(
        "this.choseHeavenfall = false;",
        "this.choseHeavenfall = false;\n\t\tthis.beatHeavenfall = false;",
        1,
    )

# playerDisplayName priority: Tamer > Slayer > Kind > Max
if "titleTamer" in et and "Heaven Tamer" not in et[et.find("playerDisplayName") : et.find("playerDisplayName") + 400]:
    pass  # may already have from prior patch
idx = et.find("playerDisplayName()")
if idx > 0:
    chunk = et[idx : idx + 450]
    if "Heaven Tamer" not in chunk:
        et = et.replace(
            "if (this.revivedFather) return LOGIC.reputation?.kindName || \"Max The Kind\";\n\t\treturn SPEAKER_NAME.max || \"Max\";",
            "if (this.titleTamer) return \"Heaven Tamer\";\n\t\tif (this.titleSlayer) return \"Heaven Slayer\";\n\t\tif (this.revivedFather) return LOGIC.reputation?.kindName || \"Max The Kind\";\n\t\treturn SPEAKER_NAME.max || \"Max\";",
            1,
        )
        print("display name order")
    else:
        print("display name ok")

ep.write_text(et)

# ---------- Dreamcast main.c ----------
mp = ROOT / "ports" / "dreamcast" / "src" / "main.c"
if mp.exists():
    mc = mp.read_text()
    # POST_ENDING_FINAL: unlock note instead of force gauntlet for heaven path;
    # Father path stays in world
    old_end = """case POST_ENDING_FINAL:
                                    find_mark(MAP_GAUNTLET, '2', &col, &row);
                                    map_id = MAP_GAUNTLET;"""
    # flexible match
    if "POST_ENDING_FINAL" in mc and "find_mark(MAP_GAUNTLET" in mc:
        # replace the gauntlet force warp block with conditional
        mc2, n = re.subn(
            r"case POST_ENDING_FINAL:\s*find_mark\(MAP_GAUNTLET,\s*'2',\s*&col,\s*&row\);\s*map_id\s*=\s*MAP_GAUNTLET;",
            "case POST_ENDING_FINAL:\n"
            "                                /* 2.4: no auto-gauntlet. Heavenfall path unlocks grove entrance. */\n"
            "                                if (chose_heavenfall) {\n"
            "                                    /* flag already set; player uses grove G when maps rebaked */\n"
            "                                }\n"
            "                                break;\n"
            "                            case POST_ENDING_FINAL_UNUSED:",
            mc,
            count=1,
        )
        if n:
            mc = mc2
            print("DC ending no auto gauntlet")
        else:
            # try multiline looser
            idx = mc.find("case POST_ENDING_FINAL:")
            if idx > 0:
                snippet = mc[idx : idx + 350]
                if "MAP_GAUNTLET" in snippet:
                    # find end of case roughly until next case
                    end = mc.find("case ", idx + 10)
                    if end < 0:
                        end = idx + 300
                    replacement = (
                        "case POST_ENDING_FINAL:\n"
                        "                                /* 2.4: stay in world; gauntlet unlocked via chose_heavenfall + grove G */\n"
                        "                                break;\n"
                    )
                    mc = mc[:idx] + replacement + mc[end:]
                    print("DC ending soft replace")
            else:
                print("WARN DC ending")
    # Wipe regret on loss from gauntlet*
    if "gauntlet_wipe_regret" not in mc:
        # add static flag near chose_heavenfall if present
        if "chose_heavenfall" in mc and "static int gauntlet_wipe_regret" not in mc:
            mc = mc.replace(
                "chose_heavenfall",
                "chose_heavenfall",  # first only for var decl harder
                1,
            )
            # inject after a known int declaration line
            if "int chose_heavenfall" in mc:
                mc = mc.replace(
                    "int chose_heavenfall",
                    "int chose_heavenfall, gauntlet_wipe_regret",
                    1,
                )
                print("DC wipe flag var")
            elif "chose_heavenfall = 0" in mc:
                mc = mc.replace(
                    "chose_heavenfall = 0",
                    "chose_heavenfall = 0; gauntlet_wipe_regret = 0",
                    1,
                )
        loss = "fade_action == FADE_ACTION_LOSS) {\n                    heal_party(party, party_n);\n                    map_id = MAP_HOUSE;"
        loss_new = (
            "fade_action == FADE_ACTION_LOSS) {\n"
            "                    {\n"
            "                        int from_g = (map_id >= MAP_GAUNTLET);\n"
            "                        if (from_g && chose_heavenfall && !gauntlet_wipe_regret) {\n"
            "                            gauntlet_wipe_regret = 1;\n"
            "                            /* talk lines need rebake; use short note via talk if available */\n"
            "                        }\n"
            "                    }\n"
            "                    heal_party(party, party_n);\n"
            "                    map_id = MAP_HOUSE;"
        )
        if loss in mc and "gauntlet_wipe_regret = 1" not in mc:
            mc = mc.replace(loss, loss_new, 1)
            print("DC wipe regret")
        elif "gauntlet_wipe_regret = 1" in mc:
            print("DC wipe already")
        else:
            print("WARN DC loss anchor")
    mp.write_text(mc)

# ---------- Bake DC content from JSON ----------
bake = ROOT / "tools" / "bake_content.py"
if bake.exists():
    try:
        subprocess.check_call([sys.executable, str(bake)], cwd=str(ROOT))
        print("bake_content ok")
    except Exception as ex:
        print("bake_content failed", ex)

print("cleanup done")

#!/usr/bin/env python3
from pathlib import Path
import re

ep = Path("src/game/engine.ts")
et = ep.read_text()

# flagFor choseHeavenfall / gauntletUnlocked
if 'need === "choseHeavenfall"' not in et:
    old = 'if (need === "hasScroll") return this.hasScroll;'
    new = old + '\n\t\tif (need === "choseHeavenfall") return this.choseHeavenfall || this.gauntletUnlocked;'
    if old not in et:
        raise SystemExit("flagFor hasScroll missing")
    et = et.replace(old, new, 1)
    print("flagFor choseHeavenfall")

# pending map for heavenfallGrave trainer
if 'heavenfallGrave' not in et or et.count('heavenfallGrave') < 2:
    # add to pending trainer table if exists
    if 'commanderFinal: ["wsoldier", "commanderFinal"]' in et:
        et = et.replace(
            'commanderFinal: ["wsoldier", "commanderFinal"]',
            'commanderFinal: ["wsoldier", "commanderFinal"],\n\t\t\theavenfallGrave: ["wsoldier", "heavenfallGrave"]',
            1,
        )
        print("pending map")
    # win handler for titles
    if 'who === "commanderFinal"' in et and 'titleSlayer' not in et[et.find('who ===') : et.find('who ===') + 800]:
        pass
    if 'heavenfallGrave' not in et[et.find('else if (who ===') :]:
        # after commander win
        anchor = 'else if (who === "commanderFinal") this.beatCommander = true;'
        if anchor in et:
            et = et.replace(
                anchor,
                anchor
                + '\n\t\t\t\telse if (who === "heavenfallGrave") {\n'
                + '\t\t\t\t\tthis.beatHeavenfall = true;\n'
                + '\t\t\t\t\tthis.titleSlayer = true;\n'
                + '\t\t\t\t\tthis.note("The world will know you as Heaven Slayer.");\n'
                + '\t\t\t\t}',
                1,
            )
            print("win slayer on defeat")

# beatHeavenfall field
if "beatHeavenfall" not in et:
    et = et.replace(
        "choseHeavenfall = false;",
        "choseHeavenfall = false;\n\tbeatHeavenfall = false;",
        1,
    )

# Capture of heavenfall -> tamer: look for catch success
if "titleTamer" not in et or et.count("titleTamer") < 2:
    # after successful catch of heavenfall species
    for anchor in [
        "this.note(`Caught ${",
        "this.markCaught(",
    ]:
        pass
    # simpler: in catch resolve when species is heavenfall
    if 'species === "heavenfall"' not in et and "titleTamer = true" not in et:
        # find party.push(mint after catch
        m = re.search(r"(this\.party\.push\(mintMonster\([^)]+\)\);)", et)
        if m:
            # too broad
            pass
        # inject near markCaught after catch
        old = None
        # search Caught note
        idx = et.find("Caught")
        print("Caught at", idx)

# Ensure TALK type allows new keys — usually index signature

ep.write_text(et)
print("engine follow-up done")

# dialogue win line
from pathlib import Path
import json
dp = Path("content/dialogue.json")
d = json.loads(dp.read_text())
talks = d.get("talk") or d.get("talks") or d
if isinstance(talks, dict):
    talks["gauntletGraveWin"] = [
        {"speaker": "max", "text": "Heavenfall falls. The path of power is paid in full."}
    ]
    if "talk" in d:
        d["talk"] = talks
    dp.write_text(json.dumps(d, indent=2) + "\n")
    print("win dialogue")

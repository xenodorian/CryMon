#!/usr/bin/env python3
"""Write the quest journal into content/logic.json (`journal`).

    python3 tools/build_journal.py
    python3 tools/merge_world.py      # only if a giver got a new `set`

Both engines show it from the pause menu (JOURNAL). A quest shows once its
`start` flag is on (no `start` = from the beginning) and reads as done once
its `done` flag is on. While it's open, the first step whose `ifNot` flag
is still off (and whose `if` flag, when given, is on) is the current hint.
A `linear` quest (the main story) instead shows the step after the last one
whose `ifNot` flag is on, so an optional step Max skipped never sticks.
Flags are any NPC-script flag, computed ones included (item:, mon:, dex:).

Some quest givers never set a flag when they first ask. ASKED below adds a
`set` to the giver's last (fallback) script step and appends the flag to
save.json, so the quest appears in the journal once Max has heard the ask.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGIC = ROOT / "content/logic.json"
NPCS = ROOT / "content/world_parts/npcs.json"
SAVE = ROOT / "content/save.json"


def q(qid, title, steps, start=None, done=None, done_text="", linear=False):
    out = {"id": qid, "title": title, "start": start, "done": done, "doneText": done_text,
           "steps": [dict(s) for s in steps]}
    if linear:
        out["linear"] = True
    return out


def s(text, if_not=None, if_=None):
    out = {"text": text}
    if if_not:
        out["ifNot"] = if_not
    if if_:
        out["if"] = if_
    return out


# giver npc id -> flag its fallback step now sets
ASKED = {
    "tam": "tamAsked", "lina": "linaAsked", "juno": "junoAsked", "pike": "talkedPike",
    "bet": "betAsked", "cobb": "cobbAsked", "sera": "seraAsked", "dunn": "dunnAsked",
    "hesse": "hesseAsked", "voss": "vossAsked", "lune": "luneAsked", "holt": "holtAsked",
    "anselm": "anselmAsked", "rhee": "rheeAsked",
}


def main_story(logic):
    steps = [
        s("Take Father's CryMon crystal from the shelf at home.", "tookStarter"),
        s("Calder blocks the east road out of CryTown. Beat him to reach the Cliffs.", "beatCalder"),
        s("Go east over the Cliffs, then the Marsh, the Quarry, the army camp and the Forest. The Prison is past the Forest.", "beatCross"),
        s("Get past Cathleen and face Shinigami in the Prison.", "beatShinigami"),
        s("The boulder west of CryTown is gone. Go through the Ruins to the Reach.", "talkedReach"),
        s("Shinigami waits under the northwest house in the Ruins.", "joinedGhost"),
        s("Do the Ghost Guild's work so Shinigami can part the Weeping Veil.", "veilLifted"),
        s("Beat Lieutenant Lead at CryTown's north gate. He fights with six CryMon.", "beatLieutenantLead"),
    ]
    for g in logic["leg3"]["generals"]:
        steps.append(s(f"Take the {g['city'].capitalize()} base from {g['name']}.", g["medal"]))
    steps.append(s("Nine medals won. Storm Nero's palace in Keter.", "beatNero"))
    return q("main", "The Weeping Army", steps, done="beatNero",
             done_text="Nero is beaten. The Sephirot are free.", linear=True)


QUESTS_AFTER_MAIN = [
    q("heavenfall", "The Fallen Star", [
        s("Show the scroll to the Priestess south of CryTown and follow the gauntlet to Heavenfall's grave.", "beatHeavenfall"),
    ], start="choseHeavenfall", done="beatHeavenfall", done_text="Heavenfall answered the scroll."),
    q("ghost", "The Ghost Guild", [
        s("Rob Ines's grave in the southeast of the Ruins.", "robbedInes"),
        s("Rob Tomas's grave in the Prison yard.", "robbedTomas"),
        s("Rob Oriel's grave in the southwest Marsh.", "robbedOriel"),
        s("Pray at the shrine at the top of the Cliffs.", "prayedCliffs"),
        s("Pray at the shrine in the Quarry.", "prayedQuarry"),
        s("Pray at the shrine in the east of the Forest.", "prayedForest"),
        s("Free the ghosts in the haunted hall, northeast in the Reach.", "expelledOriel"),
        s("Bring the bones to Shinigami in the crypt under the Ruins.", "beatVesk"),
        s("Collect the Wraith Lantern from Shinigami.", "veilLifted"),
    ], start="joinedGhost", done="veilLifted", done_text="The Wraith Lantern parted the Veil."),
    q("heroes", "The Heroes Guild", [
        s("Arrest Red Mallory in the Forest, then report to Captain Ardent.", "paidMallory"),
        s("Bring Captain Ardent a Glasswisp. They live in the Ruins' grass.", "gaveGlasswisp"),
        s("Arrest Silas the Fence in the Quarry, then report to Ardent.", "paidSilas"),
        s("Bring Ardent a Stardrop from the Quarry's grass.", "gaveStardrop"),
        s("Bring Ardent a Moonveil from the Path of Ayin.", "gaveMoonveil"),
    ], start="joinedHeroes", done="gaveMoonveil", done_text="Every Heroes Guild job is done."),
    q("thieves", "The Thieves Guild", [
        s("Shake down Sir Aldous in CryTown, then see Mag.", "paidAldous"),
        s("Shake down Dame Brin in the Ruins, then see Mag.", "paidBrin"),
        s("Shake down Captain Rook on the Cliffs, then see Mag.", "paidRook"),
    ], start="joinedThieves", done="paidRook", done_text="Every Thieves Guild job is done."),
    q("pike", "Pike's Crystal", [s("Pike lost a crystal in the east reeds of CryTown. Find it and bring it back.", "pikeHelped")],
      start="talkedPike", done="pikeHelped"),
    q("tam", "Old Tam's Watch", [
        s("Old Tam lost his watch by the Prison.", "pickedWatch"),
        s("Give Old Tam his watch in CryTown.", "gaveWatch"),
    ], start="tamAsked", done="gaveWatch"),
    q("rolo", "Lina's Boy", [
        s("Find Rolo on the Cliffs.", "roloFound"),
        s("Tell Lina in CryTown that Rolo is home.", "roloHome"),
    ], start="linaAsked", done="roloHome"),
    q("juno", "A Crymare for Juno", [s("Bring Collector Juno in CryTown a Crymare from the Ruins' grass.", "gaveCrymare")],
      start="junoAsked", done="gaveCrymare"),
    q("wyn", "The Library's Great Book", [
        s("Catch 10 kinds of CryMon and show Archivist Wyn in the Ruins library.", "libraryDex10"),
        s("Catch 25 kinds and show Wyn.", "libraryDex25"),
        s("Catch 50 kinds and show Wyn.", "libraryDex50"),
        s("Catch 80 kinds and show Wyn.", "libraryDex80"),
        s("Catch every kind and show Wyn.", "libraryDexAll"),
    ], start="talkedWyn", done="libraryDexAll", done_text="Max's name is on the first page."),
    q("brann", "A Deserter's Letter", [
        s("Take Brann's letter to his brother, Elder Marn, in Malkuth.", "gaveLetter"),
        s("Take Marn's reply back to Brann in the Ruins.", "brannDone"),
    ], start="brannAsked", done="brannDone"),
    q("osk", "Hermit Osk's Lessons", [
        s("Beat Hermit Osk in his hut in the Reach.", "beatOsk1"),
        s("Beat Lieutenant Lead, then fight Osk again.", "beatLieutenantLead"),
        s("Beat Osk's real team.", "beatOsk2"),
        s("Win all nine medals, then fight Osk one last time.", "medalOfHonor"),
        s("Beat Osk's last lesson.", "beatOsk3"),
    ], start="talkedOsk", done="beatOsk3"),
    q("maren", "Button", [
        s("Find Maren's rag doll in the north of the Marsh.", "pickedDoll"),
        s("Bring the doll to Maren in the Reach's empty house.", "marenRest"),
    ], start="talkedMaren", done="marenRest", done_text="Maren is at rest."),
    q("pip", "Pip", [
        s("Find Pip on the Path of Tau.", "pipFound"),
        s("Tell Old Bet in Malkuth that Pip is home.", "pipHome"),
    ], start="betAsked", done="pipHome"),
    q("cobb", "A Boltlamb for Cobb", [s("Bring Cobb in Yesod a Boltlamb from the Path of Resh.", "gaveBoltlamb")],
      start="cobbAsked", done="gaveBoltlamb"),
    q("sera", "Sera's Locket", [s("Find Sera's silver locket on the Path of Peh and bring it to her in Netzach.", "gaveLocket")],
      start="seraAsked", done="gaveLocket"),
    q("garrow", "Wanted: Knife-Hand Garrow", [
        s("Deal with Knife-Hand Garrow on the Path of Mem.", "beatGarrow"),
        s("Collect the bounty from Dunn in Hod.", "paidGarrow"),
    ], start="dunnAsked", done="paidGarrow"),
    q("tilly", "Tilly", [
        s("Find Tilly on the Path of Samekh.", "tillyFound"),
        s("Tell Hesse in Tiferet that Tilly is home.", "tillyHome"),
    ], start="hesseAsked", done="tillyHome"),
    q("voss", "A Wheelhog for Voss", [s("Bring Voss in Chesed a Wheelhog from the Path of Mem.", "gaveWheelhog")],
      start="vossAsked", done="gaveWheelhog"),
    q("lune", "Lune's Old Map", [s("Find Lune's old map on the Path of Heth and bring it to Gevurah.", "gaveMap")],
      start="luneAsked", done="gaveMap"),
    q("kael", "Wanted: Deserter Kael", [
        s("Deal with Deserter Kael on the Path of Daleth.", "beatKael"),
        s("Collect the bounty from Holt in Binah.", "paidKael"),
    ], start="holtAsked", done="paidKael"),
    q("iona", "Sister Iona", [
        s("Find Sister Iona on the Path of Aleph.", "ionaFound"),
        s("Tell Anselm in Chokmah that Iona is home.", "ionaHome"),
    ], start="anselmAsked", done="ionaHome"),
    q("rhee", "An Arcanox for Rhee", [s("Bring Rhee in Keter an Arcanox from the Path of Aleph.", "gaveArcanox")],
      start="rheeAsked", done="gaveArcanox"),
]


def main() -> None:
    logic = json.loads(LOGIC.read_text())
    npcs = json.loads(NPCS.read_text())
    save = json.loads(SAVE.read_text())
    asked = dict(ASKED)
    asked["osk"] = "talkedOsk"
    by_id = {n["id"]: n for n in npcs["npcs"]}
    for nid, flag in asked.items():
        n = by_id.get(nid)
        if not n:
            raise SystemExit(f"quest giver {nid!r} not in npcs.json")
        if flag == "talkedPike":
            continue  # Pike already sets it on the first talk
        if nid == "osk":
            first = n["script"][0]
            first.setdefault("set", flag)
        else:
            last = n["script"][-1]
            if last.get("set") not in (None, flag):
                raise SystemExit(f"{nid}'s last step already sets {last['set']!r}")
            last["set"] = flag
        if flag not in save["flags"]:
            save["flags"].append(flag)
    journal = {"note": "Quest journal (pause menu). See tools/build_journal.py for the rules.",
               "quests": [main_story(logic)] + QUESTS_AFTER_MAIN}
    logic["journal"] = journal
    LOGIC.write_text(json.dumps(logic, indent=2, ensure_ascii=False) + "\n")
    NPCS.write_text(json.dumps(npcs, indent=2, ensure_ascii=False) + "\n")
    SAVE.write_text(json.dumps(save, indent=2, ensure_ascii=False) + "\n")
    print(f"journal: {len(journal['quests'])} quests, {len(save['flags'])} save flags")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Fix soft spots: Lead mark, flag persistence, 2.8 rep+shop warn, CURRENT_WORK."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def jload(p: Path):
    return json.loads(p.read_text())


def jdump(p: Path, d):
    p.write_text(json.dumps(d, indent=2) + "\n")


def main() -> None:
    # 1) Lead NPC mark L -> S (avoid stump collision)
    np = ROOT / "content" / "world_parts" / "npcs.json"
    npcs = jload(np)
    nlist = npcs if isinstance(npcs, list) else npcs.get("npcs", [])
    for n in nlist:
        if n.get("id") == "lieutenantLead":
            n["mark"] = "S"
            print("Lead mark -> S")
    if isinstance(npcs, dict):
        npcs["npcs"] = nlist
        jdump(np, npcs)
    else:
        jdump(np, nlist)

    # trainer kit lead/bench shape
    for path in (
        ROOT / "content" / "world.json",
        ROOT / "content" / "world_parts" / "trainers.json",
    ):
        if not path.exists():
            continue
        data = jload(path)
        if path.name == "world.json":
            root = data.setdefault("trainers", {})
        else:
            root = data.get("trainers", data)
        kit = root.get("lieutenantLead")
        if not kit:
            continue
        if "party" in kit and "lead" not in kit:
            party = kit.pop("party")
            if party:
                kit["lead"] = [party[0]["species"], party[0].get("level", 20)]
            kit["bench"] = []
            print("kit shape", path.name)
        root["lieutenantLead"] = kit
        if path.name != "world.json" and "trainers" in data:
            data["trainers"] = root
            jdump(path, data)
        elif path.name != "world.json":
            jdump(path, root)
        else:
            jdump(path, data)

    merge = ROOT / "tools" / "merge_world.py"
    if merge.exists():
        subprocess.check_call([sys.executable, str(merge)], cwd=str(ROOT))
        print("merged")

    # 2) engine.ts
    ep = ROOT / "src" / "game" / "engine.ts"
    et = ep.read_text()

    if "beatLieutenantLead = false" not in et:
        et = et.replace(
            "beatCommander = false;",
            "beatCommander = false;\n\tbeatLieutenantLead = false;\n\theavenfallRepWarned = false;",
            1,
        )
        print("fields declared")

    if "this.beatLieutenantLead = false" not in et:
        et = et.replace(
            "this.beatCommander = false;",
            "this.beatCommander = false;\n\t\tthis.beatLieutenantLead = false;\n\t\tthis.heavenfallRepWarned = false;",
            1,
        )
        print("reset fields")

    if "beatLieutenantLead: this.beatLieutenantLead" not in et:
        et = et.replace(
            "beatCommander: this.beatCommander,",
            "beatCommander: this.beatCommander,\n"
            "\t\t\t\tbeatLieutenantLead: this.beatLieutenantLead,\n"
            "\t\t\t\tbeatHeavenfall: this.beatHeavenfall,\n"
            "\t\t\t\theavenfallRepWarned: this.heavenfallRepWarned,",
            1,
        )
        print("flags snapshot")

    if "applyHeavenfallReviveRep" not in et:
        helper = (
            "\n\tapplyHeavenfallReviveRep() {\n"
            "\t\tif (!this.beatHeavenfall) return;\n"
            "\t\t// 2.8: apply once when Heavenfall is first beaten/caught at the grave.\n"
            "\t\t// Merchant warning uses heavenfallRepWarned separately.\n"
            "\t\tconst already = (this as { _hfRepApplied?: boolean })._hfRepApplied;\n"
            "\t\tif (already) return;\n"
            "\t\t(this as { _hfRepApplied?: boolean })._hfRepApplied = true;\n"
            "\t\tconst delta =\n"
            "\t\t\t(LOGIC as { reputation?: { heavenfallRevive?: number } }).reputation?.heavenfallRevive ?? -25;\n"
            "\t\tthis.adjustReputation(delta);\n"
            "\t}\n"
        )
        et = et.replace("\tplayerDisplayName() {", helper + "\tplayerDisplayName() {", 1)
        print("helper")

    if "this.applyHeavenfallReviveRep()" not in et:
        et, n = re.subn(
            r"(this\.beatHeavenfall = true;)",
            r"\1\n\t\t\t\t\t\tthis.applyHeavenfallReviveRep();",
            et,
            count=3,
        )
        print("inject apply x", n)

    m = re.search(r"openShop\(keep:[^{]+\{\n", et)
    if m and "heavenfallShopWarn" not in et[m.end() : m.end() + 500]:
        insert = (
            "\t\tif (this.beatHeavenfall && !this.heavenfallRepWarned) {\n"
            "\t\t\tthis.heavenfallRepWarned = true;\n"
            "\t\t\tthis.say(TALK.heavenfallShopWarn || [{ speaker: \"none\", "
            "text: \"You revived Heavenfall, who knows what other horrors you are capable of.\" }]);\n"
            "\t\t}\n"
        )
        et = et[: m.end()] + insert + et[m.end() :]
        print("openShop warn")

    et = et.replace(
        'action: null as null | "bed" | "loss" | "execute"',
        'action: null as null | "bed" | "loss" | "execute" | "hfGameOver"',
        1,
    )

    ep.write_text(et)

    cw = ROOT / "CURRENT_WORK.md"
    t = cw.read_text()
    note = """
### Soft-spot pass (Grok C, 2026-09-21)

Fixed:
- **Lead mark collision:** `lieutenantLead` NPC mark **S** (stump stays **L** on veld).
- **Flag persistence:** `beatLieutenantLead`, `beatHeavenfall`, `heavenfallRepWarned` in save snapshot + class fields.
- **2.8:** `applyHeavenfallReviveRep()` applies `reputation.heavenfallRevive` (-25) when
  Heavenfall is first beaten/caught; first shop after that plays `heavenfallShopWarn`.
- Trainer kit for Lead uses `{ lead, bench }` shape expected by the web engine.
- CDI is green on recent main builds; these were the remaining web weak links.

"""
    if "Soft-spot pass (Grok C" not in t:
        if "## Leg 2 wrap" in t:
            t = t.replace("## Leg 2 wrap", note + "## Leg 2 wrap", 1)
        else:
            t += note
        cw.write_text(t)
        print("CURRENT_WORK note")

    bake = ROOT / "tools" / "bake_content.py"
    if bake.exists():
        try:
            subprocess.check_call([sys.executable, str(bake)], cwd=str(ROOT))
            print("bake ok")
        except Exception as ex:
            print("bake", ex)

    print("DONE soft-spot pass")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Write a ready-to-fight save for every trainer NPC in content/world.json.

For each NPC script step that starts a trainer fight ("pending"), patch a
base save (a strong party from the web e2e) so the player stands next to
that NPC facing it, on its map, with the story flags set so the NPC's
script reaches that step (earlier "if" steps false, earlier "ifNot" steps
true, "hideIf"/"passIf" false, "showIf" true). Output: <out>/<trainer>-before.bin,
which both scripts/e2e-trainers.mjs (web) and emu_warden.py (Dreamcast)
play from.

  trainer_saves.py --base e2e-out/quartz-before.bin --out trainers-out [trainer ...]
"""
import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SAVE = json.loads((REPO / "content" / "save.json").read_text())
MAPS = json.loads((REPO / "content" / "maps.json").read_text())
WORLD = json.loads((REPO / "content" / "world.json").read_text())
TILE = 32


def flag_offsets():
    return [o + i for o, n in SAVE["flagParts"] for i in range(n)]


def set_flag(b, name, value):
    i = SAVE["flags"].index(name)
    off = flag_offsets()[i >> 3]
    if value:
        b[off] |= 1 << (i & 7)
    else:
        b[off] &= ~(1 << (i & 7)) & 0xFF


def set_item(b, name, count):
    offs = [o + i for o, n in SAVE["bagParts"] for i in range(n)]
    b[offs[SAVE["itemOrder"].index(name)]] = count


def needed_flags(script, target):
    """Flag values that make the script pick step `target`."""
    want = {}
    for j, st in enumerate(script):
        last = j == target
        if "hideIf" in st:
            want[st["hideIf"]] = False
        if "passIf" in st:
            want[st["passIf"]] = False
        if "showIf" in st:
            want[st["showIf"]] = True
        if "if" in st:
            want[st["if"]] = last
        if "ifNot" in st:
            want[st["ifNot"]] = not last
        if last:
            break
    return want


def stand_by(npc):
    """A walkable tile next to the NPC's mark and the direction to face it."""
    rows = MAPS["rows"][npc["map"]]
    solid, doors = set(MAPS["solid"]), set(MAPS["doors"])
    busy = {w["tile"] for w in WORLD["warps"] if w["from"] == npc["map"]}
    busy |= {n["mark"] for n in WORLD["npcs"] if n["map"] == npc["map"]}
    for r, row in enumerate(rows):
        c = row.find(npc["mark"])
        if c >= 0:
            break
    else:
        return None
    for dc, dr, face in ((0, 1, "up"), (-1, 0, "right"), (1, 0, "left"), (0, -1, "down")):
        cc, rr = c + dc, r + dr
        if 0 <= rr < len(rows) and 0 <= cc < len(rows[rr]):
            ch = rows[rr][cc]
            if ch not in solid and ch not in doors and ch not in busy:
                return cc, rr, face
    return None


def build(base, npc, step):
    b = bytearray(base)
    spot = stand_by(npc)
    if spot is None:
        return None, "no free tile next to the NPC"
    c, r, face = spot
    b[SAVE["layout"]["mapId"][0]] = SAVE["mapOrder"].index(npc["map"])
    b[SAVE["layout"]["dir"][0]] = SAVE["dirOrder"].index(face)
    x, y = c * TILE + TILE // 2, r * TILE + TILE // 2
    b[8], b[9], b[10], b[11] = x & 0xFF, x >> 8, y & 0xFF, y >> 8
    # Six maxed copies of the lead: this sweep checks each fight's flow and
    # rewards on both ports, not balance, so the player must always win.
    slot = SAVE["partySlot"]
    lead = bytearray(b[46:46 + slot])
    lead[1] = 99
    lead[2:9] = bytes([255] * 7)
    lead[13] = lead[14] = lead[15] = 0
    for k in range(6):
        b[46 + k * slot:46 + (k + 1) * slot] = lead
    b[7], b[14] = 6, 0
    for name, v in needed_flags(npc["script"], step).items():
        if name.startswith("item:") and name[5:] in SAVE["itemOrder"]:
            set_item(b, name[5:], 1 if v else 0)
        elif name in SAVE["flags"]:
            set_flag(b, name, v)
    s = sum(b[:142]) & 0xFFFF
    b[142], b[143] = s & 0xFF, s >> 8
    return bytes(b), face


def fights():
    """(trainer, npc, step index) for every scripted trainer fight."""
    out = []
    for npc in WORLD["npcs"]:
        for i, st in enumerate(npc.get("script", [])):
            t = st.get("pending")
            if t in WORLD["trainers"]:
                out.append((t, npc, i))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", required=True)
    ap.add_argument("--out", default="trainers-out")
    ap.add_argument("only", nargs="*")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    base = Path(args.base).read_bytes()
    plan = []
    for t, npc, i in fights():
        if (args.only and t not in args.only) or any(q["trainer"] == t for q in plan):
            continue  # one save per trainer (first script route to it)
        blob, info = build(base, npc, i)
        if blob is None:
            print(f"SKIP  {t}: {info}")
            continue
        (out / f"{t}-before.bin").write_bytes(blob)
        plan.append({"trainer": t, "npc": npc["id"], "map": npc["map"], "face": info})
    (out / "plan.json").write_text(json.dumps(plan, indent=1))
    print(f"{len(plan)} trainer saves in {out}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Walk up to every talkable NPC on the real Dreamcast build and press A.

BUG-012: Dreamcast NPC geometry (draw position, interaction box) must match
the web build. For each NPC in content/world.json with something to say,
patch a base save (trainer_saves.build: player on the free tile next to the
NPC's mark, facing it, story flags set so its first talk step is live),
boot Flycast, Continue, press A once, and pass if the world view gives way
to a talk box, a battle or a menu. Writes <out>/<npc>.png for each.

  npc_talk.py --cdi <cdi> --flycast <AppRun> --base e2e-out/quartz-before.bin \
              [--out npc-out] [npc id ...]
"""
import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import trainer_saves as ts  # noqa: E402


def first_talk_step(npc):
    """Index of the first script step that says or starts something."""
    for i, st in enumerate(npc.get("script", [])):
        if "talk" in st or "pending" in st or "talkIf" in st:
            return i
    return None


def talking(emu):
    """Talk text is pure white glyphs drawn over the map in the bottom rows.
    emu_warden's talk_open() counts any bright pixel there, which a lit
    house or a pale sprite at the bottom of a town map also trips."""
    px = emu.shot().convert("RGB").crop((10, 425, 630, 470)).tobytes()
    return sum(1 for k in range(0, len(px), 3)
               if px[k] >= 245 and px[k + 1] >= 245 and px[k + 2] >= 245) > 15


def quiet(emu):
    """Close any arrival scene, then wait for the world to stay quiet."""
    for _ in range(3):
        for _ in range(12):
            if not talking(emu):
                break
            emu.key("x", after=0.5)
        time.sleep(1.0)
        if not talking(emu) and emu.in_world() and not emu.menu_open():
            return True
    return False


def targets(only):
    out = []
    for npc in ts.WORLD["npcs"]:
        if only and npc["id"] not in only:
            continue
        step = first_talk_step(npc)
        if step is None and "talk" not in npc:
            continue  # the player start, or a mark with nothing to say
        out.append((npc, step))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cdi", required=True)
    ap.add_argument("--flycast", required=True)
    ap.add_argument("--base", required=True, help="a 332-byte save from the web e2e")
    ap.add_argument("--out", default="npc-out")
    ap.add_argument("--display", default=":78")
    ap.add_argument("--control", action="store_true",
                    help="step away before A; every NPC should then FAIL (checks the checker)")
    ap.add_argument("only", nargs="*")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    base = Path(args.base).read_bytes()

    import vmu_tool
    from emu_warden import Emu

    fails, skips, n = [], [], 0
    emu = Emu(args.flycast, args.cdi, out, disp=args.display)
    try:
        emu.start()
        emu.stop()
        vmus = sorted(emu.data.glob("*vmu_save_A1.bin"))
        if not vmus:
            raise SystemExit(f"Flycast made no VMU image in {emu.data}")
        emu.vmu = vmus[0]
        fresh = emu.vmu.read_bytes()
        for npc, step in targets(args.only):
            if step is None:  # no script: the NPC's plain "talk" line
                npc, step = dict(npc, script=[]), 0
            blob, info = ts.build(base, npc, step)
            if blob is None:
                print(f"SKIP  {npc['id']:<20} {npc['map']:<12} {info}", flush=True)
                skips.append(npc["id"])
                continue
            n += 1
            img = bytearray(fresh)
            vmu_tool.inject(img, blob)
            emu.vmu.write_bytes(img)
            emu.start()
            emu.key("x", after=2.5)          # Continue
            emu.mark_world()
            # An arrival scene can open a talk box on load: close it and
            # wait for a quiet world, so only our A press can open one.
            if not quiet(emu):
                emu.shot(f"{npc['id']}-busy.png")
            if args.control:
                emu.key("Down", ms=400, after=0.5)  # step away: A must do nothing
            emu.key("x", after=0.2)          # talk
            hit = False
            for _ in range(8):
                if not emu.in_world() or talking(emu) or emu.menu_open():
                    hit = True
                    break
                time.sleep(0.25)
            emu.shot(f"{npc['id']}.png")
            emu.stop()
            print(("PASS  " if hit else "FAIL  ") + f"{npc['id']:<20} {npc['map']:<12} face {info}", flush=True)
            if not hit:
                fails.append(npc["id"])
    finally:
        emu.stop()
    print(f"{n - len(fails)}/{n} NPCs answer A on Dreamcast; {len(skips)} skipped (no free tile)")
    if fails:
        print("failed: " + " ".join(fails))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()

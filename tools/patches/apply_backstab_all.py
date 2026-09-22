#!/usr/bin/env python3
"""Expand backstab to all fightable NPCs not on warp gates."""
from pathlib import Path
import re

ep = Path("src/game/engine.ts")
et = ep.read_text()
if "npcOnWarpGate" not in et:
    old = """\tcanBackstab(npc, step) {
\t\tif (!(this.bag.bowieKnife > 0)) return false;
\t\tif (!step || step.after !== \"wsoldier\") return false;
\t\tif (!this.roamableNpc(npc)) return false;
\t\tif (this.npcIsExecuted(npc.id)) return false;
\t\tconst r = this.ensureRoamer(npc);
\t\tif (r.chase) return false;
\t\tif (this.roamerLos(r.x, r.y, r.dir)) return false;
\t\treturn true;
\t}
\topenBackstabChoice(npc, step) {
\t\tconst kit = TRAINERS[step.pending];
\t\tconst levels = kit ? (kit.lead?.[1] || 0) + (kit.bench || []).reduce((s, b) => s + (b[1] || 0), 0) : 1;
\t\tthis.pendingBackstab = { npc, pending: step.pending, talk: step.talk, levels };
\t\tthis.backstabCur = 0;
\t\tthis.mode = \"backstab\";
\t\tthis.audio.ui();
\t}"""
    new = Path("tools/patches/backstab-web-snippet.ts.txt").read_text()
    if old not in et:
        raise SystemExit("web canBackstab block not found")
    et = et.replace(old, new, 1)
    et = et.replace(
        "pendingBackstab: { npc: unknown; pending: string; talk: string; levels: number } | null = null;",
        "pendingBackstab: { npc: any; pending: string; after: string; talk: string; levels: number } | null = null;",
    )
    old_r = """\t\tthis.markExecuted(\"wsoldier\", pb.pending);
\t\tconst kit = TRAINERS[pb.pending];
\t\tif (kit?.grant) {
\t\t\tfor (const [iid, qty] of kit.grant) {
\t\t\t\tthis.bag[iid] = (this.bag[iid] ?? 0) + qty;
\t\t\t}
\t\t}
\t\tthis.applyWsBeatFlags(pb.pending);
\t\tif (this.roamers[pb.npc?.id]) this.roamers[pb.npc.id].chase = false;"""
    new_r = Path("tools/patches/backstab-web-resolve.txt").read_text()
    if old_r not in et:
        raise SystemExit("resolve middle not found")
    et = et.replace(old_r, new_r, 1)
    ep.write_text(et)
    print("web ok")
else:
    print("web already")

cp = Path("ports/dreamcast/src/main.c")
ct = cp.read_text()
start = ct.find("static int find_backstab_target")
if start < 0:
    raise SystemExit("no find_backstab")
m = re.search(
    r"static int find_backstab_target\(int map_id, int ppx, int ppy, int \*\*ft, int party_n\) \{.*?\n\}",
    ct[start:],
    re.S,
)
if not m:
    raise SystemExit("no match")
new_fn = Path("tools/patches/backstab-dc-find.c.txt").read_text()
pre = ct[:start]
pre = re.sub(r"\nstatic int npc_after_is_fight[\s\S]*$", "\n", pre)
pre = re.sub(r"\nstatic int npc_on_warp_gate[\s\S]*$", "\n", pre)
ct = pre + new_fn + ct[start + len(m.group(0)) :]
while ct.count("static int npc_after_is_fight") > 1:
    i = ct.find("static int npc_after_is_fight")
    j = ct.find("static int npc_after_is_fight", i + 1)
    ct = ct[:i] + ct[j:]
cp.write_text(ct)
print("dc ok")

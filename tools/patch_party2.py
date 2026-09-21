#!/usr/bin/env python3
"""Leg 2.7.3-4: Father second 6-slot party + Tab swap (web save + engine)."""
from pathlib import Path
import re

# ---------- save.json layout docs ----------
sp = Path("content/save.json")
sj = sp.read_text()
if '"party2"' not in sj:
    # Insert layout entries before closing of layout object — partyNature stays
    old = '"partyNature": 12\n  }'
    new = '"partyNature": 12,\n    "executedMask": [145, 4],\n    "party2": [149, 96],\n    "activeParty": [245, 1],\n    "party2Count": [246, 1]\n  }'
    if old not in sj:
        raise SystemExit("save.json layout anchor missing")
    sj = sj.replace(old, new, 1)
    sp.write_text(sj)
    print("save.json layout")
else:
    print("save.json already has party2")

# ---------- save.ts pack/unpack ----------
tp = Path("src/game/save.ts")
ts = tp.read_text()

if "snap.party2" in ts and "buf[245]" in ts:
    print("save.ts party2 pack already")
else:
    # After packing primary party loop, before checksum — find executedMask or checksum write
    # Insert party2 pack after main party loop ends (after nature write loop)
    pack_anchor = "\tconst m2 = buf[16];"  # this is unpack
    # Find end of pack party loop - look for checksum write
    if "/* party2 @149 */" not in ts:
        # Find: after party pack for-loop, before return or checksum
        m = re.search(
            r"(\tfor \(let p = 0; p < n; p\+\+\) \{.*?\n\t\}\n)",
            ts,
            re.S,
        )
        if not m:
            raise SystemExit("pack party loop not found")
        insert = m.group(1) + """\t{\n\t\t/* party2 @149 (96), activeParty @245, party2Count @246; executedMask @145 */\n\t\tconst p2 = snap.party2 || [];\n\t\tconst n2 = Math.min(6, p2.length);\n\t\tbuf[245] = snap.activeParty ? 1 : 0;\n\t\tbuf[246] = n2;\n\t\tif (snap.executedMask != null) {\n\t\t\tu16(buf, 145, snap.executedMask & 0xffff);\n\t\t\tu16(buf, 147, (snap.executedMask >>> 16) & 0xffff);\n\t\t}\n\t\tfor (let p = 0; p < n2; p++) {\n\t\t\tconst m = p2[p];\n\t\t\tconst o = 149 + p * SLOT;\n\t\t\tbuf[o] = Math.max(0, SAVE_SPECIES.indexOf(m.species));\n\t\t\tbuf[o + 1] = Math.max(1, Math.min(99, m.level));\n\t\t\tbuf[o + 2] = Math.max(0, Math.min(255, m.hp));\n\t\t\tbuf[o + 3] = Math.max(1, Math.min(255, m.maxHp));\n\t\t\tbuf[o + 4] = Math.max(0, Math.min(255, m.str));\n\t\t\tbuf[o + 5] = Math.max(0, Math.min(255, m.agl));\n\t\t\tbuf[o + 6] = Math.max(0, Math.min(255, m.spc));\n\t\t\tbuf[o + 7] = Math.max(0, Math.min(255, m.specialPp));\n\t\t\tbuf[o + 8] = Math.max(0, Math.min(255, m.specialPpMax));\n\t\t\tbuf[o + 9] = m.shiny ? 1 : 0;\n\t\t\tu16(buf, o + 10, Math.max(0, m.xp) & 0xffff);\n\t\t\tbuf[o + 12] = Math.max(0, Math.min(255, m.nature ?? 0));\n\t\t}\n\t}\n"""
        ts = ts[: m.start()] + insert + ts[m.end() :]
        print("save.ts pack party2")

    # unpack: before return {
    if "party2:" not in ts.split("return {")[1][:800] if "return {" in ts else True:
        pass
    unpack_insert = """\tconst party2: Monster[] = [];\n\tconst n2 = Math.min(6, buf[246] || 0);\n\tfor (let p = 0; p < n2; p++) {\n\t\tconst o = 149 + p * SLOT;\n\t\tconst species = SAVE_SPECIES[buf[o]] ?? "quillpup";\n\t\tparty2.push({\n\t\t\tid: `f${p}-${species}`,\n\t\t\tspecies,\n\t\t\tname: species[0].toUpperCase() + species.slice(1),\n\t\t\tlevel: Math.max(1, buf[o + 1]),\n\t\t\thp: buf[o + 2],\n\t\t\tmaxHp: Math.max(1, buf[o + 3]),\n\t\t\tstr: buf[o + 4],\n\t\t\tagl: buf[o + 5],\n\t\t\tspc: buf[o + 6],\n\t\t\tspecialPp: buf[o + 7],\n\t\t\tspecialPpMax: buf[o + 8],\n\t\t\tshiny: buf[o + 9] === 1,\n\t\t\txp: ru16(buf, o + 10),\n\t\t\tnature: buf[o + 12] ?? 0,\n\t\t});\n\t}\n\tconst activeParty = buf[245] ? 1 : 0;\n\tconst executedMask = buf.length >= 149 ? ru16(buf, 145) | (ru16(buf, 147) << 16) : 0;\n"""
    if "const party2: Monster[]" not in ts:
        # insert before "const m2 = buf[16];"
        if "\tconst m2 = buf[16];" not in ts:
            raise SystemExit("unpack m2 anchor missing")
        ts = ts.replace("\tconst m2 = buf[16];", unpack_insert + "\tconst m2 = buf[16];", 1)
        # add to return object
        ts = ts.replace(
            "\t\tparty,\n\t\tdexSeen:",
            "\t\tparty,\n\t\tparty2,\n\t\tactiveParty,\n\t\texecutedMask,\n\t\tdexSeen:",
            1,
        )
        print("save.ts unpack party2")
    else:
        print("save.ts unpack already")

tp.write_text(ts)

# ---------- engine.ts ----------
ep = Path("src/game/engine.ts")
e = ep.read_text()

# Ensure party2Index exists
if "party2Index" not in e:
    e = e.replace("\tactiveParty = 0;", "\tactiveParty = 0;\n\tparty2Index = 0;", 1)
    e = e.replace("\t\tthis.activeParty = 0;", "\t\tthis.activeParty = 0;\n\t\tthis.party2Index = 0;", 1)
    print("party2Index field")

# swapParties + seedFatherParty methods after adjustReputation or playerDisplayName
if "swapParties()" not in e:
    methods = r'''
	/** Swap Max <-> Father party in place so existing this.party battle code keeps working. */
	swapParties() {
		if (!this.revivedFather) {
			this.note("Father is not with you.");
			return;
		}
		const tmp = this.party;
		this.party = this.party2;
		this.party2 = tmp;
		const ti = this.partyIndex;
		this.partyIndex = this.party2Index;
		this.party2Index = ti;
		this.activeParty = this.activeParty ? 0 : 1;
		const who = this.activeParty === 1 ? "Father" : "Max";
		this.note(`${who}'s party takes the field.`);
		this.audio.ui();
	}
	seedFatherParty() {
		if (this.party2.length > 0) return;
		// Independent starter set for Father (does not touch Max's party).
		this.party2 = [
			mintMonster("mossback", 8),
			mintMonster("quillpup", 7),
		];
		for (const m of this.party2) this.markCaught(m.species);
	}
'''
    if "playerDisplayName()" not in e:
        raise SystemExit("playerDisplayName missing")
    e = e.replace(
        "\tplayerDisplayName() {",
        methods + "\tplayerDisplayName() {",
        1,
    )
    print("swap/seed methods")

# On father revive: seed party2
old_rev = """\t\t\tif (this.choiceCur === 0) {
\t\t\t\tthis.revivedFather = true;
\t\t\t\tthis.adjustReputation(LOGIC.reputation?.fatherRevive ?? 25);
\t\t\t\tthis.warpTo("house", "P", "up");
\t\t\t\tthis.say(TALK.choiceFather, "ending");"""
new_rev = """\t\t\tif (this.choiceCur === 0) {
\t\t\t\tthis.revivedFather = true;
\t\t\t\tthis.adjustReputation(LOGIC.reputation?.fatherRevive ?? 25);
\t\t\t\tthis.seedFatherParty();
\t\t\t\tthis.warpTo("house", "P", "up");
\t\t\t\tthis.say(TALK.choiceFather, "ending");"""
if "seedFatherParty()" not in e[e.find("choiceCur === 0") : e.find("choiceCur === 0") + 400]:
    if old_rev not in e:
        # softer replace
        if "this.revivedFather = true;" in e and "seedFatherParty" not in e:
            e = e.replace(
                "this.revivedFather = true;\n\t\t\t\tthis.adjustReputation",
                "this.revivedFather = true;\n\t\t\t\tthis.seedFatherParty();\n\t\t\t\tthis.adjustReputation",
                1,
            )
            print("revive seed soft")
        else:
            print("revive seed skip")
    else:
        e = e.replace(old_rev, new_rev, 1)
        print("revive seed")

# Tab / KeyQ to swap in world — inject near openBag select
if "swapParties()" in e and "pressed(\"Tab\")" not in e:
    # add to updateWorld: after select open bag
    needle = "if (this.input.select()) {\n\t\t\tthis.openBag();"
    # find first occurrence in world context - may be multiple
    if needle in e:
        e = e.replace(
            needle,
            "if (this.input.pressed(\"Tab\") || this.input.pressed(\"KeyQ\")) {\n\t\t\tthis.swapParties();\n\t\t\treturn;\n\t\t}\n\t\tif (this.input.select()) {\n\t\t\tthis.openBag();",
            1,
        )
        print("Tab swap world")
    else:
        print("world select anchor missing")

# HUD: show active party tag
if "FATHER" not in e[e.find("drawWorldHud") : e.find("drawWorldHud") + 900]:
    hud_old = 'this.text(name, 16, 12, "#e8e4d8", FONT);'
    hud_new = '''this.text(name, 16, 12, "#e8e4d8", FONT);
		if (this.revivedFather) {
			const tag = this.activeParty === 1 ? "FATHER" : "MAX";
			this.text(tag, 16 + Math.ceil(this.ctx.measureText(name).width) + 8, 12, this.activeParty === 1 ? "#c5a06a" : "#8a9eb0", FONT);
		}'''
    # only replace inside drawWorldHud once
    idx = e.find("drawWorldHud")
    sub = e[idx : idx + 1200]
    if hud_old in sub:
        sub2 = sub.replace(hud_old, hud_new, 1)
        e = e[:idx] + sub2 + e[idx + 1200 :]
        print("HUD tag")
    else:
        print("HUD anchor missing")

# snapshot already has party2/activeParty - ensure apply sets party2Index
if "this.party2Index" not in e or "snap.party2" in e:
    # after activeParty apply
    if "this.activeParty = snap.activeParty ? 1 : 0;" in e and "party2Index" in e:
        if "this.party2Index = 0" not in e[e.find("activeParty = snap") : e.find("activeParty = snap") + 200]:
            e = e.replace(
                "this.activeParty = snap.activeParty ? 1 : 0;",
                "this.activeParty = snap.activeParty ? 1 : 0;\n\t\tthis.party2Index = 0;\n\t\t// If save says Father was active, swap so this.party is the controlled set.\n\t\tif (this.activeParty === 1 && this.party2.length) {\n\t\t\tconst tmp = this.party;\n\t\t\tthis.party = this.party2;\n\t\t\tthis.party2 = tmp;\n\t\t}",
                1,
            )
            print("applySave swap if father active")

# snapshot: when saving, if Father is active, store Max in party and Father in party2
if "activeParty: this.activeParty" in e:
    old_snap = "party2: this.party2.map((m) => ({ ...m })),\n\t\t\tactiveParty: this.activeParty,"
    new_snap = "party2: (this.activeParty === 1 ? this.party : this.party2).map((m) => ({ ...m })),\n\t\t\tparty: (this.activeParty === 1 ? this.party2 : this.party).map((m) => ({ ...m })),\n\t\t\tactiveParty: this.activeParty,"
    # careful - might double party key. Read snapshot block
    if "activeParty === 1 ? this.party : this.party2" not in e:
        # replace party and party2 lines in snapshot together
        e2 = re.sub(
            r"party: this\.party\.map\(\(m\) => \(\{ \.\.\.m \}\)\),\s*party2: this\.party2\.map\(\(m\) => \(\{ \.\.\.m \}\)\),\s*activeParty: this\.activeParty,",
            "party: (this.activeParty === 1 ? this.party2 : this.party).map((m) => ({ ...m })),\n\t\t\tparty2: (this.activeParty === 1 ? this.party : this.party2).map((m) => ({ ...m })),\n\t\t\tactiveParty: this.activeParty,",
            e,
            count=1,
        )
        if e2 == e:
            print("snapshot normalize failed — manual")
        else:
            e = e2
            print("snapshot normalize")

ep.write_text(e)
print("engine done")

# ---------- controls help text in crymon-app if present ----------
ap = Path("src/components/crymon-app.tsx")
if ap.exists():
    a = ap.read_text()
    if "Tab" not in a and "Father" not in a:
        if "Back / switch CryMon" in a:
            a = a.replace(
                "Back / switch CryMon",
                "Swap Max/Father party",
                1,
            )
            # fix the line more carefully
            a = a.replace(
                '<span className="text-muted">Swap Max/Father party</span> X C Esc · 1 2 3 4 5 6',
                '<span className="text-muted">Party</span> Tab/Q swap Max↔Father · 1-6 lead · X C Esc',
                1,
            )
            ap.write_text(a)
            print("help text")
    else:
        if "Tab/Q" not in a and "switch CryMon" in a:
            a = a.replace(
                '<span className="text-muted">Back / switch CryMon</span> X C Esc · 1 2 3 4 5 6',
                '<span className="text-muted">Party</span> Tab/Q Max↔Father · 1-6 lead · X C Esc',
                1,
            )
            ap.write_text(a)
            print("help text 2")

print("DONE")

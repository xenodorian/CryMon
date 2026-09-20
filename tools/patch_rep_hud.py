#!/usr/bin/env python3
"""Add reputation readout to web + Dreamcast world HUDs."""
from pathlib import Path
import re

# --- Web engine.ts ---
ep = Path("src/game/engine.ts")
e = ep.read_text()
old = """		this.text(`Xtals ${this.bag.gem}`, statsX, 12, "#c5cec6", FONT);
		this.text(`M ${this.marks}`, statsX + 112, 12, "#8f4a40", FONT);
		this.text(lead ? `${lead.name} Lv${lead.level}  ${lead.hp}/${lead.maxHp}` : "No CryMon yet", 16, 28, "#8a8678", FONT);
		if (this.hasScroll) this.text("SCROLL", statsX + 112, 28, "#c5cec6", FONT);"""
new = """		this.text(`Xtals ${this.bag.gem}`, statsX, 12, "#c5cec6", FONT);
		this.text(`M ${this.marks}`, statsX + 112, 12, "#8f4a40", FONT);
		{
			const r = this.reputation | 0;
			const repStr = r > 0 ? `Rep +${r}` : r < 0 ? `Rep ${r}` : "Rep 0";
			const repCol = r > 0 ? "#6a9e6a" : r < 0 ? "#c05050" : "#8a8678";
			this.text(repStr, statsX + 168, 12, repCol, FONT);
		}
		this.text(lead ? `${lead.name} Lv${lead.level}  ${lead.hp}/${lead.maxHp}` : "No CryMon yet", 16, 28, "#8a8678", FONT);
		if (this.hasScroll) this.text("SCROLL", statsX + 112, 28, "#c5cec6", FONT);"""
# widen box for extra column
e2 = e.replace("const boxW = Math.max(300, statsX + 168);", "const boxW = Math.max(340, statsX + 230);")
if "Rep +" in e2 or "Rep ${" in e2 or "`Rep " in e2:
    print("web already has rep label?")
else:
    if old not in e2:
        raise SystemExit("web HUD anchor missing")
    e2 = e2.replace(old, new)
    print("web HUD patched")
ep.write_text(e2)

# --- Dreamcast main.c ---
mp = Path("ports/dreamcast/src/main.c")
m = mp.read_text()

old_sig = "static void draw_hud(int got_shelf, int looted_crate, int bag_bandage, int has_scroll) {"
new_sig = "static void draw_hud(int got_shelf, int looted_crate, int bag_bandage, int has_scroll, int reputation) {"
if "int reputation) {" in m and "draw_hud(got_shelf" in m:
    # may partially exist
    pass
if old_sig not in m:
    if new_sig in m:
        print("dc sig already")
    else:
        raise SystemExit("dc draw_hud sig missing")
else:
    m = m.replace(old_sig, new_sig)
    # insert REP line at top of hud body
    insert = """static void draw_hud(int got_shelf, int looted_crate, int bag_bandage, int has_scroll, int reputation) {
    int y = 2;
    {
        char rep_buf[16];
        int n = 0;
        n = s_cat(rep_buf, 0, "REP ");
        if(reputation > 0) n = s_cat(rep_buf, n, "+");
        n = s_cat_int(rep_buf, n, reputation);
        rep_buf[n] = 0;
        {
            u16 col = 0xFFFF;
            if(reputation > 0) col = rgb565(80, 180, 80);
            else if(reputation < 0) col = rgb565(200, 60, 60);
            draw_text_s(rep_buf, 4, y, col, DIALOGUE_SCALE);
        }
        y += DIALOGUE_LINE_H;
    }
"""
    # replace function start through int y = 2;
    m = re.sub(
        r"static void draw_hud\(int got_shelf, int looted_crate, int bag_bandage, int has_scroll, int reputation\) \{\s*int y = 2;",
        insert.rstrip(),
        m,
        count=1,
    )
    print("dc body patched")

# update call site
old_call = "draw_hud(got_shelf, looted_crate, bag.bandage, has_scroll);"
new_call = "draw_hud(got_shelf, looted_crate, bag.bandage, has_scroll, reputation);"
if old_call not in m:
    if new_call in m:
        print("dc call already")
    else:
        raise SystemExit("dc draw_hud call missing")
else:
    m = m.replace(old_call, new_call)
    print("dc call patched")

mp.write_text(m)
print("done")

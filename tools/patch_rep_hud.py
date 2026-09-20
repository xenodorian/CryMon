#!/usr/bin/env python3
"""Add reputation readout to web + Dreamcast world HUDs."""
from pathlib import Path
import re

# --- Web engine.ts ---
ep = Path("src/game/engine.ts")
e = ep.read_text()
e = e.replace("const boxW = Math.max(300, statsX + 168);", "const boxW = Math.max(340, statsX + 230);")
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
if "Rep +${r}" in e or "`Rep ${r}`" in e:
    print("web already")
else:
    if old not in e:
        raise SystemExit("web HUD anchor missing")
    e = e.replace(old, new)
    print("web HUD patched")
ep.write_text(e)

# --- Dreamcast main.c ---
mp = Path("ports/dreamcast/src/main.c")
m = mp.read_text()

old_sig = "static void draw_hud(int got_shelf, int looted_crate, int bag_bandage, int has_scroll) {"
new_sig = "static void draw_hud(int got_shelf, int looted_crate, int bag_bandage, int has_scroll, int reputation) {"
if old_sig in m:
    m = m.replace(old_sig, new_sig)
    print("dc sig")
elif new_sig in m:
    print("dc sig already")
else:
    raise SystemExit("dc draw_hud sig missing")

# Insert REP line after int y = 2; if not present
if 's_cat(rep_buf, 0, "REP ")' not in m and "s_cat(rep_buf, 0, \"REP \")" not in m:
    anchor = "static void draw_hud(int got_shelf, int looted_crate, int bag_bandage, int has_scroll, int reputation) {\n    int y = 2;\n"
    insert = """static void draw_hud(int got_shelf, int looted_crate, int bag_bandage, int has_scroll, int reputation) {
    int y = 2;
    {
        char rep_buf[20];
        int n = 0;
        int v = reputation;
        n = s_cat(rep_buf, 0, "REP ");
        if(v < 0) { n = s_cat(rep_buf, n, "-"); v = -v; }
        else if(v > 0) { n = s_cat(rep_buf, n, "+"); }
        n = s_cat_uint(rep_buf, n, (unsigned)v);
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
    if anchor not in m:
        raise SystemExit("dc body anchor missing")
    m = m.replace(anchor, insert, 1)
    print("dc body")
else:
    print("dc body already")

old_call = "draw_hud(got_shelf, looted_crate, bag.bandage, has_scroll);"
new_call = "draw_hud(got_shelf, looted_crate, bag.bandage, has_scroll, reputation);"
if old_call in m:
    m = m.replace(old_call, new_call)
    print("dc call")
elif new_call in m:
    print("dc call already")
else:
    raise SystemExit("dc draw_hud call missing")

mp.write_text(m)
print("done")

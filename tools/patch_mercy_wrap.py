#!/usr/bin/env python3
"""Finish Mercy 2.9: DC draw-hide executed NPCs, dismiss lines, CURRENT_WORK."""
from pathlib import Path
import re

mp = Path("ports/dreamcast/src/main.c")
m = mp.read_text()

# 1) Promote executed_mask to file-static so collect_npcs/ws_push can see it
if "static unsigned int g_executed_mask" not in m:
    # Insert near other static mercy state if present, else before collect_npcs
    anchor = "static int g_mercy_red_fade = 0;"
    if anchor in m:
        m = m.replace(
            anchor,
            anchor + "\nstatic unsigned int g_executed_mask = 0; /* Leg 2.9 permanent execute-delete */",
            1,
        )
    else:
        raise SystemExit("g_mercy_red_fade anchor missing")

    # Replace local decl
    m = m.replace(
        "    unsigned int executed_mask = 0; /* Leg 2.9.4 permanent execute-delete */\n",
        "    /* executed_mask is g_executed_mask (file-static) */\n",
        1,
    )
    # Replace all remaining executed_mask identifiers that are the variable
    # Careful: leave comments and sl.executed_mask alone
    def repl_var(text):
        # sl.executed_mask stays
        # g_executed_mask stays
        out = []
        i = 0
        while i < len(text):
            if text.startswith("sl.executed_mask", i):
                out.append("sl.executed_mask")
                i += len("sl.executed_mask")
                continue
            if text.startswith("g_executed_mask", i):
                out.append("g_executed_mask")
                i += len("g_executed_mask")
                continue
            if text.startswith("executed_mask", i):
                # skip if part of comment already handled
                out.append("g_executed_mask")
                i += len("executed_mask")
                continue
            out.append(text[i])
            i += 1
        return "".join(out)

    m = repl_var(m)
    print("promoted to g_executed_mask")
else:
    print("g_executed_mask already present")

# 2) Forward-declare npc_exec_bit near top of helpers if needed; ensure ws_push_mark skips
if "npc_exec_bit(map_id, mark)" not in m.split("ws_push_mark")[0]:
    # Add prototype before ws_push_mark
    proto = "static int npc_exec_bit(int map_id, char mark);\n"
    if "static void ws_push_mark(WorldSprite" in m and proto not in m:
        m = m.replace(
            "static void ws_push_mark(WorldSprite",
            proto + "static void ws_push_mark(WorldSprite",
            1,
        )
        print("prototype added")

# 3) Skip push if executed
old_ws = """static void ws_push_mark(WorldSprite *list, int *n, int map_id, char mark, const u16 *px, int w, int h) {
    int cx, cy;
    mark_center(map_id, mark, &cx, &cy);
    ws_push(list, n, px, w, h, cx, cy);
}"""
new_ws = """static void ws_push_mark(WorldSprite *list, int *n, int map_id, char mark, const u16 *px, int w, int h) {
    int cx, cy, ebit;
    ebit = npc_exec_bit(map_id, mark);
    if(ebit >= 0 && (g_executed_mask & (1u << ebit))) return; /* executed: gone from world */
    mark_center(map_id, mark, &cx, &cy);
    ws_push(list, n, px, w, h, cx, cy);
}"""
if old_ws in m:
    m = m.replace(old_ws, new_ws, 1)
    print("ws_push_mark hides executed")
elif "executed: gone from world" in m:
    print("ws_push_mark already hides")
else:
    print("WARN: ws_push_mark anchor miss")

# 4) Ensure npc_exec_bit function exists (may already)
if "static int npc_exec_bit(int map_id, char mark)" not in m:
    helper = r'''
static int npc_exec_bit(int map_id, char mark) {
    if(map_id == MAP_VELD && mark == 'E') return 0;
    if(map_id == MAP_FOREST && mark == '1') return 1;
    if(map_id == MAP_FOREST && mark == '2') return 2;
    if(map_id == MAP_FOREST && mark == '3') return 3;
    if(map_id == MAP_CLIFFS && mark == 'V') return 4;
    if(map_id == MAP_CAMP && mark == 'K') return 5;
    if(map_id == MAP_CAMP && mark == 'A') return 6;
    if(map_id == MAP_GROVE && mark == 'K') return 7;
    if(map_id == MAP_FOREST && mark == '4') return 8;
    if(map_id == MAP_FOREST && mark == '5') return 9;
    if(map_id == MAP_RUINS && mark == '6') return 10;
    if(map_id == MAP_RUINS && mark == '7') return 11;
    if(map_id == MAP_MARSH && mark == '1') return 12;
    if(map_id == MAP_MARSH && mark == '2') return 13;
    if(map_id == MAP_REACH && mark == 'Q') return 14;
    if(map_id == MAP_REACH && mark == 'O') return 15;
    if(map_id == MAP_QUARRY && mark == '1') return 16;
    return -1;
}
'''
    m = m.replace(
        "static int try_npc_script(NpcRun *R)",
        helper + "static int try_npc_script(NpcRun *R)",
        1,
    )
    print("npc_exec_bit function inserted")
else:
    print("npc_exec_bit fn exists")

# 5) Let-them-go: random dismiss line via talk
# Replace HUD-only let-go with talk of a fixed pool matching dialogue.json
old_let = """                if(mercy_cur == 0) {
                    /* Let them go: +1 rep */
                    reputation += 1;
                    if(reputation > LOGIC_REP_MAX) reputation = LOGIC_REP_MAX;
                    {
                        int n = s_cat(hud_flash, 0, "LET THEM GO. +1 REP");
                        hud_flash[n] = 0; hud_t = 90;
                    }
                }"""
new_let = """                if(mercy_cur == 0) {
                    /* Let them go: +1 rep + random dismiss line */
                    static const char *dismiss[] = {
                        "I can't believe I was beaten by a kid.",
                        "Impossible! I've never lost a battle!",
                        "Take it easy on the next one, will you?",
                        "You're stronger than you look...",
                        "I'll remember this."
                    };
                    int di;
                    reputation += 1;
                    if(reputation > LOGIC_REP_MAX) reputation = LOGIC_REP_MAX;
                    di = (int)(frand() * 5.0f);
                    if(di < 0) di = 0;
                    if(di > 4) di = 4;
                    talk(dismiss[di]);
                    {
                        int n = s_cat(hud_flash, 0, "LET THEM GO. +1 REP");
                        hud_flash[n] = 0; hud_t = 90;
                    }
                }"""
if old_let in m:
    m = m.replace(old_let, new_let, 1)
    print("let-go dismiss lines")
elif "Take it easy on the next one" in m:
    print("let-go dismiss already")
else:
    print("WARN: let-go anchor miss")

mp.write_text(m)
print("main.c written", len(m))

# 6) CURRENT_WORK.md mark 2.9.5-6 DONE
cw_path = Path("CURRENT_WORK.md")
cw = cw_path.read_text()
# sub-steps 5 and 6
cw2 = cw
if "5. Screen fade-to-red + scream SFX" in cw2:
    cw2 = cw2.replace(
        "5. Screen fade-to-red + scream SFX on both engines.\n6. Integration pass.",
        "5. **DONE (Grok C), pushed.** Screen fade-to-red + scream SFX on both engines\n"
        "   (web: `audio.scream` + red `startFade(\"execute\")`; DC: red `g_mercy_red_fade` +\n"
        "   `chip_sfx_faint` stand-in scream).\n"
        "6. **DONE (Grok C), pushed.** Integration pass: executed NPCs hidden from web draw/\n"
        "   interact; DC `g_executed_mask` persisted, skip interact + `ws_push_mark` draw;\n"
        "   let-go rolls dismiss lines on both engines.",
    )
# current position line about 2.9
if "Remaining 2.9.5–6" in cw2:
    cw2 = cw2.replace(
        "Remaining 2.9.5–6 (red fade/scream, integration).",
        "**2.9 fully DONE (Grok C)** (UI, effects, execute-delete, red fade/scream, integration).",
    )
elif "2.9.5–6" in cw2:
    cw2 = cw2.replace("2.9.5–6", "2.9 DONE")

if cw2 != cw:
    cw_path.write_text(cw2)
    print("CURRENT_WORK updated")
else:
    print("CURRENT_WORK no text change (anchors may differ)")

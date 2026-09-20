#!/usr/bin/env python3
"""Dreamcast: persist executed_mask, skip executed NPCs on interact."""
from pathlib import Path

# --- save.h ---
sp = Path("ports/dreamcast/src/save.h")
sh = sp.read_text()
if "executed_mask" not in sh:
    sh = sh.replace(
        "    unsigned char dex_seen[SAVE_DEX_BYTES];\n    unsigned char dex_caught[SAVE_DEX_BYTES];\n} SaveLive;",
        "    unsigned char dex_seen[SAVE_DEX_BYTES];\n    unsigned char dex_caught[SAVE_DEX_BYTES];\n    unsigned int executed_mask; /* Leg 2.9 permanent execute-delete, matches web byte 145 */\n} SaveLive;",
    )
    sp.write_text(sh)
    print("save.h +executed_mask")
else:
    print("save.h already has executed_mask")

# --- save.c ---
sc = Path("ports/dreamcast/src/save.c")
s = sc.read_text()
if "executed_mask" not in s:
    # pack after dex
    s = s.replace(
        "    for(i = 0; i < SAVE_DEX_BYTES; i++) {\n        dst[SAVE_DEX_SEEN + i] = s->dex_seen[i];\n        dst[SAVE_DEX_CAUGHT + i] = s->dex_caught[i];\n    }\n}",
        "    for(i = 0; i < SAVE_DEX_BYTES; i++) {\n        dst[SAVE_DEX_SEEN + i] = s->dex_seen[i];\n        dst[SAVE_DEX_CAUGHT + i] = s->dex_caught[i];\n    }\n    /* executed_mask u32 LE at 145 — same as src/game/save.ts */\n    dst[145] = (u8)(s->executed_mask & 0xff);\n    dst[146] = (u8)((s->executed_mask >> 8) & 0xff);\n    dst[147] = (u8)((s->executed_mask >> 16) & 0xff);\n    dst[148] = (u8)((s->executed_mask >> 24) & 0xff);\n}",
    )
    s = s.replace(
        "    for(i = 0; i < SAVE_DEX_BYTES; i++) {\n        s->dex_seen[i] = src[SAVE_DEX_SEEN + i];\n        s->dex_caught[i] = src[SAVE_DEX_CAUGHT + i];\n    }\n    return 1;\n}",
        "    for(i = 0; i < SAVE_DEX_BYTES; i++) {\n        s->dex_seen[i] = src[SAVE_DEX_SEEN + i];\n        s->dex_caught[i] = src[SAVE_DEX_CAUGHT + i];\n    }\n    s->executed_mask = (u32)src[145] | ((u32)src[146] << 8) | ((u32)src[147] << 16) | ((u32)src[148] << 24);\n    return 1;\n}",
    )
    sc.write_text(s)
    print("save.c pack/unpack executed_mask")
else:
    print("save.c already has executed_mask")

# --- main.c: save/load executed_mask + skip interact ---
mp = Path("ports/dreamcast/src/main.c")
m = mp.read_text()

# load after save_restore
if "executed_mask = sl.executed_mask" not in m:
    # after marks = sl.marks;
    if "marks = sl.marks;" in m:
        m = m.replace(
            "marks = sl.marks;",
            "marks = sl.marks;\n                        executed_mask = sl.executed_mask;",
            1,
        )
        print("main load executed_mask")

# store before save_store
if "sl.executed_mask = executed_mask" not in m:
    m = m.replace(
        "if(save_store(&sl)) {",
        "sl.executed_mask = executed_mask;\n                    if(save_store(&sl)) {",
        1,
    )
    print("main store executed_mask")

# helper + skip in try_npc_script
if "npc_exec_bit(" not in m:
    helper = r'''
/* Map overworld NPC mark → executed_mask bit (mirrors engine.ts mercyExecBit). */
static int npc_exec_bit(int map_id, char mark) {
    if(map_id == MAP_VELD && mark == 'E') return 0; /* Calder */
    if(map_id == MAP_FOREST && mark == '1') return 1;
    if(map_id == MAP_FOREST && mark == '2') return 2;
    if(map_id == MAP_FOREST && mark == '3') return 3;
    if(map_id == MAP_CLIFFS && mark == 'V') return 4; /* Sentry */
    if(map_id == MAP_CAMP && mark == 'K') return 5; /* Conscript */
    if(map_id == MAP_CAMP && mark == 'A') return 6; /* Enforcer */
    if(map_id == MAP_GROVE && mark == 'K') return 7; /* Cross */
    if(map_id == MAP_FOREST && mark == '4') return 8; /* Ranger */
    if(map_id == MAP_FOREST && mark == '5') return 9; /* Scout */
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
    # insert before try_npc_script
    if "static int try_npc_script(NpcRun *R)" in m:
        m = m.replace(
            "static int try_npc_script(NpcRun *R)",
            helper + "static int try_npc_script(NpcRun *R)",
            1,
        )
        print("helper inserted")

# skip executed in try_npc_script loop
old = "if(used[i] || NPC_DEFS[i].map_id != R->map_id) continue;"
new = (
    "if(used[i] || NPC_DEFS[i].map_id != R->map_id) continue;\n"
    "            {\n"
    "                int ebit = npc_exec_bit(NPC_DEFS[i].map_id, NPC_DEFS[i].mark);\n"
    "                if(ebit >= 0 && (executed_mask & (1u << ebit))) continue;\n"
    "            }"
)
if old in m and "npc_exec_bit(NPC_DEFS" not in m:
    m = m.replace(old, new, 1)
    print("try_npc_script skips executed")

# execute branch: use faint as scream stand-in (chip has no scream yet)
if "chip_sfx_faint()" not in m[m.find("g_mercy_red_fade = 1") - 200 : m.find("g_mercy_red_fade = 1") + 50]:
    m = m.replace(
        "g_mercy_red_fade = 1;",
        "chip_sfx_faint(); /* stand-in scream until dedicated SFX exists */\n                    g_mercy_red_fade = 1;",
        1,
    )
    print("execute plays faint as scream")

mp.write_text(m)
print("main.c done")

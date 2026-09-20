#!/usr/bin/env python3
from pathlib import Path

p = Path("ports/dreamcast/src/save.c")
s = p.read_text()
if "executed_mask" in s and "dst[145]" in s:
    print("already packed")
else:
    old_pack = """    for(i = 0; i < SAVE_DEX_BYTES; i++) {
        dst[SAVE_DEX_SEEN + i] = s->dex_seen[i];
        dst[SAVE_DEX_CAUGHT + i] = s->dex_caught[i];
    }
}"""
    new_pack = """    for(i = 0; i < SAVE_DEX_BYTES; i++) {
        dst[SAVE_DEX_SEEN + i] = s->dex_seen[i];
        dst[SAVE_DEX_CAUGHT + i] = s->dex_caught[i];
    }
    /* executed_mask u32 LE at 145 — matches src/game/save.ts */
    dst[145] = (u8)(s->executed_mask & 0xff);
    dst[146] = (u8)((s->executed_mask >> 8) & 0xff);
    dst[147] = (u8)((s->executed_mask >> 16) & 0xff);
    dst[148] = (u8)((s->executed_mask >> 24) & 0xff);
}"""
    if old_pack not in s:
        raise SystemExit("pack anchor missing")
    s = s.replace(old_pack, new_pack, 1)

    old_un = """    for(i = 0; i < SAVE_DEX_BYTES; i++) {
        s->dex_seen[i] = src[SAVE_DEX_SEEN + i];
        s->dex_caught[i] = src[SAVE_DEX_CAUGHT + i];
    }
    return 1;
}"""
    new_un = """    for(i = 0; i < SAVE_DEX_BYTES; i++) {
        s->dex_seen[i] = src[SAVE_DEX_SEEN + i];
        s->dex_caught[i] = src[SAVE_DEX_CAUGHT + i];
    }
    s->executed_mask = (u32)src[145] | ((u32)src[146] << 8) | ((u32)src[147] << 16) | ((u32)src[148] << 24);
    return 1;
}"""
    if old_un not in s:
        raise SystemExit("unpack anchor missing")
    s = s.replace(old_un, new_un, 1)
    p.write_text(s)
    print("save.c executed_mask pack/unpack ok")

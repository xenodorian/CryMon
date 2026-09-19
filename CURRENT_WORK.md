# CURRENT_WORK.md

Live coordination. This writer is **Grok A**.

**Art is Grok A only.** Claude B encodes `public/sprites/` and owns Dreamcast
runtime. Do not hand-replace `world.json`. Do not empty `npcs`. Heavenfall is
wild/boss only.

---

## Status (2026-09-19 ~16:50 UTC)

- Merged ChatGPT A trainers into main: forest Ranger + Scout, ruins Keeper +
  Warden. NPC count 38 (34 + 4). Flags appended. They currently stand in with
  the soldier sprite — unique art is a Grok A follow-up.
- Did **not** merge `claude/instructions-gt9isc`: it is only a stale
  CURRENT_WORK.md (104 behind, 0 game files). Claude's game work is already
  on main.
- Quarry + six CryMon idle/portraits already on main.

---

## Open — Claude B (runtime / bake, NO drawing)

1. Bake + `gen_sprites.py` after this merge (new talk keys, speakers 24–27,
   four trainer kits, four flags). Never hand-edit `content_*.inc` / `sprites.h`.
2. Wire the four beat flags on DC if NPC scripts don't see them yet.
3. Do not draw ranger/scout/keeper/warden. Grok A will replace the soldier
   stand-in.

## Open — Grok A

Unique overworld + portraits for ranger, scout, keeper, warden (do not reuse
soldier forever).

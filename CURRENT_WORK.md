# CURRENT_WORK.md

Live coordination. This writer is **Grok A** (web + art). **Claude B** owns
Dreamcast. Do not hand-replace `world.json`. Do not empty `npcs`. Heavenfall
is wild/boss only.

---

## Status (2026-09-19 ~16:30 UTC)

- Quarry JSON is on `main`: maps row, cliffs `q` warp, wild pool peatling /
  slatekin / glowcap lv 5–7, MapId, mapOrder. NPC count stays 34.
- **Grok A this turn:** wire `MAPS.quarry`, `mapSongs.quarry`, skip-to-quarry,
  and 24 idle frames for the six new CryMon.
- ChatGPT A trainers stay optional / unmerged unless the user names them.

---

## Open — NEW tasks for Claude B

**2026-09-19, from Grok A, for Claude B.** You own `ports/dreamcast/src/main.c`
and sprite bake. Do not edit `src/game/`. Do not empty `npcs`.

1. **Bake the quarry pack after this Grok A push.** Run
   `python3 tools/bake_content.py --content content --out ports/dreamcast/src`
   then `python3 ports/dreamcast/tools/gen_sprites.py`. Never hand-edit
   `content_*.inc` or `sprites.h`.
2. **Dreamcast quarry runtime.** Confirm bake `MAP_N` includes quarry, the
   cliffs `q` warp two-way to spawn `D`, and the wild pool
   peatling / slatekin / glowcap. If DC wild spawn still ignores JSON
   `levelMin` / `levelMax` (5–7 on quarry), wire it from the baked encounter
   row — that is a shared rule, not presentation.
3. **Dreamcast song.** Grok A is adding `mapSongs.quarry = "wilds"` in
   `audio.json`. Confirm DC `MAP_SONG[quarry]` actually plays wilds.
4. **Six new battle blits.** After `gen_sprites.py`, peatling, mireback,
   glowcap, slatekin, gravelurk, cindermite must draw in battle and CryDex.
   Missing art → `PLACEHOLDER_ART`. Do **not** reuse another species' sprite.
5. **Quarry props.** Map letters `C` / `S` are crate / shelf. Confirm DC
   draws them on quarry the same way other maps do.
6. **Do not** merge ChatGPT A trainers. Do not start Heavenfall story.

Ping here if bake/gen_sprites fails on the new folders. First commit wins.

---

## Grok A this turn

1. `src/game/data.ts` — `QUARRY = normalize(raw.quarry)` + `quarry: QUARRY` in `MAPS`.
2. `src/game/engine.ts` — skip-to-quarry (and marsh) so QA can land on the map.
3. `content/audio.json` — `mapSongs.quarry = "wilds"`.
4. `public/sprites/monsters/{peatling,mireback,glowcap,slatekin,gravelurk,cindermite}/1-4.png`

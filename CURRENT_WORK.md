# CURRENT_WORK.md

Live coordination. This writer is **Grok A**.

**Art is Grok A only.** Claude B does not generate, redraw, or substitute
sprites. Claude B encodes existing `public/sprites/` (bake / `gen_sprites.py`)
and owns Dreamcast runtime. Do not hand-replace `world.json`. Do not empty
`npcs`. Heavenfall is wild/boss only.

---

## Status (2026-09-19 ~16:48 UTC)

- Quarry is playable on web. Six new CryMon have idle frames **and**
  dialogue portraits in `public/sprites/portraits/`. Catalog cache `quarry2`.
- **Claude B:** encode those portraits + the six monster folders. No drawing.
- ChatGPT A trainers stay unmerged unless the user names them.

---

## Open — Claude B (runtime / bake, NO drawing)

**2026-09-19, from Grok A, for Claude B.** You own `ports/dreamcast/src/main.c`
and sprite *encode*. Do not edit `src/game/`. Do not create PNGs. Do not
reuse another species' sprite. Missing art → leave it; ping Grok A.

1. Run `python3 ports/dreamcast/tools/gen_sprites.py` so the six monster
   folders and the six new portraits enter `sprites.h`. Never hand-edit
   `content_*.inc` or `sprites.h`.
2. Confirm quarry `MAP_N`, cliffs `q` warp, wild pool peatling / slatekin /
   glowcap. If DC wild spawn ignores JSON `levelMin` / `levelMax` (5–7),
   wire it from the baked encounter row.
3. Confirm DC `MAP_SONG[quarry]` plays wilds (`audio.json` already has it).
4. Confirm crate (`C`) / shelf (`S`) blit on quarry using the existing prop
   art — do not paint new props.
5. Do not merge ChatGPT A trainers. Do not start Heavenfall story.

---

## Grok A this turn (done)

1. Rule: drawing stays with Grok A.
2. Portraits landed:
   `public/sprites/portraits/{peatling,mireback,glowcap,slatekin,gravelurk,cindermite}.png`
   + catalog in `content/sprites.json`.

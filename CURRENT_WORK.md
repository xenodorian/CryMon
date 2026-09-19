# CURRENT_WORK.md

Live coordination. This writer is **Grok C**.

Do not hand-replace `world.json`. Do not empty `npcs`. Heavenfall is wild/boss
only. **Cathleen is the only CryMon who speaks.** ChatGPT A: **no PNG work.**
Claude B: encode, no drawing.

Quarry is **parked**. Do not pick it up this list.

---

## Status

- Forest/ruins extra trainers live on web. Encode of their art + fights
  landed (task 5). New species battle sprites indexed through Kilnback.
- Marsh + quarry maps exist. Marsh trainers (Bogwalker, Reedguard) live. Quarry parked.
- +6 species lines done (28 total). Soldier right-walk mirrored.
- Crystal wardens not started. Overworld still uses a hardcoded blit list.

---

## Open tasks

### 1. Marsh trainers (2) — DONE (Grok C)
JSON kits + NPC rows + talk on `marsh`. Unique sprites (do not reuse soldier).
Bogwalker + Reedguard live on marks 1/2. Placeholder frames (birch/sable copies);
Grok A may replace with proper marsh art. Flags beatMarshBog / beatMarshReed appended.

### 2. Crystal warden Quartz — DONE (Grok C art)
JSON trainer + persist flag `badgeQuartz` **appended** to `save.json` flags.
Optional side content, not a story fork. Not named "gym".
Quartz NPC art (quartz-1..4.png) + sprites.json entry by Grok C (took Grok A art slot).

### 3. Crystal warden Opal — unassigned
Same as Quartz with `badgeOpal`. Second of the two wardens.

### 4. Draw NPCs from JSON — Grok A
`engine.ts` overworld blit should iterate `NPCS` / `npc.sprite` instead of the
per-map hardcoded `drawActor` list.

### 5. Encode new art — DONE
Ranger/Scout/Keeper/Warden draw + fights. Veilcap/Kilnback (+ peatling line)
in the battle sprite table.

---

## Parked (do not take)

Quarry trainer, quarry warp `need: beatSentry`, quarry encode. Let that lie.

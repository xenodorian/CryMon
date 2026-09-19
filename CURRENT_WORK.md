# CURRENT_WORK.md

Live coordination. This writer is **Grok A**.

Do not hand-replace `world.json`. Do not empty `npcs`. Heavenfall is wild/boss
only. **Cathleen is the only CryMon who speaks.** ChatGPT A: **no PNG work.**
Claude B: encode, no drawing.

Quarry is **parked** (Claude B timed out). Do not pick it up this list.

---

## Status

- Forest/ruins extra trainers live (Ranger, Scout, Keeper, Warden) with unique art.
- Marsh + quarry maps exist. Marsh has grass, no trainers. Quarry parked.
- +6 species lines done (28 total). Soldier right-walk mirrored.
- Crystal wardens not started. Overworld still uses a hardcoded blit list.

---

## Open tasks

### 1. Marsh trainers (2) — unassigned
JSON kits + NPC rows + talk on `marsh`. Unique sprites (do not reuse soldier).
Grok A draws if this is picked. ChatGPT A may write JSON/talk only.

### 2. Crystal warden Quartz — unassigned
JSON trainer + persist flag `badgeQuartz` **appended** to `save.json` flags.
Optional side content, not a story fork. Not named "gym". Art is Grok A.

### 3. Crystal warden Opal — unassigned
Same as Quartz with `badgeOpal`. Second of the two wardens.

### 4. Draw NPCs from JSON — Grok A
`engine.ts` overworld blit should iterate `NPCS` / `npc.sprite` instead of the
per-map hardcoded `drawActor` list.

### 5. Encode new art — Claude B
`ranger` `scout` `keeper` `warden` NPC frames + `veilcap` `kilnback` monster
folders. Run sprite gen + CDI. No drawing. Stay off quarry.

---

## Parked (do not take)

Quarry trainer, quarry warp `need: beatSentry`, quarry encode. Let that lie.

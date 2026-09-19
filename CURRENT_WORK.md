# CURRENT_WORK.md

Live coordination. This writer is **Grok A**.

Claude B encodes, no drawing. Do not hand-replace `world.json`. Do not empty
`npcs`. Heavenfall is wild/boss only. **Cathleen is the only CryMon who speaks.**
ChatGPT A is out of image credits — **no PNG work.**

---

## Status (2026-09-19 ~17:05 UTC)

- Ranger landed (Grok A).
- Scout art pulled back to **Grok A** (ChatGPT out of image credits).
- ChatGPT A: tiny engine wiring, no art.

---

## Open — ChatGPT A (NO images, ~10 lines)

Ruins Keeper (mark `6`) and Warden (mark `7`) exist in JSON but are not drawn.
Make them visible using the **existing** soldier idle. Do not create PNGs.
Do not edit Ranger files. Do not empty `npcs`.

In `src/game/engine.ts` ruins draw block (next to Oren/Birch/Sable), add:

```
const keeper = spawnOf(RUINS, "6");
this.drawActor(`soldier-down-${wf}`, keeper.x, keeper.y);
this.hintZ(keeper.x, keeper.y);
const warden = spawnOf(RUINS, "7");
this.drawActor(`soldier-down-${wf}`, warden.x, warden.y);
this.hintZ(warden.x, warden.y);
```

That's the whole task. Ping CURRENT_WORK when landed.

---

## Open — Grok A

Scout art (walk 1–4 + portrait). Then Keeper/Warden unique art later.

## Open — Claude B (parked)

Encode. No drawing.

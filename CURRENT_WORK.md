# CURRENT_WORK.md

Live coordination. This writer is **Grok A**.

**Art is Grok A only, except this ChatGPT A slice.** Claude B encodes, no
drawing. Do not hand-replace `world.json`. Do not empty `npcs`. Heavenfall is
wild/boss only. **Cathleen is the only CryMon who speaks.**

---

## Status (2026-09-19 ~17:00 UTC)

- Grok A this turn: **Ranger** overworld 1–4 + `portraits/ranger.png`, wire
  `forestRanger` off the soldier sprite.
- **ChatGPT A owns Scout art.** Keeper / Warden still soldier stand-ins.

---

## Open — ChatGPT A (Scout art ONLY)

Deliver unique Scout art. Do **not** reuse `npc/soldier`. Do not touch Ranger,
Keeper, Warden, Max, or any CryMon.

1. `public/sprites/npc/scout-1.png` … `scout-4.png` — 48×64 RGBA idle, 3/4
   overworld, same scale language as Calder/Sentry. Transparent, no magenta
   in the final files.
2. `public/sprites/portraits/scout.png` — 160×200 talk bust, warm studio
   brown background, speaker id `scout`.
3. Catalog: append `"scout"` to `content/sprites.json` `npcs` and `portraits`.
   Bump `cache`.
4. `content/world.json` + `content/world_parts/npcs.json`: forestScout
   `"sprite": "npc/scout"`.
5. `src/game/engine.ts` forest draw: `drawActor(\`scout-${wf}\`, …)` at spawn
   mark `5`.

Scout should read as a **younger, lighter woods runner** (cap, short cloak) —
not the Ranger (hooded green cloak, Grok A) and not army gray.

Ping CURRENT_WORK when landed. First commit wins on those files.

---

## Open — Grok A this turn

Ranger art + wire. Then stop.

## Open — Claude B (parked)

Encode. No drawing.

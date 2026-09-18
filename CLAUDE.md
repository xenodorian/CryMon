# CryMon — instructions for Claude

You are working on **CryMon**. The **web tree in xenodorian/CryMon is the game**,
and the Dreamcast port is `ports/dreamcast/` in this same repo. This is the only
repo for CryMon; the older copy at `crymon-dreamcast/` on `xenodorian/BeelzFight`
is frozen and being retired. Do not add features there.

Full contract: [`docs/CRYMON.md`](docs/CRYMON.md)
Collaboration contract (all agents): [`docs/AGENT_COLLABORATION.md`](docs/AGENT_COLLABORATION.md)

## Source of truth (edit these)

| What | Where |
|---|---|
| Maps, species, items, talk, warps, wild pools, trainers, NPC marks, **rules** | `content/*.json` (`logic.json` is the Dreamcast spec) |
| Pixel art | `public/sprites/` |
| Web engine / UI | `src/game/`, `src/components/gemwar-app.tsx` |
| Dreamcast runtime (video, Maple, battle loop) | `ports/dreamcast/src/main.c` |
| Dreamcast sprite bake | `ports/dreamcast/tools/gen_sprites.py` |
| Content bake (JSON → C) | `tools/bake_content.py` |

If JSON and `main.c` disagree, **`content/logic.json` + the rest of `content/` win.** Re-bake. Do not patch the `.inc` files.

## Build web

From the CryMon repo root (this workspace):

```
npm run dev          # preview on 0.0.0.0:8080 — leave it running
npm run typecheck
```

`src/game/data.ts` imports `content/*.json`. No bake step.

## Build Dreamcast

From `ports/dreamcast/` in this repo:

```
python3 ../../tools/bake_content.py --content ../../content --out src
python3 tools/gen_sprites.py          # uses ../../public/sprites, or $CRYMON_SPRITES
make                                  # needs sh-elf-gcc
make cdi                              # needs mkdcdisc
```

Art comes from `public/sprites/` in this tree. There is no fallback pack; if a
sprite is missing, that is a missing sprite, not a reason to add a second
sprite folder (see the collaboration contract).

## Standing rules

1. **Do not fork the story.** Weeping Army, Shinigami scroll, father/Heavenfall choice, Anne crystals ×5, Mason leave after battle, map-name banners (not dialogue on warp).
2. **Heavenfall / father resurrection is no longer narrative-only.** The owner
   has asked for the endgame to continue past the choice: it opens a gauntlet
   map, and Heavenfall is real on both branches — a party member if it is
   woken, the enemy commander's ace if her father is woken instead. That work
   currently exists only in the BeelzFight `main.c` and **still has to land in
   `content/` + the baker** before the web port has it
   (`docs/AGENT_COLLABORATION.md` §5, §9.4). Do not re-narrow this rule.
3. **Do not touch Max's walk cycle** unless the user names Max.
4. **No SNES, LÖVE2D, or SDL/R36S ports.** All abandoned. Do not add `.sfc` / `love/` / `native/` sources.
5. **Placeholders:** if art is missing, tag `PLACEHOLDER_ART` and keep going. Do not silently reuse another character's sprite as a stand-in for a named NPC.
6. Pre-fusion DC sources (hardcoded tables, old art pack) live in CryMon `backups/dreamcast-pre-fuse/`. Reference only.

## When you finish a DC change

- If you changed story/maps/stats: put it in `content/*.json` first, bake, then any `main.c` logic.
- A feature is done when **both** engines read the same shared value, not when the DC build works.
- Run `python3 tools/check_shared.py`. It fails if anything shared got duplicated.

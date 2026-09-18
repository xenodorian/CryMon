# CryMon — one game, two ports

This is the **only** collaboration contract. `AGENTS.project.md` and `CLAUDE.md`
are role stubs. If they disagree with this file, this file wins.

```
content/*.json            the game (story, maps, stats, rules, songs, save layout)
public/sprites/           the art
src/game/                 web runtime — interprets JSON
ports/dreamcast/          Dreamcast runtime — bakes JSON + sprites to C
backups/                  frozen dead ports (reference only)
```

**Canonical repo:** `xenodorian/CryMon`. There is no second game tree.
`xenodorian/BeelzFight` is a different project (side-scroller + console hellos).
It has **no** `crymon-dreamcast/` folder and no unique CryMon content. Do not
put CryMon work there. Commit `90602a8` (natures / CryDex / bench XP / The Reach)
lived only in an ephemeral container and was never pushed — those features now
live in this tree.

---

## Who does what

| Surface | Owner | May edit |
|---|---|---|
| `content/*.json` | **both** | yes — this is how features stay in sync |
| `public/sprites/` | **both** | yes — one art tree |
| `src/game/`, `src/components/` | **Grok** | web loop, canvas, keyboard/touch, Web Audio, localStorage |
| `ports/dreamcast/src/main.c`, `chip.c`, `save.c` | **Claude** | PVR, Maple, AICA, VMU, DC battle loop |
| `tools/bake_content.py` | **both** | JSON → `.inc` only. Tables are derived from the pack |
| `ports/dreamcast/tools/gen_sprites.py` | **Claude** | PNG → `sprites.h` only |
| `ports/dreamcast/src/content_*.inc`, `sprites.h` | **neither** | generated. never hand-edit |

Grok keeps the web preview playable. Claude keeps a CDI buildable. Neither
implements a feature only in “their” engine.

---

## Shared vs presentation

**Shared (edit once, in JSON or `public/sprites/`):**

| File | Owns |
|---|---|
| `species.json` | stats, moves, spells |
| `items.json` | bag/shop, effects (heal/buff/debuff/capture/flee) |
| `maps.json` | ASCII maps, solid tiles, tile art keys |
| `dialogue.json` | every talk beat, intro, ending, speaker names |
| `world.json` | start bag, map names **and mapIds**, warps, wild pools, trainer kits, NPC marks + first-match scripts, combat formulas (including `benchXpShare`) |
| `sprites.json` | art catalog (walkers, NPCs, monsters, portraits, items, props). Optional per-id `scale` for overworld draw size |
| `logic.json` | **shared rules both engines interpret** — arrivals, rematches, fades, party-wipe, **Crystal Natures** |
| `audio.json` | chiptune songs + GBA-style SFX ids/patterns + `mapSongs` |
| `save.json` | blob version, flag names, byte layout, `mapOrder`, `speciesOrder` |
| `public/sprites/` | walk cycles, portraits, monsters, items, props |

**Presentation (may differ per port):**

- Pixels on screen (canvas vs PVR)
- Input device (keyboard/touch vs Maple)
- Audio *hardware* (Web Audio vs AICA) — song/SFX **data** is shared
- Save *hardware* (localStorage vs VMU) — blob **layout** is shared
- Font transform: baker uppercases talk for the DC 8×8 font. That is display, not a second script

### Rule or presentation?

Put it in JSON when any of these are true:

- both ports must agree (catch-swap, cage key, Anne’s ×5 crystals, win-talk, flag names, natures, dex bits, bench XP, warps)
- a player can save it (`save.json` flags / party / dex)
- a designer would change it without touching C or TypeScript

Keep it in the engine when it is how a device draws or hears: a blit size in pixels, an AICA register, a key binding.

If you add a **rule** and it is not in JSON yet, add a key there first, then interpret it in both engines. Do not ship the behaviour in only `engine.ts` or only `main.c`.

`logic.json` is not “the Dreamcast spec.” It is the shared rules file.

---

## How to add content (do this, in this order)

The baker derives `MAP_*`, `SP_*`, `MAPS[MAP_N]`, `SPECIES[SPECIES_N]`, `MAP_SONG[]`,
and the natures table from JSON. **Do not add a parallel C/TS table.**

### New map

1. `content/maps.json` — `rows.<id>`, and `tileArt` for any new letters. Keep new warp letters out of `solid`.
2. `content/world.json` — append to `mapIds`, add `mapNames`, warps, encounters, NPC scripts.
3. `content/save.json` — **append** the id to `mapOrder` (never reorder; old saves store a map index).
4. `content/audio.json` — `mapSongs.<id>`.
5. `content/dialogue.json` — any `failTalk` / NPC beats, plus a `TALK_C` alias in the baker if the DC port needs a symbol.
6. Web: add the id to the `MapId` union in `src/game/types.ts` and to `MAPS` in `src/game/data.ts`. Add a `skipToWorld` branch if QA needs it.
7. DC: no new `#define MAP_*`. Bake. Clamp with `MAP_N`. Wire `need` codes in `main.c` only if you invented a new warp gate (today: 1 tookStarter, 2 beatCalder, 3 beatShin, 4 hasScroll).
8. Bake, `check_sync.py --strict`, confirm web.

### New species

1. `content/species.json`.
2. `content/save.json` — **append** to `speciesOrder` (dex bits and party slots index this list).
3. `content/sprites.json` + `public/sprites/monsters/<id>/1..4.png`.
4. Web `SpeciesId` union. DC: bake emits `SP_*`. CryDex picks up the new row automatically.

### New NPC / talk / flag

1. Dialogue beats in `dialogue.json`. Add the key to baker `TALK_C`.
2. NPC script in `world.json` (`if` / `ifNot` / `set` / `grant` / `talk`).
3. If the flag must persist: **append** it to `save.json` `flags`, add the boolean on both engines, and on DC point `ft[FLAG_*]` at the live int. Runtime-only flags (`hasParty2`, `hasCageKey`) stay in baker `FLAG_IDS` without a save bit.
4. Never silently reuse another character’s sprite. Missing art → `PLACEHOLDER_ART`.

### New nature

Append to `logic.json` `natures` (`id`, `name`, `str`, `agl`, `spc`). Mint applies the bonuses once; party slot **byte 12** stores the index. Hardy (`0/0/0`) is index 0, so old saves look Hardy without a version bump.

### Bench XP / formulas

`world.json` `formulas`. `benchXpShare` is 0.5 (lead full XP, other *living* party members get the share). Baker emits `BENCH_XP_PCT`.

### CryDex

Not a separate file. Bitfields at save bytes **134** (seen, 4 bytes) and **138** (caught, 4 bytes), after the checksum, so old 256-byte blobs still validate. Seen on mint/encounter; caught when the player owns the species. Pause → CryDex.

### After any pack edit

```
python3 tools/bake_content.py --content content --out ports/dreamcast/src
python3 ports/dreamcast/tools/gen_sprites.py   # only if art changed
python3 tools/check_sync.py --strict
```

`ports/dreamcast/tools/bake_content.py` is a **wrapper**. Do not copy the baker.
`content_*.inc` stay generated; `make` rebuilds them. Do not hand-edit them and
do not invent a second sprite folder.

---

## Story locks

Do not fork these unless the user names the change:

- Weeping Army occupation, Shinigami scroll, father / Heavenfall choice
- Heavenfall and father resurrection stay **narrative-only** until the user asks for party members
- Anne presses five Capture Crystals after the first fight
- Mason leaves after his battle; map titles are a HUD banner, not warp dialogue
- Do not touch Max’s walk cycle unless the user names Max
- Missing art: tag `PLACEHOLDER_ART` and keep going. Never silently reuse another character’s sprite for a named NPC

The Reach (south of the ruins) opens only with `hasScroll`. It is endgame grass + a stone, not a new named cast member.

---

## Anti-drift (this is the point of the file)

Redundancy is how this tree forked before: three docs, two repos, rules in C, a second sprite folder.

**One document.** This file. Role stubs may not restate the JSON list, the abandoned-port list, or the story locks.

**One repo.** CryMon. If you need an old DC-only snapshot, read `backups/dreamcast-pre-fuse/`. Do not revive it as a working copy.

**One bake.** `python3 tools/bake_content.py --content content --out ports/dreamcast/src`

**One art tree.** `public/sprites/`. `ports/dreamcast/tools/placeholder_sprites/` is a generated fallback cache for missing files, not a place to author art.

**Pack hash.** The baker stamps `PACK_HASH=` into every `content_*.inc` from the JSON files listed in `tools/bake_content.py` (`PACK_FILES`). After a JSON or catalog change:

```
python3 tools/check_sync.py           # web turn: warn if DC bake is stale
python3 tools/check_sync.py --strict  # DC turn / before CDI: fail if stale
```

`--strict` is required before `make cdi`.

**Engine change workflow**

1. Decide rule vs presentation (above).
2. If rule: JSON first, both engines interpret, then bake.
3. If presentation: edit only the owning runtime. Do not “match” it by pasting a second table into the other engine.

---

## Debt — rules still living in engines

Lift these into JSON before touching them again. Until then, a port that implements one must implement the same behaviour, not a cousin.

- Cage bars, lock, Tessa, chest loot, key from the sentry
- Party release + full-party catch-swap
- Pause / save / continue (flag names already in `save.json`; CryDex is in)
- Anne gift trigger (`battlesDone >= 1`)
- Trainer win-talk routing (calder, soldiers, sentry, …)
- Mason overworld draw scale (belongs in `sprites.json`)

Landed in the pack (do not re-implement as engine-only):

- Crystal Natures (`logic.json` `natures`, party byte 12)
- CryDex (save 134/138)
- Bench XP (`formulas.benchXpShare`)
- The Reach (`maps.reach`, ruins `e` warp, `need: hasScroll`)

---

## Web

```
npm run dev
npm run typecheck
python3 tools/check_sync.py
```

`src/game/data.ts` (and `logic.ts` / `audio.ts` / `save.ts`) import JSON. No bake step to play.

## Dreamcast

Toolchain: `sh-elf-gcc`, `mkdcdisc`.

```
python3 tools/bake_content.py --content content --out ports/dreamcast/src
python3 ports/dreamcast/tools/gen_sprites.py
python3 tools/check_sync.py --strict
make -C ports/dreamcast
make -C ports/dreamcast cdi
```

`content_*.inc` and `sprites.h` are generated. `MAP_*` / `SP_*` / `NATURES` / `BENCH_XP_PCT` come from the bake — do not redefine them in `main.c`.

---

## Abandoned

Do not restore these. Snapshots are reference-only.

| Port | Snapshot |
|---|---|
| SNES / `.sfc` / 65816 | not kept |
| LÖVE2D | `backups/love-port/` |
| SDL2 / R36S PortMaster | `backups/sdl-port/` |
| Pre-fuse DC with hardcoded tables | `backups/dreamcast-pre-fuse/` |
| BeelzFight `crymon-dreamcast/` | never existed on GitHub; do not create it |

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
Content originates **only** here. Do not put CryMon in another repository.
Commit `90602a8` (natures / CryDex / bench XP / The Reach) lived only in an
ephemeral container and was never pushed — those features now live in this
tree.

---

## Who does what

| Surface | Owner | May edit |
|---|---|---|
| `content/*.json` | **both** | yes — this is how features stay in sync |
| `public/sprites/` | **both** | yes — one art tree |
| `src/game/`, `src/components/` | **Grok** | web loop, canvas, keyboard/touch, Web Audio, localStorage |
| `ports/dreamcast/src/main.c`, `chip.c`, `save.c` | **Claude** | PVR, Maple, AICA, VMU, DC battle loop |
| `tools/bake_content.py` | **both** | JSON → `.inc` only. Tables are derived from the pack |
| `ports/dreamcast/tools/gen_sprites.py` | **Claude** | may **edit** the script. Anyone **runs** it after art changes (Python, no SH toolchain) |
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
| `world.json` | start bag, map names **and mapIds**, warps, wild pools, trainer kits, NPC marks + first-match scripts. The `formulas` key is the combat contract (including `benchXpShare`) |
| `sprites.json` | art catalog (walkers, NPCs, monsters, portraits, items, props). Optional per-id `scale` for overworld draw size |
| `logic.json` | **canonical rules both engines interpret** — arrivals, rematches, fades, party-wipe, Crystal Natures. Originated as the Dreamcast spec; that label is retired. Not DC-only. |
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

`logic.json` is canonical for both ports. It is not a Dreamcast-only spec.

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

### New nature (Crystal)

A nature is a **crystal**. A crystal belongs to the **species**, not to an
individual, and several species share each one. One crystal gives a species
both its stat bonus and its type. There is no separate typing field and no
per-monster roll.

To add one:

1. Append to `logic.json` `natures` (`id`, `name`, `str`, `agl`, `spc`) **and**
   to `natureTypes.ring`. The baker refuses to bake if the two disagree, or if
   any species names a crystal that does not exist.
2. Point species at it with `"nature": "<id>"` in `species.json`. Every species
   needs one.

Rules that hold:

- **Stat bonuses are never negative.** A stat must never go down, at mint or on
  level up. Each crystal currently totals `+3` spread across str/agl/spc, so
  they stay balanced against each other. Level up is `+levelHp` HP and
  `+levelStat` to each stat, always up.
- **Never reorder `natures`.** Save slot byte 12 held a per-monster crystal
  before this became per-species; it is **reserved** now and ignored on load,
  so old saves need no migration, but the indices are still what the baker
  emits per species.
- `natureTypes.ring` is its own order and is what decides matchups, so it does
  not have to match the array order above.
- Matchups are **derived, not stored**: each crystal is weak to the next
  `beatsAhead` around the ring and resists the previous `beatsAhead`. With 7
  crystals and `beatsAhead: 2` that is exactly 2 weaknesses, 2 resistances and
  2 neutral each, symmetric, with no blanket pick. Keep the count **odd** —
  an even ring gives some pairs mirror matchups.
- `strongMul` / `weakMul` are **2.0 / 0.5**. Neither engine hardcodes them:
  web reads `NATURE_TYPES` in `data.ts`, DC reads the baked `NATURE_*` defines
  plus the `ring` field on `NatureDef` and `nature` on `Species`.

### Bench XP / formulas

The `formulas` key in `world.json` is the combat contract. `benchXpShare` is 0.5
(lead full XP, other *living* party members get the share). Baker emits
`BENCH_XP_PCT`.

### Combat: move damage, speed, and guards

Every move (basic, special, spell, Toxic Burst) draws on exactly one raw stat
— `str` or `mag` — and multiplies it directly by the move's own `power`. No
defense term, no normalization step, no hidden scale constant:
`damage = round(atkStat * power)`, minimum 1. Speed works the same way off
`agl`: `moveSpeed` is a flat multiplier used only at the guard step, not
added to damage.

- Per species (`species.json`): `basicStat`/`basicPower`/`basicSpeed` and
  `specialStat`/`specialPower`/`specialSpeed`. Per spell (Cathleen's
  `spells[]`): `stat`/`power`/`speed`.
- `power`/`speed` are meant to sit roughly in **0.5–1.5**; the UI displays
  them ×10 (so "PWR6" means `power: 0.6`) — this is a display convention
  only, not a second multiplier applied to damage.
- What the defender eats is decided entirely at the guard step, never baked
  into the attack roll. Three guards, `logic.json`'s `combat` block:
  - **Dodge**: a speed contest, not a percentage roll. Attacker's
    `agl * moveSpeed` vs. defender's `agl * frand(dodgeDefenderRandMin,
    dodgeDefenderRandMax)`. Attacker positive → lands anyway; zero or
    negative → the defender slips aside, 0 dmg.
  - **Block**: `str * frand(guardRandMin, guardRandMax)` subtracted from the
    would-be damage. Reduces it to 0 or below → **Parried** (`parriedText`):
    the defender takes nothing and the *would-be* damage counters straight
    back at the attacker (can itself end the fight). Otherwise the leftover
    leaks through.
  - **Barrier**: same shape off `mag`. Reduces to 0 or below → **Absorbed**
    (`absorbedText`): defender takes nothing and heals
    `damage / barrierHealDivisor`. Otherwise the leftover leaks through.
  - Crystal-nature scaling (2x weak / 0.5x resist) is applied once, to the
    pre-guard damage, before any guard reduces it — same call site on both
    engines (`nature_scale_dmg()` / `natureScaleDmg()`).
- `Toxic Burst` (shiny-exclusive, `logic.json`'s `toxicBurst` block) is a
  universal move, not per-species: same `stat`/`power`/`speed` shape, plus a
  `poisonDivisor` for its ongoing chip tick.
- Both engines share one lookup for "raw stat a move draws on, mods
  included": `atk_stat_value()` (DC) / `atkStatValue()` (web). Do not
  duplicate the stat-selection branch elsewhere.

### CryDex

Not a separate file. Bitfields at save bytes **134** (seen, 4 bytes) and **138** (caught, 4 bytes), after the checksum, so old 256-byte blobs still validate. Seen on mint/encounter; caught when the player owns the species. Pause → CryDex.

### After any pack edit

Always bake. Baking is Python (`bake_content.py` **and** `gen_sprites.py`);
it does **not** need `sh-elf-gcc`. Skipping either because you cannot link a
CDI is how JSON/C and PNG/`sprites.h` drift.

```
python3 tools/bake_content.py --content content --out ports/dreamcast/src
python3 ports/dreamcast/tools/gen_sprites.py   # only if art changed
python3 tools/check_sync.py --strict           # required before you call the pack done
```

`--strict` is what catches JSON/C drift before commit. A web-only turn may drop
`--strict` (warn-only) **only if** no CDI will ship this turn; the bake must
still have run.

`ports/dreamcast/tools/bake_content.py` is a **wrapper**. Do not copy the baker.
`content_*.inc` stay generated; `make` rebuilds them. Do not hand-edit them and
do not invent a second sprite folder.

### If you do not have the Dreamcast toolchain

Grok’s sandbox and ChatGPT’s VM typically do not. That is fine.

1. Still do the bake + `check_sync` above. If art changed, that includes
   `gen_sprites.py` (Python → `sprites.h`). It is not a disc step.
2. Interpret the pack in the engine you own (web: `src/game/`).
3. Do **not** run `make` / `make cdi`. Do **not** claim a CDI. Do **not** skip
   the bake.
4. Stop. Claude builds the disc from the baked `.inc` files on the next DC turn.

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

**One art tree.** `public/sprites/`. Tools that write PNGs call
`tools/sprite_root.assert_write` and will refuse any other path.
`python3 tools/check_sync.py` fails if another directory named `sprites/`
appears outside `backups/`. Do not author in `placeholder_sprites/` —
missing art is generated in memory and listed as `PLACEHOLDER_ART`.

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

Presentation-only (do not lift): pause / save / continue UI, tile paint, input.

Landed in the pack (do not re-implement as engine-only):

- Crystal Natures (`logic.json` `natures`, party byte 12)
- CryDex (save 134/138)
- Bench XP (`formulas.benchXpShare`)
- The Reach (`maps.reach`, ruins `e` warp, `need: hasScroll`)
- Cage / Tessa / chest scripts (`world.json` npcs)
- Party release + catch-swap (`logic.json` `party`)
- Anne gift (`logic.json` `anneGift`)
- Trainer kits + win-talk + sentry key (`world.json` `trainers`)
- Mason overworld scale (`sprites.json` `drawScale.mason`)

---

## Web

```
npm run dev
npm run typecheck
python3 tools/check_sync.py
```

`src/game/data.ts` (and `logic.ts` / `audio.ts` / `save.ts`) import JSON. Web
does not need a bake **to play**. You still bake after a pack edit so the DC
`.inc` files do not drift (see “After any pack edit”).

## Dreamcast

Only Claude is expected to have `sh-elf-gcc` and `mkdcdisc`. Commands below are
from the **CryMon repo root**.

Bake (anyone, Python — no `sh-elf-gcc`):

```
python3 tools/bake_content.py --content content --out ports/dreamcast/src
python3 ports/dreamcast/tools/gen_sprites.py   # only if art changed
python3 tools/check_sync.py --strict
```

`gen_sprites.py` lives under `ports/dreamcast/tools/` because it emits
`sprites.h`, not because it is Claude-only. Run it in this bake block, not
with `make`.

Disc (Claude only, after `--strict` is green — this is the SH toolchain):

```
make -C ports/dreamcast
make -C ports/dreamcast cdi
```

No toolchain → follow “If you do not have the Dreamcast toolchain” above. Never
silently skip the bake or `gen_sprites.py`. `make` / `make cdi` are the only
steps that wait for Claude.

`content_*.inc` and `sprites.h` are generated. `MAP_*` / `SP_*` / `NATURES` /
`BENCH_XP_PCT` come from the bake — do not redefine them in `main.c`.

---

## Abandoned

Do not restore these. Snapshots are reference-only.

| Port | Snapshot |
|---|---|
| SNES / `.sfc` / 65816 | not kept |
| LÖVE2D | `backups/love-port/` |
| SDL2 / R36S PortMaster | `backups/sdl-port/` |
| Pre-fuse DC with hardcoded tables | `backups/dreamcast-pre-fuse/` |
| A second Dreamcast tree in another repo | never existed; do not create it |

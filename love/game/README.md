# CryMon — LOVE2D port

A full, faithful LOVE2D (Lua) port of CryMon, ported primarily from the
native SDL2/C build (`native/crymon.c`) and cross-checked against the
original TypeScript/canvas source (`src/game/{engine,data,types,input,audio}.ts`).

## Running it

```sh
love love/game            # from the repo root, run the loose directory
```

Or from inside `love/game/`:

```sh
love .
```

LOVE 11.x is required (tested against LOVE 11.5). The window is a fixed
640x480, non-resizable (see `conf.lua`), matching `native/crymon.c`'s
`VW`/`VH` exactly.

### Controls

- Arrow keys / WASD — move
- `Z` or `Space` — confirm / interact / attack
- `X` or `C` (or Escape) — cancel / close menu
- `Enter` — party menu
- `Tab` or `Q` — bag menu
- `1`-`6` — pick lead CryMon in the field

(Same layout as `native/crymon.c`'s scancode mapping — see also
`portmaster/crymon.gptk` for the gamepad-to-keyboard mapping used on the
R36S.)

## Layout

```
love/game/
  main.lua       -- love.load/update/draw/keypressed wiring only
  conf.lua       -- window/config
  src/
    data.lua     -- species, items, maps, dialogue tables, formulas
    state.lua    -- the whole game state machine (world/battle/talk/menus)
    render.lua   -- all drawing, reads state, never mutates it
    draw.lua     -- small rectangle/text/tile drawing primitives
    input.lua    -- keyboard polling (rising-edge + held-key helpers)
  assets/        -- intentionally empty; see "Assets" below
```

`main.lua` stays at the top level (not inside `src/`) because a `.love`
file requires `main.lua` at its root.

## Packaging as a `.love` / PortMaster zip

This repo deliberately does **not** commit a zipped `.love` file — package
it yourself (or in CI) when you need one:

```sh
cd love/game
zip -9 -r ../../crymon.love . -x '*.DS_Store'
```

That's it: a `.love` is just a zip of this directory with `main.lua` at
its root. See `love/portmaster/README.md` for the full PortMaster zip
assembly (launcher script, `port.json`, bundling a `love.aarch64`/
`love.x86_64` binary, etc).

## Assets

Both the web (`src/game/engine.ts`) and native (`native/crymon.c`)
versions load real pixel-art PNG sprites (see `public/sprites/` and
`native/gfx_blob.bin`) — the game is not actually 100% procedural at the
source level. This port draws everything procedurally instead
(`love.graphics.rectangle`/`polygon`/`print`, no image files), because:

- it keeps the port self-contained and trivially portable to Android
  (no asset pipeline, no `gfx_blob`-style packer, nothing to keep in sync
  with `public/sprites/`);
- `native/crymon.c` itself silently draws nothing whenever a sprite name
  is missing from its `gfx_blob.bin` (`blit()` is a no-op on a lookup
  miss), so a build with no art was already an anticipated, working state
  of that engine, and playability was explicitly prioritized over pixel
  fidelity in the porting brief.

If you want the real sprites later: drop PNGs into `assets/`, then adapt
`src/render.lua`'s `drawActorNamed`/`battleBlob`/prop helpers to try
`love.graphics.newImage` first and fall back to the current colored-block
rendering when an asset is absent — the state machine in `src/state.lua`
doesn't need to change at all.

`love.graphics.setDefaultFilter("nearest", "nearest")` is set in
`main.lua` so any pixel art added later stays crisp when scaled.

## Fidelity notes / known differences from `native/crymon.c`

`native/crymon.c` was the primary reference, but a few spots in it looked
like regressions relative to `src/game/engine.ts` + `data.ts`, or the two
disagreed outright. Where that happened, the choice made (and why) is
commented at the point of divergence in `src/data.lua` and `src/state.lua`.
Summary:

- **Shop (Bram's stall) is fully functional here.** `native/crymon.c`'s
  `M_SHOP` mode only *draws* prices and closes on cancel/start/select —
  there is no purchase code path at all (confirmed: no `marks -=` /
  `bag_* +=` anywhere near `M_SHOP` in crymon.c). `engine.ts` has a real
  buy/sell UI with tabs, and that's what's ported here
  (`src/state.lua`'s `updateShop`).
- **Grove door gate.** `engine.ts`/`data.ts` put a locked door tile
  mid-map in the grove, splitting Cathleen's half from Shinigami's, opened
  only once Cathleen is caught. `native/crymon.c` dropped that row from
  its `GROVE` map entirely (no gate at all). This port keeps the TS gate
  (see the comment on `data.GROVE`), since it reads as intentional pacing
  rather than a simplification crymon.c's own test harness happens to
  never exercise.
- **Shinigami win → ending.** `native/crymon.c` just prints a line and
  drops you back into free-roam after beating Shinigami/CryMare.
  `engine.ts` ends the demo on a dedicated screen (`mode = "demoEnd"`,
  `DEMO_END` text). This port follows `engine.ts` since a real ending
  sequence was in scope.
- **Finishing-blow message names the wrong move.** In `crymon.c`'s
  `apply_hit()`, the "X dmg." line always names the *basic* move
  (`spec_of(bPl.species)->basic`) even when a special attack or a Cathleen
  spell landed the finishing blow. Preserved verbatim here for fidelity to
  the tested C engine (see the comment in `applyHit` in `src/state.lua`)
  rather than silently "fixing" cosmetic text crymon.c's own author chose
  to ship that way.
- Everything else — species stats/growth curve, XP curve, capture-chance
  formula, battle damage math (basic/special/Cathleen spells/minigame),
  guard (dodge/block/barrier), soldier patrol/chase AI, Anne/Mason
  approach scripts, all dialogue text, map layouts, item effects and
  prices — matches `native/crymon.c` (and agrees with `engine.ts`/
  `data.ts` wherever compared).

## Known gaps

- **No audio.** Neither `native/crymon.c` (no `SDL_mixer` calls) nor this
  port play sound. The web build's `src/game/audio.ts` is a tiny
  procedural `AudioContext` beep synth (no sound files) — porting that to
  `love.audio`/`love.sound` generated waveforms would be straightforward
  future work but was left out to keep scope focused on gameplay parity.
- **No real sprites** — see "Assets" above; this is a deliberate,
  documented tradeoff, not an oversight.
- Animation is a simple 4-frame walk-cycle flicker + a facing wedge on a
  colored block, not the multi-frame character art the web/native builds
  use.

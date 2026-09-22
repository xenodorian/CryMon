# CURRENT_WORK.md

Live coordination doc for every agent working this repo (Claude, Grok,
ChatGPT, others). Read before starting anything; update before you stop.

**This is the only coordination file.** Do not create a second one
(`CURRENT_WORK_2.md`, `WORLD_STATE.md`, etc.) because your tool can't
edit this one — a parallel doc that other agents don't read defeats
the entire point of having a shared file, and has already caused a
real collision once (see "Patterns worth knowing" below). If your
write path genuinely can't update this file (e.g. an API that needs a
blob SHA your tool doesn't expose), say so plainly in your response to
the user and let them relay the update, or ask another agent in the
session to write it for you — don't fork the file as a workaround.

---

## World-map/naming contract

- The player-facing name of map ID `veld` is **CRYTOWN**. Do not use
  "Veld" or "the veld" in new prose, UI, docs, dialogue, or agent notes.
- The internal map ID stays `veld` for save/map-order compatibility.
  Do not rename that identifier without an explicit save-format migration.
- `content/world_map_layout.json` is the canonical abstract grid for
  the overworld (map positions, dimensions, every active warp pair
  with exact tile coordinates). The Town Map generator (see below)
  reads this as its source of truth.
- CRYTOWN ↔ HOME connection: exactly one CRYTOWN `D` at row 3, col 18,
  paired with HOME `D` at x=6,y=10. Do not remove/relocate without
  updating the world-map layout and connection checks (this broke once
  already, fixed in `1a5866b`).
- `public/maps/sorrow-county-town-map.svg` is the code-derived
  player-facing world map. Regenerate via `tools/generate-town-map.mjs`
  after any world_map_layout.json change — don't hand-edit the SVG.

---

## Standing house rules

- **Commit-and-push per step, always.** After finishing each
  individual step/sub-step (not each large multi-part item — each
  *step*), commit and push to `main`. Don't batch multiple steps into
  one commit — a session that gets cut off mid-work should only lose
  the one step in progress.
- **"Ship it" / "ship the build"** is a specific user trigger, distinct
  from the commit-per-step rule. It means: run the entire deployment
  pipeline now — `bake_content.py` → `gen_sprites.py` → `check_sync
  --strict` → web typecheck → `make -C ports/dreamcast` → `make -C
  ports/dreamcast cdi` → commit/push → let CI rebuild the CDI → confirm
  the Pages deploy re-ran (see CI note below).
- **After finishing a large milestone that includes a bug fix**, run
  that same full pipeline unprompted. Routine feature commits don't
  need this — just bug-fix milestones.
- Do not hand-replace `world.json`. Do not empty `npcs`.
- **Cathleen is the only CryMon who speaks**, unless a leg explicitly
  changes that.
- **Verification bar for every push, no exceptions:** `python3
  tools/bake_content.py --content content --out ports/dreamcast/src` →
  `python3 ports/dreamcast/tools/gen_sprites.py` → `python3
  tools/check_sync.py --strict` → `npm run typecheck` → `make -C
  ports/dreamcast`. Fetch immediately before every push — this repo
  has multiple agents pushing straight to `main` continuously; never
  trust a base fetched more than a few minutes ago.
- **Race-safe push protocol:** fetch → merge/rebase onto `origin/main`
  → resolve any generated-file (`.inc`/`.cdi`/`.elf`) conflicts by
  rebaking/rebuilding fresh, never by hand-merging binary diffs →
  rebuild → verify → fetch again right before pushing → push → confirm
  the push landed by checking `git log origin/main --oneline`.
- **Magenta-keyed art:** generate on solid magenta (`#FF00FF`), ship
  with a transparent background. Full recipe in "Magenta keying" below
  — don't skip the enclosed-hole punch or you get pink filigree gaps.
- **Not hardware-verified** applies to essentially everything touching
  `ports/dreamcast/` in this whole project — there is no Dreamcast
  emulator or real hardware in this sandbox. Every Dreamcast fix here
  is "compiles clean, logic re-derived by hand" confidence, not
  "confirmed working on screen." Treat accordingly; don't re-state this
  caveat per item going forward, it's a blanket truth.

### Magenta keying (when generating art)

Ship files with a **transparent** background — never leftover magenta,
never a solid-color plate. Order matters — the border clamp needs
holes already punched before it can color-correct their rims.

1. **Flood-from-edge key.** Chroma-key magenta connected to the image
   edge → alpha 0. Only clears the *outer* background; enclosed
   interiors (filigree gaps, ring holes) stay magenta after this alone.
2. **Punch enclosed magenta holes.** Required second pass. Walk
   leftover blobs that are majority chroma-key magenta and set them to
   alpha 0 too. Skipping this is what leaves pink inside crystal cages.
3. **Do not traditional-despill** (no 1px fringe-delete around the
   silhouette — eats into hair/outlines/gem cages). Don't use bare
   `strip_magenta.py`, it still does this legacy pass.
4. **Then** a 2px inner-border clamp: any opaque pixel within 2px of a
   transparent pixel, if `R > G`, set `R = G`. Kills the pink halo
   without eating the art.

```
python3 tools/strip_magenta.py key-clamp --size 128 --pad 24 -o DEST SRC
```

QC before commit: corners transparent, no leftover `#FF00FF` anywhere
(silhouette or interior cutouts), no magenta halo, interior colors
untouched.

---

## CI pipeline

`GITHUB_TOKEN` pushes can't re-trigger other workflows (GitHub loop
guard) — closed via: after a successful CDI commit+push in
`build-dreamcast.yml`, a step runs `gh workflow run deploy-pages.yml`
with `permissions: actions: write`. If deploy-pages ever fails to
start, check the Build Dreamcast CDI job log's "Trigger Pages deploy"
step and the Actions tab for a queued Deploy CryMon Web run.

---

## Current save format (binary blob, 256 bytes, v6)

Shared by `content/save.json` (source of truth), `src/game/save.ts`
(web), `ports/dreamcast/src/save.c` (Dreamcast). **Never fork this
layout between engines — both pack/unpack the identical byte offsets.**

| field | offset | size |
|---|---|---|
| magic | 0 | 4 |
| version | 4 | 1 |
| mapId | 5 | 1 |
| dir | 6 | 1 |
| partyCount | 7 | 1 |
| x, y | 8, 10 | 2, 2 |
| marks | 12 | 2 |
| partyIndex | 14 | 1 |
| battlesDone | 15 | 1 |
| mason2Map | 16 | 1 |
| reputation | 17 | 1 (stored as value+100, 0..200) |
| bag | 18 | 19 (one byte per item in `itemOrder`) |
| flags | 37 | 8 (62 of 64 bits used — 2 free) |
| party | 45 | 96 (6 × 16-byte slots) |
| checksum | 141 | 2 (covers bytes 0..140) |
| dexSeen | 143 | 4 |
| dexCaught | 147 | 4 |
| executedMask | 151 | 4 |
| party2 | 155 | 96 (Father's 6-slot party) |
| activeParty | 251 | 1 (0=Max, 1=Father) |
| party2Count | 252 | 1 |

Free bytes: 253-255 (3 spare). Each 16-byte party slot: bytes 0-9
species/lv/hp/maxHp/str/agl/spc/spp/sppMax/shiny, 10-11 xp, 12 nature,
13-15 status/statusTurns/poisonStack.

**Both engines reject a save whose byte 4 ≠ `SAVE_VERSION`**, treating
it as absent rather than partially loading it. Growing `bag` is the
usual trigger for a version bump (no spare padding there) — shifts
everything after it. Adding a **flag** (2 bits still free) or reusing
already-zeroed padding (like the status bytes above) needs no bump.
`world.mapIds` order must equal `save.mapOrder` order exactly
(append-only) — that order also drives every `MAP_*` enum on Dreamcast
and the numeric mapId byte in a save, so **never reorder or remove an
entry from the middle of `mapIds`** without a full save-format
migration; there's a legacy unreachable `"gauntlet"` (singular) map
entry left in on purpose for exactly this reason — don't "clean it up"
by deleting it from `mapIds`.

---

## Patterns worth knowing (recurring gotchas)

- **The Dreamcast `wsoldier`/`pending` trainer-battle path is NOT
  generic.** Every new trainer needs, by hand, in `main.c`:
  `TRAINER_WSOLDIER_*` and `POST_WSOLDIER_*` `#define`s, an
  `NPC_PENDING_*` dispatch case, a battle-setup `case`, and the usual
  5 save-flag touch points (var decl, `ft[]` table, load, reset,
  store). Web (`engine.ts`) *is* generic off `TRAINERS`/`worldJson`.
- **`#define` numbering collisions are real and have happened twice.**
  Multiple agents editing `main.c` concurrently have independently
  picked the same next-free number for a new `POST_*`/`TRAINER_*`
  constant more than once, breaking the build with "duplicate case
  value." Before adding one, `grep -n "#define POST_\|#define
  TRAINER_WSOLDIER_"` and pick a number past the current max, then
  rebuild immediately to catch a collision before pushing.
- `tools/bake_content.py` keeps **three separate hand-maintained
  lists** that must agree for any new `wsoldier`-style trainer:
  `kit_keys`, `PENDING_IDS` (Python dict), and the hand-written
  `#define NPC_PENDING_*` lines. Missing one either crashes bake or
  silently no-ops the battle dispatch.
- New map checklist (`check_sync --strict` enforces all of it):
  `content/maps.json` rows, `content/world.json` `mapIds`+`mapNames`,
  `content/save.json` `mapOrder` (byte-identical order to `mapIds`),
  `src/game/types.ts` `MapId` union, `src/game/data.ts` map export +
  `MAPS` entry (this last one is easy to forget — it's silently
  additive, `this.map()` just returns `undefined` for the missing
  entry instead of erroring). `MAP_*`'s Dreamcast define bakes free.
- A `world.json` npc script step needs an explicit `"after":
  "wsoldier"` (or whichever `after` code applies) to actually trigger
  anything — a step with only `"pending"` set does nothing. This bug
  has bitten Lieutenant Lead's and (partially) Heavenfall's grave
  battle triggers already; check for it whenever a new trainer's
  battle "isn't starting."
- **Corrupted PNG signature to watch for:** valid PNG header + `IEND`
  trailer, but broken IDAT stream — PIL raises `OSError: broken data
  stream`, crashes `gen_sprites.py` for everyone until removed. Has
  happened from GitHub's file-API silently truncating large binary
  pushes. Verify new art PNGs actually open before relying on them.
- `dialogue.json`'s `endingWin` is a **hardcoded single key** in
  `bake_content.py`, not the generic talk table — don't rename/delete
  it without updating the baker in the same commit.

---

## Legs 1 & 2 — status: complete except one open item

Both legs (starting town/dialogue/maps/monsters/NPCs through the full
Leg 2 feature list — capture-rate tiers, reputation stat + father's
second party, mercy/threaten/execute, secondary-move overhaul with
real status conditions, the Leg 2 wrap gate) are **done and pushed on
both engines.** Full implementation history is in git log if archaeology
is ever needed (`git log --grep "Leg 2"`); condensed to what still
matters going forward:

- **Art debt: fully cleared.** `check_sync --strict` reports zero
  missing sprites. `ports/dreamcast/ART_NEEDED.md` no longer exists.
- **Level cap is 100.** Heavenfall-path party wipe is a real Game Over
  (narrative → red fade/scream → reload-or-title), not a soft trip
  home. Lieutenant Lead blocks the (currently wall-bounded, so
  trivially blocked) north exit from CryTown; beating him is a
  placeholder "thank you for playing" → same Game Over flow.
- **Dreamcast's Game Over deliberately diverges from web:** web
  silently auto-reloads the last save in place; Dreamcast drops to the
  title screen with Continue enabled if a save exists, reusing the
  existing well-tested Continue flow instead of duplicating its
  load-into-live-state logic inline. Intentional simplification, not
  a bug.
- **Only open item: 2.8's live trigger.** The Heavenfall-revival
  reputation effect (-25 rep + one-time merchant warning) is fully
  data-ready (`logic.json`, save flag, dialogue line) and reportedly
  wired by another agent's in-flight work, but as of the last check
  here the gauntlet-grave Heavenfall battle itself wasn't yet
  triggering reliably on both engines — verify before assuming this
  is closed.
- Dreamcast title-display (`apply_player_name()`) now correctly shows
  "Heaven Slayer"/"Heaven Tamer" and persists them across save/reload,
  matching web's precedence exactly (Slayer > Tamer > revived/kindName
  > "Max"). New-Game reset also correctly clears
  `beat_heavenfall`/`heavenfall_rep_warned`/`gauntlet_unlocked`/
  `title_slayer`/`title_tamer` now (previously leaked across a second
  playthrough in the same session, same class of bug as an earlier
  `reputation` New-Game leak).

---

## World Graph / Town Map workstream — validation hardening done (Claude, 2026-09-22)

Goal: the Town Map (player-facing region map) should be a **generated
projection** of `content/world_map_layout.json`, never a second source
of truth hand-maintained separately from it.

**Architecture:**
```
World Data (world_map_layout.json)
    → World Graph (connectivity, reachability)
    → Validation Suite
    → Town Map Projection (content/town_map.json)
    → Rendered Region Map (SVG + in-game Map screen)
```

**What exists now:**
- `tools/generate-town-map.mjs` — generator: writes `content/town_map.json`
  (runtime data for web's Pause→Map screen), the player-facing SVG at
  `public/maps/sorrow-county-town-map.svg`, and a developer markdown
  dump at `docs/generated/sorrow-county-town-map.md`. Re-run after any
  world-layout change: `node tools/generate-town-map.mjs`.
- Web: Pause menu's **Map** option opens `townmap` mode, draws the
  region graph, and highlights the player's current location.
- `tools/world_graph/` — a separate Python validation layer, read-only
  (does not generate anything, only checks):
  - `validate_world_graph.py` — connectivity/reachability against
    `world_map_layout.json` (missing map refs, unreachable active maps).
  - `validate_town_projection.py` — checks the town-map projection
    itself (missing representations, invalid collapse targets, orphan
    nodes, unreachable projected regions, route dead ends).
  - `validate_progression_requirements.py` +
    `progression_flags.json` — validates that map-progression gates
    referenced in the world graph (`beatCalder`, `beatShin`,
    `hasScroll`, `choseHeavenfall`) are real, known flags, meant to
    become the single canonical list so validators stop each
    maintaining their own hardcoded copy.
  - `README.md` — one-paragraph purpose summary for the above.
  - `run_full_audit.py` — runs the generator + all 3 validators in
    order and writes one consolidated report to
    `docs/generated/sorrow_county_validation_report.md`. Re-run this
    after any world-layout or Town Map change: `python3
    tools/world_graph/run_full_audit.py`.

**Conclusion from the review:** the project does **not** need a new
Town Map generator — `generate-town-map.mjs` already produces a
correct projection (CryTown anchor, Camp/Forest/Cliffs/Quarry branches,
Gauntlet route, Heavenfall Shrine endpoint all confirmed present), and
it already guards against the two things a hand-maintained map could
get wrong (an "Unreachable: X" / "Isolated: X" build-time error if a
new map lands with no connection, or none at all). Hardening was
validation-layer work, not generator work — **done:**

1. **Done.** `validate_progression_requirements.py` now reads
   `tools/world_graph/progression_flags.json` as its source of truth
   instead of a hardcoded set, and reports unknown requirements
   (error), duplicate flag ids (error), and registry flags that don't
   gate any Town Map edge (warning only — a flag can legitimately gate
   a battle/dialogue beat without gating a map route, so this doesn't
   fail the run).
2. **Done.** `run_full_audit.py` chains generate → validate world
   graph → validate projection → validate progression into one
   `docs/generated/sorrow_county_validation_report.md`. Current status:
   **PASS**, zero errors, zero warnings.
3. **Found and fixed a real bug** while verifying item 2's report:
   `validate_town_projection.py` was checking whether a Town Map node
   was a collapse **source** (`collapse.keys()`) when it should check
   collapse **target** (`collapse.values()`) — `gauntlet_route` and
   `heavenfall_shrine` are synthetic regions other maps collapse
   *into*, never map ids or collapse keys themselves, so the old logic
   false-flagged both of them every run. Fixed and verified against a
   deliberately-injected bogus node to confirm real orphans are still
   caught (they are — 3 separate checks still fire correctly).

Nothing else queued here right now — this workstream is caught up.
Re-run `run_full_audit.py` after any future world/Town Map edit to
keep the report current.

**Grove's exits corrected: Gauntlet south, Ruins east (Claude,
2026-09-22).** The Gauntlet warp was already `dir: "down"` (correct),
but the Town Map's Ruins warp was also `"down"`, and Ruins/Gauntlet
were only disambiguated by a hardcoded SEED override in
`generate-town-map.mjs` that placed Gauntlet west — cosmetic, not
geographically accurate, and didn't match the real tile layout either
(Grove's Gauntlet gate `G` sat near the west wall, not south-center).
Fixed for real, not just relabeled:
- **`content/maps.json`:** Grove's `G` (gauntlet gate) moved to
  south-center (was near the west wall); Grove's `g` (ruins gate)
  moved to the east wall (was south-center, swapped with `G`'s old
  spot). Ruins' `D` (arrival-from-grove door) moved from its north
  wall to its west wall.
- **`content/world.json`:** grove→ruins warp is now `dir: "right"` /
  `ox: 40` (was `down`/`oy: 40`); the reverse ruins→grove warp is now
  `dir: "left"` / `ox: -32`.
- **First east/west warp this codebase has ever had** — every other
  warp is vertical (`up`/`down` + a Y offset). Required real engine
  work, not just data: `warpTo()` (web) gained an `xOff` param and the
  locked-door push-back nudge gained `left`/`right` branches;
  Dreamcast's `WarpDef.face_down` (a binary down/up flag) became
  `WarpDef.dir` (0..3, all four directions), `do_warp()` was rewritten
  to compute px/py and facing for any direction instead of only Y, and
  its own locked-door nudge got the same left/right branches. Verified
  against a real clean rebuild on both engines (typecheck, `npm run
  build`, `make -C ports/dreamcast`) — no new warnings.
- **`content/world_map_layout.json`:** connection direction/coordinates
  and the (currently tooling-only, not read by the live generator)
  `grid`/`worldBox` reference fields updated for Ruins/Gauntlet1-6 to
  match.
- **`tools/generate-town-map.mjs`'s `SEED` table** updated to match —
  this is what actually controls the rendered Town Map layout (the
  `world_map_layout.json` `grid`/`worldBox` fields are unused by it).
  Verified by regenerating and rendering the SVG: Gauntlet now sits
  directly south of the Grove, Ruins directly east.
- `check_sync --strict`, typecheck, web build, and `make -C
  ports/dreamcast` all clean.

**Town Map rendering fixed: plain routes are now the road, not a box
(Claude, 2026-09-22).** User flagged (with FireRed screenshots) that
every node — real landmarks AND plain connective routes — was drawn as
a discrete box/diamond joined by thin lines, making routes look like
disconnected "phantom" stops instead of the road itself. FireRed's Town
Map only puts a marker on true landmarks and cave/dungeon entrances;
a plain route is just the continuous tan path with a label on it.
Fixed in both renderers (they must stay in sync, same three-tier logic):
- **`tools/generate-town-map.mjs`** (SVG generator) and
  **`src/game/engine.ts`'s `drawTownMap()`** (in-game Pause→Map canvas)
  both now branch on `gem`/`kind` into three tiers instead of two:
  - `gem:true` (veld/CryTown, camp, heavenfall_shrine) → unchanged
    diamond-on-circle landmark marker.
  - `kind:"cave"` or `kind:"gauntlet"` (quarry, gauntlet_route) → new
    small dot marker (no box) — a point of interest sitting on the
    road, not a destination town.
  - everything else (`kind:"route"`, `gem:false` — forest, grove,
    cliffs, marsh, ruins, reach) → **no marker at all**, just the
    label sitting directly on the connecting road (SVG label gets a
    stroked halo for legibility over the tan path).
- Developer markdown legend (`docs/generated/sorrow-county-town-map.md`)
  updated to a matching 💎/●/· three-symbol legend.
- No `content/town_map.json` schema change (`kind` field already
  existed on every node) — this is a pure rendering fix, both
  renderers read data that was already there.
- Regenerated Town Map, re-ran `run_full_audit.py` (PASS), rendered
  the new SVG via headless Chromium and visually confirmed it now
  reads as a continuous path with landmark/POI markers only, matching
  the FireRed reference the user provided.
- `check_sync --strict`, typecheck, and web build all clean. No
  Dreamcast rebuild needed — `main.c` and baked `.inc` content
  untouched (`town_map.json` is web-only runtime data, not baked).

**Town Map follow-up: Gauntlet is a route, Quarry's marker isn't beige
(Claude, 2026-09-22).** User corrected the previous fix on two points:
- **Gauntlet is a route, not a location.** `REGION_META.gauntlet_route`
  changed from `kind: "gauntlet"` to `kind: "route"` — it now renders
  exactly like Forest/Grove/Cliffs/etc: no marker, just a label on the
  path. There is no `kind: "gauntlet"` left anywhere; the POI-dot tier
  is now driven solely by `kind === "cave"` (currently only Quarry).
- **No beige dots.** The small location-dot marker (for cave entrances)
  was `#8a7a55` — the same tan family as the road, so it read as part
  of the path rather than a distinct marker. Changed to stone-gray
  (`#5a5a52` fill / `#2a2a24` stroke) in both
  `tools/generate-town-map.mjs` and `src/game/engine.ts`'s
  `drawTownMap()`.
- Regenerated, re-ran `run_full_audit.py` (PASS), rendered and
  confirmed: Gauntlet is now a bare label on the Grove→Heavenfall
  road, Quarry keeps a dark gray dot (not beige).
- `check_sync --strict`, typecheck, web build clean. No Dreamcast
  rebuild needed (same reason as above).

---

## Leg 3 (open — from the user's doc)

**Do not start before Leg 2's gauntlet/reputation work is fully
confirmed working** — Leg 3 depends on `reputation` and the gauntlet
existing and behaving correctly.

New content: liberating cities from occupying Weeping Army soldiers,
building to a final confrontation with their king.

### 3.1 — Shackles item + Weeping Generals
- New item, **Shackles**, sold at every merchant except the first one.
  Required to challenge Weeping Generals.
- Populate newly-added liberation cities (new maps/NPCs, not yet
  designed) with one individually-named **Weeping General** each.

### 3.2 — Arrest or execute each Weeping General
- **Arrest** (requires Shackles): `+10` reputation.
- **Execute:** `-25` reputation.

### 3.3 — Golden Shackles + Weeping King Nero
Defeating **all** Weeping Generals unlocks the **Golden Shackles**,
which lets the player confront **Weeping King Nero**.

### 3.4 — King Nero's fate branches the ending
- **"Bring Him To Trial"** (Golden Shackles arrest): `+50` reputation,
  war-crimes trial + life-sentence cutscene.
- **Execute:** `-50` reputation, red fade, scream plays **3 times**,
  then a **persistent red tint stays on screen for the rest of the
  playthrough**. Player renamed **"Kingslayer"** everywhere. Cutscene:
  player crowned the new Queen.

### 3.5 — Father's reaction (only if revived per 2.7)
- Positive rep + arrested king: father congratulates the player.
- Negative rep + tried king anyway: father talks "necessary sacrifice."
- Executed king: father calls the player a monster and abandons them.

### 3.6 — Heavenfall's final resolution ends the game
- No Heavenfall in party: game ends here, full stop.
- Has Heavenfall + positive rep: tamed epilogue, stays by the player's side.
- Has Heavenfall + negative rep: turns hostile, attacks immediately,
  no rest.
  - Player wins: epilogue, renamed **"Godslayer"**.
  - Player wiped: epilogue, player **dies**, renamed posthumously
    **"Max The Bloody"**.
- Whichever branch fires, the game ends once it resolves.

---

## Party2 (Father) data model — decided, landed

Independent `party2[6]` + `activeParty` (0=Max, 1=Father), not a
generalized multi-party array — keeps every existing `party` call site
working; the swap UI just toggles which array battles/menus use. See
save-format table above for byte offsets.

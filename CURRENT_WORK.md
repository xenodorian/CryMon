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

### 3.1 — Weeping Generals, military bases, and medal progression
- Each **Weeping General** is housed indoors inside a military base in
  one of the liberation cities.
- Reaching a General is structured like a **Pokémon Gym**: the player
  must fight through soldiers who are trying to stop them from entering
  the restricted military facility. These encounters replace the
  traditional Gym Trainer role.
- Each General is individually named and has their own military base.
- Defeating a General awards one of their **actual military medals**.
  These are not symbolic badges created for the player to display as
  proof of progress. They are real military decorations such as the
  **Purple Heart, Medal of Honor, Distinguished Service Cross, Prisoner
  of War Medal, Gold Star, Silver Star, Bronze Star**, and others.
- The player must possess one General's medal before they can challenge
  another General. This is the progression gate between General
  encounters.

### 3.2 — Arrest or execute each Weeping General
- The former requirement to purchase **Shackles** before confronting a
  General is removed.
- **Shackles** are still sold at every merchant except the first one,
  but they now determine whether the player can **arrest** a General.
- If the player has Shackles, they are presented with the choice to
  **arrest** or **execute** the defeated General.
- **Arrest** (requires Shackles): `+10` reputation.
- **Execute:** `-25` reputation.
- If the player did not purchase Shackles because they do not intend to
  arrest the General, **execute is the only option presented**.

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

### Town Map gem/route split (Grok, 2026-09-21; corrected Claude, 2026-09-22)

Destinations (💎 only): CryTown, Camp, Grove, Reach, Heavenfall Shrine,
**Quarry**. Routes (corridor only, no marker): Forest, Cliffs, Marsh,
Ruins, Gauntlet.

The 2026-09-21 rewrite of `generate-town-map.mjs` (procedural tile
terrain) reset `REGION_META.quarry` to `kind:"route", gem:false` —
this silently undid an explicit user correction from earlier the same
day ("the quarry is a location, not a route; the gauntlet is meant to
be a route, not a location"). Restored: `quarry: { kind: "cave", gem:
true }`. Gauntlet was already correctly `kind:"route", gem:false` in
the rewrite — no change needed there. **If you touch `REGION_META`
again, re-read this note first** — Quarry=location/gem,
Gauntlet=route/no-marker is a standing, explicit user requirement, not
a stylistic default to rebalance.

SVG + in-game Map: thick beige roads on land, gems only on destinations.

### Town Map tile pipeline (Grok, 2026-09-21)

Procedural terrain grid in `town_map.json` (v2): water/land/biomes + road carve.
Tile-based SVG + in-game Map render; pixel dither on forest/marsh/cliff.
See `docs/generated/town-map-tile-pipeline.md`.

---

## Town Map action plan: routes must be real map shapes, not phantom
## connectors (Claude, 2026-09-22) — PLANNED, NOT STARTED

### The actual problem (user-confirmed diagnosis)

In FireRed, a Route is a real, separate playable map — same as a town
— and the Town Map's tan path for "Route 1" is a spatially faithful
sketch of *that specific map's* real shape/length/bends. Walking the
paper-map path and walking the in-game route are the same journey.

CryMon's routes (`forest`, `cliffs`, `marsh`, `ruins`, `reach`,
`gauntlet1..5`) are *also* real separate maps in `content/maps.json`
— that part already matches FireRed. But `generate-town-map.mjs`
never reads that real geometry. Every region (landmark or route
alike) collapses to a single abstract `(x, y)` integer coordinate on
the `SEED`/BFS layout grid, and the "path" between two route dots is
synthesized by `carveRoad()` — a Bresenham line stamped with generic
road tiles on a synthetic terrain grid. It has zero data lineage back
to the route's real tile layout. Two fixes so far (no boxes on
routes, no beige dots, Quarry-as-location) only changed how the fake
connector *looks* — they didn't stop it from being fake. The line
between CryTown and Cliffs still doesn't know Cliffs is 18×12 tiles,
still doesn't know which edge of Cliffs actually borders CryTown.

### Real data that already exists to fix this (verified, not assumed)

- **`content/maps.json`'s `rows[mapId]`** — the actual ASCII tile grid
  for every real map, `forest`/`cliffs`/`marsh`/`ruins`/`reach`/
  `gauntlet1..6`/etc included. Confirmed dimensions match
  `world_map_layout.json` exactly for every route (e.g. forest
  26×20, cliffs 18×12, marsh 18×13, ruins 20×13, reach 20×16,
  gauntlet1-5 16×36 each, gauntlet6 16×20, quarry 16×13).
  `maps.json.solid` (`#HWRBC^NErUSX%k`) is the legend of which tile
  chars block walking — enough to derive a walkable-vs-wall mask per
  route without new data.
- **`content/world.json`'s `warps[]`** — each entry has a `tile`
  marker char (e.g. `{from:"veld", tile:"Z", to:"forest",
  spawn:"Y", dir:"down"}`). Scanning `rows[mapId]` for that char
  (same technique `main.c`'s `find_mark()` already uses) gives the
  **exact real tile coordinate** of the door on both sides of every
  connection — i.e., real entry/exit points, not a guessed
  up/down/left/right label.
- **`world_map_layout.json`'s `maps[id].width/height`** — real
  dimensions, redundant with `rows` but useful as a cheap cross-check.

So the raw material to derive a real route shape (footprint +
orientation + the two real anchor points it must touch) already
exists in the content pack. Nothing needs to be added to JSON before
this can be built — this is a generator/renderer rewrite, not a
content-authoring task.

### Proposed phases (sequential, each independently committable/
### verifiable — do not batch into one giant patch)

**Phase 0 — Audit, read-only.** For every id currently `kind:"route"`
in `REGION_META` (forest, cliffs, marsh, ruins, reach,
gauntlet_route), confirm it has: real `rows[id]` data, real
`width/height`, and at least one warp with a real `tile` marker on
each side that connects it to its neighbors. Note exceptions:
`gauntlet_route` is a `COLLAPSE` target for **five** chained real
maps (`gauntlet1..5`), not one map — decide whether to stitch all
five shapes end-to-end (most accurate) or represent it as one
simplified elongated corridor sized as their combined length
(cheaper, still real-data-derived). Output: a short findings note
appended here, no code changes.

**Phase 1 — Shape extraction (pure function, testable in isolation).**
Add a `extractRouteShape(mapId)` step to `generate-town-map.mjs` that:
  1. Loads `rows[mapId]` and `maps.json.solid`.
  2. Downsamples into a coarse walkable/blocked mask (bucket every
     N real tiles into 1 Town-Map cell — N picked so the *longest*
     route still reads as a distinct silhouette at Town Map scale,
     not so fine it's noisy, not so coarse it's a blob).
  3. For each warp touching `mapId`, scans `rows[mapId]` for the
     `tile` char to get the real (col,row) of that door, and records
     which neighbor it connects to and which edge of the map it sits
     on (the door's position relative to the map's bounding box).
  Output: `{ id, maskCells: [[x,y],...], anchors: {neighborId: {col,row}} }`
  per route. No rendering changes yet — dump this as JSON and
  visually sanity-check a couple of routes (e.g. print Forest's mask
  next to its ASCII `rows` and confirm the silhouette matches by eye)
  before wiring it into layout.

**Phase 2 — Replace point-placement for routes only.** Landmarks
(`gem:true`) keep the existing SEED/BFS single-point placement — they
really are single pins, this isn't broken for them. For routes,
stop assigning a single abstract `(x,y)`; instead anchor the route's
extracted shape (Phase 1 output) so its two real doors line up with
the real positions of the landmark/route nodes on either side of it,
scaled to fit the layout grid's spacing. This is the structurally
hard part — the current SEED grid has ~1 unit of spacing between
adjacent nodes, nowhere near enough room to host a proportional
26×20 shape; the grid spacing/units likely need to scale up
alongside this change (e.g. move from "1 grid cell = 1 abstract
node slot" to "1 grid cell = N real tiles", consistent across all
routes so relative lengths stay meaningful).

**Phase 3 — Schema.** Bump `content/town_map.json` to v3. Add real
per-route shape data (a cell list or simplified polygon per route
edge) generated once by the Phase 1/2 pipeline. Both renderers must
read this shared field — neither should re-derive or re-guess a
shape independently, to avoid the SVG and in-game map drifting apart
again (which is exactly how the current phantom-line duplication
happened in the first place).

**Phase 4 — Rendering.** Replace `carveRoad()`'s synthetic
Bresenham-line-plus-generic-tile-stamp with: trace the real shape
data from Phase 3 directly onto the terrain grid (SVG generator) and
canvas (`engine.ts`'s `drawTownMap()`). The route's drawn shape
should now be recognizably derived from its actual level geometry —
long winding routes look long and winding, short routes look short,
an L-bend in the real map shows up as a bend on the Town Map.

**Phase 5 — Validation.** Add a check (either inline in the
generator's existing `errors[]` array, or a new
`tools/world_graph/validate_*` script) that fails loudly — not a
silent fallback to a straight line — if a route claimed as
`kind:"route"` is missing `rows`/`width`/`height` data, or if its
extracted shape doesn't actually reach the real anchor tile for one
of its declared connections. This is meant to catch future content
edits (e.g. someone resizes Forest's map or moves its door) that
would silently desync the Town Map from the real level again.

**Phase 6 — Regenerate, verify, ship.** Full verification bar
(`check_sync --strict`, typecheck, web build; Dreamcast rebuild only
if this ends up touching baked content, which it currently doesn't —
`town_map.json` stays web-only runtime data). Render via headless
Chromium, compare by eye against the FireRed reference the user
supplied, confirm each route's Town Map shape plausibly resembles
its real `rows[id]` layout. Commit per phase, not as one commit —
per the standing house rule.

### Open design questions — DECIDED (user, 2026-09-22)

- **Fidelity target: simplified ribbon.** Not a tile-for-tile
  silhouette. The extracted shape from Phase 1 gets reduced to a
  ribbon/polyline that captures the real map's length, bend count,
  and orientation — not literal wall-by-wall noise. Matches FireRed's
  own Town Map, which is also a simplification.
- **Gauntlet's 5-map chain: one simplified corridor**, sized to the
  combined length of `gauntlet1..5` (all real 16×36 maps chained
  north-south) rather than stitching five separate ribbon segments.
  Phase 0/1 should sum their real lengths along the chain's actual
  connection order and treat that as a single route shape input.
- **Scale/spacing rework: confirmed, in scope.** The whole map is
  expected to visually re-lay-out, not just routes — every node
  (landmarks included) moves to whatever spacing the real,
  proportionally-scaled route ribbons require. This is not a
  regression to avoid; it's the intended outcome of grounding the
  layout in real map geometry instead of an arbitrary 1-unit grid.

All three questions are now settled. Phase 2 can proceed without a
further check-in on these specific points; a visual check-in after
Phase 2's re-layout lands is still worthwhile (see Phase 2/3 in the
plan above) since "everything moves" is hard to fully predict without
seeing it rendered.

### Status: IMPLEMENTED (Claude, 2026-09-22)

Real routes were genuinely too short/square to read as Pokémon-style
routes, so before the generator work, the four real route maps in
`content/maps.json` were physically elongated (their actual walkable
tile grids, not just the Town Map projection):
- `forest` 26x20 -> 26x32, `cliffs` 18x12 -> 18x20, `marsh` 18x13 ->
  18x21, `ruins` 20x13 -> 20x19. `world_map_layout.json`'s
  width/height updated to match.
- Done by duplicating existing filler-pattern rows (forest/marsh
  already had a clean repeating tree/path motif; cliffs/ruins got
  extra floor-corridor rows inserted between existing chambers) —
  every trainer/NPC/warp is referenced purely by its mark character
  (scanned dynamically at runtime, confirmed via `grep` across
  `world.json`/`main.c`/`engine.ts` — nothing hardcodes row/col), so
  no entity coordinates needed updating, only the grids themselves.
  Verified every warp/mark character still appears exactly once per
  map after the edit before moving on.
- **Gauntlet's own maps were explicitly left untouched** per the
  user's instruction — they were already right.

Then `tools/generate-town-map.mjs` was rewritten for real (previously
it had drifted: the actual live `content/town_map.json`/SVG were
produced by a one-off Python script embedded directly in
`.github/workflows/town-map-v4.yml`, never ported back into the
checked-in generator — running the documented `node
tools/generate-town-map.mjs` command silently regenerated the OLD v2
procedural-terrain data and would have destroyed the v4 work; this
was caught and reverted before committing, see the note below). The
new generator:
- Sizes each region's Town Map cell proportionally to its **real**
  tile dimensions from `content/maps.json`'s `rows[id]` (not the
  partly-inert `world_map_layout.json` width/height, though those are
  now kept in sync too), scaled 1 cell : 10 real tiles.
- Fixed the Camp/Forest overlap bug found in the v4 workflow script:
  its rectangle packer only tried different x-offsets within the
  immediate row below a parent, and silently fell back to an occupied
  slot when that whole row was already taken (both Camp and Forest
  compute as veld's "south" exit by real door position). Replaced
  with an expanding-ring free-space search that guarantees no overlap.
- Gauntlet stays the single combined-length corridor (not five
  stitched segments) per the earlier decision — now 18 cells tall
  (real 180 tiles / 10), and its label is drawn at the **vertical
  middle** of that corridor instead of pinned to the top edge, per
  request.
- Restored real biome-colored terrain (route cells get a lighter path
  stripe down their long axis) instead of the flat tan blocks the
  workflow script produced.
- `src/game/engine.ts`'s `drawTownMap()` (in-game Pause->Map screen)
  and `src/game/data.ts`'s `TOWN_MAP` type were rewritten to match —
  the old code read `terrain.tiles` (a full procedural tile grid) which
  the new schema doesn't produce; it now draws proportional cells
  directly, same visual language as the SVG.
- Removed the stray duplicate `public/maps/sorrow-county-town-map-preview.png`
  and regenerated the canonical `.png` to match the new SVG (was stale,
  nothing in code referenced either PNG).

**Standing gotcha for whoever touches this next:** the leftover
`.github/workflows/town-map-*.yml`/`restore-mjs.yml`/`publish-map-png.yml`
files and `tools/_gen_parts/*.txt` scratch files are from that
workflow-based detour and are not part of the real pipeline anymore —
`tools/generate-town-map.mjs` is the source of truth again. Don't run
Town Map changes through a one-off workflow script; edit the real
generator and commit it, the same as any other tool.

Verified: `check_sync --strict` green, `npm run typecheck` clean,
`npm run build` clean, `make -C ports/dreamcast` clean (only the
known baseline warning set), `run_full_audit.py` PASS, rendered SVG
visually confirmed (no overlaps, Gauntlet's long corridor and label
centering both correct, all four routes visibly longer/thinner now).

**Flat-beige cells, gems only get color (Claude, 2026-09-22).** User
flagged that the per-kind biome colors and the route "path stripe"
implied a specific correct sub-path through a cell that isn't real —
the cell is a simplified proportional footprint, not a tile-traced
route, so a lighter stripe down the middle reads as "walk here" when
that's not meaningfully truer than any other point in the cell. Fixed
in both `tools/generate-town-map.mjs` and `engine.ts`'s
`drawTownMap()`: every cell is now the same flat beige
(`#d4c49a`/`#8a7a55` stroke), no kind-based fill, no path stripe. Gem
markers brightened to a more strikingly saturated blue (`#29b6ff`
diamond on a `#0a2f52` backing) so they read as the only meaningful
color on the map.

Also explained (not changed, per request): Quarry's box visually
sits astride the CryTown/Camp seam because Quarry's real door exits
Cliffs near a point that, projected onto the county grid, lands
inside CryTown's own box (CryTown sits directly west of Cliffs and
already owns that space) — the collision-avoiding placement search
pushes Quarry to the nearest fully free cell, which happens to be the
small gap above where Camp and CryTown meet. Not a bug to fix per the
user, just asked to explain it; explanation given, no code changed
for this part.

**Labels moved inside their own cell, except Gauntlet (Claude,
2026-09-22).** Every non-Gauntlet label was pinned just above its
box's top edge, spilling out of the rectangle it names. Moved inside
the top of the box (`generate-town-map.mjs`: `oy+(M+b.y)*CELL+9`;
`engine.ts`: `y+Math.max(4, cell*0.5)`, proportional since the
in-game panel's cell size is much smaller than the SVG's fixed 26px).
Gauntlet's label is untouched — it already sits correctly centered in
the middle of its long corridor.

**Rewired east chain: CryTown -> Cliffs -> Marsh -> Quarry -> Camp
(Claude, 2026-09-22).** Previously Camp hung directly off CryTown
(south, gated by `beatCalder`), Marsh hung off Forest (south), and
Quarry hung off Cliffs (south) — three separate short branches, not
a path. User wanted a single linear route east of CryTown through
all three, terminating at Camp. Real warp/door surgery, not just
Town Map relabeling:
- **`content/maps.json`**: added new east/west door tiles to each of
  `cliffs` (`L`, east wall), `marsh` (`G` west / `X` east), `quarry`
  (`G` west / `J` east), `camp` (`L` west); removed the old
  now-unused south/north doors (`cliffs`'s `q`, `marsh`'s `Y`,
  `quarry`'s old `D`, `camp`'s old `D`) so no phantom door graphic is
  left with nothing behind it. Verified every warp/mark character
  still appears exactly once per map afterward.
- **IMPORTANT PROCESS NOTE:** `content/world.json` is a **generated**
  file — `tools/merge_world.py` assembles it from
  `content/world_parts/*.json` (its own header says so:
  "Agents edit only their part file, then run this. Do not
  hand-edit world.json."). This wasn't written down anywhere in this
  doc before now and I initially hand-edited `world.json` directly
  out of habit before catching it — fixed by applying the same warp
  changes to `content/world_parts/warps.json` and re-running
  `python3 tools/merge_world.py` to regenerate `world.json`
  canonically. **If you're about to hand-edit `content/world.json`,
  don't — edit the matching file in `content/world_parts/` and run
  `merge_world.py`, or your change is at risk of being silently
  clobbered next time someone else runs it.**
- New warps: `cliffs<->marsh`, `marsh<->quarry`, `quarry<->camp`, all
  `dir:"right"`/`dir:"left"` (the `ox:40`/`ox:-32` convention from
  the Grove/Ruins east-west warp work earlier this session). The
  `need:"beatCalder"`/`failTalk:"campLocked"` gate moved from the old
  `veld->camp` warp onto the new `quarry->camp` warp — Camp is still
  gated behind beating Calder, just reached through the chain now.
  Old `veld<->camp`, `forest<->marsh`, `cliffs<->quarry` warps
  removed entirely (no direct branches anymore).
- **`content/world_map_layout.json`**: connections updated to match,
  with real `fromXY`/`toXY` scanned from the new door tile positions
  (not guessed) so the Town Map generator's `exitEdge()` computes
  "east"/"west" correctly from real geometry.
- **`tools/generate-town-map.mjs`**: `REGION_META.quarry.gem` set to
  `false` (was `true`) — Quarry is a waypoint on the chain now, not a
  destination.
- Regenerated: `run_full_audit.py` PASS, developer markdown confirms
  the exact chain (`CryTown -> The Cliffs [east]`, `The Cliffs -> The
  Marsh [east]`, `The Marsh -> The Quarry [east]`, `The Quarry -> The
  Camp [east] need:beatCalder`), rendered SVG visually confirmed as a
  clean eastward line with no overlaps.
- `check_sync --strict`, typecheck, web build, `make -C
  ports/dreamcast` all clean (baked `.inc` content changed since
  `maps.json`/`world.json` changed — verified the baked `WarpDef`
  entries carry the correct dir codes 2/3 for left/right and the
  `beatCalder` flag index correctly followed the gate to its new
  warp).

**Scrubbed stale location references from NPC dialogue (Claude,
2026-09-22).** User's follow-up: since the world map keeps getting
restructured, any dialogue line asserting a specific direction/
position ("Calder south", "West is Ivo, East is Nell", "the camp
guards the road south", "No one leaves Crytown by the north road")
is a standing liability — either already wrong (Camp isn't south of
CryTown anymore after the east-chain rewire above) or will break the
next time the map changes. Scanned `content/dialogue.json` (all of
`talk`/`intro`/`endingWin*`/`mercyDismissLines`) and
`content/world.json` for `north|south|east|west` plus positional
phrasing (`beyond`, `past the`, `by the water`), found 23 lines total
across `dialogue.json` and one trainer battle title
(`lieutenantLead.title` in **`content/world_parts/trainers.json`** —
edited the real source, not `world.json` directly, then re-ran
`merge_world.py`). Rewrote each to drop the specific
direction/position while keeping the character's voice and any
actually-useful hint (e.g. `pikeHint` keeps "In the tall grass by the
water," drops "East of the path"). Left place **names** alone where
they're just narrative color, not a navigation claim (e.g. "The Grove
is a prison," "Marsh trade" as a shop's flavor line) — only removed
lines making a locatable/directional claim, since that's what goes
stale, not the existence of a place name.
- `check_sync --strict`, typecheck, web build, `make -C
  ports/dreamcast` all clean.
- **If you add new NPC/trainer dialogue,** don't give it a compass
  direction or "past/beyond X" hint — the world layout is still being
  actively rearranged this session.

**Full west/south world rewrite: Ruins/Reach west, Gauntlet direct
south, Camp->Forest->Prison chain, Grove renamed (Claude, 2026-09-22).**
User-directed narrative + topology rewrite. Confirmed with the user
first: Shinigami's fight is unchanged mechanically (still grants
`hasScroll` on defeat — "freed" means freed *by* being fought, not
instead of it; he's imprisoned in the Grove, reached by first beating
Cathleen), and the new CryTown-south Gauntlet gate **replaces** the
old Grove entrance entirely.

New warp graph (all real door tiles, not just Town Map relabeling):
- **CryTown -- west --> Ruins -- west --> Reach.** New door 'P' on
  veld's west wall (row11); Ruins' old west door (was to Grove) now
  points to Reach instead; Ruins' old south door (was to Reach) moved
  to its east wall, now points to CryTown; Reach's old north door
  moved to its east wall. Gated `need:"beatShin"` (the west path is a
  shortcut unlocked by freeing Shinigami via the long way round, not
  a required progression path — you reach the Grove through the
  east/south chain regardless).
- **CryTown -- east --> Cliffs** now gated `need:"beatCalder"`
  (moved from the old `quarry->camp` warp, which is now ungated —
  Calder guards the first step of the chain, not the last). Calder's
  NPC mark physically relocated in veld's grid to stand in the
  corridor right before the 'c' door (row11, next to it).
- **Camp -- south --> Forest -- south --> The Prison** (was Grove).
  New door 'F' on camp's south wall; Forest's old north door (was to
  veld) repointed to Camp instead — CryTown no longer connects to
  Forest directly at all.
- **CryTown -- south --> Gauntlet1** (was CryTown -- south -->
  Forest). Reuses veld's existing south 'Z' tile and gauntlet1's
  existing entrance mark '2' — just repointed, no new tile surgery
  needed on either side. Gated `need:"hasScroll"`. The old
  `grove->gauntlet1` warp (gated `choseHeavenfall`) is removed
  entirely per the user's explicit "replace it" choice.
- All three gates (`beatCalder`/`beatShin`/`hasScroll`) were **already
  valid `need` codes** in `tools/bake_content.py`'s `NEED` dict and
  both engines' need-check logic (confirmed before writing any data)
  — zero new engine code required for any of the gating.
- Grove renamed to **The Prison** everywhere: `world_parts/map_meta.json`
  (`mapNames.grove`), `generate-town-map.mjs`'s `REGION_META.grove.label`,
  and every dialogue line that named "the Grove" as a place (internal
  map id `grove` is unchanged — same pattern as `veld`/CryTown).
- **Shinigami's win dialogue (`shinigamiAfter`) rewritten** — it
  previously had him vanish into fog forever ("I won't be here to
  care" / "turns to fog" / gone for good), which flatly contradicted
  the new plot (he travels to CryTown, breaks the rock, ends up at
  the Reach). Now he says he's going to go break "an old rock," and
  simply walks out.
  - **The "rock" and the "priest" are narrative-only** (`failTalk` on
    the gated warps), matching every existing gate in this codebase
    (`campLocked`/`reachLocked` etc. — none of them change world tiles
    or spawn a physical obstacle object). No new engine mechanic
    invented for this.
  - **Considered and rejected:** a literal scripted "Shinigami walks
    to CryTown, breaks the rock, walks onto the warp tile, vanishes"
    cutscene. The only existing precedent for a scripted walking NPC
    (`arrivals`/`masonAmbush` in `logic.json` + hardcoded
    rival/anne phase state in `engine.ts`) is built specifically for
    Mason and Anne, not generic — cloning it for a third character on
    both engines would have been a genuinely large new engine feature
    for one flavor beat. Told the story in text instead: his win
    dialogue narrates the rock-breaking intent, and the Reach NPC
    confirms it happened, on the way to talking about the Reach
    Stone/Quartz/Opal/badges as asked.
- **Reused the existing `reachStone` NPC slot for Shinigami's second
  appearance** (`content/world_parts/npcs.json`): id renamed
  `shinigamiFree`, sprite reused from his existing Grove appearance
  (`sprite: "shinigami"`, no new art needed), dialogue rewritten to
  explain the Reach Stone, Crystal Quartz, Crystal Opal, and the
  badges, exactly as asked. Kept the existing `talkedReach` save flag
  name unchanged even though the NPC's identity changed — it's baked
  into the binary save format's bit layout, renaming it would be
  pure churn with no functional benefit.
- **New `priest` NPC blocking the Gauntlet gate has no sprite.**
  Tried `sprite: "npc/priest"` first; caught before committing that
  no such art exists (`content/sprites.json`'s `npcs` catalog doesn't
  list "priest", nothing under `public/sprites/npc/`) — this is
  exactly the "never silently reuse another character's sprite,
  missing art → PLACEHOLDER_ART" rule in `docs/CRYMON.md`. Removed
  the sprite field entirely, matching the existing `cageGate`
  precedent (an invisible blocking/talk object, no portrait). A
  future art pass should add real `npc/priest` frames and set the
  sprite field.
  - **Also caught before committing:** giving the priest his own
    named `speaker` (`"priest"`) in dialogue crashes
    `bake_content.py` — Dreamcast's speaker system isn't just a name
    string, it's a hardcoded `SPK_*` enum in `main.c` paired 1:1 with
    a generated portrait image per speaker
    (`SPEAKER_PORTRAIT[SPK_COUNT]`), and adding a new one needs real
    generated art the same way a new NPC sprite does. Used the
    existing `speaker: "system"` (already used by the gravestone —
    an established "environmental voice, no portrait" pattern) for
    all of the priest's lines instead of inventing a new speaker id.
- Full verification: `check_sync --strict`, typecheck, web build,
  `make -C ports/dreamcast` (only baseline warnings), full
  world-graph audit PASS (every region still reachable from CryTown,
  including the Gauntlet chain and the Prison, through the new
  routes), rendered SVG visually confirmed against the requested
  layout.

**Priest -> named Heavenfall Priestess, real art, scroll-check
teleport-home (Claude, 2026-09-22).** User supplied real art (a
pixel-art sorceress on a magenta background) and asked for the
placeholder-art priest from the previous entry to become a named
character: introduces herself as "The Priestess of the Fall of
Heaven," referred to elsewhere as "the Heavenfall Priestess." No
scroll -> she says so, shouts "Then begone!", and teleports Max home.
- **Art pipeline:** `tools/strip_magenta.py key-clamp --size 0 --pad 0`
  on the source image, then PIL contain-fit into the standard 48x64
  NPC canvas (feet-aligned to the bottom), saved as
  `public/sprites/npc/heavenfallPriestess-{1..4}.png`. Registered in
  `content/sprites.json`'s `npcs` catalog (required for
  `check_sync`'s sprite-gap check). **All 4 frames are the same
  static image** — only one pose was provided, and inventing 3 more
  animation frames from imagination isn't something I'll do; she
  reads as stationary rather than idle-animated. A real 4-frame
  walk/idle cycle would be a good follow-up if more art comes in.
  - **`npc/priest` doesn't exist as a real art asset was the previous
    entry's finding — still true, that reference is gone now that
    the id and sprite are real.**
  - **Caught a real self-inflicted mistake before it landed:** ran
    `python3 tools/strip_magenta.py --help` expecting a help flag;
    this script parses argv manually and has no `--help` handling, so
    anything other than `key-clamp` as the first arg falls through to
    its *legacy bulk mode* — it silently re-processed every sprite
    under `public/sprites/` with the older, cruder 1px fringe-delete
    pass and rewrote ~15 pre-existing files (anne/mason/max walk
    frames, several npc frames). This is **exactly** the failure mode
    `CURRENT_WORK.md`'s own magenta-keying section already warns
    about ("Don't use bare `strip_magenta.py`, it still does this
    legacy pass") — I'd read that warning earlier this session and
    still tripped it via `--help`, since the warning doesn't call out
    that `--help` specifically isn't safe. Caught via `git status`
    turning up a pile of unexpected sprite diffs before committing;
    reverted all of them with `git checkout HEAD --
    <path>` and regenerated `sprites.h` fresh afterward so it
    doesn't carry the accidentally-refringed pixel data. **Never run
    `tools/strip_magenta.py` with anything other than `key-clamp ...`
    as the first argument — there is no safe no-op invocation of this
    tool, including `--help`.**
- **New NPC-level teleport mechanic (`priestessTeleport`)** — the
  first `after`-triggered effect that isn't a battle, shop, or heal.
  Small, well-precedented addition on both engines, not a new
  subsystem: reuses the existing party-wipe-style "fade out, warp to
  HOUSE's `U` mark, fade in" sequence (`LOGIC.partyWipe`), just
  without the heal. Wired end-to-end: `tools/bake_content.py`'s
  `AFTER_IDS`/header defines, `content/world_parts/npcs.json`'s
  script (`if hasScroll -> priestessHasScroll` else
  `priestessNoScroll` + `after:"priestessTeleport"`),
  `src/game/engine.ts` (`TalkAfter` union, `startFade`'s action union,
  `applyFadeHold()`, the `advanceTalk()` dispatch), and
  `ports/dreamcast/src/main.c` (`POST_PRIESTESS_TELEPORT` = 34 —
  checked the current max POST_* first per the standing numbering
  gotcha, `FADE_ACTION_PRIESTESS` = 4, both dispatch switches, and
  the `HEAVENFALLPRIESTESS_FRAMES`/`collect_npcs()` VELD registration
  so she actually renders there).
- **Found and fixed a real pre-existing Dreamcast gap while in this
  code:** the previous entry's Shinigami-at-the-Reach NPC
  (`shinigamiFree`) was never wired into `main.c`'s `collect_npcs()`
  — he'd have been invisible there on Dreamcast (the dialogue/script
  side worked fine, only the sprite draw call was missing). Added a
  `MAP_REACH` branch reusing `SHINIGAMI_FRAMES`, gated on `beat_shin`
  (opposite sense from the Grove branch, which hides him there once
  beaten). **Not fixed, pre-existing, unrelated to my changes:**
  Quartz and Opal (the Reach's badge trainers) also have no
  `collect_npcs()` entry at all — flagging for whoever touches Reach
  next, didn't want to scope-creep into it this turn.
- speaker stays `"system"` (portrait-less) for her lines, same
  reasoning as the previous entry's priest -- a proper named speaker
  needs a generated Dreamcast portrait
  (`SPEAKER_PORTRAIT[SPK_COUNT]`), which is a bigger art-pipeline
  lift than her overworld walk sprite; the dialogue portrait
  (`public/sprites/portraits/`) convention keeps each character's
  full painted background, and this source art is a character on
  flat magenta with none, which would look inconsistent with every
  other character's portrait if used as-is. Worth a proper portrait
  pass later, not blocking this feature.
- Full verification: `check_sync --strict`, typecheck, web build,
  `make -C ports/dreamcast` clean rebuild (only baseline warnings),
  full world-graph audit PASS.

**Shinigami-at-the-rock event + Priestess real portrait (Claude,
2026-09-22).** Two follow-ups to the entries above.

*Shinigami stands next to the rock (no walk cutscene, as decided
above; user confirmed: standing NPC + auto-trigger on proximity
instead).* New NPC `shinigamiRock` (id distinct from Grove's
`shinigami` and Reach's `shinigamiFree` -- same character, three
separate npc-table entries, matching how this codebase already
handles Shinigami's Grove/Reach split), `veld` mark `'9'` placed
right next to the new west door, reusing his existing `shinigami`
sprite (no new art). New save flag `sawShinigamiRock` (63rd of the
64 available bits -- 1 left after this). `engine.ts`'s
`maybeShinigamiRock()` (called from `updateWorld()` alongside the
existing `maybeStartAnne`/`maybeStartMasonRematch`) fires once, the
first time the player's viewport overlaps his position, while
`beatShinigami` is true and the event hasn't fired yet -- plays
`TALK.shinigamiRockEvent`, sets the flag, hides him after (`hideIf`
in his script + an `isSolid()` exception matching the existing
Grove-Shinigami pattern). Mirrored on Dreamcast: `saw_shinigami_rock`
local + `SAVE_FLAG_SAW_SHINIGAMI_ROCK` save/restore + `FLAG_SAW_
SHINIGAMI_ROCK` for the `hideIf`, a `collect_npcs()` VELD entry
gated on `beat_shin && !saw_shinigami_rock`, and a proximity check in
the main per-frame loop using `SCREEN_W/H` (Dreamcast's real
resolution, vs. `VIEW_W/H` on web) as the "in view" test.
**The boulder "exploding" is narrated in the dialogue text only --
no particle animation exists.** Marked with a code comment at both
trigger sites and here: a real particle-burst effect is a follow-up
for whoever next touches VFX, not implemented in this pass.

*Priestess portrait, from the source art, re-stripped since the
uncompressed intermediate wasn't kept.* The npc-sprite step earlier
this session deleted its working file (`_priestess_raw.png`) after
fitting it to 48x64, so per the user's own fallback instruction, the
portrait was made by re-running `strip_magenta.py key-clamp` fresh
against the original upload (not the compressed 48x64 sprite) and
cropping to the character's bbox with padding -- full resolution,
not tiny. This is now a **real** portrait (unlike the removed
placeholder priest), so she's wired as a proper named speaker instead
of the portrait-less `"system"` voice used before: `heavenfallPriestess`
added to `content/dialogue.json`'s `speakers`, `tools/bake_content.py`'s
`SPEAKER` dict (id 37), `content/sprites.json`'s `portraits` catalog,
and `src/game/types.ts`'s `SpeakerId` union (`check_sync` catches a
mismatch here, which is how this got noticed before it half-shipped).
- **Found and fixed a real pre-existing bug while wiring her
  Dreamcast portrait:** `SPEAKER_PORTRAIT[beat->speaker]` in `main.c`
  has never bounds-checked the array access, and `"system"` (Python
  speaker id 36) was already being looked up against an array sized
  only `SPK_COUNT` = 24 -- an out-of-bounds read on real hardware for
  every existing `system`-voiced line (gravestone, several `failTalk`
  messages), predating this session entirely. Rather than paper over
  it with a bounds-check band-aid, sized `SPEAKER_PORTRAIT` up to 38
  entries (ids 24-36 filled with `{0,0,0}`, i.e. no portrait, matching
  what those ids already mean on the web side) so `SPK_HEAVENFALLPRIESTESS`
  = 37 lines up with the same baked id Python assigned and every
  index in range is now genuinely valid memory. **If you add another
  new speaker, its id must still land inside `SPEAKER_PORTRAIT`'s
  bounds** -- extend the array (or its dummy-entry range) again, the
  same way this fix did, rather than assuming Python and C only need
  to agree on the number and not on the array actually being that
  large.
- Rewrote her introduction lines to drop the third-person "she says"
  narration wrapper now that a real speaker tag makes that redundant
  (every other character's dialogue is plain first-person text under
  their own name tag; hers should read the same way).
- Full verification: `check_sync --strict` (caught the `SpeakerId`
  union gap), typecheck, web build, `make -C ports/dreamcast` clean
  rebuild (only baseline warnings), full world-graph audit PASS.

## Tree of Life expansion (Claude, in progress, 2026-09-22)

**Design.** North of CryTown (`veld`) is Weeping Army territory. A
single new route, **The Weeping Road** (`weeping_road`), leaves
CryTown's north wall and leads to **Malkuth**, the southernmost/
lowest Sephirah and entry point into a 10-city, 22-path map cluster
shaped like the Kabbalistic Tree of Life. All 10 cities are named
after the Sephirot; all 22 connecting routes are named after the
22 paths (Hebrew-letter-named, classic Golden Dawn assignment,
paths 11-32). Every one of these 32 maps is intentionally **blank**
(bordered walkable room/corridor, no NPCs/encounters/dialogue) --
scaffolding to "build upon later," per the user's explicit request.
Movement stays strictly 4-directional (this engine has no diagonal
player movement, web or Dreamcast) -- "diagonal" is expressed two
ways that don't require engine changes: (1) a path's own corridor
tiles can zigzag/staircase through its bounding rows the same way
the warning-stripe reference image does, and (2) the county map's
generator now supports fixed coordinate overrides + a stairstep
line renderer for connections between non-adjacent cells, so the
Tree of Life silhouette actually appears on the Town Map screen.

**Sephirot -> map id / city name / tree grid coords** (col,row; col
negative=left pillar, 0=center pillar, positive=right pillar):
1 Keter/keter (0,0) 2 Chokmah/chokmah (2,1) 3 Binah/binah (-2,1)
4 Chesed/chesed (2,2) 5 Gevurah/gevurah (-2,2) 6 Tiferet/tiferet (0,3)
7 Netzach/netzach (2,4) 8 Hod/hod (-2,4) 9 Yesod/yesod (0,5)
10 Malkuth/malkuth (0,6)

**22 paths -> map id / endpoints** (`veld<->malkuth` via
`weeping_road` is separate, not part of the 22):
11 aleph keter-chokmah, 12 beth keter-binah, 13 gimel keter-tiferet,
14 daleth chokmah-binah, 15 he chokmah-tiferet, 16 vau chokmah-chesed,
17 zayin binah-tiferet, 18 heth binah-gevurah, 19 teth chesed-gevurah,
20 yod chesed-tiferet, 21 kaph chesed-netzach, 22 lamed gevurah-tiferet,
23 mem gevurah-hod, 24 nun tiferet-netzach, 25 samekh tiferet-yesod,
26 ayin tiferet-hod, 27 peh netzach-hod, 28 tzaddi netzach-yesod,
29 qoph netzach-malkuth, 30 resh hod-yesod, 31 shin hod-malkuth,
32 tau yesod-malkuth.

**Per-map wiring checklist** (repeated per map, both engines are
data-driven for blank maps -- confirmed no bespoke Dreamcast C is
needed as long as a map has zero NPCs): `content/maps.json` rows,
`content/world_parts/map_meta.json` mapIds+mapNames (append-only,
order must match `save.json`'s mapOrder exactly per `check_sync`),
`content/save.json` mapOrder, `content/world_parts/warps.json`
(bidirectional pair), `src/game/types.ts` MapId union,
`src/game/data.ts` const + MAPS entry, `content/world_map_layout.json`
(maps + connections, drives the county-map generator/world_graph
audit only -- not part of `check_sync --strict`, but kept in sync
per the CLAUDE.md contract), `tools/generate-town-map.mjs`
REGION_META entry. `python3 tools/bake_content.py` regenerates all
Dreamcast `.inc` files generically from the same JSON -- no `main.c`
edits needed per map.

**Build order** (topological -- every step's new warp endpoints
must already exist by the end of that step, so `check_sync --strict`
passes at every commit): `weeping_road`+`malkuth`, then walk the
tree from Malkuth outward (Tau, Qoph/Shin, Samekh/Nun/Ayin, ...),
introducing each new city on its first edge and wiring its remaining
edges once both endpoints exist. Each step: edit -> bake -> 
`check_sync --strict` -> typecheck -> build -> `make -C
ports/dreamcast` -> commit -> push -> note completed step here.

**Progress:** (updated per step below as they land)
- Step 1/23: `malkuth` (city) + `weepingroad` (route, CryTown's new north
  exit, mark `O` punched into `veld`'s row0). Built by
  `tools/build_sephirot.py --step 1`. Note: map ids can't contain `_`
  -- `check_sync`'s `union_members()`/`maps_object_keys()` regexes are
  `[a-zA-Z0-9]+`/`[a-z0-9]+` only, caught immediately by the strict
  gate on the first attempt (`weeping_road` -> renamed `weepingroad`).
  All city rooms are pre-carved with their FULL eventual exit set on
  first creation (Malkuth already has all 4 marks: 3 north for
  Qoph/Shin/Tau reverse + 1 south for the road) -- only the matching
  `warps.json` pair is added once both endpoints of an edge exist, so
  later steps never have to touch an already-placed city's geometry
  again, just add more warps to marks that are already sitting there
  inert. Verified: bake, check_sync --strict, typecheck, build, clean
  Dreamcast rebuild (no C changes needed, confirmed the whole tile/
  warp system is fully data-driven for NPC-less maps).
- Step 2/23: `yesod` (city) + `tau` (route, yesod<->malkuth). Green.
- Step 3/23: `netzach` (city) + `qoph` (route, netzach<->malkuth). Green.
- Step 4/23: `hod` (city) + `shin` (route, hod<->malkuth). Green.
- Step 5/23: `peh` (route, netzach<->hod). Green.
- Step 6/23: `resh` (route, hod<->yesod). Green.
- Step 7/23: `tzaddi` (route, netzach<->yesod). Bottom quad (Malkuth/
  Yesod/Netzach/Hod) now fully interconnected. Green.
- Step 8/23: `tiferet` (city, the tree's 8-degree hub -- 3 exits N,
  2 E, 2 W, 1 S, verified no mark collisions on any wall) + `samekh`
  (route, tiferet<->yesod). Green.
- Step 9/23: `nun` (route, tiferet<->netzach). Green.
- Step 10/23: `ayin` (route, tiferet<->hod). Tiferet's links to the
  bottom quad complete. Green.
- Step 11/23: `chesed` (city) + `kaph` (route, chesed<->netzach). Green.
- Step 12/23: `yod` (route, chesed<->tiferet). Green.
- Step 13/23: `gevurah` (city) + `mem` (route, gevurah<->hod). Green.
- Step 14/23: `lamed` (route, gevurah<->tiferet). Green.
- Step 15/23: `teth` (route, chesed<->gevurah). Chesed/Gevurah/Tiferet
  triangle complete. Green.
- Step 16/23: `binah` (city) + `zayin` (route, binah<->tiferet). Green.


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

**Work directly on `main`. Do not create a per-agent feature branch**
(`claude/...`, `grok/...`, or similar) as your default workflow, even
if a session's own scaffolding/system prompt tells you to. Off-`main`
branches make it unclear to the user what has and hasn't actually
landed on the live repo, and someone still has to remember to merge
and delete them later. If your harness truly cannot commit straight
to `main`, say so plainly rather than silently working on a branch,
and merge + delete it the same session once the user is aware of it.

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
  the one step in progress. A prompted task is not finished until that
  work is on `main`. That includes pictures and sheets the user was
  shown. If a file only exists under `/workspace/artifacts`, copy it
  into the repo and push it. Do not wait to be asked.
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
- Step 17/23: `heth` (route, binah<->gevurah). Green.
- Step 18/23: `chokmah` (city) + `he` (route, chokmah<->tiferet). Hit
  a real bug in `tools/build_sephirot.py`'s data.ts-registration
  check: `"raw.he" not in data_text` is a **substring** match, and
  `"raw.heth"` (added step 17) already contains `"raw.he"` as a
  substring -- so `he`'s own `export const HE = ...`/`MAPS` entry got
  silently skipped, and check_sync caught it (`data.ts MAPS keys !=
  world.mapIds`). Fixed to a word-boundary regex
  (`re.search(rf"raw\.{id}\b", ...)`), reran step 18 clean.
- Step 19/23: `vau` (route, chokmah<->chesed). Green.
- Step 20/23: `daleth` (route, chokmah<->binah). Chokmah/Binah/Tiferet
  triangle complete. Green.
- Step 21/23: `keter` (city, the crown -- final city) + `gimel`
  (route, keter<->tiferet). All 10 Sephirot cities now exist.
  Remaining: aleph, beth (Keter's other two edges). Green.
- Step 22/23: `aleph` (route, keter<->chokmah). Green.
- Step 23/23: `beth` (route, keter<->binah). **All 33 maps complete**
  (10 Sephirot cities + 22 named paths + the Weeping Road). Total map
  count 17 (pre-existing) + 33 = 50, confirmed via `world.json`'s
  `mapIds`. Content build is done; remaining work is the county-map
  generator upgrade (coordinate overrides + stairstep connector
  lines so the Tree of Life silhouette actually renders on the Town
  Map screen) -- not yet started.

**County-map generator upgrade (Claude, 2026-09-22, same day).**
Extended `tools/generate-town-map.mjs`: (1) `REGION_META` entries for
all 33 new maps; (2) cluster connectivity sourced directly from
`content/world_parts/warps.json` (not `world_map_layout.json`, which
still hasn't been extended for this cluster -- tracked below as an
open follow-up, not part of `check_sync --strict`); (3) after the
normal BFS packer runs (harmlessly auto-placing the cluster
somewhere, since it's graph-reachable via the Weeping Road), a manual
placement pass **overwrites** the 33 boxes with the classical Tree of
Life coordinates (3 pillars x 7 levels, anchored north of CryTown's
already-packed box) -- the normal cardinal-adjacency packer can't
produce a recognizable tree shape for a subgraph this cross-connected
(Tiferet alone touches 8 other cities); (4) a `stairstepPoints()`
helper draws blocky alternating-H/V connector lines (matching the
warning-stripe pixelated-diagonal reference the user gave, never a
smooth line -- this engine has no diagonal movement) between any two
cluster cells, since manual placement doesn't guarantee physical
adjacency the way the rest of the map does. Rendered and visually
verified via cairosvg -- the Tree of Life shape is unmistakable, all
10 cities and 22 path labels legible, no overlaps, `Validation: OK`.

**Known follow-up, not done today:** `content/world_map_layout.json`
and the `tools/world_graph/` audit scripts still don't know about
these 33 maps (the generator bypasses that file for this cluster and
reads warps.json directly instead, per above) -- whoever extends the
Tree of Life cluster further (adding NPCs, dialogue, real art) should
also backfill `world_map_layout.json`'s `maps`/`connections` entries
so `tools/world_graph/run_full_audit.py` covers it too.

## Dev Codes (web preview only, Claude, 2026-09-22)

Added a debug console to `src/components/crymon-app.tsx` (the web
app shell, not the in-game UI) -- a "Dev Codes" toggle button in the
header that reveals a text input + Submit button, wired to a new
`CryMon.submitDevCode(raw)` method in `src/game/engine.ts`. **Web
preview only, by design** -- there's no equivalent UI or code on
Dreamcast, and none was added; nothing in `main.c` changed.

- **`WinAll`** -- calls `devWinAll()`, which sets the current foe's hp
  to 0, clears its bench, and calls the game's own `finishWin()`
  directly (same function a real battle win calls) rather than faking
  a simpler ending -- so trainer flags, mercy prompts, and XP/marks
  rewards all fire exactly as they would from a real win, just
  instantly. No-ops with a message if no battle is in progress.
- **`PassAll`** -- sets a new `devPassAll` flag (never persisted,
  never reset on new game -- it's a session-only debug toggle, not
  game state) that (1) makes `blocked()` return false unconditionally
  (noclip through every wall/solid tile) and (2) makes `applyWarp()`
  skip its `warp.need` story-flag gate check, so every warp fires
  regardless of progress. Both are one-line additions to existing
  functions, not new systems.

Verified end-to-end with a headless-Chromium Playwright script
against the real dev server (not just typecheck): toggled Dev Codes
on, confirmed PassAll actually lets the player walk straight through
the cottage's north wall (screenshot showed the sprite outside the
room's border), and confirmed WinAll against a real battle -- forced
one via a temporary `window` test hook (removed before committing,
never shipped), submitted `WinAll` through the actual UI text box,
and confirmed mode returned to `"world"`, marks incremented by the
normal wild-win amount (+3), and the party CryMon's hp was untouched
-- exactly the "skip to the end as if you'd won" behavior asked for.

## Gate-blocking + directional warp audit (Claude, 2026-09-22)

Four bugs reported together, all fixed:

**1. Calder/Priestess didn't actually block their gates.** Both had a
sprite (which blocks by default) but sat 2+ tiles away from the real
gate tile, with open floor on every side -- the plaza around both
gates was wide open, so the "gate guard" was trivially walkable
around. Fixed by actually building a chokepoint: walled off (`H`,
matching the nearby roof/building tiles) every approach to each gate
except one tile, then moved the NPC onto that sole tile.
- East gate (`c`, mark col28 row11 in `veld`): walled `col28` at
  rows 10 and 12 (its only two neighbors besides the border and the
  west approach), moved Calder (`E`) from col26 to col27 -- now the
  gate's only reachable neighbor.
- South gate (`Z`, col14 row22): walled row21 cols 13/15/16 (it was
  a 3-tile-wide approach plus a stray col13 bypass), moved the
  Priestess (`4`) from col17 to col14, directly above the gate.
- The west gate (`P`, col0 row11) turned out to already be a clean
  1-tile chokepoint (border walls close on both sides) -- no wall
  edits needed there, see the boulder fix below.

**2. Calder/Priestess needed to stop blocking once satisfied**, still
visible ("step aside"), not vanish. `npcHidden()` (draw+collision)
intentionally couples visibility and solidity for the shinigami-rock
case below, so a *separate* mechanism was needed for "still there,
just not in the way": a new `passIf` script key, checked only in
`blocked()`, independent of drawing. Added `"passIf": "beatCalder"`
to Calder's existing `if:"beatCalder"` step and `"passIf":
"hasScroll"` to the Priestess's -- reusing the same step object
their dialogue-branch `if` already lived on, not a new script entry.
**Dreamcast had never blocked either of them at all** (found while
wiring this) -- `actor_blocks()`'s VELD branch only listed decorative
prop marks (K/I/V/A/Q/J), not Calder/Priestess -- so this was a
bigger gap there than on web. Extended `actor_blocks()`'s signature
with `beat_calder`/`has_scroll`/`saw_shinigami_rock` and added the
matching `mark_hit()` checks.

**3. Shinigami's overworld sprite stood at the west gate instead of a
rock, and appeared before he'd even been fought.** His `shinigamiRock`
NPC script only had `hideIf: sawShinigamiRock` -- nothing gated it
*on* `beatShinigami` in the first place (Dreamcast's `collect_npcs()`
already had this right, `if(beat_shin && !saw_shinigami_rock)`; only
the web side was missing the entry condition). Fixed by extending
`if`-condition support into the same generic visibility check that
already handled `hideIf` (`npcHidden()`, shared by the draw loop and
`blocked()` so they can never disagree) -- but this required a real
fix, not a blind extension: a naive `s.if && !flags[s.if]` check
broke Calder and the Priestess, because their existing `if` fields
are for *dialogue branch selection*, not visibility, and don't mean
"hide the NPC" when unmet. `npcHidden()` now only treats `if` as a
visibility gate on a step that carries no `talk` (shinigamiRock's
`{if: beatShinigami, hideIf: sawShinigamiRock}` has none; Calder's
`{if: beatCalder, talk: calderAfter, passIf: beatCalder}` does, so
its `if` is left alone). Caught by directly exercising `blocked()`
via a temporary test hook before it shipped -- the Priestess
silently stopped blocking pre-scroll on the first version of this
fix, exactly the kind of regression a plain typecheck can't catch.
- Added a **new visible boulder** (`shinigamiBoulder`, mark `Y`,
  placed on the west gate's one approach tile) since the rock was
  previously narrative-only (`CURRENT_WORK.md`'s own earlier entry
  explicitly said "no physical obstacle object, matching every
  existing gate" -- superseded now that the user asked for a real
  one). No boulder art exists, so this is **PLACEHOLDER_ART**: a
  plain schematic gray rock shape generated with PIL (see
  `public/sprites/npc/shinigamiBoulder-*.png`), not real art. Visible
  (and blocking, `hideIf: beatShinigami`) until Shinigami is beaten,
  then gone, matching when his own sprite starts appearing next to
  the (now-shattered, per existing dialogue) rock.
- Found and fixed a second bug while wiring this: `hasScroll` was
  never in `npcFlags()` at all -- meaning the Priestess's existing
  `priestessHasScroll` dialogue branch, and her failed-teleport
  branch, had *never* correctly evaluated `if: hasScroll` since she
  was added; always fell through to the no-scroll branch regardless
  of the player's actual scroll status. Added it.

**4. `veld`'s east gate warped into Cliffs' north edge instead of its
west edge** ("player is warped in through the northern warp gate of
the next map"). Root-caused with a small audit script (reused the
same `exitEdge()` logic `tools/generate-town-map.mjs` already uses
to place regions on the county map, run standalone against every
warp in `warps.json`): compares each warp's declared `dir` against
where its tile *actually* sits on its own map's border. Found exactly
one mismatch across all 122 warps (including the whole 33-map Tree of
Life cluster, which checked out clean since `build_sephirot.py`
derives `dir` from real coordinates): `veld -> cliffs` via `c` was
tagged `dir: "down"` (a leftover from some earlier topology, per
`content/town_map.json`'s node positions `cliffs` really is due
east of `veld`) when the tile is actually on veld's east border.
Fixed the warp pair's `dir`/`oy`->`ox` (both directions), and
**physically moved Cliffs' own `D` entrance mark from its north
edge (row1) to its west edge (row8, col0)** -- relabeling the warp's
`dir` alone would have fixed the *direction* but the player would
still have visually spawned falling in from the top of Cliffs. Also
fixed `skipToWorld()`'s cliffs branch (a debug fast-travel helper,
web-only, no Dreamcast equivalent) which nudged the spawn point
`down` assuming a north entrance.

**Audit script confirms all 122 warps now consistent** (declared
`dir` matches the tile's real border position on its own map, every
reciprocal pair uses the opposite direction) -- not committed as a
permanent tool since it duplicates `generate-town-map.mjs`'s
`exitEdge()` logic inline rather than importing it (a Python/JS
split), but worth re-running by hand after any future warp edit until
someone ports it in properly. `tools/world_graph/run_full_audit.py`
and `check_sync --strict` both still pass.

## Real merchant stock (Claude, 2026-09-22)

**Reported bug:** greater/mega/ultimate capture crystals showed
quantity 0 or undefined at Dray's stall. Root cause was two separate
things, both fixed:

1. **The shop UI's buy-tab quantity was never stock -- it was
   `this.bag[id]`, how many the player already owned**, mislabeled
   as if it meant availability. For an item never yet bought (every
   higher crystal tier, since none of them start in `startBag`),
   `this.bag[id]` was `undefined`, rendering as `xundefined`.
2. **The actual purchase line, `this.bag[id] += 1`, is `undefined + 1
   = NaN`** the first time any such item is bought -- permanently
   corrupting that bag slot (NaN stays NaN forever after). This is
   the real bug: even once the display was fixed, buying one of
   these crystals would have silently broken that item slot. Fixed
   to `this.bag[id] = (this.bag[id] ?? 0) + 1`, matching the
   `?? 0` idiom already used elsewhere in the file (`giveAnneGems()`).
   Dreamcast was never at risk of this class of bug -- its `Bag` is a
   fixed C struct, zero-initialized, no such thing as an "unset"
   field.

**Requested feature, built on top of the same fix:** real per-item
shop stock, 1-10 units, refreshing every time Max rests.
- `shopCatalog(keeper)` is the old `shopBuyRows()` body verbatim
  (which items a keeper CAN carry) with a new name; `shopBuyRows()`
  now also filters that catalog down to items with stock > 0.
- `rollShopStock(keeper)` assigns `1 + random(10)` to every item in
  that keeper's catalog; `rollAllShopStock()` does all 4 (bram, oren,
  fenn, dray) at once. Called from `sleepHeal()` -- itself already
  the one shared function for every "Max rests" path (a real bed,
  the after-loss teleport-home, and any NPC script step with
  `heal: true`, e.g. Wren's), so no new trigger wiring was needed,
  just extending the function that already covers all three.
  Lazily rolled on first shop open too, so a keeper visited before
  ever resting still has real stock, not empty.
- Buying decrements stock and is blocked at 0 (mirrors the existing
  sell-side `bag[id] <= 0` guard and cursor-reset-to-0 pattern).
- The buy-tab display now shows shelf stock; the sell tab is
  unchanged (still shows how many you own, which is correct there).
- **Not persisted to the save file** -- session/rest-scoped only, by
  design (a save-format change for ~15 items x 4 keepers felt out of
  proportion to what was asked; loading a save just rolls fresh
  stock, same as a new game). Flagging in case persistence turns out
  to matter later.

**Dreamcast**, for full parity (`actor_blocks()`-style reasoning
doesn't apply here, this is `main.c`'s existing `shop_rows()`/
`draw_shop()`/buy-handler trio, which had the exact same owned-vs-
stock display conflation, minus the NaN risk noted above):
- `shop_stock[SHOP_CRYSTAL_MASK_N][ITEM_COUNT]`, a plain file-scope
  global rather than threaded through every shop function's already-
  long parameter list (unlike `shop_free[]`, a flat 1-D array that's
  cheap to thread, this is a 2-D per-item table touching
  `shop_rows`/`draw_shop`/the buy handler/`try_npc_script`'s
  `NpcRun` all at once for no real benefit in a single-threaded
  game).
- `roll_all_shop_stock()` needed a forward declaration before
  `heal_party()` -- its real definition has to come after
  `content_items.inc`/`content_world.inc` are `#include`d (for
  `ITEM_COUNT`/`SHOP_CRYSTAL_MASK_N`), which happens *after*
  `heal_party()`'s own position in the file. Standard C forward-
  declare-then-define-later, not a design smell.
  Called from `heal_party()` itself (mirrors web's `sleepHeal()`
  hook exactly -- same 3 call sites for free) and once explicitly on
  new-game reset and on a successful save load (shop_stock isn't
  part of the save format there either).

Verified end-to-end via a Playwright script against the real dev
server, going through the actual `updateShop()` confirm path (not
just calling the setter methods directly): initial stock at Dray's
showed real 1-10 numbers for every item including all three crystal
tiers, buying one down to 0 correctly removed it from the buy list
and left a real (non-NaN) bag count, and `sleepHeal()` visibly
re-rolled every number. `check_sync --strict`, typecheck, web build,
and a clean Dreamcast rebuild all pass.

## Dev Codes field ate Backspace (Claude, 2026-09-22)

Reported: the Dev Codes text input wouldn't accept Backspace.
Root cause was in `src/game/input.ts`, not the Dev Codes UI itself:
`Input.attach()`'s `keydown` listener is on `window` (so held arrows/
WASD keep working no matter what's focused) and calls
`e.preventDefault()` for every code in `GAME_KEYS` -- which includes
`Backspace` (also aliases `select()`), `Enter`, `Space`, `Tab`,
`Escape`, and the WASD/Z/X/C/Q letters. That fires for every keydown
on the page regardless of focus, so typing into the Dev Codes field
had the browser's normal Backspace-deletes-character behavior
cancelled out from under it -- same for Space, Enter, and several
letters, not just Backspace.

Fixed generally rather than special-casing Backspace: `down` now
no-ops (skips both the `preventDefault()` and adding to `this.keys`)
whenever `document.activeElement` is an `<input>`, `<textarea>`, or
`contentEditable` element -- covers the Dev Codes field and any
future text input the same way, not just this one case. `keyup`
deliberately stays unconditional (removing a key from the held-set
is always safe and prevents a key pressed before focus moved to a
text field from getting stuck "held" forever).

Verified via Playwright against the real dev server: typed into Dev
Codes and confirmed Backspace actually deletes characters, and
confirmed normal gameplay input (title -> New Game -> intro, and
re-focusing the canvas after typing in the field) still works
exactly as before. Web-only change (`input.ts` has no Dreamcast
equivalent -- this is specifically about a browser DOM element
stealing keystrokes from another DOM element).

## Empty starting bag + shelf dialogue (Claude, 2026-09-22)

Two small content fixes, both pure JSON, zero engine code (both are
already fully data-driven -- confirmed startBag bakes generically
into Dreamcast's `START_BAG_INIT`, no `main.c` changes needed):

- **`content/world_parts/meta.json`'s `startBag`** had 2 salve, 1
  bitterroot, 1 dust, 2 bandage, 1 smoke bomb baked in at game start,
  on top of what the house's shelf (Quillpup) and crate (1 linen
  wrap/bandage) already grant on interaction. Zeroed every non-zero
  entry -- Max now starts with nothing, exactly the Quillpup + one
  linen wrap she actually picks up in the cottage.
- **`content/dialogue.json`'s `shelf` talk** had a line ("The crystal
  breaks warm in her hands. Quillpup shakes out onto the floorboards.")
  describing Quillpup physically appearing on the floor -- there's no
  sprite for that (Quillpup only ever renders as a party icon/battle
  sprite, no "wild starter on the floor" overworld art exists).
  Replaced with "Max closes her hand around the crystal and pockets
  it.", keeping Quillpup narratively inside the crystal rather than
  implying a visual that isn't there.

Verified against the real dev server: a fresh `reset()` shows an
empty bag (`{gem:0, salve:0, ...}` all zero) and no party, and the
live `shelf` dialogue table (fetched from the running app, not just
read from the source file) matches the new three lines exactly.
`check_sync --strict`, typecheck, web build, and a clean Dreamcast
rebuild all pass.

## Removed the "Z" interaction popup (Claude, 2026-09-22)

Web-only feature, web-only fix: `hintZ(wx, wy, radius)` drew a "Z"
above any interactable (shelf, crate, herb, NPCs, the wrecked cart,
etc.) once Max stood within `radius` of it -- ~15 call sites across
`drawWorld()`. Turned it into a no-op rather than stripping all 15
call sites individually (lower risk, same result; `interact()`'s own
proximity checks are separate code and unaffected). Dreamcast never
had this popup at all (confirmed: no `"Z"` text draw anywhere in
`main.c`), so no Dreamcast change needed.

Verified visually against the real dev server: standing next to the
house's shelf (previously a guaranteed trigger) shows no popup.
typecheck, web build, and a clean Dreamcast rebuild all pass.

## Camera unclamped so the HUD box never occludes map edges (Claude, 2026-09-22)

User reported a house near a map's top edge looking "chopped up" --
actually a fixed top-left HUD box (`drawWorldHud()` web /
`draw_hud()` Dreamcast, both ~40px tall, drawn at screen `(8,8)`)
occluding map content whenever the player stood within `VIEW_H/2`
(240px web) / `SCREEN_H/2` (120px Dreamcast) of the top or left map
edge, because the camera used to clamp to `[0, mapWidth-VIEW_W]` /
`[0, mapHeight-VIEW_H]` and couldn't pan far enough to keep the player
centered near an edge. User's own follow-up correctly diagnosed the
real fix: let the camera move past the map bounds instead of clamping
it.

- **`src/game/engine.ts`'s `cam()`** and **`ports/dreamcast/src/main.c`'s
  `compute_camera()`** now always center exactly on the player,
  unconditionally -- no bounds clamp at all. Safe because `drawMap()`'s
  tile loop (both engines) already skips anything outside the grid and
  the background is filled first, so panning past an edge just reveals
  plain background, no crash risk.
- Verified via Playwright: the previously-occluded house door/roof now
  renders fully visible below the HUD with clear margin; spot-checked
  other map corners too.
- `check_sync --strict`, typecheck, web build, `make -C
  ports/dreamcast` all clean.

## Fixed NaN HP / NaN capture% on wild encounters (Claude, 2026-09-22)

User reported "NaN% x5" on a Capture Crystal in the battle item menu,
then separately that a wild Briarfox had "NaN" for its HP bar. Same
root cause: **`content/world_parts/meta.json`'s `formulas` object was
missing the `wildLevelCap` key entirely** (confirmed via `git log --all
-p` that it existed before, valued `50`, and was already absent going
back to the earliest commit that still touches this file -- a
pre-existing bug, not something introduced this session).

Poisoning chain: `tryEncounter()` (`src/game/engine.ts`) does `const
cap = shiny ? Math.floor(FORMULAS.wildLevelCap / 2) : FORMULAS.wildLevelCap;
lv = Math.min(lv, cap);` -- with `wildLevelCap` `undefined`, `Math.min(lv,
undefined)` is `NaN`, which then poisons `mintMonster()`'s entire stat
block (`Math.max(1, NaN)` is `NaN`, `Math.round(NaN)` is `NaN`, etc.),
and separately breaks `captureChance()`'s clamp (`NaN < 0`/`NaN > 100`
are both `false`, so a NaN chance falls through uncaught).

- **`content/world_parts/meta.json`**: restored `"wildLevelCap": 50`
  in `formulas`, plus its historical rationale note ("hard ceiling on
  any wild-encounter mint... no encounter table currently rolls
  anywhere near it, this is a safety clamp").
- **`src/game/data.ts`'s `captureChance()`**: added a defensive
  `!Number.isFinite(chance)` guard alongside the existing `< 0` clamp,
  per the user's explicit ask that a negative/invalid chance should
  display as zero -- belt-and-suspenders on top of the meta.json fix,
  not a substitute for it.
- **Dreamcast confirmed unaffected**, no C-side change needed:
  `tools/bake_content.py` already falls back to `levelCap` (100) when
  `wildLevelCap` is missing when baking `#define WILD_LEVEL_CAP`, and
  `capture_chance()` in `main.c` works entirely in `int`, so there's
  no NaN-equivalent failure mode there. This is why only the web build
  showed the bug.
- Verified end-to-end via Playwright against the real dev server:
  minted a wild Briarfox (normal and shiny) and computed its capture
  chance -- all values are real numbers (e.g. `hp:28, maxHp:28,
  chance:56`; shiny `level:6, hp:38, maxHp:38`), no NaN anywhere,
  including the shiny-doubling path that halves the cap.
- `check_sync --strict`, typecheck, web build, `make -C
  ports/dreamcast` all clean.

## Stump-blocking bug ("acorn-like sprite in the way") -- STILL OPEN

User reported being unable to walk into the space near the tree-stump
prop in veld (tallgrass + brick building nearby in their screenshot).
Investigated and ruled out the obvious causes without finding a root
cause:
- The stump (`prop-stump`, mark `'L'` via `spawnOf(VELD, "L")`) is
  purely decorative -- `drawProp()` calls have no collision logic tied
  to them on web at all, and grep found zero `'L'`-mark handling
  anywhere in Dreamcast's `main.c` (`actor_blocks()`'s per-map
  hardcoded list only covers real NPC marks like K/I/V/A/Q/J/E/4/Y/9).
- Called `blocked(x,y)` directly (web) at the stump's exact tile and
  all 4 cardinal neighbors in a fresh `skipToWorld("veld")` state --
  every call returned `false`.
- No coincidental NPC mark sits within blocking radius of the stump.

Re-tested after the `wildLevelCap` fix landed: re-located the stump
via `spawnOf(MAPS.veld, "L")` (now row12/col24, `x:784,y:400` in the
current, heavily-rewritten veld layout) and probed `blocked()` at that
tile plus all 8 neighbors, and scanned `NPCS` for anything within 3
tiles -- still all clear, still no NPC nearby. No code path currently
blocks this position.

Leaning toward this having been the `wildLevelCap` NaN bug all along
(stump sits next to tallgrass, a wild-encounter trigger tile -- a
NaN-corrupted encounter could plausibly read as a movement soft-lock
rather than a true collision), now fixed as a side effect, plus
possibly veld's own repeated layout rewrites this session moving the
stump's surroundings away from whatever it was originally sitting
against. Not fully confirmed since the original screenshot's exact
game state can't be replayed. **If the user reports this again,**
get the exact tile/direction from a fresh screenshot rather than
re-assuming it's the same root cause.

## Lieutenant Lead repositioned, stump prop removed for good (Claude, 2026-09-22)

User's follow-up screenshot with marked red dots pinned two more
things: (1) Lieutenant Lead standing off to the side of the north
path instead of guarding it, (2) the recurring "acorn-like sprite"
(the tree stump prop) sitting next to Calder.

- **Lieutenant Lead**: `content/maps.json`'s veld rows had his mark
  ('S') at row2/col13, two tiles left of the path's actual center
  (col14-16, confirmed by scanning every `=` column across all 23
  rows). Moved to row1/col15 -- directly under the north exit ('O' at
  row0/col15) and centered on the path, so he now visually blocks/
  guards it instead of standing beside it on the grass.
- **Stump prop, resolved by removal (per explicit user request) rather
  than another positioning fix**: deleted the mark ('L') from
  `maps.json`, deleted its `npcs.json` entry (`role: "loot"`, granted
  1 bandage on first interaction -- that free item is gone now, not
  relocated), and deleted the `drawProp("prop-stump", ...)` /
  `hintZ()` call in `engine.ts` that rendered it. This closes the
  still-open item from the entry above -- turns out the object itself
  was simply unwanted, not just mispositioned.
- Dreamcast's C side never had rendering code for mark 'L' (confirmed
  again via grep) -- it only tracked the `got_stump` save flag, which
  is untouched and now permanently unused, same treatment as any
  other flag whose feature gets removed (no save-version bump needed).
- Verified visually against the real dev server: Lieutenant Lead now
  stands on/blocking the path; the stump area (near the brick building
  and Calder) renders with no stump sprite at all.
- `check_sync --strict`, typecheck, web build, `make -C
  ports/dreamcast` all clean.

## Leg 2.12: Bowie Knife + Backstab (Claude, 2026-09-22)

New item + mechanic: a reputation-gated, one-of-a-kind weapon that
lets the player kill a still-unspotted roaming trainer outright,
skipping the battle entirely.

- **Bowie Knife** (`content/items.json`): `buy:60, sell:0` (never
  listed for sale, same trick `cageKey`/`perfectcrystal` use), not a
  battle or field item -- it's a passive unlock, checked directly off
  `bag.bowieKnife > 0` rather than ever being "used" from a menu.
  Reusable, never consumed (confirmed with the user up front).
- **Dray's one-time warning**: `openShop("dray")` (web) /
  `POST_SHOP`'s Dray branch (Dreamcast) checks `reputation < 0 &&
  !drayKnifeOffered` before opening the buy/sell screen, same
  precedent as the existing Heavenfall-revival merchant warning. Shows
  `TALK.drayKnifeOffer` ("I've heard of your reputation..."), sets the
  one-time flag, and only then does the knife appear in his catalog
  (`shopCatalog()`/`shop_rows()` both special-case keeper===dray +
  flag set + not already owned -- this naturally caps it at one ever,
  since the moment `bag.bowieKnife` goes non-zero the row disappears
  again). Confirmed with the user: shows once ever, normal shop after.
- **Backstab**: while carrying the knife, interacting with a roamable
  wsoldier trainer (the Leg-2.11 "Roamer" chase/LOS system) that
  hasn't started chasing yet opens an Approach/Backstab prompt instead
  of normal dialogue (`canBackstab()`/`openBackstabChoice()` on web;
  Dreamcast's `find_backstab_target()` mirrors `try_npc_script()`'s
  own best-match proximity scan, filtered to
  `npc_def_roamable()` + unspotted + still-fightable). Approach falls
  through to the normal talk/battle flow unchanged. Backstab resolves
  immediately as if the player had won the fight and chosen Execute:
  **-25 reputation** (vs. -10 for a real Execute -- explicit user
  request, unprovoked kill), `marks += combinedFoeLevels*10`, 2 random
  items granted, the same permanent `executedMask` bit set (`web`:
  `markExecuted("wsoldier", pending)`; Dreamcast: `npc_exec_bit(map_id,
  mark)` called directly off the matched `NpcDef`, since there's no
  battle struct to derive `trainer_kind`/`soldier_id` from), scream
  SFX + red fade, `TALK.backstabExecute`.
- **Save format bumped 6 -> 7**: `itemOrder` gained `bowieKnife`
  (index 19, end of bag), `flags` gained `drayKnifeOffered`. Every
  `save.ts`/`save.c` byte offset from `bag` onward (flags, party,
  checksum, dexSeen/Caught, executedMask, party2, activeParty,
  party2Count) shifted +1 to match `content/save.json`'s layout;
  still fits in the 256-byte blob (2 spare bytes). Dreamcast's `Bag`
  struct/`bag_field()`/`START_BAG_INIT` all updated by hand for the
  new field (auto-baked items list vs. hand-maintained struct --
  see the save-format section up top).
- Verified end-to-end on web via Playwright: Dray's catalog excludes
  the knife before the warning fires; negative reputation triggers the
  dialogue once; the knife appears after, disappears again once
  owned; Bram's shop never carries it; backstabbing an unspotted
  sentry moved reputation -20 -> -45 exactly, granted the sentry's
  combined-level*10 marks, and set its executed flag; an already-
  chasing (spotted) sentry falls through to the normal battle flow
  instead, confirming eligibility is LOS-gated correctly.
- Dreamcast side compiles clean (`make -C ports/dreamcast`,
  `verify_step.sh` all green) and was hand-traced against the web
  logic line-for-line, but **not hardware-verified** -- no Dreamcast
  emulator/hardware available in this sandbox, same standing caveat
  as every other Dreamcast-only feature in this log.

## Fix: pressing A/Z shouldn't trigger a warp gate, only walking onto it (Claude, 2026-09-22)

User reported pressing A (Z on keyboard) near a warp gate was
triggering the warp on its own, when only walking onto the tile
should. Found it in `interact()` (`engine.ts`): a fallback fired
`useDoor()` whenever the player was merely *adjacent* to any
`'D'`-tagged warp tile (`nearbyTiles()`'s 4 cardinal neighbors +
center) and pressed confirm -- not only when standing on it. Every
warp tile, including every `'D'` one across every map (`content/
world_parts/warps.json` has a dozen+), already triggers correctly by
walking onto it via `tryDoor()`/`tryMapWarp()`, which run
unconditionally every frame regardless of button state. Removed the
redundant button-triggered fallback and the now-dead `nearbyTiles()`
helper it was the only caller of. Dreamcast's `main.c` never had an
equivalent button-triggered path -- its warp check was always purely
position-based -- so this bug was web-only.

Verified via Playwright: standing one tile from the house door and
pressing A no longer warps (stays in house); walking exactly onto the
door tile still auto-warps with no button press, unchanged. No
content/Dreamcast rebake needed (pure `engine.ts` fix).

## Fix: picked-up items stayed interactable/visible forever (Claude, 2026-09-22)

User reported that one-time pickups (capture crystals and similar
loot) stayed interactable after being taken -- e.g. in the house or
CryTown (veld). Investigated every `role: "loot"` NPC (`crate` house,
`herb`/`gem` veld, `chest` cliffs, `quarryCrate`/`quarryShelf` quarry)
and found two separate bugs:

- **Visual**: the house crate and cliffs chest (`prop-crate`) were
  drawn unconditionally in `drawWorld()` regardless of whether they'd
  been looted -- unlike `herb`/`gem`, which were already correctly
  gated behind `!this.gotHerb`/`!this.gotFieldGem`. Added the same
  `!this.lootedCrate`/`!this.chestLooted` gates. Dreamcast's
  `draw_props()` (house) and `collect_npcs()`'s CLIFFS/QUARRY blocks
  had the identical bug (crate/chest/quarry crate+shelf sprites all
  drawn unconditionally) -- threaded `looted_crate`/`chest_looted`/
  `quarry_crate_looted`/`quarry_shelf_searched` through both
  functions' signatures and call sites to gate them the same way.
- **Re-grantable (worse)**: `quarryCrateLooted` and
  `quarryShelfSearched` were real class fields, correctly set by
  `setNpcFlag()`, but never included in `npcFlags()` -- the object
  `matchNpcScript()`/`npcHidden()` actually read from. Their `ifNot`
  gate on the grant step always saw the flag as unset, so both could
  be looted for infinite smoke bombs/dust. Dreamcast's equivalent
  `ft[]` wiring was already correct (not affected). Added both to
  `npcFlags()`.
- Beyond the visual fix, added a `{"hideIf": "<flag>"}` step (the
  same mechanism already used for `cageGate`/`shinigamiRock`/etc.) as
  the first script entry for all six loot NPCs, so
  `matchNpcScript()`/`npcHidden()` treat them as fully gone --
  no sprite, no interact, no leftover "it's empty" line -- the moment
  their flag is set, on both engines (Dreamcast's `hide_if` NpcStep
  field bakes and is read by `npc_match_step()` the same way).
- Verified via Playwright: interacting twice with each of the five
  pickups that grant a real item (house crate, veld herb/gem, quarry
  crate/shelf) grants exactly once -- the second interact is a no-op,
  confirming both the regrant bug and the hide-on-pickup behavior.
  `verify_step.sh` (bake, check_sync --strict, typecheck, Dreamcast
  build) all green.

## Fix: shelf (Quillpup starter) stayed interactable/mashable forever (Claude, 2026-09-23)

User reported that after Max takes Quillpup from the shelf, mashing
the interact button kept popping the "shelfEmpty" dialogue box open
and closed forever. Same root cause as the loot-pickup fix above,
just missed there since the shelf is `role: "starter"` (grants a
monster via `grantMonster`), not `role: "loot"` -- its script had the
identical two-step shape (`{ifNot: tookStarter, ...}` then an
unconditional `{talk: "shelfEmpty"}` fallback) with no `hideIf` to
stop the fallback from matching forever. Added the same
`{"hideIf": "tookStarter"}` first step used for the six loot NPCs.
The shelf's furniture sprite itself stays drawn afterward (unlike
crate/chest, it isn't a consumable that should vanish -- it's just an
empty shelf now, same treatment the bed gets), only the interaction
stops.

Verified via Playwright: with `tookStarter` true, mashing confirm 20x
near the shelf produces zero mode changes and never opens a dialogue
box (previously each press reopened/closed "shelfEmpty").

While rebasing this fix onto `main` (which had moved forward
significantly from unrelated automated work -- Backstab-eligibility
expansion, facing-only LOS, trainer level balancing, Dray shop
fixes), also caught and fixed a real compile break already present on
`main`: the Backstab-expansion commit used `NULL` in `main.c` without
including `<stddef.h>`, and this is a `-nostdlib -ffreestanding`
build with no libc -- `NULL` isn't defined anywhere else in the file.
`verify_step.sh` was silently reporting "ALL GREEN" despite `make`
actually failing (a pre-existing bug in that script's exit-code
handling, not touched here). Fixed by using `0` instead of `NULL`,
matching the rest of the file's freestanding-C convention (confirmed
via `make -C ports/dreamcast` succeeding clean after the change).

## Backstab review: LOS confirmed one-direction, forest soldiers wired in, Approach loop fixed (Claude, 2026-09-23)

User asked to review the repo, confirm fightable NPCs only have a
linear (one-direction) LOS, and make sure every fightable NPC not
standing on a warp tile can be Backstabbed. Both engines' `roamerLos`/
`roamer_los` and `soldierLos`/`soldier_los` already ray only along a
single stored facing direction (confirmed by an earlier, separately-
landed automated commit) -- no change needed there beyond a stale doc
comment on `roomerLos` that still described the old *omnidirectional*
"shares its row or column" behavior; corrected to describe the actual
one-direction ray.

Backstab eligibility itself had a real gap: the 3 FOREST patrol/scout/
sentry trainers live in their own `this.soldiers` array (`soldiers[]`/
`SOLDIERS[]` on Dreamcast), not the generic NPCS/`NPC_DEFS` script
table `canBackstab()`/`find_backstab_target()` walk -- so they could
never be offered a Backstab at all, on either engine, despite
`isFightAfter()`/`npc_after_is_fight()` and even `resolveBackstab()`'s
dead `after === "soldier"` branch already anticipating it. Added
`canBackstabSoldier()`/`openBackstabChoiceForSoldier()` (web) and an
equivalent eligibility check + `backstab_soldier_idx` state
(Dreamcast) wired into `interact()`'s/the manual-interact handler's
forest branch, using the same LOS/chase/knife gates as every other
target.

Wiring this in surfaced two latent bugs that would otherwise have
first triggered here:
- **id collision**: forest soldier ids are `"patrol"`/`"scout"`/
  `"sentry"`, and `"sentry"` is *also* the pending id of an unrelated
  Cliffs wsoldier trainer. `resolveBackstab()`'s generic tail
  (`TRAINERS[pending]`/`applyWsBeatFlags(pending)`) would have set the
  Cliffs Sentry's `beatSentry` flag from backstabbing the *forest*
  sentry. Isolated the `after === "soldier"` case completely --
  resolves `sol.beaten` directly (mirroring `finishWin()`'s real
  trainer-win behavior for forest soldiers, which never used the
  exec-mask system those flags gate anyway) and never touches the
  pending-keyed lookups. Dreamcast's equivalent code never had this
  risk (it keys everything off `NPC_PENDING_*` enum values, which
  forest soldiers were never part of), but was written the same
  isolated way for clarity/parity.
- **Approach reopening the same prompt forever (Dreamcast only)**:
  the "Approach" row's A-press did nothing but close `backstab_mode`
  -- the existing comment claimed the next interact would "fall
  through to `try_npc_script()`", but since the target's LOS/chase
  state is unchanged, the very next Z/A press would just re-match the
  same target and reopen the identical Backstab prompt, forever
  (never hardware-verified, so never caught). Fixed by making
  Approach resolve immediately: factored `try_npc_script()`'s
  per-target effect-application into `apply_npc_step()` and its
  `post_action` switch into `npc_after_to_post_action()` (both now
  reusable), and call them directly from Approach with the stored
  target index -- exactly mirroring web's `runNpc(pb.npc)`. Also
  relocated the `POST_*` `#define`s (previously mid-`main()`, after
  some now-shared-function-needing locals) to file scope; a pure
  preprocessor relocation, no behavior change, confirmed by nothing
  in the file using them before their original definition point
  either.

Verified via Playwright: an unspotted forest sentry + knife opens the
Backstab prompt; Approach on it opens the real "spots you" dialogue
(not a loop); a Backstab kill on it grants the right marks, sets
`sol.beaten`, and leaves the unrelated Cliffs `beatSentry` flag
untouched; the existing Cliffs wsoldier Backstab flow (a real
`beatSentry` case) still resolves correctly post-refactor. Dreamcast
side rebuilt clean from a `make clean` (checked directly for
`error:`, not just via `verify_step.sh`, given the false-green bug
found earlier this session) but remains hand-traced only -- no
hardware/emulator available to confirm on screen.

## WinAll dev code: passive mode instead of one-shot flag dump (Claude, 2026-09-23)

User asked to change the WinAll dev code (web preview only, no
Dreamcast equivalent) from an instant one-shot ("flip every trainer's
beat-flag right now") into a persistent mode: once entered, it stays
active for the rest of the playthrough (same lifetime as `devPassAll`
-- not reset by New Game), and from then on, engaging any not-yet-
beaten fightable NPC outside a Backstab skips both the pre-fight
dialogue and the battle itself, landing straight in the mercy menu
exactly as a real win would.

- Removed `devWinAllFlags()` (the old instant flag-dump) entirely and
  replaced it with a `devWinAllMode` boolean field, set by
  `submitDevCode("winall")`'s outside-battle branch (the in-battle
  "win this fight now" and in-mercy "clear battle" shortcuts are
  unchanged, and now also flip the mode on for later).
- Added `isMercyFightAfter()` -- narrower than the Backstab-eligibility
  `isFightAfter()` used elsewhere, since only calder/soldier(forest)/
  wsoldier trainers actually open mercy on a real win; cathleen/
  shinigami/mason resolve through their own one-off win dialogue
  instead and were left untouched (auto-opening a mercy menu they
  never show on a real win would be a bigger behavior change than
  "go straight to the mercy menu" asks for).
- Added `triggerDevWinAllFight(after)`: builds the same battle object
  a real encounter would (mirrors `advanceTalk()`'s calder/soldier/
  wsoldier dispatch) and instantly resolves it via the existing
  `devWinAll()` (itself unchanged, still reuses `finishWin()` so it
  can't drift from a real win's XP/flag/mercy handling).
- Wired the `devWinAllMode` check into every place a fight-leading
  dialogue would otherwise be shown for a not-yet-backstabbed target:
  `runNpc()` (manual interact and the Backstab-prompt's own Approach
  row, both funnel through here for calder/cathleen/shinigami/
  wsoldier NPCs), `interact()`'s FOREST branch (manual walk-up to an
  unalerted soldier), `updateSoldiers()`'s and `updateRoamers()`'s
  auto chase-catch (getting caught by LOS), and the Backstab choice's
  own soldier-specific Approach branch. In every case the existing
  canBackstab()/canBackstabSoldier() check still runs first and takes
  priority -- WinAll never suppresses a Backstab-eligible prompt, only
  the ordinary talk-then-battle path once Backstab isn't in play
  (declining it via Approach still triggers the instant win, per "not
  a backstab").
- Verified via Playwright: entering "winall" through the real Dev
  Codes UI no longer flips `beatCalder`/`beatSentry` instantly;
  engaging an unbeaten Calder, an unbeaten FOREST sentry, and an
  unbeaten Cliffs wsoldier sentry (no knife carried, so none are
  Backstab-eligible) each skip straight to mercy mode with no
  dialogue or battle in between; carrying the knife against the same
  Cliffs sentry still opens the Backstab prompt as normal, and
  choosing Approach from it (declining the Backstab) then triggers
  the instant win into mercy, confirming the "not a backstab"
  condition is respected. `verify_step.sh` all green; no content/
  Dreamcast changes needed (dev codes are web-preview-only, per the
  engine's own standing `devPassAll` doc comment).

## Turbo button: web-only rapid-advance for dialogue/battle (Claude, 2026-09-23)

User asked for a web-only on-screen "turbo" button that rapidly
presses A/Z (the confirm button) to fast-forward through dialogue and
battle messages, matching a classic turbo controller -- hold it, and
whatever confirm() would normally do fires as fast as each system's
own cooldown allows, instead of waiting on real button mashing.

- `Input` (`input.ts`) gained a public `turboHeld` boolean. `startLoop()`
  (`engine.ts`) queues one extra `queueA()` tap per rendered frame
  while it's true -- reusing the exact same `tapAQueued` mechanism the
  on-screen A button already drives, so it's paced by the display's
  refresh rate and self-throttled downstream by each system's own gate
  (`talkLock` for dialogue, phase transitions in battle), the same way
  a human mashing the real button would be.
- New `TurboBtn` component in `crymon-app.tsx` (same press-and-hold
  pattern as the D-pad's `PadBtn`, with `setPointerCapture` so a drag
  off the button still releases cleanly): sets `input.turboHeld` on
  pointerdown/up/cancel/leave. Added to the "How to play" list.
- `turboHeld` is also cleared by `Input`'s existing blur/tab-hidden
  handler (same one that clears held keys), so alt-tabbing away or
  losing focus mid-hold can't leave it stuck on.
- No Dreamcast equivalent (no on-screen UI to drive it there), same
  standing note `devPassAll` already carries for web-preview-only
  features.

Verified via Playwright (real pointer events via `page.mouse`, not a
synthetic click): holding Turbo advances a real multi-line dialogue
to completion without any manual confirm taps, and releasing it drops
`aria-pressed` back to false immediately. (One thing confirmed *not*
a bug: holding Turbo while standing next to a repeatable-dialogue NPC
re-triggers them the instant their line closes, same as a human
mashing A there would -- moving away first is what actually settles
it, exactly as intended.) `verify_step.sh` all green; web-only, no
content/Dreamcast changes.

## Button edge-detection fix, take two (Claude, 2026-09-23)

User reported button pressing was broken again: multiple times a
second the game should check for a press and fire once on detection,
then refuse to fire again until a release is detected (also polled
multiple times a second), at which point it's immediately ready to
fire again -- no wall-clock timer waiting out a fixed delay before
resetting. Turbo was explicitly exempted (its extra-tap-per-frame
design is intentional and stays as-is).

- Root cause: `Input.dir()` (`input.ts`), which backs `up()/down()/
  left()/right()` for menu cursor navigation, still carried a
  `performance.now()`-based auto-repeat timer (`dirHeldAt`/
  `dirLastFire`, 55ms initial delay then a 28ms repeat interval) that
  fired repeatedly for as long as the touch D-pad or a gamepad stick
  stayed pushed past threshold, rather than requiring a fresh
  release-then-repress per step. That timer had been made more
  aggressive by an earlier, unrelated commit tightening virtual-button
  lag, which is the most likely reason it read as "broken again."
  Keyboard-driven menu navigation was unaffected (keys already went
  through plain `pressed()` edge detection) -- the bug's real impact
  was specifically the on-screen D-pad and gamepad sticks.
- `confirm()/cancel()/start()/select()` were re-checked and were
  already correct: keyboard via `pressed()` (true exactly once per
  press, resets the instant `held` goes false), touch/gamepad via the
  single-queued-tap model (`queueA()` etc., consumed once per
  `beginFrame()`/`consumeQueuedFace()`) -- no changes needed there.
  World movement's `axis()` is intentionally continuous (not a
  discrete button) and was left alone.
- Fix: removed the `dirHeldAt`/`dirLastFire` fields and the timer
  branch from `dir()` entirely. It's now pure edge detection, the same
  shape as `confirm()`/`cancel()`: `keys.some(pressed) || (active &&
  !was)` -- fires exactly once when a key is pressed or the axis
  crosses threshold, stays silent no matter how long it's held, fires
  again only after going inactive (released) and re-crossing
  threshold. Same principle as every other button now, everywhere.
- Confirmed Dreamcast's `main.c` never had this pattern to begin with
  (grepped for any repeat/held-duration timer logic, zero matches --
  it's already pure edge detection like `up_now && !prev_up`
  throughout). Web-only fix, no Dreamcast or content changes.
- Verified two ways: (1) an isolated unit test dynamically importing
  the real `Input` class from the Vite dev server inside a Playwright
  page (no test runner is configured in this repo) -- held touch
  D-pad input fires exactly once across 30 simulated frames, a
  release-then-repress fires exactly once more, and a held keyboard
  arrow key likewise fires exactly once across 30 frames; (2) a real
  end-to-end smoke test holding the on-screen D-pad button for 0.8s
  via actual `page.mouse` events against the running UI, confirming
  no crash and correct single-step behavior. `npx tsc --noEmit` clean.

## Button edge-detection, take three: frame-vs-tick mismatch, plus warp gate footprint (Claude, 2026-09-23)

User reported the prior take-two fix made things worse: buttons
sometimes did nothing at all, other times a held menu direction
"zipped" as if turbo were on. Also reported walk-on warp gates felt
too precise and asked for them to cover the whole tile they sit on.

Root cause of the button regression: `Input.beginFrame()`/`endFrame()`
(which reset the per-button "used" gate and snapshot `prev` for
`pressed()`/`dir()` edge detection) were anchored to each *rendered*
frame, but `engine.ts`'s `startLoop()` runs a fixed-timestep
accumulator (`STEP = 1/60s`) that can execute zero, one, or several
logic ticks per rendered frame:
- **Zero ticks** (a high-refresh display, where less than one STEP of
  real time has accumulated since the last frame): `endFrame()` still
  ran every rendered frame regardless, so it could snapshot a freshly
  pressed key into `prev` *before* any `update()` tick ever saw it --
  silently swallowing the press. This is the "nothing happens" half
  of the report.
- **Several ticks** (a catch-up burst after a stutter): `used` was
  cleared once per extra tick via `consumeQueuedFace()`, but `prev`
  only advanced once for the whole rendered frame, so a held key's
  `pressed()`/`dir()` check re-passed on every extra tick within that
  same burst -- firing a menu-cursor move once per tick instead of
  once per real press. This is the "zips like turbo" half.
  `verify_step.sh`'s prior take-two testing missed this because
  Playwright + a synthetic `Input` unit test never produces a genuine
  multi-tick catch-up burst or a sub-STEP high-refresh frame on its
  own.

Fix: replaced `beginFrame()`/`endFrame()`/`consumeQueuedFace()` with
`stepBegin()`/`stepEnd()`, called once each per logic tick (inside
`startLoop()`'s `while (this.acc >= STEP)` loop, wrapping each
`update(STEP)` call) instead of once per rendered frame. `used`
clears and the `prev`/`prevAxisX`/`prevAxisY` snapshot now always
advance together, exactly once per tick, so a held button can only
ever register once per real press-hold-release cycle regardless of
the display's refresh rate relative to the fixed 60Hz logic rate.
`pollGamepad()` and Turbo's per-frame `queueA()` stay outside the
loop, unchanged -- both are legitimately tied to render cadence, not
logic ticks. Verified with a true unit test against the real `Input`
class: a simulated 5-tick catch-up burst with a key held the whole
time fires exactly once (not five times); a key pressed with zero
prior ticks that frame is still seen on the very next tick (not
swallowed); a touch D-pad held across a 4-tick burst also fires
exactly once.

Warp gate size: `tryMapWarp()` used to test only the player's single
center-anchor pixel against `tileAt()`. Since that's already
tile-quantized (`Math.floor(x / TILE)`), it in theory already covered
a full 32px tile -- but a single pixel test only fires the instant
the anchor itself crosses the tile boundary, with no forgiveness for
where within (or just short of) the tile the player actually is,
unlike `tryDoor()`'s separate "ahead of facing direction" pre-trigger
that doors already got. Changed it to test the player's whole r=10
collision footprint (same box `blocked()` uses) against every warp in
`WARPS`, firing on the first point that matches -- so every warp gate,
not just doors, now triggers as soon as any part of the player
overlaps its tile, with the same ~10px of give in every direction
that movement collision already allows. Verified via Playwright: an
isolated `setPos()` sweep across and beyond the house door's tile
bounds confirms the trigger now extends a further ~10px past each
edge of the tile (previously exact pixel-for-pixel only); a real
walk-through-the-door test (real keyboard hold, `blocked()` collision
active) still warps correctly across the whole practically-walkable
width, unchanged.

`verify_step.sh` all green; Dreamcast rebuilt clean from `make clean`
and checked directly for `error:` (not just verify_step.sh, per the
standing false-green caution) -- `main.c` untouched, so no changes
there; these were web-only bugs (`main.c`'s input handling and warp
checks are already pure edge/single-tick, with no equivalent
frame/tick split to have this bug in the first place).

## Status conditions now count toward the capture-rate "vulnerable" bonus (Claude, 2026-09-23)

Every capture crystal's own description text ("Base 100% minus the
CryMon's level, strength, and current HP. Status adds +50.") already
promised a status condition adds the same flat +50 a stat debuff
does, but the code never actually checked status -- both
`captureChance()` call sites in `engine.ts` (item-row % preview and
the real catch roll) and Dreamcast's `battle_capture_chance()` in
`main.c` fed it `foeDebuffed()`/`battle_foe_debuffed(b)`, which only
looks at stat mods/stages, never `b.foe.status`. User asked to add
Burned/Poisoned/Paralyzed/Confused/Exhausted to the set of states
that trigger the bonus.

- New `foeVulnerable()` (`engine.ts`) / `battle_foe_vulnerable()`
  (`main.c`): `foeDebuffed()` OR foe has any status other than
  `"none"`. Deliberately kept separate from `foeDebuffed()` itself
  rather than folding status into it -- that function is also read by
  Mana Surge's 2x-damage check (`castSpell`'s manasurge branch /
  `main.c`'s Mana Surge cast), and status conditions widening an
  unrelated damage-multiplier mechanic wasn't asked for. Both capture
  call sites on both engines now pass the new function instead.
  `captureChance()`/`capture_chance()` themselves are unchanged --
  they already had the +50 branch on their `vulnerable` bool, it was
  only ever being fed the wrong (stat-only) value.
- `verify_step.sh` all green; Dreamcast rebuilt clean from `make
  clean`, checked directly for `error:` per the standing false-green
  caution since `main.c` was touched this time.

## Overworld sprite depth-sort + web-only Turbo on the T key (Claude, 2026-09-23)

Two small, unrelated web-only asks in one pass.

**Depth sort**: `drawWorld()` used to draw all overworld actors (map
NPCs, rival, Anne, forest soldiers, Cathleen) in a fixed list order,
then always drew Max dead last -- so she was always drawn in front of
any NPC she happened to be standing above, even when that NPC was
physically lower (closer to "camera" in this top-down/orthographic
view) and should have been in front of her instead. Dreamcast's
`main.c` already had the correct behavior here (`ws_sort_and_draw()`,
an insertion sort by world-y with the player pushed into the same
list as the NPCs -- see that function's own doc comment, dated from
an earlier leg) -- this was a web-only gap. Changed `drawWorld()` to
queue every actor as a `{y, draw}` entry instead of drawing
immediately, then sort the queue ascending by world-y and draw in
that order once collected -- same painter's-algorithm shape as the
already-proven Dreamcast version, just expressed as `Array.sort`
instead of an insertion sort. Static props (house furniture, doors,
carts, the cliffs chest) stay outside the queue and still draw first,
unchanged -- the ask was about character sprites overlapping each
other, not sprites vs. the environment.

Verified visually via Playwright: positioned Max a few pixels above
vs. below Cathleen's overworld sprite (grove) and screenshotted both
-- with Max above (should be behind), Cathleen's dark portrait
dominates the overlap; with Max below (should be in front), Max's
sprite dominates with only Cathleen's hood peeking out above her
head. Confirms the sort direction is right, not just that sorting
happens.

**Turbo on T**: the on-screen Turbo button already worked by setting
`Input.turboHeld` while held; `startLoop()` queues an extra confirm
tap per rendered frame whenever that's true. Added `KeyT` to
`GAME_KEYS` (so it gets the same held-key `preventDefault()`
treatment as every other game key) and changed the check to `if
(this.input.turboHeld || this.input.held("KeyT"))` rather than
folding T into `turboHeld` itself -- that field also drives the
on-screen button's own `aria-pressed` visual state, which shouldn't
light up just because the keyboard key is held. "How to play" text
updated to list T next to the on-screen button. No Dreamcast
equivalent, same as Turbo itself -- there's no on-screen UI to have
driven it there in the first place, and this is purely an
alternate *input path* onto the exact same already-web-only feature.

Verified via Playwright: approached Wren, opened her dialogue with a
real confirm tap, held `KeyT`, and confirmed the conversation advanced
across multiple lines with no further taps -- same fast-forward
behavior the on-screen button already had, confirmed working.

`verify_step.sh` all green; no `main.c`/content changes needed for
either half (Dreamcast already had the correct sort, and Turbo has no
Dreamcast surface to add a key to).

## No Backstab on Cathleen/Shinigami; Father's party was unreachable (Claude, 2026-09-23)

Three requests: remove Backstab eligibility from Cathleen and
Shinigami, fix Father's party (his "6 fresh capture slots") not
appearing when he joins, and make Left/Right in the CryMon menu swap
between Max's and Father's party lists.

**Backstab**: `isFightAfter()` (`engine.ts`) / `npc_after_is_fight()`
(`main.c`) is the sole gate `canBackstab()`/`find_backstab_target()`
check before offering the Bowie Knife prompt. Removed `"cathleen"`
and `"shinigami"` from web's list and `NPC_AFTER_CATHLEEN`/
`NPC_AFTER_SHINIGAMI` from Dreamcast's -- both still fight normally
via the ordinary talk-then-battle path, just never through Backstab.
Verified via Playwright: approaching an unspotted Cathleen with the
Bowie Knife carried now opens her normal `cathleenSpot` dialogue
directly (mode stays "world", never "backstab"), where it used to
open the Approach/Backstab prompt first.

**Father's party was real, just unreachable**: `seedFatherParty()`
was working correctly all along (verified: swapping does put
`["mossback","quillpup"]` into `this.party`) -- the actual bug was
that the swap trigger itself could never fire from the world screen.
`updateWorld()` had its own `Tab`/`KeyQ` → `swapParties()` check, but
the *outer* `update()` dispatcher already intercepts `Tab`/`KeyQ`
several lines earlier via `this.input.select()` (which also matches
Tab/Backspace) to open the Bag, and returns before `updateWorld()`
ever runs that tick. The world-level swap check was 100% dead code --
confirmed by dispatching a real synthetic `Tab` keydown from the
world screen and watching `mode` become `"bag"`, never `"party"`.
Removed the dead check entirely rather than trying to out-prioritize
Bag's own (correctly documented, still-wanted) Tab/Q binding.

The *in-menu* Tab/Q swap (`updateParty()`'s own separate check) was
never affected by this and already worked correctly once you'd
actually gotten into the party menu -- but nothing told the player
that was the only way in, and the menu's own hint text still said
"Left/Right settings", stale since Leg 2.3 moved Settings to the
pause menu and never wired Left/Right to anything in the party list
view at all.

**Fix**: added `this.input.left() || this.input.right()` as an
additional trigger alongside the existing in-menu Tab/Q check (same
`swapParties()` call), corrected the party menu's hint text to "Z
choose Left/Right swap party Start close", and updated the "How to
play" panel's Party line to describe the real, working path (open
the CryMon menu, then Left/Right) instead of the dead Tab/Q-from-
anywhere claim. Dreamcast has no `party2`/swap mechanic at all yet
(`revived_father` there is only a reputation/title flag) -- web-only,
matching every other Father-party feature so far.

Verified via Playwright (real dispatched keydown/keyup, not
`page.keyboard` which Chromium's own Tab-focus-navigation seems to
swallow before it reaches the page in headless mode): from inside the
party menu, ArrowRight swaps to Father's party (`["mossback",
"quillpup"]`, HUD flashes "Father's party takes the field."), and
ArrowLeft swaps back to Max's.

`verify_step.sh` all green; Dreamcast rebuilt clean from `make
clean`, checked directly for `error:` per the standing false-green
caution since `main.c` was touched.

## Dray's knife shop was wiping his whole inventory; split his reputation spiel across two boxes (Claude, 2026-09-23)

Two bugs in the same negative-reputation flow: (1) once Dray offers
the Bowie Knife, his shop showed *only* the knife instead of the
knife added to what he already sells, and (2) the offer line itself
("I've heard of your reputation... Sickos like you sometimes prefer
up close and personal action.") got cut off mid-sentence, ending at
"Sickos like".

**Inventory wipe**: the `drayKnifeShop` completion handler
(`engine.ts`) did `this.shopStock.dray = { bowieKnife: 1 }`, replacing
his entire rolled stock object instead of adding to it; Dreamcast's
`POST_DRAY_KNIFE_SHOP` case had the identical bug, zeroing every
`shop_stock[3][i]` before setting just the knife slot. Both engines
already have a `shopCatalog()`/`shop_rows()` filter that correctly
includes the knife once the offer's fired (`drayKnifeOffered`/
`dray_knife_offered`) without needing this override at all -- fixed
by dropping the wipe: web now only rolls stock if it doesn't exist
yet (`if (!this.shopStock.dray) this.rollShopStock("dray")`) then sets
just `.bowieKnife = 1`; Dreamcast just sets `shop_stock[3][19] = 1`
directly, since `roll_all_shop_stock()` (called at boot/reset/rest)
already guarantees his stock array exists with everything else
already rolled by the time this fires. Verified via Playwright:
Dray's buy list now shows his full normal catalog (Moss salve, Linen
wrap, Bitterroot, Calm Draft, Burn Salve, capture crystals, etc.)
alongside the knife, not just the knife alone.

**Cut-off dialogue**: `drawTalk()`'s portrait dialogue box wraps text
at 20 chars/line but only ever draws the first 4 wrapped lines
(`.slice(0, 4)`) -- a fixed box-height constraint every other line of
dialogue in the game is already written to fit inside, which this one
line (127 chars, needs ~7 wrapped lines) blew straight through,
silently dropping everything past "Sickos like". Rather than change
that shared rendering constraint (touching every dialogue box in the
game), split `drayKnifeOffer` in `content/dialogue.json` into two
beats at the existing sentence boundary -- "I've heard of your
reputation. Can I interest you in a knife?" then "Sickos like you
sometimes prefer up close and personal action." -- each of which
wraps to exactly 4 lines, fitting the box precisely. Updated
`engine.ts`'s inline fallback array (`TALK.drayKnifeOffer || [...]`)
to match. Verified via Playwright: the two lines now display as two
separate boxes advanced by pressing Z, both fully visible, nothing
truncated.

`verify_step.sh` all green (content rebake picked up the split
dialogue automatically -- no Dreamcast dialogue-system changes needed
beyond the `main.c` stock fix, since Dreamcast's `seq_lines`/
`TALK_LEN()` sequencing already advances beat-by-beat the same way
every other multi-line TALK array in the game does). Dreamcast
rebuilt clean from `make clean`, checked directly for `error:` per
the standing false-green caution.

## Stray brown blob on the Marsh->Quarry warp tile (Claude, 2026-09-23)

User attached a screenshot of a small brown/maroon blob sitting on
the ground next to Max on the marsh path and asked for it removed.
Traced it to `paintTile()`'s procedural rendering for tile character
`X`: `content/maps.json`'s marsh rows use `X` at (17,10) purely as a
warp tile (`warps.json`: marsh `X` -> quarry) -- but `X`'s *default*
pixel art everywhere else in the game (veld's cart, cliffs' chest) is
a crate/chest-shaped blob, drawn safely because a real `drawProp()`
sprite always covers it there. Marsh has no special-case prop drawn
over its `X`, so that blob rendered bare in the middle of the path --
not decorative litter and not safe to delete outright, since `X` is
the live warp connecting Marsh to Quarry.

Fix: added a marsh-specific override in `paintTile()` (same
`ch === "X" && this.world.mapId === "..."` pattern already used for
`F`'s house-only override just above it) so marsh's copy of `X`
renders as a plain path tile instead -- the same look `=`/`O`/every
other warp character already gets. The warp itself, its destination,
and every other map's `X` usage are untouched. Confirmed Dreamcast's
`draw_tile()` has no `X` case at all and already falls through to
plain grass by default -- this was web-only, no `main.c` change
needed.

Verified via Playwright: positioned Max next to marsh's `X` tile
before and after the fix -- before, a dark reddish-brown blob sits
beside her matching the user's screenshot pixel-for-pixel; after, a
plain tan path tile, indistinguishable from the rest of the corridor.

`verify_step.sh` all green; web-only change (`src/game/engine.ts`).

## Lieutenant Lead: stationary, unbackstabbable, no more save-wiping win; dead warp gate + note removed; autosave disabled (Claude, 2026-09-23)

Five requests from one screenshot: make Lieutenant Lead stationary,
not Backstab-eligible, only speak/fight on interact; remove a leftover
warp-gate tile and a stray "behind Shinigami" line; disable autosave
and the automatic save-reload his win was triggering.

**Root cause investigation turned up a real, separate bug along the
way**: `npcFlags()` (`engine.ts`) -- the flags object every script
match (`matchNpcScript`, `npcHidden`, `updateRoamers`) reads -- was
missing `beatLieutenantLead` entirely, so his `hideIf:
"beatLieutenantLead"` script step could never fire; he stayed
interactable and re-fightable forever, win or not. Confirmed by
setting the flag directly and watching him still auto-chase and
re-open his spotted dialogue. Fixed by adding the missing key.
Dreamcast's own flag table already had the equivalent
(`FLAG_BEAT_LIEUTENANT_LEAD`) -- this half was web-only.

**Stationary + unbackstabbable**: he shares the generic `"wsoldier"`
battle-trigger with every roaming ambush trainer (marshBog, forest
soldiers, etc.), and `roamableNpc()`/`npc_def_roamable()` couple
"roamable" to that same tag -- dropping `wsoldier` from his script
would've also broken the shared `startWsBattle()` wiring. Excluded him
by id/mark instead: `roamableNpc()` (web) and `npc_def_roamable()`
(Dreamcast) now return false for him specifically, and
`canBackstab()`/`find_backstab_target()` do the same, so he can never
be chased into or Backstabbed, while `runClosestNpc()`'s ordinary
walk-up-and-interact path (unaffected by any of this) still handles
his talk/battle normally. Verified via Playwright: standing next to
him for a full second no longer auto-triggers anything; a manual
interact still opens his normal spotted dialogue (not a Backstab
prompt) even with the knife carried.

**Save-wiping win**: his win handler passed `"leadThanksGO"` as
`afterTalk`, which called `startFade("hfGameOver")` -- the exact same
fade action the genuine Heavenfall party-wipe game-over uses, which on
completion calls `reloadLastSaveOrTitle()`. Beating him was silently
reloading (or dropping to title on) whatever the last autosave
happened to be. Removed the `leadThanksGO` branch entirely (matching
Dreamcast's now-`POST_NONE` `post_action`, replacing the removed
`POST_LEAD_GAMEOVER`) -- his win text plays and the game just returns
to normal play, same as it always should have. The real Heavenfall
game-over path (`beginHeavenfallGameOver()`/`BAFTER_LOSS`) is
untouched. Verified via WinAll dev mode: after his placeholder win
text, mode stays `"world"` on the same map (not reloaded), and
`beatLieutenantLead` is `true` -- re-interacting afterward now
produces nothing, confirming the `npcFlags()` fix hides him for good.

**Dead warp gate**: `veld`'s `O` tile (a single gap in the north
border wall, directly above his mark) warped to `weepingroad` -- one
of the large set of Kabbalah-named maps that are unfinished/unreachable
placeholder content, not part of the actual demo. Removed both the
outbound (`veld.O -> weepingroad`) and the now-orphaned return
(`weepingroad.1 -> veld.O`) warp entries from `warps.json`, and sealed
the map tile itself from `O` to `#` (solid wall) -- leaving it walkable
but inert would've been worse than before. `check_sync --strict`
correctly flagged the orphaned return warp on the first pass (missing
reciprocal spawn), confirming both entries needed removing together.

**Stray note**: `this.note("A path opened behind Shinigami.")` fires
from an unrelated code path (the Scroll choice's Heavenfall branch,
`gauntletUnlocked`), not from Lieutenant Lead at all -- removed the
flavor text only, left the functional `gauntletUnlocked = true;` flag
untouched since the user asked only about the dialogue reference.

**Autosave**: `persist(manual = false)` used to write on nearly every
warp, NPC grant, and tab-hide, so "Continue" from the title screen
never actually resumed where the player last manually saved --
matching the reported "loading last save is broken." Every non-manual
call is now a no-op (`if (!manual) return false;` as the first line);
the pause menu's explicit Save and the dev `saveNow()` hook are
unaffected, still the only path that reaches `writeSaveBlob()`.
Confirmed Dreamcast has no autosave path at all to begin with (its one
`SaveLive` write block is the manual pause-menu Save) -- nothing to
change there.

`verify_step.sh` all green; Dreamcast rebuilt clean from `make clean`,
checked directly for `error:` per the standing false-green caution.

## CryTown north gate restored behind Lieutenant Lead (Grok, 2026-09-25)

The sealed north exit is open again. `veld` row 0, column 15 (the wall
tile directly north of Lieutenant Lead's `L` on row 1) is warp tile
`O`. `veld.O` goes up onto `weepingroad` spawn `1` (`oy` -32, one tile
inside the road). Coming back, `weepingroad.1` spawns on `veld.O` with
`oy` 64, which lands on the grass one tile south of Lead, so he stays
between the player and the gate. No `need` flag: he is still non-solid,
the gate is only behind him in space. `check_sync --strict` and
typecheck passed. No Dreamcast toolchain in this sandbox, so the CDI
rebuild is left to CI.

## Path maps are scale models of the county sheet (Grok, 2026-09-25)

The 22 path maps and the Weeping Road were straight 24×6 or 6×24 halls.
They are now the county sheet's bands rasterized at 8 pixels per tile
(`tools/build_sephirot.py --paths-only`, `build_scaled_path`). A band
that is diagonal on the sheet is a stairstep corridor in the game; an
axis-aligned band stays a rectangle. Thickness follows the sheet: the
band is one eighth of its straight-line length, so a long path is wider
than a short one. Warp marks are unchanged: `1` is still the A end and
`2` the B end, and the tile the existing arrival offset steps onto is
floor. Cities were not resized. `check_sync --strict` and typecheck
passed. No Dreamcast toolchain here; CI rebuilds the CDI.

## County sheet pushed (Grok, 2026-09-26)

The Tree of Life county sheet that had only lived under
`/workspace/artifacts` is now the player-facing map:
`public/maps/sorrow-county-town-map.svg` and
`public/maps/sorrow-county-town-map.png`. It is the hand layout (thick
bands, stairstep diagonals, Weeping Road meeting CryTown), not a fresh
run of `tools/generate-town-map.mjs`. Regenerating that tool will
overwrite it.

## Rectangle NPC generator removed (Grok, 2026-09-26)

`tools/gen_art_debt_2_0.py` is gone. Nothing else imported it. It was
the `draw_walker_base` script that painted Bogwalker, Reedguard, Fenn,
and the Quartz placeholder as flat rectangles. The sprites it already
wrote are still in `public/sprites/`. It is not a way to regenerate
them.

## Flat walkers replaced with generated pixel art (Grok, 2026-09-26)

Bogwalker, Reedguard, and Fenn (frames 1–4 and portraits) are generated
16-bit pixel art, keyed with the flood-plus-hole-punch plus 2px
inner-border clamp, then fitted to 48×64 (feet down) and 160×200.
Quartz frames 1–4 are the same new standing sprite. Frame 2 was the
only file that script wrote, but 1, 3, and 4 were the same flat style
and would have flashed back to it on the idle cycle. No magenta left
in the shipped PNGs.

## County map title fixed; orphaned predecessor asset removed (Claude, 2026-09-26)

Confirmed with the user: `public/maps/sorrow-county-town-map.svg`/`.png`
are the canonical, player-facing map of Sorrow County -- the region
that contains every playable in-game map. Both its committed title
(the `content/town_map.json` `"name"` field and the SVG's own header
text) read **"CryMon overworld map layout"** instead of "Sorrow
County" -- that's `content/world_map_layout.json`'s own doc-description
string, which `tools/generate-town-map.mjs` was defaulting to
(`name: layout.name ?? "Sorrow County"` picks `layout.name` whenever
it's non-null, so the fallback never fires). Fixed by hand, not by
rerunning the generator: per the "County sheet pushed" note above,
today's `sorrow-county-town-map.svg` is the hand-authored Tree-of-Life
layout, and regenerating would overwrite it (confirmed the hard way --
ran `generate-town-map.mjs` once to test the fix, saw it silently
resize several Tree-of-Life path cells against the current
`content/maps.json`, and reverted before committing). Changed only the
title text in `content/town_map.json`, `content/world_map_layout.json`,
and the SVG header; also fixed the generator's default so a future
*legitimate* regen doesn't reintroduce the same bug.
**Both follow-ups flagged above are now fixed too (Claude, same day):**

`content/town_map.json`'s node geometry was stale against
`content/maps.json`'s current Tree-of-Life path sizes. Fixed by
running `generate-town-map.mjs` for real this time, then restoring
the hand-authored `sorrow-county-town-map.svg` over its regenerated
output afterward (diffed node-by-node first: same 44 ids before and
after, only `realSize`/`x`/`y`/`cellW`/`cellH` changed, on exactly
the 22 path cells plus CryTown's width -- no nodes added, removed, or
renamed). `docs/generated/sorrow-county-town-map.md` was left as the
generator produced it (it's a plain generated dev doc, not
hand-authored). The in-game pause-menu map screen now reads correct
proportions for every cell.

`public/maps/sorrow-county-town-map.png` had the old title baked
into its raster pixels. No `imagemagick` in this sandbox, so
rasterized the corrected SVG with the pre-installed headless
Chromium via Playwright instead (`chromium.launch({executablePath:
"/opt/pw-browsers/chromium"})`, screenshot clipped to the SVG's own
860x1565 `width`/`height`) rather than waiting on the `Publish map
PNG` GitHub Action.

Removed `public/maps/crytown-world-map.svg`: an orphaned predecessor
of the county map from before the "Rename world map to Sorrow County"
commit (`ef321b0`) generated by a since-abandoned approach. Confirmed
zero references anywhere in the repo before deleting.

Left "Town Map" terminology itself alone by explicit user choice:
`TOWN_MAP`, `openTownMap`/`drawTownMap`/`mode === "townmap"` in
`engine.ts` (and its Dreamcast mirror in `main.c`),
`tools/generate-town-map.mjs`, the `.github/workflows/town-map-*.yml`
names, and `docs/generated/sorrow-county-town-map.md`'s own title are
a deliberate Pokemon FireRed "Town Map" item homage (that item shows
the whole region too), not a naming mistake -- untangling it across
both runtimes wasn't asked for in this pass.

`python3 tools/check_sync.py --strict` passes. No Dreamcast rebuild
needed: neither `content/town_map.json` nor
`content/world_map_layout.json` feed `tools/bake_content.py`.


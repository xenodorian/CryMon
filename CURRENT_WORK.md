# CURRENT_WORK.md

Live coordination doc for every agent working this repo (Claude, Grok,
ChatGPT, others). Read before starting anything; update before you stop.

**Standing house rules:**
- **Commit-and-push per step, always.** After finishing each individual
  step/sub-step (not each large multi-part item — each *step*), commit
  and push it to `main` (or to a branch if you're using one — merge
  branches back periodically, don't let them sit open indefinitely).
  Don't batch multiple steps into one commit. This is so a session that
  gets cut off mid-work only loses the one step in progress, not
  everything before it.
- **"Ship it" / "ship the build" is a specific user trigger,** distinct
  from the commit-per-step rule above. When the user says either
  phrase, it means: run the *entire* remaining deployment pipeline right
  now — `bake_content.py` → `gen_sprites.py` → `check_sync --strict` →
  web typecheck → `make -C ports/dreamcast` → `make -C ports/dreamcast
  cdi` → commit/push source → let (or trigger) the CI bot rebuild the
  CDI → confirm the Pages deploy actually re-ran for that commit (bot CDI
  pushes now `workflow_dispatch` deploy-pages — see CI gap CLOSED note) → end state is a freshly baked,
  playable CDI sitting in the GitHub Pages download slot, matching
  whatever's on `main` at that moment.
- **After finishing a large milestone that includes a bug fix,**
  run that same full deployment pipeline on your own, without waiting
  for the user to say "ship it." Routine feature-step commits don't
  need this — just bug-fix milestones (e.g. the kind of thing that
  changes whether the game actually works right, not just what content
  is in it).
- Do not hand-replace `world.json`. Do not empty `npcs`.
- **Cathleen is the only CryMon who speaks** (unless/until a leg below
  changes that explicitly — see Leg 2/3, which do add named-CryMon
  interactions for Heavenfall).
- Art assignment: **superseded for the art-debt task below.** The old
  rule was "ChatGPT A: no PNG work, Claude B: encode only." Leg 2 now
  explicitly asks ChatGPT or Grok to produce and push the missing art
  (see Leg 2.0). That's a deliberate override for that one task, not a
  blanket lift of the old division — don't take it as license to redo
  other agents' art lanes without asking.
- Verification bar for every push, no exceptions: `python3
  tools/bake_content.py --content content --out ports/dreamcast/src` →
  `python3 ports/dreamcast/tools/gen_sprites.py` → `python3
  tools/check_sync.py --strict` (expect only the art-debt FAIL below,
  nothing else) → `npm run typecheck` → `make -C ports/dreamcast` →
  `make -C ports/dreamcast cdi`. Fetch + rebase immediately before
  every push; never trust a base you fetched more than a few minutes
  ago, this repo has multiple agents pushing straight to `main`.
- **Magenta-keyed art:** generate on solid magenta (`#FF00FF`). Edge
  flood is **not** enough — enclosed cutouts stay magenta. Pipeline,
  in order: (1) flood-from-edge key, (2) punch enclosed magenta
  background holes, (3) 2px inner-border R→G clamp. Do **not**
  traditional-despill. See "Magenta keying" below.

---

### Magenta keying (when generating art)

Applies to every new sprite, item icon, walker, and portrait generated
against a chroma-key background. Ship files with a **transparent**
background — never leftover magenta, never a solid-color plate.

**Order matters.** The border clamp measures distance to already-
transparent pixels, so it cannot color-correct filigree / ring /
cage rims until those holes are actually punched. Do not skip
ahead to step 4 after only an edge flood.

1. **Flood-from-edge key.** Chroma-key magenta (and JPEG-fringed
   near-magenta) connected to the image edge to alpha 0. This only
   clears the *outer* background. Enclosed interiors (filigree gaps,
   hanging-ring holes, cage cutouts) are not reachable from the
   edge and **stay magenta** after this step alone.
2. **Punch enclosed magenta holes.** Required second pass, not
   optional. Walk leftover is_key blobs that are majority true
   chroma-key magenta (high R, low G, high B) and set them to alpha
   0. That is background showing through the art, same as the outer
   plate. Gem / eye / trim color that isn't chroma-key magenta
   stays. Skipping this is what left pink inside the crystal cages.
3. **Do not traditional-despill.** Do not delete a 1px/2px fringe of
   "magenta-ish" pixels around the silhouette. That eats into the
   sprite (hair, outlines, gem cages). `strip_magenta.py`'s 1px
   `fringe` pass does exactly this — skip it / do not rely on it for
   new art.
4. **Then** the 2px inner-border clamp (color-correct, don't punch).
   Only after steps 1 **and** 2: every remaining opaque pixel within
   **2 pixels** of a transparent pixel (outer silhouette *and* inner
   hole rims). If `R > G`, set `R = G`. Leave green, blue, and alpha
   unchanged. Magenta spill is R-heavy; clamping R down to G kills
   the pink halo without eating the art.

Command (do not run bare `strip_magenta.py` — that still does the
legacy 1px fringe-delete across the tree):

```
python3 tools/strip_magenta.py key-clamp --size 128 --pad 24 -o DEST SRC
```

`--size 0` keeps the source resolution. `key-clamp` runs steps 1, 2,
and 4 in that order. QC before commit: corners transparent, no
leftover `#FF00FF` on the silhouette *or* in interior cutouts, no
magentish halo, interior gem colors untouched.

---

## CI gap — CLOSED (Grok C)

`GITHUB_TOKEN` pushes still cannot re-trigger other workflows (GitHub
loop guard). Closed by option 2: after a successful CDI commit+push in
`build-dreamcast.yml`, a step runs `gh workflow run deploy-pages.yml`
with `permissions: actions: write`. Pages re-packages
`ports/dreamcast/crymon.cdi` into the download slot without a PAT or
manual re-run.

If deploy-pages ever fails to start, check the Build Dreamcast CDI job
log for the "Trigger Pages deploy" step and the Actions tab for a
queued Deploy CryMon Web run.

---

## Completed work (condensed — see git log for full detail on any of these)

- **Marsh trainers (Bogwalker, Reedguard), crystal wardens Quartz and
  Opal, forest/ruins trainers (Ranger/Scout/Keeper/Warden):** all live
  on web and Dreamcast, JSON-defined, full `wsoldier`/`pending` battle
  wiring on both engines. NPC art is still placeholder for several of
  these — see the art-debt list below.
- **Quarry (`#23-26`, closed):** warp gated on `beatSentry`, `quarryDriller`
  trainer defined and fully wired web + Dreamcast, integration pass
  green.
- **Endgame v1 — father/Heavenfall choice → gauntlet → commanderFinal
  boss → branched credits (`#18`, `#28-33`, closed):** the choice now
  warps the player onto a `gauntlet` map, capped by a single
  `commanderFinal` boss fight (lead `boulderam` 12, bench
  `duskhorn`/`sableclaw` 11), win sets `beatCommander` and fires
  branched credits (`endingWin` / `endingWinHeavenfall` per
  `choseHeavenfall`). Wired end-to-end on web and Dreamcast, and
  **playtested for real by the user on an actual Dreamcast emulator** —
  confirmed working. **This design is substantially reworked by Leg 2
  below** (auto-teleport → unlockable path, single boss → 5 tall-grass
  maps + a Heavenfall finale). Don't treat "closed" as "final" — read
  Leg 2.4 before touching the gauntlet again.

### Patterns worth knowing before starting Leg 2 or 3 (recurring gotchas)

- **The Dreamcast `wsoldier`/`pending` trainer-battle path is NOT
  generic.** Every new trainer needs, by hand, in `main.c`:
  `TRAINER_WSOLDIER_*` and `POST_WSOLDIER_*` `#define`s, an
  `NPC_PENDING_*` dispatch case, a battle-setup `case`, and the usual
  5 save-flag touch points (var decl, `ft[]` table, load, reset, store).
  The web side (`engine.ts`) *is* generic off `TRAINERS`/`worldJson`.
- `tools/bake_content.py` keeps **three separate hand-maintained lists**
  that must agree by name/number for any new trainer: `kit_keys`,
  `PENDING_IDS` (Python dict), and the hand-written
  `#define NPC_PENDING_*` lines. Forgetting one of the three either
  crashes bake or silently no-ops the battle dispatch.
- New map checklist (`check_sync --strict` enforces all of this):
  `content/maps.json` rows, `content/world.json` `mapIds`+`mapNames`,
  `content/save.json` `mapOrder` (byte-identical order to `mapIds`),
  `src/game/types.ts` `MapId` union, `src/game/data.ts` map export +
  `MAPS` entry. `MAP_*`'s Dreamcast define bakes for free (index-driven).
- `save.json`'s `flags` array is **append-only** — never reorder, it's
  byte-position indexed in the binary save. Currently at 50 flags
  (64-bit capacity). Leg 2's reputation stat will need a new numeric
  field, not a flag — check `save.json`'s `layout` byte map before
  picking where it goes.
- **Corrupted PNG signature to watch for:** valid PNG header + `IEND`
  trailer, but broken IDAT stream — PIL raises `OSError: broken data
  stream`, crashes `gen_sprites.py` for everyone until the bad file is
  removed. Happened twice already (`quartz-2.png`, `opal-2.png`), both
  from GitHub's file-API silently truncating large binary pushes.
  Verify any new art commit's PNGs actually open cleanly before relying
  on it.
- `dialogue.json`'s `endingWin` is a **hardcoded single key** in
  `bake_content.py` (`data["dialogue"]["endingWin"]`, not the generic
  talk table) — don't rename/delete it without updating the baker in
  the same commit, or bake crashes for everyone.
- Race-safe push protocol (used successfully every step so far):
  fetch → rebase onto `origin/main` → resolve any generated-file
  (`.inc`/`.cdi`/`.elf`) conflicts via `--ours`/`--theirs` + full
  rebake → rebuild → verify → fetch again right before pushing → push
  → verify the push landed by diffing against `origin/main` directly.

### Known pre-existing art debt (placeholder-covered, not blocking)

`check_sync --strict`'s one standing FAIL, **16 files** (regenerate via
`python3 ports/dreamcast/tools/gen_sprites.py`, see
`ports/dreamcast/ART_NEEDED.md` for exact specs):
- `npc/bogwalker-1..4.png` + `portraits/bogwalker.png`
- `npc/reedguard-1..4.png` + `portraits/reedguard.png`
- `npc/quartz-2.png` (frame 2 only, the corrupted-file casualty)
- `npc/fenn-1..4.png` + `portraits/fenn.png`

**Shipped (Grok A):** Mega / Ultimate / Perfect Capture Crystal item
icons (`public/sprites/items/{mega,ultimate,perfect}crystal.png`,
128x128 RGBA, same caged-stone silhouette as Common). Dropped
ART_NEEDED 28→25. Re-keyed with flood-from-edge + enclosed
magenta background holes (filigree/rings) + 2px inner-border
R→G clamp (no fringe-delete).
**Shipped (Grok A):** Driller quarry-trainer world frames
(`npc/driller-1..4.png`, 48x64 RGBA, yellow hard-hat miner with
pickaxe idle). Dropped ART_NEEDED 25→21. No Driller portrait in
the debt list.
**Shipped (Grok A):** Dray camp-merchant world frames + portrait
(`npc/dray-1..4.png` 48x64, `portraits/dray.png`). Rust
vest, backpack, lantern. Dropped ART_NEEDED 21→16.

---

## SEE_GIT_HISTORY_FOR_REMAINDER

(Full Leg 2/3 body restored in follow-up if truncated — critical CI section above is closed.)


---

## Leg 2.9 status (2026-09-20, Grok)

**Fully DONE and pushed** — post-battle mercy/threaten/execute for human
trainers (not Mason / Shinigami):

| Sub-step | Commit (approx) | Status |
|----------|-----------------|--------|
| 2.9.1 dismissal lines | prior | DONE |
| 2.9.2 UI (`mercy` mode, 4 options) | b9f3864 | DONE |
| 2.9.3 effects (rep / marks / items) | ae9e549 | DONE |
| 2.9.4 permanent execute-delete | eb004d2 | DONE |
| 2.9.5 red fade + scream SFX | ed75419 | DONE |
| 2.9.6 integration (soldiers → menu) | 522f039 | DONE |

**Still open (not 2.9):** 2.7 sub-steps 3+ (second party), 2.4 gauntlet,
2.8 (blocked on 2.4), Leg 3, art debt.

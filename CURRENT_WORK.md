# CURRENT_WORK.md

Live coordination doc for every agent working this repo (Claude, Grok,
ChatGPT, others). Read before starting anything; update before you stop.

**Standing house rules:**
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

---

## CI gap (still open): Pages doesn't auto-redeploy after a bot-only CDI rebuild

Found by Claude B: `build-dreamcast.yml`'s bot commit touches
`ports/dreamcast/crymon.cdi` (in `deploy-pages.yml`'s path filter), but
that push authenticates as the default `GITHUB_TOKEN`, and GitHub
Actions blocks `GITHUB_TOKEN`-authored pushes from triggering other
workflows (loop prevention). So `deploy-pages.yml` never fires off a
CDI-only rebuild — the live Pages site's downloadable CDI silently
stays one build behind until someone manually re-runs it
(Actions tab → Deploy CryMon Web to GitHub Pages → Run workflow).

**Fix options, still not done, whoever owns CI next:**
1. Give `build-dreamcast.yml`'s push step a PAT instead of the default
   token, so its push can trigger `deploy-pages.yml` normally.
2. Add a step at the end of `build-dreamcast.yml` that calls
   `deploy-pages.yml` via `workflow_dispatch` (needs `actions: write`).

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

### Known pre-existing art debt (placeholder-covered, not blocking, not this leg's fault)

`check_sync --strict`'s one standing FAIL, 15 files (regenerate via
`python3 ports/dreamcast/tools/gen_sprites.py`, see
`ports/dreamcast/ART_NEEDED.md` for exact specs):
- `npc/bogwalker-1..4.png` + `portraits/bogwalker.png`
- `npc/reedguard-1..4.png` + `portraits/reedguard.png`
- `npc/quartz-2.png` (frame 2 only, the corrupted-file casualty)
- `npc/driller-1..4.png`

---

## Leg 2 execution order (Claude A, 2026-09-20 overnight run)

User is offline for a while and asked me to work through Leg 2
autonomously: fastest/smallest items first, large items broken into
documented sub-steps, committing between every step so nothing's lost
if I run out of budget mid-task. This is that plan. **Check this
section's "Current position" line before claiming any item below** —
it's updated after every commit this run.

**Order (fastest/most-diagnosed first):**
1. **2.1 walk speed** — root cause already found (see 2.1 below),
   single-spot `main.c` fix, no cross-file plumbing. Fastest item.
2. **2.3 settings→start menu** — mechanical relocation, touches both
   engines' menu state machines but no new systems.
3. **2.5 capture-rate overhaul + crystal tiers** — **re-sized up after
   digging in**, see 2.5 below: it needs a shared binary-save-format
   byte-layout shift (both engines, real corruption risk if rushed)
   plus new item icon art, not just JSON. Still doing it next since
   it's the actual blocker for 2.6, but budget the same care as 2.7,
   not the "medium" pace this was filed at originally.
4. **2.6 more merchants** — depends on 2.5's items existing; same
   NPC/shop pattern used all session.
5. **2.9 mercy/threaten/execute menu** — new UI mode + dialogue pools +
   a permanent-NPC-deletion mechanic; broken into sub-steps below. Its
   dialogue-pool sub-step (2.9.1) has zero dependencies and could be
   picked up standalone by anyone if 2.5/2.6/2.7 are all mid-flight.
6. **2.7 reputation stat + father becomes a 2nd party member** — large
   systems feature (second controllable party, new persisted stat);
   broken into sub-steps below, same shape as quarry/endgame.
7. **2.10 reputation's economic effects** — small, but needs 2.7's
   `reputation` field to exist first.
8. **2.8 Heavenfall-revival reputation effect** — small, but needs
   2.4's redesigned gauntlet to exist first (it fires on gauntlet
   completion).
9. **2.4 gauntlet redesign** — largest and most ambiguous (open design
   question already flagged below it); broken into sub-steps below,
   saved for once the smaller wins are banked.
10. **2.2 Dreamcast audio** — investigation only, deliberately last.
    Raw AICA register-poke code (`chip.c`), no emulator in this sandbox
    to verify any fix actually produces sound, and the user's own note
    says it might be an emulator issue rather than a code bug. I will
    audit for obvious register/init bugs and document findings, but
    won't claim "fixed" without someone verifying on real hardware/a
    real emulator. See 2.2 below for what's already been checked.

(2.0 art debt isn't on this list — it's assigned to ChatGPT/Grok, not
a coding task for me.)

**Current position:** 2.1, 2.3, and 2.5 DONE and pushed, both engines,
verified by build/typecheck/check_sync only (**no Dreamcast emulator in
this sandbox for any of them** — see each section's own caveat before
assuming a "feels wrong" report means the fix itself is wrong rather
than unverified). Next: 2.6 (more merchants), per the execution order
above — it depends on 2.5's crystal items existing, which they now do.

---

## Leg 2 (open — from the user's "CryMon edits Leg 2" doc, 2026-09-20)

Playtesting the endgame build on a real Dreamcast emulator surfaced
bugs and a pile of new feature work. This is a big leg — claim
individual numbered items, don't try to do it all in one pass (same
lesson quarry and the endgame both taught: token exhaustion and
merge conflicts get worse the bigger a single commit gets).

### 2.0 — Art debt cleanup (assign to ChatGPT or Grok, not a coding task)

Have ChatGPT or Grok produce real art for the 15-file debt list above
and push it to `public/sprites/` at the exact paths `ART_NEEDED.md`
specifies (24x32 world-sprite frames, 312x176 portraits, transparent
background, matching the existing pixel-art style already in
`public/sprites/`). This supersedes the old "ChatGPT A: no PNG work"
rule for this task specifically. Once real files land, re-run
`gen_sprites.py` and confirm `check_sync --strict` drops this FAIL.

### 2.1 — Dreamcast walking speed bug — DONE (Claude A)

**Root cause found:** `engine.ts` moves the player at `84 px/sec`
(delta-time based, `src/game/engine.ts` ~line 1609: `const sp = 84;`).
`main.c`'s equivalent (~line 5602) is `int speed = 1; /* px/frame;
~60px/sec at 60fps... */` — an **integer** pixels-per-frame step, fixed
at 60fps via `wait_vblank()`. `int speed = 1` can only ever be an exact
integer number of pixels per frame, so it's hard-locked to exactly
60px/sec — **29% slower than web's 84px/sec**, and there's no way to
hit 84 exactly with a plain integer step at 60fps (84/60 = 1.4 px/frame).

**Fix:** replace the flat `int speed = 1` with a fixed-point
sub-pixel accumulator so the *average* speed matches 84px/sec despite
only ever moving whole pixels in a frame. Pattern: keep a persistent
`int speed_frac` (accumulates `84 * 256 / 60` ≈ 358 per frame, i.e.
almost 1.4<<8), move by `speed_frac >> 8` pixels, then
`speed_frac &= 255` to keep the remainder for next frame. This is the
standard fixed-point way to get a non-integer average speed from
integer per-frame steps — same idea as a Bresenham accumulator.
Apply it identically to both the dx and dy branches (currently
`nx = px + dx*speed`/`ny = py + dy*speed`).

**Caveat:** I can't run a Dreamcast emulator in this sandbox, so this
is verified by re-deriving the math and by the build compiling clean,
not by watching the character actually move at the right speed on
screen. If it still feels off after this, check whether
`wait_vblank()` is actually pacing at a true 60Hz (PAL Dreamcasts run
at 50Hz and would need the constant `60` above adjusted to whatever
the real vblank rate is) before assuming the accumulator math is wrong.

### 2.2 — Dreamcast has no audio (web does) — investigation notes, not fixed

Deliberately scheduled last (see execution order above): `chip.c` is a
**raw AICA register-poke implementation** (writes directly to
`0xa0700000`+ channel registers over the G2 bus, no KOS/libronin sound
API), which is inherently easy to get subtly wrong in ways that only
show up as silence, and I have **no Dreamcast emulator in this sandbox**
to verify any fix actually produces sound. Confirmed already (per the
user): `chip.c` is genuinely in the build (`OBJS`, explicit Makefile
rule, compiles clean every time this session).

**What to check, if you pick this up with a way to actually test it:**
- `aica_ch_setup()`/`aica_ch_wave()`/`aica_ch_vol_pitch()`/`aica_keyex()`
  in `chip.c` — verify the key-on/key-off bit and register offsets
  against AICA docs; a single wrong bit here silently produces no
  sound with no error.
- `G2_FIFO` busy-wait (`g2_w32`, ~line 28) — if G2 bus writes are
  issued before the FIFO is actually ready, they can silently drop.
- Whether `chip_init()` is actually called before the first
  `chip_set_song`/`chip_sfx_*` call in `main()`'s startup sequence.
- Compare against `src/game/audio.ts` (the reference this mirrors) for
  anything AICA-equivalent that's missing entirely, not just wrong.
- Rule out the emulator first if possible: does the *exact same* CDI
  play audio in a different Dreamcast emulator, or on real hardware?
  If not even the emulator's own BIOS/menu sounds play, it's likely an
  emulator config issue, not this codebase.

**Do not mark this "fixed" from a code read alone** — the failure mode
here is exactly "compiles fine, silently produces no sound," which
looks identical whether the bug is in `chip.c` or in the emulator.

### 2.3 — Move settings into the start/title menu — DONE (Claude A)

Settings used to be a tab inside the Bag menu (Select button, both
engines). Moved to the party/CryMon menu instead (opened via Start on
web, via the pause menu's CryMon entry on Dreamcast) since that's the
"start menu" in this game's control scheme:

- **Web (`engine.ts`):** retired `bagTab`/`BagTab` entirely (Bag is
  items-only now, no tab UI). Added `"settings"` to the `PartyView`
  union (`types.ts`). From the party list (`partyView === "list"`),
  Left/Right now enters `partyView = "settings"` (was unused there
  before); Up/Down nudges volume same as the old Bag tab did; Cancel/
  Start returns to the list. `drawParty()` renders the volume bar in
  the party window instead of `drawBag()`.
- **Dreamcast (`main.c`):** same relocation. Renamed `bag_tab` →
  `party_settings`, moved its toggle out of `menu_mode == 1` (bag) into
  `menu_mode == 2` (party) via Left/Right; `draw_bag_menu()` lost its
  `tab` parameter (items-only now); `draw_party_menu()` gained a
  `party_settings` parameter and a settings-screen render branch.
  Entering settings works even with an empty party (checked — the old
  bag-tab toggle didn't have this restriction either, so kept parity).

Verified: `check_sync --strict` clean but for the pre-existing art
debt, `npm run typecheck` clean, `main.c` compiles with no new
warnings, `make cdi` succeeds, dev server boots clean with no console
errors. **Not played through on real hardware/an emulator** (same
caveat as 2.1) — this is build/typecheck-verified navigation logic,
not a confirmed working menu on screen. If the settings screen doesn't
actually appear/respond right, re-check the Left/Right entry point in
`updateParty()`'s base "list" case (web) or the `menu_mode==2` input
block (Dreamcast) before assuming the whole approach is wrong.

### 2.4 — Redesign the gauntlet (replaces Leg-1's single-map/single-boss version)

Current behavior (from the endgame leg just closed): the gauntlet map
is empty and the player is unconditionally teleported there right
after the father/Heavenfall choice. **New spec:**

- The gauntlet becomes an **unlockable location reached via a path
  behind Shinigami** (in the Grove) — not an automatic teleport after
  the choice. (Open question for whoever implements this: does the
  father/Heavenfall choice still happen at the same point in the story,
  or does it move to gate/follow the gauntlet instead? The doc doesn't
  say explicitly — check with the user before assuming either way.)
- It's **5 maps of tall grass**, back to back, each with
  increasingly higher-level wild CryMon than the last.
- The **5th map's encounter pool includes every CryMon species in the
  game** that isn't a one-off named character (Cathleen and Heavenfall
  excluded), all catchable there.
- After clearing all 5, the player reaches a **6th map with no tall
  grass**, containing a gravestone.
- **Interacting with the gravestone while holding the scroll
  (`hasScroll`) resurrects Heavenfall.** The player then battles it.
  - Dropping Heavenfall to 0 HP (defeating, not catching) renames the
    player to **"Heaven Slayer"** in every iteration/interaction.
  - Capturing Heavenfall in a Capture Crystal renames the player to
    **"Heaven Tamer"** in every iteration/interaction.
- This is where Leg 2's design and the old story lock intersect: the
  old lock said Heavenfall stays narrative-only, no capture, until the
  user asked for that explicitly — **this doc is that explicit ask.**
  `docs/CRYMON.md`'s story-lock section should get a one-line update
  reflecting that, in whichever commit actually implements this.
- `commanderFinal` (the old single gauntlet boss) isn't mentioned in
  this redesign at all — decide with the user whether it's kept as an
  earlier beat, folded into one of the 5 grass maps, or removed;
  don't unilaterally delete a working boss fight without asking.

**Largest item in Leg 2, most open design questions. Do not start
implementing until the two open questions above (choice-screen timing,
`commanderFinal`'s fate) are answered by the user** — this is the one
place in Leg 2 where guessing wrong means throwing away real work,
unlike the smaller items. Proposed sub-steps once answered, mirroring
the quarry/endgame breakdown shape that worked well all session:
1. Design pass: exact tile layouts for the 5 grass maps + the 6th
   gravestone map, the level curve across the 5 (what "increasingly
   higher level" means numerically), and the full encounter-pool list
   for map 5 (every non-one-off species — enumerate it explicitly from
   `species.json` so nothing's missed or wrongly included).
2. Add the 6 maps + encounter tables in JSON (mirrors quarry/gauntlet-v1
   map-adding checklist in "Patterns worth knowing" above).
3. The path-behind-Shinigami unlock mechanic (new warp/gate, replacing
   the old auto-teleport in `POST_ENDING_FINAL`/`next === "ending"`).
4. Heavenfall boss definition (JSON) + the gravestone interaction +
   scroll-gate check.
5. The Slayer/Tamer rename mechanic — same "how deep does the rename
   go" question as Max The Kind in 2.7, decide the approach once there
   rather than solving it twice differently.
6. `docs/CRYMON.md` story-lock update (one line, reflecting this is
   the user's explicit ask to lift the Heavenfall-narrative-only lock).
7. Wire into `engine.ts`, then `main.c` (same non-generic Dreamcast
   wiring every boss/map addition has needed all session).
8. Integration pass + playtest.

### 2.5 — Replace the capture-rate mechanic + add crystal tiers

**DONE (Claude A), pushed.** Implemented on both engines:
`captureChance()`/`capture_chance()` rewritten to
`base - level - str - hp` (+50 if debuffed/status-afflicted), clamped
0-100. Added Mega (100 marks/base 160) and Ultimate (250/190) Capture
Crystals; renamed `gem`→"Common Capture Crystal" (base 100) and
`greatcrystal`→"Greater Capture Crystal" (base 130); added a
non-purchasable Perfect Capture Crystal (base 1000 — guarantees
capture without a special-case branch). Shared binary save format
bumped to version 3 (bag grows 10→13 bytes, shifting every field after
it — hand-updated in both `save.ts` and `save.c`; `check_sync.py`'s own
independently-hardcoded golden layout was also fixed to derive offsets
from `itemOrder` length instead of hardcoding them a third time, which
would have gone stale). New items use synthesized placeholder icons
(registered in `sprites.json`, now 18 files in `ART_NEEDED.md`, assigned
to 2.0). Also fixed two Dreamcast UI overflow bugs found by inspection:
`draw_bag_menu()` and `draw_shop()` both drew a fixed number of
unconditional rows and would have drawn off the bottom of the menu box
now that bag (13) and shop (11 buyable) item counts exceed what fits
unscrolled — both now use the cursor-following scroll window already
used by the attack-move menu.

**Interpretation decision made (flag for correction if wrong):** the
doc's formula is implemented literally in raw stat units, not
normalized — a high-level/high-stat CryMon can go pre-clamp negative
(clamped to 0%) unless nearly dead. This matches the simplest reading
that doesn't invent normalization the doc never mentions.

**Deferred (not part of this pass):** sub-step 8, wiring the Perfect
Capture Crystal as an actual reward for defeating/capturing Heavenfall
— depends on 2.4 (gauntlet redesign) landing first, don't force it in
early.

**Not hardware-verified** — no Dreamcast emulator in this sandbox;
verified via `make`/`make cdi`/`check_sync --strict`/`npm run
typecheck` only.

- **Common Capture Crystal** (rename of today's base Capture Crystal):
  25 marks. Capture rate formula: `100% - CryMon's level - CryMon's
  strength stat - CryMon's current HP` (as percentages/points — the
  doc doesn't spell out units beyond this, clarify with the user before
  implementing if the current capture-rate formula in `logic.json`/
  `data.ts`'s `captureChance()` doesn't already use comparable units).
  A status condition (poison, etc.) affecting the target CryMon
  increases the capture rate by +50%.
- **Greater Capture Crystal:** 50 marks, base capture rate 130%.
- **Mega Capture Crystal** (new item): 100 marks, base capture rate 160%.
- **Ultimate Capture Crystal** (new item): 250 marks, base capture rate 190%.
- **Perfect Capture Crystal** (new item): always captures. **Not
  purchasable** — awarded only after defeating or capturing Heavenfall.

**Re-sized after digging in (Claude A): this is bigger than "medium."**
Found two real dependencies my original estimate missed, both now
confirmed by reading the actual code rather than guessing:

- **The save format needs a byte-layout shift, not just an append.**
  `content/save.json`'s `layout.bag` is `[18, 10]` — 10 fixed byte
  offsets, one per `itemOrder` entry, no padding after it (`flags`
  starts immediately at byte 28). Adding 3 new items means `bag` grows
  to 13 bytes, which pushes `flags`/`party`/`checksum`/`dexSeen`/
  `dexCaught` all +3 bytes each. This is a real binary-format change
  on **both** engines' save pack/unpack code (`src/game/save.ts` and
  `ports/dreamcast/src/save.c`), not a JSON-only edit — get this wrong
  and old saves (or saves written by one engine, read by the other
  mid-transition) silently corrupt. Don't rush it.
- **New items need new icons** (`icon_megacrystal` etc. on the
  Dreamcast side, `item-<id>` sprites on web) — same category of
  problem as the NPC art debt, just for items instead of NPCs. Either
  get real art the same way as 2.0 (ChatGPT/Grok), or use a plain
  placeholder icon deliberately and say so, but don't skip silently.

**Sub-steps (do in order, commit after each — this now genuinely
belongs closer to 2.7/2.9 in size, moved down the execution order
accordingly, see the top of this section):**
1. Pick the 3 new items' final byte offsets and write out the full
   shifted `layout` table by hand before touching any code — get the
   arithmetic right on paper first (bag 18→13 bytes ends at 31; flags
   31,8; party 39,96; checksum 135,2; dexSeen 137,4; dexCaught 141,4;
   double-check `size` still covers it, currently 256, plenty of room).
2. Update `save.ts` (web) and `save.c` (Dreamcast)'s pack/unpack to the
   new offsets, **together in the same commit** — one engine ahead of
   the other here is exactly the corruption risk above.
3. Rename `gem` → "Common Capture Crystal" in `items.json` (25 marks),
   add Mega/Ultimate/Perfect to `items.json` + `save.json`'s
   `itemOrder` (matching the new layout from step 1). Perfect: no `buy`
   price / excluded from shop buy lists (check how any existing
   non-purchasable item — if one exists — signals that; otherwise this
   needs a new convention, don't invent one silently).
4. Icons for the 3 new items (see the art note above — flag it, get
   real art or an explicit placeholder, don't skip).
5. New capture-chance formula: `captureChance()` in `src/game/data.ts`
   (currently `agl`/`missing-hp%`/`bonus`/`vulnerable` based) needs to
   become `level`/`str`/`hp`/tier-base based, per the doc's literal
   formula. **Interpretation decision needed if not already obvious
   from the doc when you reread it:** is `100% - level - str - HP` in
   raw stat units (a level-20 STR-20 HP-80 CryMon then has a *negative*
   pre-clamp rate, i.e. you must nearly kill it first) or some
   normalized version? I'd implement it literally (raw units, clamp
   0-100, tier's "base capture rate" replaces the leading 100) unless
   you have reason to think otherwise — that's the simplest reading
   that doesn't require inventing new normalization the doc doesn't
   mention. Status affliction: +50 percentage points, additive (same
   style as the existing `+25` bonus on Greater Crystal today).
6. Mirror the same formula in `main.c`'s capture roll.
7. Retire or repurpose the old formula's `FORMULAS.captureAgl` etc. in
   `logic.json` — don't leave dead config nobody reads.
8. Wire "Perfect Capture Crystal" as a reward on defeating/capturing
   Heavenfall (depends on 2.4 existing — this step likely lands after
   2.4, not before; don't force an ordering that doesn't fit).
9. Integration pass (rebake, check_sync, typecheck, build, cdi).

### 2.6 — Populate the world with more merchants

**Sub-steps:** (1) design how many/where — pick map spots not already
used; (2) add merchant NPC rows in `world.json` (role/dialogue/shop
inventory, same pattern as Bram/Oren) restricted to Greater/Mega/
Ultimate stock; (3) dialogue entries; (4) integration pass. Small
relative to the others — mostly repeating an established pattern.

Add additional merchant NPCs across the maps. The first/existing
merchant sells **Common Capture Crystals only**. Every other merchant
sells **Greater, Mega, and Ultimate** Capture Crystals (not Common,
not Perfect — that one's never sold).

### 2.7 — New `reputation` stat + father-revival branch

- New persisted numeric stat, `reputation`, starts at 0. Range **-100
  to +100** (see 2.10 for the price-scaling effects at each end).
- Choosing to revive the father (the existing choice-screen option):
  - `+25` reputation immediately.
  - Teleports the player back to the father's side for a short
    dialogue where he thanks the player for saving his life.
  - **He joins the party as a second player-controlled character** the
    player can swap to, who can carry an additional 6 CryMon (i.e., a
    second 6-slot party the player switches between).
  - Permanently renames the player **"Max The Kind"** in every
    iteration/interaction.

**This is the biggest single item in Leg 2 — a second controllable
party is a real systems feature, not a flag.** Sub-steps:
1. `reputation` field: needs a numeric byte in the save layout (not a
   bit flag — check `save.json`'s `layout` map for free space, it's a
   fixed byte-offset binary format shared by web+Dreamcast, adding a
   field means extending `layout`/`size` deliberately, not just
   appending to `flags[]` like every other addition this session).
   Land this alone first, both engines reading/writing it as 0, before
   touching anything else here.
2. The father-revival dialogue + teleport-back + reputation +25, using
   the existing `choiceFather` hook as the trigger point. No second
   party yet in this step — just the narrative/flag piece.
3. Design the second-party data model: is it a fully independent
   6-slot party array (`party2`?) with its own save layout, or some
   other shape? This needs a decision before writing code — the
   existing `party` array/UI (`PARTY_MAX`, `partyView`, etc.) is
   pervasive through `engine.ts`, and a second one either duplicates
   that surface or generalizes it. Don't start coding this step until
   that shape is picked (ask the user if unclear).
4. The swap-between-parties UI/input (web), then its Dreamcast mirror.
5. The "Max The Kind" rename — figure out how deep "every
   iteration/interaction" needs to go (dialogue speaker name display?
   just the HUD? every `"max"` speaker line's displayed name?) before
   implementing; this likely means a display-name override on the
   `max`/player speaker rather than literally rewriting dialogue text.
6. Integration pass.

### 2.8 — Heavenfall-revival reputation effect

Choosing to revive Heavenfall (at the original choice screen) has **no
immediate reputation effect**. Only after going through the (redesigned)
gauntlet and successfully reviving Heavenfall there does reputation
drop by `-25`, and **every merchant's first interaction with the player
after that point** says "You revived Heavenfall, who knows what other
horrors you are capable of."

### 2.9 — Post-battle mercy/threaten/execute menu (human opponents)

After defeating any human trainer **other than Mason or Shinigami**,
prompt the player with 4 options:
- **"Let Them Go"** — triggers a random dismissal line from the NPC
  ("I can't believe I was beaten by a kid", "Impossible! I've never
  lost a battle!", or similar — need a small pool of these). `+1`
  reputation.
- **"Threaten Them For Money"** — NPC says "Don't hurt me, just take
  it!", `-1` reputation, player receives marks equal to the **combined
  level of all their CryMon**.
- **"Threaten Them For An Item"** — same dialogue line, `-2`
  reputation, player receives **one fully random item**.
- **"Execute"** — Max says "No survivors, no witnesses.", screen fades
  to red with a scream sound effect, `-10` reputation, player receives
  marks equal to **combined CryMon level × 10** plus **2 random items**,
  the NPC is **permanently deleted from the world as an entity**, then
  the screen fades back in from red to normal.

**Dependency note:** this needs the bare `reputation` numeric field to
exist (2.7 sub-step 1 only — not the second-party system, that part of
2.7 is unrelated to this). Land 2.7 step 1 first if this gets picked up
before the rest of 2.7.

**Sub-steps:**
1. A small pool of "let them go" dismissal lines in `dialogue.json`
   (needs at least 3-4 for variety, doc gives 2 examples).
2. The post-battle prompt UI itself — likely a new `mode`/menu state
   the same way the father/Heavenfall `choice` screen works
   (`updateChoice`/`draw_choice` pattern), but 4 options instead of 2,
   and only reachable from a trainer-win instead of the one scripted
   spot. Scope check: "any human trainer other than Mason or
   Shinigami" is a lot of existing trainers (Cross, Conscript,
   Enforcer, Sentry, Ranger/Scout/Keeper/Warden, Bog/Reed, Quartz/Opal,
   Driller, commanderFinal...) — confirm whether ALL of them get this
   prompt or just future ones, since retrofitting every existing
   win-handler is a bigger diff than adding it to new content only.
3. The 4 branches' effects (marks math, item RNG, reputation deltas).
4. "Permanently deleted from the world" for Execute — needs a new
   per-NPC persisted flag (`beat<Name>` flags already exist for "don't
   refight," but "deleted as an entity" implies also hidden from any
   future non-combat interaction/dialogue too — check whether the
   existing win-flag already achieves that or a new flag is needed).
5. Screen fade-to-red + scream SFX on both engines.
6. Integration pass.

### 2.10 — Reputation's economic effects

- Range: **-100 to +100** (hard clamp).
- Each **positive** reputation point reduces shop item prices by 1%
  (floor of 1 mark per item — never free from this alone).
- Each **negative** reputation point increases shop item prices by 5%.
- At **exactly +100** reputation: interacting with a merchant gives a
  free item — **once per merchant, for the whole playthrough** (track
  per-merchant, not just a global once-ever flag).
- At **-100** reputation: merchants refuse to do business with the
  player at all.

---

## Leg 3 (open — also from the same doc)

**Do not start before Leg 2's gauntlet/reputation work lands** — Leg 3
depends on `reputation` existing and behaving per Leg 2.7-2.10.

New content: liberating cities from occupying Weeping Army soldiers,
building to a final confrontation with their king.

### 3.1 — Shackles item + Weeping Generals

- New item, **Shackles**, sold at every merchant **except the first
  one**. Required to challenge Weeping Generals (see below).
- Populate the newly-added liberation cities (new maps/NPCs — not yet
  designed, needs its own design pass same as the gauntlet did) with
  one **Weeping General** each, individually named (e.g. "Weeping
  General Gideon", "Weeping General Arthur" — the doc gives these as
  examples, not a fixed roster; needs an actual name list sized to
  however many cities get added).

### 3.2 — Arrest or execute each Weeping General

After defeating a Weeping General, the player chooses:
- **Arrest** (requires Shackles): `+10` reputation.
- **Execute:** `-25` reputation.

### 3.3 — Golden Shackles + Weeping King Nero

Defeating **all** Weeping Generals unlocks the **Golden Shackles**,
which lets the player confront **Weeping King Nero**.

### 3.4 — King Nero's fate branches the ending

- **"Bring Him To Trial"** (arrest via Golden Shackles): `+50`
  reputation, plays a cutscene of his war-crimes trial and life
  sentence.
- **Execute:** `-50` reputation, fade to red, a new scream audio plays
  **3 times in a row**, then a **red tint stays on screen for the rest
  of the playthrough** (persistent visual state, not a temporary fade).
  Player is renamed **"Kingslayer"** in every iteration/interaction. A
  cutscene plays where the player is crowned the new Queen.

### 3.5 — Father's reaction (only if the father is alive, i.e. was revived per 2.7)

Regardless of the trial/execute choice above, if the father is alive:
- **Positive reputation + arrested the king:** cutscene, father
  congratulates the player for being merciful.
- **Negative reputation + brought the king to trial anyway:** cutscene,
  father talks about "necessary sacrifice."
- **Executed the king:** father calls the player a monster and
  abandons them.

### 3.6 — Heavenfall's final resolution ends the game

- If the player **does not** have Heavenfall in their party at this
  point: the game ends here, full stop.
- If the player **has Heavenfall** and **positive reputation**:
  cutscene where Heavenfall is "tamed by the player's good nature,"
  plus an epilogue about Heavenfall staying by their side.
- If the player **has Heavenfall** and **negative reputation**:
  Heavenfall is "poisoned by the player's evil," turns hostile, and
  **attacks immediately** with no rest opportunity after the previous
  battle.
  - If the player **defeats** hostile Heavenfall: epilogue, player
    renamed **"Godslayer"**, feared as a merciless murderer for the
    rest of history.
  - If hostile Heavenfall **wipes the player's whole party**: epilogue,
    the player **dies**, renamed **"Max The Bloody"** posthumously,
    remembered as the one who let Heavenfall loose to rampage across
    the world.
- Whichever branch fires, **the game ends once it resolves.**

# CURRENT_WORK.md

Live coordination. This writer is **Grok C**.

Do not hand-replace `world.json`. Do not empty `npcs`. Heavenfall is wild/boss
only. **Cathleen is the only CryMon who speaks.** ChatGPT A: **no PNG work.**
Claude B: encode, no drawing.

Quarry is **parked**. Do not pick it up this list.

---

## Status

- Forest/ruins extra trainers live on web. Encode of their art + fights
  landed (task 5). New species battle sprites indexed through Kilnback.
- Marsh + quarry maps exist. Marsh trainers (Bogwalker, Reedguard) live. Quarry parked.
- +6 species lines done (28 total). Soldier right-walk mirrored.
- Quartz + Opal + marsh trainers live on web and Dreamcast PENDING. Quarry Driller by Claude A.

---

## Open tasks

### 1. Marsh trainers (2) — DONE (Grok C)
JSON kits + NPC rows + talk on `marsh`. Unique sprites (do not reuse soldier).
Bogwalker + Reedguard live on marks 1/2. Placeholder frames (birch/sable copies);
Grok A may replace with proper marsh art. Flags beatMarshBog / beatMarshReed appended.

### 2. Crystal warden Quartz — DONE (Grok C art)
JSON trainer + persist flag `badgeQuartz` **appended** to `save.json` flags.
Optional side content, not a story fork. Not named "gym".
Quartz NPC art (quartz-1..4.png) + sprites.json entry by Grok C (took Grok A art slot).

### 3. Crystal warden Opal — DONE (Grok C)
JSON + badgeOpal + Reach mark O + dialogue + engine flags + opal-1..4 art.
Dreamcast PENDING dispatch for marshBog/marshReed/opal wired (Grok C).

### 4. Draw NPCs from JSON — DONE (Grok C)
`engine.ts` overworld blit iterates `NPCS` / `npc.sprite`. Props, Mason/Anne,
forest soldiers, and Cathleen-ow stay special-cased. Marsh/Quartz now draw from JSON.

### 5. Encode new art — DONE
Ranger/Scout/Keeper/Warden draw + fights. Veilcap/Kilnback (+ peatling line)
in the battle sprite table.

---

## Parked (do not take)

~~Quarry trainer, quarry warp `need: beatSentry`, quarry encode. Let that lie.~~
**Unparked by the user.** Broken into 5 small steps to avoid the one-pass
token exhaustion that hit it before:

1. Gate the warp (`need: beatSentry`) — DONE, live on `main`.
2. Define `quarryDriller` trainer in JSON — DONE.
3. Wire into `engine.ts` (web) — **DONE, this commit** (Claude A). Five
   touch points, matching the `badgeOpal` template exactly: property
   decl, reset-state, both save-serialize spots, win-handler `else if`,
   `wsName` display-name entry. `npm run typecheck` clean.
4. Wire into `main.c` (Dreamcast) — **DONE, this commit** (Claude A).
   Confirmed the `wsoldier`/`pending` win path is **not** fully generic
   on Dreamcast — it needs explicit per-trainer C: `TRAINER_WSOLDIER_*`
   / `POST_WSOLDIER_*` defines, an `NPC_PENDING_QUARRY_DRILLER` id, a
   dispatch `else if` in the `NPC_AFTER_WSOLDIER` chain, a battle-setup
   `case` (mirrors `POST_WSOLDIER_QUARTZ`), and the usual 5 save-flag
   touch points (`beat_quarry_driller` var, `ft[]` table, load, reset,
   store). Also added `quarryDriller` to `bake_content.py`'s `kit_keys`
   (was hardcoded, quarry wasn't in it) so `TRAINER_KITS`/`KIT_QUARRY_DRILLER`
   bake at all.
5. Integration pass — **DONE, this commit** (Claude A). Rebake,
   `gen_sprites.py`, `check_sync.py --strict`, `npm run typecheck`, full
   `make -C ports/dreamcast` + `make -C ports/dreamcast cdi` all pass.

**Fixed the pre-existing `SPEAKER`/`PENDING_IDS`/`SpeakerId` gap flagged
above, for real this time:** added `opal`/`driller` to `bake_content.py`'s
`SPEAKER` dict, added `marshBog`/`marshReed`/`opal`/`quarryDriller` to
`PENDING_IDS` (only `quarryDriller` got a matching Dreamcast dispatch —
see below), and added `opal`/`driller` to `types.ts`'s `SpeakerId` union.
Bake no longer throws `KeyError: 'opal'`.

**Found and quarantined a second corrupted PNG:** `public/sprites/npc/opal-2.png`
(from commit `ca4b53e`) had the same failure signature as the
`quartz-2.png` corruption earlier this session — valid PNG header/IEND,
broken IDAT stream, crashes `gen_sprites.py` with `OSError: broken data
stream`. Deleted it (git-tracked, fully recoverable from history) rather
than fabricate replacement art; the placeholder-synthesis pipeline covers
it now. Added `"driller"` to `content/sprites.json`'s `npcs` list too —
it wasn't registered there at all, so `gen_sprites.py` didn't even know
to placeholder it.

~~Still open... marshBog/marshReed/opal Dreamcast wiring~~ **DONE (Grok C)**,
commit `2209c25`: `NPC_PENDING_*` defines, dispatch, `kit_keys` entries,
win-handler branches all landed for all three. Verified (Claude A):
rebake/`gen_sprites`/`check_sync --strict`/typecheck/`make`+`make cdi`
all pass. Quarry is fully closed out — all 5 steps done, Opal (BUG-004)
done end to end on both web and Dreamcast.

---

## Endgame: Heavenfall + gauntlet map (was #18, unparked by the user)

**Unparked.** Same reason as quarry: too big for one pass, broken into
6 small independently-verifiable steps. **Story-lock boundary that does
NOT move with this unparking** (per `docs/CRYMON.md`): Heavenfall and
father resurrection stay **narrative-only** — no party member, no
capture, no battle-usable Heavenfall — until the user explicitly asks
for that separately. This breakdown only extends what happens *after*
the existing father/Heavenfall choice dialogue, before the credits.

Today: `POST_ENDING_FINAL` (main.c) fires `ending_mode=1` immediately
after `TALK_CHOICE_FATHER`/`TALK_CHOICE_HEAVENFALL` closes, straight to
the `endingWin` credits text. The "gauntlet map" is a new final-stretch
map inserted in that gap, capped by a boss fight (likely the existing
`commander` NPC on the camp map — dialogue-only today, no trainer kit
yet) before the (rewritten) credits roll.

1. Design the outline (JSON-first, no code) — open, task #28. Branching
   climax dialogue (flavor only, not mechanics, by which choice was
   made), pick/define the boss, sketch the gauntlet map layout.
2. Add the `gauntlet` map + warp gating in JSON — open, task #29,
   blocked on #28. Mirrors quarry Task 1's warp-gate precedent.
3. Define the boss trainer + branching win dialogue in JSON — open,
   task #30, blocked on #29. Append-only save flag, PLACEHOLDER_ART if
   no boss art exists. Mirrors quarry Task 2.
4. Wire into `engine.ts` (web) — open, task #31, blocked on #30.
   Mirrors quarry Task 3's 5-touch-point template; relocates the ending
   trigger to fire after the boss falls.
5. Wire into `main.c` (Dreamcast) — open, task #32, blocked on #31.
   Expect the same non-generic `TRAINER_*`/`POST_*`/dispatch/kit_keys
   wiring quarry Task 4 needed, since the `wsoldier`/`pending` win path
   isn't generic there.
6. Integration pass — open, task #33, blocked on #32. Rebake,
   `gen_sprites`, `check_sync --strict`, typecheck, `make` + `make cdi`,
   playtest both branches if feasible.

Claiming any of these: check task #28-33's status/owner in the task
tool first (or this file, whichever's freshest) before starting, so we
don't duplicate quarry's early friction.

### Step 1 outline — DONE (Claude A), design only, nothing applied yet

No `content/*.json` edits in this step. Plan for whoever picks up #29:

**Boss: the returning `commander`.** He's dialogue-only today (camp
map, mark `I`, `role: "talk"`) and already met Max once mid-game — she
brushed him off ("I'm already going there"). Reusing him as the final
boss gives a payoff without inventing a new named character or new
mid-game continuity. Give him a second NPC row (new id, e.g.
`commanderFinal`) on the new `gauntlet` map rather than upgrading the
camp one, so the camp scene stays exactly as it is.

**Persisted choice flag (new, append to `save.json`):**
`choseHeavenfall` (bool, default false = father branch). Nothing
persists this today — `choice_cur` in `main.c` is transient, picks
which of `TALK_CHOICE_FATHER`/`TALK_CHOICE_HEAVENFALL` plays, then both
paths converge straight into `POST_ENDING_FINAL`. Step 2/3 needs to set
this flag when the choice is made and read it back after the gauntlet
boss falls, to pick the ending variant.

**Map sketch — `gauntlet`:** short, linear, ~14x8, not an exploration
hub. A last corridor back through the Weeping Army's ground: fenced-in
push (reuse `%`/`H` solids for the corridor walls), one or two tall-grass
tiles near the entrance for a last optional wild encounter, opens onto
a small clearing at the far end where `commanderFinal` blocks the exit.
Single warp in, no warp out — beating the boss is what ends the run.

**Where the warp fires:** today `POST_OPEN_CHOICE` -> choice screen ->
`POST_ENDING_FINAL` fires the credits immediately once the chosen
`TALK_CHOICE_*` dialogue closes. Step 2 should redirect that same spot
to warp onto `gauntlet`'s entrance tile instead (setting `choseHeavenfall`
first); `POST_ENDING_FINAL` moves to fire only after `commanderFinal`'s
win-handler, same as every other `wsoldier`-style boss.

**Boss trainer proposal (finalize in Step 3):** lead `duskhorn` lvl 12,
bench `[["boulderam", 11], ["sableclaw", 11]]` (2-bench, matching
Shinigami's the only other 2-bench kit — this should read as the
hardest fight in the demo). `marks: 25` (current max is Quartz's 16).
Flag `beatGauntlet`. Sprite `npc/commander` already exists (reuse, not
a new PLACEHOLDER_ART unless art wants a distinct "final" look).

**Branching dialogue (flavor only, mechanics identical either way):**
- `commanderFinalSpotFather` / `commanderFinalSpotHeavenfall` — two
  short spot-talk variants referencing which choice was made.
- One shared `commanderFinalWin` (no need to branch the win line itself).
- Two ending variants replacing the single `endingWin`: `endingWinFather`
  / `endingWinHeavenfall`, same length/tone as today's, gated on
  `choseHeavenfall` for which one main.c's ending screen shows.
  Draft text for both is in this session's task #28 notes if whoever
  picks up #30 wants a starting point rather than writing from scratch.

### Step 2 — DONE (Claude A). Map + map-id plumbing landed; no literal
"warp" entry, and here's why.

**Correction to Step 1's framing:** there's no tile-walked warp to gate.
Checked `main.c` -- the choice sequence isn't a warp at all. Defeating
Shinigami fires `POST_OPEN_CHOICE` directly (a scripted state change,
same spot Anne's father-death reveal already fired from), the choice
screen closes into `POST_ENDING_FINAL`, which today jumps straight to
`ending_mode=1` in place, no map change involved. So "gate the warp"
doesn't apply here; entry onto `gauntlet` will be a scripted teleport
(`POST_ENDING_FINAL` repointed to spawn the player on `gauntlet`'s mark
`2` instead of firing the ending immediately) -- that's Step 4/5's job,
not something expressible in `world.json`'s `warps[]` array.

**What actually landed, JSON + the mechanical cross-file plumbing
`check_sync --strict` requires for any new map (same category of edit
as adding a species or a talk key -- not engine logic):**
- `content/maps.json`: `gauntlet` map, 16x8, walls all around, spawn
  mark `2` near the entrance, boss mark `1` at the far end. No tall
  grass -- an encounter pool for a wild-tile is Step 3's call, not
  this step's, so left it out to keep this step's JSON self-consistent
  on its own without touching encounters.json.
- `content/world.json`: `gauntlet` added to `mapIds` (end of list) and
  `mapNames` ("THE GAUNTLET").
- `content/save.json`: `gauntlet` appended to `mapOrder`, same position,
  keeping it byte-identical to `mapIds` per `check_sync`'s rule.
- `src/game/types.ts`: `gauntlet` added to the `MapId` union.
- `src/game/data.ts`: `GAUNTLET` export + `MAPS.gauntlet` entry,
  mechanical (`normalize(raw.gauntlet)`), same pattern as every other
  map -- no rendering/gameplay logic touched.

No `choseHeavenfall` flag, no boss trainer, no dialogue in this step --
that's Step 3 (#30). `MAP_GAUNTLET`'s Dreamcast define bakes for free
(index-driven off `mapIds`, not a hardcoded list like `kit_keys` was).

Verified: rebake, `check_sync --strict` (clean but for the pre-existing
15-file art-placeholder debt), `npm run typecheck`, `make -C ports/dreamcast`,
`make -C ports/dreamcast cdi` all pass.

### Step 3 — DONE (Claude A). Boss trainer + branching dialogue, JSON only.

Landed with two deltas from Step 1's proposal, both to keep every step
independently green (this session's hard-earned rule -- never leave a
`KeyError`/bake crash for the next step to discover):

- **Boss stat swap:** lead is `boulderam` lvl 12 (not `duskhorn`) --
  reads better as a final boss leading with the evolved/tankier form;
  bench is `[["duskhorn", 11], ["sableclaw", 11]]`. Still 2-bench,
  still `marks: 25`, still the hardest kit in the demo on paper.
- **`endingWin` is untouched, not renamed.** Step 1 proposed replacing
  it with `endingWinFather`/`endingWinHeavenfall`, but `bake_content.py`
  hardcodes `data["dialogue"]["endingWin"]` (a single `DEMO_END[]` C
  array, not the generic talk table) -- deleting/renaming that key now
  would crash bake for everyone until Step 4/5 lands. Instead:
  `endingWin` stays as-is (reads as the father-branch/default ending),
  and a new `endingWinHeavenfall` array was added alongside it, purely
  additive. Step 4/5 needs to teach `bake_content.py` to emit both as
  separate C arrays and `main.c`/`engine.ts` to pick between them on
  `choseHeavenfall` -- may as well rename `endingWin`→`endingWinFather`
  in that same commit for clarity, since the code and the rename would
  land atomically then.

**What actually landed:**
- `content/world.json` `trainers.commanderFinal`: lead `boulderam` 12,
  bench `duskhorn`/`sableclaw` 11, `marks: 25`, `winTalk:
  "commanderFinalWin"`, `set: "beatCommander"`.
- `content/world.json` `npcs[]`: new row, map `gauntlet`, mark `1`,
  `sprite: "npc/commander"` (reused, no new art needed), 3-branch
  script mirroring the quarryDriller/opal pattern exactly: `if
  beatCommander → win text`, `if choseHeavenfall → Heavenfall-flavor
  spot text`, else → father-flavor spot text (both spot branches go
  `after: "wsoldier", pending: "commanderFinal"`).
- `content/dialogue.json`: `commanderFinalSpotFather`,
  `commanderFinalSpotHeavenfall`, `commanderFinalWin` (shared), and the
  new `endingWinHeavenfall` array.
- `content/save.json` flags: appended `choseHeavenfall` and
  `beatCommander` (50/64-bit capacity now). Neither is set by any code
  yet -- that's Step 4/5. `choseHeavenfall` defaults false, so today
  the gauntlet NPC (once Step 4/5 makes it reachable) always shows the
  father-branch text; that's expected until the choice sets the flag.

Confirmed non-crashing: `commanderFinal` isn't yet in
`bake_content.py`'s `kit_keys`/`PENDING_IDS`/Dreamcast `NPC_PENDING_*`
defines (that's Step 5), so its `pending` field bakes to `-1` via the
existing `PENDING_IDS.get(..., -1)` fallback -- same as quarryDriller
sat between Task 2 and Task 4. No dispatch yet, nothing crashes.

Verified: rebake (`PACK_HASH=96d660d5...`), `check_sync --strict`
(clean but for the same 15-file art debt), `npm run typecheck`,
`make -C ports/dreamcast`, `make -C ports/dreamcast cdi` all pass.

### Step 4 — DONE (Claude A). engine.ts wiring, web side.

5-touch-point wiring for `choseHeavenfall`/`beatCommander`, matching
the `quarryDriller`/`badgeOpal` template exactly: property decl (both
new flags), reset-state, both save-serialize spots, win-handler branch,
`wsName` display entry (`commanderFinal: "Commander"`). `TRAINERS`
reads generically off `worldJson.trainers`, so `commanderFinal` needed
no separate registration to become winnable in a battle.

**The actual endgame-flow rewire, beyond the standard template:**
- `updateChoice()` now sets `this.choseHeavenfall = this.choiceCur ===
  1` right when the player confirms, before the `TALK.choiceFather`/
  `choiceHeavenfall` text plays (still tagged `"ending"` as its
  `TalkAfter`, unchanged key name to keep the diff small).
- The `next === "ending"` handler in the talk-advance switch — the spot
  that used to jump straight into `mode = "ending"` (credits) — now
  calls `this.warpTo("gauntlet", "2", "down")` instead. Beating
  `Shinigami` still leads into the choice exactly as before; only what
  happens after the choice text closes changed.
- A new `TalkAfter` value, `"creditsFinal"`, is the actual ending
  trigger now (`mode = "ending"; endI = 0`). Only `commanderFinal`'s
  win-handler passes it: `this.say(TALK[kit.winTalk] ..., who ===
  "commanderFinal" ? "creditsFinal" : null)` inside the shared
  `wsoldier` win branch — every other `wsoldier` trainer keeps passing
  `null` (no after-tag), unchanged.
- Added `endingText()` (`choseHeavenfall ? ENDING_WIN_HEAVENFALL :
  ENDING_WIN`), used at both spots that used to read `ENDING_WIN`
  directly (the `endI` length check and the credits draw call).
  `ENDING_WIN_HEAVENFALL` is a new `data.ts` export off
  `dialogueJson.endingWinHeavenfall` (the key Step 3 added).

**Not done, deliberately (Step 5's job):** no Dreamcast changes.
`commanderFinal` still isn't in `bake_content.py`'s
`kit_keys`/`PENDING_IDS`/Dreamcast defines, so `main.c` can't reach the
gauntlet or fight the boss yet — only the web build can walk this path
today.

**Playtest note:** tried to smoke-test the full choice→gauntlet→boss
flow in a headless browser by reaching into the running `CryMon`
instance directly (temporary `window.__cm` hook, reverted before
committing — not in this diff). Poking engine state mid-title didn't
stick since the per-frame loop's own title-mode update overwrites it
before a mode set from outside takes effect; getting a reliable
console-driven playthrough working would need actually clicking
through intro/title first, which felt like more machinery than this
step warranted. Deferred to Step 6, which already owns "playtest both
branches if feasible" -- do that one for real there, ideally by
driving real input through intro → new game → (localStorage save
injection or a very long real playthrough) rather than reaching into
the instance mid-frame.

Verified instead via: `npm run typecheck` clean (note: `engine.ts` is
`// @ts-nocheck`, so this mostly checks the files that import from it,
not deep type-correctness inside `engine.ts` itself -- pre-existing,
not something this step changed), `check_sync --strict` clean but for
the pre-existing art debt, dev server boots and serves 200 with no
console errors on load.

### Step 5 — DONE (Claude A). main.c wiring, Dreamcast side.

Same non-generic wiring quarryDriller's Task 4 needed, now for
`commanderFinal`, plus the warp-relocation piece that's unique to this
trainer (nobody else's win fires the ending).

**Baker (`tools/bake_content.py`):**
- Added `commanderFinal` to `kit_keys` (its 2-entry bench fits the
  existing `bench_sp[2]`/`bench_lv[2]` struct fine, same shape as
  Shinigami's bespoke kit).
- Added `commanderFinal: 13` to `PENDING_IDS`, and the matching
  `#define NPC_PENDING_COMMANDER_FINAL 13` hand-written line (this
  file's `NPC_PENDING_*` defines and `PENDING_IDS` dict are two
  separate hand-maintained lists that have to agree by number -- same
  gap format as quarry Task 4 hit).

**`main.c`, mirroring quartz/opal/quarryDriller's shape exactly:**
- `TRAINER_WSOLDIER_COMMANDER_FINAL 19`, `POST_WSOLDIER_COMMANDER_FINAL
  27` defines.
- `NPC_PENDING_COMMANDER_FINAL` dispatch in the `NPC_AFTER_WSOLDIER`
  chain.
- `case POST_WSOLDIER_COMMANDER_FINAL:` battle-setup block (message
  "COMMANDER SENDS BOULDERAM", matching the lead species from Step 3).
- The 5 save-flag touch points, x2 (one pair for `chose_heavenfall`,
  one for `beat_commander`): var decl, `ft[]` table, load, reset,
  store.
- Win-handler branch sets `beat_commander = 1`, `marks += 25`, plays
  `TALK_COMMANDER_FINAL_WIN` -- **and, unlike every other `wsoldier`
  trainer, sets `post_action = POST_CREDITS_FINAL` instead of
  `POST_NONE`.** This is the Dreamcast mirror of engine.ts's `who ===
  "commanderFinal" ? "creditsFinal" : null` from Step 4.

**The actual warp relocation (`POST_ENDING_FINAL`'s case body):**
used to be `ending_mode = 1; ending_i = 0;` directly. Now it does the
same "place exactly at a mark, no door-offset math" teleport the
title-screen new-game code already uses (`find_mark` + `col*TILE+TILE/2`
placement, `door_lock = 20`, `map_banner_timer = MAP_BANNER_TOTAL`),
landing on `gauntlet`'s mark `2`. `choice_mode`'s confirm handler now
sets `chose_heavenfall = choice_cur` right before firing
`POST_ENDING_FINAL`, mirroring engine.ts's `updateChoice()`.

**New `POST_CREDITS_FINAL 28`** does what `POST_ENDING_FINAL` used to
do (`ending_mode = 1; ending_i = 0;`) -- it's the real ending trigger
now, reached only from `commanderFinal`'s win.

**Also closed the ending-text-branching gap flagged in Step 3, rather
than deferring it again:** `bake_content.py`'s `bake_talk()` now emits
both `DEMO_END[]` (from `endingWin`) and a new `DEMO_END_HEAVENFALL[]`
(from `endingWinHeavenfall`, falling back to `endingWin`'s content if
that key were ever missing -- it isn't, Step 3 added it, this is just
defensive). Both of `main.c`'s `ending_mode` read sites (the `a_now`
length-check in the input handler, and the `draw_ending()` call in the
draw pass) now branch on `chose_heavenfall` to pick the right array.
Dreamcast's ending text matches web's now -- this step didn't leave
that half-done.

Verified: rebake (`PACK_HASH=96d660d5...` -- unchanged from Step 3
despite this ending-text addition, since `content/*.json` itself didn't
change, only the baker's Python and `main.c`), symbol-checked every new
`#define`/`KIT_`/`TALK_`/`SAVE_FLAG_`/`FLAG_`/`MAP_` name against the
freshly baked `.inc` files before building, `check_sync --strict` clean
but for the pre-existing art debt, `npm run typecheck` clean, `make -C
ports/dreamcast` clean (only pre-existing warnings, no new ones),
`make -C ports/dreamcast cdi` succeeds.

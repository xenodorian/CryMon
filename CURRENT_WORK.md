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

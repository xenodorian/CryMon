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

### 2.1 — Dreamcast walking speed bug

Web movement is fine; the Dreamcast CDI walks noticeably slower.
Investigate why (frame-rate-dependent movement math in `main.c` vs.
`engine.ts`'s delta-time-based movement is the prime suspect — compare
how each side scales player speed per frame) and fix it.

### 2.2 — Dreamcast has no audio (web does)

`chip.c` is confirmed in the build (`OBJS`, has a Makefile rule,
builds clean). Unclear yet whether this is an emulator limitation or a
real code bug — user is running the `.cdi` in a real (non-embedded)
Dreamcast emulator, not the pre-installed sandbox browser one. Start
by comparing against the reference web audio implementation
(`src/game/audio.ts` / `chip`'s JS counterpart) this port is supposed
to mirror, and troubleshoot `chip.c`'s actual sound-output path from
there (AICA driver setup, buffer submission, whether `chip_set_song`/
`chip_sfx_*` calls are actually reaching hardware output vs. just
updating internal state).

### 2.3 — Move settings into the start/title menu

Currently wherever settings live today — relocate the entry point into
the start menu.

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

### 2.5 — Replace the capture-rate mechanic + add crystal tiers

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

### 2.6 — Populate the world with more merchants

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

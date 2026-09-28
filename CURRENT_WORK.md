# CURRENT_WORK.md

Live coordination document for all CryMon agents. Read before changing the repo; update it when you finish a task.

## Current status — 2026-09-27

- Work directly on `main` unless the user explicitly asks for a branch. Multiple agents push concurrently.
- Claude's PR #39 was successfully merged into `main` as `bb43ff26`.
- Current `main` is `149b75e` after the Lead asset cleanup and successful Dreamcast CDI rebuild.
- PR #40 (battle hit effects) is **merged** into `main` (`acd675c`).
- The current Dreamcast ELF/CDI were freshly rebuilt from the cleaned Lead assets by CI. Claude re-ran bake, `gen_sprites.py`, `check_sync.py --strict` and a clean `make` locally on `149b75e`: all pass, no generated-file diff, ELF byte-identical to the committed one. Emulator/e2e verification is still separate.
- Lead's overworld walker (`npc/lead-1..4.png`) replaced 2026-09-28 with user-supplied art (navy/black greatcoat, crimson trim, peaked cap), matching his portrait. Frames 2 and 4 are a 1px breathing dip above the waist; feet stay planted.
- Latest NPC/state audit found no current regression. Shinigami gating, Lieutenant Lead's fight/walk-away choice, Dreamcast dialogue pagination, and Calder persistence are present in current `main`.
- Current generated Dreamcast content was rebaked after recent dialogue changes. Do not hand-edit generated `.inc` files; regenerate them from source.

**Showing images to the user.** Whenever the user asks to see an image
(a sprite, portrait, screenshot, generated art), send the file itself
with the session's send-file tool (Claude Code: `SendUserFile`,
`display: "render"`) instead of describing it or only giving a path.
If your tool set has no such tool, say so and give the repo path.

- Opal's overworld walker (`npc/opal-1..4.png`) and portrait (`portraits/opal.png`) replaced 2026-09-28 with user-supplied art; transparent backgrounds. Still flat or low-detail (see Claude's 2026-09-28 audit): Quartz portrait, Driller portrait, Shinigami walk frames, and the small dark walkers (heavenfallPriestess, sable, father, sentry, conscript, enforcer, birch, commander, ranger, scout, keeper, warden, oren, tessa, cross, dray, driller).

- Shinigami frames (2026-09-28, user): only `shinigami/down-1`/`down-2` (and `up-1`/`up-2`) are real art; `down-3`/`down-4`, `up-3`/`up-4` and `left`/`right` 1-3 are flat leftovers. engine.ts already walks him on 1-2 (down/up) and 3-4 (left/right) and idles on down-1. Dreamcast now idles on down-1 only (SHINIGAMI_FRAMES, baker GENERIC_WALKER_SPRITES). Open: left/right only have one good frame (4), so a sideways walk still shows flat frame 3.

## Immediate work queue

1. **Complete deployment verification.** CI has passed bake/gen-sprites/ELF/CDI and web deploy on the cleaned `main`; emulator/e2e and full Dreamcast trainer sweep remain.
2. **Complete the two-port sweep after the fresh build.** Web currently passes 70/70 maps and 61/61 trainers. The last Dreamcast trainer sweep was incomplete; the full rerun is still required.
3. **Continue regional dialogue/NPC audits.** NPCs should act from their story role and current state; avoid redundant exposition for characters who already know Max.
4. **Lead walker art:** DONE 2026-09-28 (user-supplied). Battle art (monsters/lead/*) still has an opaque painted background.

## Claude non-art pass (2026-09-27, in progress, session_01GPDsdW8JR9AqXFQ7HYorsa)

User asked for all five non-art items, in this order, pushed step by step. If this
session stops, pick up at the first step not marked DONE.

1. **Emulator/e2e verification -- DONE.** CI `checks.yml` on `main`: web Quartz e2e,
   battle e2e, map tour, CDI build all pass. Dreamcast Flycast: Quartz passes
   (badge, +16 marks, 1 battle, survives reboot). **Opal is intermittent**: passed
   on `b76a403` (run 36337517294), failed on `1d84787` and `a30d395` (run
   36341811561: "fight over after 21 presses", no badgeOpal, +0 marks, 0 battles).
   Doc-only commits, so this is a flaky Dreamcast/harness issue, not a content change.
   `main` Checks stays red until step 3 is fixed.
2. **Full Dreamcast trainer sweep -- DROPPED by user request.** Web half passed (71/71
   maps, 64/64 trainers, run 36342511707). The Dreamcast run (36343732508) was cancelled
   after 85+ min with no visible progress. Note: `sweep.yml` marks its steps
   `if: always()`, which keeps them running after a cancel; use `if: ${{ !cancelled() }}`
   if the sweep is revived.
3. **Opal fight bug root cause -- DONE.** Not a game bug. Reproduced locally (1 fail in 7
   Flycast runs): the fight, win and mercy menu all worked ("LET THEM GO. +1 REP"), but
   `emu_warden.py pause_save()` pressed Down 7 times blind and one press was dropped, so
   it opened SETTINGS instead of SAVE and nothing reached the VMU. Fix: `pause_cursor()`
   reads the green highlighted row off the screen and steps until it is on SAVE.
   Verified: 6/6 Opal runs under full CPU load, plus full Quartz + Opal (incl. reboot)
   all PASS. The "21 presses" count is normal for Opal, not a symptom.
4. **BUG-012 NPC geometry (all NPCs, DC) -- DONE.** New tool
   `ports/dreamcast/tools/npc_talk.py` (save next to each NPC, Continue, close any
   arrival scene, press A once; PASS on talk box, battle or menu). Result on `aeb6ce8`
   content: **158/158 NPCs answer A on Dreamcast**; 1 skipped (`shinigamiBoulder`, a
   blocking prop with no free tile beside it). Caveat: a PASS proves *an* NPC answered;
   `--control` showed two cases where a second NPC was also in reach. Uses its own
   white-glyph talk detector (emu_warden `talk_open()` false-fires on bright town art).
   Rerun (~35 min): `npc_talk.py --cdi ports/dreamcast/test.cdi --flycast <AppRun>
   --base e2e-out/quartz-before.bin`.
5. **Regional dialogue/NPC audit -- REPORT WRITTEN, AWAITING USER OK.** Covered the 20
   regions no earlier audit touched. Findings and proposed rewrites:
   `docs/DIALOGUE_AUDIT_2026-09-27.md` (4 state bugs, 4 redundant-exposition items).
   Nothing in `content/` changed yet. Do not apply without the user's approval.
6. **Move / growth redesign -- DONE (Claude, both engines, user approved).**
   User decisions 2026-09-27: Lv20/Lv30 moves are **one pair per crystal** (18 moves,
   like `natureMoves`); Claude implements **web and Dreamcast**; **bump the save
   version** (old saves rejected). Hype Up already exists (`logic.json` `hypeUp`).
   Stat stages only lower stats, so "self-buff" riders use Hype Up.
   Phases, each shipped on both engines together:
   - **A. Numbers:** `evolveAt` 15, `evolveAt2` 25, every secondary `maxPp` 10, every
     species `specialPp` 5, `save.json` version 7 -> 8. -- DONE (bake, check_sync
     apart from the pre-existing shinigami/idle.png FAIL, typecheck, 55 unit tests, web
     warden + battle e2e, Dreamcast build all pass).
   - **B. Lv15 gate:** Hype Up for species in an evolution line from Lv15 (not merely
     "is an evolved form"); **Attack Swap** at Lv15 for single-stage species (basic
     damage, then pick a party CryMon to switch in; foe AI uses it as a plain hit). -- DONE.
     `logic.json` `growth.hypeUpAt`/`attackSwapAt` + `attackSwap`; web `data.ts`
     `knowsHypeUp(m)`/`knowsAttackSwap(m)`, engine phase `"swap"` + `pickSwap()`; DC
     `knows_hype_up()`/`knows_attack_swap()`, `UMOVE_SWAP`, battle phase 5 chooser.
     Verified: new `scripts/e2e-growth.mjs` (15/15, in checks.yml), web warden e2e,
     Flycast Quartz + Opal, and a Flycast Attack Swap run (hit, SWAP IN, OUT, foe
     answers). Note: `test:e2e:battle` "fast foe opens the round" is flaky on plain
     main too (2 of 3 runs failed before this change); not fixed here.
   - **C. Lv20 / Lv30 crystal moves:** Lv20 basic-power hit + rider, 10 PP/battle;
     Lv30 special-power hit + rider, 5 PP/battle; rider = foe stage down, foe status,
     or self Hype Up; applies only when the hit lands. -- DONE. `logic.json`
     `crystalMoves` (18 moves, names in the table there) + `growth.signatureAt`/
     `finisherAt`; web `data.ts` kinds `signature`/`finisher`, engine `applyRider()`,
     finisher reuses the special minigame (`b.minigameMove`); DC baker
     `CRYSTAL_MOVES[NATURE_N][2]`, `UMOVE_SIG`/`UMOVE_FIN`, `apply_rider()`,
     `battle_pick_crystal()`, `mg_fin`/`mg_move`. Foe AI uses them (30%) at plain power.
     Verified: `e2e-growth.mjs` (25 checks), web warden e2e, Flycast Quartz + Opal, and
     Flycast runs of Rally Blow (hit + STATS UP) and Crushing Charge (minigame + STR
     FALLS). Fixed on the way: DC `pend_swap` was never cleared, so a crystal move
     opened SWAP IN; DC attack rows now show names only, uses + rider on a detail line.

## Standing repository rules

- Commit and push each completed step to `main`; do not batch unrelated steps.
- Before every push: fetch current `main`, rebase/merge, regenerate generated files after conflicts, rebuild, verify, fetch again, push, and confirm the resulting `main` commit.
- Never hand-replace `content/world.json`; never empty its NPC list.
- `content/world_map_layout.json` is canonical for the overworld graph. Regenerate `public/maps/sorrow-county-town-map.svg` after layout changes.
- Player-facing name of internal map ID `veld` is **CRYTOWN**. Do not rename the internal ID without a save migration.
- Cathleen is the only CryMon who speaks unless a story leg explicitly changes that.
- Dreamcast changes are not hardware-verified unless an actual emulator/build run was performed.
- Art must be transparent and correctly magenta-keyed; do not leave magenta backgrounds or halos.

## Required verification

For normal Dreamcast/source changes:
```
python3 tools/bake_content.py --content content --out ports/dreamcast/src
python3 ports/dreamcast/tools/gen_sprites.py
python3 tools/check_sync.py --strict
npm run typecheck
make -C ports/dreamcast
```

For a deployment/"ship the build" request, also run the CDI target and emulator/e2e checks, then verify CI/deploy status.

### Generated-content rule

Source of truth is `content/*.json` plus source art. Generated Dreamcast output includes `content_*.inc`, `sprites.h`, and `ports/dreamcast/disc/MONSTERS.BIN`. Regenerate rather than manually merging generated output.

## Important engine/state gotchas

- An NPC script step with `pending` must also have the correct `after` (for example `"after": "wsoldier"`) or its battle trigger will not fire.
- NPC script conditions use `ifNot`; obsolete keys such as `unless` must not be used. `check_sync` validates script keys.
- Dreamcast `wsoldier` trainer handling is partly hand-wired. New trainers may require matching `TRAINER_WSOLDIER_*`, `POST_WSOLDIER_*`, `NPC_PENDING_*`, battle setup, and save-flag wiring in `main.c`.
- Before adding Dreamcast `#define` values, inspect existing `POST_*` and `TRAINER_WSOLDIER_*` numbers. Duplicate switch values have broken builds before.
- `tools/bake_content.py` has multiple trainer mappings (`kit_keys`, `PENDING_IDS`, and C defines); keep them synchronized.
- `dialogue.json` `endingWin` is special-cased in the baker.
- Validate newly pushed PNGs with Pillow; truncated PNGs have previously broken `gen_sprites.py`.

## Save-format contract

Current save format is v6, 256 bytes. Do not change offsets or reorder map IDs without an explicit migration.

- `content/save.json` is the save-layout source of truth.
- `world.mapIds` order must exactly match `save.mapOrder`; it is append-only.
- Legacy unreachable map ID `gauntlet` remains intentionally in the order for save compatibility.
- Two flag bits remain free; adding a flag does not by itself require a version bump.
- Expanding the bag requires a save-format migration/version bump.

## Completed work that still matters

### NPC/state
- **Shinigami:** generic boulder sprite is hidden until `cathleenCaught`, remains while imprisoned, and is removed after `beatShinigami`. Dreamcast must not draw a duplicate generic walker.
- **Lieutenant Lead:** interaction offers Fight or Walk Away. Fight sets `beatLieutenantLead`; walk-away does not.
- **Lead art cleanup (2026-09-27):** all corrupt/truncated Lead overworld source/install files were removed. `public/sprites/npc/lead-1..4.png` now resolve to a valid transparent 48x64 military-officer asset; battle frames and portrait were structurally valid and retained. CI regenerated `sprites.h`/CDI successfully.
- NPC/state audit covered 164 NPCs / 461 script steps: unknown keys/flags, invalid `after`, contradictory conditions, dead steps, and source-vs-generated script discrepancies; no current discrepancy found.
- **Dreamcast dialogue pagination:** long wrapped dialogue is paginated instead of clipped; page state resets when a new sequence begins.

### Art/runtime
- Still-frame optimization is active on web and Dreamcast. Web aliases missing still frames to frame 1; Dreamcast records frame counts and clamps still animations.
- Dreamcast monster battle art normally streams from `MONSTERS.BIN`; resident 16×16 icons provide fallback.
- Current art systems include generated NPC walkers/portraits, painted overworld tiles, themed buildings, battle backdrops, ambience, item icons, title/ending screens, and Hollow-specific art. Do not redo these wholesale unless requested.
- **Battle effects (Claude, 2026-09-27):** one hit burst per real crystal (`tools/pixelforge/hitfx.py`, natures from logic.json), plus particles, shock ring, screen flash, damage-scaled shake and floating numbers, all from `content/sprites.json` `battleFx`. Web: `src/game/battleFx.ts`; Dreamcast: `gen_sprites.py emit_battle_fx()` + main.c `fx_*`. Both only watch battle state. `emu_warden.py` saves quick `fx-fight-NN.png` frames during fights.
- **Dreamcast Opal warden check:** was a harness flake (pause menu Down press dropped, landed on SETTINGS). Fixed in `emu_warden.py` by reading the highlighted row.
- Player monster back-view sprites are **not implemented**; both engines currently use front battle art. Treat back views as a separate art/engine project.

### World validation
- `tools/world_graph/run_full_audit.py` generates and validates the Town Map projection and currently passes. Re-run after world-layout/Town Map changes.
- CRYTOWN ↔ HOME is a compatibility-sensitive warp; keep it synchronized with `world_map_layout.json`.
- Grove's Gauntlet exit is south; Ruins exit is east. Both engines support east/west warps.

### Testing
- Web map tour: 70/70 maps passed.
- Web trainer sweep: 61/61 scripted trainers passed.
- Dreamcast trainer sweep requires a fresh complete rerun after the current build.
- Dreamcast emulator tooling: `ports/dreamcast/tools/emu_warden.py`; map/trainer generators are under `ports/dreamcast/tools/` and `scripts/`.

## Coordination notes

Keep this file short. Record only active work, durable contracts, important recent fixes, and blockers. Detailed archaeology belongs in git history. When a task is fully verified, replace its temporary working note with a one- or two-line durable result.

### Move / growth redesign (queued — Grok, 2026-09-27)

**Not implemented yet.** Design contract for a future growth pass. Current live values remain `secondaryAt: 5`, `specialAt: 10`, `evolveAt: 12`, `evolveAt2: 22`, special PP ~3, mixed secondary PP.

| Level | Rule |
|------:|------|
| — | **Secondary moves:** all **10 PP** (stage and status; shinies too) |
| — | **Special moves:** all **5 PP** (was ~3) |
| **15** | **First evolution** (`evolveAt` → 15) |
| **15** | Species **with** a second stage: learn **Hype Up** at 15 (same gate as first evo, not only “on evolve”) |
| **15** | Species **without** a second stage: learn **Attack Swap** — deals the same damage as their **basic** move, then the player chooses another party CryMon to switch in |
| **20** | **All** CryMon learn a move that deals **basic-tier damage** and also applies a **debuff, status, or self-buff** (per-species definition TBD) |
| **25** | Species with a **third** stage evolve (`evolveAt2` → 25) |
| **30** | **All** CryMon learn a **new special** that also applies a **debuff, status, or self-buff** (per-species definition TBD) |

**Implied engine work when implementing:**
- `content/logic.json` `growth` + `natureMoves` / `shinyMove` `maxPp` + per-species `specialPp`
- `unlockedMoves()` gates; new move kinds for Attack Swap and the Lv20 / Lv30 signatures
- Switch-on-hit flow for Attack Swap (web + Dreamcast)
- Content pass: define the Lv20 and Lv30 effects per species (or by nature)

Do not partially ship without updating both engines and save/docs if PP or learnsets change mid-playthrough.


# CURRENT_WORK.md

Live coordination document for all CryMon agents. Read before changing the repo; update it when you finish a task.

## Current status — 2026-09-27

- Work directly on `main` unless the user explicitly asks for a branch. Multiple agents push concurrently.
- Claude's PR #39 was successfully merged into `main` as `bb43ff26`.
- Current `main` is `149b75e` after the Lead asset cleanup and successful Dreamcast CDI rebuild.
- PR #40 (battle hit effects) is **merged** into `main` (`acd675c`).
- The current Dreamcast ELF/CDI were freshly rebuilt from the cleaned Lead assets by CI. Claude re-ran bake, `gen_sprites.py`, `check_sync.py --strict` and a clean `make` locally on `149b75e`: all pass, no generated-file diff, ELF byte-identical to the committed one. Emulator/e2e verification is still separate.
- Lead's overworld walker (`npc/lead-1..4.png`) is valid but is a green-camo soldier that does not match his navy/red officer portraits; all four frames are identical. Needs matching art.
- Latest NPC/state audit found no current regression. Shinigami gating, Lieutenant Lead's fight/walk-away choice, Dreamcast dialogue pagination, and Calder persistence are present in current `main`.
- Current generated Dreamcast content was rebaked after recent dialogue changes. Do not hand-edit generated `.inc` files; regenerate them from source.

## Immediate work queue

1. **Complete deployment verification.** CI has passed bake/gen-sprites/ELF/CDI and web deploy on the cleaned `main`; emulator/e2e and full Dreamcast trainer sweep remain.
2. **Complete the two-port sweep after the fresh build.** Web currently passes 70/70 maps and 61/61 trainers. The last Dreamcast trainer sweep was incomplete; the full rerun is still required.
3. **Continue regional dialogue/NPC audits.** NPCs should act from their story role and current state; avoid redundant exposition for characters who already know Max.
4. **Lead walker art:** replace with a navy/red officer walker matching the portraits.

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
- **Dreamcast Opal warden check:** fails the same way on the battle-effects branch and on PR #39 (fight ends after 21 presses, no battle counted). Not caused by battle effects; not root-caused yet.
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

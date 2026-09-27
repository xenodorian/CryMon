# BUG_LOG.md

Static bug audit for CryMon. This log records potential defects and test gaps identified during code and build review. Items are not all confirmed runtime bugs.

## High priority

### BUG-001: Dreamcast build stability after recent art changes
Status: Verified 2026-09-27. Clean bake + `make` in the CI toolchain image (einsteinx2/dcdev-kos-toolchain:gcc-9) builds the ELF with no errors.
The Dreamcast build has recently failed during development after content/art changes. Re-run the full Dreamcast pipeline from a clean checkout and verify that the generated content, ELF, and CDI all build successfully.

### BUG-002: Quartz victory flow requires end-to-end verification
Status: Fixed and verified 2026-09-27 (web, real run). `npm run test:e2e:quartz`.
Verify the complete Quartz sequence on Dreamcast and web:
1. Talk to Quartz.
2. Start the Quartz battle.
3. Win the battle.
4. Set `badgeQuartz`.
5. Award 16 Marks.
6. Switch Quartz to the win dialogue.
7. Save.
8. Reload.
9. Confirm Quartz remains defeated and the badge persists.
Result: all nine steps pass on web. Fixed on the way: web skipped the quartzWin line after the fight, and counted the fight as two battles. Dreamcast steps verified from code plus a host build of save.c reading the web save (byte-identical repack); no emulator run yet.

### BUG-003: Quartz progression parity between web and Dreamcast
Status: Fixed 2026-09-27. Both ports now go battle, winTalk, mercy menu, one battle counted; mercy header names the trainer on both.
The web content uses the Quartz NPC pending/progression state, while Dreamcast uses generated content and separate C-side battle handling. Confirm that both platforms transition through the same prerequisite, battle, victory, dialogue, and save states.
Also fixed: save x/y were in 20px tiles on Dreamcast and 32px on web in the "shared" blob. Dreamcast now converts to web pixels.

### BUG-004: Opal warden is not implemented
Status: Stale, closed 2026-09-27. Opal has a kit, NPC and badge handling in both ports; the e2e test covers Opal too.
`badgeOpal` and the second crystal warden are still absent from the current coordination status. Implement and then add parity checks for web and Dreamcast.

## Medium priority

### BUG-005: Generated-content parity risk
Status: Fixed 2026-09-27. `.github/workflows/checks.yml` re-bakes and fails if any content_*.inc differs, then runs check_sync --strict.
Web and Dreamcast consume generated/baked content through different paths. A JSON change can succeed on one platform while the generated Dreamcast content is stale or fails to compile. CI should verify regeneration from a clean state.

### BUG-006: No automated trainer gameplay regression tests
Status: Fixed 2026-09-27. scripts/e2e-trainers.mjs plays all 61 scripted trainer fights on web (61/61 pass); emu_warden.py plays them on Dreamcast. Both run nightly in sweep.yml.
The repository validates content relationships, but does not automatically execute trainer interactions through battle victory, rewards, dialogue changes, and persistence.

### BUG-007: No Dreamcast emulator regression test
Status: Fixed 2026-09-27. CI boots the real CDI headless in Flycast (ports/dreamcast/tools/emu_warden.py), plays Quartz and Opal from a web-made save, saves, reboots, Continues, and checks badge, marks and battle count from the VMU image. Screenshots in the `e2e` artifact.
CI builds the Dreamcast artifacts but does not establish that the CDI boots in an emulator, accepts controller input, or reaches gameplay.

### BUG-008: Dreamcast save persistence is not automatically tested
Status: Fixed 2026-09-27. save_host_check.c tests save.c on the host, and the Flycast test (BUG-007) covers VMU write, reboot and reload.
There is no automated test covering save, reset/reload, and restoration of progression flags on the Dreamcast target.

### BUG-009: Web/Dreamcast save compatibility is not automatically tested
Status: Fixed 2026-09-27. CI feeds each web e2e save to the Dreamcast save.c and requires the badge flag and a byte-identical repack.
The two implementations have separate save paths and formats. There is no automated parity test confirming equivalent progression semantics.

### BUG-010: NPC rendering and interaction can diverge
Status: Found and fixed 2026-09-27 (Dreamcast). Seven JSON-only NPCs (bogwalker, reedguard, quartz, opal, driller, fenn, dray) were marked hand-drawn in bake_content.py but no hand code drew them: talkable but invisible on DC. They now use the generic roaming path; the Flycast screenshots show Quartz and Opal.
Rendering and interaction are separate systems. An NPC can potentially remain interactable while its sprite is missing or fail to render while still having an interaction footprint.

### BUG-011: Quartz NPC default interaction footprint may be oversized
Status: Working as designed, 2026-09-27. Web uses logic.json `interact` (48x52 + 16 buffer) and the closest NPC wins (Dreamcast's try_npc_script says it scales the same box; not re-checked); Quartz and Opal are nine rows apart, so no cross-talk.
Quartz does not specify an explicit interaction width/height in the current NPC data. Verify that the default interaction rectangle does not cause accidental interactions from adjacent tiles.

### BUG-012: Dreamcast NPC geometry differs from web geometry
Status: Verified 2026-09-27. ports/dreamcast/tools/npc_talk.py: in Flycast, standing next to each NPC and pressing A starts its talk for 158/158 NPCs (shinigamiBoulder skipped: no free tile). A PASS shows an NPC answered, not always the target when two are in reach.
Dreamcast interaction/render coordinates are scaled from the web coordinate system. Rounding during conversion can produce one-pixel/tile discrepancies at some positions.

## Lower priority

### BUG-013: Save checksum excludes Pokédex byte ranges
Status: Won't fix for now, 2026-09-27. On Dreamcast the VMS CRC already covers the whole file (save.c save_restore). Widening the web checksum changes the shared format and would reject every existing save for little gain on localStorage.
The web save checksum does not cover all serialized data. The Pokédex seen/caught ranges are outside the checksum-covered bytes, so corruption in those fields may not be detected.

### BUG-014: Saved player coordinates need walkability validation
Status: Fixed 2026-09-27. Both ports move a loaded position that is off-map, solid or a door to the nearest walkable tile (engine.ts rescueStandPos, main.c rescue_stand_pos). e2e covers web.
Loading a save should ideally validate that the stored player position is within map bounds and corresponds to a legal walkable location before applying it.

### BUG-015: Save version/key migration risk
Status: Won't fix for now, 2026-09-27. The binary version byte (save.json `version`) is what both ports check; renaming the localStorage key would orphan saves without adding safety.
The web save key remains `crymon.save.v1` while the binary save schema has advanced. This is not necessarily a current defect, but future migrations can become ambiguous if key and schema versioning diverge.

### BUG-016: Asset loading failures are not surfaced clearly
Status: Fixed 2026-09-27. Failed art is listed, warned once, and exposed via `window.__crymon.artStatus()`; e2e fails on any missing art.
Web art loading can fail without producing a user-visible error. Missing assets may therefore appear as invisible sprites rather than a diagnosable loading failure.

### BUG-017: Web readiness can precede complete art loading
Status: Mitigated 2026-09-27. Progressive loading is intentional (critical art first); `artStatus().done` now says when the rest has finished.
The web engine can become ready before asynchronous art loading has completely finished. Early interaction/rendering can therefore occur while some assets are still unavailable.

## Recommended regression sequence

After the next Dreamcast build succeeds, test Quartz specifically on both platforms, then test save/reload persistence. After Opal is implemented, repeat the same sequence for Opal.

## Scope note

Quarry remains parked and is intentionally excluded from this bug log's implementation scope.

### BUG-018: Dreamcast HUD text overlapped (found in Flycast)
Status: Fixed 2026-09-27. The map name (scale 2, top right) printed over the lead and scroll lines, "SAVED" printed over the lead's name, and the foe's battle line ("NEEDLEROOT LV10 20/66") ran off the right edge with the player's nature badge over the "/". Map name is now scale 1 on the REP row, the toast sits centered under the HUD, and the battle lines stay on screen with badges beside the text.

### BUG-019: Needleroot art has magenta patches
Status: Fixed, closed 2026-09-27 by commit 005d363. A scan of every PNG under public/sprites finds no magenta pixels left. Original note: public/sprites/monsters/needleroot/*.png contain opaque magenta pixels (frame 3: 803 of 4704 opaque pixels), which show on both ports. The DC converter is not the cause. Owned by the art thread.

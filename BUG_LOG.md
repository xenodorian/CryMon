# BUG_LOG.md

Static bug audit for CryMon. This log records potential defects and test gaps identified during code and build review. Items are not all confirmed runtime bugs.

## High priority

### BUG-001: Dreamcast build stability after recent art changes
Status: Investigate.
The Dreamcast build has recently failed during development after content/art changes. Re-run the full Dreamcast pipeline from a clean checkout and verify that the generated content, ELF, and CDI all build successfully.

### BUG-002: Quartz victory flow requires end-to-end verification
Status: Unverified.
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

### BUG-003: Quartz progression parity between web and Dreamcast
Status: Unverified.
The web content uses the Quartz NPC pending/progression state, while Dreamcast uses generated content and separate C-side battle handling. Confirm that both platforms transition through the same prerequisite, battle, victory, dialogue, and save states.

### BUG-004: Opal warden is not implemented
Status: Open.
`badgeOpal` and the second crystal warden are still absent from the current coordination status. Implement and then add parity checks for web and Dreamcast.

## Medium priority

### BUG-005: Generated-content parity risk
Status: Test gap.
Web and Dreamcast consume generated/baked content through different paths. A JSON change can succeed on one platform while the generated Dreamcast content is stale or fails to compile. CI should verify regeneration from a clean state.

### BUG-006: No automated trainer gameplay regression tests
Status: Test gap.
The repository validates content relationships, but does not automatically execute trainer interactions through battle victory, rewards, dialogue changes, and persistence.

### BUG-007: No Dreamcast emulator regression test
Status: Test gap.
CI builds the Dreamcast artifacts but does not establish that the CDI boots in an emulator, accepts controller input, or reaches gameplay.

### BUG-008: Dreamcast save persistence is not automatically tested
Status: Test gap.
There is no automated test covering save, reset/reload, and restoration of progression flags on the Dreamcast target.

### BUG-009: Web/Dreamcast save compatibility is not automatically tested
Status: Test gap.
The two implementations have separate save paths and formats. There is no automated parity test confirming equivalent progression semantics.

### BUG-010: NPC rendering and interaction can diverge
Status: Potential.
Rendering and interaction are separate systems. An NPC can potentially remain interactable while its sprite is missing or fail to render while still having an interaction footprint.

### BUG-011: Quartz NPC default interaction footprint may be oversized
Status: Potential.
Quartz does not specify an explicit interaction width/height in the current NPC data. Verify that the default interaction rectangle does not cause accidental interactions from adjacent tiles.

### BUG-012: Dreamcast NPC geometry differs from web geometry
Status: Potential.
Dreamcast interaction/render coordinates are scaled from the web coordinate system. Rounding during conversion can produce one-pixel/tile discrepancies at some positions.

## Lower priority

### BUG-013: Save checksum excludes Pokédex byte ranges
Status: Potential integrity issue.
The web save checksum does not cover all serialized data. The Pokédex seen/caught ranges are outside the checksum-covered bytes, so corruption in those fields may not be detected.

### BUG-014: Saved player coordinates need walkability validation
Status: Potential.
Loading a save should ideally validate that the stored player position is within map bounds and corresponds to a legal walkable location before applying it.

### BUG-015: Save version/key migration risk
Status: Maintenance risk.
The web save key remains `crymon.save.v1` while the binary save schema has advanced. This is not necessarily a current defect, but future migrations can become ambiguous if key and schema versioning diverge.

### BUG-016: Asset loading failures are not surfaced clearly
Status: Potential.
Web art loading can fail without producing a user-visible error. Missing assets may therefore appear as invisible sprites rather than a diagnosable loading failure.

### BUG-017: Web readiness can precede complete art loading
Status: Potential.
The web engine can become ready before asynchronous art loading has completely finished. Early interaction/rendering can therefore occur while some assets are still unavailable.

## Recommended regression sequence

After the next Dreamcast build succeeds, test Quartz specifically on both platforms, then test save/reload persistence. After Opal is implemented, repeat the same sequence for Opal.

## Scope note

Quarry remains parked and is intentionally excluded from this bug log's implementation scope.

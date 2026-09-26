# Dreamcast port

Runtime only. Contract: [`../../docs/CRYMON.md`](../../docs/CRYMON.md).

```
python3 ../../tools/bake_content.py --content ../../content --out src
python3 tools/gen_sprites.py
python3 ../../tools/check_sync.py --strict
make
make cdi
```

## Disc streaming

The game is no longer one executable that holds everything. `gen_sprites.py`
writes the monster battle frames to `disc/MONSTERS.BIN` (not in git; it is
regenerated), `make cdi` puts that file on the disc next to `1ST_READ.BIN`,
and `src/disc.c` reads it at runtime through the BIOS GD-ROM calls (no KOS).
Battles load the two CryMon on screen into two slots; 16x16 icons for every
species stay in RAM for the party menu and as a fallback if a disc read
fails. The ELF went from ~9.3 MB to ~1.9 MB.

- `make sprites STREAM=0 && make STREAM=0 && make cdi STREAM=0` builds the
  old everything-in-RAM version (no disc reads at all) if streaming ever
  misbehaves on hardware.
- New big data (region packs for the Sephirot, music, maps) should follow the
  same pattern: a generated file on the disc + `disc_find()` /
  `disc_read_sectors()`, loaded on entry and freed on exit.


# CryMon — content plan and agent coordination

Companion to [`CRYMON.md`](CRYMON.md). That file says *what* is shared.
This one says *how multiple agents edit it at once without colliding*,
and *which folders must never be created*.

Read this before adding a feature, a file, or a folder.

---

## 1. Why this file exists

The shared-content architecture is correct, but it is currently not
holding. Measured against `xenodorian/CryMon@origin/main` and
`xenodorian/BeelzFight@claude/relaxed-rubin-u950jh`:

| Thing | Copies | State |
|---|---|---|
| `content/*.json` | 2 | **drifted** — `logic.json` exists only in CryMon |
| Dreamcast `main.c` | 2 | **drifted** |
| `gen_sprites.py` | 2 | **drifted** |
| Dreamcast `Makefile` | 2 | **drifted** |
| `bake_content.py` | **3** | **all three differ**, two of them inside CryMon alone (`tools/` and `ports/dreamcast/tools/`) |
| Generated `content_*.inc` | 2 sets | BeelzFight set is missing `content_logic.inc` |
| Sprite packs | 3 | `public/sprites/` + `art/sprites/` + `placeholder_sprites/` |

Every one of these is a place where a feature can land on one port and
silently not the other. The plan below removes the duplicates and gives
each agent a lane.

---

## 2. The two hard rules

**Rule 1 — One tree.** `xenodorian/CryMon` is the game. It already
contains the Dreamcast port at `ports/dreamcast/`. There is no reason
for a second working copy of the port to exist anywhere.

**Rule 2 — Generated files are not source.** Anything a tool can
reproduce is build output. Two agents who both run a build produce two
different multi-thousand-line outputs and a guaranteed conflict on
files nobody wrote.

---

## 3. Folders that must never be created

Creating any of these is the failure this document exists to prevent.
If a task seems to need one, the answer is in §5 instead.

| Never create | Because | Use instead |
|---|---|---|
| A second `content/` | Splits the source of truth; already caused the `logic.json` drift | `CryMon/content/` |
| A second sprite pack (`art/sprites/`, `placeholder_sprites/`, `assets/dc/`) | Art silently differs per port | `public/sprites/` |
| A second `bake_content.py` or `gen_sprites.py` | Two bakers = two dialects of the same JSON | `tools/bake_content.py`, `ports/dreamcast/tools/gen_sprites.py` |
| A per-port data file (`dc_species.json`, `logic.dc.json`, `dialogue_dc.json`) | This is the "just for DC" trap `AGENTS.project.md` already bans | Add a field to the existing shared file |
| A new `backups/` snapshot | They are never read back and they double every grep hit | Git history |
| A second port directory for a port that already exists | The whole problem above | `ports/<name>/` |

Adding a **new port** is the one legitimate new folder: `ports/<name>/`,
consuming `content/` and `public/sprites/` like the Dreamcast one does.
It never gets its own content or art.

---

## 4. Ownership lanes

Agents work in parallel by owning **non-overlapping files**. Claim a
lane, stay in it, and a second agent in a different lane can never
conflict with you.

| Lane | Owns | Never touches |
|---|---|---|
| **Content** | `content/*.json` | engine code, `.inc`, art |
| **Web engine** | `src/game/`, `src/components/` | `content/`, `main.c` |
| **DC runtime** | `ports/dreamcast/src/main.c`, `dc.ld`, `Makefile` | `content/`, `src/game/` |
| **Art** | `public/sprites/` | everything else |
| **Toolchain** | `tools/bake_content.py`, `ports/dreamcast/tools/gen_sprites.py` | `content/`, engines |

Two agents in the **Content** lane at once: split by *file*
(`species.json` vs `dialogue.json`), and if you must share a file, split
by *top-level key* (`world.json` → `warps` vs `trainers`). Never
reformat or re-sort a JSON file you do not own the whole of — it turns a
3-line diff into a whole-file conflict.

A feature that spans lanes (most do) is **sequential, not parallel**:
content first, then baker, then the two engines. §5 is that order.

---

## 5. Adding a feature so both ports get it

The order matters. Data before rules before engines.

1. **Data** → `content/*.json`. New species field, new map, new talk
   beat, new warp. Never a new file.
2. **Rules and constants** → `content/logic.json`. Anything both ports
   must agree on: multipliers, thresholds, gating. Not a magic number
   in two engines.
3. **Baker** → `tools/bake_content.py`. Emit the new field into the
   `.inc` so C can see it.
4. **Web engine** → `src/game/`. Read the JSON. Do not re-declare the
   data.
5. **DC runtime** → `ports/dreamcast/src/main.c`. Read the baked
   `.inc`. Do not re-declare the data.

If you stop after 4, the Dreamcast silently lacks the feature. If you
stop after 5, the web does. **A feature is not done until both engines
read the same shared value.**

### Worked example — Crystal Natures

The typing system currently implemented in the BeelzFight `main.c`
maps onto this as:

| Step | Change |
|---|---|
| 1. Data | `species.json`: add `"nature": "spinel"` to each of the 20 entries |
| 2. Rules | `logic.json`: add `natures` — the 7-name ring order, `strongMul: 1.5`, `weakMul: 0.65`, and the "beats the next two around the ring" rule as data |
| 3. Baker | `bake_species()` emits `NAT_<NAME>`; a new `bake_logic()` field emits the ring and multipliers |
| 4. Web | `engine.ts` damage math multiplies by the ring lookup |
| 5. DC | `main.c` keeps `nature_matchup()` / `nature_scale_dmg()` but reads the ring and multipliers from the baked logic, not from `#define`s |

The CryDex UI, the dex-caught tracking, bench XP and the Reach gauntlet
follow the same split: the *numbers and text* are content, the *drawing
and input* are per-port presentation and legitimately differ.

---

## 6. Generated files

These are build output. They should be `.gitignore`d, and no agent
should ever hand-edit or hand-resolve a conflict in one:

```
ports/dreamcast/src/content_*.inc
ports/dreamcast/src/sprites.h
*.elf
*.cdi
```

Rebuild instead of merging:

```
python3 tools/bake_content.py --content content --out ports/dreamcast/src
python3 ports/dreamcast/tools/gen_sprites.py
```

A shipped CDI is a **release artifact**, not a source file. If one must
be committed for distribution, it belongs in exactly one place
(`public/rom/`), produced by one release step, never rebuilt casually by
whoever happened to touch the tree.

> Note: `bake_content.py` also carries `SPECIES_ORDER`, a hand-kept list
> of the 20 species ids. That is content knowledge living in the
> toolchain, and it will drift the first time someone adds a species and
> forgets. It should be derived from `species.json` instead.

---

## 7. Conflict protocol

- **Rebase or merge before you start**, not after you finish.
- **Never force-push a shared branch.** Merge; a merge commit keeps
  everyone else's checkout valid.
- **Conflict in a generated file** → discard both sides and re-run the
  tool. Never hand-merge.
- **Conflict in JSON** → resolve key by key. If the whole file conflicts,
  someone reformatted; take the un-reformatted side and re-apply the
  real change.
- **Conflict in an engine file** → the lane owner resolves it. If you are
  not the owner, say what you need and let them.
- **Another agent pushed while you worked** → read their change before
  reconciling. A refactor that moved your data out of a file is not a
  conflict to defeat, it is the new location to move your change into.

---

## 8. Migration — getting from here to the plan

In dependency order. Steps 1 and 2 are the ones that stop the bleeding.

1. **Collapse the duplicate bakers.** Keep `tools/bake_content.py`.
   Delete `ports/dreamcast/tools/bake_content.py`. Point every doc and
   Makefile at the survivor.
2. **Retire `BeelzFight/crymon-dreamcast/`** as a working copy — it is
   the source of the content and `main.c` drift. Either delete it in
   favour of `CryMon/ports/dreamcast/`, or reduce it to a README
   pointing at CryMon. *(Destructive and cross-repo: needs the owner's
   go-ahead, see §9.)*
3. **Port the in-flight Dreamcast work** (Crystal Natures, CryDex, bench
   XP, the Reach endgame) into `content/` + `tools/bake_content.py` per
   §5, so both ports get it.
4. **Gitignore the generated files** and drop them from the index.
5. **Derive `SPECIES_ORDER`** from `species.json`.
6. **Fold `art/sprites/`** into `public/sprites/` and delete the
   fallback path from `gen_sprites.py`.

---

## 9. Open decisions for the owner

These need a human call; they are not agent judgement:

1. **Does `BeelzFight/crymon-dreamcast/` get deleted, or kept as a
   pointer?** Deleting it is the clean fix and removes the whole drift
   class. Keeping a copy means accepting a sync step forever.
2. **Do committed `.cdi`/`.elf` artifacts stay in git?** They are large,
   they conflict on every parallel build, and they are reproducible.
3. **`CLAUDE.md` standing rule 2** says "Heavenfall / father
   resurrection is narrative-only unless the user asks to make them
   party members." The user has now asked, and the work is built — so
   that rule needs updating rather than being silently contradicted.

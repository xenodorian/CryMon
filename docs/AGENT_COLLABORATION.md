# CryMon — agent collaboration contract

**Every agent working on CryMon follows this file.** Grok, Emergent,
Claude, and anything added later. It outranks habit, convenience, and
whatever a previous turn did.

More than one agent is usually working on this project at the same time.
The rules below exist so two agents can work at once without producing
two versions of the game.

Architecture reference: [`CRYMON.md`](CRYMON.md).
Before you finish a turn: `python3 tools/check_shared.py`.

---

## The three laws

**1. One repo.** `xenodorian/CryMon` is the only repository for CryMon.
The web game and the Dreamcast port both live in this tree. Do not start
work in a second repo, do not create one, and do not treat a copy in
another repo as a place to add features.

> `xenodorian/BeelzFight` `crymon-dreamcast/` is a pre-existing second
> copy of the Dreamcast port. It is **frozen**: no new features, no new
> content. It is being retired (§9). If you find yourself editing it,
> stop — you are in the wrong tree.

**2. One copy of everything shared.** One content pack. One sprite pack.
One baker. One of each engine. If you are about to write a file whose
job is already done by an existing file somewhere else, the answer is to
change the existing file. Duplicating it is the failure this contract
exists to prevent.

**3. One direction.** Shared data flows `content/` → baker → each
engine. Never the other way, and never sideways between engines. An
engine reads shared values; it does not restate them, cache them in its
own table, or "temporarily" hardcode them.

---

## Why these are laws and not suggestions

They were already written as suggestions, in `CRYMON.md` and
`AGENTS.project.md`, and within about a day of the shared-content
refactor landing:

- `content/` had two copies, and they had **already drifted** —
  `logic.json` existed in one and not the other.
- The Dreamcast `main.c`, `Makefile` and `gen_sprites.py` all differed
  between the two trees.
- `bake_content.py` existed **three** times, all three different, two of
  them inside this repo alone.

Nobody decided to do that. It happened because copying is the path of
least resistance when you are in a hurry and the rule is only prose. So
the rule is now also a script that fails: `tools/check_shared.py`.

---

## Canonical paths

This table is the whole registry. A file that duplicates a job below is
a duplicate, whatever it is called or wherever it sits.

| Job | The one place |
|---|---|
| Species, items, maps, dialogue, warps, encounters, trainers, NPC marks | `content/*.json` |
| Shared rules, constants, thresholds, multipliers | `content/logic.json` |
| Pixel art | `public/sprites/` |
| JSON → C baker | `tools/bake_content.py` |
| Sprites → C baker | `ports/dreamcast/tools/gen_sprites.py` |
| Web engine | `src/game/` |
| Dreamcast runtime | `ports/dreamcast/src/main.c` |
| Shipped release artifact | `public/rom/` |

Everything under `backups/` is reference-only. Never edit it, never
copy from it forward, never add to it.

---

## Before you create a file or folder

Work down this list. Stop at the first line that applies.

1. **Does a file already do this job?** (see the table) → edit that one.
2. **Is it a copy "so I can work without breaking the other one"?** →
   no. Use a branch.
3. **Is it a per-port version of shared data** (`species_dc.json`,
   `logic.web.json`, a second dialogue file) → no. Add a field to the
   shared file; let each engine read what it needs.
4. **Is it generated?** (`*.inc`, `sprites.h`, `*.elf`, `*.cdi`) → it is
   build output, not a file you author. §6.
5. **Is it a report, plan, summary, or notes about work you just did?** →
   put it in the commit message or the reply. Do not add a document to
   the tree.
6. **Is it a new port?** → `ports/<name>/`, consuming `content/` and
   `public/sprites/` exactly as the Dreamcast one does. It never gets
   its own content or art.
7. Otherwise it is probably fine. Name it for its job, put it in the
   folder that already holds that kind of thing, and do not create a new
   top-level directory to hold one file.

**Never create:** a second `content/`, a second sprite pack
(`art/sprites/`, `placeholder_sprites/`, `assets/dc/`), a second baker,
a per-port data file, a new `backups/` snapshot, or a second copy of a
port that already exists.

---

## Working at the same time as another agent

Claim a **lane** and stay in it. Two agents in different lanes cannot
conflict.

| Lane | Owns | Never touches |
|---|---|---|
| Content | `content/*.json` | engines, `.inc`, art |
| Web engine | `src/game/`, `src/components/` | `content/`, `main.c` |
| DC runtime | `ports/dreamcast/src/` (hand-written files) | `content/`, `src/game/` |
| Art | `public/sprites/` | everything else |
| Toolchain | `tools/`, `ports/dreamcast/tools/` | `content/`, engines |

Rules for sharing a lane:

- Two agents in **Content** at once: split by file (`species.json` vs
  `dialogue.json`). If you must share a file, split by top-level key
  (`world.json` → `warps` vs `trainers`).
- **Never reformat, re-sort, or re-indent a file you do not own
  entirely.** It turns a three-line diff into a whole-file conflict and
  buries the other agent's change.
- A feature that spans lanes is **sequential, not parallel**. §5 is the
  order.
- **Read before you reconcile.** If another agent pushed while you
  worked, read what they did first. A refactor that moved your data into
  a different file is not a conflict to defeat; it is the new location
  to move your change into.

---

## §5 — Getting a feature into both ports

Order matters. Data, then rules, then tools, then engines.

1. **Data** → `content/*.json`.
2. **Rules and constants** → `content/logic.json`. Anything both ports
   must agree on. Not a magic number in two engines.
3. **Baker** → `tools/bake_content.py`, so C can see the new field.
4. **Web engine** → `src/game/`. Read it. Do not re-declare it.
5. **DC runtime** → `ports/dreamcast/src/main.c`. Read the baked value.
   Do not re-declare it.

Stop after 4 and the Dreamcast silently lacks the feature. Stop after 5
and the web does. **A feature is done when both engines read the same
shared value** — not when one of them works.

What legitimately differs per port: rendering, input, audio, menu
layout. That is presentation. Numbers, names, text and rules are not.

### Worked example — Crystal Natures

A typing system currently exists only in the BeelzFight `main.c`, which
is exactly the wrong place. It lands here as:

| Step | Change |
|---|---|
| 1 | `species.json`: a `nature` field on each of the 20 entries |
| 2 | `logic.json`: the ring order, `strongMul`, `weakMul`, and the "beats the next two around the ring" rule, as data |
| 3 | `bake_content.py`: emit the nature and the ring |
| 4 | `engine.ts`: multiply damage by the ring lookup |
| 5 | `main.c`: keep the lookup helpers, but read the ring and multipliers from the baked values rather than `#define`s |

The CryDex screen and the Dreamcast menu chrome are presentation and
may differ. The natures, the multipliers and the species assignments
may not.

---

## §6 — Generated files

Build output. Never authored, never hand-edited, never hand-merged:

```
ports/dreamcast/src/content_*.inc
ports/dreamcast/src/sprites.h
*.elf
*.cdi          (except a deliberate release in public/rom/)
```

On a conflict in one of these, discard both sides and rebuild:

```
python3 tools/bake_content.py --content content --out ports/dreamcast/src
python3 ports/dreamcast/tools/gen_sprites.py
```

These should be gitignored. Until they are, do not commit a rebuild of
one unless that rebuild is the point of your change.

---

## §7 — Conflicts

- Merge or rebase **before** you start, not after you finish.
- **Never force-push a shared branch.** Merge; a merge commit keeps
  every other agent's checkout valid.
- Generated file → rebuild, never hand-merge.
- JSON → resolve key by key. Whole-file conflict means somebody
  reformatted; take the un-reformatted side and re-apply the real
  change.
- Engine file → the lane owner resolves it.

---

## §8 — The check

```
python3 tools/check_shared.py
```

Run it before you finish. It fails if a shared thing got duplicated, if
a second content pack or sprite pack appeared, if a generated file got
committed, or if `species.json` and the baker's species list disagree.

A failure is not advisory. Fix it in the same turn, or say clearly in
your reply that you did not and why.

---

## §9 — Known violations

Real, as of this file. Fixing them is ordinary work, not a special
project. `check_shared.py` reports the live list.

1. **`ports/dreamcast/tools/bake_content.py`** is a second baker. Keep
   `tools/bake_content.py`, delete this one, repoint the Makefile.
2. **`ports/dreamcast/src/content_*.inc`** are committed build output.
   Gitignore and drop from the index.
3. **`BeelzFight/crymon-dreamcast/`** is a second copy of the port and
   the source of the content and `main.c` drift. Retire it in favour of
   `ports/dreamcast/`. *(Cross-repo and destructive — the owner decides
   whether it is deleted or reduced to a pointer.)*
4. **Crystal Natures, the CryDex, bench XP and the Reach endgame** exist
   only in the BeelzFight `main.c`. They need porting into `content/` +
   the baker per §5 so the web port has them too.
5. **`SPECIES_ORDER`** in the baker is a hand-kept copy of the species
   list. Derive it from `species.json`.
6. **`art/sprites/`** in BeelzFight is a third sprite pack. Fold into
   `public/sprites/` and delete the fallback path in `gen_sprites.py`.

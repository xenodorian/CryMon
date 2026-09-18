#!/usr/bin/env python3
"""Guard the single-source-of-truth rules in docs/AGENT_COLLABORATION.md.

Run before you finish a turn:

    python3 tools/check_shared.py

Exit 0 = clean. Exit 1 = you (or another agent) duplicated something
shared, or a generated file got committed. Every failure names the file
and the rule it broke.

This exists because the rules were already written down and still did not
hold: content/ ended up with two copies that drifted, and bake_content.py
ended up with three. Prose does not stop that. A check that fails does.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Exactly one of each of these may exist. Value = the canonical path.
SINGLETONS = {
    "bake_content.py": "tools/bake_content.py",
    "gen_sprites.py": "ports/dreamcast/tools/gen_sprites.py",
}

# A directory holding this file IS a content pack. Only one may exist.
CONTENT_MARKER = "species.json"
CANONICAL_CONTENT = "content"

# Directories that are a second sprite pack by another name.
BANNED_ART_DIRS = [
    "art/sprites",
    "ports/dreamcast/art",
    "ports/dreamcast/tools/placeholder_sprites",
]
CANONICAL_ART = "public/sprites"

# Tracked files matching these are build output and must not be in git.
# public/rom/ is the one allowed home for a shipped release artifact.
GENERATED_GLOBS = [
    "*/content_*.inc",
    "content_*.inc",
    "*/sprites.h",
    "*.elf",
    "*.cdi",
]
RELEASE_DIRS = ("public/rom/",)

# Not part of the live tree: backups/ is reference-only by policy, and
# .vercel/ is the deploy tool's own output directory. Flagging either on
# every run would only teach agents to ignore this script.
EXCLUDED_PREFIXES = ("backups/", ".vercel/")

failures: list[str] = []
notes: list[str] = []


def fail(rule: str, detail: str) -> None:
    failures.append(f"[{rule}] {detail}")


def tracked_files() -> list[str]:
    try:
        out = subprocess.run(
            ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        notes.append("not a git checkout; skipped the committed-artifact check")
        return []
    return [
        p
        for p in out.splitlines()
        if p and not p.startswith(EXCLUDED_PREFIXES)
    ]


def check_singletons(files: list[str]) -> None:
    for name, canonical in SINGLETONS.items():
        hits = sorted(p for p in files if Path(p).name == name)
        if not hits:
            notes.append(f"{name}: not found (expected at {canonical})")
            continue
        if len(hits) > 1:
            extra = [h for h in hits if h != canonical]
            fail(
                "one-copy",
                f"{len(hits)} copies of {name}: {', '.join(hits)} "
                f"-- keep {canonical}, delete {', '.join(extra) or 'the rest'}",
            )


def check_content_packs(files: list[str]) -> None:
    packs = sorted({str(Path(p).parent) for p in files if Path(p).name == CONTENT_MARKER})
    if not packs:
        notes.append(f"no {CONTENT_MARKER} found at all")
        return
    if len(packs) > 1 or packs[0] != CANONICAL_CONTENT:
        fail(
            "one-content",
            f"content pack(s) at {', '.join(packs)} -- the only one is "
            f"{CANONICAL_CONTENT}/",
        )


def check_art(files: list[str]) -> None:
    for banned in BANNED_ART_DIRS:
        hits = [p for p in files if p.startswith(banned + "/")]
        if hits:
            fail(
                "one-art",
                f"{len(hits)} file(s) under {banned}/ -- art lives in "
                f"{CANONICAL_ART}/ only",
            )


def check_generated(files: list[str]) -> None:
    import fnmatch

    for pattern in GENERATED_GLOBS:
        for p in files:
            if not fnmatch.fnmatch(p, pattern):
                continue
            if p.startswith(RELEASE_DIRS):
                continue
            fail(
                "generated",
                f"{p} is build output and is committed -- gitignore it and "
                f"rebuild instead of merging it",
            )


def check_species_order() -> None:
    """The baker keeps its own hand-written species list. If it disagrees
    with species.json, one port silently ships a different roster."""
    baker = ROOT / SINGLETONS["bake_content.py"]
    pack = ROOT / CANONICAL_CONTENT / CONTENT_MARKER
    if not baker.exists() or not pack.exists():
        return
    text = baker.read_text()
    if "SPECIES_ORDER" not in text:
        return
    try:
        start = text.index("SPECIES_ORDER")
        block = text[start : text.index("]", start) + 1]
        ids_in_baker = [
            tok.strip().strip("\"'")
            for tok in block[block.index("[") + 1 : -1].split(",")
            if tok.strip().strip("\"'")
        ]
        ids_in_pack = list(json.loads(pack.read_text()).keys())
    except (ValueError, json.JSONDecodeError) as exc:
        notes.append(f"could not compare SPECIES_ORDER: {exc}")
        return

    missing = [i for i in ids_in_pack if i not in ids_in_baker]
    extra = [i for i in ids_in_baker if i not in ids_in_pack]
    if missing:
        fail("drift", f"species.json has ids the baker will not emit: {', '.join(missing)}")
    if extra:
        fail("drift", f"baker lists ids that are not in species.json: {', '.join(extra)}")


def main() -> int:
    files = tracked_files()
    check_singletons(files)
    check_content_packs(files)
    check_art(files)
    check_generated(files)
    check_species_order()

    for n in notes:
        print(f"note: {n}")

    if not failures:
        print("check_shared: OK -- one copy of everything shared.")
        return 0

    print(f"\ncheck_shared: {len(failures)} problem(s)\n")
    for f in failures:
        print(f"  {f}")
    print("\nRules: docs/AGENT_COLLABORATION.md")
    return 1


if __name__ == "__main__":
    sys.exit(main())

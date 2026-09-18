#!/usr/bin/env python3
"""Canonical sprite tree: public/sprites/. Nothing else is art."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "public" / "sprites"

# Live directories that must not exist. backups/ is frozen and skipped.
_SKIP_TOP = {
    ".git",
    ".grok",
    ".vercel",
    "backups",
    "node_modules",
    "artifacts",
    "attachments",
    "screenshots",
    "tmp",
}


def is_canon(path: Path) -> bool:
    try:
        path.resolve().relative_to(CANON.resolve())
        return True
    except ValueError:
        return False


def assert_write(path: Path) -> Path:
    """Refuse to write a sprite file anywhere but public/sprites/."""
    path = Path(path)
    if not is_canon(path):
        raise SystemExit(f"refusing to write {path}; sprites only under {CANON}")
    return path


def stray_sprite_dirs() -> list[str]:
    """Any directory named sprites/ that is not public/sprites/."""
    hits: list[str] = []
    for dirpath, dirnames, _ in os.walk(ROOT):
        top = Path(dirpath).relative_to(ROOT).parts
        if top and top[0] in _SKIP_TOP:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in _SKIP_TOP and d != "placeholder_sprites"]
        if os.path.basename(dirpath) == "sprites":
            rel = os.path.relpath(dirpath, ROOT).replace("\\", "/")
            if rel != "public/sprites":
                hits.append(rel)
    return sorted(hits)

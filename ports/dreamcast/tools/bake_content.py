#!/usr/bin/env python3
"""Thin wrapper. Canonical baker is tools/bake_content.py at repo root."""
import runpy
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[3]
sys.argv[0] = str(root / "tools" / "bake_content.py")
runpy.run_path(str(root / "tools" / "bake_content.py"), run_name="__main__")

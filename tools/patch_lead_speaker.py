#!/usr/bin/env python3
"""Add lead/system speaker names; extend SpeakerId; bake DC content."""
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

dp = ROOT / "content" / "dialogue.json"
d = json.loads(dp.read_text())
sp = d.setdefault("speakers", {})
sp["lead"] = "Lieutenant Lead"
sp["system"] = ""  # narrator / no name plate
dp.write_text(json.dumps(d, indent=2) + "\n")
print("speakers lead/system")

tp = ROOT / "src" / "game" / "types.ts"
tt = tp.read_text()
chunk_start = tt.find("SpeakerId")
chunk = tt[chunk_start : chunk_start + 900] if chunk_start >= 0 else ""
if '| "lead"' not in chunk:
    if '| "none"' in tt:
        tt = tt.replace('| "none"', '| "lead" | "system" | "none"', 1)
        tp.write_text(tt)
        print("SpeakerId +lead +system")
elif '| "system"' not in chunk and '"system"' not in chunk:
    if '| "none"' in tt:
        tt = tt.replace('| "none"', '| "system" | "none"', 1)
        tp.write_text(tt)
        print("SpeakerId +system")
else:
    print("SpeakerId ok")

bake = ROOT / "tools" / "bake_content.py"
if bake.exists():
    subprocess.check_call([sys.executable, str(bake)], cwd=str(ROOT))
    print("bake ok")

print("done")

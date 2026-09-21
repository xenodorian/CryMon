#!/usr/bin/env python3
"""Add lead/system speaker names; bake SPEAKER table; bake DC content."""
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

dp = ROOT / "content" / "dialogue.json"
d = json.loads(dp.read_text())
sp = d.setdefault("speakers", {})
sp["lead"] = "Lieutenant Lead"
sp["system"] = ""
dp.write_text(json.dumps(d, indent=2) + "\n")
print("dialogue speakers lead/system")

tp = ROOT / "src" / "game" / "types.ts"
tt = tp.read_text()
chunk = tt[tt.find("SpeakerId") : tt.find("SpeakerId") + 900]
if '| "lead"' not in chunk:
    tt = tt.replace('| "none"', '| "lead" | "system" | "none"', 1)
    tp.write_text(tt)
    print("SpeakerId")
elif '| "system"' not in chunk:
    tt = tt.replace('| "none"', '| "system" | "none"', 1)
    tp.write_text(tt)

bp = ROOT / "tools" / "bake_content.py"
bt = bp.read_text()
if '"lead": 35' not in bt:
    old = '    "dray": 34,\n}'
    new = '    "dray": 34,\n    "lead": 35,\n    "system": 36,\n}'
    if old not in bt:
        raise SystemExit("SPEAKER anchor missing")
    bp.write_text(bt.replace(old, new, 1))
    print("bake SPEAKER +lead +system")

subprocess.check_call([sys.executable, str(ROOT / "tools" / "bake_content.py")], cwd=str(ROOT))
print("bake ok")

#!/usr/bin/env python3
"""Add lead -> Lieutenant Lead speaker map; extend SpeakerId; bake DC content."""
from pathlib import Path
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

# dialogue.json speakers
dp = ROOT / "content" / "dialogue.json"
d = json.loads(dp.read_text())
sp = d.setdefault("speakers", {})
sp["lead"] = "Lieutenant Lead"
dp.write_text(json.dumps(d, indent=2) + "\n")
print("speakers.lead =", sp["lead"])

# types.ts SpeakerId
tp = ROOT / "src" / "game" / "types.ts"
tt = tp.read_text()
if '| "lead"' not in tt and '"lead"' not in tt[tt.find("SpeakerId") : tt.find("SpeakerId") + 800]:
    # insert before | "none"
    if '| "none"' in tt:
        tt = tt.replace('| "none"', '| "lead" | "none"', 1)
        tp.write_text(tt)
        print("SpeakerId +lead")
    else:
        print("WARN no none in SpeakerId")
else:
    print("SpeakerId already has lead")

# bake
bake = ROOT / "tools" / "bake_content.py"
if bake.exists():
    try:
        subprocess.check_call([sys.executable, str(bake)], cwd=str(ROOT))
        print("bake ok")
    except Exception as e:
        print("bake failed", e)
else:
    print("no bake script")

print("done")

#!/usr/bin/env python3
import json
from pathlib import Path

p = Path("content/audio.json")
d = json.loads(p.read_text())
# Correct pattern format is NOTE:frames (see faint), vol is 0-15 int
d["sfx"]["scream"] = {
    "tracks": [
        {
            "wave": "pulse",
            "duty": 1,
            "vol": 12,
            "pattern": "A4:4 F4:4 D4:4 B3:4 G3:6 E3:6 C3:8 A2:10",
        },
        {
            "wave": "noise",
            "duty": 0,
            "vol": 10,
            "pattern": "n:6 n:6 n:8 n:10 r:4",
        },
    ]
}
p.write_text(json.dumps(d, indent=2) + "\n")
print("scream pattern fixed")

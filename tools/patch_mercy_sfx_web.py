#!/usr/bin/env python3
"""Web: add scream SFX and use it on Execute."""
from pathlib import Path
import json

# --- content/audio.json ---
audio_path = Path("content/audio.json")
audio = json.loads(audio_path.read_text())
sfx = audio.setdefault("sfx", {})
if "scream" not in sfx:
    # Harsh descending noise based on faint, louder / longer
    faint = sfx.get("faint", {"tracks": []})
    sfx["scream"] = {
        "tracks": [
            {
                "wave": "saw",
                "duty": 0.5,
                "vol": 0.55,
                "pattern": "8:A3 8:F3 8:D3 8:B2 8:G2 8:E2 8:C2 8:A1",
            },
            {
                "wave": "noise",
                "duty": 0.5,
                "vol": 0.4,
                "pattern": "8:C4 8:C4 8:C3 8:C3 8:C2 8:C2 8:C1 8:C1",
            },
        ]
    }
    audio_path.write_text(json.dumps(audio, indent=2) + "\n")
    print("audio.json +scream")
else:
    print("audio.json scream already present")

# --- src/game/audio.ts ---
ap = Path("src/game/audio.ts")
at = ap.read_text()
if "scream()" not in at:
    at = at.replace(
        "\tfaint() {\n\t\tthis.playSfx(\"faint\");\n\t}",
        "\tfaint() {\n\t\tthis.playSfx(\"faint\");\n\t}\n\tscream() {\n\t\tthis.playSfx(\"scream\");\n\t}",
    )
    ap.write_text(at)
    print("audio.ts +scream()")
else:
    print("audio.ts already has scream")

# --- engine resolveMercy execute branch ---
ep = Path("src/game/engine.ts")
et = ep.read_text()
if "this.audio.scream()" not in et:
    et = et.replace(
        "this.markExecuted(this.mercyTrainer, this.mercySoldierId);\n\t\t\tthis.audio.faint();\n\t\t\tthis.startFade(\"execute\");",
        "this.markExecuted(this.mercyTrainer, this.mercySoldierId);\n\t\t\tthis.audio.scream();\n\t\t\tthis.startFade(\"execute\");",
    )
    ep.write_text(et)
    print("engine.ts scream on execute")
else:
    print("engine already screams")

print("web mercy sfx done")

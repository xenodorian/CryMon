#!/usr/bin/env python3
from pathlib import Path

e = Path("src/game/engine.ts").read_text()

# Add Tab/Q in updateWorld after talking/hud gates, before movement —
# look for unique sequence near start of free control.
needle = "\tif (this.input.start()) {\n\t\t\tthis.openParty();"
# alternate patterns used in crymon
alts = [
    needle,
    "\tif (this.input.start()) {\n\t\tthis.openParty();",
    "if (this.input.start()) {\n\t\t\tthis.openParty(\"list\");",
    "if (this.input.start()) {\n\t\t\tthis.openParty();",
]

injected = False
for a in alts:
    if a in e and "pressed(\"Tab\")" not in e[e.find("updateWorld") : e.find("updateWorld") + 5000]:
        # only inject once at first start() in updateWorld region
        uw = e.find("\tupdateWorld(")
        region = e[uw : uw + 6000]
        if a.strip() in region or a in region:
            rep = (
                "if (this.input.pressed(\"Tab\") || this.input.pressed(\"KeyQ\")) {\n"
                "\t\t\tthis.swapParties();\n"
                "\t\t\treturn;\n"
                "\t\t}\n\t\t" + a.lstrip()
            )
            # replace within full file once carefully
            idx = e.find(a, uw)
            if idx > 0:
                e = e[:idx] + rep + e[idx + len(a) :]
                injected = True
                print("injected at start()")
                break

if not injected:
    # Fallback: after hudT block ends with talkLock = .2
    mark = "this.talkLock = .2;\n\t\t\t}\n\t\t\treturn;\n\t\t}"
    uw = e.find("\tupdateWorld(")
    idx = e.find(mark, uw)
    if idx > 0 and "swapParties()" not in e[uw : uw + 5000]:
        insert = mark + "\n\t\tif (this.input.pressed(\"Tab\") || this.input.pressed(\"KeyQ\")) {\n\t\t\tthis.swapParties();\n\t\t\treturn;\n\t\t}"
        e = e[:idx] + insert + e[idx + len(mark) :]
        print("injected after hud")
        injected = True

if not injected:
    print("WARN: could not inject Tab in updateWorld")
else:
    Path("src/game/engine.ts").write_text(e)

# Also ensure GAME_KEYS includes Tab (already does in input.ts)
inp = Path("src/game/input.ts").read_text()
if '"Tab"' not in inp:
    print("WARN: Tab not in GAME_KEYS")
else:
    print("Tab in GAME_KEYS ok")

print("done")

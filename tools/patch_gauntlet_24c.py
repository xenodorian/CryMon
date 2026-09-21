#!/usr/bin/env python3
from pathlib import Path

ep = Path("src/game/engine.ts")
et = ep.read_text()

old = '''else if (who === "commanderFinal") this.beatCommander = true;
				this.marks += kit?.marks ?? 12;
				// Win talk deferred; mercy menu first (not mason/shinigami).
				this.audio.ok();
				this.openMercy(b);
				return;'''

new = '''else if (who === "commanderFinal") this.beatCommander = true;
				else if (who === "heavenfallGrave") {
					this.beatHeavenfall = true;
					this.titleSlayer = true;
					this.titleTamer = false;
					this.marks += kit?.marks ?? 12;
					this.audio.ok();
					this.note("The world will know you as Heaven Slayer.");
					this.say(TALK.gauntletGraveWin || [{ speaker: "max", text: "Heavenfall falls." }], "creditsFinal");
					return;
				}
				this.marks += kit?.marks ?? 12;
				// Win talk deferred; mercy menu first (not mason/shinigami).
				this.audio.ok();
				this.openMercy(b);
				return;'''

if "who === \"heavenfallGrave\"" in et and "creditsFinal" in et[et.find("heavenfallGrave") : et.find("heavenfallGrave") + 500]:
    print("already wired")
elif old in et:
    et = et.replace(old, new, 1)
    print("win+credits")
else:
    # softer
    a = 'else if (who === "commanderFinal") this.beatCommander = true;'
    if a in et and 'who === "heavenfallGrave"' not in et:
        et = et.replace(
            a,
            a
            + '\n\t\t\t\telse if (who === "heavenfallGrave") {\n'
            + '\t\t\t\t\tthis.beatHeavenfall = true; this.titleSlayer = true; this.titleTamer = false;\n'
            + '\t\t\t\t\tthis.marks += kit?.marks ?? 12; this.audio.ok();\n'
            + '\t\t\t\t\tthis.note("The world will know you as Heaven Slayer.");\n'
            + '\t\t\t\t\tthis.say(TALK.gauntletGraveWin || [{ speaker: "max", text: "Heavenfall falls." }], "creditsFinal");\n'
            + '\t\t\t\t\treturn;\n\t\t\t\t}',
            1,
        )
        print("win soft")
    else:
        print("WARN")

# ensure playerDisplayName has Tamer
if 'return "Heaven Tamer"' not in et:
    et = et.replace(
        "if (this.revivedFather) return LOGIC.reputation?.kindName || \"Max The Kind\";\n\t\treturn SPEAKER_NAME.max || \"Max\";",
        "if (this.titleTamer) return \"Heaven Tamer\";\n\t\tif (this.titleSlayer) return \"Heaven Slayer\";\n\t\tif (this.revivedFather) return LOGIC.reputation?.kindName || \"Max The Kind\";\n\t\treturn SPEAKER_NAME.max || \"Max\";",
        1,
    )
    print("display names")

ep.write_text(et)
print("ok")

# Dialogue audit: unaudited regions (2026-09-27)

Scope: the 20 regions no earlier audit touched (`96ef97c`, `b63fb27`, `486007c`,
`1ee9ec9`, `d91e39e`): house, the ten Sephirot cities, Keter, the Ruins Inn, the
Haunted Hall, the Grave and the Path maps. Rule applied (CURRENT_WORK queue 3):
NPCs act from their story role and current state, and do not re-explain what the
listener already knows.

**Status: proposals only. Nothing in `content/` has been changed.** Each item
needs the user's OK before it is applied (then re-bake and `check_sync --strict`).

Every finding cites the dialogue key or the `world.json` script step it comes
from. "Unverified" marks an inference not yet confirmed in play.

## A. State bugs (a line can show at the wrong time)

A1. **Hollis, Ruins Inn** (`hollisRest`, one unconditional step). The last line,
"Free for you. The whole Ruins knows who beat the soldiers at the gate.", shows
on every visit. The Ruins guards (`ruinsKeeper`, `ruinsWarden`) are optional and
do not gate the inn (the `ruins` to `ruinsinn` warp has no `need`), so Max can
hear this before fighting them. Proposal: split into two steps.
- `if beatRuinsWarden` (or both guard flags): keep the current line.
- default: "Welcome to the Ruins Inn. Only inn west of CryTown, so don't
  complain about the beds." / narration / "Rest up. Pay me back by keeping the
  soldiers off my road."
- Unverified: whether the guards stand at the Ruins gate. If they do not, the
  "at the gate" wording should change too.

A2. **Sera, Netzach** (`seraAfter`, step `if gaveLocket`). "Beat Stroud and his
dead can rest. Mine too." still plays after Stroud is beaten
(`medalPowMedal`) and after the war ends (`leg3Ended`). Proposal: add
`if medalPowMedal` step before it: "Stroud's dead were let go. I felt it. He's
resting now."

A3. **Sister Iona, Chokmah** (`ionaHome`). "When Nero falls, the dead can rest.
Pray it's soon." plays after Nero falls. Proposal: add `if leg3Ended` step:
"The dead are going home. I hear them leaving, one by one."

A4. **Lune, Gevurah** (`luneAfter`). "The palace door in Keter only opens for
Golden Shackles. The last General carries them." plays after Max has the
Shackles (`hasGoldenShackles`) and after the war. Proposal: add
`if hasGoldenShackles` step: "Golden Shackles. Then my old road to Keter is
yours. Walk it well."

## B. Redundant exposition

B1. **Father, house** (`father`). Max tells her own father what a CryMon is:
"So I'm taking your CryMon. Your Crystal Monster. / It sleeps inside the crystal
until someone cracks it open." The father owns it. The information is there for
the player, so keep it but move it out of the speech to him. Proposal:
- max: "So I'm taking your CryMon."
- none: "A Crystal Monster sleeps inside the crystal until someone cracks it open."

B2. **The nine city hint NPCs** (`hintMalkuth` .. `hintChokmah`). All nine
end with the same line, "Bring Shackles. An arrest is better for your name than
an execution.", and Marn already gives this rule in Malkuth (`marnFirst`).
By the fourth city Max has arrested or killed three Generals, and strangers
still explain it. Proposal: keep the line only in `hintMalkuth`; in the other
eight, replace it with one line of local color tied to that General (the
`citizen*Before` lines already set each city's mood: Ashgrove's rules, Stroud's
cells, Kessler's fires, Crane's birds, Morrow's water, Blackwood's garrison,
Sorrel's guard). Draft lines can follow once the direction is approved.

B3. **Hint NPC "after" lines** (`hint*After`). Each tells Max which medal she now
holds ("General Harrow is beaten. You have the Bronze Star."). Max just took it
herself. Proposal: drop the "You have the X" sentence and keep the pointer to
the next city, e.g. "Harrow's gone. Yesod's next. Ashgrove holds it."

B4. **Palace-door rule said three times** (`hintKeter`, `luneAfter`,
`marnFirst`/`marnGold`). Three NPCs explain that Golden Shackles open Nero's
palace. Proposal: keep Marn and the Keter elder, and change Lune per A4.

## C. Checked and fine

- Max as "her" (`shelf` narration, `quillVesk`, `marnPost` "a girl from
  CryTown") is consistent across these regions.
- "Twelve years" (Marn, Hod, Keter elder) is consistent.
- Bounty quests pay what they say: `dunnDead` and `holtDead` pay 20 and 30
  Marks, half of `dunnThanks` (40) and `holtThanks` (60).
- City order in the hint chain matches (Malkuth, Yesod, Netzach, Hod, Tiferet,
  Chesed, Gevurah, Binah, Chokmah, Keter): every "door won't open until" medal
  is the one the previous city's "next base is" line names.
- Rescue quests (Pip, Tilly, Iona) close their loops: found step, thanks step,
  home NPC appears (`showIf`).
- Hod's `citizenHodBefore` "..." is intentional: `citizenHodAfter` says "We can
  talk again."

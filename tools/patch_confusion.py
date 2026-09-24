#!/usr/bin/env python3
"""Confusion: 1-4 turn duration (from STATUS_EFFECTS.confused) + Wait skips self-hit roll."""
from pathlib import Path

engine = Path("src/game/engine.ts")
data = Path("src/game/data.ts")
t = engine.read_text()
d = data.read_text()

# 1) pickAttack: Wait before confusion roll so Wait never self-hits
old_pick = '''\t\t// Paralysis/confusion intercept before the chosen move even runs --\n\t\t// the turn-countdown/HP-tick itself happens once per round in\n\t\t// resolve_guard, not here, so this only checks and bypasses.\n\t\tif (b.player.status === "paralyzed") {\n\t\t\tb.pendingDmg = 0;\n\t\t\tb.pendingLabel = `${b.player.name} is paralyzed and can't move.`;\n\t\t\tb.phase = "resolve_hit";\n\t\t\tthis.audio.miss();\n\t\t\treturn;\n\t\t}\n\t\tconst confused = this.confusionOutcome(b.player, true);\n\t\tif (confused && confused.kind !== "normal") {\n\t\t\tb.pendingDmg = 0;\n\t\t\tif (confused.kind === "none") {\n\t\t\t\tb.pendingLabel = `${b.player.name} is too confused to act.`;\n\t\t\t} else if (confused.kind === "self") {\n\t\t\t\tconst dmg = Math.max(0, Math.min(b.player.hp - 1, confused.dmg));\n\t\t\t\tb.player.hp = Math.max(1, b.player.hp - dmg);\n\t\t\t\tb.pendingLabel = `${b.player.name} is confused and hits itself!`;\n\t\t\t} else {\n\t\t\t\tconst target = this.party[confused.targetIdx];\n\t\t\t\tif (target) target.hp = Math.max(0, target.hp - confused.dmg);\n\t\t\t\tb.pendingLabel = `${b.player.name} is confused and hits ${target?.name ?? "an ally"}!`;\n\t\t\t}\n\t\t\tb.phase = "resolve_hit";\n\t\t\tthis.audio.miss();\n\t\t\treturn;\n\t\t}\n\t\tif (mv.kind === "wait") {\n\t\t\tb.msg = [`${b.player.name} holds.`];\n\t\t\tb.msgI = 0;\n\t\t\tb.phase = "msg";\n\t\t\tb.afterMsg = "guard";\n\t\t\tthis.audio.ui();\n\t\t\treturn;\n\t\t}'''

new_pick = '''\t\t// Paralysis intercept before the chosen move. Confusion only rolls\n\t\t// on a real attack (not Wait) so holding safely burns a confusion turn.\n\t\t// Turn-countdown itself happens once per round in resolve_guard.\n\t\tif (b.player.status === "paralyzed") {\n\t\t\tb.pendingDmg = 0;\n\t\t\tb.pendingLabel = `${b.player.name} is paralyzed and can't move.`;\n\t\t\tb.phase = "resolve_hit";\n\t\t\tthis.audio.miss();\n\t\t\treturn;\n\t\t}\n\t\tif (mv.kind === "wait") {\n\t\t\tb.msg = [`${b.player.name} holds.`];\n\t\t\tb.msgI = 0;\n\t\t\tb.phase = "msg";\n\t\t\tb.afterMsg = "guard";\n\t\t\tthis.audio.ui();\n\t\t\treturn;\n\t\t}\n\t\tconst confused = this.confusionOutcome(b.player, true);\n\t\tif (confused && confused.kind !== "normal") {\n\t\t\tb.pendingDmg = 0;\n\t\t\tif (confused.kind === "none") {\n\t\t\t\tb.pendingLabel = `${b.player.name} is too confused to act.`;\n\t\t\t} else if (confused.kind === "self") {\n\t\t\t\tconst dmg = Math.max(0, Math.min(b.player.hp - 1, confused.dmg));\n\t\t\t\tb.player.hp = Math.max(1, b.player.hp - dmg);\n\t\t\t\tb.pendingLabel = `${b.player.name} is confused and hits itself!`;\n\t\t\t} else {\n\t\t\t\tconst target = this.party[confused.targetIdx];\n\t\t\t\tif (target) target.hp = Math.max(0, target.hp - confused.dmg);\n\t\t\t\tb.pendingLabel = `${b.player.name} is confused and hits ${target?.name ?? "an ally"}!`;\n\t\t\t}\n\t\t\tb.phase = "resolve_hit";\n\t\t\tthis.audio.miss();\n\t\t\treturn;\n\t\t}'''

if old_pick not in t:
    if "holding safely burns a confusion turn" in t:
        print("pickAttack already patched")
    else:
        raise SystemExit("pickAttack block not found")
else:
    t = t.replace(old_pick, new_pick, 1)
    print("pickAttack patched")

# 2) inflictStatus: roll 1-4 turns for confused
old_inf = '''\t\tif (status === "burned") {\n\t\t\tconst e = STATUS_EFFECTS.burned;\n\t\t\tm.statusTurns = randI(e.turnsMin, e.turnsMax);\n\t\t\tm.poisonStack = 0;\n\t\t} else if (status === "paralyzed") {\n\t\t\tconst e = STATUS_EFFECTS.paralyzed;\n\t\t\tm.statusTurns = randI(e.turnsMin, e.turnsMax);\n\t\t\tm.poisonStack = 0;\n\t\t} else if (status === "poisoned") {\n\t\t\tm.statusTurns = 0;\n\t\t\tm.poisonStack = 0;\n\t\t} else {\n\t\t\tm.statusTurns = 0;\n\t\t\tm.poisonStack = 0;\n\t\t}'''

new_inf = '''\t\tif (status === "burned") {\n\t\t\tconst e = STATUS_EFFECTS.burned;\n\t\t\tm.statusTurns = randI(e.turnsMin, e.turnsMax);\n\t\t\tm.poisonStack = 0;\n\t\t} else if (status === "paralyzed") {\n\t\t\tconst e = STATUS_EFFECTS.paralyzed;\n\t\t\tm.statusTurns = randI(e.turnsMin, e.turnsMax);\n\t\t\tm.poisonStack = 0;\n\t\t} else if (status === "confused") {\n\t\t\tconst e = STATUS_EFFECTS.confused;\n\t\t\tm.statusTurns = randI(e.turnsMin, e.turnsMax);\n\t\t\tm.poisonStack = 0;\n\t\t} else if (status === "poisoned") {\n\t\t\tm.statusTurns = 0;\n\t\t\tm.poisonStack = 0;\n\t\t} else {\n\t\t\tm.statusTurns = 0;\n\t\t\tm.poisonStack = 0;\n\t\t}'''

if old_inf not in t:
    if 'status === "confused"' in t and "STATUS_EFFECTS.confused" in t:
        print("inflictStatus already patched")
    else:
        raise SystemExit("inflictStatus block not found")
else:
    t = t.replace(old_inf, new_inf, 1)
    print("inflictStatus patched")

# 3) tickStatus: countdown confused (no HP drain)
old_tick = '''\t\tif (m.status === "paralyzed") {\n\t\t\tm.statusTurns = (m.statusTurns ?? 1) - 1;\n\t\t\tif (m.statusTurns <= 0) this.clearStatus(m);\n\t\t\treturn "";\n\t\t}\n\t\treturn "";\n\t}'''

new_tick = '''\t\tif (m.status === "paralyzed") {\n\t\t\tm.statusTurns = (m.statusTurns ?? 1) - 1;\n\t\t\tif (m.statusTurns <= 0) this.clearStatus(m);\n\t\t\treturn "";\n\t\t}\n\t\tif (m.status === "confused") {\n\t\t\tm.statusTurns = (m.statusTurns ?? 1) - 1;\n\t\t\tif (m.statusTurns <= 0) {\n\t\t\t\tthis.clearStatus(m);\n\t\t\t\treturn " snapped out of confusion";\n\t\t\t}\n\t\t\treturn "";\n\t\t}\n\t\treturn "";\n\t}'''

if old_tick not in t:
    if 'm.status === "confused"' in t and "snapped out of confusion" in t:
        print("tickStatus already patched")
    else:
        raise SystemExit("tickStatus block not found")
else:
    t = t.replace(old_tick, new_tick, 1)
    print("tickStatus patched")

engine.write_text(t)

# 4) data.ts: type + fallback for confused
old_type = '''export type StatusEffectsConfig = {
  burned: { hpPercent: number; turnsMin: number; turnsMax: number };
  poisoned: { startPercent: number; stepPercent: number };
  paralyzed: { turnsMin: number; turnsMax: number };
};
export const STATUS_EFFECTS = ((logicJson as { statusEffects?: StatusEffectsConfig }).statusEffects || {
  burned: { hpPercent: 5, turnsMin: 2, turnsMax: 5 },
  poisoned: { startPercent: 1, stepPercent: 1 },
  paralyzed: { turnsMin: 1, turnsMax: 5 },
}) as StatusEffectsConfig;'''

new_type = '''export type StatusEffectsConfig = {
  burned: { hpPercent: number; turnsMin: number; turnsMax: number };
  poisoned: { startPercent: number; stepPercent: number };
  paralyzed: { turnsMin: number; turnsMax: number };
  confused: { turnsMin: number; turnsMax: number };
};
export const STATUS_EFFECTS = ((logicJson as { statusEffects?: StatusEffectsConfig }).statusEffects || {
  burned: { hpPercent: 5, turnsMin: 2, turnsMax: 5 },
  poisoned: { startPercent: 1, stepPercent: 1 },
  paralyzed: { turnsMin: 1, turnsMax: 5 },
  confused: { turnsMin: 1, turnsMax: 4 },
}) as StatusEffectsConfig;'''

if old_type not in d:
    if "confused: { turnsMin: number; turnsMax: number }" in d:
        print("data.ts already patched")
    else:
        raise SystemExit("data.ts STATUS_EFFECTS block not found")
else:
    d = d.replace(old_type, new_type, 1)
    data.write_text(d)
    print("data.ts patched")

print("OK")

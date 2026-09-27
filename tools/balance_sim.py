#!/usr/bin/env python3
"""Headless balance simulator: plays the trainer path with a modeled team.

    python3 tools/balance_sim.py              # report, current rules
    python3 tools/balance_sim.py --runs 60 --grind 6 --csv out.csv

It is a model, not a port of either engine. It reads the real content
(content/world.json trainers and encounters, content/species.json,
content/logic.json growth / natureTypes, world formulas) and mirrors the
battle rules that decide who wins:

  - Stats: foes are minted (species stat x (1 + (lv - mintBaseLevel) x
    mintGrowPerLevel), plus the crystal bonus). The player's monsters are
    minted when caught, then grow on level-up by the rule in
    growth.levelUpStats (see LEVEL_UP below), and evolve at evolveAt /
    evolveAt2 (re-minted at their level, as tryEvolve() does).
  - A round is: player attacks (special while it has PP, landing
    "connected" 1.5x, else basic), foe attacks (special 28% while it has
    PP, else basic), player guards with Block or Barrier, whichever of
    STR / SPC is higher (score = stat x U(guardRandMin, guardRandMax);
    a full block parries the hit back). Crystal matchups use strongMul /
    weakMul. XP: lead full, living bench benchXpShare.
  - Not modeled: status, stat stages, Hype Up, items in battle, dodge.
    Both sides have these, so they mostly cancel out.

The player's journey: Quillpup at Lv 3, then before each fight, every
wild area whose top level is at most the fight's lead level + 1 is
visited once. In each new area the player fights --grind wild battles
with the weakest member leading (spreading XP) and catches the area's
strongest species at the area's top level, keeping the best six.
Between fights the party is healed. On a loss the player grinds more
wild battles in the best area so far and retries (that count is the
"grind" column).

A fight is flagged WALL when the median first-try win rate is under 50%
or it needs more than 8 extra wild fights on average, and PUSHOVER when
the party loses under 10% of its HP. Optional side trainers are shown
but only main-path fights are flagged.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Trainer ids in story order. Side trainers (guilds, bounties, hermit,
# ghosts) are listed after the main fight they sit near, marked optional.
MAIN_PATH = [
    "mason", "calder", "sentry", "marshBog", "marshReed", "quarryDriller",
    "cathleen", "conscript", "enforcer", "forestRanger", "forestScout",
    "forestSoldiers1", "forestSoldiers2", "forestSoldiers3", "cross", "ruinsKeeper", "ruinsWarden", "shinigami",
    "quartz", "opal", "commanderFinal", "lieutenantLead",
    "baseMalkuthA", "baseMalkuthB", "generalHarrow",
    "baseYesodA", "baseYesodB", "generalAshgrove",
    "baseNetzachA", "baseNetzachB", "generalStroud",
    "baseHodA", "baseHodB", "generalVale",
    "baseTiferetA", "baseTiferetB", "generalKessler",
    "baseChesedA", "baseChesedB", "generalMorrow",
    "baseGevurahA", "baseGevurahB", "generalCrane",
    "baseBinahA", "baseBinahB", "generalBlackwood",
    "baseChokmahA", "baseChokmahB", "generalSorrel",
    "palaceGuardA", "palaceGuardB", "nero",
    "hollowRanger", "hollowShade", "hollowWarden", "calderPost",
]
OPTIONAL = {"heavenfallGrave", "heavenfallFinal", "ghostSoldierA", "ghostSoldierB", "ghostOriel",
            "sirAldous", "redMallory", "dameBrin", "silasFence", "mournerVesk", "captainRook",
            "oskOne", "oskTwo", "oskThree", "garrowOutlaw", "kaelDeserter"}


def load(p):
    return json.loads((ROOT / p).read_text())


class Rules:
    def __init__(self, level_up: str):
        world = load("content/world.json")
        logic = load("content/logic.json")
        sp = load("content/species.json")
        sp = sp.get("species", sp)
        self.species = sp if isinstance(sp, dict) else {s["id"]: s for s in sp}
        self.trainers = {}
        for tid, kit in world["trainers"].items():
            if isinstance(kit, list):  # forestSoldiers: three one-monster soldiers
                for i, sol in enumerate(kit):
                    self.trainers[f"{tid}{i + 1}"] = {"lead": [sol["species"], sol["level"]], "bench": []}
            else:
                self.trainers[tid] = kit
        self.encounters = world["encounters"]
        self.f = world["formulas"]
        self.growth = logic["growth"]
        self.combat = logic["combat"]
        self.initiative = self.combat.get("initiative")
        self.natures = {n["id"]: n for n in logic["natures"]}
        nt = logic["natureTypes"]
        self.strong, self.weak = nt["strongMul"], nt["weakMul"]
        self.beats = {(b["atk"], b["def"]) for b in nt["beats"]}
        self.evolved = {s.get("evolvesTo") for s in self.species.values() if s.get("evolvesTo")}
        self.level_up = level_up

    def nature(self, sid):
        return self.species[sid].get("nature", "quartz")

    def matchup(self, a, d):
        na, nd = self.nature(a), self.nature(d)
        if (na, nd) in self.beats:
            return self.strong
        if (nd, na) in self.beats:
            return self.weak
        return 1.0

    def grow(self, lv):
        return 1 + (lv - self.f["mintBaseLevel"]) * self.f["mintGrowPerLevel"]

    def mint(self, sid, lv):
        s, g, n = self.species[sid], self.grow(lv), self.natures.get(self.nature(sid), {})
        hp = round(s["maxHp"] * g)
        return {"sp": sid, "lv": lv, "xp": 0, "maxHp": hp, "hp": hp,
                "str": round(s["str"] * g) + n.get("str", 0),
                "agl": round(s["agl"] * g) + n.get("agl", 0),
                "spc": round(s["spc"] * g) + n.get("spc", 0)}

    def level_up_once(self, m):
        m["lv"] += 1
        if self.level_up == "flat":
            d = {"maxHp": self.f["levelHp"], "str": self.f["levelStat"],
                 "agl": self.f["levelStat"], "spc": self.f["levelStat"]}
        else:  # "curve": follow the mint curve of the species
            s = self.species[m["sp"]]
            g0, g1 = self.grow(m["lv"] - 1), self.grow(m["lv"])
            d = {k: max(1, round(s[k] * g1) - round(s[k] * g0)) for k in ("maxHp", "str", "agl", "spc")}
        for k, v in d.items():
            m[k] += v
        m["hp"] = min(m["maxHp"], m["hp"] + d["maxHp"])

    def gain_xp(self, m, foe_lv, share):
        m["xp"] += int((self.f["xpBase"] + foe_lv * self.f["xpPerLevel"]) * share)
        while m["xp"] >= m["lv"] * self.f["levelXpMul"] and m["lv"] < self.f["levelCap"]:
            m["xp"] -= m["lv"] * self.f["levelXpMul"]
            self.level_up_once(m)

    def evolve(self, m):
        to = self.species[m["sp"]].get("evolvesTo")
        at = self.growth["evolveAt2"] if m["sp"] in self.evolved else self.growth["evolveAt"]
        if not to or to not in self.species or m["lv"] < at:
            return m
        n = self.mint(to, m["lv"])
        n["xp"] = m["xp"]
        n["hp"] = max(1, round(n["maxHp"] * m["hp"] / max(1, m["maxHp"])))
        return n


def stat_of(r, m, which):
    return m["spc"] if which in ("spc", "mag") else m[which]


def attack(r, rng, a, d, special, conn):
    s = r.species[a["sp"]]
    if special:
        dmg = stat_of(r, a, s["specialStat"]) * s["specialPower"] * conn
    else:
        dmg = stat_of(r, a, s["basicStat"]) * s["basicPower"]
    return max(1, round(max(1, round(dmg)) * r.matchup(a["sp"], d["sp"])))


SKILL = {"good": 1.0, "avg": 0.6}
skill_best_guard = 1.0


def fight(r, rng, party, kit, conn=1.5):
    """One trainer fight. Mutates party hp/xp/levels. Returns (won, hp_lost_frac)."""
    foes = [r.mint(kit["lead"][0], kit["lead"][1])] + [r.mint(s, lv) for s, lv in kit.get("bench", [])]
    mul = kit.get("hpMul", 1)
    for f in foes:
        f["maxHp"] = f["hp"] = round(f["maxHp"] * mul)
    for f in foes:
        f["pp"] = r.species[f["sp"]].get("specialPp", 0) if f["lv"] >= r.growth["specialAt"] else 0
    for m in party:
        m["pp"] = r.species[m["sp"]].get("specialPp", 0) if m["lv"] >= r.growth["specialAt"] else 0
    start_hp = sum(m["hp"] for m in party)
    total_hp = sum(m["maxHp"] for m in party)
    order = sorted(range(len(party)), key=lambda i: -(party[i]["str"] + party[i]["spc"] + party[i]["maxHp"]))
    gmin, gmax = r.combat["guardRandMin"], r.combat["guardRandMax"]
    ini = r.initiative
    fi = 0

    def player_strike(li):
        """The lead hits. Returns 'won' when the last foe falls, 'ko' on a KO."""
        nonlocal fi
        p, foe = party[li], foes[fi]
        use_sp = p.get("pp", 0) > 0
        if use_sp:
            p["pp"] -= 1
        foe["hp"] -= attack(r, rng, p, foe, use_sp, conn)
        if foe["hp"] > 0:
            return None
        for i, m in enumerate(party):
            if m["hp"] > 0:
                r.gain_xp(m, foe["lv"], 1.0 if i == li else r.f["benchXpShare"])
                pp = m.get("pp", 0)
                party[i] = r.evolve(m)
                party[i].setdefault("pp", pp)
        fi += 1
        return "won" if fi >= len(foes) else "ko"

    def foe_strike(li):
        p, foe = party[li], foes[fi]
        f_sp = foe["pp"] > 0 and rng.random() < 0.28
        if f_sp:
            foe["pp"] -= 1
        dmg = attack(r, rng, foe, p, f_sp, 1.0)
        gstat = max(p["str"], p["spc"]) if rng.random() < skill_best_guard else rng.choice([p["str"], p["spc"], 0])
        guard = gstat * rng.uniform(gmin, gmax)  # 0 = a dodge that fails
        dmg = dmg - round(guard)
        if dmg <= 0:
            foe["hp"] += dmg  # parried: the foe eats its own blow
            if foe["hp"] <= 0:
                foe["hp"] = 1  # keep it simple: parries never finish a foe
        else:
            p["hp"] = max(0, p["hp"] - dmg)

    def lead():
        alive = [i for i in order if party[i]["hp"] > 0]
        return alive[0] if alive else None

    for rounds in range(400):
        li = lead()
        if li is None:
            return False, 1.0
        # Speed turn order (logic.json combat.initiative); ties go to the player.
        foe_first = ini is not None and (
            foes[fi]["agl"] * rng.uniform(ini["randMin"], ini["randMax"])
            > party[li]["agl"] * rng.uniform(ini["randMin"], ini["randMax"]))
        if foe_first:
            foe_strike(li)
            li = lead()  # a fallen lead's replacement still acts this round
            if li is None:
                return False, 1.0
        res = player_strike(li)
        if res == "won":
            lost = (start_hp - sum(m["hp"] for m in party)) / max(1, total_hp)
            return True, max(0.0, lost)
        if res is None and not foe_first:
            foe_strike(li)
    return False, 1.0


def heal(party):
    for m in party:
        m["hp"] = m["maxHp"]


def power(m):
    return m["maxHp"] + 2 * (m["str"] + m["spc"]) + m["agl"]


def journey(r, rng, grind, conn):
    party = [r.mint("quillpup", 3)]
    visited = set()
    areas = sorted(r.encounters, key=lambda e: e["levelMax"])
    out = []
    for tid in MAIN_PATH + sorted(OPTIONAL, key=lambda t: max([r.trainers[t]["lead"][1]] + [b[1] for b in r.trainers[t].get("bench", [])])):
        if tid not in r.trainers:
            continue
        kit = r.trainers[tid]
        top = max([kit["lead"][1]] + [b[1] for b in kit.get("bench", [])])
        best_area = None
        for i, e in enumerate(areas):
            if e["levelMax"] <= kit["lead"][1] + 1:
                best_area = e
                if i in visited:
                    continue
                visited.add(i)
                for _ in range(grind):
                    wild_battle(r, rng, party, e, conn)
                catch(r, rng, party, e)
        heal(party)
        extra = 0
        won, lost = fight(r, rng, [dict(m) for m in party], kit, conn)
        first = won
        while not won and extra < 60:
            heal(party)
            for _ in range(3):
                wild_battle(r, rng, party, best_area or areas[0], conn)
                extra += 1
            heal(party)
            won, lost = fight(r, rng, [dict(m) for m in party], kit, conn)
        heal(party)
        snap = [dict(m) for m in party]
        fight(r, rng, snap, kit, conn)  # XP from the win
        party[:] = [m for m in snap]
        heal(party)
        out.append((tid, top, first, extra, lost, max(m["lv"] for m in party),
                    round(statistics.mean(m["lv"] for m in party), 1)))
    return out


def wild_battle(r, rng, party, e, conn):
    lv = rng.randint(e["levelMin"], e["levelMax"])
    kit = {"lead": [rng.choice(e["pool"]), lv], "bench": []}
    heal(party)
    lead = min(range(len(party)), key=lambda i: party[i]["lv"])
    party.insert(0, party.pop(lead))
    fight(r, rng, party, kit, conn)
    heal(party)


POLICY = "best"


def catch(r, rng, party, e):
    if POLICY == "loyal" and len(party) >= 6:
        return
    best = max(set(e["pool"]), key=lambda s: power(r.mint(s, e["levelMax"])))
    m = r.mint(best, e["levelMax"])
    if len(party) < 6:
        party.append(m)
    else:
        weakest = min(range(len(party)), key=lambda i: power(party[i]))
        if power(m) > power(party[weakest]):
            party[weakest] = m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=40)
    ap.add_argument("--grind", type=int, default=6, help="wild battles per new area")
    ap.add_argument("--level-up", choices=["flat", "curve"], default=None)
    ap.add_argument("--conn", type=float, default=1.25, help="special multiplier the player lands")
    ap.add_argument("--skill", choices=list(SKILL), default="avg",
                    help="good: always guards with the best stat; avg: 60%% of the time, else a random guard")
    ap.add_argument("--policy", choices=["best", "loyal"], default="best",
                    help="best: swap in stronger catches; loyal: keep the first six forever")
    ap.add_argument("--boss-hp", type=float, help="try an hpMul on every General and Nero (overrides the data)")
    ap.add_argument("--no-initiative", action="store_true", help="old rule: the player always acts first")
    ap.add_argument("--csv")
    a = ap.parse_args()
    global skill_best_guard, POLICY
    skill_best_guard, POLICY = SKILL[a.skill], a.policy
    logic = load("content/logic.json")
    mode = a.level_up or logic["growth"].get("levelUpStats", "flat")
    r = Rules(mode)
    if a.no_initiative:
        r.initiative = None
    if a.boss_hp:
        for tid, kit in r.trainers.items():
            if tid.startswith("general") or tid == "nero":
                kit["hpMul"] = a.boss_hp
    runs = [journey(r, random.Random(seed), a.grind, a.conn) for seed in range(a.runs)]
    rows = []
    print(f"level-up rule: {mode}, runs {a.runs}, grind {a.grind}/area, specials x{a.conn}, skill {a.skill}, policy {a.policy}")
    print(f"{'trainer':18} {'top':>3} {'win1':>5} {'grind':>5} {'hpLost':>6} {'pMax':>4} {'pAvg':>5}  flag")
    for i, (tid, top, *_rest) in enumerate(runs[0]):
        col = [run[i] for run in runs]
        win1 = sum(1 for c in col if c[2]) / len(col)
        grind = statistics.mean(c[3] for c in col)
        lost = statistics.median(c[4] for c in col)
        pmax = statistics.median(c[5] for c in col)
        pavg = statistics.median(c[6] for c in col)
        flag = ""
        if tid not in OPTIONAL:
            if win1 < 0.5 or grind > 8:
                flag = "WALL"
            elif lost < 0.10:
                flag = "pushover"
        else:
            flag = "(optional)"
        rows.append((tid, top, win1, grind, lost, pmax, pavg, flag))
        print(f"{tid:18} {top:>3} {win1:>5.0%} {grind:>5.1f} {lost:>6.0%} {pmax:>4} {pavg:>5}  {flag}")
    walls = [r_[0] for r_ in rows if r_[7] == "WALL"]
    push = [r_[0] for r_ in rows if r_[7] == "pushover"]
    print(f"\nwalls ({len(walls)}): {', '.join(walls) or 'none'}")
    print(f"pushovers ({len(push)}): {', '.join(push) or 'none'}")
    if a.csv:
        with open(a.csv, "w") as fh:
            fh.write("trainer,top,win1,grind,hpLost,partyMax,partyAvg,flag\n")
            for row in rows:
                fh.write(",".join(str(x) for x in row) + "\n")


if __name__ == "__main__":
    main()

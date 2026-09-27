#!/usr/bin/env python3
"""Compose the extra chiptune songs into content/audio.json.

    python3 tools/compose_songs.py

Writes `songs.<id>` for every song in SONGS below (the seven original songs
are left alone) plus `mapSongs` for every map in MAP_SONGS and
`trainerSongs`. Both engines read audio.json directly (web) or through the
bake (Dreamcast), so run the bake after this.

A song is four tracks, all the same length so the loop stays in step:
melody (pulse), harmony (pulse), bass (triangle), drums (noise). Melodies
are written as "NOTE:beats" tokens; the helpers turn chords into arpeggios,
bass lines and drum loops. `fpb` is frames per beat at 60 Hz.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "content/audio.json"

NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
NAMES = ["C", "Cs", "D", "Ds", "E", "F", "Fs", "G", "Gs", "A", "Bb", "B"]


def midi(name: str) -> int:
    acc = 1 if name[1:2] in ("s", "#") else -1 if name[1:2] == "b" else 0
    octv = int(name[2:] if acc else name[1:])
    return 12 * (octv + 1) + NOTE[name[0]] + acc


def name(m: int) -> str:
    return f"{NAMES[m % 12]}{m // 12 - 1}"


# Chord symbols -> semitones above the root.
QUAL = {"": (0, 4, 7), "m": (0, 3, 7), "7": (0, 4, 7, 10), "m7": (0, 3, 7, 10),
        "dim": (0, 3, 6), "sus": (0, 5, 7), "5": (0, 7, 12)}


def chord(sym: str, octv: int) -> list[int]:
    root = sym[0] + (sym[1] if sym[1:2] in ("s", "b") else "")
    q = sym[len(root):]
    base = midi(f"{root}{octv}")
    return [base + i for i in QUAL[q]]


def melody(text: str, fpb: int) -> tuple[str, int]:
    """'E5:1 r:.5 G5:1.5' -> pattern, total frames."""
    out, total = [], 0
    for tok in text.split():
        n, beats = tok.split(":")
        f = round(float(beats) * fpb)
        out.append(f"{n}:{f}")
        total += f
    return " ".join(out), total


def arp(prog: list[str], fpb: int, beats: int, octv: int, step: float = 0.5, shape=(0, 1, 2, 1)) -> str:
    out = []
    f = round(step * fpb)
    per = int(beats / step)
    for sym in prog:
        c = chord(sym, octv)
        for i in range(per):
            out.append(f"{name(c[shape[i % len(shape)] % len(c)])}:{f}")
    return " ".join(out)


def pads(prog: list[str], fpb: int, beats: int, octv: int, tone: int = 1) -> str:
    """One held chord tone per bar, a soft second voice."""
    return " ".join(f"{name(chord(s, octv)[tone % 3])}:{beats * fpb}" for s in prog)


def bass(prog: list[str], fpb: int, beats: int, octv: int, style: str = "half") -> str:
    out = []
    for sym in prog:
        c = chord(sym, octv)
        r, fifth = c[0], c[0] + 7
        if style == "whole":
            out.append(f"{name(r)}:{beats * fpb}")
        elif style == "half":
            half = beats * fpb // 2
            out += [f"{name(r)}:{half}", f"{name(fifth)}:{beats * fpb - half}"]
        elif style == "walk":
            seq = [r, r + 12, fifth, r + 12]
            out += [f"{name(seq[i % 4])}:{fpb}" for i in range(beats)]
        elif style == "drive":
            e = fpb // 2
            out += [f"{name(r if i % 4 != 3 else fifth)}:{e}" for i in range(beats * 2)]
        elif style == "waltz":
            out += [f"{name(r)}:{fpb}", "r:%d" % fpb, f"{name(fifth)}:{fpb}"]
    return " ".join(out)


def drums(bars: int, fpb: int, beats: int, kind: str) -> str:
    out = []
    for _ in range(bars):
        for b in range(beats):
            if kind == "soft":
                out += (["n:2", f"r:{fpb - 2}"] if b % 2 == 0 else [f"r:{fpb}"])
            elif kind == "march":
                h = fpb // 2
                out += ["n:3", f"r:{h - 3}", "n:1", f"r:{fpb - h - 1}"] if b % 2 == 1 else ["n:2", f"r:{fpb - 2}"]
            elif kind == "rock":
                h = fpb // 2
                out += ["n:4", f"r:{h - 4}", "n:1", f"r:{fpb - h - 1}"]
            elif kind == "waltz":
                out += (["n:2", f"r:{fpb - 2}"] if b == 0 else ["n:1", f"r:{fpb - 1}"])
            elif kind == "none":
                out.append(f"r:{fpb}")
            elif kind == "toll":
                out += (["n:6", f"r:{fpb - 6}"] if b == 0 else [f"r:{fpb}"])
    return " ".join(out)


def song(mel: str, prog: list[str], fpb: int, beats: int, *, lead=(2, 11), harm="arp", harm_oct=4,
         harm_vol=5, bass_style="half", bass_oct=2, bass_vol=8, drum="soft", drum_vol=4, harm_duty=1,
         shape=(0, 1, 2, 1), step=0.5) -> dict:
    lead_pat, total = melody(mel, fpb)
    bars = len(prog)
    if total != bars * beats * fpb:
        raise SystemExit(f"melody is {total} frames, progression is {bars * beats * fpb}")
    if harm == "arp":
        h = arp(prog, fpb, beats, harm_oct, step, shape)
    else:
        h = pads(prog, fpb, beats, harm_oct)
    return {"loop": True, "tracks": [
        {"wave": "pulse", "duty": lead[0], "vol": lead[1], "pattern": lead_pat},
        {"wave": "pulse", "duty": harm_duty, "vol": harm_vol, "pattern": h},
        {"wave": "tri", "duty": 0, "vol": bass_vol, "pattern": bass(prog, fpb, beats, bass_oct, bass_style)},
        {"wave": "noise", "duty": 0, "vol": drum_vol, "pattern": drums(bars, fpb, beats, drum)},
    ]}


SONGS = {
    # The Sephirot: the cities and paths north of the Veil. D minor, hopeful
    # and tense, walking pace.
    "sephirot": song(
        "D5:1 A4:.5 D5:.5 E5:1 F5:1 "
        "E5:1.5 D5:.5 C5:1 G4:1 "
        "F4:1 Bb4:1 D5:1 C5:.5 Bb4:.5 "
        "A4:2 Cs5:1 E5:1 "
        "F5:1 E5:.5 D5:.5 A5:1 F5:1 "
        "A5:1 G5:.5 F5:.5 C5:1 F5:1 "
        "G5:1.5 F5:.5 E5:1 D5:1 "
        "Cs5:1 E5:1 A4:2",
        ["Dm", "C", "Bb", "A", "Dm", "F", "G", "A"], 22, 4, bass_style="half", drum="soft"),
    # The Weeping Road and the gauntlet: travelling music, A major.
    "road": song(
        "E5:1 Cs5:.5 E5:.5 A5:1 E5:1 "
        "D5:1 B4:.5 D5:.5 Gs5:1 E5:1 "
        "Fs5:1 E5:.5 Cs5:.5 A4:1 Cs5:1 "
        "D5:1.5 Cs5:.5 B4:1 A4:1 "
        "Cs5:.5 E5:.5 A5:1 Gs5:.5 Fs5:.5 E5:1 "
        "B4:.5 Cs5:.5 D5:1 E5:1 Gs5:1 "
        "A5:1 Fs5:1 D5:1 Fs5:1 "
        "E5:2 r:1 E4:1",
        ["A", "E", "Fsm", "D", "A", "E", "D", "E"], 18, 4, bass_style="walk", drum="rock", drum_vol=3,
        harm_duty=0, shape=(0, 2, 1, 2)),
    # The Ghost Guild crypt, the haunted hall, the empty house. Slow A minor,
    # thin lead, no drums but a toll every bar.
    "crypt": song(
        "E5:2 C5:1 B4:1 "
        "A4:3 r:1 "
        "D5:2 F5:1 E5:1 "
        "Gs4:3 r:1 "
        "A5:2 G5:1 E5:1 "
        "F5:2 C5:2 "
        "D5:1 E5:1 F5:1 D5:1 "
        "E5:4",
        ["Am", "Am", "Dm", "E", "Am", "F", "Dm", "E"], 34, 4, lead=(0, 9), harm="arp", harm_oct=3,
        harm_vol=3, harm_duty=2, bass_style="whole", bass_vol=7, drum="toll", drum_vol=2, step=1),
    # The nine military bases. E minor march with a snare.
    "base": song(
        "E5:.5 r:.5 E5:.5 E5:.5 G5:1 E5:1 "
        "B4:.5 r:.5 B4:.5 B4:.5 D5:1 B4:1 "
        "C5:.5 r:.5 C5:.5 E5:.5 G5:1 E5:1 "
        "D5:.5 r:.5 D5:.5 Fs5:.5 A5:1 Fs5:1 "
        "G5:1 Fs5:.5 E5:.5 B4:1 E5:1 "
        "G5:1 A5:.5 G5:.5 Fs5:1 E5:1 "
        "A5:1 G5:.5 Fs5:.5 E5:1 C5:1 "
        "B4:1 Ds5:1 Fs5:1 B5:1",
        ["Em", "Em", "C", "D", "Em", "Em", "Am", "B"], 18, 4, bass_style="drive", drum="march", drum_vol=6,
        harm_duty=0, harm_vol=4),
    # Nero's palace at Keter. C minor, slow and grand.
    "palace": song(
        "C5:2 Eb5:1 G5:1 "
        "Ab5:2 G5:1 Eb5:1 "
        "F5:2 Ab5:1 C6:1 "
        "B5:2 D5:1 G5:1 "
        "C6:1.5 Bb5:.5 Ab5:1 G5:1 "
        "Eb5:2 G5:1 Bb5:1 "
        "Ab5:1 F5:1 G5:1 B4:1 "
        "C5:4",
        ["Cm", "Ab", "Fm", "G", "Cm", "Eb", "Fm", "Cm"], 30, 4, harm_oct=3, harm_vol=5,
        bass_style="half", bass_vol=9, drum="toll", drum_vol=3, harm_duty=2),
    # Inns, the library, the guild halls: a small waltz in G.
    "guild": song(
        "D5:1 G5:1 B5:1 "
        "A5:2 G5:1 "
        "Fs5:1 A5:1 D5:1 "
        "G5:3 "
        "E5:1 G5:1 B5:1 "
        "C6:1 B5:1 A5:1 "
        "D5:1 Fs5:1 A5:1 "
        "G5:3",
        ["G", "C", "D", "G", "Em", "C", "D", "G"], 22, 3, lead=(1, 9), bass_style="waltz", drum="waltz",
        drum_vol=2, harm_vol=4, shape=(1, 2, 0), step=1),
    # Generals, Lieutenant Lead, Mourner Vesk, the Commander. B minor, fast.
    "general": song(
        "B4:.5 D5:.5 Fs5:.5 B5:.5 A5:.5 Fs5:.5 D5:.5 Fs5:.5 "
        "G5:.5 B4:.5 D5:.5 G5:.5 Fs5:.5 D5:.5 B4:.5 D5:.5 "
        "E5:.5 G5:.5 B5:.5 E5:.5 D5:.5 E5:.5 Fs5:.5 G5:.5 "
        "Fs5:1 As5:1 Cs6:1 Fs5:1 "
        "B5:.5 A5:.5 Fs5:.5 D5:.5 B5:.5 A5:.5 Fs5:.5 D5:.5 "
        "G5:.5 Fs5:.5 D5:.5 B4:.5 G5:.5 Fs5:.5 D5:.5 B4:.5 "
        "E5:1 G5:.5 E5:.5 Fs5:1 A5:.5 Fs5:.5 "
        "Fs5:2 r:1 Fs4:1",
        ["Bm", "G", "Em", "Fs", "Bm", "G", "Em", "Fs"], 12, 4, lead=(2, 12), bass_style="drive",
        bass_vol=10, drum="rock", drum_vol=7, harm_duty=0, harm_vol=6, harm_oct=3),
    # Nero and the hostile Heavenfall. E phrygian, fastest in the game.
    "finalboss": song(
        "E5:.5 F5:.5 E5:.5 B4:.5 E5:.5 F5:.5 G5:.5 F5:.5 "
        "E5:.5 F5:.5 E5:.5 C5:.5 D5:.5 E5:.5 F5:.5 D5:.5 "
        "E5:.5 G5:.5 B5:.5 E6:.5 D6:.5 B5:.5 G5:.5 E5:.5 "
        "F5:1 A5:1 C6:1 F5:1 "
        "E6:.5 D6:.5 B5:.5 G5:.5 E6:.5 D6:.5 B5:.5 G5:.5 "
        "C6:.5 B5:.5 A5:.5 F5:.5 C6:.5 B5:.5 A5:.5 F5:.5 "
        "D6:1 C6:.5 B5:.5 A5:1 G5:.5 F5:.5 "
        "E5:2 F5:1 E5:1",
        ["Em", "C", "Em", "F", "Em", "F", "Dm", "E"], 10, 4, lead=(2, 12), bass_style="drive",
        bass_vol=11, drum="rock", drum_vol=8, harm_duty=0, harm_vol=7, harm_oct=3),
}

HOUSE_SONG = "guild"
MAP_SONGS = {
    "gauntlet": "road", "gauntlet1": "road", "gauntlet2": "road", "gauntlet3": "road",
    "gauntlet4": "road", "gauntlet5": "road", "gauntlet6": "crypt", "weepingroad": "road",
    "palaceketer": "palace", "keter": "palace",
    "ghostcrypt": "crypt", "hauntedhall": "crypt", "emptyhouse": "crypt",
    "heroeshall": HOUSE_SONG, "thievesden": HOUSE_SONG, "ruinslibrary": HOUSE_SONG,
    "ruinsinn": HOUSE_SONG, "brannhouse": "home", "hermithut": HOUSE_SONG, "sagehouse": "home",
}
TRAINER_SONGS = {
    "lieutenantLead": "general", "commanderFinal": "general", "mournerVesk": "general",
    "shinigami": "general", "nero": "finalboss", "heavenfallFinal": "finalboss",
    "heavenfallGrave": "finalboss",
}


def main() -> None:
    audio = json.loads(AUDIO.read_text())
    world = json.loads((ROOT / "content/world.json").read_text())
    logic = json.loads((ROOT / "content/logic.json").read_text())
    for sid, s in SONGS.items():
        audio["songs"][sid] = s
    ms = audio["mapSongs"]
    for mid in world["mapIds"]:
        if mid in MAP_SONGS:
            ms[mid] = MAP_SONGS[mid]
        elif mid.startswith("base"):
            ms[mid] = "base"
        elif mid not in ms:
            ms[mid] = "sephirot"  # every other new map is a Sephirot city or path
    audio["defaultMapSong"] = "overworld"
    ts = dict(TRAINER_SONGS)
    for g in logic["leg3"]["generals"]:
        ts[g["trainer"]] = "general"
    audio["trainerSongs"] = ts
    AUDIO.write_text(json.dumps(audio, indent=2, ensure_ascii=False) + "\n")
    print(f"songs: {len(audio['songs'])}, mapSongs: {len(ms)}, trainerSongs: {len(ts)}")


if __name__ == "__main__":
    main()

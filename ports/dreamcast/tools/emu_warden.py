#!/usr/bin/env python3
"""Play a crystal warden fight on the real Dreamcast build, in Flycast.

Boots the CDI headless (Xvfb), loads a save made by the web build one tile
under the warden (scripts/e2e-quartz.mjs writes <who>-before.bin), mashes A
through the talk, the battle, the win line and the mercy menu ("Let them
go"), saves from the pause menu, then reads the VMU back and checks the
badge flag, the kit's Marks and one battle. Then it reboots, picks
Continue, saves again and checks the badge survived the reload.

  emu_warden.py --cdi ports/dreamcast/crymon.cdi --flycast /path/to/flycast \
                --save-dir e2e-out [--out emu-out] [quartz opal]

Needs: Xvfb, python-xlib, Pillow, a Flycast binary (AppImage or extracted
AppRun). No BIOS: Flycast's built-in HLE BIOS (reios) boots the disc.
Default Flycast keyboard map: arrows = d-pad, X = A, Return = Start.
"""
import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from PIL import ImageGrab
from Xlib import X, XK, display
from Xlib.ext import xtest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
import vmu_tool  # noqa: E402

W, H = 640, 480
fails = []


def check(ok, what):
    print(("PASS  " if ok else "FAIL  ") + what, flush=True)
    if not ok:
        fails.append(what)


class Emu:
    def __init__(self, flycast, cdi, out, disp=":77"):
        self.flycast, self.cdi, self.out, self.disp = flycast, cdi, out, disp
        self.home = Path(tempfile.mkdtemp(prefix="crymon-flycast-"))
        cfg = self.home / ".config" / "flycast"
        cfg.mkdir(parents=True)
        (cfg / "emu.cfg").write_text(
            "[config]\nPerGameVmu = no\nUploadCrashLogs = no\n"
            f"[window]\nfullscreen = no\nleft = 0\ntop = 0\nwidth = {W}\nheight = {H}\nmaximized = no\n")
        self.data = self.home / ".local" / "share" / "flycast"
        self.data.mkdir(parents=True)  # Flycast will not create it for the VMU
        self.vmu = None  # found after the first boot (per-game name)
        self.xvfb = self.proc = self.d = None

    def env(self):
        e = dict(os.environ, HOME=str(self.home), DISPLAY=self.disp,
                 XDG_RUNTIME_DIR=str(self.home / "xdg"), SDL_AUDIODRIVER="dummy")
        (self.home / "xdg").mkdir(mode=0o700, exist_ok=True)
        return e

    def start(self):
        # A fresh X server per boot: a killed Flycast can leave XTest keys
        # stuck, and the next boot then ignores input.
        self.xvfb = subprocess.Popen(["Xvfb", self.disp, "-screen", "0", f"{W}x{H}x24"],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1.0)
        self.proc = subprocess.Popen([self.flycast, str(self.cdi)], env=self.env(),
                                     stdout=open(self.out / "flycast.log", "ab"), stderr=subprocess.STDOUT)
        self.d = display.Display(self.disp)
        for _ in range(60):
            if self.window():
                break
            time.sleep(0.5)
        time.sleep(6.0)  # reios boot + CryMon title

    def stop(self):
        for p in (self.proc, self.xvfb):
            if p and p.poll() is None:
                p.terminate()  # Flycast writes the VMU image on the way out
                try:
                    p.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    p.send_signal(signal.SIGKILL)
                    p.wait()
        self.proc = self.xvfb = None
        self.d = None

    def window(self):
        def walk(w):
            try:
                # SDL sets the title only as UTF-8 _NET_WM_NAME, so the
                # plain WM_NAME is empty: match the class instead.
                if "flycast" in (w.get_wm_class() or ()):
                    return w
            except Exception:
                pass
            for c in w.query_tree().children:
                r = walk(c)
                if r:
                    return r
            return None
        return walk(self.d.screen().root)

    def key(self, name, ms=120, after=0.15):
        w = self.window()
        if w:
            w.set_input_focus(X.RevertToParent, X.CurrentTime)
        kc = self.d.keysym_to_keycode(XK.string_to_keysym(name))
        xtest.fake_input(self.d, X.KeyPress, kc)
        self.d.sync()
        time.sleep(ms / 1000)
        xtest.fake_input(self.d, X.KeyRelease, kc)
        self.d.sync()
        time.sleep(after)

    def shot(self, name=None):
        im = ImageGrab.grab(xdisplay=self.disp)
        if name:
            im.save(self.out / name)
        return im

    def talk_open(self):
        """The talk box is bright text on the bottom rows of the 640x480 frame."""
        im = self.shot().convert("L").crop((10, 410, 630, 470))
        return sum(im.histogram()[161:]) > 150  # grey narration lines too

    def close_talk(self):
        for _ in range(12):
            if not self.talk_open():
                return
            self.key("x", after=0.4)

    # The world view always draws the HUD's "REP" word top-left; battles
    # and menus cover it. Its outline mask (lit vs black) doesn't change
    # with the reputation colour, so it tells world from battle.
    HUD_BOX = (6, 2, 70, 22)

    def hud_mask(self):
        im = self.shot().convert("L").crop(self.HUD_BOX)
        return [1 if v > 60 else 0 for v in im.point(lambda v: v).tobytes()]

    def mark_world(self):
        self.hud_ref = self.hud_mask()

    def in_world(self):
        m = self.hud_mask()
        diff = sum(a != b for a, b in zip(m, self.hud_ref))
        return diff < len(m) // 12

    def menu_open(self, im=None):
        """A draw_ui_frame() panel (pause, mercy, shop): its stretched
        9-slice edge makes the columns just inside the left and right
        borders a few flat colours from top to bottom."""
        im = (im or self.shot()).convert("RGB")
        cols = []
        for x in (42, W - 43):
            px = [im.getpixel((x, y)) for y in range(70, 400, 6)]
            if max(sum(p) for p in px) < 90:
                return False  # black letterbox, not a frame
            cols.append(len(set(px)))
        return max(cols) <= 6

    def idle(self):
        return self.in_world() and not self.talk_open() and not self.menu_open()

    def fight(self, max_presses=400):
        """Mash A until a battle has come and gone and the world is idle.
        Pressing A in the world next to the trainer would start the talk
        again, so stop as soon as the world is back with no talk or menu."""
        seen_battle = False
        for i in range(max_presses):
            self.key("x", after=0.3)
            world = self.in_world()
            if not world and not seen_battle:
                seen_battle = True
                self.shot("03-fight.png")
            if seen_battle and world and self.idle():
                # Lines type out letter by letter, so a fresh line can look
                # empty for a moment: stay idle over ~2 s before stopping.
                if all(time.sleep(0.5) or self.idle() for _ in range(4)):
                    return i
        return max_presses

    def pause_save(self):
        self.close_talk()
        self.key("Return", after=0.6)
        for _ in range(pause_row("SAVE")):
            self.key("Down", after=0.1)
        self.key("x", after=2.0)


def pause_row(label):
    """Row of a pause menu item, read from main.c so new items don't break us."""
    src = (REPO / "ports" / "dreamcast" / "src" / "main.c").read_text()
    body = src[src.index("static void draw_pause_menu("):]
    rows = re.search(r"rows\[\d+\]\s*=\s*\{([^}]*)\}", body).group(1)
    return re.findall(r'"([^"]*)"', rows).index(label)


def decode(blob):
    save = json.loads((REPO / "content" / "save.json").read_text())
    offs = [o + i for o, n in save["flagParts"] for i in range(n)]
    flags = {name: bool(blob[offs[i >> 3]] >> (i & 7) & 1) for i, name in enumerate(save["flags"])}
    return {"marks": blob[12] | blob[13] << 8, "battles": blob[15], "map": blob[5], "flags": flags}


def run(who, args):
    world = json.loads((REPO / "content" / "world.json").read_text())
    kit = world["trainers"][who]
    pre = Path(args.save_dir) / f"{who}-before.bin"
    out = Path(args.out) / who
    out.mkdir(parents=True, exist_ok=True)
    print(f"--- {kit['name']} on Dreamcast (Flycast) ---", flush=True)
    before = decode(pre.read_bytes())
    emu = Emu(args.flycast, args.cdi, out, disp=args.display)
    try:
        emu.start()                      # first boot creates the VMU image
        emu.stop()
        vmus = sorted(emu.data.glob("*vmu_save_A1.bin"))
        if not vmus:
            raise SystemExit(f"Flycast made no VMU image in {emu.data}")
        emu.vmu = vmus[0]
        img = bytearray(emu.vmu.read_bytes())
        vmu_tool.inject(img, pre.read_bytes())
        emu.vmu.write_bytes(img)

        emu.start()
        emu.shot("01-title.png")
        emu.key("x", after=2.0)          # Continue
        emu.shot("02-continue.png")
        emu.mark_world()
        n = emu.fight(max_presses=args.max_presses)
        print(f"      fight over after {n} presses", flush=True)
        emu.shot("04-after.png")
        emu.pause_save()
        emu.shot("05-saved.png")
        emu.stop()
        after = decode(vmu_tool.extract(bytearray(emu.vmu.read_bytes())))
        if kit.get("set"):
            check(after["flags"][kit["set"]], f"{kit['set']} set in the VMU save")
        check(after["marks"] - before["marks"] == kit.get("marks", 0),
              f"+{kit['marks']} marks (got +{after['marks'] - before['marks']})")
        check(after["battles"] - before["battles"] == 1,
              f"one battle counted (got {after['battles'] - before['battles']})")

        if args.quick:
            return
        emu.start()                      # reload: Continue, save again
        emu.key("x", after=2.0)
        emu.shot("06-reloaded.png")
        emu.pause_save()
        emu.stop()
        again = decode(vmu_tool.extract(bytearray(emu.vmu.read_bytes())))
        check((not kit.get("set") or again["flags"][kit["set"]]) and again["marks"] == after["marks"],
              "badge and marks survive a reboot + Continue + save")
    finally:
        emu.stop()
        shutil.rmtree(emu.home, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cdi", required=True)
    ap.add_argument("--flycast", required=True)
    ap.add_argument("--save-dir", required=True, help="dir with <who>-before.bin from the web e2e")
    ap.add_argument("--out", default="emu-out")
    ap.add_argument("--display", default=":77", help="X display for the private Xvfb")
    ap.add_argument("--quick", action="store_true", help="skip the reboot + Continue check")
    ap.add_argument("--max-presses", type=int, default=400)
    ap.add_argument("who", nargs="*", default=["quartz", "opal"])
    args = ap.parse_args()
    for who in args.who:
        run(who, args)
    print(f"screenshots: {args.out}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()

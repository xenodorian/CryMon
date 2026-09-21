#!/usr/bin/env python3
"""Snappier touch virtual controls: pointerdown + faster d-pad repeat + tap counters."""
from pathlib import Path
import re

# --- input.ts: faster dir repeat, count-based taps ---
ip = Path("src/game/input.ts")
it = ip.read_text()

# Initial hold delay 280 -> 140, repeat interval 110 -> 50
it2 = it.replace("if (held > 280 && since > 110)", "if (held > 140 && since > 50)")
if it2 == it:
    if "held > 140 && since > 50" in it:
        print("dir repeat already fast")
    else:
        raise SystemExit("dir repeat anchor missing")
else:
    it = it2
    print("dir repeat tightened")

# Convert boolean queues to counters so rapid presses aren't collapsed
if "private tapAQueued = false" in it:
    it = it.replace("private tapAQueued = false;", "private tapAQueued = 0;")
    it = it.replace("private tapBQueued = false;", "private tapBQueued = 0;")
    it = it.replace("private tapStartQueued = false;", "private tapStartQueued = 0;")
    it = it.replace("private tapSelectQueued = false;", "private tapSelectQueued = 0;")
    # beginFrame: consume one per frame if any
    old_bf = """  beginFrame() {
    this.used.clear();
    if (this.tapAQueued) {
      this.tapA = true;
      this.tapAQueued = false;
    } else this.tapA = false;
    if (this.tapBQueued) {
      this.tapB = true;
      this.tapBQueued = false;
    } else this.tapB = false;
    if (this.tapStartQueued) {
      this.tapStart = true;
      this.tapStartQueued = false;
    } else this.tapStart = false;
    if (this.tapSelectQueued) {
      this.tapSelect = true;
      this.tapSelectQueued = false;
    } else this.tapSelect = false;
  }"""
    new_bf = """  beginFrame() {
    this.used.clear();
    if (this.tapAQueued > 0) {
      this.tapA = true;
      this.tapAQueued -= 1;
    } else this.tapA = false;
    if (this.tapBQueued > 0) {
      this.tapB = true;
      this.tapBQueued -= 1;
    } else this.tapB = false;
    if (this.tapStartQueued > 0) {
      this.tapStart = true;
      this.tapStartQueued -= 1;
    } else this.tapStart = false;
    if (this.tapSelectQueued > 0) {
      this.tapSelect = true;
      this.tapSelectQueued -= 1;
    } else this.tapSelect = false;
  }"""
    if old_bf not in it:
        raise SystemExit("beginFrame anchor missing")
    it = it.replace(old_bf, new_bf)
    # queue* increments
    it = it.replace(
        """  queueA() {
    this.tapAQueued = true;
  }
  queueB() {
    this.tapBQueued = true;
  }
  queueStart() {
    this.tapStartQueued = true;
  }
  queueSelect() {
    this.tapSelectQueued = true;
  }""",
        """  queueA() {
    this.tapAQueued += 1;
  }
  queueB() {
    this.tapBQueued += 1;
  }
  queueStart() {
    this.tapStartQueued += 1;
  }
  queueSelect() {
    this.tapSelectQueued += 1;
  }""",
    )
    # gamepad edge still does = true -> change to += 1
    it = it.replace("if (aBtn && !this.padA) this.tapAQueued = true;", "if (aBtn && !this.padA) this.tapAQueued += 1;")
    it = it.replace("if (bBtn && !this.padB) this.tapBQueued = true;", "if (bBtn && !this.padB) this.tapBQueued += 1;")
    it = it.replace("if (startBtn && !this.padStart) this.tapStartQueued = true;", "if (startBtn && !this.padStart) this.tapStartQueued += 1;")
    it = it.replace("if (selectBtn && !this.padSelect) this.tapSelectQueued = true;", "if (selectBtn && !this.padSelect) this.tapSelectQueued += 1;")
    print("tap counters")
else:
    print("tap counters already?")

ip.write_text(it)

# --- crymon-app.tsx: Face uses pointerdown, not click ---
ap = Path("src/components/crymon-app.tsx")
a = ap.read_text()

old_face = '''function Face({
  label,
  onClick,
  primary,
}: {
  label: string;
  onClick: () => void;
  primary?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "min-h-11 min-w-12 rounded-md border px-3 py-2 text-xs font-medium",
        primary ? "border-fg bg-fg text-bg" : "border-border bg-raised text-fg",
      )}
    >
      {label}
    </button>
  );
}'''

new_face = '''function Face({
  label,
  onClick,
  primary,
}: {
  label: string;
  onClick: () => void;
  primary?: boolean;
}) {
  return (
    <button
      type="button"
      style={{ touchAction: "manipulation" }}
      onPointerDown={(e) => {
        e.preventDefault();
        (e.currentTarget as HTMLElement).setPointerCapture?.(e.pointerId);
        onClick();
      }}
      onClick={(e) => {
        // Keyboard / accessibility activation only; touch already fired on pointerdown.
        if (e.detail === 0) onClick();
      }}
      className={cn(
        "min-h-11 min-w-12 rounded-md border px-3 py-2 text-xs font-medium select-none",
        primary ? "border-fg bg-fg text-bg" : "border-border bg-raised text-fg",
      )}
    >
      {label}
    </button>
  );
}'''

if "touchAction: \"manipulation\"" in a or "touchAction: 'manipulation'" in a:
    print("Face already patched")
else:
    if old_face not in a:
        raise SystemExit("Face component anchor missing")
    a = a.replace(old_face, new_face)
    print("Face pointerdown")

# PadBtn: touch-action manipulation + preventDefault on pointerdown when present
if 'touchAction: "manipulation"' not in a or a.count("manipulation") < 2:
    old_pad = '''function PadBtn({
  children,
  ...rest
}: { children: ReactNode } & HTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      type="button"
      className="grid size-11 place-items-center rounded-md border border-border bg-raised text-sm text-fg active:bg-fg active:text-bg"
      {...rest}
    >
      {children}
    </button>
  );
}'''
    new_pad = '''function PadBtn({
  children,
  ...rest
}: { children: ReactNode } & HTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      type="button"
      style={{ touchAction: "manipulation" }}
      className="grid size-11 place-items-center rounded-md border border-border bg-raised text-sm text-fg active:bg-fg active:text-bg select-none"
      {...rest}
    >
      {children}
    </button>
  );
}'''
    if old_pad in a:
        a = a.replace(old_pad, new_pad)
        print("PadBtn touch-action")
    else:
        print("PadBtn anchor missing (non-fatal)")

ap.write_text(a)
print("done")

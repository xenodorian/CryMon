const GAME_KEYS = new Set([
  "ArrowUp",
  "ArrowDown",
  "ArrowLeft",
  "ArrowRight",
  "KeyW",
  "KeyA",
  "KeyS",
  "KeyD",
  "KeyZ",
  "KeyX",
  "Space",
  "Enter",
  "Escape",
  "KeyC",
  "KeyQ",
  "Tab",
  "Backspace",
  "Digit1",
  "Digit2",
  "Digit3",
]);

export class Input {
  keys = new Set<string>();
  injected: string[] | null = null;
  prev = new Set<string>();
  padX = 0;
  padY = 0;
  padA = false;
  padB = false;
  padStart = false;
  padSelect = false;
  tapA = false;
  tapB = false;
  tapStart = false;
  tapSelect = false;
  /** Web-only Turbo button (crymon-app.tsx): held true while the on-screen
   *  Turbo button is pressed. The game loop queues an extra confirm tap
   *  every rendered frame while this is true (see startLoop()), so
   *  dialogue/battle message advances fire as fast as each system's own
   *  cooldown (talkLock, phase transitions) allows, instead of waiting on
   *  real button mashing. No Dreamcast equivalent -- there's no on-screen
   *  UI to drive it there. */
  turboHeld = false;
  private touchPad = { x: 0, y: 0 };
  private prevAxisX = 0;
  private prevAxisY = 0;
  private dirHeldAt: Record<string, number | null> = { up: null, down: null, left: null, right: null };
  private dirLastFire: Record<string, number> = { up: 0, down: 0, left: 0, right: 0 };

  private tapAQueued = 0;
  private tapBQueued = 0;
  private tapStartQueued = 0;
  private tapSelectQueued = 0;
  private used = new Set<string>();

  attach(el: HTMLElement) {
    // This listener is on window, so it fires for every keystroke on the
    // page -- including real text inputs like crymon-app.tsx's Dev Codes
    // field. Without this check, GAME_KEYS' preventDefault() (needed so
    // held arrows/WASD don't scroll the page) also steals Backspace,
    // Space, Enter, Tab and the letter keys from any focused input.
    const typing = () => {
      const t = document.activeElement;
      return !!t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || (t as HTMLElement).isContentEditable);
    };
    const down = (e: KeyboardEvent) => {
      if (typing()) return;
      if (GAME_KEYS.has(e.code)) e.preventDefault();
      this.keys.add(e.code);
    };
    // Always process keyup (even while typing) so a key held down before
    // focus moved to a text field doesn't get stuck "pressed" forever --
    // removing from the set is harmless no matter who has focus.
    const up = (e: KeyboardEvent) => this.keys.delete(e.code);
    const clear = () => {
      this.keys.clear();
      this.turboHeld = false;
    };
    window.addEventListener("keydown", down);
    window.addEventListener("keyup", up);
    window.addEventListener("blur", clear);
    document.addEventListener("visibilitychange", () => {
      if (document.hidden) clear();
    });
    el.style.touchAction = "none";
    return () => {
      window.removeEventListener("keydown", down);
      window.removeEventListener("keyup", up);
      window.removeEventListener("blur", clear);
    };
  }

  beginFrame() {
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
  }

  endFrame() {
    this.prev = new Set(this.live());
    const a = this.rawAxis();
    this.prevAxisX = a.x;
    this.prevAxisY = a.y;
  }

  live() {
    if (this.injected) return new Set(this.injected);
    return this.keys;
  }

  held(code: string) {
    return this.live().has(code);
  }

  pressed(code: string) {
    return this.live().has(code) && !this.prev.has(code);
  }

  rawAxis() {
    return { x: this.padX + this.touchPad.x, y: this.padY + this.touchPad.y };
  }

  axis() {
    let x = this.rawAxis().x;
    let y = this.rawAxis().y;
    if (this.held("KeyA") || this.held("ArrowLeft")) x -= 1;
    if (this.held("KeyD") || this.held("ArrowRight")) x += 1;
    if (this.held("KeyW") || this.held("ArrowUp")) y -= 1;
    if (this.held("KeyS") || this.held("ArrowDown")) y += 1;
    const m = Math.hypot(x, y);
    if (m > 1) {
      x /= m;
      y /= m;
    }
    return { x, y };
  }

  confirm() {
    if (this.used.has("_confirm")) return false;
    const v = this.pressed("KeyZ") || this.pressed("Space") || this.tapA;
    if (v) this.used.add("_confirm");
    return v;
  }

  cancel() {
    if (this.used.has("_cancel")) return false;
    const v = this.pressed("KeyX") || this.pressed("Escape") || this.pressed("KeyC") || this.tapB;
    if (v) this.used.add("_cancel");
    return v;
  }

  start() {
    if (this.used.has("_start")) return false;
    const v = this.pressed("Enter") || this.tapStart;
    if (v) this.used.add("_start");
    return v;
  }

  select() {
    if (this.used.has("_select")) return false;
    const v =
      this.pressed("KeyQ") || this.pressed("Tab") || this.pressed("Backspace") || this.tapSelect;
    if (v) this.used.add("_select");
    return v;
  }

  private dir(name: "up" | "down" | "left" | "right", keys: string[], cur: number, prev: number, negative: boolean) {
    if (this.used.has("_" + name)) return false;
    const thresh = 0.5;
    const active = negative ? cur < -thresh : cur > thresh;
    const was = negative ? prev < -thresh : prev > thresh;
    const now = performance.now();
    let v = keys.some((k) => this.pressed(k));
    if (active && !was) {
      v = true;
      this.dirHeldAt[name] = now;
      this.dirLastFire[name] = now;
    } else if (!active) {
      this.dirHeldAt[name] = null;
    } else if (this.dirHeldAt[name] != null) {
      const held = now - (this.dirHeldAt[name] as number);
      const since = now - this.dirLastFire[name];
      if (held > 55 && since > 28) {
        this.dirLastFire[name] = now;
        v = true;
      }
    }
    if (v) this.used.add("_" + name);
    return v;
  }

  up() {
    return this.dir("up", ["ArrowUp", "KeyW"], this.rawAxis().y, this.prevAxisY, true);
  }

  down() {
    return this.dir("down", ["ArrowDown", "KeyS"], this.rawAxis().y, this.prevAxisY, false);
  }

  left() {
    return this.dir("left", ["ArrowLeft", "KeyA"], this.rawAxis().x, this.prevAxisX, true);
  }

  right() {
    return this.dir("right", ["ArrowRight", "KeyD"], this.rawAxis().x, this.prevAxisX, false);
  }

  queueA() {
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
  }
  consumeQueuedFace() {
    if (this.tapAQueued > 0) { this.tapA = true; this.tapAQueued -= 1; }
    if (this.tapBQueued > 0) { this.tapB = true; this.tapBQueued -= 1; }
    if (this.tapStartQueued > 0) { this.tapStart = true; this.tapStartQueued -= 1; }
    if (this.tapSelectQueued > 0) { this.tapSelect = true; this.tapSelectQueued -= 1; }
    this.used.clear();
  }

  setPad(x: number, y: number) {
    this.touchPad = { x, y };
  }

  pollGamepad() {
    const pads = navigator.getGamepads?.() ?? [];
    let any = false;
    let x = 0;
    let y = 0;
    for (const p of pads) {
      if (!p) continue;
      any = true;
      const ax = p.axes[0] ?? 0;
      const ay = p.axes[1] ?? 0;
      const m = Math.hypot(ax, ay);
      if (m > 0.18) {
        const s = (m - 0.18) / 0.82 / m;
        x += ax * s;
        y += ay * s;
      }
      if (p.buttons[12]?.pressed) y -= 1;
      if (p.buttons[13]?.pressed) y += 1;
      if (p.buttons[14]?.pressed) x -= 1;
      if (p.buttons[15]?.pressed) x += 1;
      const aBtn = Boolean(p.buttons[0]?.pressed);
      const bBtn = Boolean(p.buttons[1]?.pressed);
      const startBtn = Boolean(p.buttons[9]?.pressed);
      const selectBtn = Boolean(p.buttons[8]?.pressed);
      if (aBtn && !this.padA) this.tapAQueued += 1;
      if (bBtn && !this.padB) this.tapBQueued += 1;
      if (startBtn && !this.padStart) this.tapStartQueued += 1;
      if (selectBtn && !this.padSelect) this.tapSelectQueued += 1;
      this.padA = aBtn;
      this.padB = bBtn;
      this.padStart = startBtn;
      this.padSelect = selectBtn;
    }
    if (any) {
      this.padX = x;
      this.padY = y;
    }
  }
}

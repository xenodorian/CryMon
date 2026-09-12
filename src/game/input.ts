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
  private touchPad = { x: 0, y: 0 };

  private tapAQueued = false;
  private tapBQueued = false;
  private tapStartQueued = false;
  private tapSelectQueued = false;
  private used = new Set<string>();

  attach(el: HTMLElement) {
    const down = (e: KeyboardEvent) => {
      if (GAME_KEYS.has(e.code)) e.preventDefault();
      this.keys.add(e.code);
    };
    const up = (e: KeyboardEvent) => this.keys.delete(e.code);
    const clear = () => this.keys.clear();
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
  }

  endFrame() {
    this.prev = new Set(this.live());
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

  axis() {
    let x = this.padX + this.touchPad.x;
    let y = this.padY + this.touchPad.y;
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

  up() {
    return this.pressed("ArrowUp") || this.pressed("KeyW");
  }

  down() {
    return this.pressed("ArrowDown") || this.pressed("KeyS");
  }

  left() {
    return this.pressed("ArrowLeft") || this.pressed("KeyA");
  }

  right() {
    return this.pressed("ArrowRight") || this.pressed("KeyD");
  }

  queueA() {
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
      if (aBtn && !this.padA) this.tapAQueued = true;
      if (bBtn && !this.padB) this.tapBQueued = true;
      if (startBtn && !this.padStart) this.tapStartQueued = true;
      if (selectBtn && !this.padSelect) this.tapSelectQueued = true;
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

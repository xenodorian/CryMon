import { useEffect, useRef, useState, type HTMLAttributes, type PointerEvent, type ReactNode } from "react";
import { Download, Gamepad2, Maximize, Minimize, Volume2, VolumeX, Zap } from "lucide-react";
import { Button, buttonVariants } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { CryMon } from "@/game/engine";
import { cn } from "@/lib/utils";

export function CryMonApp() {
  const ref = useRef<HTMLCanvasElement>(null);
  const gameRef = useRef<CryMon | null>(null);
  const stageRef = useRef<HTMLElement>(null);
  const [fullscreen, setFullscreen] = useState(false);
  const [padOn, setPadOn] = useState(true);
  const [ready, setReady] = useState(false);
  const [muted, setMuted] = useState(false);
  const [devCodesOn, setDevCodesOn] = useState(false);
  const [devCodeText, setDevCodeText] = useState("");
  const [devCodeMsg, setDevCodeMsg] = useState("");

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    let live = true;
    let g: CryMon | null = null;
    const failsafe = window.setTimeout(() => {
      if (!live) return;
      g?.startLoop();
      setReady(true);
    }, 900);
    try {
      g = new CryMon(canvas);
      gameRef.current = g;
      void g
        .boot()
        .then(() => {
          if (!live) return;
          g?.startLoop();
          setReady(true);
        })
        .catch(() => {
          if (!live) return;
          g?.startLoop();
          setReady(true);
        });
    } catch {
      setReady(true);
    }
    return () => {
      live = false;
      window.clearTimeout(failsafe);
      g?.stop();
    };
  }, []);

  useEffect(() => {
    const g = gameRef.current;
    if (!g) return;
    g.audio.muted = muted;
  }, [muted]);

  // Real Fullscreen API where the browser has it (desktop, Android); a fixed
  // overlay where it does not (iPhone Safari has no element fullscreen).
  const toggleFullscreen = async () => {
    const el = stageRef.current as (HTMLElement & { webkitRequestFullscreen?: () => void }) | null;
    const doc = document as Document & { webkitFullscreenElement?: Element | null; webkitExitFullscreen?: () => void };
    if (!el) return;
    if (doc.fullscreenElement || doc.webkitFullscreenElement) {
      await (doc.exitFullscreen?.() ?? doc.webkitExitFullscreen?.());
      return;
    }
    if (fullscreen) {
      setFullscreen(false);
      return;
    }
    try {
      if (el.requestFullscreen) await el.requestFullscreen();
      else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen();
      else setFullscreen(true);
    } catch {
      setFullscreen(true);
    }
  };

  useEffect(() => {
    const doc = document as Document & { webkitFullscreenElement?: Element | null };
    const sync = () => setFullscreen(!!(doc.fullscreenElement || doc.webkitFullscreenElement));
    document.addEventListener("fullscreenchange", sync);
    document.addEventListener("webkitfullscreenchange", sync);
    return () => {
      document.removeEventListener("fullscreenchange", sync);
      document.removeEventListener("webkitfullscreenchange", sync);
    };
  }, []);

  // Touch pad defaults on for touch devices, off for mouse/keyboard; the choice sticks.
  useEffect(() => {
    try {
      const saved = localStorage.getItem("crymon.pad");
      setPadOn(saved !== null ? saved === "1" : window.matchMedia("(pointer: coarse)").matches);
    } catch {
      setPadOn(window.matchMedia("(pointer: coarse)").matches);
    }
  }, []);
  const togglePad = () =>
    setPadOn((v) => {
      try {
        localStorage.setItem("crymon.pad", v ? "0" : "1");
      } catch {
        /* storage blocked */
      }
      return !v;
    });

  const toggleRef = useRef(toggleFullscreen);
  toggleRef.current = toggleFullscreen;
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = document.activeElement;
      if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA")) return;
      if (e.code === "KeyF" && !e.ctrlKey && !e.metaKey && !e.altKey) void toggleRef.current();
      if (e.code === "Escape") setFullscreen((f) => (document.fullscreenElement ? f : false));
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  // Pad written straight to Input on pointer events.

  return (
    <div className="min-h-dvh bg-bg text-fg">
      <header className="border-b border-border">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3 px-4 py-4 sm:px-6">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-muted">480p homebrew</p>
            <h1 className="font-display text-2xl font-medium tracking-tight">CryMon</h1>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setMuted((m) => !m)}
              aria-label={muted ? "Unmute" : "Mute"}
            >
              {muted ? <VolumeX className="size-4" /> : <Volume2 className="size-4" />}
              {muted ? "Muted" : "Sound"}
            </Button>
            <Button
              size="sm"
              variant={padOn ? "default" : "ghost"}
              onClick={togglePad}
              aria-pressed={padOn}
              aria-label={padOn ? "Hide touch pad" : "Show touch pad"}
            >
              <Gamepad2 className="size-4" />
              Touch pad
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => void toggleFullscreen()}
              aria-label={fullscreen ? "Exit fullscreen" : "Fullscreen"}
            >
              {fullscreen ? <Minimize className="size-4" /> : <Maximize className="size-4" />}
              Fullscreen
            </Button>
            <a
              className={cn(buttonVariants({ variant: "default", size: "sm" }))}
              href={`${import.meta.env.BASE_URL}rom/CryMon.cdi?v=dc8`}
              download="CryMon.cdi"
              rel="noopener"
            >
              <Download className="size-4" />
              Dreamcast CDI
            </a>
            <Button
              size="sm"
              variant={devCodesOn ? "default" : "ghost"}
              onClick={() => {
                setDevCodesOn((v) => !v);
                setDevCodeMsg("");
              }}
              aria-pressed={devCodesOn}
            >
              Dev Codes
            </Button>
          </div>
        </div>
        {devCodesOn && (
          <div className="mx-auto flex max-w-5xl flex-wrap items-center gap-2 px-4 pb-4 sm:px-6">
            <Input
              value={devCodeText}
              onChange={(e) => setDevCodeText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key !== "Enter") return;
                const msg = gameRef.current?.submitDevCode(devCodeText) ?? "";
                setDevCodeMsg(msg);
              }}
              placeholder="WinAll · PassAll"
              className="max-w-[220px]"
              aria-label="Dev code"
            />
            <Button
              size="sm"
              variant="outline"
              onClick={() => {
                const msg = gameRef.current?.submitDevCode(devCodeText) ?? "";
                setDevCodeMsg(msg);
              }}
            >
              Submit
            </Button>
            {devCodeMsg && <span className="text-xs text-muted">{devCodeMsg}</span>}
          </div>
        )}
      </header>

      <main className="mx-auto grid max-w-5xl gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[minmax(0,1fr)_220px]">
        <section
          ref={stageRef}
          className={cn(
            "flex flex-col items-center gap-4",
            fullscreen && "fixed inset-0 z-50 h-dvh w-screen justify-between gap-0 bg-black p-0",
          )}
        >
          <div
            className={cn(
              "relative w-full max-w-[960px] overflow-hidden rounded-lg border border-border bg-inset p-2 shadow-panel",
              fullscreen && "min-h-0 max-w-none flex-1 rounded-none border-0 bg-black p-0 shadow-none",
            )}
          >
            <canvas
              ref={ref}
              className={cn(
                "mx-auto block h-auto w-full max-w-[960px] touch-none bg-bg",
                fullscreen && "h-full max-w-none bg-black object-contain",
              )}
              style={{ imageRendering: "pixelated", aspectRatio: fullscreen ? undefined : "640 / 480" }}
              width={640}
              height={480}
            />
            {fullscreen && (
              <div className="absolute right-2 top-2 z-10 flex gap-2">
                <Button size="sm" variant="outline" className="bg-black/60 opacity-70 hover:opacity-100" onClick={togglePad} aria-pressed={padOn}>
                  <Gamepad2 className="size-4" />
                  Pad
                </Button>
                <Button size="sm" variant="outline" className="bg-black/60 opacity-70 hover:opacity-100" onClick={() => void toggleFullscreen()}>
                  <Minimize className="size-4" />
                  Exit
                </Button>
              </div>
            )}
            {!ready && (
              <p className="absolute inset-0 grid place-items-center text-sm text-muted">Loading cart…</p>
            )}
          </div>

          <div
            className={cn(
              "flex w-full max-w-[960px] items-end justify-between gap-3 overflow-x-hidden",
              !padOn && "hidden",
              fullscreen && "px-2 pb-2",
            )}
          >
            <Dpad
              onPad={(v) => {
                gameRef.current?.input.setPad(v.x, v.y);
              }}
            />
            <TurboBtn
              onHold={(held) => {
                if (gameRef.current) gameRef.current.input.turboHeld = held;
              }}
            />
            <div className="grid grid-cols-2 gap-2 pb-2">
              <Face label="B" onClick={() => gameRef.current?.input.queueB()} />
              <Face label="A" primary onClick={() => gameRef.current?.input.queueA()} />
              <Face label="SEL" onClick={() => gameRef.current?.input.queueSelect()} />
              <Face label="S" onClick={() => gameRef.current?.input.queueStart()} />
            </div>
          </div>
        </section>

        <aside className="flex flex-col gap-4 text-sm leading-relaxed text-muted">
          <h2 className="font-display text-lg text-fg">How to play</h2>
          <p>
            Max walks out with Quillpup and no Capture Crystals. Anne presses five into her hand after the first fight. Tall grass hides wild CryMon. Tamers will not.
          </p>
          <ul className="space-y-2 text-fg">
            <li>
              <span className="text-muted">Move</span> WASD / arrows
            </li>
            <li>
              <span className="text-muted">Run</span> hold Shift, or X / Square on a pad (X on Dreamcast)
            </li>
            <li>
              <span className="text-muted">Talk / confirm</span> Z Space · people, herbs, the wrecked cart
            </li>
            <li>
              <span className="text-muted">CryMon (Start)</span> Enter · Start on a pad · S on touch — sprites, HP, send out, stats, moves, release. A full party asks you to release one when a capture lands.
            </li>
            <li>
              <span className="text-muted">Bag (Select)</span> Q Tab · Select on a pad · SEL on touch — use salves and wraps on a CryMon
            </li>
            <li>
              <span className="text-muted">Sleep</span> Max's empty bed in the cottage restores every CryMon. Father's bed is the occupied one.
            </li>
            <li>
              <span className="text-muted">Shop</span> Bram on the dirt path — buy and sell for marks
            </li>
            <li>
              <span className="text-muted">Doors</span> walk onto them — no button
            </li>
            <li>
              <span className="text-muted">Party</span> in the CryMon menu, Left/Right swaps Max↔Father · 1-6 lead · X C Esc
            </li>
            <li>
              <span className="text-muted">Turbo</span> T · hold the on-screen button — fast-forwards dialogue and battle messages
            </li>
          </ul>
          <p>
            In battle: items first, then a strike. Specials spend PP and open a timing bar. When the foe
            answers, dodge on agility, block on strength, or raise a barrier on special. Capture Crystals
            only take wild CryMon.
          </p>
          <p>
            Mason waits outside the cottage. Wren is west, Ivo in the grove, Nell by the pond. Bram keeps a stall on the path.
            Pike lost a crystal in the east reeds. Tall grass west hides Glimmoth; east hides Tortcask; south hits
            harder. Calder waits at the south tent.
          </p>
        </aside>
      </main>
    </div>
  );
}

function Dpad({ onPad }: { onPad: (v: { x: number; y: number }) => void }) {
  const hold = (x: number, y: number) => ({
    onPointerDown: (e: PointerEvent) => {
      (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
      onPad({ x, y });
    },
    onPointerUp: () => onPad({ x: 0, y: 0 }),
    onPointerCancel: () => onPad({ x: 0, y: 0 }),
  });
  return (
    <div className="grid w-[132px] grid-cols-3 grid-rows-3 gap-1">
      <span />
      <PadBtn {...hold(0, -1)}>↑</PadBtn>
      <span />
      <PadBtn {...hold(-1, 0)}>←</PadBtn>
      <span />
      <PadBtn {...hold(1, 0)}>→</PadBtn>
      <span />
      <PadBtn {...hold(0, 1)}>↓</PadBtn>
      <span />
    </div>
  );
}

/** Web-only Turbo button: holds gameRef.current.input.turboHeld true for
 *  as long as it's pressed, so the game loop queues an extra confirm tap
 *  every rendered frame (see startLoop()'s turboHeld check) -- rapid-fire
 *  through dialogue and battle messages without real button mashing. No
 *  Dreamcast port equivalent (no on-screen UI there to drive it). */
function TurboBtn({ onHold }: { onHold: (held: boolean) => void }) {
  const [active, setActive] = useState(false);
  const set = (held: boolean) => {
    setActive(held);
    onHold(held);
  };
  return (
    <button
      type="button"
      style={{ touchAction: "manipulation" }}
      aria-pressed={active}
      aria-label="Turbo (hold to fast-forward dialogue and battles)"
      onPointerDown={(e) => {
        e.preventDefault();
        (e.currentTarget as HTMLElement).setPointerCapture?.(e.pointerId);
        set(true);
      }}
      onPointerUp={() => set(false)}
      onPointerCancel={() => set(false)}
      onPointerLeave={() => set(false)}
      className={cn(
        "flex size-11 flex-col items-center justify-center gap-0.5 rounded-md border text-[10px] font-medium select-none",
        active ? "border-fg bg-fg text-bg" : "border-border bg-raised text-fg",
      )}
    >
      <Zap className="size-4" />
      Turbo
    </button>
  );
}

function PadBtn({
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
}

function Face({
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
        e.stopPropagation();
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
}

import { useEffect, useRef, useState, type HTMLAttributes, type PointerEvent, type ReactNode } from "react";
import { Download, Volume2, VolumeX } from "lucide-react";
import { Button, buttonVariants } from "@/components/ui/button";
import { CryMon } from "@/game/engine";
import { cn } from "@/lib/utils";

export function CryMonApp() {
  const ref = useRef<HTMLCanvasElement>(null);
  const gameRef = useRef<CryMon | null>(null);
  const [ready, setReady] = useState(false);
  const [muted, setMuted] = useState(false);
  const [pad, setPad] = useState({ x: 0, y: 0 });

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

  useEffect(() => {
    gameRef.current?.input.setPad(pad.x, pad.y);
  }, [pad]);

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
            <a
              className={cn(buttonVariants({ variant: "default", size: "sm" }))}
              href={`${import.meta.env.BASE_URL}rom/CryMon.cdi?v=dc8`}
              download="CryMon.cdi"
              rel="noopener"
            >
              <Download className="size-4" />
              Dreamcast CDI
            </a>
          </div>
        </div>
      </header>

      <main className="mx-auto grid max-w-5xl gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[minmax(0,1fr)_220px]">
        <section className="flex flex-col items-center gap-4">
          <div className="relative w-full max-w-[960px] overflow-hidden rounded-lg border border-border bg-inset p-2 shadow-panel">
            <canvas
              ref={ref}
              className="mx-auto block h-auto w-full max-w-[960px] touch-none bg-bg"
              style={{ imageRendering: "pixelated", aspectRatio: "640 / 480" }}
              width={640}
              height={480}
            />
            {!ready && (
              <p className="absolute inset-0 grid place-items-center text-sm text-muted">Loading cart…</p>
            )}
          </div>

          <div className="flex w-full max-w-[960px] items-end justify-between gap-3 overflow-x-hidden">
            <Dpad
              onPad={(v) => {
                setPad(v);
                gameRef.current?.input.setPad(v.x, v.y);
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
              <span className="text-muted">Back / switch CryMon</span> X C Esc · 1 2 3 4 5 6
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

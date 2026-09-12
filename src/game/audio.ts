export class Chip {
  ctx: AudioContext | null = null;
  muted = false;

  unlock() {
    if (this.ctx) {
      void this.ctx.resume();
      return;
    }
    const C = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    this.ctx = new C();
  }

  private beep(freq: number, dur: number, type: OscillatorType, gain = 0.05) {
    if (this.muted) return;
    this.unlock();
    const ctx = this.ctx;
    if (!ctx) return;
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.type = type;
    o.frequency.value = freq;
    g.gain.value = gain;
    g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + dur);
    o.connect(g);
    g.connect(ctx.destination);
    o.start();
    o.stop(ctx.currentTime + dur);
  }

  ui() {
    this.beep(520, 0.05, "square", 0.03);
  }
  ok() {
    this.beep(720, 0.07, "square", 0.04);
    this.beep(980, 0.09, "square", 0.03);
  }
  hit() {
    this.beep(180, 0.09, "sawtooth", 0.05);
  }
  special() {
    this.beep(440, 0.06, "square", 0.04);
    this.beep(660, 0.1, "square", 0.04);
  }
  miss() {
    this.beep(140, 0.12, "triangle", 0.04);
  }
  catch() {
    this.beep(520, 0.08, "square", 0.04);
    this.beep(780, 0.12, "square", 0.04);
  }
  step() {
    this.beep(90, 0.03, "square", 0.02);
  }
}

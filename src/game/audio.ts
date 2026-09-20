import audioJson from "../../content/audio.json";

type Wave = "pulse" | "tri" | "noise";
type Ev = { n: number; f: number; v: number };
type Track = { wave: Wave; duty: number; vol: number; ev: Ev[] };
type Song = { loop: boolean; tracks: Track[] };

const NOTE_OFF: Record<string, number> = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };

export function parsePattern(pattern: string, defaultVol: number): Ev[] {
	const out: Ev[] = [];
	for (const raw of pattern.split(/\s+/).filter(Boolean)) {
		let tok = raw;
		let vol = defaultVol;
		if (tok.includes("@")) {
			const parts = tok.split("@");
			tok = parts[0];
			vol = Number(parts[1]) || defaultVol;
		}
		const [name, framesRaw] = tok.split(":");
		const frames = Math.max(1, Number(framesRaw) || 8);
		if (name === "r") {
			out.push({ n: 0, f: frames, v: 0 });
			continue;
		}
		if (name === "n") {
			out.push({ n: 1, f: frames, v: vol });
			continue;
		}
		const letter = name[0];
		let i = 1;
		let acc = 0;
		if (name[1] === "#") {
			acc = 1;
			i = 2;
		} else if (name[1] === "b") {
			acc = -1;
			i = 2;
		} else if (name[1] === "s") {
			acc = 1;
			i = 2;
		}
		const oct = Number(name.slice(i));
		const base = NOTE_OFF[letter];
		if (base === undefined || !Number.isFinite(oct)) {
			out.push({ n: 0, f: frames, v: 0 });
			continue;
		}
		out.push({ n: 12 * (oct + 1) + base + acc, f: frames, v: vol });
	}
	return out;
}

function compileTrack(t: { wave: string; duty: number; vol: number; pattern: string }): Track {
	return {
		wave: (t.wave as Wave) || "pulse",
		duty: t.duty ?? 2,
		vol: t.vol ?? 8,
		ev: parsePattern(t.pattern, t.vol ?? 8),
	};
}

function compileSong(s: { loop?: boolean; tracks: { wave: string; duty: number; vol: number; pattern: string }[] }): Song {
	return { loop: s.loop !== false, tracks: (s.tracks || []).map(compileTrack) };
}

const SONGS: Record<string, Song> = {};
for (const [k, v] of Object.entries(audioJson.songs as Record<string, { loop?: boolean; tracks: { wave: string; duty: number; vol: number; pattern: string }[] }>)) {
	SONGS[k] = compileSong(v);
}
const SFX: Record<string, Song> = {};
for (const [k, v] of Object.entries(audioJson.sfx as Record<string, { tracks: { wave: string; duty: number; vol: number; pattern: string }[] }>)) {
	SFX[k] = compileSong({ loop: false, tracks: v.tracks });
}

export const MAP_SONG = audioJson.mapSongs as Record<string, string>;
export const TITLE_SONG = audioJson.titleSong;
export const BATTLE_SONG = audioJson.battleSong;
export const TRAINER_SONG = audioJson.trainerSong;
export const ENDING_SONG = audioJson.endingSong;

const VOLUME_CFG = (audioJson as { volume?: { min: number; max: number; default: number; step: number; baseMaster: number } }).volume || {
	min: 0,
	max: 2,
	default: 1,
	step: 0.1,
	baseMaster: 0.9,
};
export const VOLUME = VOLUME_CFG;
const SETTINGS_KEY = "crymon.settings.v1";
const aj = audioJson as { musicBus?: number; sfxBus?: number; battleMusicMul?: number };
const MUSIC_BUS = aj.musicBus ?? 0.22;
const SFX_BUS = aj.sfxBus ?? 0.32;
const BATTLE_MUSIC_MUL = aj.battleMusicMul ?? 0.5;

function midiHz(n: number) {
	if (n <= 1) return 0;
	return 440 * Math.pow(2, (n - 69) / 12);
}

function pulseWave(ctx: AudioContext, duty: number) {
	const d = [0.125, 0.25, 0.5, 0.75][duty] ?? 0.5;
	const n = 32;
	const real = new Float32Array(n);
	const imag = new Float32Array(n);
	for (let k = 1; k < n; k++) imag[k] = (2 / (k * Math.PI)) * Math.sin(k * Math.PI * d);
	return ctx.createPeriodicWave(real, imag);
}

type Voice = {
	osc: OscillatorNode | AudioBufferSourceNode;
	gain: GainNode;
	wave: Wave;
	duty: number;
};

class Chan {
	i = 0;
	left = 0;
	song: Song | null = null;
	ch = 0;
}

export class Chip {
	ctx: AudioContext | null = null;
	muted = false;
	volume = VOLUME.default;
	master: GainNode | null = null;
	musicBus: GainNode | null = null;
	sfxBus: GainNode | null = null;
	voices: Voice[] = [];
	sfxVoices: Voice[] = [];
	noiseBuf: AudioBuffer | null = null;
	waves: PeriodicWave[] = [];
	songId: string | null = null;
	song: Song | null = null;
	music: Chan[] = [new Chan(), new Chan(), new Chan(), new Chan()];
	sfx: Chan[] = [new Chan(), new Chan()];
	acc = 0;
	playing = false;

	constructor() {
		this.loadSettings();
	}

	loadSettings() {
		try {
			const raw = localStorage.getItem(SETTINGS_KEY);
			if (!raw) return;
			const j = JSON.parse(raw) as { volume?: number };
			if (typeof j.volume === "number") this.volume = this.clampVolume(j.volume);
		} catch {
			/* ignore */
		}
	}

	saveSettings() {
		try {
			localStorage.setItem(SETTINGS_KEY, JSON.stringify({ volume: this.volume }));
		} catch {
			/* ignore */
		}
	}

	clampVolume(v: number) {
		const stepped = Math.round(v / VOLUME.step) * VOLUME.step;
		return Math.min(VOLUME.max, Math.max(VOLUME.min, Math.round(stepped * 100) / 100));
	}

	setVolume(v: number) {
		this.volume = this.clampVolume(v);
		this.applyMaster();
		this.saveSettings();
	}

	nudgeVolume(dir: number) {
		this.setVolume(this.volume + dir * VOLUME.step);
	}

	volumePct() {
		return Math.round(this.volume * 100);
	}

	private applyMaster() {
		if (!this.master || !this.ctx) return;
		const gain = this.muted ? 0.0001 : VOLUME.baseMaster * this.volume;
		this.master.gain.setTargetAtTime(gain, this.ctx.currentTime, 0.02);
	}

	unlock() {
		try {
			const C = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
			if (!this.ctx) {
				this.ctx = new C({ latencyHint: "interactive" });
				this.buildGraph();
			}
			if (this.ctx.state === "suspended") void this.ctx.resume();
		} catch {
			this.ctx = null;
		}
	}

	private buildGraph() {
		const ctx = this.ctx!;
		this.master = ctx.createGain();
		this.musicBus = ctx.createGain();
		this.sfxBus = ctx.createGain();
		this.musicBus.gain.value = this.musicGainFor(this.songId);
		this.sfxBus.gain.value = SFX_BUS;
		this.master.gain.value = this.muted ? 0 : VOLUME.baseMaster * this.volume;
		this.musicBus.connect(this.master);
		this.sfxBus.connect(this.master);
		this.master.connect(ctx.destination);
		this.noiseBuf = ctx.createBuffer(1, ctx.sampleRate, ctx.sampleRate);
		const data = this.noiseBuf.getChannelData(0);
		let ls = 0xace1;
		for (let i = 0; i < data.length; i++) {
			ls = (ls >> 1) ^ (ls & 1 ? 0x6000 : 0);
			data[i] = ((ls & 0xff) / 128 - 1) * 0.5;
		}
		this.waves = [0, 1, 2, 3].map((d) => pulseWave(ctx, d));
		this.voices = [0, 1, 2, 3].map((i) => this.makeVoice(i < 2 ? "pulse" : i === 2 ? "tri" : "noise", i === 0 ? 2 : i === 1 ? 1 : 0, this.musicBus!));
		this.sfxVoices = [0, 1].map(() => this.makeVoice("pulse", 2, this.sfxBus!));
	}

	private makeVoice(wave: Wave, duty: number, bus: GainNode): Voice {
		const ctx = this.ctx!;
		const gain = ctx.createGain();
		gain.gain.value = 0;
		gain.connect(bus);
		if (wave === "noise") {
			const osc = ctx.createBufferSource();
			osc.buffer = this.noiseBuf;
			osc.loop = true;
			osc.connect(gain);
			osc.start();
			return { osc, gain, wave, duty };
		}
		const osc = ctx.createOscillator();
		if (wave === "tri") osc.type = "triangle";
		else osc.setPeriodicWave(this.waves[duty] ?? this.waves[2]);
		osc.frequency.value = 440;
		osc.connect(gain);
		osc.start();
		return { osc, gain, wave, duty };
	}

	private retune(v: Voice, wave: Wave, duty: number) {
		if (v.wave === wave && (wave !== "pulse" || v.duty === duty)) return;
		const ctx = this.ctx!;
		const gain = v.gain;
		try {
			v.osc.stop();
			v.osc.disconnect();
		} catch {
			/* already stopped */
		}
		if (wave === "noise") {
			const osc = ctx.createBufferSource();
			osc.buffer = this.noiseBuf;
			osc.loop = true;
			osc.connect(gain);
			osc.start();
			v.osc = osc;
		} else {
			const osc = ctx.createOscillator();
			if (wave === "tri") osc.type = "triangle";
			else osc.setPeriodicWave(this.waves[duty] ?? this.waves[2]);
			osc.frequency.value = 440;
			osc.connect(gain);
			osc.start();
			v.osc = osc;
		}
		v.wave = wave;
		v.duty = duty;
	}

	private gate(v: Voice, hz: number, vol: number, noise: boolean) {
		const ctx = this.ctx!;
		const t = ctx.currentTime;
		const g = v.gain.gain;
		if (vol <= 0 || (!noise && hz <= 0)) {
			g.setTargetAtTime(0.0001, t, 0.008);
			return;
		}
		if (!noise && v.osc instanceof OscillatorNode) v.osc.frequency.setValueAtTime(hz, t);
		else if (noise && v.osc instanceof AudioBufferSourceNode) v.osc.playbackRate.setValueAtTime(0.6 + Math.min(3, hz / 400), t);
		const amp = (vol / 15) * 0.22;
		g.setTargetAtTime(Math.max(0.0001, amp), t, 0.004);
	}

	private stepChan(ch: Chan, voices: Voice[], idx: number) {
		if (!ch.song) {
			if (voices[idx]) this.gate(voices[idx], 0, 0, false);
			return;
		}
		const tr = ch.song.tracks[idx];
		if (!tr || !tr.ev.length) {
			if (voices[idx]) this.gate(voices[idx], 0, 0, false);
			return;
		}
		if (ch.left > 0) {
			ch.left -= 1;
			return;
		}
		if (ch.i >= tr.ev.length) {
			if (ch.song.loop) ch.i = 0;
			else {
				ch.song = null;
				if (voices[idx]) this.gate(voices[idx], 0, 0, false);
				return;
			}
		}
		const ev = tr.ev[ch.i++];
		ch.left = Math.max(0, ev.f - 1);
		const v = voices[idx];
		if (!v) return;
		this.retune(v, tr.wave, tr.duty);
		this.gate(v, midiHz(ev.n), ev.v, tr.wave === "noise");
	}

	private musicGainFor(id: string | null) {
		const battle = id === BATTLE_SONG || id === TRAINER_SONG;
		return MUSIC_BUS * (battle ? BATTLE_MUSIC_MUL : 1);
	}

	setSong(id: string | null) {
		if (id === this.songId) {
			if (this.musicBus) this.musicBus.gain.value = this.musicGainFor(id);
			return;
		}
		this.songId = id;
		this.song = id ? SONGS[id] ?? null : null;
		if (this.musicBus) this.musicBus.gain.value = this.musicGainFor(id);
		for (let i = 0; i < 4; i++) {
			this.music[i].song = this.song;
			this.music[i].i = 0;
			this.music[i].left = 0;
			this.music[i].ch = i;
		}
	}

	playSfx(name: string) {
		if (this.muted) return;
		this.unlock();
		if (!this.ctx) return;
		const s = SFX[name];
		if (!s) return;
		for (let i = 0; i < this.sfx.length; i++) {
			this.sfx[i].song = s;
			this.sfx[i].i = 0;
			this.sfx[i].left = 0;
			this.sfx[i].ch = i;
		}
	}

	tick(dt: number) {
		try {
			if (this.master && this.ctx) this.applyMaster();
			if (!this.ctx || this.ctx.state === "suspended") return;
			this.acc += dt;
			const step = 1 / 60;
			while (this.acc >= step) {
				this.acc -= step;
				for (let i = 0; i < 4; i++) this.stepChan(this.music[i], this.voices, i);
				for (let i = 0; i < 2; i++) this.stepChan(this.sfx[i], this.sfxVoices, i);
			}
		} catch {
			/* keep the game loop alive if a voice node died */
		}
	}

	ui() {
		this.playSfx("ui");
	}
	ok() {
		this.playSfx("ok");
	}
	hit() {
		this.playSfx("hit");
	}
	special() {
		this.playSfx("special");
	}
	miss() {
		this.playSfx("miss");
	}
	catch() {
		this.playSfx("catch");
	}
	save() {
		this.playSfx("save");
	}
	heal() {
		this.playSfx("heal");
	}
	faint() {
		this.playSfx("faint");
	}
	scream() {
		this.playSfx("scream");
	}
	step() {
		/* footsteps stay silent — GBA overworlds rarely tick every tile */
	}
}

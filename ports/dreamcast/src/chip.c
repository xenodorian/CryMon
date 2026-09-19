/* GBA-style 4-channel tracker. Data is content/audio.json via content_audio.inc.
 * Playback is AICA PCM looped waveforms (pulse/tri/noise) pitched per note.
 * Same interpreter as src/game/audio.ts — do not fork the event format. */
#include <stdint.h>
#include "chip.h"
#include "content_audio.inc"

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

#define AICA_BASE   0xa0700000u
#define SNDRAM      0xa0800000u
#define G2_FIFO     (*(volatile u32 *)0xa05f688cu)

#define WAVE_LEN    32
#define NOISE_LEN   2048
#define ADDR_PULSE  0x0000
#define ADDR_TRI    (ADDR_PULSE + 4 * WAVE_LEN * 2)
#define ADDR_NOISE  (ADDR_TRI + WAVE_LEN * 2)

static void g2_wait(void) {
    int i;
    for(i = 0; i < 0x1800; i++) {
        if((G2_FIFO & 0x11u) == 0)
            return;
    }
}

static void g2_w32(u32 addr, u32 v) {
    g2_wait();
    *(volatile u32 *)addr = v;
}

static void g2_w16(u32 addr, u16 v) {
    g2_wait();
    *(volatile u16 *)addr = v;
}

static u32 aica_pitch(int hz) {
    int rate, oct, fns;
    if(hz < 8) hz = 8;
    if(hz > 12000) hz = 12000;
    rate = WAVE_LEN * hz;
    oct = 0;
    while(rate < 44100 && oct > -8) { rate *= 2; oct--; }
    while(rate >= 88200 && oct < 7) { rate /= 2; oct++; }
    fns = (int)(((u32)rate * 1024u) / 44100u) - 1024;
    if(fns < 0) fns = 0;
    if(fns > 0x3ff) fns = 0x3ff;
    return ((u32)(oct & 0xf) << 11) | (u32)(fns & 0x7ff);
}

static int midi_hz(int midi) {
    /* 440 * 2^((n-69)/12) as integer via a small table around A4. */
    static const u16 hz_a[12] = { 440, 466, 494, 523, 554, 587, 622, 659, 698, 740, 784, 831 };
    int rel, oct, base, i;
    if(midi <= 1) return 0;
    rel = midi - 69;
    oct = 0;
    while(rel < 0) { rel += 12; oct--; }
    while(rel >= 12) { rel -= 12; oct++; }
    base = hz_a[rel];
    if(oct > 0) {
        for(i = 0; i < oct; i++) base *= 2;
    } else if(oct < 0) {
        for(i = 0; i < -oct; i++) base /= 2;
        if(base < 8) base = 8;
    }
    return base;
}

static void aica_upload_waves(void) {
    int d, i, bit, duty;
    u16 *dst;
    u32 lfsr = 0xace1u;
    static const int duties[4] = { 4, 8, 16, 24 }; /* of 32 */
    for(d = 0; d < 4; d++) {
        duty = duties[d];
        dst = (u16 *)(SNDRAM + ADDR_PULSE + d * WAVE_LEN * 2);
        for(i = 0; i < WAVE_LEN; i++) {
            g2_w16((u32)(dst + i), (u16)(i < duty ? 12000 : (u16)-12000));
        }
    }
    dst = (u16 *)(SNDRAM + ADDR_TRI);
    for(i = 0; i < WAVE_LEN; i++) {
        int t = (i < 16) ? (i * 4000 - 32000) : ((32 - i) * 4000 - 32000);
        g2_w16((u32)(dst + i), (u16)t);
    }
    dst = (u16 *)(SNDRAM + ADDR_NOISE);
    for(i = 0; i < NOISE_LEN; i++) {
        bit = lfsr & 1u;
        lfsr = (lfsr >> 1) ^ (bit ? 0x6000u : 0);
        g2_w16((u32)(dst + i), (u16)(bit ? 10000 : (u16)-10000));
    }
}

static void aica_ch_setup(int ch, u32 ram_off, int loop_samples) {
    u32 base = AICA_BASE + (u32)ch * 0x80u;
    g2_w32(base + 0x00, 0);
    g2_w32(base + 0x04, ram_off >> 1);
    g2_w32(base + 0x08, 0);
    g2_w32(base + 0x0c, (u32)loop_samples);
    g2_w32(base + 0x10, aica_pitch(440));
    g2_w32(base + 0x14, 0x1f);
    g2_w32(base + 0x18, 0x1f);
    g2_w32(base + 0x1c, 0);
    g2_w32(base + 0x20, 0);
    g2_w32(base + 0x24, 0x00ff); /* silent, center-ish pan */
    g2_w32(base + 0x00, 0x4000 | 0x8000); /* 16-bit PCM, loop, key-on */
}

static u8 last_wave[8];
static u8 last_duty[8];

static void aica_ch_wave(int ch, int wave, int duty) {
    u32 base = AICA_BASE + (u32)ch * 0x80u;
    u32 off;
    int len = WAVE_LEN;
    if(last_wave[ch] == (u8)wave && last_duty[ch] == (u8)duty) return;
    last_wave[ch] = (u8)wave;
    last_duty[ch] = (u8)duty;
    if(wave == 2) {
        off = ADDR_NOISE;
        len = NOISE_LEN;
    } else if(wave == 1) {
        off = ADDR_TRI;
    } else {
        off = ADDR_PULSE + (u32)(duty & 3) * WAVE_LEN * 2;
    }
    g2_w32(base + 0x04, off >> 1);
    g2_w32(base + 0x08, 0);
    g2_w32(base + 0x0c, (u32)len);
}

static void aica_ch_vol_pitch(int ch, int hz, int vol) {
    u32 base = AICA_BASE + (u32)ch * 0x80u;
    u32 atten;
    if(vol <= 0 || hz <= 0) {
        g2_w32(base + 0x24, 0x00ff);
        return;
    }
    {
        float scaled = (float)vol * vol_scale;
        int atten_i;
        if(scaled <= 0.0f) {
            g2_w32(base + 0x24, 0x00ff);
            return;
        }
        atten_i = (int)((15.0f - scaled) * 8.0f);
        if(atten_i < 0) atten_i = 0;
        if(atten_i > 0xff) atten_i = 0xff;
        atten = (u32)atten_i;
    }
    g2_w32(base + 0x10, aica_pitch(hz));
    g2_w32(base + 0x24, (atten << 8) | 0x80);
}

static void aica_keyex(void) {
    g2_w32(0xa0702800u, 1);
}

typedef struct {
    const ChipSong *song;
    int i[4];
    int left[4];
} ChipPlay;

static ChipPlay music;
static ChipPlay sfx;
static int cur_song = -1;
static int inited;
static float vol_scale = VOL_DEFAULT;

void chip_set_volume(float v) {
    if(v < VOL_MIN) v = VOL_MIN;
    if(v > VOL_MAX) v = VOL_MAX;
    vol_scale = v;
}

void chip_nudge_volume(int dir) {
    chip_set_volume(vol_scale + (dir > 0 ? VOL_STEP : -VOL_STEP));
}

float chip_volume(void) {
    return vol_scale;
}

int chip_volume_pct(void) {
    int p = (int)(vol_scale * 100.0f + 0.5f);
    if(p < 0) p = 0;
    return p;
}

int chip_volume_fill(int bar_w) {
    int fill = (int)((float)bar_w * (vol_scale / VOL_MAX) + 0.5f);
    if(fill < 0) fill = 0;
    if(fill > bar_w) fill = bar_w;
    return fill;
}

static void play_reset(ChipPlay *p, const ChipSong *song) {
    int c;
    p->song = song;
    for(c = 0; c < 4; c++) {
        p->i[c] = 0;
        p->left[c] = 0;
    }
}

static void play_step(ChipPlay *p, int voice0, int nvoice) {
    int c;
    if(!p->song) {
        for(c = 0; c < nvoice; c++)
            aica_ch_vol_pitch(voice0 + c, 0, 0);
        return;
    }
    for(c = 0; c < nvoice && c < p->song->ntr; c++) {
        const ChipTrack *tr = &p->song->tr[c];
        const ChipEv *ev;
        int hz, vol;
        if(p->left[c] > 0) {
            p->left[c]--;
            continue;
        }
        if(p->i[c] >= tr->n) {
            if(p->song->loop)
                p->i[c] = 0;
            else {
                aica_ch_vol_pitch(voice0 + c, 0, 0);
                continue;
            }
        }
        ev = &tr->ev[p->i[c]++];
        p->left[c] = ev->frames ? (int)ev->frames - 1 : 0;
        aica_ch_wave(voice0 + c, tr->wave, tr->duty);
        vol = ev->vol;
        if(tr->wave == 2) {
            hz = vol > 0 ? 800 : 0;
        } else {
            hz = midi_hz(ev->midi);
        }
        aica_ch_vol_pitch(voice0 + c, hz, vol);
    }
}

void chip_init(void) {
    int ch;
    g2_w32(0xa0702c00u, 1); /* hold ARM in reset so SH4 owns channels */
    aica_upload_waves();
    for(ch = 0; ch < 8; ch++) {
        last_wave[ch] = 0xff;
        last_duty[ch] = 0xff;
    }
    for(ch = 0; ch < 4; ch++)
        aica_ch_setup(ch, ADDR_PULSE + (u32)(ch == 0 ? 2 : 1) * WAVE_LEN * 2, WAVE_LEN);
    aica_ch_setup(2, ADDR_TRI, WAVE_LEN);
    aica_ch_setup(3, ADDR_NOISE, NOISE_LEN);
    /* sfx overlay voices 4-5 */
    aica_ch_setup(4, ADDR_PULSE + 2 * WAVE_LEN * 2, WAVE_LEN);
    aica_ch_setup(5, ADDR_NOISE, NOISE_LEN);
    aica_keyex();
    play_reset(&music, 0);
    play_reset(&sfx, 0);
    cur_song = -1;
    inited = 1;
}

void chip_set_song(int id) {
    if(!inited) return;
    if(id == cur_song) return;
    cur_song = id;
    if(id < 0 || id >= SONG_N)
        play_reset(&music, 0);
    else
        play_reset(&music, &CHIP_SONGS[id]);
}

void chip_sfx(int id) {
    if(!inited) return;
    if(id < 0 || id >= SFX_N) return;
    play_reset(&sfx, &CHIP_SFX[id]);
}

void chip_tick(void) {
    int c;
    if(!inited) return;
    play_step(&music, 0, 4);
    if(sfx.song) {
        int alive = 0;
        play_step(&sfx, 4, 2);
        for(c = 0; c < sfx.song->ntr && c < 2; c++) {
            if(sfx.i[c] < sfx.song->tr[c].n || sfx.left[c] > 0)
                alive = 1;
        }
        if(!alive && !sfx.song->loop)
            sfx.song = 0;
    }
}

void chip_sfx_ui(void) { chip_sfx(SFX_UI); }
void chip_sfx_ok(void) { chip_sfx(SFX_OK); }
void chip_sfx_miss(void) { chip_sfx(SFX_MISS); }
void chip_sfx_hit(void) { chip_sfx(SFX_HIT); }
void chip_sfx_special(void) { chip_sfx(SFX_SPECIAL); }
void chip_sfx_catch(void) { chip_sfx(SFX_CATCH); }
void chip_sfx_save(void) { chip_sfx(SFX_SAVE); }
void chip_sfx_heal(void) { chip_sfx(SFX_HEAL); }
void chip_sfx_faint(void) { chip_sfx(SFX_FAINT); }

int chip_song_title(void) { return SONG_ID_TITLE; }
int chip_song_ending(void) { return SONG_ID_ENDING; }
int chip_song_battle(int trainer) { return trainer ? SONG_ID_TRAINER : SONG_ID_BATTLE; }
int chip_song_map(int map_id) {
    if(map_id < 0 || map_id >= MAP_SONG_N) return SONG_ID_TITLE;
    return MAP_SONG[map_id];
}


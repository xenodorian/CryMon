/* AUTO-GENERATED from content/*.json PACK_HASH=3e1a9f8c8c87c0ba — do not edit. python3 tools/bake_content.py */

#ifndef CONTENT_AUDIO_INC
#define CONTENT_AUDIO_INC

typedef struct { unsigned char midi, frames, vol; } ChipEv;
typedef struct {
    unsigned char wave, duty, vol;
    const ChipEv *ev;
    int n;
} ChipTrack;
typedef struct { const ChipTrack *tr; int ntr; int loop; } ChipSong;

#define SONG_TITLE 0
#define SONG_HOME 1
#define SONG_OVERWORLD 2
#define SONG_WILDS 3
#define SONG_OCCUPATION 4
#define SONG_BATTLE 5
#define SONG_BOSS 6
#define SONG_N 7

#define SFX_UI 0
#define SFX_OK 1
#define SFX_MISS 2
#define SFX_HIT 3
#define SFX_SPECIAL 4
#define SFX_CATCH 5
#define SFX_SAVE 6
#define SFX_HEAL 7
#define SFX_FAINT 8
#define SFX_SCREAM 9
#define SFX_N 10

static const ChipEv song_title_t0[] = {
    { 64, 20, 11 },
    { 67, 20, 11 },
    { 71, 20, 11 },
    { 76, 20, 11 },
    { 74, 20, 11 },
    { 71, 20, 11 },
    { 67, 20, 11 },
    { 62, 20, 11 },
    { 64, 20, 11 },
    { 67, 20, 11 },
    { 69, 20, 11 },
    { 71, 20, 11 },
    { 67, 40, 11 },
    { 64, 40, 11 },
};
static const ChipEv song_title_t1[] = {
    { 52, 40, 6 },
    { 59, 40, 6 },
    { 55, 40, 6 },
    { 52, 40, 6 },
    { 47, 40, 6 },
    { 50, 40, 6 },
    { 52, 40, 6 },
    { 47, 40, 6 },
};
static const ChipEv song_title_t2[] = {
    { 40, 80, 8 },
    { 47, 80, 8 },
    { 43, 80, 8 },
    { 40, 80, 8 },
};
static const ChipEv song_title_t3[] = {
    { 0, 36, 0 },
    { 1, 4, 4 },
    { 0, 36, 0 },
    { 1, 4, 4 },
    { 0, 36, 0 },
    { 1, 4, 4 },
    { 0, 36, 0 },
    { 1, 4, 4 },
    { 0, 36, 0 },
    { 1, 4, 4 },
    { 0, 36, 0 },
    { 1, 4, 4 },
    { 0, 36, 0 },
    { 1, 4, 4 },
    { 0, 36, 0 },
    { 1, 4, 4 },
};
static const ChipTrack song_title_tr[] = {
    { 0, 2, 11, song_title_t0, 14 },
    { 0, 1, 6, song_title_t1, 8 },
    { 1, 0, 8, song_title_t2, 4 },
    { 2, 0, 4, song_title_t3, 16 },
};

static const ChipEv song_home_t0[] = {
    { 67, 40, 8 },
    { 62, 40, 8 },
    { 63, 40, 8 },
    { 62, 40, 8 },
    { 58, 40, 8 },
    { 60, 40, 8 },
    { 62, 40, 8 },
    { 67, 40, 8 },
};
static const ChipEv song_home_t1[] = {
    { 55, 80, 5 },
    { 50, 80, 5 },
    { 51, 80, 5 },
    { 55, 80, 5 },
};
static const ChipEv song_home_t2[] = {
    { 43, 160, 7 },
    { 38, 160, 7 },
};
static const ChipEv song_home_t3[] = {
    { 0, 320, 0 },
};
static const ChipTrack song_home_tr[] = {
    { 0, 1, 8, song_home_t0, 8 },
    { 0, 2, 5, song_home_t1, 4 },
    { 1, 0, 7, song_home_t2, 2 },
    { 2, 0, 2, song_home_t3, 1 },
};

static const ChipEv song_overworld_t0[] = {
    { 69, 10, 11 },
    { 72, 10, 11 },
    { 76, 20, 11 },
    { 74, 10, 11 },
    { 72, 10, 11 },
    { 69, 20, 11 },
    { 67, 10, 11 },
    { 69, 10, 11 },
    { 72, 20, 11 },
    { 71, 20, 11 },
    { 69, 20, 11 },
    { 69, 10, 11 },
    { 72, 10, 11 },
    { 76, 20, 11 },
    { 79, 10, 11 },
    { 76, 10, 11 },
    { 74, 20, 11 },
    { 72, 20, 11 },
    { 71, 20, 11 },
    { 69, 40, 11 },
};
static const ChipEv song_overworld_t1[] = {
    { 57, 20, 6 },
    { 52, 20, 6 },
    { 57, 20, 6 },
    { 60, 20, 6 },
    { 55, 20, 6 },
    { 50, 20, 6 },
    { 55, 20, 6 },
    { 59, 20, 6 },
    { 57, 40, 6 },
    { 52, 40, 6 },
    { 57, 40, 6 },
    { 52, 40, 6 },
};
static const ChipEv song_overworld_t2[] = {
    { 45, 40, 9 },
    { 40, 40, 9 },
    { 45, 40, 9 },
    { 43, 40, 9 },
    { 45, 80, 9 },
    { 40, 80, 9 },
};
static const ChipEv song_overworld_t3[] = {
    { 1, 2, 5 },
    { 0, 8, 0 },
    { 1, 2, 5 },
    { 0, 8, 0 },
    { 1, 2, 5 },
    { 0, 18, 0 },
    { 1, 2, 5 },
    { 0, 8, 0 },
    { 1, 2, 5 },
    { 0, 8, 0 },
    { 1, 2, 5 },
    { 0, 18, 0 },
    { 1, 2, 5 },
    { 0, 8, 0 },
    { 1, 2, 5 },
    { 0, 8, 0 },
    { 1, 2, 5 },
    { 0, 18, 0 },
    { 1, 2, 5 },
    { 0, 8, 0 },
    { 1, 2, 5 },
    { 0, 8, 0 },
    { 1, 2, 5 },
    { 0, 18, 0 },
    { 1, 2, 5 },
    { 0, 8, 0 },
    { 1, 2, 5 },
    { 0, 8, 0 },
    { 1, 2, 5 },
    { 0, 18, 0 },
    { 1, 2, 5 },
    { 0, 8, 0 },
    { 1, 2, 5 },
    { 0, 8, 0 },
    { 1, 2, 5 },
    { 0, 18, 0 },
    { 1, 2, 5 },
    { 0, 8, 0 },
    { 1, 2, 5 },
    { 0, 8, 0 },
    { 1, 2, 5 },
    { 0, 18, 0 },
    { 1, 2, 5 },
    { 0, 8, 0 },
    { 1, 2, 5 },
    { 0, 8, 0 },
    { 1, 2, 5 },
    { 0, 18, 0 },
};
static const ChipTrack song_overworld_tr[] = {
    { 0, 2, 11, song_overworld_t0, 20 },
    { 0, 1, 6, song_overworld_t1, 12 },
    { 1, 0, 9, song_overworld_t2, 6 },
    { 2, 0, 5, song_overworld_t3, 48 },
};

static const ChipEv song_wilds_t0[] = {
    { 62, 30, 10 },
    { 65, 10, 10 },
    { 69, 20, 10 },
    { 67, 20, 10 },
    { 62, 20, 10 },
    { 60, 20, 10 },
    { 57, 40, 10 },
    { 65, 20, 10 },
    { 67, 20, 10 },
    { 69, 40, 10 },
    { 67, 20, 10 },
    { 65, 20, 10 },
    { 62, 40, 10 },
};
static const ChipEv song_wilds_t1[] = {
    { 50, 80, 5 },
    { 45, 80, 5 },
    { 53, 80, 5 },
    { 50, 80, 5 },
};
static const ChipEv song_wilds_t2[] = {
    { 38, 160, 8 },
    { 33, 160, 8 },
};
static const ChipEv song_wilds_t3[] = {
    { 0, 28, 0 },
    { 1, 4, 3 },
    { 0, 8, 0 },
    { 0, 28, 0 },
    { 1, 4, 3 },
    { 0, 8, 0 },
    { 0, 28, 0 },
    { 1, 4, 3 },
    { 0, 8, 0 },
    { 0, 28, 0 },
    { 1, 4, 3 },
    { 0, 8, 0 },
    { 0, 28, 0 },
    { 1, 4, 3 },
    { 0, 8, 0 },
    { 0, 28, 0 },
    { 1, 4, 3 },
    { 0, 8, 0 },
    { 0, 28, 0 },
    { 1, 4, 3 },
    { 0, 8, 0 },
    { 0, 28, 0 },
    { 1, 4, 3 },
    { 0, 8, 0 },
};
static const ChipTrack song_wilds_tr[] = {
    { 0, 1, 10, song_wilds_t0, 13 },
    { 0, 2, 5, song_wilds_t1, 4 },
    { 1, 0, 8, song_wilds_t2, 2 },
    { 2, 0, 3, song_wilds_t3, 24 },
};

static const ChipEv song_occupation_t0[] = {
    { 64, 8, 11 },
    { 64, 8, 11 },
    { 64, 8, 11 },
    { 0, 8, 0 },
    { 67, 16, 11 },
    { 71, 16, 11 },
    { 64, 8, 11 },
    { 64, 8, 11 },
    { 64, 8, 11 },
    { 0, 8, 0 },
    { 62, 16, 11 },
    { 59, 16, 11 },
    { 67, 8, 11 },
    { 67, 8, 11 },
    { 67, 8, 11 },
    { 0, 8, 0 },
    { 71, 16, 11 },
    { 76, 16, 11 },
    { 71, 16, 11 },
    { 67, 16, 11 },
    { 64, 32, 11 },
};
static const ChipEv song_occupation_t1[] = {
    { 52, 16, 6 },
    { 47, 16, 6 },
    { 52, 16, 6 },
    { 50, 16, 6 },
    { 52, 16, 6 },
    { 47, 16, 6 },
    { 52, 16, 6 },
    { 55, 16, 6 },
    { 52, 16, 6 },
    { 47, 16, 6 },
    { 52, 16, 6 },
    { 50, 16, 6 },
    { 52, 32, 6 },
    { 47, 32, 6 },
};
static const ChipEv song_occupation_t2[] = {
    { 40, 32, 9 },
    { 35, 32, 9 },
    { 40, 32, 9 },
    { 38, 32, 9 },
    { 40, 32, 9 },
    { 35, 32, 9 },
    { 40, 32, 9 },
    { 43, 32, 9 },
};
static const ChipEv song_occupation_t3[] = {
    { 1, 4, 6 },
    { 0, 12, 0 },
    { 1, 4, 6 },
    { 0, 12, 0 },
    { 1, 4, 6 },
    { 0, 12, 0 },
    { 1, 4, 6 },
    { 0, 12, 0 },
    { 1, 4, 6 },
    { 0, 12, 0 },
    { 1, 4, 6 },
    { 0, 12, 0 },
    { 1, 4, 6 },
    { 0, 12, 0 },
    { 1, 4, 6 },
    { 0, 12, 0 },
    { 1, 4, 6 },
    { 0, 12, 0 },
    { 1, 4, 6 },
    { 0, 12, 0 },
    { 1, 4, 6 },
    { 0, 12, 0 },
    { 1, 4, 6 },
    { 0, 12, 0 },
    { 1, 4, 6 },
    { 0, 12, 0 },
    { 1, 4, 6 },
    { 0, 12, 0 },
    { 1, 4, 6 },
    { 0, 12, 0 },
    { 1, 4, 6 },
    { 0, 12, 0 },
};
static const ChipTrack song_occupation_tr[] = {
    { 0, 2, 11, song_occupation_t0, 21 },
    { 0, 0, 6, song_occupation_t1, 14 },
    { 1, 0, 9, song_occupation_t2, 8 },
    { 2, 0, 6, song_occupation_t3, 32 },
};

static const ChipEv song_battle_t0[] = {
    { 76, 5, 12 },
    { 79, 5, 12 },
    { 83, 5, 12 },
    { 88, 5, 12 },
    { 86, 5, 12 },
    { 83, 5, 12 },
    { 79, 5, 12 },
    { 74, 5, 12 },
    { 76, 5, 12 },
    { 79, 5, 12 },
    { 83, 5, 12 },
    { 86, 5, 12 },
    { 88, 5, 12 },
    { 86, 5, 12 },
    { 83, 5, 12 },
    { 79, 5, 12 },
    { 72, 5, 12 },
    { 76, 5, 12 },
    { 79, 5, 12 },
    { 84, 5, 12 },
    { 83, 5, 12 },
    { 79, 5, 12 },
    { 76, 5, 12 },
    { 72, 5, 12 },
    { 74, 5, 12 },
    { 77, 5, 12 },
    { 81, 5, 12 },
    { 86, 5, 12 },
    { 84, 5, 12 },
    { 81, 5, 12 },
    { 77, 5, 12 },
    { 74, 5, 12 },
};
static const ChipEv song_battle_t1[] = {
    { 64, 10, 7 },
    { 59, 10, 7 },
    { 64, 10, 7 },
    { 62, 10, 7 },
    { 60, 10, 7 },
    { 55, 10, 7 },
    { 60, 10, 7 },
    { 59, 10, 7 },
    { 62, 10, 7 },
    { 57, 10, 7 },
    { 62, 10, 7 },
    { 60, 10, 7 },
    { 64, 20, 7 },
    { 59, 20, 7 },
};
static const ChipEv song_battle_t2[] = {
    { 40, 20, 10 },
    { 35, 20, 10 },
    { 36, 20, 10 },
    { 31, 20, 10 },
    { 38, 20, 10 },
    { 33, 20, 10 },
    { 40, 20, 10 },
    { 35, 20, 10 },
};
static const ChipEv song_battle_t3[] = {
    { 1, 2, 7 },
    { 0, 6, 0 },
    { 1, 2, 7 },
    { 0, 6, 0 },
    { 1, 2, 7 },
    { 0, 6, 0 },
    { 1, 2, 7 },
    { 0, 6, 0 },
    { 1, 2, 7 },
    { 0, 6, 0 },
    { 1, 2, 7 },
    { 0, 6, 0 },
    { 1, 2, 7 },
    { 0, 6, 0 },
    { 1, 2, 7 },
    { 0, 6, 0 },
    { 1, 2, 7 },
    { 0, 6, 0 },
    { 1, 2, 7 },
    { 0, 6, 0 },
    { 1, 2, 7 },
    { 0, 6, 0 },
    { 1, 2, 7 },
    { 0, 6, 0 },
    { 1, 2, 7 },
    { 0, 6, 0 },
    { 1, 2, 7 },
    { 0, 6, 0 },
    { 1, 2, 7 },
    { 0, 6, 0 },
    { 1, 2, 7 },
    { 0, 6, 0 },
    { 1, 2, 7 },
    { 0, 6, 0 },
    { 1, 2, 7 },
    { 0, 6, 0 },
    { 1, 2, 7 },
    { 0, 6, 0 },
    { 1, 2, 7 },
    { 0, 6, 0 },
};
static const ChipTrack song_battle_tr[] = {
    { 0, 2, 12, song_battle_t0, 32 },
    { 0, 1, 7, song_battle_t1, 14 },
    { 1, 0, 10, song_battle_t2, 8 },
    { 2, 0, 7, song_battle_t3, 40 },
};

static const ChipEv song_boss_t0[] = {
    { 76, 4, 12 },
    { 77, 4, 12 },
    { 79, 4, 12 },
    { 80, 4, 12 },
    { 81, 4, 12 },
    { 80, 4, 12 },
    { 79, 4, 12 },
    { 77, 4, 12 },
    { 76, 4, 12 },
    { 79, 4, 12 },
    { 83, 4, 12 },
    { 88, 4, 12 },
    { 87, 4, 12 },
    { 83, 4, 12 },
    { 79, 4, 12 },
    { 75, 4, 12 },
    { 76, 4, 12 },
    { 77, 4, 12 },
    { 79, 4, 12 },
    { 83, 4, 12 },
    { 88, 8, 12 },
    { 83, 8, 12 },
    { 79, 4, 12 },
    { 81, 4, 12 },
    { 83, 4, 12 },
    { 86, 4, 12 },
    { 88, 8, 12 },
    { 86, 8, 12 },
    { 83, 16, 12 },
    { 0, 16, 0 },
};
static const ChipEv song_boss_t1[] = {
    { 52, 8, 8 },
    { 58, 8, 8 },
    { 52, 8, 8 },
    { 59, 8, 8 },
    { 52, 8, 8 },
    { 58, 8, 8 },
    { 52, 8, 8 },
    { 62, 8, 8 },
    { 52, 8, 8 },
    { 58, 8, 8 },
    { 52, 8, 8 },
    { 59, 8, 8 },
    { 52, 8, 8 },
    { 55, 8, 8 },
    { 59, 8, 8 },
    { 64, 8, 8 },
    { 0, 32, 0 },
};
static const ChipEv song_boss_t2[] = {
    { 40, 16, 11 },
    { 34, 16, 11 },
    { 40, 16, 11 },
    { 35, 16, 11 },
    { 40, 16, 11 },
    { 34, 16, 11 },
    { 40, 16, 11 },
    { 38, 16, 11 },
    { 0, 32, 0 },
};
static const ChipEv song_boss_t3[] = {
    { 1, 2, 8 },
    { 0, 2, 0 },
    { 1, 2, 8 },
    { 0, 2, 0 },
    { 1, 4, 8 },
    { 0, 4, 0 },
    { 1, 2, 8 },
    { 0, 2, 0 },
    { 1, 2, 8 },
    { 0, 2, 0 },
    { 1, 4, 8 },
    { 0, 4, 0 },
    { 1, 2, 8 },
    { 0, 2, 0 },
    { 1, 2, 8 },
    { 0, 2, 0 },
    { 1, 4, 8 },
    { 0, 4, 0 },
    { 1, 2, 8 },
    { 0, 2, 0 },
    { 1, 2, 8 },
    { 0, 2, 0 },
    { 1, 4, 8 },
    { 0, 4, 0 },
    { 1, 2, 8 },
    { 0, 2, 0 },
    { 1, 2, 8 },
    { 0, 2, 0 },
    { 1, 4, 8 },
    { 0, 4, 0 },
    { 1, 2, 8 },
    { 0, 2, 0 },
    { 1, 2, 8 },
    { 0, 2, 0 },
    { 1, 4, 8 },
    { 0, 4, 0 },
    { 1, 2, 8 },
    { 0, 2, 0 },
    { 1, 2, 8 },
    { 0, 2, 0 },
    { 1, 4, 8 },
    { 0, 4, 0 },
    { 1, 2, 8 },
    { 0, 2, 0 },
    { 1, 2, 8 },
    { 0, 2, 0 },
    { 1, 4, 8 },
    { 0, 4, 0 },
    { 1, 2, 8 },
    { 0, 2, 0 },
    { 1, 2, 8 },
    { 0, 2, 0 },
    { 1, 4, 8 },
    { 0, 4, 0 },
    { 1, 2, 8 },
    { 0, 2, 0 },
    { 1, 2, 8 },
    { 0, 2, 0 },
    { 1, 4, 8 },
    { 0, 4, 0 },
};
static const ChipTrack song_boss_tr[] = {
    { 0, 2, 12, song_boss_t0, 30 },
    { 0, 0, 8, song_boss_t1, 17 },
    { 1, 0, 11, song_boss_t2, 9 },
    { 2, 0, 8, song_boss_t3, 60 },
};

static const ChipEv sfx_ui_t0[] = {
    { 84, 3, 8 },
};
static const ChipTrack sfx_ui_tr[] = {
    { 0, 2, 8, sfx_ui_t0, 1 },
};

static const ChipEv sfx_ok_t0[] = {
    { 72, 4, 9 },
    { 76, 4, 9 },
    { 79, 6, 9 },
};
static const ChipTrack sfx_ok_tr[] = {
    { 0, 2, 9, sfx_ok_t0, 3 },
};

static const ChipEv sfx_miss_t0[] = {
    { 55, 6, 8 },
    { 50, 10, 8 },
};
static const ChipEv sfx_miss_t1[] = {
    { 1, 8, 4 },
    { 0, 8, 0 },
};
static const ChipTrack sfx_miss_tr[] = {
    { 0, 1, 8, sfx_miss_t0, 2 },
    { 2, 0, 4, sfx_miss_t1, 2 },
};

static const ChipEv sfx_hit_t0[] = {
    { 1, 5, 10 },
    { 0, 3, 0 },
};
static const ChipEv sfx_hit_t1[] = {
    { 52, 3, 8 },
    { 48, 6, 8 },
};
static const ChipTrack sfx_hit_tr[] = {
    { 2, 0, 10, sfx_hit_t0, 2 },
    { 0, 0, 8, sfx_hit_t1, 2 },
};

static const ChipEv sfx_special_t0[] = {
    { 72, 3, 10 },
    { 76, 3, 10 },
    { 79, 3, 10 },
    { 84, 8, 10 },
};
static const ChipTrack sfx_special_tr[] = {
    { 0, 2, 10, sfx_special_t0, 4 },
};

static const ChipEv sfx_catch_t0[] = {
    { 72, 4, 10 },
    { 76, 4, 10 },
    { 79, 4, 10 },
    { 84, 8, 10 },
    { 88, 10, 10 },
};
static const ChipTrack sfx_catch_tr[] = {
    { 0, 2, 10, sfx_catch_t0, 5 },
};

static const ChipEv sfx_save_t0[] = {
    { 67, 5, 10 },
    { 72, 5, 10 },
    { 76, 5, 10 },
    { 79, 10, 10 },
};
static const ChipTrack sfx_save_tr[] = {
    { 0, 2, 10, sfx_save_t0, 4 },
};

static const ChipEv sfx_heal_t0[] = {
    { 76, 4, 9 },
    { 79, 4, 9 },
    { 83, 4, 9 },
    { 88, 8, 9 },
};
static const ChipTrack sfx_heal_tr[] = {
    { 0, 1, 9, sfx_heal_t0, 4 },
};

static const ChipEv sfx_faint_t0[] = {
    { 64, 6, 8 },
    { 60, 6, 8 },
    { 55, 8, 8 },
    { 52, 12, 8 },
};
static const ChipTrack sfx_faint_tr[] = {
    { 0, 1, 8, sfx_faint_t0, 4 },
};

static const ChipEv sfx_scream_t0[] = {
    { 69, 4, 12 },
    { 65, 4, 12 },
    { 62, 4, 12 },
    { 59, 4, 12 },
    { 55, 6, 12 },
    { 52, 6, 12 },
    { 48, 8, 12 },
    { 45, 10, 12 },
};
static const ChipEv sfx_scream_t1[] = {
    { 1, 6, 10 },
    { 1, 6, 10 },
    { 1, 8, 10 },
    { 1, 10, 10 },
    { 0, 4, 0 },
};
static const ChipTrack sfx_scream_tr[] = {
    { 0, 1, 12, sfx_scream_t0, 8 },
    { 2, 0, 10, sfx_scream_t1, 5 },
};

static const ChipSong CHIP_SONGS[SONG_N] = {
    { song_title_tr, 4, 1 },
    { song_home_tr, 4, 1 },
    { song_overworld_tr, 4, 1 },
    { song_wilds_tr, 4, 1 },
    { song_occupation_tr, 4, 1 },
    { song_battle_tr, 4, 1 },
    { song_boss_tr, 4, 1 },
};
static const ChipSong CHIP_SFX[SFX_N] = {
    { sfx_ui_tr, 1, 0 },
    { sfx_ok_tr, 1, 0 },
    { sfx_miss_tr, 2, 0 },
    { sfx_hit_tr, 2, 0 },
    { sfx_special_tr, 1, 0 },
    { sfx_catch_tr, 1, 0 },
    { sfx_save_tr, 1, 0 },
    { sfx_heal_tr, 1, 0 },
    { sfx_faint_tr, 1, 0 },
    { sfx_scream_tr, 2, 0 },
};

#define MAP_SONG_N 50
static const int MAP_SONG[MAP_SONG_N] = {
    SONG_HOME,
    SONG_OVERWORLD,
    SONG_WILDS,
    SONG_WILDS,
    SONG_OCCUPATION,
    SONG_WILDS,
    SONG_OCCUPATION,
    SONG_WILDS,
    SONG_WILDS,
    SONG_WILDS,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
    SONG_OVERWORLD,
};
#define SONG_ID_TITLE SONG_TITLE
#define SONG_ID_BATTLE SONG_BATTLE
#define SONG_ID_TRAINER SONG_BOSS
#define SONG_ID_ENDING SONG_TITLE

/* Master volume scale. 1 = original, 2 = 2x that ceiling. */
#define VOL_MIN 0.0f
#define VOL_MAX 2.0f
#define VOL_DEFAULT 1.0f
#define VOL_STEP 0.1f
#define BATTLE_MUSIC_MUL 0.5f

#endif

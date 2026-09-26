/* AUTO-GENERATED from content/*.json PACK_HASH=ae603c00c11cc6f7 — do not edit. python3 tools/bake_content.py */

#define SP_QUILLPUP 0
#define SP_GLIMMOTH 1
#define SP_TORTCASK 2
#define SP_RAZORBAT 3
#define SP_MOSSBACK 4
#define SP_BRIARFOX 5
#define SP_FENWISP 6
#define SP_DUSKHORN 7
#define SP_NEEDLEROOT 8
#define SP_CATHLEEN 9
#define SP_CRYMARE 10
#define SP_EMBERLING 11
#define SP_FROSTAIL 12
#define SP_BOULDERAM 13
#define SP_STORMWING 14
#define SP_SABLECLAW 15
#define SP_THORNHIDE 16
#define SP_GLASSWISP 17
#define SP_ASHENMAW 18
#define SP_HEAVENFALL 19
#define SP_PEATLING 20
#define SP_MIREBACK 21
#define SP_GLOWCAP 22
#define SP_SLATEKIN 23
#define SP_GRAVELURK 24
#define SP_CINDERMITE 25
#define SP_VEILCAP 26
#define SP_KILNBACK 27
#define SP_LEAD 28
#define SP_SHREWBIT 29
#define SP_JOLTHARE 30
#define SP_VOLTBUCK 31
#define SP_CHILLNEWT 32
#define SP_RIMEWYRM 33
#define SP_RUNEMOTE 34
#define SP_GLYPHWING 35
#define SP_SCAVRAT 36
#define SP_PLUNDERAT 37
#define SP_STARDROP 38
#define SP_RIMEOWL 39
#define SP_VOLTGRUB 40
#define SP_CHARMKIN 41
#define SPECIES_N 42

static const SpellDef SPELLS[4] = {
    { ATK_MAG, 0.6f, 1.2f },
    { ATK_MAG, 0.6f, 1.2f },
    { ATK_MAG, 0.6f, 1.2f },
    { ATK_MAG, 1.0f, 0.8f },
};

static const Species SPECIES[SPECIES_N] = {
    { "QUILLPUP", "NIP", "QUILLBURST", 34, 15, 10, 7, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 0, 8 },
    { "GLIMMOTH", "DUSTWING", "LAMPFLARE", 29, 8, 15, 18, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 3, 14 },
    { "TORTCASK", "SHOVE", "SHELLSLAM", 50, 15, 6, 10, 3, ATK_STR, ATK_STR, 0.6f, 1.2f, 1.3f, 0.5f, 0, {0,0,0,0}, 1, -1 },
    { "RAZORBAT", "RAKE", "SWOOPCUT", 31, 14, 16, 9, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 4, 15 },
    { "MOSSBACK", "SQUELCH", "MOSSGUARD", 36, 12, 6, 11, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 0.6f, 0.7f, 0, {0,0,0,0}, 6, 2 },
    { "BRIARFOX", "BRAMBLE", "THORNRUSH", 31, 15, 19, 11, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 6, -1 },
    { "FENWISP", "GLIM", "FENFLARE", 21, 7, 14, 15, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 4, 3 },
    { "DUSKHORN", "GORE", "DUSKRAM", 41, 18, 9, 8, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 4, -1 },
    { "NEEDLEROOT", "PRICK", "SAPDRAIN", 36, 14, 8, 16, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 0.7f, 1.0f, 0, {0,0,0,0}, 6, 16 },
    { "CATHLEEN", "FIRE BOLT", "MANA SURGE", 38, 11, 13, 19, 4, ATK_MAG, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 4, {0,1,2,3}, 5, -1 },
    { "CRYMARE", "WAIL", "NIGHTBRIDLE", 33, 10, 15, 20, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.2f, 0.6f, 0, {0,0,0,0}, 4, -1 },
    { "EMBERLING", "SPARK", "EMBERBLAZE", 28, 13, 14, 11, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 7, 18 },
    { "FROSTAIL", "CHILL", "FROSTFANG", 36, 13, 12, 16, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 8, -1 },
    { "BOULDERAM", "RAM", "STONESLAM", 54, 20, 5, 7, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 1, -1 },
    { "STORMWING", "GUST", "THUNDERDIVE", 33, 12, 24, 16, 3, ATK_STR, ATK_STR, 0.6f, 1.2f, 1.1f, 1.2f, 0, {0,0,0,0}, 3, -1 },
    { "SABLECLAW", "SLASH", "SHADOWRIP", 38, 20, 16, 11, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 4, -1 },
    { "THORNHIDE", "BARB", "THORNWALL", 51, 14, 8, 13, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 6, -1 },
    { "GLASSWISP", "CHIME", "PRISMFLARE", 27, 8, 18, 23, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 5, -1 },
    { "ASHENMAW", "BITE", "ASHENROAR", 38, 20, 13, 12, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 7, -1 },
    { "HEAVENFALL", "METEOR", "STARFALL", 58, 20, 10, 22, 4, ATK_STR, ATK_MAG, 1.5f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 2, -1 },
    { "PEATLING", "SOP", "PEATSPIT", 30, 11, 12, 10, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 0.8f, 1.1f, 0, {0,0,0,0}, 1, 21 },
    { "MIREBACK", "WALLOP", "SINKHOLE", 45, 16, 7, 12, 3, ATK_STR, ATK_STR, 0.6f, 1.2f, 1.25f, 0.55f, 0, {0,0,0,0}, 1, -1 },
    { "GLOWCAP", "SPORE", "CAPFLARE", 28, 8, 11, 17, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.15f, 0.7f, 0, {0,0,0,0}, 6, 26 },
    { "SLATEKIN", "CHIP", "FLAKEEDGE", 30, 13, 8, 7, 3, ATK_STR, ATK_STR, 0.6f, 1.2f, 1.05f, 1.05f, 0, {0,0,0,0}, 1, 24 },
    { "GRAVELURK", "GRIND", "QUARRYDROP", 44, 17, 4, 6, 3, ATK_STR, ATK_STR, 0.6f, 1.2f, 1.35f, 0.45f, 0, {0,0,0,0}, 1, 13 },
    { "CINDERMITE", "NIBBLE", "KILNSPARK", 26, 12, 14, 13, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.1f, 1.15f, 0, {0,0,0,0}, 7, 27 },
    { "VEILCAP", "SPORE", "VEILBURST", 37, 9, 12, 23, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.25f, 0.65f, 0, {0,0,0,0}, 6, -1 },
    { "KILNBACK", "NIBBLE", "SLAGBURST", 36, 17, 13, 16, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.2f, 0.9f, 0, {0,0,0,0}, 7, -1 },
    { "LIEUTENANT LEAD", "BURST FIRE", "SUPPRESSING FIRE", 20, 7, 7, 3, 3, ATK_STR, ATK_STR, 1.5f, 1.0f, 1.2f, 0.9f, 0, {0,0,0,0}, 0, -1 },
    { "SHREWBIT", "SCRATCH", "TAILWHIP", 25, 10, 14, 7, 3, ATK_STR, ATK_STR, 0.6f, 1.2f, 0.9f, 1.2f, 0, {0,0,0,0}, 0, 36 },
    { "JOLTHARE", "ZAP", "BOLTKICK", 27, 9, 16, 11, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 3, 31 },
    { "VOLTBUCK", "ZAP", "THUNDERHOOF", 36, 13, 18, 13, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.2f, 0.7f, 0, {0,0,0,0}, 3, -1 },
    { "CHILLNEWT", "FROSTLICK", "SLEETSPIT", 30, 9, 11, 14, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 8, 33 },
    { "RIMEWYRM", "COIL", "RIMEBREATH", 40, 14, 10, 18, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.25f, 0.65f, 0, {0,0,0,0}, 8, -1 },
    { "RUNEMOTE", "FLICKER", "RUNEFLARE", 20, 5, 13, 17, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.1f, 0.8f, 0, {0,0,0,0}, 5, 41 },
    { "GLYPHWING", "FLICKER", "GLYPHSTORM", 34, 8, 18, 24, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.25f, 0.7f, 0, {0,0,0,0}, 5, -1 },
    { "SCAVRAT", "GNAW", "RANSACK", 33, 14, 15, 7, 3, ATK_STR, ATK_STR, 0.6f, 1.2f, 1.05f, 1.05f, 0, {0,0,0,0}, 0, 37 },
    { "PLUNDERAT", "GNAW", "PILLAGE", 43, 18, 16, 7, 3, ATK_STR, ATK_STR, 0.6f, 1.2f, 1.3f, 0.6f, 0, {0,0,0,0}, 0, -1 },
    { "STARDROP", "GLINT", "STARSHARD", 35, 14, 10, 17, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.1f, 0.8f, 0, {0,0,0,0}, 2, -1 },
    { "RIMEOWL", "TALON", "HAILWING", 32, 12, 16, 15, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 8, -1 },
    { "VOLTGRUB", "BURROW", "ARCSPARK", 26, 9, 9, 12, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.05f, 1.0f, 0, {0,0,0,0}, 3, 1 },
    { "CHARMKIN", "TWINKLE", "HEXCHARM", 26, 7, 17, 19, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 5, 35 },
};


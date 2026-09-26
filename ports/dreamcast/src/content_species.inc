/* AUTO-GENERATED from content/*.json PACK_HASH=2c179a5a33041d5e — do not edit. python3 tools/bake_content.py */

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
    { "GLIMMOTH", "DUSTWING", "LAMPFLARE", 26, 7, 13, 16, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 3, 14 },
    { "TORTCASK", "SHOVE", "SHELLSLAM", 42, 13, 5, 8, 3, ATK_STR, ATK_STR, 0.6f, 1.2f, 1.3f, 0.5f, 0, {0,0,0,0}, 1, -1 },
    { "RAZORBAT", "RAKE", "SWOOPCUT", 30, 14, 16, 9, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 4, 15 },
    { "MOSSBACK", "SQUELCH", "MOSSGUARD", 38, 12, 6, 11, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 0.6f, 0.7f, 0, {0,0,0,0}, 6, -1 },
    { "BRIARFOX", "BRAMBLE", "THORNRUSH", 28, 13, 17, 10, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 6, 16 },
    { "FENWISP", "GLIM", "FENFLARE", 24, 8, 16, 17, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 4, 17 },
    { "DUSKHORN", "GORE", "DUSKRAM", 36, 16, 8, 7, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 4, 13 },
    { "NEEDLEROOT", "PRICK", "SAPDRAIN", 32, 12, 7, 14, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 0.7f, 1.0f, 0, {0,0,0,0}, 6, -1 },
    { "CATHLEEN", "FIRE BOLT", "MANA SURGE", 38, 11, 13, 19, 4, ATK_MAG, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 4, {0,1,2,3}, 5, -1 },
    { "CRYMARE", "WAIL", "NIGHTBRIDLE", 30, 9, 14, 18, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.2f, 0.6f, 0, {0,0,0,0}, 4, -1 },
    { "EMBERLING", "SPARK", "EMBERBLAZE", 28, 14, 15, 12, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 7, 18 },
    { "FROSTAIL", "CHILL", "FROSTFANG", 32, 12, 11, 15, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 8, -1 },
    { "BOULDERAM", "RAM", "STONESLAM", 46, 17, 4, 6, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 1, -1 },
    { "STORMWING", "GUST", "THUNDERDIVE", 26, 10, 19, 13, 3, ATK_STR, ATK_STR, 0.6f, 1.2f, 1.1f, 1.2f, 0, {0,0,0,0}, 3, -1 },
    { "SABLECLAW", "SLASH", "SHADOWRIP", 30, 16, 13, 9, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 4, -1 },
    { "THORNHIDE", "BARB", "THORNWALL", 40, 11, 6, 10, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 6, -1 },
    { "GLASSWISP", "CHIME", "PRISMFLARE", 22, 6, 14, 18, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 5, -1 },
    { "ASHENMAW", "BITE", "ASHENROAR", 34, 18, 12, 11, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 7, -1 },
    { "HEAVENFALL", "METEOR", "STARFALL", 58, 20, 10, 22, 4, ATK_STR, ATK_MAG, 1.5f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 2, -1 },
    { "PEATLING", "SOP", "PEATSPIT", 30, 11, 12, 10, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 0.8f, 1.1f, 0, {0,0,0,0}, 1, 21 },
    { "MIREBACK", "WALLOP", "SINKHOLE", 44, 16, 7, 12, 3, ATK_STR, ATK_STR, 0.6f, 1.2f, 1.25f, 0.55f, 0, {0,0,0,0}, 1, -1 },
    { "GLOWCAP", "SPORE", "CAPFLARE", 28, 8, 11, 17, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.15f, 0.7f, 0, {0,0,0,0}, 6, 26 },
    { "SLATEKIN", "CHIP", "FLAKEEDGE", 32, 14, 9, 8, 3, ATK_STR, ATK_STR, 0.6f, 1.2f, 1.05f, 1.05f, 0, {0,0,0,0}, 1, 24 },
    { "GRAVELURK", "GRIND", "QUARRYDROP", 48, 18, 4, 7, 3, ATK_STR, ATK_STR, 0.6f, 1.2f, 1.35f, 0.45f, 0, {0,0,0,0}, 1, -1 },
    { "CINDERMITE", "NIBBLE", "KILNSPARK", 26, 13, 15, 14, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.1f, 1.15f, 0, {0,0,0,0}, 7, 27 },
    { "VEILCAP", "SPORE", "VEILBURST", 36, 9, 12, 22, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.25f, 0.65f, 0, {0,0,0,0}, 6, -1 },
    { "KILNBACK", "NIBBLE", "SLAGBURST", 38, 17, 13, 16, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.2f, 0.9f, 0, {0,0,0,0}, 7, -1 },
    { "LIEUTENANT LEAD", "BURST FIRE", "SUPPRESSING FIRE", 20, 7, 7, 3, 3, ATK_STR, ATK_STR, 1.5f, 1.0f, 1.2f, 0.9f, 0, {0,0,0,0}, 0, -1 },
    { "SHREWBIT", "SCRATCH", "TAILWHIP", 26, 10, 15, 7, 3, ATK_STR, ATK_STR, 0.6f, 1.2f, 0.9f, 1.2f, 0, {0,0,0,0}, 0, -1 },
    { "JOLTHARE", "ZAP", "BOLTKICK", 26, 9, 16, 11, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 3, 31 },
    { "VOLTBUCK", "ZAP", "THUNDERHOOF", 36, 14, 19, 14, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.2f, 0.7f, 0, {0,0,0,0}, 3, -1 },
    { "CHILLNEWT", "FROSTLICK", "SLEETSPIT", 30, 9, 11, 14, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 8, 33 },
    { "RIMEWYRM", "COIL", "RIMEBREATH", 44, 15, 11, 19, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.25f, 0.65f, 0, {0,0,0,0}, 8, -1 },
    { "RUNEMOTE", "FLICKER", "RUNEFLARE", 22, 5, 14, 18, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.1f, 0.8f, 0, {0,0,0,0}, 5, 35 },
    { "GLYPHWING", "FLICKER", "GLYPHSTORM", 32, 8, 17, 23, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.25f, 0.7f, 0, {0,0,0,0}, 5, -1 },
    { "SCAVRAT", "GNAW", "RANSACK", 28, 12, 13, 6, 3, ATK_STR, ATK_STR, 0.6f, 1.2f, 1.05f, 1.05f, 0, {0,0,0,0}, 0, 37 },
    { "PLUNDERAT", "GNAW", "PILLAGE", 40, 17, 15, 7, 3, ATK_STR, ATK_STR, 0.6f, 1.2f, 1.3f, 0.6f, 0, {0,0,0,0}, 0, -1 },
    { "STARDROP", "GLINT", "STARSHARD", 30, 12, 8, 14, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.1f, 0.8f, 0, {0,0,0,0}, 2, -1 },
    { "RIMEOWL", "TALON", "HAILWING", 28, 10, 14, 13, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 8, -1 },
    { "VOLTGRUB", "BURROW", "ARCSPARK", 30, 11, 10, 14, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.05f, 1.0f, 0, {0,0,0,0}, 3, -1 },
    { "CHARMKIN", "TWINKLE", "HEXCHARM", 24, 6, 15, 17, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 5, -1 },
};


/* AUTO-GENERATED from content/*.json PACK_HASH=5ceed561aef4b9e7 — do not edit. python3 tools/bake_content.py */

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
#define SPECIES_N 20

static const SpellDef SPELLS[4] = {
    { ATK_MAG, 0.6f, 1.2f },
    { ATK_MAG, 0.6f, 1.2f },
    { ATK_MAG, 0.6f, 1.2f },
    { ATK_MAG, 1.0f, 0.8f },
};

static const Species SPECIES[SPECIES_N] = {
    { "QUILLPUP", "NIP", "QUILLBURST", 34, 15, 10, 7, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 0 },
    { "GLIMMOTH", "DUSTWING", "LAMPFLARE", 26, 7, 13, 16, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 6 },
    { "TORTCASK", "SHOVE", "SHELLSLAM", 42, 13, 5, 8, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 2 },
    { "RAZORBAT", "RAKE", "SWOOPCUT", 30, 14, 16, 9, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 4 },
    { "MOSSBACK", "SQUELCH", "MOSSGUARD", 38, 12, 6, 11, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 0 },
    { "BRIARFOX", "BRAMBLE", "THORNRUSH", 28, 13, 17, 10, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 3 },
    { "FENWISP", "GLIM", "FENFLARE", 24, 8, 16, 17, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 6 },
    { "DUSKHORN", "GORE", "DUSKRAM", 36, 16, 8, 7, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 1 },
    { "NEEDLEROOT", "PRICK", "SAPDRAIN", 32, 12, 7, 14, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 0 },
    { "CATHLEEN", "FIRE BOLT", "MANA SURGE", 38, 11, 13, 19, 4, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 4, {0,1,2,3}, 5 },
    { "CRYMARE", "WAIL", "NIGHTBRIDLE", 30, 9, 14, 18, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 5 },
    { "EMBERLING", "SPARK", "EMBERBLAZE", 28, 14, 15, 12, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 4 },
    { "FROSTAIL", "CHILL", "FROSTFANG", 32, 12, 11, 15, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 6 },
    { "BOULDERAM", "RAM", "STONESLAM", 46, 17, 4, 6, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 1 },
    { "STORMWING", "GUST", "THUNDERDIVE", 26, 10, 19, 13, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 3 },
    { "SABLECLAW", "SLASH", "SHADOWRIP", 30, 16, 13, 9, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 4 },
    { "THORNHIDE", "BARB", "THORNWALL", 40, 11, 6, 10, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 2 },
    { "GLASSWISP", "CHIME", "PRISMFLARE", 22, 6, 14, 18, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 5 },
    { "ASHENMAW", "BITE", "ASHENROAR", 34, 18, 12, 11, 3, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 1 },
    { "HEAVENFALL", "METEOR", "STARFALL", 58, 20, 10, 22, 4, ATK_STR, ATK_MAG, 0.6f, 1.2f, 1.0f, 0.8f, 0, {0,0,0,0}, 2 },
};


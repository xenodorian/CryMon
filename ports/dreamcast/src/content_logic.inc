/* AUTO-GENERATED from content/*.json PACK_HASH=cdecab0082db2463 — do not edit. python3 tools/bake_content.py */

/* Canonical rules from content/logic.json (Dreamcast spec). */
#define LOGIC_FADE_OUT_FRAMES 16
#define LOGIC_FADE_HOLD_FRAMES 3
#define LOGIC_FADE_IN_FRAMES 16
#define LOGIC_MASON_AMBUSH_NEED_PARTY 1
#define LOGIC_MASON_AMBUSH_UNLESS_BEAT 1
static const int LOGIC_MASON2_MAPS[] = { MAP_VELD, MAP_FOREST, MAP_GROVE };
#define LOGIC_MASON2_MAP_N 3

typedef struct { const char *name; int str, agl, spc; } NatureDef;
#define NATURE_N 7
static const NatureDef NATURES[NATURE_N] = {
    { "HARDY", 0, 0, 0 },
    { "LONELY", 2, -1, 0 },
    { "ADAMANT", 2, 0, -1 },
    { "BOLD", -1, 2, 0 },
    { "TIMID", 0, 2, -1 },
    { "MODEST", -1, 0, 2 },
    { "CALM", 0, -1, 2 },
};

#define PARTY_MAX 6
#define PARTY_RELEASE 1
#define PARTY_CATCH_SWAP 1
#define PARTY_KEEP_LAST 1
#define ANNE_GIFT_AFTER 1
#define ANNE_GIFT_QTY 5
#define SPR_SCALE_MASON 2


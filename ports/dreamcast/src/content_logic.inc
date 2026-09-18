/* AUTO-GENERATED from content/*.json PACK_HASH=4a2cc637cba7400e — do not edit. python3 tools/bake_content.py */

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


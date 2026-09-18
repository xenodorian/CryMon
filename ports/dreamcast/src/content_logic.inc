/* AUTO-GENERATED from content/*.json PACK_HASH=8820088ad75f469a — do not edit. python3 tools/bake_content.py */

/* Canonical rules from content/logic.json (Dreamcast spec). */
#define LOGIC_FADE_OUT_FRAMES 16
#define LOGIC_FADE_HOLD_FRAMES 3
#define LOGIC_FADE_IN_FRAMES 16
#define LOGIC_MASON_AMBUSH_NEED_PARTY 1
#define LOGIC_MASON_AMBUSH_UNLESS_BEAT 1
static const int LOGIC_MASON2_MAPS[] = { MAP_VELD, MAP_FOREST, MAP_GROVE };
#define LOGIC_MASON2_MAP_N 3

typedef struct { const char *name; int str, agl, spc; int ring; } NatureDef;
#define NATURE_N 7
static const NatureDef NATURES[NATURE_N] = {
    { "QUARTZ", 1, 1, 1, 2 },
    { "HEMATITE", 3, 0, 0, 1 },
    { "DIAMOND", 2, 0, 1, 0 },
    { "OPAL", 0, 3, 0, 5 },
    { "SPINEL", 1, 2, 0, 6 },
    { "LAPIS LAZULI", 0, 0, 3, 4 },
    { "AMETHYST", 0, 1, 2, 3 },
};
/* Crystal matchups: each crystal splits the next
   NATURE_BEATS_AHEAD around the ring and is split by the
   previous that many. Derived, not a stored matrix. */
#define NATURE_RING_N 7
#define NATURE_BEATS_AHEAD 2
#define NATURE_STRONG_MUL 2.0f
#define NATURE_WEAK_MUL 0.5f
#define NATURE_STRONG_TEXT "WEAKNESS X2"
#define NATURE_WEAK_TEXT "RESISTED X0.5"

#define PARTY_MAX 6
#define PARTY_RELEASE 1
#define PARTY_CATCH_SWAP 1
#define PARTY_KEEP_LAST 1
#define ANNE_GIFT_AFTER 1
#define ANNE_GIFT_QTY 5
#define SPR_SCALE_MASON 2


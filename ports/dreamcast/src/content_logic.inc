/* AUTO-GENERATED from content/*.json PACK_HASH=79d1877c0f742658 — do not edit. python3 tools/bake_content.py */

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

/* Guard resolution -- see content/logic.json's combat block. */
#define DODGE_DEF_RAND_MIN 0.75f
#define DODGE_DEF_RAND_MAX 1.25f
#define GUARD_RAND_MIN 0.25f
#define GUARD_RAND_MAX 0.75f
#define BARRIER_HEAL_DIVISOR 2
#define GUARD_PARRIED_TEXT "PARRIED!"
#define GUARD_ABSORBED_TEXT "ABSORBED!"
/* Special timing bar -- logic.json combat.minigame. */
#define SPEC_PERFECT_LO 45.0f
#define SPEC_PERFECT_HI 55.0f
#define SPEC_CONN_LO 30.0f
#define SPEC_CONN_HI 70.0f
#define SPEC_MUL_PERFECT 2.0f
#define SPEC_MUL_CONN 1.5f
#define SPEC_MUL_FIZZ 1.0f
#define SPEC_NEEDLE_SPEED 110.0f

/* Toxic Burst -- universal shiny-exclusive move, not per-species. */
#define TOXIC_NAME "TOXIC BURST"
#define TOXIC_STAT ATK_STR
#define TOXIC_POWER 0.5f
#define TOXIC_SPEED 1.0f
#define TOXIC_POISON_DIVISOR 16

/* Move unlocks + evolution -- logic.json growth. */
#define LV_SECONDARY 5
#define LV_SPECIAL 10
#define LV_EVOLVE 12

typedef struct { const char *name; int stat; float power, speed; int dstr, dagl, dspc; } NatureMove;
#define NATURE_MOVE_N 7
static const NatureMove NATURE_MOVES[NATURE_N] = {
    { "FRACTURE", ATK_STR, 0.5f, 1.0f, -2, -2, -2 },
    { "REND", ATK_STR, 0.5f, 0.9f, -4, 0, 0 },
    { "CLEAVE", ATK_STR, 0.5f, 1.0f, -3, -1, 0 },
    { "DAZZLE", ATK_MAG, 0.5f, 1.2f, 0, -4, 0 },
    { "BIND", ATK_STR, 0.5f, 1.1f, -2, -2, 0 },
    { "VEIL", ATK_MAG, 0.5f, 1.0f, 0, 0, -4 },
    { "HEX", ATK_MAG, 0.5f, 1.0f, 0, -2, -2 },
};


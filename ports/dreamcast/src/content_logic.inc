/* AUTO-GENERATED from content/*.json PACK_HASH=d7688e3bf23b8009 — do not edit. python3 tools/bake_content.py */

/* Canonical rules from content/logic.json (Dreamcast spec). */
#define LOGIC_FADE_OUT_FRAMES 16
#define LOGIC_FADE_HOLD_FRAMES 3
#define LOGIC_FADE_IN_FRAMES 16
#define LOGIC_REP_MIN -100
#define LOGIC_REP_MAX 100
#define LOGIC_REP_FATHER_REVIVE 25
#define LOGIC_REP_HEAVENFALL_REVIVE -25
#define LOGIC_REP_KIND_NAME "MAX THE KIND"
#define LOGIC_REP_PRICE_POS_PCT 1
#define LOGIC_REP_PRICE_NEG_PCT 5
#define LOGIC_REP_MIN_PRICE 1
#define LOGIC_REP_REFUSE_AT -100
#define LOGIC_REP_FREE_AT 100
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

/* Move unlocks + evolution -- logic.json growth. */
#define LV_SECONDARY 5
#define LV_SPECIAL 10
#define LV_EVOLVE 12

#define STAT_STR 0
#define STAT_AGL 1
#define STAT_SPC 2
#define STATUS_NONE 0
#define STATUS_BURNED 1
#define STATUS_POISONED 2
#define STATUS_CONFUSED 3
#define STATUS_PARALYZED 4
#define STATUS_EXHAUSTED 5
#define STAT_STAGE_MAX 4
#define STAT_STAGE_FLOOR 1
#define STAT_STAGE_N 5
static const float STAT_STAGE_MULT[5] = { 1.0f, 0.7f, 0.4f, 0.1f, 0.0f };

#define STATUS_BURN_PCT 5
#define STATUS_BURN_TURNS_MIN 2
#define STATUS_BURN_TURNS_MAX 5
#define STATUS_POISON_START_PCT 1
#define STATUS_POISON_STEP_PCT 1
#define STATUS_PARALYZE_TURNS_MIN 1
#define STATUS_PARALYZE_TURNS_MAX 5

/* Overload -- universal shiny-exclusive move, not per-species. */
#define SHINY_MOVE_NAME "OVERLOAD"
#define SHINY_MOVE_STATUS 5
#define SHINY_MOVE_MAX_PP 10

/* Hype Up -- learned on evolving, see bake_npc note / CURRENT_WORK 2.11. */
#define HYPE_UP_NAME "HYPE UP"
#define HYPE_UP_PCT 35
#define HYPE_UP_MAX_PP 10

#define STAT_MOVE_CAP 10
#define STATUS_MOVE_CAP 5

typedef struct { const char *name; int kind; int stat; int status; int max_pp; } NatureMove;
#define NMOVE_KIND_STAGE 0
#define NMOVE_KIND_STATUS 1
#define NATURE_MOVE_N 7
static const NatureMove NATURE_MOVES[NATURE_N] = {
    { "PROUD ROAR", NMOVE_KIND_STAGE, 0, 0, 10 },
    { "SCORCH", NMOVE_KIND_STATUS, 0, 1, 5 },
    { "BLIGHT", NMOVE_KIND_STATUS, 0, 2, 5 },
    { "SLOW POWDER", NMOVE_KIND_STAGE, 1, 0, 10 },
    { "BIND", NMOVE_KIND_STATUS, 0, 4, 5 },
    { "VEIL", NMOVE_KIND_STATUS, 0, 3, 5 },
    { "MAGEBANE", NMOVE_KIND_STAGE, 2, 0, 10 },
};


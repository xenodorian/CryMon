/* AUTO-GENERATED from content/*.json PACK_HASH=7fa1142217b96dc0 — do not edit. python3 tools/bake_content.py */

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

typedef struct { const char *name; int str, agl, spc; } NatureDef;
#define NATURE_N 9
static const NatureDef NATURES[NATURE_N] = {
    { "QUARTZ", 1, 1, 1 },
    { "JASPER", 3, 0, 0 },
    { "DIAMOND", 2, 0, 1 },
    { "CITRINE", 0, 3, 0 },
    { "OBSIDIAN", 1, 2, 0 },
    { "PRISM", 0, 0, 3 },
    { "EMERALD", 0, 1, 2 },
    { "RUBY", 2, 1, 0 },
    { "SAPPHIRE", 1, 0, 2 },
};
#define NATURE_BADGE_MAX 6
static const int NATURE_BADGE_N[NATURE_N] = {
    1, /* quartz */
    1, /* jasper */
    1, /* diamond */
    1, /* citrine */
    1, /* obsidian */
    5, /* prism */
    1, /* emerald */
    1, /* ruby */
    1, /* sapphire */
};
static const unsigned short NATURE_BADGE[NATURE_N][NATURE_BADGE_MAX] = {
    { 0xEF5C, 0xEF5C, 0xEF5C, 0xEF5C, 0xEF5C, 0xEF5C }, /* quartz */
    { 0x9B06, 0x9B06, 0x9B06, 0x9B06, 0x9B06, 0x9B06 }, /* jasper */
    { 0xBE3F, 0xBE3F, 0xBE3F, 0xBE3F, 0xBE3F, 0xBE3F }, /* diamond */
    { 0xF606, 0xF606, 0xF606, 0xF606, 0xF606, 0xF606 }, /* citrine */
    { 0x2926, 0x2926, 0x2926, 0x2926, 0x2926, 0x2926 }, /* obsidian */
    { 0xD1C7, 0xF606, 0x3D09, 0x3B7A, 0x8A7A, 0x8A7A }, /* prism */
    { 0x3D09, 0x3D09, 0x3D09, 0x3D09, 0x3D09, 0x3D09 }, /* emerald */
    { 0xD1C7, 0xD1C7, 0xD1C7, 0xD1C7, 0xD1C7, 0xD1C7 }, /* ruby */
    { 0x3B7A, 0x3B7A, 0x3B7A, 0x3B7A, 0x3B7A, 0x3B7A }, /* sapphire */
};
/* Crystal matchups from logic.json natureTypes.beats:
   NATURE_CHART[atk][def] is +1 (atk splits def), -1 (def
   holds), 0 neutral. Always antisymmetric. */
static const signed char NATURE_CHART[NATURE_N][NATURE_N] = {
    {  0,  0,  0,  0,  0,  0,  0,  0,  0 }, /* quartz */
    {  0,  0, -1,  1,  0,  0, -1,  1, -1 }, /* jasper */
    {  0,  1,  0,  0, -1,  0,  0,  0,  0 }, /* diamond */
    {  0, -1,  0,  0,  1, -1,  0,  0,  0 }, /* citrine */
    {  0,  0,  1, -1,  0,  1, -1,  0,  0 }, /* obsidian */
    {  0,  0,  0,  1, -1,  0,  0,  1,  1 }, /* prism */
    {  0,  1,  0,  0,  1,  0,  0, -1, -1 }, /* emerald */
    {  0, -1,  0,  0,  0, -1,  1,  0,  1 }, /* ruby */
    {  0,  1,  0,  0,  0, -1,  1, -1,  0 }, /* sapphire */
};
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
#define SPR_SCALE_MASON 1

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
#define NATURE_MOVE_N 9
static const NatureMove NATURE_MOVES[NATURE_N] = {
    { "PROUD ROAR", NMOVE_KIND_STAGE, 0, 0, 10 },
    { "SANDBLAST", NMOVE_KIND_STAGE, 1, 0, 10 },
    { "GRAVITY", NMOVE_KIND_STAGE, 1, 0, 10 },
    { "STATIC", NMOVE_KIND_STATUS, 0, 4, 5 },
    { "VEIL", NMOVE_KIND_STATUS, 0, 3, 5 },
    { "MAGEBANE", NMOVE_KIND_STAGE, 2, 0, 10 },
    { "BLIGHT", NMOVE_KIND_STATUS, 0, 2, 5 },
    { "SCORCH", NMOVE_KIND_STATUS, 0, 1, 5 },
    { "FROSTBITE", NMOVE_KIND_STAGE, 0, 0, 10 },
};


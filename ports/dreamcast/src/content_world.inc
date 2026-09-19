/* AUTO-GENERATED from content/*.json PACK_HASH=cbb639f34acbf37e — do not edit. python3 tools/bake_content.py */

/* Canonical world tables from content/world.json + items.json. */
#define XP_BASE 6
#define XP_PER_LEVEL 4
#define LEVEL_XP_MUL 10
#define LEVEL_CAP 20
#define LEVEL_HP 3
#define LEVEL_STAT 1
#define CAPTURE_AGL 5
#define CAPTURE_VULN 25
#define SHINY_DENOM 64
#define ENCOUNTER_PCT 18
#define GREATCRYSTAL_BONUS 25
#define BENCH_XP_PCT 50
#define BITTERROOT_STR 4
#define WARROOT_AGL 4
#define DUST_STR -3
#define DUST_AGL -2
#define DUST_SPC -2
#define START_MARKS 16
#define START_BAG_INIT { 2, 2, 1, 1, 0, 0, 0, 1, 0, 0 }

typedef struct {
    int from_map, to_map;
    char tile, spawn;
    int face_down; /* 1 = arrive facing down (from south) */
    int need;      /* 0 none, 1 tookStarter, 2 beatCalder, 3 beatShin, 4 hasScroll */
    int on_arrive; /* 0 none, 1 masonAmbush, 2 ensureSoldiers */
    int fail_talk; /* talk table index, -1 none */
} WarpDef;
static const WarpDef WARPS[] = {
    { MAP_HOUSE, MAP_VELD, 'D', 'D', 1, 1, 1, 7 },
    { MAP_VELD, MAP_HOUSE, 'D', 'D', 0, 0, 0, -1 },
    { MAP_VELD, MAP_FOREST, 'Z', 'Y', 1, 0, 2, -1 },
    { MAP_FOREST, MAP_VELD, 'Y', 'Z', 0, 0, 0, -1 },
    { MAP_FOREST, MAP_GROVE, 'O', 'O', 1, 0, 0, -1 },
    { MAP_GROVE, MAP_FOREST, 'O', 'O', 0, 0, 0, -1 },
    { MAP_VELD, MAP_CAMP, 'F', 'D', 1, 2, 0, 8 },
    { MAP_CAMP, MAP_VELD, 'D', 'F', 0, 0, 0, -1 },
    { MAP_VELD, MAP_CLIFFS, 'c', 'D', 1, 0, 0, -1 },
    { MAP_CLIFFS, MAP_VELD, 'D', 'c', 0, 0, 0, -1 },
    { MAP_GROVE, MAP_RUINS, 'g', 'D', 1, 3, 0, 9 },
    { MAP_RUINS, MAP_GROVE, 'D', 'g', 0, 0, 0, -1 },
    { MAP_RUINS, MAP_REACH, 'e', 'D', 1, 4, 0, 75 },
    { MAP_REACH, MAP_RUINS, 'D', 'e', 0, 0, 0, -1 },
};
#define WARP_N (int)(sizeof(WARPS)/sizeof(WARPS[0]))

typedef struct {
    int map_id;
    char tile;
    int rate;
    int pool[8];
    int pool_n;
    int lv_min, lv_max;
    int ty_bonus_gt; /* -1 none */
} EncDef;
static const EncDef ENCOUNTERS[] = {
    { MAP_GROVE, 'T', 18, { 3,5,6,0,0,0,0,0 }, 3, 5, 8, -1 },
    { MAP_CAMP, 'T', 18, { 7,18,15,0,0,0,0,0 }, 3, 6, 9, -1 },
    { MAP_RUINS, 'T', 18, { 2,17,4,0,0,0,0,0 }, 3, 6, 9, -1 },
    { MAP_FOREST, 'T', 18, { 6,7,0,3,0,0,0,0 }, 4, 3, 5, -1 },
    { MAP_CLIFFS, 'T', 18, { 14,15,12,16,13,17,0,0 }, 6, 5, 7, -1 },
    { MAP_VELD, 'T', 18, { 1,2,11,5,0,0,0,0 }, 4, 2, 4, 14 },
    { MAP_REACH, 'T', 22, { 18,8,10,14,17,4,0,0 }, 6, 8, 11, -1 },
};
#define ENC_N 7

typedef struct {
    int lead_sp, lead_lv;
    int bench_sp[2], bench_lv[2], bench_n;
} TrainerKit;
static const TrainerKit TRAINER_KITS[4] = {
    { 11, 5, { 12, 14 }, { 6, 7 }, 2 },
    { 15, 7, { 13, 18 }, { 8, 9 }, 2 },
    { 16, 8, { 17, 7 }, { 9, 10 }, 2 },
    { 10, 9, { 18, 13 }, { 10, 11 }, 2 },
};
#define KIT_SENTRY 0
#define KIT_CONSCRIPT 1
#define KIT_ENFORCER 2
#define KIT_CROSS 3
#define KIT_CATHLEEN_LV 10
#define KIT_SHINIGAMI_LEAD_LV 15
#define KIT_SHINIGAMI_B0_LV 14
#define KIT_SHINIGAMI_B1_LV 13

typedef struct { int kind, amount, str, agl, spc, bonus; } ItemFx;
static const ItemFx ITEM_FX[] = {
    { 1, 22, 0, 0, 0, 0 },
    { 1, 12, 0, 0, 0, 0 },
    { 2, 0, 4, 0, 0, 0 },
    { 3, 0, -3, -2, -2, 0 },
    { 4, 0, 0, 0, 0, 0 },
    { 1, 40, 0, 0, 0, 0 },
    { 2, 0, 0, 4, 0, 0 },
    { 5, 0, 0, 0, 0, 0 },
    { 4, 0, 0, 0, 0, 25 },
    { 0, 0, 0, 0, 0, 0 },
};

/* NPC first-match scripts from content/world.json. */
#define FLAG_TOOK_STARTER 0
#define FLAG_TALKED_FATHER 1
#define FLAG_LOOTED_CRATE 2
#define FLAG_TALKED_WREN 3
#define FLAG_BEAT_CALDER 4
#define FLAG_READ_CART 5
#define FLAG_TALKED_MAE 6
#define FLAG_TALKED_IVO 7
#define FLAG_TALKED_NELL 8
#define FLAG_NELL_BONUS 9
#define FLAG_HAS_PARTY2 10
#define FLAG_GOT_FIELD_GEM 11
#define FLAG_PIKE_HELPED 12
#define FLAG_TALKED_PIKE 13
#define FLAG_GOT_HERB 14
#define FLAG_GOT_STUMP 15
#define FLAG_CATHLEEN_CAUGHT 16
#define FLAG_BEAT_SHINIGAMI 17
#define FLAG_BEAT_CROSS 18
#define FLAG_BEAT_CONSCRIPT 19
#define FLAG_BEAT_ENFORCER 20
#define FLAG_BEAT_SENTRY 21
#define FLAG_TESSA_GIFTED 22
#define FLAG_CHEST_LOOTED 23
#define FLAG_BIRCH_GIFTED 24
#define FLAG_SABLE_GIFTED 25
#define FLAG_CAGE_OPEN 26
#define FLAG_HAS_CAGE_KEY 27
#define FLAG_TALKED_REACH 28
#define FLAG_FOUGHT_MASON 29
#define FLAG_CAUGHT_ONCE 30
#define FLAG_ANNE_GIFTED 31
#define FLAG_BEAT_CATHLEEN 32
#define FLAG_HAS_SCROLL 33
#define FLAG_ANNE2_TOLD 34
#define FLAG_MASON2_DONE 35
#define FLAG_SOLDIER_BEATEN0 36
#define FLAG_SOLDIER_BEATEN1 37
#define FLAG_SOLDIER_BEATEN2 38
#define FLAG_N 39
#define NPC_AFTER_NONE 0
#define NPC_AFTER_BED_HEAL 1
#define NPC_AFTER_SHOP 2
#define NPC_AFTER_OREN_SHOP 3
#define NPC_AFTER_CALDER 4
#define NPC_AFTER_CATHLEEN 5
#define NPC_AFTER_SHINIGAMI 6
#define NPC_AFTER_WSOLDIER 7
#define NPC_PENDING_CROSS 0
#define NPC_PENDING_CONSCRIPT 1
#define NPC_PENDING_ENFORCER 2
#define NPC_PENDING_SENTRY 3
typedef struct {
    int if_flag, if_not, hide_if, set_flag;
    int g_item[3], g_qty[3], g_n;
    int g_sp, g_lv;
    int talk, talk_if, talk_else;
    int after, pending;
    int heal, marks;
    int take_item;
} NpcStep;
typedef struct {
    int map_id;
    char mark;
    int step0, stepn;
    int w, h;
} NpcDef;
static const NpcStep NPC_STEPS[] = {
};
static const NpcDef NPC_DEFS[] = {
};
#define NPC_DEF_N 0
#define INTERACT_BUFFER 10


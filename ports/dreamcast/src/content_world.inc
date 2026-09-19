/* AUTO-GENERATED from content/*.json PACK_HASH=7f03a1a29850762c — do not edit. python3 tools/bake_content.py */

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
    { MAP_FOREST, MAP_MARSH, 'm', 'Y', 1, 0, 0, -1 },
    { MAP_MARSH, MAP_FOREST, 'Y', 'm', 0, 0, 0, -1 },
    { MAP_CLIFFS, MAP_QUARRY, 'q', 'D', 1, 0, 0, -1 },
    { MAP_QUARRY, MAP_CLIFFS, 'D', 'q', 0, 0, 0, -1 },
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
    { MAP_MARSH, 'T', 18, { 6,0,4,0,0,0,0,0 }, 3, 4, 6, -1 },
    { MAP_QUARRY, 'T', 18, { 20,23,22,0,0,0,0,0 }, 3, 5, 7, -1 },
};
#define ENC_N 9

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
#define FLAG_BEAT_FOREST_RANGER 39
#define FLAG_BEAT_FOREST_SCOUT 40
#define FLAG_BEAT_RUINS_KEEPER 41
#define FLAG_BEAT_RUINS_WARDEN 42
#define FLAG_QUARRY_CRATE_LOOTED 43
#define FLAG_QUARRY_SHELF_SEARCHED 44
#define FLAG_N 45
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
    { 0, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 1, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, 1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 0, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 2, -1, -1, 1, -1, 0, 0, -1 },
    { -1, 0, -1, 0, { -1,-1,-1 }, { 0,0,0 }, 0, 0, 3, 3, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 4, -1, -1, 0, -1, 0, 0, -1 },
    { -1, 2, -1, 2, { 1,-1,-1 }, { 1,0,0 }, 1, -1, 0, 5, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 6, -1, -1, 0, -1, 0, 0, -1 },
    { -1, 3, -1, 3, { 0,-1,-1 }, { 1,0,0 }, 1, -1, 0, 17, -1, -1, 0, -1, 0, 0, -1 },
    { 4, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 18, -1, -1, 0, -1, 0, 0, -1 },
    { 5, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 19, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 20, -1, -1, 0, -1, 1, 0, -1 },
    { -1, 6, -1, 6, { 1,-1,-1 }, { 1,0,0 }, 1, -1, 0, 21, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 22, -1, -1, 0, -1, 0, 0, -1 },
    { -1, 7, -1, 7, { 2,-1,-1 }, { 1,0,0 }, 1, -1, 0, 23, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 24, -1, -1, 0, -1, 0, 0, -1 },
    { -1, 8, -1, 8, { 0,-1,-1 }, { 1,0,0 }, 1, -1, 0, 25, -1, -1, 0, -1, 0, 0, -1 },
    { 10, 9, -1, 9, { 0,-1,-1 }, { 1,0,0 }, 1, -1, 0, 26, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 27, -1, -1, 0, -1, 0, 0, -1 },
    { 11, 12, -1, 12, { 1,-1,-1 }, { 1,0,0 }, 1, -1, 0, 29, -1, -1, 0, -1, 0, 0, -1 },
    { -1, 13, -1, 13, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 28, -1, -1, 0, -1, 0, 0, -1 },
    { 12, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 30, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 31, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 53, -1, -1, 2, -1, 0, 0, -1 },
    { 4, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 40, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 41, -1, -1, 4, -1, 0, 0, -1 },
    { -1, 14, -1, 14, { 2,-1,-1 }, { 1,0,0 }, 1, -1, 0, 32, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 33, -1, -1, 0, -1, 0, 0, -1 },
    { -1, 11, -1, 11, { 4,-1,-1 }, { 1,0,0 }, 1, -1, 0, 34, 13, 35, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 36, -1, -1, 0, -1, 0, 0, -1 },
    { -1, 15, -1, 15, { 1,-1,-1 }, { 1,0,0 }, 1, -1, 0, 37, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 38, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, 5, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 39, -1, -1, 0, -1, 0, 0, -1 },
    { -1, 16, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 44, -1, -1, 5, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 46, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, 17, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 47, -1, -1, 6, -1, 0, 0, -1 },
    { 18, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 61, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 60, -1, -1, 7, 0, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 43, -1, -1, 0, -1, 0, 0, -1 },
    { 19, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 57, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 56, -1, -1, 7, 1, 0, 0, -1 },
    { 20, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 59, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 58, -1, -1, 7, 2, 0, 0, -1 },
    { 21, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 55, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 54, -1, -1, 7, 3, 0, 0, -1 },
    { 26, 22, -1, 22, { 8,-1,-1 }, { 1,0,0 }, 1, -1, 0, 63, -1, -1, 0, -1, 0, 0, -1 },
    { 26, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 64, -1, -1, 0, -1, 0, 0, -1 },
    { 27, -1, -1, 26, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 11, -1, -1, 0, -1, 0, 0, 9 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 10, -1, -1, 0, -1, 0, 0, -1 },
    { 26, 23, -1, 23, { 5,8,-1 }, { 1,1,0 }, 2, -1, 0, 69, -1, -1, 0, -1, 0, 25, -1 },
    { 26, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 70, -1, -1, 0, -1, 0, 0, -1 },
    { 27, -1, -1, 26, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 11, -1, -1, 0, -1, 0, 0, 9 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 10, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, 26, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, -1 },
    { 27, -1, -1, 26, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 11, -1, -1, 0, -1, 0, 0, 9 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 10, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 62, -1, -1, 3, -1, 0, 0, -1 },
    { -1, 24, -1, 24, { 5,-1,-1 }, { 1,0,0 }, 1, -1, 0, 65, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 66, -1, -1, 0, -1, 0, 0, -1 },
    { -1, 25, -1, 25, { 6,-1,-1 }, { 1,0,0 }, 1, -1, 0, 67, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 68, -1, -1, 0, -1, 0, 0, -1 },
    { -1, 28, -1, 28, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 76, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 77, -1, -1, 0, -1, 0, 0, -1 },
    { 39, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 89, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 88, -1, -1, 7, -1, 0, 0, -1 },
    { 40, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 91, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 90, -1, -1, 7, -1, 0, 0, -1 },
    { 41, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 93, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 92, -1, -1, 7, -1, 0, 0, -1 },
    { 42, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 95, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 94, -1, -1, 7, -1, 0, 0, -1 },
    { -1, 43, -1, 43, { 7,-1,-1 }, { 1,0,0 }, 1, -1, 0, 96, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 97, -1, -1, 0, -1, 0, 0, -1 },
    { -1, 44, -1, 44, { 3,-1,-1 }, { 1,0,0 }, 1, -1, 0, 98, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 99, -1, -1, 0, -1, 0, 0, -1 },
};
static const NpcDef NPC_DEFS[] = {
    { MAP_HOUSE, 'B', 0, 2, 30, 32 },
    { MAP_HOUSE, 'U', 2, 1, 40, 35 },
    { MAP_HOUSE, 'S', 3, 2, 25, 28 },
    { MAP_HOUSE, 'C', 5, 2, 20, 20 },
    { MAP_VELD, 'K', 7, 4, 30, 32 },
    { MAP_VELD, 'I', 11, 2, 30, 32 },
    { MAP_VELD, 'V', 13, 2, 30, 32 },
    { MAP_VELD, 'A', 15, 3, 30, 32 },
    { MAP_VELD, 'Q', 18, 4, 30, 32 },
    { MAP_VELD, 'J', 22, 1, 30, 32 },
    { MAP_VELD, 'E', 23, 2, 30, 32 },
    { MAP_VELD, 'M', 25, 2, 20, 20 },
    { MAP_VELD, 'G', 27, 2, 18, 18 },
    { MAP_VELD, 'L', 29, 2, 20, 20 },
    { MAP_VELD, 'X', 31, 1, 35, 30 },
    { MAP_GROVE, '8', 32, 2, 30, 32 },
    { MAP_GROVE, '9', 34, 2, 30, 32 },
    { MAP_GROVE, 'K', 36, 2, 30, 32 },
    { MAP_CAMP, 'I', 38, 1, 30, 32 },
    { MAP_CAMP, 'K', 39, 2, 30, 32 },
    { MAP_CAMP, 'A', 41, 2, 30, 32 },
    { MAP_CLIFFS, 'V', 43, 2, 30, 32 },
    { MAP_CLIFFS, 'Y', 45, 4, 30, 32 },
    { MAP_CLIFFS, 'C', 49, 4, 20, 20 },
    { MAP_CLIFFS, 'k', 53, 3, 30, 32 },
    { MAP_RUINS, 'J', 56, 1, 30, 32 },
    { MAP_RUINS, 'K', 57, 2, 30, 32 },
    { MAP_RUINS, 'A', 59, 2, 30, 32 },
    { MAP_REACH, 'Y', 61, 2, 30, 32 },
    { MAP_FOREST, '4', 63, 2, 30, 32 },
    { MAP_FOREST, '5', 65, 2, 30, 32 },
    { MAP_RUINS, '6', 67, 2, 30, 32 },
    { MAP_RUINS, '7', 69, 2, 30, 32 },
    { MAP_QUARRY, 'C', 71, 2, 20, 20 },
    { MAP_QUARRY, 'S', 73, 2, 25, 28 },
};
#define NPC_DEF_N 35
#define INTERACT_BUFFER 10


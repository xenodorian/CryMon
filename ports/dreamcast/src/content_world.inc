/* AUTO-GENERATED from content/*.json PACK_HASH=796dd1ab543ab121 — do not edit. python3 tools/bake_content.py */

/* Canonical world tables from content/world.json + items.json. */
#define XP_BASE 6
#define XP_PER_LEVEL 4
#define LEVEL_XP_MUL 10
#define LEVEL_CAP 100
#define WILD_LEVEL_CAP 50
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
#define START_BAG_INIT { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 }

typedef struct {
    int from_map, to_map;
    char tile, spawn;
    int dir;       /* facing on arrival: 0=down,1=up,2=left,3=right */
    int need;      /* 0 none, 1 tookStarter, 2 beatCalder, 3 beatShin, 4 hasScroll */
    int on_arrive; /* 0 none, 1 masonAmbush, 2 ensureSoldiers */
    int fail_talk; /* talk table index, -1 none */
} WarpDef;
static const WarpDef WARPS[] = {
    { MAP_HOUSE, MAP_VELD, 'D', 'D', 0, 1, 1, 9 },
    { MAP_VELD, MAP_HOUSE, 'D', 'D', 1, 0, 0, -1 },
    { MAP_FOREST, MAP_GROVE, 'O', 'O', 0, 0, 0, -1 },
    { MAP_GROVE, MAP_FOREST, 'O', 'O', 1, 0, 0, -1 },
    { MAP_VELD, MAP_CLIFFS, 'c', 'D', 3, 2, 0, 131 },
    { MAP_CLIFFS, MAP_VELD, 'D', 'c', 2, 0, 0, -1 },
    { MAP_GAUNTLET1, MAP_GAUNTLET2, '1', '2', 0, 0, 0, -1 },
    { MAP_GAUNTLET2, MAP_GAUNTLET1, '2', '1', 1, 0, 0, -1 },
    { MAP_GAUNTLET2, MAP_GAUNTLET3, '1', '2', 0, 0, 0, -1 },
    { MAP_GAUNTLET3, MAP_GAUNTLET2, '2', '1', 1, 0, 0, -1 },
    { MAP_GAUNTLET3, MAP_GAUNTLET4, '1', '2', 0, 0, 0, -1 },
    { MAP_GAUNTLET4, MAP_GAUNTLET3, '2', '1', 1, 0, 0, -1 },
    { MAP_GAUNTLET4, MAP_GAUNTLET5, '1', '2', 0, 0, 0, -1 },
    { MAP_GAUNTLET5, MAP_GAUNTLET4, '2', '1', 1, 0, 0, -1 },
    { MAP_GAUNTLET5, MAP_GAUNTLET6, '1', '2', 0, 0, 0, -1 },
    { MAP_GAUNTLET6, MAP_GAUNTLET5, '2', '1', 1, 0, 0, -1 },
    { MAP_CLIFFS, MAP_MARSH, 'L', 'G', 3, 0, 0, -1 },
    { MAP_MARSH, MAP_CLIFFS, 'G', 'L', 2, 0, 0, -1 },
    { MAP_MARSH, MAP_QUARRY, 'X', 'G', 3, 0, 0, -1 },
    { MAP_QUARRY, MAP_MARSH, 'G', 'X', 2, 0, 0, -1 },
    { MAP_QUARRY, MAP_CAMP, 'J', 'L', 3, 0, 0, -1 },
    { MAP_CAMP, MAP_QUARRY, 'L', 'J', 2, 0, 0, -1 },
    { MAP_VELD, MAP_RUINS, 'P', 'e', 2, 3, 0, 132 },
    { MAP_RUINS, MAP_VELD, 'e', 'P', 3, 0, 0, -1 },
    { MAP_RUINS, MAP_REACH, 'D', 'D', 2, 0, 0, -1 },
    { MAP_REACH, MAP_RUINS, 'D', 'D', 3, 0, 0, -1 },
    { MAP_VELD, MAP_GAUNTLET1, 'Z', '2', 0, 4, 0, 121 },
    { MAP_GAUNTLET1, MAP_VELD, '2', 'Z', 1, 0, 0, -1 },
    { MAP_CAMP, MAP_FOREST, 'F', 'Y', 0, 0, 0, -1 },
    { MAP_FOREST, MAP_CAMP, 'Y', 'F', 1, 0, 0, -1 },
    { MAP_WEEPINGROAD, MAP_MALKUTH, '2', 'Z', 1, 0, 0, -1 },
    { MAP_MALKUTH, MAP_WEEPINGROAD, 'Z', '2', 0, 0, 0, -1 },
    { MAP_YESOD, MAP_TAU, 'G', '1', 0, 0, 0, -1 },
    { MAP_TAU, MAP_YESOD, '1', 'G', 1, 0, 0, -1 },
    { MAP_TAU, MAP_MALKUTH, '2', 'G', 0, 0, 0, -1 },
    { MAP_MALKUTH, MAP_TAU, 'G', '2', 1, 0, 0, -1 },
    { MAP_NETZACH, MAP_QOPH, 'Z', '1', 0, 0, 0, -1 },
    { MAP_QOPH, MAP_NETZACH, '1', 'Z', 1, 0, 0, -1 },
    { MAP_QOPH, MAP_MALKUTH, '2', 'D', 0, 0, 0, -1 },
    { MAP_MALKUTH, MAP_QOPH, 'D', '2', 1, 0, 0, -1 },
    { MAP_HOD, MAP_SHIN, 'P', '1', 0, 0, 0, -1 },
    { MAP_SHIN, MAP_HOD, '1', 'P', 1, 0, 0, -1 },
    { MAP_SHIN, MAP_MALKUTH, '2', 'O', 0, 0, 0, -1 },
    { MAP_MALKUTH, MAP_SHIN, 'O', '2', 1, 0, 0, -1 },
    { MAP_NETZACH, MAP_PEH, 'G', '1', 2, 0, 0, -1 },
    { MAP_PEH, MAP_NETZACH, '1', 'G', 3, 0, 0, -1 },
    { MAP_PEH, MAP_HOD, '2', 'G', 2, 0, 0, -1 },
    { MAP_HOD, MAP_PEH, 'G', '2', 3, 0, 0, -1 },
    { MAP_HOD, MAP_RESH, 'Z', '1', 3, 0, 0, -1 },
    { MAP_RESH, MAP_HOD, '1', 'Z', 2, 0, 0, -1 },
    { MAP_RESH, MAP_YESOD, '2', 'D', 3, 0, 0, -1 },
    { MAP_YESOD, MAP_RESH, 'D', '2', 2, 0, 0, -1 },
    { MAP_NETZACH, MAP_TZADDI, 'P', '1', 2, 0, 0, -1 },
    { MAP_TZADDI, MAP_NETZACH, '1', 'P', 3, 0, 0, -1 },
    { MAP_TZADDI, MAP_YESOD, '2', 'Z', 2, 0, 0, -1 },
    { MAP_YESOD, MAP_TZADDI, 'Z', '2', 3, 0, 0, -1 },
    { MAP_TIFERET, MAP_SAMEKH, 'Q', '1', 0, 0, 0, -1 },
    { MAP_SAMEKH, MAP_TIFERET, '1', 'Q', 1, 0, 0, -1 },
    { MAP_SAMEKH, MAP_YESOD, '2', 'O', 0, 0, 0, -1 },
    { MAP_YESOD, MAP_SAMEKH, 'O', '2', 1, 0, 0, -1 },
    { MAP_TIFERET, MAP_NUN, 'P', '1', 3, 0, 0, -1 },
    { MAP_NUN, MAP_TIFERET, '1', 'P', 2, 0, 0, -1 },
    { MAP_NUN, MAP_NETZACH, '2', 'O', 3, 0, 0, -1 },
    { MAP_NETZACH, MAP_NUN, 'O', '2', 2, 0, 0, -1 },
    { MAP_TIFERET, MAP_AYIN, 'D', '1', 2, 0, 0, -1 },
    { MAP_AYIN, MAP_TIFERET, '1', 'D', 3, 0, 0, -1 },
    { MAP_AYIN, MAP_HOD, '2', 'D', 2, 0, 0, -1 },
    { MAP_HOD, MAP_AYIN, 'D', '2', 3, 0, 0, -1 },
    { MAP_CHESED, MAP_KAPH, 'D', '1', 0, 0, 0, -1 },
    { MAP_KAPH, MAP_CHESED, '1', 'D', 1, 0, 0, -1 },
    { MAP_KAPH, MAP_NETZACH, '2', 'D', 0, 0, 0, -1 },
    { MAP_NETZACH, MAP_KAPH, 'D', '2', 1, 0, 0, -1 },
    { MAP_CHESED, MAP_YOD, 'Z', '1', 2, 0, 0, -1 },
    { MAP_YOD, MAP_CHESED, '1', 'Z', 3, 0, 0, -1 },
    { MAP_YOD, MAP_TIFERET, '2', 'L', 2, 0, 0, -1 },
    { MAP_TIFERET, MAP_YOD, 'L', '2', 3, 0, 0, -1 },
    { MAP_GEVURAH, MAP_MEM, 'G', '1', 0, 0, 0, -1 },
    { MAP_MEM, MAP_GEVURAH, '1', 'G', 1, 0, 0, -1 },
    { MAP_MEM, MAP_HOD, '2', 'O', 0, 0, 0, -1 },
    { MAP_HOD, MAP_MEM, 'O', '2', 1, 0, 0, -1 },
    { MAP_GEVURAH, MAP_LAMED, 'O', '1', 3, 0, 0, -1 },
    { MAP_LAMED, MAP_GEVURAH, '1', 'O', 2, 0, 0, -1 },
    { MAP_LAMED, MAP_TIFERET, '2', 'Z', 3, 0, 0, -1 },
    { MAP_TIFERET, MAP_LAMED, 'Z', '2', 2, 0, 0, -1 },
    { MAP_CHESED, MAP_TETH, 'O', '1', 2, 0, 0, -1 },
    { MAP_TETH, MAP_CHESED, '1', 'O', 3, 0, 0, -1 },
    { MAP_TETH, MAP_GEVURAH, '2', 'Z', 2, 0, 0, -1 },
    { MAP_GEVURAH, MAP_TETH, 'Z', '2', 3, 0, 0, -1 },
    { MAP_BINAH, MAP_ZAYIN, 'Z', '1', 0, 0, 0, -1 },
    { MAP_ZAYIN, MAP_BINAH, '1', 'Z', 1, 0, 0, -1 },
    { MAP_ZAYIN, MAP_TIFERET, '2', 'J', 0, 0, 0, -1 },
    { MAP_TIFERET, MAP_ZAYIN, 'J', '2', 1, 0, 0, -1 },
    { MAP_BINAH, MAP_HETH, 'G', '1', 0, 0, 0, -1 },
    { MAP_HETH, MAP_BINAH, '1', 'G', 1, 0, 0, -1 },
    { MAP_HETH, MAP_GEVURAH, '2', 'D', 0, 0, 0, -1 },
    { MAP_GEVURAH, MAP_HETH, 'D', '2', 1, 0, 0, -1 },
    { MAP_CHOKMAH, MAP_HE, 'G', '1', 0, 0, 0, -1 },
    { MAP_HE, MAP_CHOKMAH, '1', 'G', 1, 0, 0, -1 },
    { MAP_HE, MAP_TIFERET, '2', 'G', 0, 0, 0, -1 },
    { MAP_TIFERET, MAP_HE, 'G', '2', 1, 0, 0, -1 },
    { MAP_CHOKMAH, MAP_VAU, 'Z', '1', 0, 0, 0, -1 },
    { MAP_VAU, MAP_CHOKMAH, '1', 'Z', 1, 0, 0, -1 },
    { MAP_VAU, MAP_CHESED, '2', 'G', 0, 0, 0, -1 },
    { MAP_CHESED, MAP_VAU, 'G', '2', 1, 0, 0, -1 },
    { MAP_CHOKMAH, MAP_DALETH, 'O', '1', 2, 0, 0, -1 },
    { MAP_DALETH, MAP_CHOKMAH, '1', 'O', 3, 0, 0, -1 },
    { MAP_DALETH, MAP_BINAH, '2', 'O', 2, 0, 0, -1 },
    { MAP_BINAH, MAP_DALETH, 'O', '2', 3, 0, 0, -1 },
    { MAP_KETER, MAP_GIMEL, 'G', '1', 0, 0, 0, -1 },
    { MAP_GIMEL, MAP_KETER, '1', 'G', 1, 0, 0, -1 },
    { MAP_GIMEL, MAP_TIFERET, '2', 'O', 0, 0, 0, -1 },
    { MAP_TIFERET, MAP_GIMEL, 'O', '2', 1, 0, 0, -1 },
    { MAP_KETER, MAP_ALEPH, 'D', '1', 3, 0, 0, -1 },
    { MAP_ALEPH, MAP_KETER, '1', 'D', 2, 0, 0, -1 },
    { MAP_ALEPH, MAP_CHOKMAH, '2', 'D', 3, 0, 0, -1 },
    { MAP_CHOKMAH, MAP_ALEPH, 'D', '2', 2, 0, 0, -1 },
    { MAP_KETER, MAP_BETH, 'O', '1', 2, 0, 0, -1 },
    { MAP_BETH, MAP_KETER, '1', 'O', 3, 0, 0, -1 },
    { MAP_BETH, MAP_BINAH, '2', 'D', 2, 0, 0, -1 },
    { MAP_BINAH, MAP_BETH, 'D', '2', 3, 0, 0, -1 },
};
#define WARP_N (int)(sizeof(WARPS)/sizeof(WARPS[0]))

typedef struct {
    int map_id;
    char tile;
    int rate;
    int pool[26];
    int pool_n;
    int lv_min, lv_max;
    int ty_bonus_gt; /* -1 none */
} EncDef;
static const EncDef ENCOUNTERS[] = {
    { MAP_GROVE, 'T', 18, { 3,5,6,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 5, 8, -1 },
    { MAP_CAMP, 'T', 18, { 7,18,15,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 6, 9, -1 },
    { MAP_RUINS, 'T', 18, { 2,17,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 6, 9, -1 },
    { MAP_FOREST, 'T', 18, { 6,7,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 4, 3, 5, -1 },
    { MAP_CLIFFS, 'T', 18, { 14,15,12,16,13,17,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 6, 5, 7, -1 },
    { MAP_VELD, 'T', 18, { 1,2,11,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 4, 2, 4, 14 },
    { MAP_REACH, 'T', 22, { 18,8,10,14,17,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 6, 8, 11, -1 },
    { MAP_MARSH, 'T', 18, { 6,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 4, 6, -1 },
    { MAP_QUARRY, 'T', 18, { 20,23,22,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 5, 7, -1 },
    { MAP_GAUNTLET1, 'T', 22, { 0,1,20,11,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 4, 8, 11, -1 },
    { MAP_GAUNTLET2, 'T', 22, { 3,5,6,22,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 4, 10, 13, -1 },
    { MAP_GAUNTLET3, 'T', 22, { 7,4,16,25,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 4, 12, 15, -1 },
    { MAP_GAUNTLET4, 'T', 22, { 15,14,18,24,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 4, 14, 17, -1 },
    { MAP_GAUNTLET5, 'T', 25, { 0,1,2,3,4,5,6,7,8,10,11,12,13,14,15,16,17,18,20,21,22,23,24,25,26,27 }, 26, 16, 20, -1 },
};
#define ENC_N 14

typedef struct {
    int lead_sp, lead_lv;
    int bench_sp[2], bench_lv[2], bench_n;
} TrainerKit;
static const TrainerKit TRAINER_KITS[16] = {
    { 11, 3, { 12, 14 }, { 3, 3 }, 2 },
    { 15, 7, { 13, 18 }, { 8, 9 }, 2 },
    { 16, 8, { 17, 7 }, { 9, 10 }, 2 },
    { 10, 9, { 18, 13 }, { 10, 11 }, 2 },
    { 5, 5, { 6, 0 }, { 5, 1 }, 1 },
    { 7, 5, { 3, 0 }, { 6, 1 }, 1 },
    { 4, 7, { 17, 0 }, { 7, 1 }, 1 },
    { 2, 8, { 18, 0 }, { 8, 1 }, 1 },
    { 4, 9, { 8, 0 }, { 10, 1 }, 1 },
    { 23, 4, { 22, 0 }, { 4, 1 }, 1 },
    { 20, 3, { 21, 0 }, { 3, 1 }, 1 },
    { 6, 3, { 22, 0 }, { 3, 1 }, 1 },
    { 17, 10, { 14, 0 }, { 11, 1 }, 1 },
    { 13, 12, { 7, 15 }, { 11, 11 }, 2 },
    { 28, 20, { 0, 0 }, { 1, 1 }, 0 },
    { 19, 20, { 0, 0 }, { 1, 1 }, 0 },
};
#define KIT_SENTRY 0
#define KIT_CONSCRIPT 1
#define KIT_ENFORCER 2
#define KIT_CROSS 3
#define KIT_FOREST_RANGER 4
#define KIT_FOREST_SCOUT 5
#define KIT_RUINS_KEEPER 6
#define KIT_RUINS_WARDEN 7
#define KIT_QUARTZ 8
#define KIT_QUARRY_DRILLER 9
#define KIT_MARSH_BOG 10
#define KIT_MARSH_REED 11
#define KIT_OPAL 12
#define KIT_COMMANDER_FINAL 13
#define KIT_LIEUTENANT_LEAD 14
#define KIT_HEAVENFALL_GRAVE 15
#define KIT_CATHLEEN_LV 10
#define KIT_SHINIGAMI_LEAD_LV 15
#define KIT_SHINIGAMI_B0_LV 14
#define KIT_SHINIGAMI_B1_LV 13

#define ITEM_STATUS_ALL 6
typedef struct { int kind, amount, str, agl, spc, base, status; } ItemFx;
static const ItemFx ITEM_FX[] = {
    { 1, 22, 0, 0, 0, 100, 0 },
    { 1, 12, 0, 0, 0, 100, 0 },
    { 2, 0, 4, 0, 0, 100, 0 },
    { 3, 0, -3, -2, -2, 100, 0 },
    { 4, 0, 0, 0, 0, 100, 0 },
    { 1, 40, 0, 0, 0, 100, 0 },
    { 2, 0, 0, 4, 0, 100, 0 },
    { 5, 0, 0, 0, 0, 100, 0 },
    { 4, 0, 0, 0, 0, 150, 0 },
    { 0, 0, 0, 0, 0, 100, 0 },
    { 4, 0, 0, 0, 0, 200, 0 },
    { 4, 0, 0, 0, 0, 300, 0 },
    { 4, 0, 0, 0, 0, 1000, 0 },
    { 6, 0, 0, 0, 0, 100, 0 },
    { 7, 0, 0, 0, 0, 100, 1 },
    { 7, 0, 0, 0, 0, 100, 2 },
    { 7, 0, 0, 0, 0, 100, 3 },
    { 7, 0, 0, 0, 0, 100, 4 },
    { 7, 0, 0, 0, 0, 100, 6 },
    { 0, 0, 0, 0, 0, 100, 0 },
};

#define SHOP_CRYSTAL_DEFAULT_MASK 3328
static const int SHOP_CRYSTAL_MASK[] = {
    16, /* 0: bram */
    3328, /* 1: oren */
    3328, /* 2: fenn */
    3328, /* 3: dray */
};
#define SHOP_CRYSTAL_MASK_N 4

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
#define FLAG_SAW_SHINIGAMI_ROCK 29
#define FLAG_FOUGHT_MASON 30
#define FLAG_CAUGHT_ONCE 31
#define FLAG_ANNE_GIFTED 32
#define FLAG_BEAT_CATHLEEN 33
#define FLAG_HAS_SCROLL 34
#define FLAG_ANNE2_TOLD 35
#define FLAG_MASON2_DONE 36
#define FLAG_SOLDIER_BEATEN0 37
#define FLAG_SOLDIER_BEATEN1 38
#define FLAG_SOLDIER_BEATEN2 39
#define FLAG_BEAT_FOREST_RANGER 40
#define FLAG_BEAT_FOREST_SCOUT 41
#define FLAG_BEAT_RUINS_KEEPER 42
#define FLAG_BEAT_RUINS_WARDEN 43
#define FLAG_QUARRY_CRATE_LOOTED 44
#define FLAG_QUARRY_SHELF_SEARCHED 45
#define FLAG_BEAT_MARSH_BOG 46
#define FLAG_BEAT_MARSH_REED 47
#define FLAG_BADGE_QUARTZ 48
#define FLAG_BADGE_OPAL 49
#define FLAG_BEAT_QUARRY_DRILLER 50
#define FLAG_CHOSE_HEAVENFALL 51
#define FLAG_BEAT_COMMANDER 52
#define FLAG_REVIVED_FATHER 53
#define FLAG_SHOP_FREE_BRAM 54
#define FLAG_SHOP_FREE_OREN 55
#define FLAG_SHOP_FREE_FENN 56
#define FLAG_SHOP_FREE_DRAY 57
#define FLAG_GAUNTLET_UNLOCKED 58
#define FLAG_GAUNTLET_WIPE_REGRET 59
#define FLAG_TITLE_SLAYER 60
#define FLAG_TITLE_TAMER 61
#define FLAG_BEAT_HEAVENFALL 62
#define FLAG_BEAT_LIEUTENANT_LEAD 63
#define FLAG_HEAVENFALL_REP_WARNED 64
#define FLAG_DRAY_KNIFE_OFFERED 65
#define FLAG_N 66
#define NPC_AFTER_NONE 0
#define NPC_AFTER_BED_HEAL 1
#define NPC_AFTER_SHOP 2
#define NPC_AFTER_CALDER 4
#define NPC_AFTER_CATHLEEN 5
#define NPC_AFTER_SHINIGAMI 6
#define NPC_AFTER_WSOLDIER 7
#define NPC_AFTER_PRIESTESS_TELEPORT 8
#define NPC_PENDING_CROSS 0
#define NPC_PENDING_CONSCRIPT 1
#define NPC_PENDING_ENFORCER 2
#define NPC_PENDING_SENTRY 3
#define NPC_PENDING_FOREST_RANGER 4
#define NPC_PENDING_FOREST_SCOUT 5
#define NPC_PENDING_RUINS_KEEPER 6
#define NPC_PENDING_RUINS_WARDEN 7
#define NPC_PENDING_QUARTZ 8
#define NPC_PENDING_QUARRY_DRILLER 12
#define NPC_PENDING_MARSH_BOG 9
#define NPC_PENDING_MARSH_REED 10
#define NPC_PENDING_OPAL 11
#define NPC_PENDING_COMMANDER_FINAL 13
#define NPC_PENDING_LEAD 14
#define NPC_PENDING_HEAVENFALL_GRAVE 15
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
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 4, -1, -1, 1, -1, 0, 0, -1 },
    { -1, -1, 0, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, -1 },
    { -1, 0, -1, 0, { -1,-1,-1 }, { 0,0,0 }, 0, 0, 3, 5, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 6, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, 2, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, -1 },
    { -1, 2, -1, 2, { 1,-1,-1 }, { 1,0,0 }, 1, -1, 0, 7, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 8, -1, -1, 0, -1, 0, 0, -1 },
    { -1, 3, -1, 3, { 0,-1,-1 }, { 1,0,0 }, 1, -1, 0, 18, -1, -1, 0, -1, 0, 0, -1 },
    { 4, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 19, -1, -1, 0, -1, 0, 0, -1 },
    { 5, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 20, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 21, -1, -1, 0, -1, 1, 0, -1 },
    { -1, 6, -1, 6, { 1,-1,-1 }, { 1,0,0 }, 1, -1, 0, 22, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 23, -1, -1, 0, -1, 0, 0, -1 },
    { -1, 7, -1, 7, { 2,-1,-1 }, { 1,0,0 }, 1, -1, 0, 24, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 25, -1, -1, 0, -1, 0, 0, -1 },
    { -1, 8, -1, 8, { 0,-1,-1 }, { 1,0,0 }, 1, -1, 0, 26, -1, -1, 0, -1, 0, 0, -1 },
    { 10, 9, -1, 9, { 0,-1,-1 }, { 1,0,0 }, 1, -1, 0, 27, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 28, -1, -1, 0, -1, 0, 0, -1 },
    { 11, 12, -1, 12, { 1,-1,-1 }, { 1,0,0 }, 1, -1, 0, 30, -1, -1, 0, -1, 0, 0, -1 },
    { -1, 13, -1, 13, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 29, -1, -1, 0, -1, 0, 0, -1 },
    { 12, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 31, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 32, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 54, -1, -1, 2, 0, 0, 0, -1 },
    { 4, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 41, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 42, -1, -1, 4, -1, 0, 0, -1 },
    { -1, -1, 14, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, -1 },
    { -1, 14, -1, 14, { 2,-1,-1 }, { 1,0,0 }, 1, -1, 0, 33, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 34, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, 11, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, -1 },
    { -1, 11, -1, 11, { 4,-1,-1 }, { 1,0,0 }, 1, -1, 0, 35, 13, 36, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 37, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, 5, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 40, -1, -1, 0, -1, 0, 0, -1 },
    { -1, 16, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 45, -1, -1, 5, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 47, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, 17, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 48, -1, -1, 6, -1, 0, 0, -1 },
    { 18, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 62, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 61, -1, -1, 7, 0, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 44, -1, -1, 0, -1, 0, 0, -1 },
    { 19, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 58, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 57, -1, -1, 7, 1, 0, 0, -1 },
    { 20, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 60, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 59, -1, -1, 7, 2, 0, 0, -1 },
    { 21, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 56, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 55, -1, -1, 7, 3, 0, 0, -1 },
    { 26, 22, -1, 22, { 8,-1,-1 }, { 1,0,0 }, 1, -1, 0, 64, -1, -1, 0, -1, 0, 0, -1 },
    { 26, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 65, -1, -1, 0, -1, 0, 0, -1 },
    { 27, -1, -1, 26, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 12, -1, -1, 0, -1, 0, 0, 9 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 11, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, 23, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, -1 },
    { 26, 23, -1, 23, { 5,8,-1 }, { 1,1,0 }, 2, -1, 0, 70, -1, -1, 0, -1, 0, 25, -1 },
    { 26, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 71, -1, -1, 0, -1, 0, 0, -1 },
    { 27, -1, -1, 26, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 12, -1, -1, 0, -1, 0, 0, 9 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 11, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, 26, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, -1 },
    { 27, -1, -1, 26, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 12, -1, -1, 0, -1, 0, 0, 9 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 11, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 63, -1, -1, 2, 1, 0, 0, -1 },
    { -1, 24, -1, 24, { 5,-1,-1 }, { 1,0,0 }, 1, -1, 0, 66, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 67, -1, -1, 0, -1, 0, 0, -1 },
    { -1, 25, -1, 25, { 6,-1,-1 }, { 1,0,0 }, 1, -1, 0, 68, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 69, -1, -1, 0, -1, 0, 0, -1 },
    { -1, 28, -1, 28, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 129, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 130, -1, -1, 0, -1, 0, 0, -1 },
    { 29, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, -1 },
    { 40, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 91, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 90, -1, -1, 7, 4, 0, 0, -1 },
    { 41, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 93, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 92, -1, -1, 7, 5, 0, 0, -1 },
    { 42, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 95, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 94, -1, -1, 7, 6, 0, 0, -1 },
    { 43, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 97, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 96, -1, -1, 7, 7, 0, 0, -1 },
    { -1, -1, 44, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, -1 },
    { -1, 44, -1, 44, { 7,-1,-1 }, { 1,0,0 }, 1, -1, 0, 98, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 99, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, 45, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, -1 },
    { -1, 45, -1, 45, { 3,-1,-1 }, { 1,0,0 }, 1, -1, 0, 100, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 101, -1, -1, 0, -1, 0, 0, -1 },
    { 46, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 103, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 102, -1, -1, 7, 9, 0, 0, -1 },
    { 47, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 105, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 104, -1, -1, 7, 10, 0, 0, -1 },
    { 48, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 78, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 77, -1, -1, 7, 8, 0, 0, -1 },
    { 49, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 107, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 106, -1, -1, 7, 11, 0, 0, -1 },
    { 50, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 109, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 108, -1, -1, 7, 12, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 113, -1, -1, 2, 2, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 114, -1, -1, 2, 3, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 123, -1, -1, 0, -1, 0, 0, -1 },
    { 34, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 124, -1, -1, 7, 15, 0, 0, -1 },
    { -1, -1, 63, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 126, -1, -1, 7, 14, 0, 0, -1 },
    { 34, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 133, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 134, -1, -1, 8, -1, 0, 0, -1 },
    { 17, -1, 29, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, -1 },
    { -1, -1, 29, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, -1 },
};
static const NpcDef NPC_DEFS[] = {
    { MAP_HOUSE, 'U', 0, 1, 40, 35 },
    { MAP_HOUSE, 'S', 1, 3, 25, 28 },
    { MAP_HOUSE, 'C', 4, 3, 20, 20 },
    { MAP_VELD, 'K', 7, 4, 30, 32 },
    { MAP_VELD, 'I', 11, 2, 30, 32 },
    { MAP_VELD, 'V', 13, 2, 30, 32 },
    { MAP_VELD, 'A', 15, 3, 30, 32 },
    { MAP_VELD, 'Q', 18, 4, 30, 32 },
    { MAP_VELD, 'J', 22, 1, 30, 32 },
    { MAP_VELD, 'E', 23, 2, 30, 32 },
    { MAP_VELD, 'M', 25, 3, 20, 20 },
    { MAP_VELD, 'G', 28, 3, 18, 18 },
    { MAP_VELD, 'X', 31, 1, 35, 30 },
    { MAP_GROVE, '8', 32, 2, 30, 32 },
    { MAP_GROVE, '9', 34, 2, 30, 32 },
    { MAP_GROVE, 'K', 36, 2, 30, 32 },
    { MAP_CAMP, 'I', 38, 1, 30, 32 },
    { MAP_CAMP, 'K', 39, 2, 30, 32 },
    { MAP_CAMP, 'A', 41, 2, 30, 32 },
    { MAP_CLIFFS, 'V', 43, 2, 30, 32 },
    { MAP_CLIFFS, 'Y', 45, 4, 30, 32 },
    { MAP_CLIFFS, 'C', 49, 5, 20, 20 },
    { MAP_CLIFFS, 'k', 54, 3, 30, 32 },
    { MAP_RUINS, 'J', 57, 1, 30, 32 },
    { MAP_RUINS, 'K', 58, 2, 30, 32 },
    { MAP_RUINS, 'A', 60, 2, 30, 32 },
    { MAP_REACH, 'Y', 62, 3, 30, 32 },
    { MAP_FOREST, '4', 65, 2, 30, 32 },
    { MAP_FOREST, '5', 67, 2, 30, 32 },
    { MAP_RUINS, '6', 69, 2, 30, 32 },
    { MAP_RUINS, '7', 71, 2, 30, 32 },
    { MAP_QUARRY, 'C', 73, 3, 20, 20 },
    { MAP_QUARRY, 'S', 76, 3, 25, 28 },
    { MAP_MARSH, '1', 79, 2, 30, 32 },
    { MAP_MARSH, '2', 81, 2, 30, 32 },
    { MAP_REACH, 'Q', 83, 2, 30, 32 },
    { MAP_REACH, 'O', 85, 2, 30, 32 },
    { MAP_QUARRY, '1', 87, 2, 30, 32 },
    { MAP_MARSH, 'F', 89, 1, 30, 32 },
    { MAP_CAMP, 'S', 90, 1, 30, 32 },
    { MAP_GAUNTLET6, 'G', 91, 2, 30, 32 },
    { MAP_VELD, 'S', 93, 2, 30, 32 },
    { MAP_VELD, '4', 95, 2, 30, 32 },
    { MAP_VELD, '9', 97, 1, 30, 32 },
    { MAP_VELD, 'Y', 98, 1, 30, 32 },
};
#define NPC_DEF_N 45
#define INTERACT_BUFFER 20


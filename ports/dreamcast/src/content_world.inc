/* AUTO-GENERATED from content/*.json PACK_HASH=e84fe66c0f1d4a31 — do not edit. python3 tools/bake_content.py */

/* Canonical world tables from content/world.json + items.json. */
#define XP_BASE 6
#define XP_PER_LEVEL 4
#define LEVEL_XP_MUL 10
#define LEVEL_CAP 100
#define WILD_LEVEL_CAP 60
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
#define START_BAG_INIT { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 }

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
    { MAP_VELD, MAP_WEEPINGROAD, 'O', '1', 1, 1136, 0, 288 },
    { MAP_WEEPINGROAD, MAP_VELD, '1', 'O', 0, 0, 0, -1 },
    { MAP_YESOD, MAP_TAU, 'G', '1', 0, 0, 0, -1 },
    { MAP_TAU, MAP_YESOD, '1', 'G', 1, 0, 0, -1 },
    { MAP_TAU, MAP_MALKUTH, '2', 'O', 0, 0, 0, -1 },
    { MAP_MALKUTH, MAP_TAU, 'O', '2', 1, 0, 0, -1 },
    { MAP_NETZACH, MAP_QOPH, 'Z', '1', 0, 0, 0, -1 },
    { MAP_QOPH, MAP_NETZACH, '1', 'Z', 1, 0, 0, -1 },
    { MAP_QOPH, MAP_MALKUTH, '2', 'G', 0, 0, 0, -1 },
    { MAP_MALKUTH, MAP_QOPH, 'G', '2', 1, 0, 0, -1 },
    { MAP_HOD, MAP_SHIN, 'P', '1', 0, 0, 0, -1 },
    { MAP_SHIN, MAP_HOD, '1', 'P', 1, 0, 0, -1 },
    { MAP_SHIN, MAP_MALKUTH, '2', 'D', 0, 0, 0, -1 },
    { MAP_MALKUTH, MAP_SHIN, 'D', '2', 1, 0, 0, -1 },
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
    { MAP_TIFERET, MAP_NUN, 'O', '1', 3, 0, 0, -1 },
    { MAP_NUN, MAP_TIFERET, '1', 'O', 2, 0, 0, -1 },
    { MAP_NUN, MAP_NETZACH, '2', 'O', 3, 0, 0, -1 },
    { MAP_NETZACH, MAP_NUN, 'O', '2', 2, 0, 0, -1 },
    { MAP_TIFERET, MAP_AYIN, 'J', '1', 2, 0, 0, -1 },
    { MAP_AYIN, MAP_TIFERET, '1', 'J', 3, 0, 0, -1 },
    { MAP_AYIN, MAP_HOD, '2', 'D', 2, 0, 0, -1 },
    { MAP_HOD, MAP_AYIN, 'D', '2', 3, 0, 0, -1 },
    { MAP_CHESED, MAP_KAPH, 'D', '1', 0, 0, 0, -1 },
    { MAP_KAPH, MAP_CHESED, '1', 'D', 1, 0, 0, -1 },
    { MAP_KAPH, MAP_NETZACH, '2', 'D', 0, 0, 0, -1 },
    { MAP_NETZACH, MAP_KAPH, 'D', '2', 1, 0, 0, -1 },
    { MAP_CHESED, MAP_YOD, 'Z', '1', 2, 0, 0, -1 },
    { MAP_YOD, MAP_CHESED, '1', 'Z', 3, 0, 0, -1 },
    { MAP_YOD, MAP_TIFERET, '2', 'D', 2, 0, 0, -1 },
    { MAP_TIFERET, MAP_YOD, 'D', '2', 3, 0, 0, -1 },
    { MAP_GEVURAH, MAP_MEM, 'Z', '1', 0, 0, 0, -1 },
    { MAP_MEM, MAP_GEVURAH, '1', 'Z', 1, 0, 0, -1 },
    { MAP_MEM, MAP_HOD, '2', 'O', 0, 0, 0, -1 },
    { MAP_HOD, MAP_MEM, 'O', '2', 1, 0, 0, -1 },
    { MAP_GEVURAH, MAP_LAMED, 'O', '1', 3, 0, 0, -1 },
    { MAP_LAMED, MAP_GEVURAH, '1', 'O', 2, 0, 0, -1 },
    { MAP_LAMED, MAP_TIFERET, '2', 'L', 3, 0, 0, -1 },
    { MAP_TIFERET, MAP_LAMED, 'L', '2', 2, 0, 0, -1 },
    { MAP_CHESED, MAP_TETH, 'O', '1', 2, 0, 0, -1 },
    { MAP_TETH, MAP_CHESED, '1', 'O', 3, 0, 0, -1 },
    { MAP_TETH, MAP_GEVURAH, '2', 'D', 2, 0, 0, -1 },
    { MAP_GEVURAH, MAP_TETH, 'D', '2', 3, 0, 0, -1 },
    { MAP_BINAH, MAP_ZAYIN, 'Z', '1', 0, 0, 0, -1 },
    { MAP_ZAYIN, MAP_BINAH, '1', 'Z', 1, 0, 0, -1 },
    { MAP_ZAYIN, MAP_TIFERET, '2', 'G', 0, 0, 0, -1 },
    { MAP_TIFERET, MAP_ZAYIN, 'G', '2', 1, 0, 0, -1 },
    { MAP_BINAH, MAP_HETH, 'G', '1', 0, 0, 0, -1 },
    { MAP_HETH, MAP_BINAH, '1', 'G', 1, 0, 0, -1 },
    { MAP_HETH, MAP_GEVURAH, '2', 'G', 0, 0, 0, -1 },
    { MAP_GEVURAH, MAP_HETH, 'G', '2', 1, 0, 0, -1 },
    { MAP_CHOKMAH, MAP_HE, 'G', '1', 0, 0, 0, -1 },
    { MAP_HE, MAP_CHOKMAH, '1', 'G', 1, 0, 0, -1 },
    { MAP_HE, MAP_TIFERET, '2', 'P', 0, 0, 0, -1 },
    { MAP_TIFERET, MAP_HE, 'P', '2', 1, 0, 0, -1 },
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
    { MAP_GIMEL, MAP_TIFERET, '2', 'Z', 0, 0, 0, -1 },
    { MAP_TIFERET, MAP_GIMEL, 'Z', '2', 1, 0, 0, -1 },
    { MAP_KETER, MAP_ALEPH, 'D', '1', 3, 0, 0, -1 },
    { MAP_ALEPH, MAP_KETER, '1', 'D', 2, 0, 0, -1 },
    { MAP_ALEPH, MAP_CHOKMAH, '2', 'D', 3, 0, 0, -1 },
    { MAP_CHOKMAH, MAP_ALEPH, 'D', '2', 2, 0, 0, -1 },
    { MAP_KETER, MAP_BETH, 'O', '1', 2, 0, 0, -1 },
    { MAP_BETH, MAP_KETER, '1', 'O', 3, 0, 0, -1 },
    { MAP_BETH, MAP_BINAH, '2', 'D', 2, 0, 0, -1 },
    { MAP_BINAH, MAP_BETH, 'D', '2', 3, 0, 0, -1 },
    { MAP_MALKUTH, MAP_BASEMALKUTH, 'b', 'D', 1, 0, 0, -1 },
    { MAP_BASEMALKUTH, MAP_MALKUTH, 'D', 'b', 0, 0, 0, -1 },
    { MAP_YESOD, MAP_BASEYESOD, 'b', 'D', 1, 1084, 0, 140 },
    { MAP_BASEYESOD, MAP_YESOD, 'D', 'b', 0, 0, 0, -1 },
    { MAP_NETZACH, MAP_BASENETZACH, 'b', 'D', 1, 1085, 0, 140 },
    { MAP_BASENETZACH, MAP_NETZACH, 'D', 'b', 0, 0, 0, -1 },
    { MAP_HOD, MAP_BASEHOD, 'b', 'D', 1, 1086, 0, 140 },
    { MAP_BASEHOD, MAP_HOD, 'D', 'b', 0, 0, 0, -1 },
    { MAP_TIFERET, MAP_BASETIFERET, 'b', 'D', 1, 1087, 0, 140 },
    { MAP_BASETIFERET, MAP_TIFERET, 'D', 'b', 0, 0, 0, -1 },
    { MAP_CHESED, MAP_BASECHESED, 'b', 'D', 1, 1088, 0, 140 },
    { MAP_BASECHESED, MAP_CHESED, 'D', 'b', 0, 0, 0, -1 },
    { MAP_GEVURAH, MAP_BASEGEVURAH, 'b', 'D', 1, 1089, 0, 140 },
    { MAP_BASEGEVURAH, MAP_GEVURAH, 'D', 'b', 0, 0, 0, -1 },
    { MAP_BINAH, MAP_BASEBINAH, 'b', 'D', 1, 1090, 0, 140 },
    { MAP_BASEBINAH, MAP_BINAH, 'D', 'b', 0, 0, 0, -1 },
    { MAP_CHOKMAH, MAP_BASECHOKMAH, 'b', 'D', 1, 1091, 0, 140 },
    { MAP_BASECHOKMAH, MAP_CHOKMAH, 'D', 'b', 0, 0, 0, -1 },
    { MAP_KETER, MAP_PALACEKETER, 'b', 'D', 1, 1104, 0, 141 },
    { MAP_PALACEKETER, MAP_KETER, 'D', 'b', 0, 0, 0, -1 },
    { MAP_RUINS, MAP_GHOSTCRYPT, 'w', 'D', 1, 1028, 0, 286 },
    { MAP_GHOSTCRYPT, MAP_RUINS, 'D', 'w', 0, 0, 0, -1 },
    { MAP_REACH, MAP_HAUNTEDHALL, 'w', 'D', 1, 1123, 0, 287 },
    { MAP_HAUNTEDHALL, MAP_REACH, 'D', 'w', 0, 0, 0, -1 },
    { MAP_VELD, MAP_HEROESHALL, 'w', 'D', 1, 0, 0, -1 },
    { MAP_HEROESHALL, MAP_VELD, 'D', 'w', 0, 0, 0, -1 },
    { MAP_MARSH, MAP_THIEVESDEN, 'w', 'D', 1, 0, 0, -1 },
    { MAP_THIEVESDEN, MAP_MARSH, 'D', 'w', 0, 0, 0, -1 },
    { MAP_RUINS, MAP_RUINSLIBRARY, '(', 'D', 1, 0, 0, -1 },
    { MAP_RUINSLIBRARY, MAP_RUINS, 'D', '(', 0, 0, 0, -1 },
    { MAP_RUINS, MAP_RUINSINN, ')', 'D', 1, 0, 0, -1 },
    { MAP_RUINSINN, MAP_RUINS, 'D', ')', 0, 0, 0, -1 },
    { MAP_RUINS, MAP_BRANNHOUSE, '0', 'D', 1, 0, 0, -1 },
    { MAP_BRANNHOUSE, MAP_RUINS, 'D', '0', 0, 0, 0, -1 },
    { MAP_REACH, MAP_HERMITHUT, '(', 'D', 1, 0, 0, -1 },
    { MAP_HERMITHUT, MAP_REACH, 'D', '(', 0, 0, 0, -1 },
    { MAP_REACH, MAP_SAGEHOUSE, ')', 'D', 1, 0, 0, -1 },
    { MAP_SAGEHOUSE, MAP_REACH, 'D', ')', 0, 0, 0, -1 },
    { MAP_REACH, MAP_EMPTYHOUSE, '0', 'D', 1, 0, 0, -1 },
    { MAP_EMPTYHOUSE, MAP_REACH, 'D', '0', 0, 0, 0, -1 },
    { MAP_REACH, MAP_HOLLOW, '<', '>', 2, 1111, 0, 508 },
    { MAP_HOLLOW, MAP_REACH, '>', '<', 3, 0, 0, -1 },
};
#define WARP_N (int)(sizeof(WARPS)/sizeof(WARPS[0]))

typedef struct {
    int map_id;
    char tile;
    int rate;
    int pool[39];
    int pool_n;
    int lv_min, lv_max;
    int ty_bonus_gt; /* -1 none */
} EncDef;
static const EncDef ENCOUNTERS[] = {
    { MAP_GROVE, 'T', 18, { 8,5,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 10, 13, -1 },
    { MAP_CAMP, 'T', 18, { 11,36,7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 7, 10, -1 },
    { MAP_RUINS, 'T', 18, { 34,10,17,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 13, 15, -1 },
    { MAP_FOREST, 'T', 18, { 0,6,22,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 9, 11, -1 },
    { MAP_CLIFFS, 'T', 18, { 12,39,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 4, 6, -1 },
    { MAP_VELD, 'T', 18, { 29,30,40,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 2, 4, 14 },
    { MAP_REACH, 'T', 22, { 41,24,21,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 13, 16, -1 },
    { MAP_MARSH, 'T', 18, { 20,4,32,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 5, 7, -1 },
    { MAP_QUARRY, 'T', 18, { 23,25,38,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 6, 8, -1 },
    { MAP_GAUNTLET1, 'T', 22, { 2,26,31,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 8, 11, -1 },
    { MAP_GAUNTLET2, 'T', 22, { 33,18,27,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 10, 13, -1 },
    { MAP_GAUNTLET3, 'T', 22, { 16,37,14,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 12, 15, -1 },
    { MAP_GAUNTLET4, 'T', 22, { 35,13,15,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 14, 17, -1 },
    { MAP_GAUNTLET5, 'T', 25, { 0,1,2,3,4,5,6,7,8,10,11,12,13,14,15,16,17,18,20,21,22,23,24,25,26,27,30,29,32,41,39,38,40,36,34,35,37,31,33 }, 39, 16, 20, -1 },
    { MAP_WEEPINGROAD, 'T', 18, { 42,45,48,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 18, 21, -1 },
    { MAP_TAU, 'T', 18, { 51,54,57,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 22, 25, -1 },
    { MAP_QOPH, 'T', 18, { 60,63,66,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 24, 27, -1 },
    { MAP_SHIN, 'T', 18, { 69,72,75,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 24, 27, -1 },
    { MAP_RESH, 'T', 18, { 78,80,82,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 26, 29, -1 },
    { MAP_TZADDI, 'T', 18, { 84,86,88,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 26, 29, -1 },
    { MAP_PEH, 'T', 18, { 90,92,94,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 28, 31, -1 },
    { MAP_SAMEKH, 'T', 18, { 96,98,100,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 28, 31, -1 },
    { MAP_AYIN, 'T', 18, { 101,102,103,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 30, 33, -1 },
    { MAP_NUN, 'T', 18, { 104,105,106,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 30, 33, -1 },
    { MAP_KAPH, 'T', 18, { 107,108,109,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 32, 35, -1 },
    { MAP_MEM, 'T', 18, { 110,43,46,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 32, 35, -1 },
    { MAP_LAMED, 'T', 18, { 49,52,55,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 34, 37, -1 },
    { MAP_YOD, 'T', 18, { 58,61,64,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 34, 37, -1 },
    { MAP_HE, 'T', 18, { 67,70,73,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 36, 39, -1 },
    { MAP_TETH, 'T', 18, { 76,79,81,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 36, 39, -1 },
    { MAP_ZAYIN, 'T', 18, { 83,85,87,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 36, 39, -1 },
    { MAP_GIMEL, 'T', 18, { 89,91,93,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 38, 41, -1 },
    { MAP_HETH, 'T', 18, { 95,97,99,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 38, 41, -1 },
    { MAP_VAU, 'T', 18, { 44,47,50,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 38, 41, -1 },
    { MAP_DALETH, 'T', 18, { 53,56,59,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 40, 43, -1 },
    { MAP_ALEPH, 'T', 18, { 62,65,68,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 42, 45, -1 },
    { MAP_BETH, 'T', 18, { 71,74,77,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 3, 42, 45, -1 },
    { MAP_HOLLOW, 'T', 20, { 58,58,58,105,105,105,70,70,70,74,74,74,44,44,44,65,95,71,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, 18, 45, 55, -1 },
};
#define ENC_N 38

#define KIT_BENCH_MAX 5
typedef struct {
    int lead_sp, lead_lv;
    int bench_sp[KIT_BENCH_MAX], bench_lv[KIT_BENCH_MAX], bench_n;
    const char *name; /* kit `name`, DC text (mercy menu header) */
    int hp_mul_pct; /* kit `hpMul` x100: boss HP, applied by leg3_start_battle() */
} TrainerKit;
static const TrainerKit TRAINER_KITS[65] = {
    { 11, 5, { 12, 14, 0, 0, 0 }, { 5, 6, 1, 1, 1 }, 2, "SENTRY", 100 },
    { 15, 9, { 13, 18, 0, 0, 0 }, { 9, 10, 1, 1, 1 }, 2, "CONSCRIPT", 100 },
    { 16, 10, { 17, 7, 0, 0, 0 }, { 10, 11, 1, 1, 1 }, 2, "ENFORCER", 100 },
    { 10, 12, { 18, 13, 0, 0, 0 }, { 12, 13, 1, 1, 1 }, 2, "WARDEN CROSS", 100 },
    { 5, 11, { 6, 0, 0, 0, 0 }, { 11, 1, 1, 1, 1 }, 1, "RANGER", 100 },
    { 7, 11, { 3, 0, 0, 0, 0 }, { 12, 1, 1, 1, 1 }, 1, "SCOUT", 100 },
    { 4, 14, { 17, 0, 0, 0, 0 }, { 14, 1, 1, 1, 1 }, 1, "KEEPER", 100 },
    { 2, 15, { 18, 0, 0, 0, 0 }, { 15, 1, 1, 1, 1 }, 1, "WARDEN", 100 },
    { 4, 15, { 8, 0, 0, 0, 0 }, { 16, 1, 1, 1, 1 }, 1, "QUARTZ", 100 },
    { 23, 7, { 22, 0, 0, 0, 0 }, { 8, 1, 1, 1, 1 }, 1, "DRILLER", 100 },
    { 20, 6, { 21, 0, 0, 0, 0 }, { 6, 1, 1, 1, 1 }, 1, "BOGWALKER", 100 },
    { 6, 6, { 22, 0, 0, 0, 0 }, { 7, 1, 1, 1, 1 }, 1, "REEDGUARD", 100 },
    { 17, 16, { 14, 0, 0, 0, 0 }, { 17, 1, 1, 1, 1 }, 1, "OPAL", 100 },
    { 13, 17, { 7, 15, 0, 0, 0 }, { 16, 16, 1, 1, 1 }, 2, "COMMANDER", 100 },
    { 15, 22, { 14, 13, 7, 10, 28 }, { 22, 23, 23, 24, 26 }, 5, "LIEUTENANT LEAD", 100 },
    { 19, 20, { 0, 0, 0, 0, 0 }, { 1, 1, 1, 1, 1 }, 0, "HEAVENFALL", 100 },
    { 42, 23, { 0, 0, 0, 0, 0 }, { 1, 1, 1, 1, 1 }, 0, "BASE GUARD", 100 },
    { 48, 24, { 45, 0, 0, 0, 0 }, { 23, 1, 1, 1, 1 }, 1, "BASE GUARD", 100 },
    { 52, 26, { 51, 75, 0, 0, 0 }, { 24, 24, 1, 1, 1 }, 2, "GENERAL HARROW", 200 },
    { 57, 25, { 0, 0, 0, 0, 0 }, { 1, 1, 1, 1, 1 }, 0, "BASE GUARD", 100 },
    { 54, 26, { 51, 0, 0, 0, 0 }, { 25, 1, 1, 1, 1 }, 1, "BASE GUARD", 100 },
    { 55, 28, { 54, 78, 0, 0, 0 }, { 26, 26, 1, 1, 1 }, 2, "GENERAL ASHGROVE", 200 },
    { 63, 27, { 0, 0, 0, 0, 0 }, { 1, 1, 1, 1, 1 }, 0, "BASE GUARD", 100 },
    { 60, 28, { 66, 0, 0, 0, 0 }, { 27, 1, 1, 1, 1 }, 1, "BASE GUARD", 100 },
    { 61, 30, { 60, 82, 0, 0, 0 }, { 28, 28, 1, 1, 1 }, 2, "GENERAL STROUD", 200 },
    { 72, 29, { 0, 0, 0, 0, 0 }, { 1, 1, 1, 1, 1 }, 0, "BASE GUARD", 100 },
    { 69, 30, { 75, 0, 0, 0, 0 }, { 29, 1, 1, 1, 1 }, 1, "BASE GUARD", 100 },
    { 58, 32, { 69, 90, 0, 0, 0 }, { 30, 30, 1, 1, 1 }, 2, "GENERAL VALE", 200 },
    { 96, 31, { 0, 0, 0, 0, 0 }, { 1, 1, 1, 1, 1 }, 0, "BASE GUARD", 100 },
    { 100, 32, { 98, 0, 0, 0, 0 }, { 31, 1, 1, 1, 1 }, 1, "BASE GUARD", 100 },
    { 107, 34, { 86, 43, 0, 0, 0 }, { 32, 32, 1, 1, 1 }, 2, "GENERAL KESSLER", 200 },
    { 108, 34, { 0, 0, 0, 0, 0 }, { 1, 1, 1, 1, 1 }, 0, "BASE GUARD", 100 },
    { 109, 35, { 84, 0, 0, 0, 0 }, { 34, 1, 1, 1, 1 }, 1, "BASE GUARD", 100 },
    { 85, 37, { 109, 73, 0, 0, 0 }, { 35, 35, 1, 1, 1 }, 2, "GENERAL MORROW", 200 },
    { 110, 37, { 0, 0, 0, 0, 0 }, { 1, 1, 1, 1, 1 }, 0, "BASE GUARD", 100 },
    { 43, 38, { 46, 0, 0, 0, 0 }, { 37, 1, 1, 1, 1 }, 1, "BASE GUARD", 100 },
    { 68, 40, { 67, 93, 0, 0, 0 }, { 38, 38, 1, 1, 1 }, 2, "GENERAL CRANE", 200 },
    { 83, 40, { 0, 0, 0, 0, 0 }, { 1, 1, 1, 1, 1 }, 0, "BASE GUARD", 100 },
    { 85, 41, { 87, 0, 0, 0, 0 }, { 40, 1, 1, 1, 1 }, 1, "BASE GUARD", 100 },
    { 50, 43, { 99, 81, 0, 0, 0 }, { 41, 41, 1, 1, 1 }, 2, "GENERAL BLACKWOOD", 200 },
    { 67, 43, { 0, 0, 0, 0, 0 }, { 1, 1, 1, 1, 1 }, 0, "BASE GUARD", 100 },
    { 47, 44, { 44, 0, 0, 0, 0 }, { 43, 1, 1, 1, 1 }, 1, "BASE GUARD", 100 },
    { 65, 46, { 95, 102, 0, 0, 0 }, { 44, 44, 1, 1, 1 }, 2, "GENERAL SORREL", 200 },
    { 89, 47, { 0, 0, 0, 0, 0 }, { 1, 1, 1, 1, 1 }, 0, "ROYAL GUARD", 100 },
    { 93, 48, { 91, 0, 0, 0, 0 }, { 47, 1, 1, 1, 1 }, 1, "ROYAL GUARD", 100 },
    { 71, 50, { 74, 77, 44, 56, 62 }, { 48, 48, 48, 48, 48 }, 5, "WEEPING KING NERO", 150 },
    { 19, 55, { 0, 0, 0, 0, 0 }, { 1, 1, 1, 1, 1 }, 0, "HEAVENFALL", 100 },
    { 69, 15, { 57, 0, 0, 0, 0 }, { 14, 1, 1, 1, 1 }, 1, "SOLDIER'S GHOST", 100 },
    { 106, 17, { 69, 90, 0, 0, 0 }, { 16, 16, 1, 1, 1 }, 2, "SERGEANT'S GHOST", 100 },
    { 70, 19, { 69, 0, 0, 0, 0 }, { 18, 1, 1, 1, 1 }, 1, "BOUND CRYPTLAMP", 100 },
    { 105, 21, { 106, 90, 70, 71, 0 }, { 19, 19, 20, 21, 1 }, 4, "MOURNER VESK", 100 },
    { 5, 17, { 36, 37, 0, 0, 0 }, { 16, 18, 1, 1, 1 }, 2, "RED MALLORY", 100 },
    { 25, 19, { 23, 37, 27, 0, 0 }, { 18, 19, 20, 1, 1 }, 3, "SILAS THE FENCE", 100 },
    { 30, 16, { 31, 0, 0, 0, 0 }, { 17, 1, 1, 1, 1 }, 1, "SIR ALDOUS", 100 },
    { 34, 19, { 10, 14, 0, 0, 0 }, { 18, 19, 1, 1, 1 }, 2, "DAME BRIN", 100 },
    { 39, 21, { 12, 3, 15, 0, 0 }, { 20, 21, 22, 1, 1 }, 3, "CAPTAIN ROOK", 100 },
    { 43, 34, { 110, 46, 109, 0, 0 }, { 33, 34, 35, 1, 1 }, 3, "KNIFE-HAND GARROW", 100 },
    { 59, 42, { 53, 56, 91, 50, 0 }, { 41, 42, 41, 43, 1 }, 4, "DESERTER KAEL", 100 },
    { 13, 18, { 14, 33, 0, 0, 0 }, { 17, 17, 1, 1, 1 }, 2, "HERMIT OSK", 100 },
    { 107, 31, { 109, 43, 108, 0, 0 }, { 30, 30, 31, 1, 1 }, 3, "HERMIT OSK", 100 },
    { 50, 47, { 95, 44, 47, 56, 0 }, { 45, 46, 46, 47, 1 }, 4, "HERMIT OSK", 100 },
    { 15, 55, { 59, 65, 53, 18, 14 }, { 52, 52, 53, 53, 54 }, 5, "CALDER", 100 },
    { 105, 50, { 109, 97, 0, 0, 0 }, { 48, 49, 1, 1, 1 }, 2, "LOST RANGER", 100 },
    { 71, 52, { 106, 70, 74, 0, 0 }, { 50, 51, 51, 1, 1 }, 3, "HOLLOW SHADE", 100 },
    { 56, 55, { 50, 47, 44, 68, 0 }, { 53, 53, 54, 54, 1 }, 4, "HOLLOW WARDEN", 100 },
};
#define KIT_LEG3_FIRST 16
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
#define KIT_BASE_MALKUTH_A 16
#define KIT_BASE_MALKUTH_B 17
#define KIT_GENERAL_HARROW 18
#define KIT_BASE_YESOD_A 19
#define KIT_BASE_YESOD_B 20
#define KIT_GENERAL_ASHGROVE 21
#define KIT_BASE_NETZACH_A 22
#define KIT_BASE_NETZACH_B 23
#define KIT_GENERAL_STROUD 24
#define KIT_BASE_HOD_A 25
#define KIT_BASE_HOD_B 26
#define KIT_GENERAL_VALE 27
#define KIT_BASE_TIFERET_A 28
#define KIT_BASE_TIFERET_B 29
#define KIT_GENERAL_KESSLER 30
#define KIT_BASE_CHESED_A 31
#define KIT_BASE_CHESED_B 32
#define KIT_GENERAL_MORROW 33
#define KIT_BASE_GEVURAH_A 34
#define KIT_BASE_GEVURAH_B 35
#define KIT_GENERAL_CRANE 36
#define KIT_BASE_BINAH_A 37
#define KIT_BASE_BINAH_B 38
#define KIT_GENERAL_BLACKWOOD 39
#define KIT_BASE_CHOKMAH_A 40
#define KIT_BASE_CHOKMAH_B 41
#define KIT_GENERAL_SORREL 42
#define KIT_PALACE_GUARD_A 43
#define KIT_PALACE_GUARD_B 44
#define KIT_NERO 45
#define KIT_HEAVENFALL_FINAL 46
#define KIT_GHOST_SOLDIER_A 47
#define KIT_GHOST_SOLDIER_B 48
#define KIT_GHOST_ORIEL 49
#define KIT_MOURNER_VESK 50
#define KIT_RED_MALLORY 51
#define KIT_SILAS_FENCE 52
#define KIT_SIR_ALDOUS 53
#define KIT_DAME_BRIN 54
#define KIT_CAPTAIN_ROOK 55
#define KIT_GARROW_OUTLAW 56
#define KIT_KAEL_DESERTER 57
#define KIT_OSK_ONE 58
#define KIT_OSK_TWO 59
#define KIT_OSK_THREE 60
#define KIT_CALDER_POST 61
#define KIT_HOLLOW_RANGER 62
#define KIT_HOLLOW_SHADE 63
#define KIT_HOLLOW_WARDEN 64
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
    { 0, 0, 0, 0, 0, 100, 0 },
    { 0, 0, 0, 0, 0, 100, 0 },
    { 0, 0, 0, 0, 0, 100, 0 },
    { 0, 0, 0, 0, 0, 100, 0 },
    { 0, 0, 0, 0, 0, 100, 0 },
    { 0, 0, 0, 0, 0, 100, 0 },
    { 0, 0, 0, 0, 0, 100, 0 },
    { 0, 0, 0, 0, 0, 100, 0 },
    { 0, 0, 0, 0, 0, 100, 0 },
    { 0, 0, 0, 0, 0, 100, 0 },
    { 0, 0, 0, 0, 0, 100, 0 },
    { 0, 0, 0, 0, 0, 100, 0 },
};

#define SHOP_CRYSTAL_DEFAULT_MASK 3328
static const int SHOP_CRYSTAL_MASK[] = {
    16, /* 0: bram */
    3328, /* 1: oren */
    3328, /* 2: fenn */
    3328, /* 3: dray */
    3328, /* 4: hale */
};
#define SHOP_CRYSTAL_MASK_N 5
static const int SHOP_NOT_SOLD_MASK[] = {
    1048576, /* 0: bram */
    0, /* 1: oren */
    0, /* 2: fenn */
    0, /* 3: dray */
    0, /* 4: hale */
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
#define FLAG_BEAT_BASE_MALKUTH_A 66
#define FLAG_BEAT_BASE_MALKUTH_B 67
#define FLAG_BEAT_BASE_YESOD_A 68
#define FLAG_BEAT_BASE_YESOD_B 69
#define FLAG_BEAT_BASE_NETZACH_A 70
#define FLAG_BEAT_BASE_NETZACH_B 71
#define FLAG_BEAT_BASE_HOD_A 72
#define FLAG_BEAT_BASE_HOD_B 73
#define FLAG_BEAT_BASE_TIFERET_A 74
#define FLAG_BEAT_BASE_TIFERET_B 75
#define FLAG_BEAT_BASE_CHESED_A 76
#define FLAG_BEAT_BASE_CHESED_B 77
#define FLAG_BEAT_BASE_GEVURAH_A 78
#define FLAG_BEAT_BASE_GEVURAH_B 79
#define FLAG_BEAT_BASE_BINAH_A 80
#define FLAG_BEAT_BASE_BINAH_B 81
#define FLAG_BEAT_BASE_CHOKMAH_A 82
#define FLAG_BEAT_BASE_CHOKMAH_B 83
#define FLAG_MEDAL_BRONZE_STAR 84
#define FLAG_MEDAL_PURPLE_HEART 85
#define FLAG_MEDAL_POW_MEDAL 86
#define FLAG_MEDAL_SILVER_STAR 87
#define FLAG_MEDAL_GOLD_STAR 88
#define FLAG_MEDAL_LEGION_OF_MERIT 89
#define FLAG_MEDAL_FLYING_CROSS 90
#define FLAG_MEDAL_SERVICE_CROSS 91
#define FLAG_MEDAL_OF_HONOR 92
#define FLAG_ARRESTED_HARROW 93
#define FLAG_ARRESTED_ASHGROVE 94
#define FLAG_ARRESTED_STROUD 95
#define FLAG_ARRESTED_VALE 96
#define FLAG_ARRESTED_KESSLER 97
#define FLAG_ARRESTED_MORROW 98
#define FLAG_ARRESTED_CRANE 99
#define FLAG_ARRESTED_BLACKWOOD 100
#define FLAG_ARRESTED_SORREL 101
#define FLAG_BEAT_PALACE_GUARD_A 102
#define FLAG_BEAT_PALACE_GUARD_B 103
#define FLAG_HAS_GOLDEN_SHACKLES 104
#define FLAG_BEAT_NERO 105
#define FLAG_NERO_TRIED 106
#define FLAG_TITLE_KINGSLAYER 107
#define FLAG_FATHER_ABANDONED 108
#define FLAG_TITLE_GODSLAYER 109
#define FLAG_TITLE_BLOODY 110
#define FLAG_LEG3_ENDED 111
#define FLAG_TALKED_MARN 112
#define FLAG_SHOP_FREE_HALE 113
#define FLAG_CITIZEN_THANKED_MALKUTH 114
#define FLAG_CITIZEN_THANKED_YESOD 115
#define FLAG_CITIZEN_THANKED_NETZACH 116
#define FLAG_CITIZEN_THANKED_HOD 117
#define FLAG_CITIZEN_THANKED_TIFERET 118
#define FLAG_CITIZEN_THANKED_CHESED 119
#define FLAG_CITIZEN_THANKED_GEVURAH 120
#define FLAG_CITIZEN_THANKED_BINAH 121
#define FLAG_CITIZEN_THANKED_CHOKMAH 122
#define FLAG_JOINED_GHOST 123
#define FLAG_ROBBED_INES 124
#define FLAG_ROBBED_TOMAS 125
#define FLAG_ROBBED_ORIEL 126
#define FLAG_PRAYED_CLIFFS 127
#define FLAG_PRAYED_QUARRY 128
#define FLAG_PRAYED_FOREST 129
#define FLAG_EXPELLED_GHOST_A 130
#define FLAG_EXPELLED_GHOST_B 131
#define FLAG_EXPELLED_ORIEL 132
#define FLAG_BEAT_VESK 133
#define FLAG_ARRESTED_VESK 134
#define FLAG_EXECUTED_VESK 135
#define FLAG_VEIL_LIFTED 136
#define FLAG_JOINED_HEROES 137
#define FLAG_JOINED_THIEVES 138
#define FLAG_BEAT_MALLORY 139
#define FLAG_ARRESTED_MALLORY 140
#define FLAG_EXECUTED_MALLORY 141
#define FLAG_PAID_MALLORY 142
#define FLAG_BEAT_SILAS 143
#define FLAG_ARRESTED_SILAS 144
#define FLAG_EXECUTED_SILAS 145
#define FLAG_PAID_SILAS 146
#define FLAG_GAVE_GLASSWISP 147
#define FLAG_GAVE_STARDROP 148
#define FLAG_GAVE_MOONVEIL 149
#define FLAG_BEAT_ALDOUS 150
#define FLAG_THREATENED_ALDOUS 151
#define FLAG_EXECUTED_ALDOUS 152
#define FLAG_PAID_ALDOUS 153
#define FLAG_BEAT_BRIN 154
#define FLAG_THREATENED_BRIN 155
#define FLAG_EXECUTED_BRIN 156
#define FLAG_PAID_BRIN 157
#define FLAG_BEAT_ROOK 158
#define FLAG_THREATENED_ROOK 159
#define FLAG_EXECUTED_ROOK 160
#define FLAG_PAID_ROOK 161
#define FLAG_PICKED_WATCH 162
#define FLAG_GAVE_WATCH 163
#define FLAG_ROLO_FOUND 164
#define FLAG_ROLO_HOME 165
#define FLAG_GAVE_CRYMARE 166
#define FLAG_PIP_FOUND 167
#define FLAG_PIP_HOME 168
#define FLAG_GAVE_BOLTLAMB 169
#define FLAG_PICKED_LOCKET 170
#define FLAG_GAVE_LOCKET 171
#define FLAG_BEAT_GARROW 172
#define FLAG_ARRESTED_GARROW 173
#define FLAG_EXECUTED_GARROW 174
#define FLAG_PAID_GARROW 175
#define FLAG_TILLY_FOUND 176
#define FLAG_TILLY_HOME 177
#define FLAG_GAVE_WHEELHOG 178
#define FLAG_PICKED_MAP 179
#define FLAG_GAVE_MAP 180
#define FLAG_BEAT_KAEL 181
#define FLAG_ARRESTED_KAEL 182
#define FLAG_EXECUTED_KAEL 183
#define FLAG_PAID_KAEL 184
#define FLAG_IONA_FOUND 185
#define FLAG_IONA_HOME 186
#define FLAG_GAVE_ARCANOX 187
#define FLAG_TALKED_WYN 188
#define FLAG_LIBRARY_DEX10 189
#define FLAG_LIBRARY_DEX25 190
#define FLAG_LIBRARY_DEX50 191
#define FLAG_LIBRARY_DEX80 192
#define FLAG_LIBRARY_DEX_ALL 193
#define FLAG_BRANN_ASKED 194
#define FLAG_GAVE_LETTER 195
#define FLAG_BRANN_DONE 196
#define FLAG_BEAT_OSK1 197
#define FLAG_BEAT_OSK2 198
#define FLAG_BEAT_OSK3 199
#define FLAG_ILSE_GIFT 200
#define FLAG_TALKED_ILSE 201
#define FLAG_TALKED_MAREN 202
#define FLAG_PICKED_DOLL 203
#define FLAG_MAREN_REST 204
#define FLAG_TAM_ASKED 205
#define FLAG_LINA_ASKED 206
#define FLAG_JUNO_ASKED 207
#define FLAG_BET_ASKED 208
#define FLAG_COBB_ASKED 209
#define FLAG_SERA_ASKED 210
#define FLAG_DUNN_ASKED 211
#define FLAG_HESSE_ASKED 212
#define FLAG_VOSS_ASKED 213
#define FLAG_LUNE_ASKED 214
#define FLAG_HOLT_ASKED 215
#define FLAG_ANSELM_ASKED 216
#define FLAG_RHEE_ASKED 217
#define FLAG_TALKED_OSK 218
#define FLAG_BEAT_CALDER_POST 219
#define FLAG_DAGNY_ASKED 220
#define FLAG_SHOWED_CINDERMITE 221
#define FLAG_FENWICK_ASKED 222
#define FLAG_SHOWED_CHILLNEWT 223
#define FLAG_MET_HOLLOW_KEEPER 224
#define FLAG_BEAT_HOLLOW_RANGER 225
#define FLAG_BEAT_HOLLOW_SHADE 226
#define FLAG_BEAT_HOLLOW_WARDEN 227
#define FLAG_HOLLOW_REWARDED 228
#define FLAG_N 229
#define FLAG_ITEM_BASE 2000
#define FLAG_MON_BASE 3000
#define FLAG_REP_POS 4000
#define FLAG_REP_NEG 4001
#define FLAG_DEX_BASE 5000
static const short FLAG_TO_SAVE[FLAG_N] = { 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, -1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, -1, 36, 62, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226 };
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
    int take_item[3], take_n; /* takeItem: one id or a list of up to 3 */
    int take_mon; /* species index handed over, -1 none */
    int rep;      /* reputation change (step key `rep`) */
} NpcStep;
typedef struct {
    int map_id;
    char mark;
    int step0, stepn;
    int w, h;
} NpcDef;
static const NpcStep NPC_STEPS[] = {
    { -1, -1, 53, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 0, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, 1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 0, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 4, -1, -1, 1, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 0, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 0, -1, 0, { -1,-1,-1 }, { 0,0,0 }, 0, 0, 3, 5, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 6, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 2, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 2, -1, 2, { 1,-1,-1 }, { 1,0,0 }, 1, -1, 0, 7, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 8, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 3, -1, 3, { 0,-1,-1 }, { 1,0,0 }, 1, -1, 0, 18, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 4, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 19, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 5, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 20, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 21, -1, -1, 0, -1, 1, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 6, -1, 6, { 1,-1,-1 }, { 1,0,0 }, 1, -1, 0, 22, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 23, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 7, -1, 7, { 2,-1,-1 }, { 1,0,0 }, 1, -1, 0, 24, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 25, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 8, -1, 8, { 0,-1,-1 }, { 1,0,0 }, 1, -1, 0, 26, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 10, 9, -1, 9, { 0,-1,-1 }, { 1,0,0 }, 1, -1, 0, 27, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 28, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 11, 12, -1, 12, { 1,-1,-1 }, { 1,0,0 }, 1, -1, 0, 30, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 13, -1, 13, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 29, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 12, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 31, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 32, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 54, -1, -1, 2, 0, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 111, 219, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 486, -1, -1, 7, 145, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 219, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 488, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 4, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 41, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 42, -1, -1, 4, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 14, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 14, -1, 14, { 2,-1,-1 }, { 1,0,0 }, 1, -1, 0, 33, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 34, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 11, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 11, -1, 11, { 4,-1,-1 }, { 1,0,0 }, 1, -1, 0, 35, 13, 36, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 37, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 16, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 16, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 45, -1, -1, 5, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 47, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -18, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 17, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 48, -1, -1, 6, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 18, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 62, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 61, -1, -1, 7, 0, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 52, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 232, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 53, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 110, -1, -1, 7, 13, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 51, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 111, -1, -1, 7, 13, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 44, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 19, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 58, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 57, -1, -1, 7, 1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 20, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 60, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 59, -1, -1, 7, 2, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 21, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 56, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 55, -1, -1, 7, 3, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 26, 22, -1, 22, { 8,-1,-1 }, { 1,0,0 }, 1, -1, 0, 64, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 26, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 65, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 27, -1, -1, 26, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 12, -1, -1, 0, -1, 0, 0, { 9, -1, -1 }, 1, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 11, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 23, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 26, 23, -1, 23, { 5,8,-1 }, { 1,1,0 }, 2, -1, 0, 70, -1, -1, 0, -1, 0, 25, { -1, -1, -1 }, 0, -1, 0 },
    { 26, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 71, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 27, -1, -1, 26, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 12, -1, -1, 0, -1, 0, 0, { 9, -1, -1 }, 1, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 11, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 26, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 27, -1, -1, 26, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 12, -1, -1, 0, -1, 0, 0, { 9, -1, -1 }, 1, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 11, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 63, -1, -1, 2, 1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 24, -1, 24, { 5,-1,-1 }, { 1,0,0 }, 1, -1, 0, 66, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 67, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 25, -1, 25, { 6,-1,-1 }, { 1,0,0 }, 1, -1, 0, 68, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 69, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 28, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, 28, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 129, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 40, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 91, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 90, -1, -1, 7, 4, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 41, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 93, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 92, -1, -1, 7, 5, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 42, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 95, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 94, -1, -1, 7, 6, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 43, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 97, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 96, -1, -1, 7, 7, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 44, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 44, -1, 44, { 7,-1,-1 }, { 1,0,0 }, 1, -1, 0, 98, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 99, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 45, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 45, -1, 45, { 3,-1,-1 }, { 1,0,0 }, 1, -1, 0, 100, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 101, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 46, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 103, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 102, -1, -1, 7, 9, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 47, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 105, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 104, -1, -1, 7, 10, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 48, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 78, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 77, -1, -1, 7, 8, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 49, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 107, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 106, -1, -1, 7, 11, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 50, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 109, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 108, -1, -1, 7, 12, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 113, -1, -1, 2, 2, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 114, -1, -1, 2, 3, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 62, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 193, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 34, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 123, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 34, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 124, -1, -1, 7, 15, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 63, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 17, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 195, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 126, -1, -1, 7, 14, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 34, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 133, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 53, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 194, -1, -1, 8, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 134, -1, -1, 8, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -19, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 29, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 17, -1, -1, 29, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 135, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 29, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 66, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 196, -1, -1, 7, 100, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 67, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 198, -1, -1, 7, 101, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 84, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 144, -1, -1, 7, 102, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 68, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 200, -1, -1, 7, 103, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 69, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 202, -1, -1, 7, 104, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 85, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 148, -1, -1, 7, 105, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 70, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 204, -1, -1, 7, 106, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 71, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 206, -1, -1, 7, 107, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 86, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 152, -1, -1, 7, 108, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 72, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 208, -1, -1, 7, 109, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 73, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 210, -1, -1, 7, 110, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 87, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 156, -1, -1, 7, 111, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 74, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 212, -1, -1, 7, 112, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 75, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 214, -1, -1, 7, 113, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 88, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 160, -1, -1, 7, 114, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 76, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 216, -1, -1, 7, 115, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 77, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 218, -1, -1, 7, 116, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 89, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 164, -1, -1, 7, 117, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 78, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 220, -1, -1, 7, 118, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 79, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 222, -1, -1, 7, 119, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 90, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 168, -1, -1, 7, 120, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 80, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 224, -1, -1, 7, 121, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 81, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 226, -1, -1, 7, 122, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 91, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 172, -1, -1, 7, 123, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 82, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 228, -1, -1, 7, 124, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 83, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 230, -1, -1, 7, 125, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 92, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 176, -1, -1, 7, 126, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 102, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 136, -1, -1, 7, 127, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 103, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 138, -1, -1, 7, 128, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 105, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 180, -1, -1, 7, 129, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 233, -1, -1, 0, -1, 1, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 234, -1, -1, 2, 4, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 2029, 195, -1, 195, { 30,-1,-1 }, { 1,0,0 }, 1, -1, 0, 466, -1, -1, 0, -1, 0, 0, { 29, -1, -1 }, 1, -1, 0 },
    { 111, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 501, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 112, -1, 112, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 235, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 104, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 237, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 236, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 84, 114, -1, 114, { 0,-1,-1 }, { 2,0,0 }, 1, -1, 0, 239, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 84, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 240, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 238, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 85, 115, -1, 115, { 1,-1,-1 }, { 2,0,0 }, 1, -1, 0, 242, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 85, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 243, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 241, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 86, 116, -1, 116, { 5,-1,-1 }, { 1,0,0 }, 1, -1, 0, 245, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 86, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 246, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 244, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 87, 117, -1, 117, { 6,-1,-1 }, { 1,0,0 }, 1, -1, 0, 248, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 87, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 249, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 247, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 88, 118, -1, 118, { 8,-1,-1 }, { 1,0,0 }, 1, -1, 0, 251, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 88, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 252, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 250, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 89, 119, -1, 119, { 18,-1,-1 }, { 1,0,0 }, 1, -1, 0, 254, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 89, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 255, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 253, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 90, 120, -1, 120, { 10,-1,-1 }, { 1,0,0 }, 1, -1, 0, 257, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 90, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 258, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 256, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 91, 121, -1, 121, { 11,-1,-1 }, { 1,0,0 }, 1, -1, 0, 260, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 91, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 261, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 259, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 92, 122, -1, 122, { 18,-1,-1 }, { 2,0,0 }, 1, -1, 0, 263, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 92, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 264, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 262, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 123, -1, 123, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 265, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 136, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 275, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 133, -1, -1, 136, { 25,-1,-1 }, { 1,0,0 }, 1, -1, 0, 273, 134, 274, 0, -1, 0, 0, { 22, 23, 24 }, 3, -1, 0 },
    { -1, 2022, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 266, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 2023, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 266, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 2024, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 266, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 127, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 267, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 128, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 267, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 129, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 267, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 132, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 268, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 269, -1, -1, 7, 134, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 124, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 282, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 123, -1, -1, 124, { 22,-1,-1 }, { 1,0,0 }, 1, -1, 0, 277, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, -3 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 276, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 125, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 282, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 123, -1, -1, 125, { 23,-1,-1 }, { 1,0,0 }, 1, -1, 0, 279, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, -3 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 278, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 126, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 282, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 123, -1, -1, 126, { 24,-1,-1 }, { 1,0,0 }, 1, -1, 0, 281, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, -3 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 280, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 127, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 285, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 123, -1, -1, 127, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 284, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 283, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 128, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 285, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 123, -1, -1, 128, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 284, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 283, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 129, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 285, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 123, -1, -1, 129, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 284, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 1 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 283, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 130, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 289, -1, -1, 7, 131, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 131, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 291, -1, -1, 7, 132, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 132, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 293, -1, -1, 7, 133, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 138, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 297, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 4000, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 296, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 48, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 295, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 49, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 295, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 137, -1, 137, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 298, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 140, 142, -1, 142, { 10,-1,-1 }, { 1,0,0 }, 1, -1, 0, 300, -1, -1, 0, -1, 0, 30, { -1, -1, -1 }, 0, -1, 0 },
    { 141, 142, -1, 142, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 301, -1, -1, 0, -1, 0, 10, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 142, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 299, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 3017, 147, -1, 147, { 18,-1,-1 }, { 2,0,0 }, 1, -1, 0, 303, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, 17, 0 },
    { -1, 147, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 302, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 144, 146, -1, 146, { 11,-1,-1 }, { 1,0,0 }, 1, -1, 0, 305, -1, -1, 0, -1, 0, 40, { -1, -1, -1 }, 0, -1, 0 },
    { 145, 146, -1, 146, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 306, -1, -1, 0, -1, 0, 15, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 146, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 304, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 3038, 148, -1, 148, { 10,-1,-1 }, { 2,0,0 }, 1, -1, 0, 308, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, 38, 0 },
    { -1, 148, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 307, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 3102, 149, -1, 149, { 11,-1,-1 }, { 2,0,0 }, 1, -1, 0, 310, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, 102, 0 },
    { -1, 149, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 309, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 311, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 137, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 313, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 138, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 314, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 312, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 137, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 316, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 138, -1, 138, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 315, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 150, 153, -1, 153, { 7,-1,-1 }, { 3,0,0 }, 1, -1, 0, 318, -1, -1, 0, -1, 0, 30, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 153, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 317, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 154, 157, -1, 157, { 8,-1,-1 }, { 3,0,0 }, 1, -1, 0, 320, -1, -1, 0, -1, 0, 40, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 157, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 319, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 158, 161, -1, 161, { 11,-1,-1 }, { 1,0,0 }, 1, -1, 0, 322, -1, -1, 0, -1, 0, 60, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 161, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 321, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 323, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 138, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 325, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 137, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 326, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 324, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 150, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 138, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 328, -1, -1, 7, 137, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 327, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 154, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 138, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 333, -1, -1, 7, 138, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 332, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 158, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 138, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 338, -1, -1, 7, 139, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 337, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 139, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 137, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 343, -1, -1, 7, 135, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 342, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 143, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 137, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 348, -1, -1, 7, 136, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 347, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 111, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 489, 106, 490, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 29, 28, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 353, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 28, 123, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 354, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 123, 136, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 355, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 136, 63, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 356, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 63, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 357, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 352, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 162, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, 162, { 26,-1,-1 }, { 1,0,0 }, 1, -1, 0, 359, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 2026, 163, -1, 163, { -1,-1,-1 }, { 0,0,0 }, 0, 31, 14, 360, -1, -1, 0, -1, 0, 0, { 26, -1, -1 }, 1, -1, 0 },
    { 163, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 361, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, 205, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 358, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 164, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, 164, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 363, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -166, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 364, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 164, 165, -1, 165, { 10,-1,-1 }, { 1,0,0 }, 1, -1, 0, 365, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 165, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 366, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, 206, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 362, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 3010, 166, -1, 166, { 11,-1,-1 }, { 1,0,0 }, 1, -1, 0, 368, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, 10, 0 },
    { 166, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 369, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, 207, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 367, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 167, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, 167, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 371, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -169, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 372, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 167, 168, -1, 168, { 10,-1,-1 }, { 2,0,0 }, 1, -1, 0, 373, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 168, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 374, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, 208, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 370, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 3078, 169, -1, 169, { 18,-1,-1 }, { 3,0,0 }, 1, -1, 0, 376, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, 78, 0 },
    { 169, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 377, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, 209, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 375, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 170, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, 170, { 27,-1,-1 }, { 1,0,0 }, 1, -1, 0, 379, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 2027, 171, -1, 171, { -1,-1,-1 }, { 0,0,0 }, 0, 94, 28, 380, -1, -1, 0, -1, 0, 0, { 27, -1, -1 }, 1, -1, 0 },
    { 171, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 381, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, 210, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 378, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 172, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 383, -1, -1, 7, 140, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 173, 175, -1, 175, { 10,-1,-1 }, { 1,0,0 }, 1, -1, 0, 387, -1, -1, 0, -1, 0, 40, { -1, -1, -1 }, 0, -1, 0 },
    { 174, 175, -1, 175, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 388, -1, -1, 0, -1, 0, 20, { -1, -1, -1 }, 0, -1, 0 },
    { 175, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 389, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, 211, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 382, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 176, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, 176, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 391, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -178, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 392, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 176, 177, -1, 177, { 11,-1,-1 }, { 1,0,0 }, 1, -1, 0, 393, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 177, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 394, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, 212, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 390, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 3110, 178, -1, 178, { 11,-1,-1 }, { 1,0,0 }, 1, -1, 0, 396, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, 110, 0 },
    { 178, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 397, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, 213, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 395, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 179, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, 179, { 28,-1,-1 }, { 1,0,0 }, 1, -1, 0, 399, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 2028, 180, -1, 180, { -1,-1,-1 }, { 0,0,0 }, 0, 97, 38, 400, -1, -1, 0, -1, 0, 0, { 28, -1, -1 }, 1, -1, 0 },
    { 180, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 401, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, 214, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 398, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 181, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 403, -1, -1, 7, 141, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 182, 184, -1, 184, { 11,-1,-1 }, { 1,0,0 }, 1, -1, 0, 407, -1, -1, 0, -1, 0, 60, { -1, -1, -1 }, 0, -1, 0 },
    { 183, 184, -1, 184, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 408, -1, -1, 0, -1, 0, 30, { -1, -1, -1 }, 0, -1, 0 },
    { 184, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 409, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, 215, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 402, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 185, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, 185, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 411, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -187, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 412, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 185, 186, -1, 186, { 18,10,-1 }, { 3,2,0 }, 2, -1, 0, 413, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 186, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 414, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, 216, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 410, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 3062, 187, -1, 187, { 11,-1,-1 }, { 2,0,0 }, 1, -1, 0, 416, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, 62, 0 },
    { 187, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 417, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, 217, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 415, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 111, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 491, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 84, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 421, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 420, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 111, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 492, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 85, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 423, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 422, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 111, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 493, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 86, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 425, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 424, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 111, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 494, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 87, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 427, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 426, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 111, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 495, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 88, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 429, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 428, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 111, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 496, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 89, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 431, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 430, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 111, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 497, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 90, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 433, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 432, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 111, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 498, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 91, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 435, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 434, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 111, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 499, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 92, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 437, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 436, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 111, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 500, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 104, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 419, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 418, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 188, -1, 188, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 438, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 5010, 189, -1, 189, { 8,-1,-1 }, { 5,0,0 }, 1, -1, 0, 439, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 5025, 190, -1, 190, { 10,-1,-1 }, { 3,0,0 }, 1, -1, 0, 440, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 5050, 191, -1, 191, { 11,-1,-1 }, { 3,0,0 }, 1, -1, 0, 441, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 5080, 192, -1, 192, { 12,-1,-1 }, { 1,0,0 }, 1, -1, 0, 442, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 5111, 193, -1, 193, { 12,-1,-1 }, { 3,0,0 }, 1, -1, 0, 443, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 189, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 444, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 190, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 445, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 191, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 446, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 192, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 447, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 193, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 448, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 449, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 63, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 451, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 450, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 452, -1, -1, 0, -1, 1, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 136, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 461, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 28, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 453, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 123, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 454, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 124, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 455, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 125, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 456, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 126, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 457, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 127, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 458, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 128, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 458, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 129, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 458, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 132, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 459, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 460, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 2030, 196, -1, 196, { -1,-1,-1 }, { 0,0,0 }, 0, 104, 28, 464, -1, -1, 0, -1, 0, 0, { 30, -1, -1 }, 1, -1, 0 },
    { 196, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 465, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 194, -1, 194, { 29,-1,-1 }, { 1,0,0 }, 1, -1, 0, 462, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 463, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 197, -1, 218, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 467, -1, -1, 7, 142, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 63, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 469, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 198, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 470, -1, -1, 7, 143, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 92, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 472, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 199, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 473, -1, -1, 7, 144, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 475, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 201, -1, 201, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 476, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 48, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 478, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 49, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 478, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 200, -1, 200, { 11,-1,-1 }, { 1,0,0 }, 1, -1, 0, 477, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 479, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 204, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -125, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 2031, -1, -1, 204, { -1,-1,-1 }, { 0,0,0 }, 0, 72, 20, 482, -1, -1, 0, -1, 0, 0, { 31, -1, -1 }, 1, -1, 2 },
    { -1, 202, -1, 202, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 480, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 481, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 484, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, 203, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -204, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, 203, { 31,-1,-1 }, { 1,0,0 }, 1, -1, 0, 483, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 3025, 221, -1, 221, { 5,-1,-1 }, { 2,0,0 }, 1, -1, 0, 503, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 221, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 504, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, 220, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 502, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 3032, 223, -1, 223, { 1,-1,-1 }, { 3,0,0 }, 1, -1, 0, 506, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 223, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 507, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, 222, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 505, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 224, -1, 224, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 509, -1, -1, 0, -1, 1, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 228, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 512, -1, -1, 0, -1, 1, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 227, -1, -1, 228, { 11,-1,-1 }, { 3,0,0 }, 1, -1, 0, 511, -1, -1, 0, -1, 1, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 510, -1, -1, 0, -1, 1, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 225, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 513, -1, -1, 7, 146, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 515, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 226, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 516, -1, -1, 7, 147, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 518, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { 227, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 522, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 225, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 519, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, 226, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 519, -1, -1, 0, -1, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
    { -1, -1, -1, -1, { -1,-1,-1 }, { 0,0,0 }, 0, -1, 0, 520, -1, -1, 7, 148, 0, 0, { -1, -1, -1 }, 0, -1, 0 },
};
static const NpcDef NPC_DEFS[] = {
    { MAP_HOUSE, 'B', 0, 3, 30, 32 },
    { MAP_HOUSE, 'U', 3, 1, 40, 35 },
    { MAP_HOUSE, 'S', 4, 3, 25, 28 },
    { MAP_HOUSE, 'C', 7, 3, 20, 20 },
    { MAP_VELD, 'K', 10, 4, 30, 32 },
    { MAP_VELD, 'I', 14, 2, 30, 32 },
    { MAP_VELD, 'V', 16, 2, 30, 32 },
    { MAP_VELD, 'A', 18, 3, 30, 32 },
    { MAP_VELD, 'Q', 21, 4, 30, 32 },
    { MAP_VELD, 'J', 25, 1, 30, 32 },
    { MAP_VELD, 'E', 26, 4, 30, 32 },
    { MAP_VELD, 'M', 30, 3, 20, 20 },
    { MAP_VELD, 'G', 33, 3, 18, 18 },
    { MAP_GROVE, '8', 36, 3, 30, 32 },
    { MAP_GROVE, '9', 39, 3, 30, 32 },
    { MAP_GROVE, 'K', 42, 2, 30, 32 },
    { MAP_CAMP, 'I', 44, 4, 30, 32 },
    { MAP_CAMP, 'K', 48, 2, 30, 32 },
    { MAP_CAMP, 'A', 50, 2, 30, 32 },
    { MAP_CLIFFS, 'V', 52, 2, 30, 32 },
    { MAP_CLIFFS, 'Y', 54, 4, 30, 32 },
    { MAP_CLIFFS, 'C', 58, 5, 20, 20 },
    { MAP_CLIFFS, 'k', 63, 3, 30, 32 },
    { MAP_RUINS, 'J', 66, 1, 30, 32 },
    { MAP_RUINS, 'K', 67, 2, 30, 32 },
    { MAP_RUINS, 'A', 69, 2, 30, 32 },
    { MAP_REACH, 'Y', 71, 2, 30, 32 },
    { MAP_FOREST, '4', 73, 2, 30, 32 },
    { MAP_FOREST, '5', 75, 2, 30, 32 },
    { MAP_RUINS, '6', 77, 2, 30, 32 },
    { MAP_RUINS, '7', 79, 2, 30, 32 },
    { MAP_QUARRY, 'C', 81, 3, 20, 20 },
    { MAP_QUARRY, 'S', 84, 3, 25, 28 },
    { MAP_MARSH, '1', 87, 2, 30, 32 },
    { MAP_MARSH, '2', 89, 2, 30, 32 },
    { MAP_REACH, 'Q', 91, 2, 30, 32 },
    { MAP_REACH, 'O', 93, 2, 30, 32 },
    { MAP_QUARRY, '1', 95, 2, 30, 32 },
    { MAP_MARSH, 'F', 97, 1, 30, 32 },
    { MAP_CAMP, 'S', 98, 1, 30, 32 },
    { MAP_GAUNTLET6, 'G', 99, 3, 30, 32 },
    { MAP_VELD, 'L', 102, 3, 30, 32 },
    { MAP_VELD, '4', 105, 3, 30, 32 },
    { MAP_VELD, '9', 108, 3, 30, 32 },
    { MAP_VELD, 'Y', 111, 1, 30, 32 },
    { MAP_BASEMALKUTH, 's', 112, 2, 30, 32 },
    { MAP_BASEMALKUTH, 't', 114, 2, 30, 32 },
    { MAP_BASEMALKUTH, 'a', 116, 2, 30, 32 },
    { MAP_BASEYESOD, 's', 118, 2, 30, 32 },
    { MAP_BASEYESOD, 't', 120, 2, 30, 32 },
    { MAP_BASEYESOD, 'a', 122, 2, 30, 32 },
    { MAP_BASENETZACH, 's', 124, 2, 30, 32 },
    { MAP_BASENETZACH, 't', 126, 2, 30, 32 },
    { MAP_BASENETZACH, 'a', 128, 2, 30, 32 },
    { MAP_BASEHOD, 's', 130, 2, 30, 32 },
    { MAP_BASEHOD, 't', 132, 2, 30, 32 },
    { MAP_BASEHOD, 'a', 134, 2, 30, 32 },
    { MAP_BASETIFERET, 's', 136, 2, 30, 32 },
    { MAP_BASETIFERET, 't', 138, 2, 30, 32 },
    { MAP_BASETIFERET, 'a', 140, 2, 30, 32 },
    { MAP_BASECHESED, 's', 142, 2, 30, 32 },
    { MAP_BASECHESED, 't', 144, 2, 30, 32 },
    { MAP_BASECHESED, 'a', 146, 2, 30, 32 },
    { MAP_BASEGEVURAH, 's', 148, 2, 30, 32 },
    { MAP_BASEGEVURAH, 't', 150, 2, 30, 32 },
    { MAP_BASEGEVURAH, 'a', 152, 2, 30, 32 },
    { MAP_BASEBINAH, 's', 154, 2, 30, 32 },
    { MAP_BASEBINAH, 't', 156, 2, 30, 32 },
    { MAP_BASEBINAH, 'a', 158, 2, 30, 32 },
    { MAP_BASECHOKMAH, 's', 160, 2, 30, 32 },
    { MAP_BASECHOKMAH, 't', 162, 2, 30, 32 },
    { MAP_BASECHOKMAH, 'a', 164, 2, 30, 32 },
    { MAP_PALACEKETER, 's', 166, 2, 30, 32 },
    { MAP_PALACEKETER, 't', 168, 2, 30, 32 },
    { MAP_PALACEKETER, 'a', 170, 2, 30, 32 },
    { MAP_MALKUTH, 'h', 172, 1, 30, 32 },
    { MAP_MALKUTH, 'v', 173, 1, 30, 32 },
    { MAP_MALKUTH, 'y', 174, 5, 30, 32 },
    { MAP_MALKUTH, 'u', 179, 3, 30, 32 },
    { MAP_YESOD, 'u', 182, 3, 30, 32 },
    { MAP_NETZACH, 'u', 185, 3, 30, 32 },
    { MAP_HOD, 'u', 188, 3, 30, 32 },
    { MAP_TIFERET, 'u', 191, 3, 30, 32 },
    { MAP_CHESED, 'u', 194, 3, 30, 32 },
    { MAP_GEVURAH, 'u', 197, 3, 30, 32 },
    { MAP_BINAH, 'u', 200, 3, 30, 32 },
    { MAP_CHOKMAH, 'u', 203, 3, 30, 32 },
    { MAP_GHOSTCRYPT, 'x', 206, 11, 30, 32 },
    { MAP_RUINS, 'd', 217, 3, 30, 32 },
    { MAP_GROVE, 'd', 220, 3, 30, 32 },
    { MAP_MARSH, 'd', 223, 3, 30, 32 },
    { MAP_CLIFFS, 'f', 226, 3, 30, 32 },
    { MAP_QUARRY, 'f', 229, 3, 30, 32 },
    { MAP_FOREST, 'f', 232, 3, 30, 32 },
    { MAP_HAUNTEDHALL, 's', 235, 2, 30, 32 },
    { MAP_HAUNTEDHALL, 't', 237, 2, 30, 32 },
    { MAP_HAUNTEDHALL, 'a', 239, 2, 30, 32 },
    { MAP_HEROESHALL, 'x', 241, 18, 30, 32 },
    { MAP_HEROESHALL, 'z', 259, 3, 30, 32 },
    { MAP_THIEVESDEN, 'x', 262, 9, 30, 32 },
    { MAP_THIEVESDEN, 'z', 271, 3, 30, 32 },
    { MAP_VELD, 'i', 274, 3, 30, 32 },
    { MAP_RUINS, 'i', 277, 3, 30, 32 },
    { MAP_CLIFFS, 'i', 280, 3, 30, 32 },
    { MAP_FOREST, 'i', 283, 3, 30, 32 },
    { MAP_QUARRY, 'i', 286, 3, 30, 32 },
    { MAP_VELD, 'j', 289, 7, 30, 32 },
    { MAP_GROVE, 'j', 296, 2, 30, 32 },
    { MAP_VELD, 'l', 298, 3, 30, 32 },
    { MAP_CLIFFS, 'j', 301, 2, 30, 32 },
    { MAP_VELD, 'o', 303, 2, 30, 32 },
    { MAP_VELD, 'n', 305, 3, 30, 32 },
    { MAP_VELD, 'p', 308, 3, 30, 32 },
    { MAP_TAU, 'p', 311, 2, 30, 32 },
    { MAP_MALKUTH, 'l', 313, 2, 30, 32 },
    { MAP_MALKUTH, 'j', 315, 3, 30, 32 },
    { MAP_YESOD, 'j', 318, 3, 30, 32 },
    { MAP_PEH, 'l', 321, 2, 30, 32 },
    { MAP_NETZACH, 'j', 323, 3, 30, 32 },
    { MAP_MEM, 'o', 326, 2, 30, 32 },
    { MAP_HOD, 'j', 328, 4, 30, 32 },
    { MAP_SAMEKH, 'p', 332, 2, 30, 32 },
    { MAP_TIFERET, 'l', 334, 2, 30, 32 },
    { MAP_TIFERET, 'j', 336, 3, 30, 32 },
    { MAP_CHESED, 'j', 339, 3, 30, 32 },
    { MAP_HETH, 'l', 342, 2, 30, 32 },
    { MAP_GEVURAH, 'j', 344, 3, 30, 32 },
    { MAP_DALETH, 'o', 347, 2, 30, 32 },
    { MAP_BINAH, 'j', 349, 4, 30, 32 },
    { MAP_ALEPH, 'p', 353, 2, 30, 32 },
    { MAP_CHOKMAH, 'l', 355, 2, 30, 32 },
    { MAP_CHOKMAH, 'j', 357, 3, 30, 32 },
    { MAP_KETER, 'j', 360, 3, 30, 32 },
    { MAP_MALKUTH, 'i', 363, 3, 30, 32 },
    { MAP_YESOD, 'i', 366, 3, 30, 32 },
    { MAP_NETZACH, 'i', 369, 3, 30, 32 },
    { MAP_HOD, 'i', 372, 3, 30, 32 },
    { MAP_TIFERET, 'i', 375, 3, 30, 32 },
    { MAP_CHESED, 'i', 378, 3, 30, 32 },
    { MAP_GEVURAH, 'i', 381, 3, 30, 32 },
    { MAP_BINAH, 'i', 384, 3, 30, 32 },
    { MAP_CHOKMAH, 'i', 387, 3, 30, 32 },
    { MAP_KETER, 'i', 390, 3, 30, 32 },
    { MAP_RUINSLIBRARY, 'x', 393, 12, 30, 32 },
    { MAP_RUINSLIBRARY, 'z', 405, 2, 30, 32 },
    { MAP_RUINSINN, 'x', 407, 1, 30, 32 },
    { MAP_RUINSINN, 'z', 408, 11, 30, 32 },
    { MAP_BRANNHOUSE, 'x', 419, 4, 30, 32 },
    { MAP_HERMITHUT, 'x', 423, 6, 30, 32 },
    { MAP_SAGEHOUSE, 'x', 429, 5, 30, 32 },
    { MAP_EMPTYHOUSE, 'x', 434, 5, 30, 32 },
    { MAP_EMPTYHOUSE, 'z', 439, 1, 30, 32 },
    { MAP_MARSH, 'n', 440, 3, 30, 32 },
    { MAP_QUARRY, 'm', 443, 3, 30, 32 },
    { MAP_MARSH, 'm', 446, 3, 30, 32 },
    { MAP_HOLLOW, 'i', 449, 4, 30, 32 },
    { MAP_HOLLOW, 'f', 453, 2, 30, 32 },
    { MAP_HOLLOW, 'j', 455, 2, 30, 32 },
    { MAP_HOLLOW, 'd', 457, 4, 30, 32 },
};
#define NPC_DEF_N 159
#define NPC_SPRITE_N 76
static const unsigned short *const NPC_SPRITE_FRAMES[NPC_SPRITE_N][4] = {
    { npc_bogwalker_1, npc_bogwalker_2, npc_bogwalker_3, npc_bogwalker_4 },
    { npc_reedguard_1, npc_reedguard_2, npc_reedguard_3, npc_reedguard_4 },
    { npc_quartz_1, npc_quartz_2, npc_quartz_3, npc_quartz_4 },
    { npc_opal_1, npc_opal_2, npc_opal_3, npc_opal_4 },
    { npc_driller_1, npc_driller_2, npc_driller_3, npc_driller_4 },
    { npc_fenn_1, npc_fenn_2, npc_fenn_3, npc_fenn_4 },
    { npc_dray_1, npc_dray_2, npc_dray_3, npc_dray_4 },
    { npc_lead_1, npc_lead_2, npc_lead_3, npc_lead_4 },
    { npc_weepingGuard_1, npc_weepingGuard_2, npc_weepingGuard_3, npc_weepingGuard_4 },
    { npc_royalGuard_1, npc_royalGuard_2, npc_royalGuard_3, npc_royalGuard_4 },
    { npc_harrow_1, npc_harrow_2, npc_harrow_3, npc_harrow_4 },
    { npc_ashgrove_1, npc_ashgrove_2, npc_ashgrove_3, npc_ashgrove_4 },
    { npc_stroud_1, npc_stroud_2, npc_stroud_3, npc_stroud_4 },
    { npc_vale_1, npc_vale_2, npc_vale_3, npc_vale_4 },
    { npc_kessler_1, npc_kessler_2, npc_kessler_3, npc_kessler_4 },
    { npc_morrow_1, npc_morrow_2, npc_morrow_3, npc_morrow_4 },
    { npc_crane_1, npc_crane_2, npc_crane_3, npc_crane_4 },
    { npc_blackwood_1, npc_blackwood_2, npc_blackwood_3, npc_blackwood_4 },
    { npc_sorrel_1, npc_sorrel_2, npc_sorrel_3, npc_sorrel_4 },
    { npc_nero_1, npc_nero_2, npc_nero_3, npc_nero_4 },
    { npc_ada_1, npc_ada_2, npc_ada_3, npc_ada_4 },
    { npc_hale_1, npc_hale_2, npc_hale_3, npc_hale_4 },
    { npc_marn_1, npc_marn_2, npc_marn_3, npc_marn_4 },
    { npc_citizen_1, npc_citizen_2, npc_citizen_3, npc_citizen_4 },
    { npc_vesk_1, npc_vesk_2, npc_vesk_3, npc_vesk_4 },
    { npc_ghost_1, npc_ghost_2, npc_ghost_3, npc_ghost_4 },
    { npc_grave_1, npc_grave_2, npc_grave_3, npc_grave_4 },
    { npc_shrine_1, npc_shrine_2, npc_shrine_3, npc_shrine_4 },
    { npc_ardent_1, npc_ardent_2, npc_ardent_3, npc_ardent_4 },
    { npc_mag_1, npc_mag_2, npc_mag_3, npc_mag_4 },
    { npc_pell_1, npc_pell_2, npc_pell_3, npc_pell_4 },
    { npc_fingers_1, npc_fingers_2, npc_fingers_3, npc_fingers_4 },
    { npc_aldous_1, npc_aldous_2, npc_aldous_3, npc_aldous_4 },
    { npc_brin_1, npc_brin_2, npc_brin_3, npc_brin_4 },
    { npc_rook_1, npc_rook_2, npc_rook_3, npc_rook_4 },
    { npc_mallory_1, npc_mallory_2, npc_mallory_3, npc_mallory_4 },
    { npc_silas_1, npc_silas_2, npc_silas_3, npc_silas_4 },
    { npc_townsman_1, npc_townsman_2, npc_townsman_3, npc_townsman_4 },
    { npc_townswoman_1, npc_townswoman_2, npc_townswoman_3, npc_townswoman_4 },
    { npc_elder_1, npc_elder_2, npc_elder_3, npc_elder_4 },
    { npc_child_1, npc_child_2, npc_child_3, npc_child_4 },
    { npc_bandit_1, npc_bandit_2, npc_bandit_3, npc_bandit_4 },
    { npc_pickup_1, npc_pickup_2, npc_pickup_3, npc_pickup_4 },
    { npc_crier_1, npc_crier_2, npc_crier_3, npc_crier_4 },
    { npc_tam_1, npc_tam_2, npc_tam_3, npc_tam_4 },
    { npc_lina_1, npc_lina_2, npc_lina_3, npc_lina_4 },
    { npc_rolo_1, npc_rolo_2, npc_rolo_3, npc_rolo_4 },
    { npc_juno_1, npc_juno_2, npc_juno_3, npc_juno_4 },
    { npc_bet_1, npc_bet_2, npc_bet_3, npc_bet_4 },
    { npc_pip_1, npc_pip_2, npc_pip_3, npc_pip_4 },
    { npc_cobb_1, npc_cobb_2, npc_cobb_3, npc_cobb_4 },
    { npc_sera_1, npc_sera_2, npc_sera_3, npc_sera_4 },
    { npc_dunn_1, npc_dunn_2, npc_dunn_3, npc_dunn_4 },
    { npc_garrow_1, npc_garrow_2, npc_garrow_3, npc_garrow_4 },
    { npc_hesse_1, npc_hesse_2, npc_hesse_3, npc_hesse_4 },
    { npc_tilly_1, npc_tilly_2, npc_tilly_3, npc_tilly_4 },
    { npc_voss_1, npc_voss_2, npc_voss_3, npc_voss_4 },
    { npc_lune_1, npc_lune_2, npc_lune_3, npc_lune_4 },
    { npc_holt_1, npc_holt_2, npc_holt_3, npc_holt_4 },
    { npc_kael_1, npc_kael_2, npc_kael_3, npc_kael_4 },
    { npc_anselm_1, npc_anselm_2, npc_anselm_3, npc_anselm_4 },
    { npc_iona_1, npc_iona_2, npc_iona_3, npc_iona_4 },
    { npc_rhee_1, npc_rhee_2, npc_rhee_3, npc_rhee_4 },
    { npc_wyn_1, npc_wyn_2, npc_wyn_3, npc_wyn_4 },
    { npc_lark_1, npc_lark_2, npc_lark_3, npc_lark_4 },
    { npc_hollis_1, npc_hollis_2, npc_hollis_3, npc_hollis_4 },
    { npc_quill_1, npc_quill_2, npc_quill_3, npc_quill_4 },
    { npc_brann_1, npc_brann_2, npc_brann_3, npc_brann_4 },
    { npc_osk_1, npc_osk_2, npc_osk_3, npc_osk_4 },
    { npc_ilse_1, npc_ilse_2, npc_ilse_3, npc_ilse_4 },
    { npc_maren_1, npc_maren_2, npc_maren_3, npc_maren_4 },
    { npc_hollowKeeper_1, npc_hollowKeeper_2, npc_hollowKeeper_3, npc_hollowKeeper_4 },
    { npc_hollowRanger_1, npc_hollowRanger_2, npc_hollowRanger_3, npc_hollowRanger_4 },
    { npc_hollowShade_1, npc_hollowShade_2, npc_hollowShade_3, npc_hollowShade_4 },
    { npc_hollowWarden_1, npc_hollowWarden_2, npc_hollowWarden_3, npc_hollowWarden_4 },
    { npc_shinigami_1, npc_shinigami_2, npc_shinigami_3, npc_shinigami_4 },
};
/* NPC_SPRITE_FRAMES index per NPC_DEFS entry (-1: drawn by hand-wired code). */
static const signed char NPC_DEF_SPRITE[NPC_DEF_N] = { -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 75, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 1, 2, 3, 4, 5, 6, -1, 7, -1, 75, -1, 8, 8, 10, 8, 8, 11, 8, 8, 12, 8, 8, 13, 8, 8, 14, 8, 8, 15, 8, 8, 16, 8, 8, 17, 8, 8, 18, 9, 9, 19, 20, 21, 22, 23, 23, 23, 23, 23, 23, 23, 23, 23, 75, 26, 26, 26, 27, 27, 27, 25, 25, 25, 28, 30, 29, 31, 32, 33, 34, 35, 36, 43, 42, 44, 46, 46, 45, 47, 49, 49, 48, 50, 42, 51, 53, 52, 55, 55, 54, 56, 42, 57, 59, 58, 61, 61, 60, 62, 38, 37, 38, 37, 38, 37, 38, 37, 38, 39, 63, 64, 65, 66, 67, 68, 69, 70, 26, 42, 38, 37, 71, 72, 73, 74 };
#define INTERACT_BUFFER 20


/* Quest journal (logic.json journal, tools/build_journal.py). A quest shows
   once start is on (-1 = always) and is done once done is on; the current
   hint is its first step whose if_not is off and if_flag (if any) is on. */
typedef struct { int if_flag, if_not; const char *text; } JournalStep;
typedef struct { const char *title; int start, done; const char *done_text; int step0, nsteps, linear; } JournalQuest;
#define JOURNAL_QUEST_N 27
#define JOURNAL_STEP_N 79
static const JournalStep JOURNAL_STEPS[JOURNAL_STEP_N] = {
    { -1, 0, "TAKE FATHER'S CRYMON CRYSTAL FROM THE SHELF AT HOME." },
    { -1, 4, "CALDER BLOCKS THE EAST ROAD OUT OF CRYTOWN. BEAT HIM TO REACH THE CLIFFS." },
    { -1, 18, "GO EAST OVER THE CLIFFS, THEN THE MARSH, THE QUARRY, THE ARMY CAMP AND THE FOREST. THE PRISON IS PAST THE FOREST." },
    { -1, 17, "GET PAST CATHLEEN AND FACE SHINIGAMI IN THE PRISON." },
    { -1, 28, "THE BOULDER WEST OF CRYTOWN IS GONE. GO THROUGH THE RUINS TO THE REACH." },
    { -1, 123, "SHINIGAMI WAITS UNDER THE NORTHWEST HOUSE IN THE RUINS." },
    { -1, 136, "DO THE GHOST GUILD'S WORK SO SHINIGAMI CAN PART THE WEEPING VEIL." },
    { -1, 63, "BEAT LIEUTENANT LEAD AT CRYTOWN'S NORTH GATE. HE FIGHTS WITH SIX CRYMON." },
    { -1, 84, "TAKE THE MALKUTH BASE FROM GENERAL HARROW." },
    { -1, 85, "TAKE THE YESOD BASE FROM GENERAL ASHGROVE." },
    { -1, 86, "TAKE THE NETZACH BASE FROM GENERAL STROUD." },
    { -1, 87, "TAKE THE HOD BASE FROM GENERAL VALE." },
    { -1, 88, "TAKE THE TIFERET BASE FROM GENERAL KESSLER." },
    { -1, 89, "TAKE THE CHESED BASE FROM GENERAL MORROW." },
    { -1, 90, "TAKE THE GEVURAH BASE FROM GENERAL CRANE." },
    { -1, 91, "TAKE THE BINAH BASE FROM GENERAL BLACKWOOD." },
    { -1, 92, "TAKE THE CHOKMAH BASE FROM GENERAL SORREL." },
    { -1, 105, "NINE MEDALS WON. STORM NERO'S PALACE IN KETER." },
    { -1, 219, "CALDER IS WAITING AT CRYTOWN'S EAST GATE. HE WANTS ONE MORE FIGHT." },
    { -1, 224, "THE BRAMBLES WEST OF THE REACH HAVE DIED BACK. SOMETHING WAITS IN THE HOLLOW." },
    { -1, 225, "BEAT THE LOST RANGER IN THE HOLLOW, WEST OF THE REACH." },
    { -1, 226, "BEAT THE HOLLOW SHADE BY THE SOUTH GRASS." },
    { -1, 227, "BEAT THE HOLLOW WARDEN IN THE WEST." },
    { -1, 228, "GO BACK TO THE KEEPER BY THE HOLLOW'S ENTRANCE." },
    { -1, 62, "SHOW THE SCROLL TO THE PRIESTESS SOUTH OF CRYTOWN AND FOLLOW THE GAUNTLET TO HEAVENFALL'S GRAVE." },
    { -1, 124, "ROB INES'S GRAVE IN THE SOUTHEAST OF THE RUINS." },
    { -1, 125, "ROB TOMAS'S GRAVE IN THE PRISON YARD." },
    { -1, 126, "ROB ORIEL'S GRAVE IN THE SOUTHWEST MARSH." },
    { -1, 127, "PRAY AT THE SHRINE AT THE TOP OF THE CLIFFS." },
    { -1, 128, "PRAY AT THE SHRINE IN THE QUARRY." },
    { -1, 129, "PRAY AT THE SHRINE IN THE EAST OF THE FOREST." },
    { -1, 132, "FREE THE GHOSTS IN THE HAUNTED HALL, NORTHEAST IN THE REACH." },
    { -1, 133, "BRING THE BONES TO SHINIGAMI IN THE CRYPT UNDER THE RUINS." },
    { -1, 136, "COLLECT THE WRAITH LANTERN FROM SHINIGAMI." },
    { -1, 142, "ARREST RED MALLORY IN THE FOREST, THEN REPORT TO CAPTAIN ARDENT." },
    { -1, 147, "BRING CAPTAIN ARDENT A GLASSWISP. THEY LIVE IN THE RUINS' GRASS." },
    { -1, 146, "ARREST SILAS THE FENCE IN THE QUARRY, THEN REPORT TO ARDENT." },
    { -1, 148, "BRING ARDENT A STARDROP FROM THE QUARRY'S GRASS." },
    { -1, 149, "BRING ARDENT A MOONVEIL FROM THE PATH OF AYIN." },
    { -1, 153, "SHAKE DOWN SIR ALDOUS IN CRYTOWN, THEN SEE MAG." },
    { -1, 157, "SHAKE DOWN DAME BRIN IN THE RUINS, THEN SEE MAG." },
    { -1, 161, "SHAKE DOWN CAPTAIN ROOK ON THE CLIFFS, THEN SEE MAG." },
    { -1, 12, "PIKE LOST A CRYSTAL IN THE EAST REEDS OF CRYTOWN. FIND IT AND BRING IT BACK." },
    { -1, 162, "OLD TAM LOST HIS WATCH BY THE PRISON." },
    { -1, 163, "GIVE OLD TAM HIS WATCH IN CRYTOWN." },
    { -1, 164, "FIND ROLO ON THE CLIFFS." },
    { -1, 165, "TELL LINA IN CRYTOWN THAT ROLO IS HOME." },
    { -1, 166, "BRING COLLECTOR JUNO IN CRYTOWN A CRYMARE FROM THE RUINS' GRASS." },
    { -1, 221, "CATCH A CINDERMITE IN THE QUARRY'S GRASS AND SHOW FOREMAN DAGNY." },
    { -1, 223, "CATCH A CHILLNEWT IN THE MARSH'S GRASS AND SHOW OLD FENWICK." },
    { -1, 189, "CATCH 10 KINDS OF CRYMON AND SHOW ARCHIVIST WYN IN THE RUINS LIBRARY." },
    { -1, 190, "CATCH 25 KINDS AND SHOW WYN." },
    { -1, 191, "CATCH 50 KINDS AND SHOW WYN." },
    { -1, 192, "CATCH 80 KINDS AND SHOW WYN." },
    { -1, 193, "CATCH EVERY KIND AND SHOW WYN." },
    { -1, 195, "TAKE BRANN'S LETTER TO HIS BROTHER, ELDER MARN, IN MALKUTH." },
    { -1, 196, "TAKE MARN'S REPLY BACK TO BRANN IN THE RUINS." },
    { -1, 197, "BEAT HERMIT OSK IN HIS HUT IN THE REACH." },
    { -1, 63, "BEAT LIEUTENANT LEAD, THEN FIGHT OSK AGAIN." },
    { -1, 198, "BEAT OSK'S REAL TEAM." },
    { -1, 92, "WIN ALL NINE MEDALS, THEN FIGHT OSK ONE LAST TIME." },
    { -1, 199, "BEAT OSK'S LAST LESSON." },
    { -1, 203, "FIND MAREN'S RAG DOLL IN THE NORTH OF THE MARSH." },
    { -1, 204, "BRING THE DOLL TO MAREN IN THE REACH'S EMPTY HOUSE." },
    { -1, 167, "FIND PIP ON THE PATH OF TAU." },
    { -1, 168, "TELL OLD BET IN MALKUTH THAT PIP IS HOME." },
    { -1, 169, "BRING COBB IN YESOD A BOLTLAMB FROM THE PATH OF RESH." },
    { -1, 171, "FIND SERA'S SILVER LOCKET ON THE PATH OF PEH AND BRING IT TO HER IN NETZACH." },
    { -1, 172, "DEAL WITH KNIFE-HAND GARROW ON THE PATH OF MEM." },
    { -1, 175, "COLLECT THE BOUNTY FROM DUNN IN HOD." },
    { -1, 176, "FIND TILLY ON THE PATH OF SAMEKH." },
    { -1, 177, "TELL HESSE IN TIFERET THAT TILLY IS HOME." },
    { -1, 178, "BRING VOSS IN CHESED A WHEELHOG FROM THE PATH OF MEM." },
    { -1, 180, "FIND LUNE'S OLD MAP ON THE PATH OF HETH AND BRING IT TO GEVURAH." },
    { -1, 181, "DEAL WITH DESERTER KAEL ON THE PATH OF DALETH." },
    { -1, 184, "COLLECT THE BOUNTY FROM HOLT IN BINAH." },
    { -1, 185, "FIND SISTER IONA ON THE PATH OF ALEPH." },
    { -1, 186, "TELL ANSELM IN CHOKMAH THAT IONA IS HOME." },
    { -1, 187, "BRING RHEE IN KETER AN ARCANOX FROM THE PATH OF ALEPH." },
};
static const JournalQuest JOURNAL_QUESTS[27] = {
    { "THE WEEPING ARMY", -1, 105, "NERO IS BEATEN. THE SEPHIROT ARE FREE.", 0, 18, 1 },
    { "AFTER THE WAR", 111, 219, "CALDER WENT TO JOIN THE NEW GUARD IN MALKUTH.", 18, 2, 0 },
    { "THE HOLLOW", 224, 228, "THE KEEPER GAVE MAX THREE ULTIMATE CAPTURE CRYSTALS.", 20, 4, 0 },
    { "THE FALLEN STAR", 51, 62, "HEAVENFALL ANSWERED THE SCROLL.", 24, 1, 0 },
    { "THE GHOST GUILD", 123, 136, "THE WRAITH LANTERN PARTED THE VEIL.", 25, 9, 0 },
    { "THE HEROES GUILD", 137, 149, "EVERY HEROES GUILD JOB IS DONE.", 34, 5, 0 },
    { "THE THIEVES GUILD", 138, 161, "EVERY THIEVES GUILD JOB IS DONE.", 39, 3, 0 },
    { "PIKE'S CRYSTAL", 13, 12, "", 42, 1, 0 },
    { "OLD TAM'S WATCH", 205, 163, "", 43, 2, 0 },
    { "LINA'S BOY", 206, 165, "", 45, 2, 0 },
    { "A CRYMARE FOR JUNO", 207, 166, "", 47, 1, 0 },
    { "THE FUSE-EATER", 220, 221, "", 48, 1, 0 },
    { "COLD WATER", 222, 223, "", 49, 1, 0 },
    { "THE LIBRARY'S GREAT BOOK", 188, 193, "MAX'S NAME IS ON THE FIRST PAGE.", 50, 5, 0 },
    { "A DESERTER'S LETTER", 194, 196, "", 55, 2, 0 },
    { "HERMIT OSK'S LESSONS", 218, 199, "", 57, 5, 0 },
    { "BUTTON", 202, 204, "MAREN IS AT REST.", 62, 2, 0 },
    { "PIP", 208, 168, "", 64, 2, 0 },
    { "A BOLTLAMB FOR COBB", 209, 169, "", 66, 1, 0 },
    { "SERA'S LOCKET", 210, 171, "", 67, 1, 0 },
    { "WANTED, KNIFE-HAND GARROW", 211, 175, "", 68, 2, 0 },
    { "TILLY", 212, 177, "", 70, 2, 0 },
    { "A WHEELHOG FOR VOSS", 213, 178, "", 72, 1, 0 },
    { "LUNE'S OLD MAP", 214, 180, "", 73, 1, 0 },
    { "WANTED, DESERTER KAEL", 215, 184, "", 74, 2, 0 },
    { "SISTER IONA", 216, 186, "", 76, 2, 0 },
    { "AN ARCANOX FOR RHEE", 217, 187, "", 78, 1, 0 },
};

/* Pause-menu Map (logic.json mapScreen). Nodes are dots with a label under
   them, links are lines; x/y are in a 280x152 box under the menu title.
   MAP_WHERE[map]: node index, 1000 + link index, or -1. */
typedef struct { int page, x, y, gem; const char *label; } MapScreenNode;
typedef struct { int a, b; const char *label; } MapScreenLink;
#define MAPSCREEN_PAGE_N 2
#define MAPSCREEN_NODE_N 24
#define MAPSCREEN_LINK_N 35
static const char *const MAPSCREEN_PAGE_TITLE[MAPSCREEN_PAGE_N] = { "SORROW COUNTY", "THE SEPHIROT" };
static const MapScreenNode MAPSCREEN_NODES[MAPSCREEN_NODE_N] = {
    { 0, 140, 0, 0, "MALKUTH" },
    { 0, 140, 24, 0, "WEEPING ROAD" },
    { 0, 34, 24, 1, "REACH" },
    { 0, 34, 0, 0, "HOLLOW" },
    { 0, 60, 50, 0, "RUINS" },
    { 0, 140, 50, 1, "CRYTOWN" },
    { 0, 222, 50, 0, "CLIFFS" },
    { 0, 240, 76, 0, "MARSH" },
    { 0, 240, 102, 0, "QUARRY" },
    { 0, 240, 128, 1, "CAMP" },
    { 0, 165, 128, 0, "FOREST" },
    { 0, 165, 88, 1, "PRISON" },
    { 0, 75, 90, 0, "GAUNTLET" },
    { 0, 70, 128, 1, "HEAVENFALL" },
    { 1, 140, 0, 1, "KETER" },
    { 1, 40, 20, 1, "BINAH" },
    { 1, 240, 20, 1, "CHOKMAH" },
    { 1, 40, 60, 1, "GEVURAH" },
    { 1, 240, 60, 1, "CHESED" },
    { 1, 140, 68, 1, "TIFERET" },
    { 1, 40, 100, 1, "HOD" },
    { 1, 240, 100, 1, "NETZACH" },
    { 1, 140, 108, 1, "YESOD" },
    { 1, 140, 136, 1, "MALKUTH" },
};
static const MapScreenLink MAPSCREEN_LINKS[MAPSCREEN_LINK_N] = {
    { 0, 1, "" },
    { 1, 5, "" },
    { 5, 4, "" },
    { 4, 2, "" },
    { 2, 3, "" },
    { 5, 6, "" },
    { 6, 7, "" },
    { 7, 8, "" },
    { 8, 9, "" },
    { 9, 10, "" },
    { 10, 11, "" },
    { 5, 12, "" },
    { 12, 13, "" },
    { 23, 22, "PATH OF TAU" },
    { 23, 21, "PATH OF QOPH" },
    { 20, 23, "PATH OF SHIN" },
    { 20, 21, "PATH OF PEH" },
    { 20, 22, "PATH OF RESH" },
    { 21, 22, "PATH OF TZADDI" },
    { 19, 22, "PATH OF SAMEKH" },
    { 21, 19, "PATH OF NUN" },
    { 20, 19, "PATH OF AYIN" },
    { 18, 21, "PATH OF KAPH" },
    { 18, 19, "PATH OF YOD" },
    { 17, 20, "PATH OF MEM" },
    { 17, 19, "PATH OF LAMED" },
    { 18, 17, "PATH OF TETH" },
    { 15, 19, "PATH OF ZAYIN" },
    { 15, 17, "PATH OF HETH" },
    { 16, 19, "PATH OF HE" },
    { 18, 16, "PATH OF VAU" },
    { 15, 16, "PATH OF DALETH" },
    { 14, 19, "PATH OF GIMEL" },
    { 16, 14, "PATH OF ALEPH" },
    { 15, 14, "PATH OF BETH" },
};
static const short MAP_WHERE[71] = { 5, 5, 10, 11, 9, 6, 4, 2, 7, 8, 12, 12, 12, 12, 12, 12, 13, 23, 1, 22, 1013, 21, 1014, 20, 1015, 1016, 1017, 1018, 19, 1019, 1020, 1021, 18, 1022, 1023, 17, 1024, 1025, 1026, 15, 1027, 1028, 16, 1029, 1030, 1031, 14, 1032, 1033, 1034, 23, 22, 21, 20, 19, 18, 17, 15, 16, 14, 4, 2, 5, 7, 4, 4, 4, 2, 2, 2, 3 };

/* ---- Leg 3: bases, Generals, Nero, endings (logic.json leg3) ---- */
#define NPC_PENDING_LEG3_FIRST 100
#define LEG3_POST_N 49
#define LEG3_KIND_GUARD 0
#define LEG3_KIND_GENERAL 1
#define LEG3_KIND_KING 2
#define LEG3_KIND_FINAL 3
/* sprite: LEG3_SPRITES index (LEG3_SPRITE_NAMES in the baker), -1 none */
#define LEG3_KIND_BOUNTY 4
#define LEG3_KIND_SHAKEDOWN 5
/* arrest/exec/threat flags: FLAG_* set by the fate menu (-1 none); loot is
   what a shakedown (threaten or execute) takes: item+qty, CryMon+level. */
typedef struct { int kit, kind, gen, set_flag, win_talk, marks, sprite; const char *title;
                 int arrest_flag, exec_flag, threat_flag, loot_item, loot_qty, loot_sp, loot_lv;
                 int talk_arrest, talk_exec, talk_threat; } Leg3Post;
static const Leg3Post LEG3_POSTS[LEG3_POST_N] = {
    { 16, 0, 0, FLAG_BEAT_BASE_MALKUTH_A, 197, 14, 0, "BASE GUARD SENDS SPARKIT", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* baseMalkuthA */
    { 17, 0, 0, FLAG_BEAT_BASE_MALKUTH_B, 199, 14, 0, "BASE GUARD SENDS PIPSPROUT", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* baseMalkuthB */
    { 18, 1, 0, FLAG_MEDAL_BRONZE_STAR, 145, 30, 2, "GENERAL HARROW SENDS TUNNELER", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* generalHarrow */
    { 19, 0, 1, FLAG_BEAT_BASE_YESOD_A, 201, 16, 0, "BASE GUARD SENDS SOOTTICK", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* baseYesodA */
    { 20, 0, 1, FLAG_BEAT_BASE_YESOD_B, 203, 16, 0, "BASE GUARD SENDS SPARKFLY", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* baseYesodB */
    { 21, 1, 1, FLAG_MEDAL_PURPLE_HEART, 149, 35, 3, "GENERAL ASHGROVE SENDS ARCWASP", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* generalAshgrove */
    { 22, 0, 2, FLAG_BEAT_BASE_NETZACH_A, 205, 18, 0, "BASE GUARD SENDS MOONCALF", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* baseNetzachA */
    { 23, 0, 2, FLAG_BEAT_BASE_NETZACH_B, 207, 18, 0, "BASE GUARD SENDS CARDKIN", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* baseNetzachB */
    { 24, 1, 2, FLAG_MEDAL_POW_MEDAL, 153, 40, 4, "GENERAL STROUD SENDS FATEWEAVER", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* generalStroud */
    { 25, 0, 3, FLAG_BEAT_BASE_HOD_A, 209, 20, 0, "BASE GUARD SENDS SNOWBELL", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* baseHodA */
    { 26, 0, 3, FLAG_BEAT_BASE_HOD_B, 211, 20, 0, "BASE GUARD SENDS TALLOWISP", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* baseHodB */
    { 27, 1, 3, FLAG_MEDAL_SILVER_STAR, 157, 45, 5, "GENERAL VALE SENDS GLOOMSPIDER", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* generalVale */
    { 28, 0, 4, FLAG_BEAT_BASE_TIFERET_A, 213, 22, 0, "BASE GUARD SENDS DAWNCHICK", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* baseTiferetA */
    { 29, 0, 4, FLAG_BEAT_BASE_TIFERET_B, 215, 22, 0, "BASE GUARD SENDS MOTLEY", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* baseTiferetB */
    { 30, 1, 4, FLAG_MEDAL_GOLD_STAR, 161, 50, 6, "GENERAL KESSLER SENDS HORNBLAZE", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* generalKessler */
    { 31, 0, 5, FLAG_BEAT_BASE_CHESED_A, 217, 24, 0, "BASE GUARD SENDS ATLASHELL", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* baseChesedA */
    { 32, 0, 5, FLAG_BEAT_BASE_CHESED_B, 219, 24, 0, "BASE GUARD SENDS TIDEWOLF", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* baseChesedB */
    { 33, 1, 5, FLAG_MEDAL_LEGION_OF_MERIT, 165, 55, 7, "GENERAL MORROW SENDS FLOECLAW", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* generalMorrow */
    { 34, 0, 6, FLAG_BEAT_BASE_GEVURAH_A, 221, 26, 0, "BASE GUARD SENDS WHEELHOG", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* baseGevurahA */
    { 35, 0, 6, FLAG_BEAT_BASE_GEVURAH_B, 223, 26, 0, "BASE GUARD SENDS BLAZELYNX", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* baseGevurahB */
    { 36, 1, 6, FLAG_MEDAL_FLYING_CROSS, 169, 60, 8, "GENERAL CRANE SENDS GRANDROC", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* generalCrane */
    { 37, 0, 7, FLAG_BEAT_BASE_BINAH_A, 225, 28, 0, "BASE GUARD SENDS GEMINAL", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* baseBinahA */
    { 38, 0, 7, FLAG_BEAT_BASE_BINAH_B, 227, 28, 0, "BASE GUARD SENDS FLOECLAW", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* baseBinahB */
    { 39, 1, 7, FLAG_MEDAL_SERVICE_CROSS, 173, 65, 9, "GENERAL BLACKWOOD SENDS ROOTKING", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* generalBlackwood */
    { 40, 0, 8, FLAG_BEAT_BASE_CHOKMAH_A, 229, 30, 0, "BASE GUARD SENDS KESTRAIL", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* baseChokmahA */
    { 41, 0, 8, FLAG_BEAT_BASE_CHOKMAH_B, 231, 30, 0, "BASE GUARD SENDS GLACIERJAW", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* baseChokmahB */
    { 42, 1, 8, FLAG_MEDAL_OF_HONOR, 177, 70, 10, "GENERAL SORREL SENDS ECLIPSAUR", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* generalSorrel */
    { 43, 0, -1, FLAG_BEAT_PALACE_GUARD_A, 137, 34, 1, "ROYAL GUARD SENDS CRAGSAGE", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* palaceGuardA */
    { 44, 0, -1, FLAG_BEAT_PALACE_GUARD_B, 139, 36, 1, "ROYAL GUARD SENDS MAGISTOWL", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* palaceGuardB */
    { 45, 2, -1, FLAG_BEAT_NERO, 181, 80, 19, "WEEPING KING NERO SENDS DEATHKNELL", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* nero */
    { 46, 3, -1, FLAG_TITLE_GODSLAYER, 191, 0, -1, "HEAVENFALL TURNS ON YOU", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* heavenfallFinal */
    { 47, 0, -1, FLAG_EXPELLED_GHOST_A, 290, 0, 0, "A SOLDIER'S GHOST RISES", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* ghostSoldierA */
    { 48, 0, -1, FLAG_EXPELLED_GHOST_B, 292, 0, 0, "A SERGEANT'S GHOST RISES", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* ghostSoldierB */
    { 49, 0, -1, FLAG_EXPELLED_ORIEL, 294, 0, 0, "ORIEL'S BOUND CRYPTLAMP FLARES", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* ghostOriel */
    { 50, 4, -1, FLAG_BEAT_VESK, 270, 40, -1, "MOURNER VESK SENDS GALLOWCROW", 134, 135, -1, -1, 0, -1, 0, 271, 272, -1 }, /* mournerVesk */
    { 51, 4, -1, FLAG_BEAT_MALLORY, 344, 25, -1, "RED MALLORY SENDS BRIARFOX", 140, 141, -1, -1, 0, -1, 0, 345, 346, -1 }, /* redMallory */
    { 52, 4, -1, FLAG_BEAT_SILAS, 349, 35, -1, "SILAS THE FENCE SENDS CINDERMITE", 144, 145, -1, -1, 0, -1, 0, 350, 351, -1 }, /* silasFence */
    { 53, 5, -1, FLAG_BEAT_ALDOUS, 329, 20, -1, "SIR ALDOUS SENDS JOLTHARE", -1, 152, 151, 10, 1, 17, 14, -1, 331, 330 }, /* sirAldous */
    { 54, 5, -1, FLAG_BEAT_BRIN, 334, 30, -1, "DAME BRIN SENDS RUNEMOTE", -1, 156, 155, 18, 2, 14, 16, -1, 336, 335 }, /* dameBrin */
    { 55, 5, -1, FLAG_BEAT_ROOK, 339, 40, -1, "CAPTAIN ROOK SENDS RIMEOWL", -1, 160, 159, 11, 1, 15, 18, -1, 341, 340 }, /* captainRook */
    { 56, 4, -1, FLAG_BEAT_GARROW, 384, 30, -1, "KNIFE-HAND GARROW SENDS BLAZELYNX", 173, 174, -1, -1, 0, -1, 0, 385, 386, -1 }, /* garrowOutlaw */
    { 57, 4, -1, FLAG_BEAT_KAEL, 404, 45, -1, "DESERTER KAEL SENDS WIDOWSHADE", 182, 183, -1, -1, 0, -1, 0, 405, 406, -1 }, /* kaelDeserter */
    { 58, 0, -1, FLAG_BEAT_OSK1, 468, 30, 0, "HERMIT OSK SENDS BOULDERAM", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* oskOne */
    { 59, 0, -1, FLAG_BEAT_OSK2, 471, 60, 0, "HERMIT OSK SENDS HORNBLAZE", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* oskTwo */
    { 60, 0, -1, FLAG_BEAT_OSK3, 474, 120, 0, "HERMIT OSK SENDS ROOTKING", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* oskThree */
    { 61, 0, -1, FLAG_BEAT_CALDER_POST, 487, 250, 0, "CALDER SENDS SABLECLAW", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* calderPost */
    { 62, 0, -1, FLAG_BEAT_HOLLOW_RANGER, 514, 90, 0, "THE LOST RANGER SENDS GALLOWCROW", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* hollowRanger */
    { 63, 0, -1, FLAG_BEAT_HOLLOW_SHADE, 517, 110, 0, "THE HOLLOW SHADE SENDS DEATHKNELL", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* hollowShade */
    { 64, 0, -1, FLAG_BEAT_HOLLOW_WARDEN, 521, 150, 0, "THE HOLLOW WARDEN SENDS THUNDERQUEEN", -1, -1, -1, -1, 0, -1, 0, -1, -1, -1 }, /* hollowWarden */
};
static const int LEG3_POST_SONG[LEG3_POST_N] = {
    -1, -1, 13, -1, -1, 13, -1, -1, 13, -1, -1, 13, -1, -1, 13, -1, -1, 13, -1, -1, 13, -1, -1, 13, -1, -1, 13, -1, -1, 14, 14, -1, -1, -1, 13, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 14, -1, -1, 14
};
#define SONG_FOR_LEAD 13
#define SONG_FOR_COMMANDER_FINAL 13
#define SONG_FOR_HEAVENFALL_GRAVE 14
#define SONG_FOR_SHINIGAMI 13
#define LEG3_GEN_N 9
typedef struct { int medal_flag, arrested_flag, talk_arrest, talk_execute; const char *medal, *name; } Leg3Gen;
static const Leg3Gen LEG3_GENS[LEG3_GEN_N] = {
    { FLAG_MEDAL_BRONZE_STAR, FLAG_ARRESTED_HARROW, 146, 147, "BRONZE STAR", "GENERAL HARROW" },
    { FLAG_MEDAL_PURPLE_HEART, FLAG_ARRESTED_ASHGROVE, 150, 151, "PURPLE HEART", "GENERAL ASHGROVE" },
    { FLAG_MEDAL_POW_MEDAL, FLAG_ARRESTED_STROUD, 154, 155, "PRISONER OF WAR MEDAL", "GENERAL STROUD" },
    { FLAG_MEDAL_SILVER_STAR, FLAG_ARRESTED_VALE, 158, 159, "SILVER STAR", "GENERAL VALE" },
    { FLAG_MEDAL_GOLD_STAR, FLAG_ARRESTED_KESSLER, 162, 163, "GOLD STAR", "GENERAL KESSLER" },
    { FLAG_MEDAL_LEGION_OF_MERIT, FLAG_ARRESTED_MORROW, 166, 167, "LEGION OF MERIT", "GENERAL MORROW" },
    { FLAG_MEDAL_FLYING_CROSS, FLAG_ARRESTED_CRANE, 170, 171, "DISTINGUISHED FLYING CROSS", "GENERAL CRANE" },
    { FLAG_MEDAL_SERVICE_CROSS, FLAG_ARRESTED_BLACKWOOD, 174, 175, "DISTINGUISHED SERVICE CROSS", "GENERAL BLACKWOOD" },
    { FLAG_MEDAL_OF_HONOR, FLAG_ARRESTED_SORREL, 178, 179, "MEDAL OF HONOR", "GENERAL SORREL" },
};
#define LEG3_FLAG_N 56
static const int LEG3_FLAG_ID[LEG3_FLAG_N] = { FLAG_BEAT_BASE_MALKUTH_A, FLAG_BEAT_BASE_MALKUTH_B, FLAG_MEDAL_BRONZE_STAR, FLAG_ARRESTED_HARROW, FLAG_BEAT_BASE_YESOD_A, FLAG_BEAT_BASE_YESOD_B, FLAG_MEDAL_PURPLE_HEART, FLAG_ARRESTED_ASHGROVE, FLAG_BEAT_BASE_NETZACH_A, FLAG_BEAT_BASE_NETZACH_B, FLAG_MEDAL_POW_MEDAL, FLAG_ARRESTED_STROUD, FLAG_BEAT_BASE_HOD_A, FLAG_BEAT_BASE_HOD_B, FLAG_MEDAL_SILVER_STAR, FLAG_ARRESTED_VALE, FLAG_BEAT_BASE_TIFERET_A, FLAG_BEAT_BASE_TIFERET_B, FLAG_MEDAL_GOLD_STAR, FLAG_ARRESTED_KESSLER, FLAG_BEAT_BASE_CHESED_A, FLAG_BEAT_BASE_CHESED_B, FLAG_MEDAL_LEGION_OF_MERIT, FLAG_ARRESTED_MORROW, FLAG_BEAT_BASE_GEVURAH_A, FLAG_BEAT_BASE_GEVURAH_B, FLAG_MEDAL_FLYING_CROSS, FLAG_ARRESTED_CRANE, FLAG_BEAT_BASE_BINAH_A, FLAG_BEAT_BASE_BINAH_B, FLAG_MEDAL_SERVICE_CROSS, FLAG_ARRESTED_BLACKWOOD, FLAG_BEAT_BASE_CHOKMAH_A, FLAG_BEAT_BASE_CHOKMAH_B, FLAG_MEDAL_OF_HONOR, FLAG_ARRESTED_SORREL, FLAG_BEAT_PALACE_GUARD_A, FLAG_BEAT_PALACE_GUARD_B, FLAG_HAS_GOLDEN_SHACKLES, FLAG_BEAT_NERO, FLAG_NERO_TRIED, FLAG_TITLE_KINGSLAYER, FLAG_FATHER_ABANDONED, FLAG_TITLE_GODSLAYER, FLAG_TITLE_BLOODY, FLAG_LEG3_ENDED, FLAG_TALKED_MARN, FLAG_CITIZEN_THANKED_MALKUTH, FLAG_CITIZEN_THANKED_YESOD, FLAG_CITIZEN_THANKED_NETZACH, FLAG_CITIZEN_THANKED_HOD, FLAG_CITIZEN_THANKED_TIFERET, FLAG_CITIZEN_THANKED_CHESED, FLAG_CITIZEN_THANKED_GEVURAH, FLAG_CITIZEN_THANKED_BINAH, FLAG_CITIZEN_THANKED_CHOKMAH };
static const int LEG3_SAVE_ID[LEG3_FLAG_N] = { 64, 65, 82, 91, 66, 67, 83, 92, 68, 69, 84, 93, 70, 71, 85, 94, 72, 73, 86, 95, 74, 75, 87, 96, 76, 77, 88, 97, 78, 79, 89, 98, 80, 81, 90, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 112, 113, 114, 115, 116, 117, 118, 119, 120 };
#define LEG3_F_HAS_GOLDEN_SHACKLES 38
#define LEG3_F_BEAT_NERO 39
#define LEG3_F_NERO_TRIED 40
#define LEG3_F_TITLE_KINGSLAYER 41
#define LEG3_F_FATHER_ABANDONED 42
#define LEG3_F_TITLE_GODSLAYER 43
#define LEG3_F_TITLE_BLOODY 44
#define LEG3_F_LEG3_ENDED 45
#define LEG3_TALK_GOLDEN_SHACKLES_GET 142
#define LEG3_TALK_GENERAL_ARREST_NO_SHACKLES 143
#define LEG3_TALK_NERO_TRIAL 182
#define LEG3_TALK_NERO_EXECUTE 183
#define LEG3_TALK_NERO_CROWNED 184
#define LEG3_TALK_FATHER_PROUD 185
#define LEG3_TALK_FATHER_SACRIFICE 186
#define LEG3_TALK_FATHER_MONSTER 187
#define LEG3_TALK_HF_END_NONE 188
#define LEG3_TALK_HF_END_TAMED 189
#define LEG3_TALK_HF_END_HOSTILE 190
#define LEG3_TALK_HF_END_GODSLAYER 191
#define LEG3_TALK_HF_END_BLOODY 192
#define LEG3_REP_ARREST 10
#define LEG3_REP_EXECUTE -25
#define LEG3_REP_TRIAL 50
#define LEG3_REP_KING_EXECUTE -50
#define LEG3_REP_BOUNTY_ARREST 5
#define LEG3_REP_BOUNTY_EXECUTE -10
#define LEG3_REP_THREATEN -3
#define LEG3_REP_SHAKEDOWN_EXECUTE -10
#define LEG3_ITEM_SHACKLES 20
#define LEG3_ITEM_GOLDEN 21
#define LEG3_SP_HEAVENFALL 19
#define LEG3_SCREAM_N 3
#define LEG3_SCREAM_GAP_FRAMES 42
#define LEG3_TINT_R 150
#define LEG3_TINT_G 0
#define LEG3_TINT_B 0
#define LEG3_TINT_A256 56
#define LEG3_NAME_KINGSLAYER "KINGSLAYER"
#define LEG3_NAME_GODSLAYER "GODSLAYER"
#define LEG3_NAME_BLOODY "MAX THE BLOODY"
#define LEG3_END_WAR "THE WEEPING ARMY IS FINISHED. THE CITIES OF THE SEPHIROT ARE FREE."
#define LEG3_END_TRIAL "NERO LIVES OUT HIS LIFE IN A PRISON CELL IN MALKUTH."
#define LEG3_END_CROWNED "QUEEN MAX, THE KINGSLAYER, RULES FROM THE THRONE IN KETER."
#define LEG3_END_FATHER_STAYS "FATHER COMES HOME TO CRYTOWN WITH HER."
#define LEG3_END_FATHER_GONE "FATHER NEVER SPEAKS TO HER AGAIN."
#define LEG3_END_NONE "MAX HAS NO GOD AT HER SIDE. SHE NEVER NEEDED ONE."
#define LEG3_END_TAMED "HEAVENFALL STAYS AT HER SIDE FOR THE REST OF HER DAYS."
#define LEG3_END_GODSLAYER "THEY CALL HER GODSLAYER NOW. NOBODY SAYS IT TO HER FACE."
#define LEG3_END_BLOODY "MAX THE BLOODY IS DEAD. THE STORIES ABOUT HER ARE NOT KIND."
#define LEG3_END_END "THE END"

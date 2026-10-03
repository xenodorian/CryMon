/* ----------------------------------------------------------------------
 * The world: all 4 maps, verbatim from CryMon's love/game/src/data.lua
 * (data.HOUSE/VELD/FOREST/GROVE), data.isSolidTile (SOLID_SET), and
 * love/game/src/draw.lua (paintTile). 32px tiles in the original,
 * drawn here at 20px (matching every earlier step); VELD/FOREST/GROVE
 * are much bigger than the 320x240 screen, so this step adds camera
 * scrolling (compute_camera below) -- HOUSE still ends up centered
 * exactly like before, since a map smaller than the screen just gets
 * a centered (possibly negative) camera offset.
 *
 * GROVE's mid-map 'D' row (data.lua splits the Cathleen half from the
 * Shinigami half, opened only after Cathleen is caught) is walkable
 * here rather than gated: no cathCaught state exists yet (that's
 * battle/catching, a later milestone), and the reference project's
 * own data.lua notes that native/crymon.c already ships this same
 * simplification, so it's a documented, precedented deferral rather
 * than a new gap.
 * ---------------------------------------------------------------------- */
#define TILE 20

/* ATK_STR/ATK_MAG tag which raw stat a move draws on. Defined before
   content_logic.inc so baked NATURE_MOVES / TOXIC_STAT can use them. */
#define ATK_STR 0
#define ATK_MAG 1

typedef struct {
    const char *const *rows;
    int cols, rows_n;
} Map;


/*
 * Story, maps, species, items, and talk beats are NOT authored here.
 * They live in content/*.json (shared with the web build) and are
 * baked into src/content_*.inc by tools/bake_content.py. Edit the
 * JSON, bake, then rebuild. Runtime (video, Maple, battle loop) stays
 * in this file.
 *
 * hello-world-dreamcast/src/hello.c for the video/vblank/Maple-driver
 * derivation notes against KallistiOS's real source, unchanged since
 * step 1). A full, playable port of the reference LÖVE build
 * (xenodorian/CryMon, the Lua sources under love/game/src): title
 * screen, all 4 maps
 * (HOUSE/VELD/FOREST/GROVE) with camera scrolling and every door/warp
 * between them, the starting room's props and Quillpup/bandage
 * grants, every VELD/FOREST/GROVE NPC and pickup, the full turn-based
 * battle system (attack/special-minigame/guard/items/capture/XP),
 * wild encounters, Bram's shop, and the single ending (DEMO_END,
 * reached via the Grove/Shinigami/Anne chain and the resurrection
 * choice -- see draw_choice()). Each major system's own section comment below
 * (search for "----" banners) cites the exact Lua functions/tables it
 * ports and any formula it reproduces verbatim.
 *
 * Known, deliberate departures from the reference -- each is also
 * called out inline at the relevant code, this is just the index:
 *   - Item icons: bag and shop rows show the real items/ PNG icon
 *     next to each item now; the battle item menu stays text-only
 *     (its rows already run long with stat/percent text and BCONTENT_W
 *     is a small fraction of the full-screen bag/shop menus).
 *   - No manual in-battle "switch to bench monster" item-menu row --
 *     the automatic emergency swap-in on a guard-phase faint is
 *     ported (state.lua does this one automatically too), just not
 *     the player-chosen mid-turn version. (Manual party *lead*
 *     switching, engine.ts's cycleParty(to), IS ported -- see the
 *     party-menu section comment.)
 *   - Sprites: the player and the 3 walking world actors (Mason, Anne,
 *     FOREST soldiers) get a real 4-frame walk cycle per direction;
 *     every stationary world NPC and every fightable species' battle
 *     art idle-animates too now (4 frames at 4fps, 3fps for Shinigami,
 *     matching drawWorld()/drawBattle()'s own clock-driven frame
 *     index -- see draw_npc_idle()/draw_battle_sprites()). Map tiles
 *     still draw as flat color blocks (paintTile's own palette, ported
 *     in full -- see draw_tile); the reference itself does this too
 *     for terrain (draw.lua's paintTile is flat rectangles in the
 *     LÖVE build as well, not a tileset image).
 *   - Dialogue/UI text is upper-cased to fit this port's own hand-
 *     authored 8x8 bitmap font (no lowercase glyph set -- a real
 *     mixed-case font is its own separate undertaking), but every
 *     every TALK_* array (and DEMO_END) now carries the reference's own
 *     punctuation (apostrophes, periods, commas, question/exclamation
 *     marks -- see glyph_apostrophe/period/comma/question/exclaim
 *     near draw_glyph). Characters this font still can't render
 *     (quotes, colons/semicolons folded to commas, em dashes folded
 *     to periods) are the only things actually dropped or substituted
 *     from the source text now.
 */

#include <stdint.h>

typedef unsigned char  u8;
typedef unsigned short u16;
typedef unsigned int   u32;

#include "sprites.h"

/* No libc here, but GCC may still emit calls to these for large struct
   initialisers/copies (the Bag grew an `extra[]` array for quest items). */
void *memset(void *d, int c, __SIZE_TYPE__ n);
void *memset(void *d, int c, __SIZE_TYPE__ n) {
    unsigned char *p = (unsigned char *)d;
    while(n--) *p++ = (unsigned char)c;
    return d;
}
void *memcpy(void *d, const void *s, __SIZE_TYPE__ n);
void *memcpy(void *d, const void *s, __SIZE_TYPE__ n) {
    unsigned char *p = (unsigned char *)d;
    const unsigned char *q = (const unsigned char *)s;
    while(n--) *p++ = *q++;
    return d;
}
#include "disc.h"
#include "chip.h"
#include "save.h"


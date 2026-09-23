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
#include "chip.h"
#include "save.h"

#define PVR_BASE 0xa05f8000u
#define PVR(reg) (*(volatile u32 *)(PVR_BASE + (reg)))

#define PVR_BORDER_COLOR     0x040
#define PVR_FB_CFG_1         0x044
#define PVR_FB_CFG_2         0x048
#define PVR_RENDER_MODULO    0x04c
#define PVR_FB_ADDR          0x050
#define PVR_FB_SIZE          0x05c
#define PVR_VPOS_IRQ         0x0cc
#define PVR_IL_CFG           0x0d0
#define PVR_BORDER_X         0x0d4
#define PVR_SCAN_CLK         0x0d8
#define PVR_BORDER_Y         0x0dc
#define PVR_VIDEO_CFG        0x0e8
#define PVR_BITMAP_X         0x0ec
#define PVR_BITMAP_Y         0x0f0
#define PVR_SYNC_STATUS      0x10c  /* bits 0-8: nonzero while in vblank */

#define SCREEN_W 320
#define SCREEN_H 240

/* Double buffering, pipelined: each iteration flips to show whatever
   was drawn into the back buffer *last* iteration, then draws the
   next frame into the buffer that just became hidden. This is the
   order a KallistiOS/Dreamcast homebrew community reference (a
   DCEmulation forum thread on KOS double buffering) describes as
   correct: wait_vblank() -> flip the already-drawn buffer into view
   -> only then draw the next frame. The single-buffer version tried
   before this made tearing worse, not better, since every redraw
   wrote directly into whatever the display was actively scanning;
   double buffering keeps drawing entirely off-screen, so only a
   correctly-timed flip is needed to avoid tearing.

   This requires drawing every frame unconditionally, not just when
   something changed: alternating buffers while only sometimes
   redrawing would show one buffer's fresh content and then the
   *other* buffer's stale content every other frame once movement
   stops, which is its own visible glitch. Redrawing every frame is
   safe here specifically because it only ever touches the hidden
   buffer -- it was only unsafe in the single-buffer version. */
#define FB_OFFSET0 0x000000u
#define FB_OFFSET1 0x040000u

static u32 fb_back_offset = FB_OFFSET1;
static volatile u16 *draw_fb = (volatile u16 *)(0xa5000000u + FB_OFFSET1);

static void fb_flip(void) {
    PVR(PVR_FB_ADDR) = fb_back_offset;
    fb_back_offset = (fb_back_offset == FB_OFFSET0) ? FB_OFFSET1 : FB_OFFSET0;
    draw_fb = (volatile u16 *)(0xa5000000u + fb_back_offset);
}

/* DM_320x240_NTSC timing parameters, from KallistiOS's vid_builtin table */
#define SCANLINES 262
#define CLOCKS    857
#define BITMAPX   164
#define BITMAPY   24
#define SCANINT1  21
#define SCANINT2  260
#define BORDERX1  141
#define BORDERX2  843
#define BORDERY1  24
#define BORDERY2  263

static void video_init(void) {
    PVR(PVR_VIDEO_CFG) = PVR(PVR_VIDEO_CFG) | 0x8u;
    PVR(PVR_FB_CFG_1)  = PVR(PVR_FB_CFG_1) & ~1u;

    PVR(PVR_BORDER_COLOR) = 0;

    PVR(PVR_FB_CFG_1) = (1u << 2);
    PVR(PVR_FB_CFG_2) = 1u | (1u << 3);

    PVR(PVR_RENDER_MODULO) = (SCREEN_W * 2) / 8;
    PVR(PVR_FB_ADDR) = 0;

    PVR(PVR_FB_SIZE) = (((SCREEN_W * 2) / 4) - 1)
                      | (1u << 20)
                      | ((SCREEN_H - 1u) << 10);

    PVR(PVR_VPOS_IRQ) = (SCANINT1 << 16) | SCANINT2;
    PVR(PVR_IL_CFG) = 0x100;

    PVR(PVR_BORDER_X) = (BORDERX1 << 16) | BORDERX2;
    PVR(PVR_BORDER_Y) = (BORDERY1 << 16) | BORDERY2;
    PVR(PVR_SCAN_CLK) = (SCANLINES << 16) | CLOCKS;

    PVR(PVR_VIDEO_CFG) = PVR(PVR_VIDEO_CFG) | 0x100u;

    PVR(PVR_BITMAP_X) = BITMAPX;
    PVR(PVR_BITMAP_Y) = (BITMAPY << 16) | BITMAPY;

    *(volatile u32 *)0xa0702c00 =
        (*(volatile u32 *)0xa0702c00 & 0xfffffcffu) | (3u << 8);

    PVR(PVR_VIDEO_CFG) = PVR(PVR_VIDEO_CFG) & ~0x8u;
    PVR(PVR_FB_CFG_1)  = PVR(PVR_FB_CFG_1) | 1u;
}

/* Checked against KallistiOS's own vid_waitvbl() (hardware/video.c):
   wait for vblank to start, then wait for it to end, so each call
   corresponds to exactly one fresh frame. */
static void wait_vblank(void) {
    while(!(PVR(PVR_SYNC_STATUS) & 0x01ffu))
        ;
    while(PVR(PVR_SYNC_STATUS) & 0x01ffu)
        ;
}

static void vram_clear(void) {
    u32 i;
    for(i = 0; i < (u32)SCREEN_W * SCREEN_H; i++)
        draw_fb[i] = 0x0000;
}

/* Screen fade to/from black (bed heal, a party wipe teleporting home
   -- see main()'s fade_state machine). There's no alpha channel to
   composite with here, so this darkens whatever was already drawn
   into draw_fb this frame, in place, as the very last step before
   fb_flip -- level is 0 (untouched) to FADE_STEPS (fully black).
   FADE_STEPS is a power of 2 so the per-channel scale is a multiply
   + shift, not a divide, cheap enough to run over all 76800 pixels
   every frame a fade is in progress.

   This is the *resolution* of the darkening, not its duration. How long
   each phase lasts comes from content/logic.json's screenFade, baked as
   LOGIC_FADE_OUT/HOLD/IN_FRAMES; fade_level() below maps phase progress
   onto this scale. The two were the same number for a while, which is
   why the hold phase silently lasted one frame instead of its three. */
#define FADE_STEPS 16
/* Leg 2.9 mercy state — must be before apply_fade uses red tint */
static int g_mercy_red_fade = 0;
static unsigned int g_executed_mask = 0;

static void apply_fade(int level) {
    u32 i, keep;
    if(level <= 0) return;
    if(level >= FADE_STEPS) {
        if(g_mercy_red_fade) {
            u32 j;
            for(j = 0; j < (u32)SCREEN_W * SCREEN_H; j++) draw_fb[j] = ((u16)(((80 >> 3) << 11) | ((8 >> 2) << 5) | (8 >> 3)));
        } else {
            vram_clear();
        }
        return;
    }
    keep = (u32)(FADE_STEPS - level);
    for(i = 0; i < (u32)SCREEN_W * SCREEN_H; i++) {
        u16 c = draw_fb[i];
        u16 r = (u16)(((u32)((c >> 11) & 0x1Fu) * keep) >> 4);
        u16 g = (u16)(((u32)((c >> 5) & 0x3Fu) * keep) >> 4);
        u16 b = (u16)(((u32)(c & 0x1Fu) * keep) >> 4);
        draw_fb[i] = (u16)((r << 11) | (g << 5) | b);
    }
}

static void put_pixel(int x, int y, u16 color) {
    if(x < 0 || x >= SCREEN_W || y < 0 || y >= SCREEN_H)
        return;
    draw_fb[y * SCREEN_W + x] = color;
}

static void fill_rect(int x, int y, int w, int h, u16 color) {
    int px, py;
    for(py = y; py < y + h; py++)
        for(px = x; px < x + w; px++)
            put_pixel(px, py, color);
}

static u16 rgb565(u8 r, u8 g, u8 b) {
    return (u16)(((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3));
}

/* Blits a w x h RGB565 sprite (see sprites.h) with its top-left
   corner at (x, y), skipping any pixel equal to SPRITE_KEY
   (color-keyed transparency -- the sprite has no separate alpha
   channel once baked into the array). */
static void blit_sprite(const u16 *px, int w, int h, int x, int y) {
    int sx, sy;
    for(sy = 0; sy < h; sy++) {
        for(sx = 0; sx < w; sx++) {
            u16 c = px[sy * w + sx];
            if(c != SPRITE_KEY)
                put_pixel(x + sx, y + sy, c);
        }
    }
}

/* Nearest-neighbor 2x blit — Mason's walk frames are a small figure
   in a padded 48x64 sheet, so he reads tiny next to Max unless the
   dest quad is doubled. Same pixels, twice the size. */
static void blit_sprite_2x(const u16 *px, int w, int h, int x, int y) {
    int sx, sy;
    for(sy = 0; sy < h; sy++) {
        for(sx = 0; sx < w; sx++) {
            u16 c = px[sy * w + sx];
            if(c != SPRITE_KEY) {
                int dx = x + sx * 2, dy = y + sy * 2;
                put_pixel(dx, dy, c);
                put_pixel(dx + 1, dy, c);
                put_pixel(dx, dy + 1, c);
                put_pixel(dx + 1, dy + 1, c);
            }
        }
    }
}

static void blit_sprite_fit(const u16 *px, int sw, int sh, int dx, int dy, int dw, int dh) {
    int x, y;
    for(y = 0; y < dh; y++) {
        int sy = y * sh / dh;
        for(x = 0; x < dw; x++) {
            int sx = x * sw / dw;
            u16 c = px[sy * sw + sx];
            if(c != SPRITE_KEY)
                put_pixel(dx + x, dy + y, c);
        }
    }
}

static void draw_party_mon_icon(int species, int x, int y);

/* Shiny palette swap: no second set of source art exists for shiny
   CryMon (see mint_shiny()), so this recolors the existing battle
   sprite at blit time instead -- swap the 5-bit R/G565's B channels
   (a cheap, cheerful "basic palette swap" that turns e.g. a green
   Quillpup magenta/teal) and nudge green down a notch so the swap
   reads as a genuinely different color rather than just a channel
   shuffle on near-gray pixels. */
static u16 shiny_tint(u16 c) {
    u16 r = (u16)((c >> 11) & 0x1F);
    u16 g = (u16)((c >> 5) & 0x3F);
    u16 b = (u16)(c & 0x1F);
    u16 g2 = (u16)(g > 8 ? g - 8 : 0);
    return (u16)((b << 11) | (g2 << 5) | r);
}

/* Battle enter/faint animation: one blitter used for both, driven by
   two independent params instead of two separate effects, so a
   battle sprite always renders through the same code whether it's
   idle, entering, or fainting. `revealed` (0..h) only draws that many
   rows counted up from the BOTTOM of the sprite -- at revealed==h
   it's a plain full blit, at revealed==0 nothing draws, and animating
   it 0->h over a few frames reads as the CryMon rising up into place
   (used when a fresh monster -- a new battle, or a bench swap-in --
   first appears). `fade` (0..16) scales every channel down toward
   black like apply_fade's screen-wide version, but per-sprite;
   animating it 16->0 reads as the CryMon fainting. The two are
   independent so idle draws (revealed=h, fade=16) are just the old
   plain blit_sprite/blit_sprite_shiny with extra math that folds
   away. */
static void blit_sprite_anim(const u16 *px, int w, int h, int x, int y,
                              int shiny, int revealed, int fade) {
    int sx, sy, start;
    if(revealed < 0) revealed = 0;
    if(revealed > h) revealed = h;
    if(fade < 0) fade = 0;
    if(fade > 16) fade = 16;
    start = h - revealed;
    for(sy = start; sy < h; sy++) {
        for(sx = 0; sx < w; sx++) {
            u16 c = px[sy * w + sx];
            if(c == SPRITE_KEY) continue;
            if(shiny) c = shiny_tint(c);
            if(fade < 16) {
                u16 r = (u16)((((c >> 11) & 0x1Fu) * (u32)fade) / 16u);
                u16 g = (u16)((((c >> 5) & 0x3Fu) * (u32)fade) / 16u);
                u16 b = (u16)(((c & 0x1Fu) * (u32)fade) / 16u);
                c = (u16)((r << 11) | (g << 5) | b);
            }
            put_pixel(x + sx, y + sy, c);
        }
    }
}

/* ----------------------------------------------------------------------
 * Font: 8x8, 1bpp glyphs, A-Z/0-9/space plus a handful of hand-added
 * symbol glyphs further down (-+/ for stat/damage text, then
 * '.,?! for real dialogue punctuation). Bit 7 = leftmost pixel of
 * each row. No lowercase set, so all on-screen text is upper-cased by
 * construction -- everything else the source text actually uses now
 * renders as written.
 * ---------------------------------------------------------------------- */
static const uint8_t font_AZ[26][8] = {
    /* A */ { 0b00111100, 0b01000010, 0b10000001, 0b10000001,
              0b11111111, 0b10000001, 0b10000001, 0b00000000 },
    /* B */ { 0b11111100, 0b10000010, 0b10000010, 0b11111100,
              0b10000010, 0b10000010, 0b11111100, 0b00000000 },
    /* C */ { 0b01111110, 0b10000000, 0b10000000, 0b10000000,
              0b10000000, 0b10000000, 0b01111110, 0b00000000 },
    /* D */ { 0b11111100, 0b10000010, 0b10000001, 0b10000001,
              0b10000001, 0b10000010, 0b11111100, 0b00000000 },
    /* E */ { 0b11111111, 0b10000000, 0b10000000, 0b11111100,
              0b10000000, 0b10000000, 0b11111111, 0b00000000 },
    /* F */ { 0b11111111, 0b10000000, 0b10000000, 0b11111100,
              0b10000000, 0b10000000, 0b10000000, 0b00000000 },
    /* G */ { 0b01111110, 0b10000000, 0b10000000, 0b10001111,
              0b10000001, 0b10000001, 0b01111110, 0b00000000 },
    /* H */ { 0b10000001, 0b10000001, 0b10000001, 0b11111111,
              0b10000001, 0b10000001, 0b10000001, 0b00000000 },
    /* I */ { 0b11111111, 0b00011000, 0b00011000, 0b00011000,
              0b00011000, 0b00011000, 0b11111111, 0b00000000 },
    /* J */ { 0b00000111, 0b00000010, 0b00000010, 0b00000010,
              0b10000010, 0b10000010, 0b01111100, 0b00000000 },
    /* K */ { 0b10000010, 0b10000100, 0b10001000, 0b11110000,
              0b10001000, 0b10000100, 0b10000010, 0b00000000 },
    /* L */ { 0b10000000, 0b10000000, 0b10000000, 0b10000000,
              0b10000000, 0b10000000, 0b11111111, 0b00000000 },
    /* M */ { 0b10000001, 0b11000011, 0b10100101, 0b10011001,
              0b10000001, 0b10000001, 0b10000001, 0b00000000 },
    /* N */ { 0b10000001, 0b11000001, 0b10100001, 0b10010001,
              0b10001001, 0b10000101, 0b10000011, 0b00000000 },
    /* O */ { 0b01111110, 0b10000001, 0b10000001, 0b10000001,
              0b10000001, 0b10000001, 0b01111110, 0b00000000 },
    /* P */ { 0b11111100, 0b10000010, 0b10000010, 0b11111100,
              0b10000000, 0b10000000, 0b10000000, 0b00000000 },
    /* Q */ { 0b01111110, 0b10000001, 0b10000001, 0b10000001,
              0b10010101, 0b10001001, 0b01110110, 0b00000000 },
    /* R */ { 0b11111110, 0b10000001, 0b10000001, 0b11111110,
              0b10010000, 0b10001000, 0b10000100, 0b00000000 },
    /* S */ { 0b01111110, 0b10000000, 0b10000000, 0b01111100,
              0b00000010, 0b00000010, 0b11111100, 0b00000000 },
    /* T */ { 0b11111111, 0b00011000, 0b00011000, 0b00011000,
              0b00011000, 0b00011000, 0b00011000, 0b00000000 },
    /* U */ { 0b10000001, 0b10000001, 0b10000001, 0b10000001,
              0b10000001, 0b10000001, 0b01111110, 0b00000000 },
    /* V */ { 0b10000001, 0b10000001, 0b10000001, 0b01000010,
              0b01000010, 0b00100100, 0b00011000, 0b00000000 },
    /* W */ { 0b10000001, 0b10000001, 0b10000001, 0b10100101,
              0b10100101, 0b11011011, 0b10000001, 0b00000000 },
    /* X */ { 0b10000001, 0b01000010, 0b00100100, 0b00011000,
              0b00100100, 0b01000010, 0b10000001, 0b00000000 },
    /* Y */ { 0b10000001, 0b01000010, 0b00100100, 0b00011000,
              0b00011000, 0b00011000, 0b00011000, 0b00000000 },
    /* Z */ { 0b11111111, 0b00000010, 0b00000100, 0b00001000,
              0b00010000, 0b00100000, 0b11111111, 0b00000000 },
};

/* Digits 0-9, same style/size as font_AZ. Needed for the room's HUD
   (Quillpup's level, the bandage count) -- nothing in the dialogue
   text itself uses digits. */
static const uint8_t font_09[10][8] = {
    /* 0 */ { 0b00111100, 0b01100110, 0b01101110, 0b01110110,
              0b01100110, 0b01100110, 0b00111100, 0b00000000 },
    /* 1 */ { 0b00011000, 0b00111000, 0b00011000, 0b00011000,
              0b00011000, 0b00011000, 0b01111110, 0b00000000 },
    /* 2 */ { 0b00111100, 0b01100110, 0b00000110, 0b00001100,
              0b00011000, 0b00110000, 0b01111110, 0b00000000 },
    /* 3 */ { 0b00111100, 0b01100110, 0b00000110, 0b00011100,
              0b00000110, 0b01100110, 0b00111100, 0b00000000 },
    /* 4 */ { 0b00001100, 0b00011100, 0b00101100, 0b01001100,
              0b01111110, 0b00001100, 0b00001100, 0b00000000 },
    /* 5 */ { 0b01111110, 0b01100000, 0b01111100, 0b00000110,
              0b00000110, 0b01100110, 0b00111100, 0b00000000 },
    /* 6 */ { 0b00011100, 0b00110000, 0b01100000, 0b01111100,
              0b01100110, 0b01100110, 0b00111100, 0b00000000 },
    /* 7 */ { 0b01111110, 0b00000110, 0b00001100, 0b00011000,
              0b00110000, 0b00110000, 0b00110000, 0b00000000 },
    /* 8 */ { 0b00111100, 0b01100110, 0b01100110, 0b00111100,
              0b01100110, 0b01100110, 0b00111100, 0b00000000 },
    /* 9 */ { 0b00111100, 0b01100110, 0b01100110, 0b00111110,
              0b00000110, 0b00001100, 0b00111000, 0b00000000 },
};

/* '-', '+', '/', needed by the battle system's stat-mod and damage
   messages ("STR+4", "FOE STR-3", "HP N/N") -- font_AZ/font_09 alone
   can't render any of these. */
static const uint8_t glyph_minus[8] = {
    0, 0, 0, 0b00111100, 0, 0, 0, 0,
};
static const uint8_t glyph_plus[8] = {
    0, 0b00011000, 0b00011000, 0b01111110, 0b00011000, 0b00011000, 0, 0,
};
static const uint8_t glyph_slash[8] = {
    0b00000011, 0b00000110, 0b00001100, 0b00011000,
    0b00110000, 0b01100000, 0b01000000, 0,
};

/* Punctuation, added to restore the reference's actual TALK_* text
   (apostrophes/periods/commas/question and exclamation marks) instead
   of the all-depunctuated placeholder text this font's original A-Z/
   0-9/-+/ set forced. Same minimalist style as the digits above (a
   6-wide glyph inside the 8-wide cell). */
static const uint8_t glyph_apostrophe[8] = {
    0b00110000, 0b00110000, 0b00100000, 0, 0, 0, 0, 0,
};
static const uint8_t glyph_period[8] = {
    0, 0, 0, 0, 0, 0, 0b00110000, 0,
};
static const uint8_t glyph_comma[8] = {
    0, 0, 0, 0, 0, 0b00110000, 0b00110000, 0b00100000,
};
static const uint8_t glyph_question[8] = {
    0b00111100, 0b01100110, 0b00001100, 0b00011000,
    0b00011000, 0, 0b00011000, 0,
};
static const uint8_t glyph_exclaim[8] = {
    0b00011000, 0b00011000, 0b00011000, 0b00011000,
    0b00011000, 0, 0b00011000, 0,
};

/* Every text call draws with a 2px black outline instead of sitting
   on an opaque box (see the now-boxless draw_dialogue_box/
   draw_menu_frame/draw_box/draw_hud_toast below).
   The outline is a full 2px ring (every offset from -2..2 except
   (0,0), 24 of them) drawn in black first so the border has no
   gaps at glyph corners even at that thickness, then the glyph
   itself is drawn once on top in the real color (not bold -- see
   git history for the bold faux-thickening pass this replaced).
   Costs ~24x the fill work per glyph over the original single-pass
   version, but glyphs are tiny (8x8) and this only runs for
   on-screen text. */
static void draw_glyph(int ox, int oy, const uint8_t bitmap[8], u16 color, int scale) {
    int row, col, sx, sy, dx, dy;

    for(dy = -2; dy <= 2; dy++) {
        for(dx = -2; dx <= 2; dx++) {
            if(dx == 0 && dy == 0)
                continue;
            for(row = 0; row < 8; row++) {
                uint8_t bits = bitmap[row];
                for(col = 0; col < 8; col++) {
                    if(!(bits & (0x80 >> col)))
                        continue;
                    for(sy = 0; sy < scale; sy++)
                        for(sx = 0; sx < scale; sx++)
                            put_pixel(ox + col * scale + sx + dx,
                                      oy + row * scale + sy + dy, 0x0000);
                }
            }
        }
    }

    for(row = 0; row < 8; row++) {
        uint8_t bits = bitmap[row];

        for(col = 0; col < 8; col++) {
            if(!(bits & (0x80 >> col)))
                continue;

            for(sy = 0; sy < scale; sy++)
                for(sx = 0; sx < scale; sx++)
                    put_pixel(ox + col * scale + sx,
                              oy + row * scale + sy, color);
        }
    }
}

/* Extra gap between characters, beyond the glyph's own 8px cell.
   draw_glyph's black outline is a full 2px ring around each glyph, so
   a gap under 2px still lets adjacent glyphs' outlines collide even
   though the glyphs themselves don't -- the previous 1px gap (scale)
   wasn't enough, still visibly overlapping; +2 flat pixels on top of
   the scaled base gap clears the outline reach with room to spare.
   CHAR_CELL is the resulting total per-character advance; every
   char-count-based word-wrap width (DIALOGUE_MAX_CHARS, the battle
   message box, the ending screen) is computed from it rather than a
   bare /8, so wrapping still matches the font's real on-screen
   width instead of running text past the edge of its box. */
#define LETTER_GAP(scale) ((scale) + 2)
#define CHAR_CELL(scale)  (8 * (scale) + LETTER_GAP(scale))

static void draw_text_s(const char *s, int x, int y, u16 color, int scale) {
    int cx = x;
    int px = CHAR_CELL(scale);
    for(; *s; s++) {
        if(*s >= 'A' && *s <= 'Z')
            draw_glyph(cx, y, font_AZ[*s - 'A'], color, scale);
        else if(*s >= '0' && *s <= '9')
            draw_glyph(cx, y, font_09[*s - '0'], color, scale);
        else if(*s == '-')
            draw_glyph(cx, y, glyph_minus, color, scale);
        else if(*s == '+')
            draw_glyph(cx, y, glyph_plus, color, scale);
        else if(*s == '/')
            draw_glyph(cx, y, glyph_slash, color, scale);
        else if(*s == '\'')
            draw_glyph(cx, y, glyph_apostrophe, color, scale);
        else if(*s == '.')
            draw_glyph(cx, y, glyph_period, color, scale);
        else if(*s == ',')
            draw_glyph(cx, y, glyph_comma, color, scale);
        else if(*s == '?')
            draw_glyph(cx, y, glyph_question, color, scale);
        else if(*s == '!')
            draw_glyph(cx, y, glyph_exclaim, color, scale);
        cx += px;
    }
}

static int text_width_s(const char *s, int scale) {
    int n = 0;
    for(; *s; s++) n++;
    return n * CHAR_CELL(scale);
}

static void draw_text_center_s(const char *s, int cx, int y, u16 color, int scale) {
    draw_text_s(s, cx - text_width_s(s, scale) / 2, y, color, scale);
}

static int word_len(const char *s) {
    int n = 0;
    while(s[n] && s[n] != ' ')
        n++;
    return n;
}

/* Word-wraps s (space-separated, uppercase-and-punctuation-free like
   every TALK string below) into lines of at most max_chars columns,
   greedily packing words, and draws each line left-aligned at x
   starting at y with line_h pixels between line tops. Used for the
   dialogue box, whose longest ported line (data.TALK.shelf's second
   beat) wraps to exactly 3 lines -- the box is sized for that. */
#define WRAP_BUF_MAX 40
static void draw_wrapped(const char *s, int x, int y, u16 color, int scale,
                          int max_chars, int line_h) {
    char buf[WRAP_BUF_MAX + 1];
    int buf_len = 0;
    int line = 0;
    const char *p = s;

    for(;;) {
        int wlen = word_len(p);
        int need = wlen + (buf_len > 0 ? 1 : 0);

        if(buf_len > 0 && buf_len + need > max_chars) {
            buf[buf_len] = 0;
            draw_text_s(buf, x, y + line * line_h, color, scale);
            line++;
            buf_len = 0;
        }

        if(buf_len > 0)
            buf[buf_len++] = ' ';
        {
            int i;
            for(i = 0; i < wlen && buf_len < WRAP_BUF_MAX; i++)
                buf[buf_len++] = p[i];
        }

        p += wlen;
        if(*p != ' ')
            break;
        p++;
    }

    buf[buf_len] = 0;
    draw_text_s(buf, x, y + line * line_h, color, scale);
}

/* ----------------------------------------------------------------------
 * Tiny manual string building for the HUD/bag/party rows below (no
 * libc here -- nostdlib/ffreestanding). s_cat/s_cat_uint append to a
 * caller-owned buffer and return the new length; callers chain them
 * to build one row's text before a single draw_text_s call.
 * ---------------------------------------------------------------------- */
static int s_cat(char *dst, int len, const char *src) {
    while(*src)
        dst[len++] = *src++;
    return len;
}

static int s_cat_uint(char *dst, int len, int v) {
    char tmp[6];
    int n = 0;
    if(v == 0) {
        dst[len++] = '0';
        return len;
    }
    while(v > 0 && n < 6) {
        tmp[n++] = (char)('0' + (v % 10));
        v /= 10;
    }
    while(n > 0)
        dst[len++] = tmp[--n];
    return len;
}

#define TITLE_SCALE 3
#define DIALOGUE_SCALE 1

static void draw_press_start(int cur, int has_save) {
    vram_clear();
    draw_text_center_s("CRYMON", SCREEN_W / 2, 48, 0xFFFF, 2);
    draw_text_center_s(cur == 0 ? "> CONTINUE" : "CONTINUE", SCREEN_W / 2, 120,
                        has_save ? (cur == 0 ? rgb565(90, 122, 82) : rgb565(197, 206, 198))
                                 : rgb565(80, 80, 72), 1);
    draw_text_center_s(cur == 1 ? "> NEW GAME" : "NEW GAME", SCREEN_W / 2, 140,
                        cur == 1 ? rgb565(90, 122, 82) : rgb565(197, 206, 198), 1);
    draw_text_center_s("A CONFIRM", SCREEN_W / 2, SCREEN_H - 28,
                        rgb565(90, 122, 82), 1);
}

/* ----------------------------------------------------------------------
 * Minimal Maple bus controller driver (port A / unit 0 only). Same
 * derivation as hello-world-dreamcast/src/hello.c -- see that file for
 * the full explanation of the register layout and packet format,
 * checked against KallistiOS's own Maple driver source.
 * ---------------------------------------------------------------------- */
#define MAPLE_BASE      0xa05f6c00u
#define MAPLE_DMA_ADDR  (*(volatile u32 *)(MAPLE_BASE + 0x04))
#define MAPLE_DMA_TSEL  (*(volatile u32 *)(MAPLE_BASE + 0x10))
#define MAPLE_ENABLE    (*(volatile u32 *)(MAPLE_BASE + 0x14))
#define MAPLE_STATE     (*(volatile u32 *)(MAPLE_BASE + 0x18))
#define MAPLE_SPEED     (*(volatile u32 *)(MAPLE_BASE + 0x80))
#define MAPLE_DMA_PROT  (*(volatile u32 *)(MAPLE_BASE + 0x8c))

#define MAPLE_COMMAND_GETCOND   9
#define MAPLE_RESPONSE_DATATRF  8
#define MAPLE_FUNC_CONTROLLER   0x01000000u

#define CONT_C            (1u << 0)
#define CONT_B            (1u << 1)
#define CONT_A            (1u << 2)
#define CONT_START        (1u << 3)
#define CONT_DPAD_UP      (1u << 4)
#define CONT_DPAD_DOWN    (1u << 5)
#define CONT_DPAD_LEFT    (1u << 6)
#define CONT_DPAD_RIGHT   (1u << 7)
#define CONT_Z            (1u << 8)
#define CONT_Y            (1u << 9)
#define CONT_X            (1u << 10)

static u32 maple_cmd_buf[8]  __attribute__((aligned(32)));
static u32 maple_resp_buf[64] __attribute__((aligned(32)));

#define P2(p)   ((volatile u32 *)(((u32)(p)) | 0x20000000u))
#define PHYS(p) (((u32)(p)) & 0x1fffffffu)

static void maple_init(void) {
    MAPLE_DMA_PROT = 0x6155404fu;
    MAPLE_DMA_TSEL = 0;
    MAPLE_SPEED = 0x0000u | (50000u << 16);
    MAPLE_ENABLE = 1;
}

static u16 maple_poll_buttons(void) {
    volatile u32 *cmd  = P2(maple_cmd_buf);
    volatile u32 *resp = P2(maple_resp_buf);
    u32 timeout;

    cmd[0] = 1u | (0u << 16) | 0x80000000u;
    cmd[1] = PHYS(maple_resp_buf);
    cmd[2] = MAPLE_COMMAND_GETCOND | (0x20u << 8) | (0u << 16) | (1u << 24);
    cmd[3] = MAPLE_FUNC_CONTROLLER;

    MAPLE_DMA_ADDR = PHYS(maple_cmd_buf);
    MAPLE_STATE = 1;

    /* A real GetCondition transfer completes in well under a millisecond;
       this spin only ever runs its full course when there's no
       controller to answer (or a genuine bus stall). 2,000,000 iterations
       of a volatile-register poll costs tens of milliseconds at 200MHz --
       multiple whole frames -- and this function runs once every frame,
       so a disconnected controller used to stall the game every single
       frame. 100,000 is still ~50x the margin a real transfer needs. */
    for(timeout = 0; timeout < 100000u; timeout++) {
        if(MAPLE_STATE == 0)
            break;
    }
    if(MAPLE_STATE != 0)
        return 0xffff;

    if((resp[0] & 0xffu) != MAPLE_RESPONSE_DATATRF)
        return 0xffff;
    if(resp[1] != MAPLE_FUNC_CONTROLLER)
        return 0xffff;

    return (u16)(resp[2] & 0xffffu);
}

static int pressed(u16 raw, u16 mask) {
    return (raw & mask) == 0;
}

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

#include "content_maps.inc"
#include "content_logic.inc"

/* Display-name override (Leg 2.7.5). Defaults to MAX; father revival
   swaps in LOGIC_REP_KIND_NAME. Precedence matches web's
   playerDisplayName() exactly: titleSlayer > titleTamer > revived
   (kindName) > "MAX". Call whenever any of the three inputs changes
   (title_slayer/title_tamer flip at the heavenfallGrave win/capture
   branches, revived flips at the resurrection choice) and once after
   a save loads, so a reload doesn't silently drop a title. */
static const char *g_player_name = "MAX";
static int g_player_renamed = 0;
static void apply_player_name(int revived, int slayer, int tamer) {
    g_player_renamed = (revived || slayer || tamer) ? 1 : 0;
    if(slayer) g_player_name = "HEAVEN SLAYER";
    else if(tamer) g_player_name = "HEAVEN TAMER";
    else if(revived) g_player_name = LOGIC_REP_KIND_NAME;
    else g_player_name = "MAX";
}

#define FADE_NONE 0
#define FADE_OUT  1
#define FADE_HOLD 2
#define FADE_IN   3

/* Brightness for the current phase, 0..FADE_STEPS. Mirrors the web's
   fadeAlpha(): out ramps up across its own frame budget, hold sits fully
   black, in ramps back down. Phase durations come from content/logic.json
   (LOGIC_FADE_*_FRAMES) and are deliberately independent of FADE_STEPS, so
   retiming a fade in JSON no longer silently does nothing here. */
static int fade_level(int phase, int timer) {
    int lvl;
    if(phase == FADE_OUT) {
        if(LOGIC_FADE_OUT_FRAMES <= 0) return FADE_STEPS;
        lvl = timer * FADE_STEPS / LOGIC_FADE_OUT_FRAMES;
        return lvl > FADE_STEPS ? FADE_STEPS : lvl;
    }
    if(phase == FADE_HOLD)
        return FADE_STEPS;
    if(phase == FADE_IN) {
        if(LOGIC_FADE_IN_FRAMES <= 0) return 0;
        lvl = FADE_STEPS - timer * FADE_STEPS / LOGIC_FADE_IN_FRAMES;
        return lvl < 0 ? 0 : lvl;
    }
    return 0;
}

static int tile_is_solid(char ch) {
    const char *p;
    for(p = SOLID_TILES; *p; p++)
        if(*p == ch)
            return 1;
    return 0;
}

/* blocked()'s GROVE gate-row addition vs crymon.c (see data.lua's
   GROVE comment): the mid-map door row is walkable per SOLID_SET
   (data.isSolidTile has no 'D'), but state.lua blocks it in the
   collision check itself until Cathleen is caught -- now that
   Cathleen is a real, catchable GROVE fight in this port, this gate
   is ported too instead of staying an open door. The story now has
   her relinquish the door's key on any win against her, capture or
   not (both call sites below OR beat_cathleen into the cath_caught
   param), so the 3rd param here still just means "the key is hers to
   give" regardless of which flag actually earned it. */
static int tile_blocked(int map_id, char ch, int cath_caught, int beat_calder, int beat_shin, int cage_open) {
    if(ch == 'k' && cage_open) return 0;
    if(tile_is_solid(ch)) return 1;
    if(map_id == MAP_GROVE && ch == 'D' && !cath_caught) return 1;
    return 0;
}

/* Out-of-bounds tiles read as '#' (solid), matching data.tileAt. */
static char tile_at(int map_id, int col, int row) {
    const Map *m = &MAPS[map_id];
    if(col < 0 || col >= m->cols || row < 0 || row >= m->rows_n)
        return '#';
    return m->rows[row][col];
}

/* First occurrence of mark, row-major, matching data.spawnOf's
   row:find() scan order. Every call site below only asks for marks
   known to exist on that map (checked against the grids above), so
   the not-found fallback is never actually hit in practice. */
static void find_mark(int map_id, char mark, int *out_col, int *out_row) {
    const Map *m = &MAPS[map_id];
    int row, col;
    for(row = 0; row < m->rows_n; row++) {
        for(col = 0; col < m->cols; col++) {
            if(m->rows[row][col] == mark) {
                *out_col = col;
                *out_row = row;
                return;
            }
        }
    }
    *out_col = 2;
    *out_row = 2;
}

static void mark_center(int map_id, char mark, int *out_x, int *out_y) {
    int col, row;
    find_mark(map_id, mark, &col, &row);
    *out_x = col * TILE + TILE / 2;
    *out_y = row * TILE + TILE / 2;
}

/* draw.lua's paintTile, verbatim palette (including its two-rect
   detail tiles: grass speckle '.', tree 'T', forest-floor '#', flower
   '*'). Tile chars not explicitly listed (every NPC/prop mark, plus
   VELD/FOREST/GROVE decoration letters not ported to real props
   here) fall through to paintTile's own grass-green default. */
static void draw_tile(int map_id, char ch, int dx, int dy) {
    int t = TILE;

    switch(ch) {
        case 'H':
            fill_rect(dx, dy, t, t, rgb565(42, 30, 22));
            return;
        case 'r':
            /* Terracotta eaves — shingle rows + dark drip edge. */
            fill_rect(dx, dy, t, t, rgb565(138, 48, 24));
            fill_rect(dx, dy, t, 2, rgb565(196, 104, 64));
            fill_rect(dx, dy + 6, t, 1, rgb565(74, 28, 18));
            fill_rect(dx, dy + 12, t, 1, rgb565(74, 28, 18));
            fill_rect(dx + 4, dy + 2, 1, 4, rgb565(74, 28, 18));
            fill_rect(dx + 12, dy + 8, 1, 4, rgb565(74, 28, 18));
            fill_rect(dx, dy + t - 2, t, 2, rgb565(58, 20, 14));
            return;
        case 'R':
            /* Ridge cap on Max's house (the row above the eaves). */
            fill_rect(dx, dy, t, t, rgb565(163, 74, 50));
            fill_rect(dx, dy, t, 3, rgb565(210, 136, 88));
            fill_rect(dx, dy + 8, t, 1, rgb565(90, 36, 24));
            fill_rect(dx, dy + 14, t, 1, rgb565(90, 36, 24));
            return;
        case '%':
        case 'g':
        case 'k':
            fill_rect(dx, dy, t, t, rgb565(74, 64, 48));
            fill_rect(dx + 4, dy, 3, t, rgb565(26, 24, 20));
            fill_rect(dx + 13, dy, 3, t, rgb565(42, 36, 28));
            if(ch == 'k') {
                fill_rect(dx + 7, dy + 8, 8, 8, rgb565(138, 115, 72));
                fill_rect(dx + 10, dy + 11, 3, 3, rgb565(42, 28, 20));
            }
            return;
        case 'F':
            if(map_id != MAP_HOUSE) {
                fill_rect(dx, dy, t, t, rgb565(107, 90, 58));
                return;
            }
        case 'P':
            fill_rect(dx, dy, t, t, rgb565(106, 82, 56));
            return;
        case 'D':
            fill_rect(dx, dy, t, t, rgb565(26, 18, 12));
            return;
        case 'B':
        case 'U':
        case 'C':
        case 'S':
            fill_rect(dx, dy, t, t, rgb565(106, 82, 56));
            return;
        case '.':
            fill_rect(dx, dy, t, t, rgb565(61, 90, 56));
            fill_rect(dx + 3, dy + 4, 1, 1, rgb565(90, 122, 82));
            return;
        case 'T':
            fill_rect(dx, dy, t, t, rgb565(47, 74, 44));
            fill_rect(dx + 4, dy + 3, 3, 15, rgb565(106, 138, 58));
            fill_rect(dx + 10, dy + 1, 3, 16, rgb565(90, 122, 82));
            return;
        case '=':
        case 'Z':
        case 'Y':
        case '3':
        case 'O':
        case '8':
        case '9':
            fill_rect(dx, dy, t, t, rgb565(107, 90, 58));
            return;
        case ',':
            fill_rect(dx, dy, t, t, rgb565(90, 74, 58));
            return;
        case '#':
            fill_rect(dx, dy, t, t, rgb565(28, 36, 24));
            fill_rect(dx + 3, dy + 1, 15, 11, rgb565(61, 90, 56));
            return;
        case 'W':
            fill_rect(dx, dy, t, t, rgb565(42, 58, 68));
            return;
        case '^':
            fill_rect(dx, dy, t, t, rgb565(74, 64, 48));
            return;
        case 'N':
        case 'E':
            fill_rect(dx, dy, t, t, rgb565(90, 70, 48));
            return;
        case '*':
            fill_rect(dx, dy, t, t, rgb565(61, 90, 56));
            fill_rect(dx + 8, dy + 8, 4, 4, rgb565(180, 60, 80));
            return;
        default:
            fill_rect(dx, dy, t, t, rgb565(61, 90, 56));
            return;
    }
}

/* Keeps the player roughly centered, clamped to the map's edges; a
   map no bigger than the screen (HOUSE) instead gets a fixed,
   centered offset (possibly negative), which is what actually
   produces the letterboxed look the old HOUSE-only code hardcoded --
   a tile drawn at col*TILE - cam_x still lands in the right place
   when cam_x is negative. */
/* Unclamped (matches engine.ts's cam()): always centers exactly on the
   player, even past a map edge -- the tile-draw loop already skips
   anything outside the grid, so this just reveals plain background
   there. Clamping to the map bounds used to push small/near-edge maps'
   top rows up under draw_hud()'s fixed top-left box whenever the
   player was anywhere in the map's top SCREEN_H/2 (120px). Free camera
   panning keeps the player centered instead, so nothing near an edge
   sits under the HUD. */
static void compute_camera(int map_id, int px, int py, int *cam_x, int *cam_y) {
    (void)map_id;
    *cam_x = px - SCREEN_W / 2;
    *cam_y = py - SCREEN_H / 2;
}
/* Draws only the tile range that can be visible at this camera
   offset -- VELD alone is 30x22 = 660 tiles, too many to redraw
   in full every frame at 20px/tile through put_pixel. */
static void draw_map(int map_id, int cam_x, int cam_y) {
    const Map *m = &MAPS[map_id];
    int col0 = cam_x / TILE;
    int col1 = (cam_x + SCREEN_W) / TILE + 1;
    int row0 = cam_y / TILE;
    int row1 = (cam_y + SCREEN_H) / TILE + 1;
    int row, col;

    if(col0 < 0) col0 = 0;
    if(row0 < 0) row0 = 0;
    if(col1 > m->cols) col1 = m->cols;
    if(row1 > m->rows_n) row1 = m->rows_n;

    /* Letterboxed maps (HOUSE, and CAMP vertically) leave a border the
       tile loop below never touches, so it needs clearing or it'd show
       whatever was drawn there previously (e.g. the title screen text).
       Every other outdoor map is at least as big as the viewport in
       both axes, so the tile loop below already overwrites every
       screen pixel -- clearing first was pure wasted work there: a
       full 320x240 scalar fill, every single frame, unconditionally,
       immediately drawn over. That's exactly the kind of invisible
       per-frame cost that reads as "slow for no reason" (nothing on
       screen explains it, since the clear never stays visible).
       Decided from this frame's actual drawn region rather than a
       hardcoded map list, so it still clears correctly if the camera
       ever clamps short of covering the screen (letterboxed maps, or
       any edge case upstream). */
    if(col0 * TILE - cam_x > 0 || col1 * TILE - cam_x < SCREEN_W ||
       row0 * TILE - cam_y > 0 || row1 * TILE - cam_y < SCREEN_H) {
        vram_clear();
    }

    for(row = row0; row < row1; row++)
        for(col = col0; col < col1; col++)
            draw_tile(map_id, m->rows[row][col], col * TILE - cam_x, row * TILE - cam_y);
}

/* Props are center-anchored on their mark's tile center, matching the
   flat-rect placeholders this replaced in an earlier step. Sizes come
   from sprites.h (the real art's own dimensions, downscaled by
   gen_sprites.py -- not the original 32px-tile-space sizes from
   render.lua, which didn't match the actual art's proportions
   anyway). HOUSE-only: B/U/S/C don't appear on any other map. */
static void draw_prop(char mark, const u16 *px, int w, int h, int cam_x, int cam_y) {
    int cx, cy;
    mark_center(MAP_HOUSE, mark, &cx, &cy);
    blit_sprite(px, w, h, cx - cam_x - w / 2, cy - cam_y - h / 2);
}

static void draw_props(int map_id, int cam_x, int cam_y, int looted_crate) {
    if(map_id != MAP_HOUSE)
        return;
    draw_prop('B', prop_bed_father, PROP_BED_FATHER_W, PROP_BED_FATHER_H, cam_x, cam_y);
    draw_prop('U', prop_bed_empty, PROP_BED_EMPTY_W, PROP_BED_EMPTY_H, cam_x, cam_y);
    draw_prop('S', prop_shelf, PROP_SHELF_W, PROP_SHELF_H, cam_x, cam_y);
    if(!looted_crate)
        draw_prop('C', prop_crate, PROP_CRATE_W, PROP_CRATE_H, cam_x, cam_y);
}

/* World NPCs: bottom-anchored on their mark's tile like the player
   (feet at the tile center), matching render.lua's actor placement.
   All stationary single-frame sprites -- see the world-NPC section
   comment further down for why (no walk/idle animation ported for
   any of them, unlike the player). */
/* A patrolling/chasing FOREST soldier. File-scope (not just a local
   inside main()) since draw_npcs below needs the type too. Matches
   engine.ts's soldiers[] entries (id/name/species/level stay in the
   const SoldierDef table further down; this is just the live
   movement state). */
typedef struct {
    float x, y;
    int dir, anim;
    int chase;
    int axis;           /* 0 = patrols x, 1 = patrols y, 2 = stationary */
    float minv, maxv;
    int sign;
} Soldier;

/* Every world actor (the 8 stationary NPCs, Mason/Anne/soldiers, and
   the player) is bottom-center anchored at a "feet" point (cx, cy) in
   map/world pixel space -- draw order used to just be "all the NPCs,
   then the player on top, always", so the player would occlude an
   NPC standing further down the screen than them (in front, by the
   usual 2D convention) instead of the other way around. Now every
   sprite due to be drawn this frame is collected into this list
   first, instead of blitting immediately, so they can all be sorted
   by cy and drawn back-to-front (lower feet == closer to the camera
   == drawn last == on top) regardless of which is the player and
   which is an NPC. */
typedef struct {
    const u16 *px;
    int w, h;
    int cx, cy;
    int scale;
} WorldSprite;

#define MAX_WORLD_SPRITES 12

static void ws_push(WorldSprite *list, int *n, const u16 *px, int w, int h, int cx, int cy) {
    if(*n >= MAX_WORLD_SPRITES) return;
    list[*n].px = px;
    list[*n].w = w;
    list[*n].h = h;
    list[*n].cx = cx;
    list[*n].cy = cy;
    list[*n].scale = 1;
    (*n)++;
}

static int npc_exec_bit(int map_id, char mark);
static void ws_push_mark(WorldSprite *list, int *n, int map_id, char mark, const u16 *px, int w, int h) {
    int cx, cy, ebit;
    ebit = npc_exec_bit(map_id, mark);
    if(ebit >= 0 && (g_executed_mask & (1u << ebit))) return; /* executed: gone from world */
    mark_center(map_id, mark, &cx, &cy);
    ws_push(list, n, px, w, h, cx, cy);
}

/* Idle-animated variant of the above, for the 8 stationary NPCs that
   still cycle 4 standing frames in the reference (drawWorld()'s
   `Math.floor(this.clock * 4) % 4 + 1`, `* 3` for Shinigami --
   frames_per_step converts that fps into "how many 60Hz vblank
   frames this idle frame holds", 15 for 4fps, 20 for 3fps). */
static void ws_push_mark_idle(WorldSprite *list, int *n, int map_id, char mark,
                               const u16 *const frames[4], u32 frame_count,
                               int frames_per_step, int w, int h) {
    int f = (int)((frame_count / (u32)frames_per_step) % 4u);
    ws_push_mark(list, n, map_id, mark, frames[f], w, h);
}

/* Same as ws_push_mark_idle, but nudged by (off_x, off_y) pixels --
   for a gate-blocking NPC (Calder, the Priestess) that steps aside
   once its passIf condition is met instead of just stopping being
   solid at the same spot (matches engine.ts's equivalent offset in
   the NPC draw loop). Still honors g_executed_mask like the plain
   variant. */
static void ws_push_mark_idle_off(WorldSprite *list, int *n, int map_id, char mark,
                                   const u16 *const frames[4], u32 frame_count,
                                   int frames_per_step, int w, int h,
                                   int off_x, int off_y) {
    int f = (int)((frame_count / (u32)frames_per_step) % 4u);
    int cx, cy, ebit;
    ebit = npc_exec_bit(map_id, mark);
    if(ebit >= 0 && (g_executed_mask & (1u << ebit))) return;
    mark_center(map_id, mark, &cx, &cy);
    ws_push(list, n, frames[f], w, h, cx + off_x, cy + off_y);
}

/* dir/frame lookup tables for the 3 walking actors (Mason, Anne, the
   FOREST soldiers all share one sprite set), matching
   gen_sprites.py's PLAYER_DIRS order: 0=down,1=up,2=left,3=right. */
static const u16 *const MASON_FRAMES[4][4] = {
    { npc_mason_down_1,  npc_mason_down_2,  npc_mason_down_3,  npc_mason_down_4 },
    { npc_mason_up_1,    npc_mason_up_2,    npc_mason_up_3,    npc_mason_up_4 },
    { npc_mason_left_1,  npc_mason_left_2,  npc_mason_left_3,  npc_mason_left_4 },
    { npc_mason_right_1, npc_mason_right_2, npc_mason_right_3, npc_mason_right_4 },
};
static const u16 *const ANNE_FRAMES[4][4] = {
    { npc_anne_down_1,  npc_anne_down_2,  npc_anne_down_3,  npc_anne_down_4 },
    { npc_anne_up_1,    npc_anne_up_2,    npc_anne_up_3,    npc_anne_up_4 },
    { npc_anne_left_1,  npc_anne_left_2,  npc_anne_left_3,  npc_anne_left_4 },
    { npc_anne_right_1, npc_anne_right_2, npc_anne_right_3, npc_anne_right_4 },
};
static const u16 *const SOLDIER_FRAMES[4][4] = {
    { npc_soldier_down_1,  npc_soldier_down_2,  npc_soldier_down_3,  npc_soldier_down_4 },
    { npc_soldier_up_1,    npc_soldier_up_2,    npc_soldier_up_3,    npc_soldier_up_4 },
    { npc_soldier_left_1,  npc_soldier_left_2,  npc_soldier_left_3,  npc_soldier_left_4 },
    { npc_soldier_right_1, npc_soldier_right_2, npc_soldier_right_3, npc_soldier_right_4 },
};

static void ws_push_walker(WorldSprite *list, int *n, const u16 *const frames[4][4],
                            float x, float y, int dir, int frame) {
    ws_push(list, n, frames[dir & 3][frame & 3], NPC_SPRITE_W, NPC_SPRITE_H, (int)x, (int)y);
}

static const u16 *const WREN_FRAMES[4]   = { npc_wren_1, npc_wren_2, npc_wren_3, npc_wren_4 };
static const u16 *const MAE_FRAMES[4]    = { npc_mae_1, npc_mae_2, npc_mae_3, npc_mae_4 };
static const u16 *const IVO_FRAMES[4]    = { npc_ivo_1, npc_ivo_2, npc_ivo_3, npc_ivo_4 };
static const u16 *const NELL_FRAMES[4]   = { npc_nell_1, npc_nell_2, npc_nell_3, npc_nell_4 };
static const u16 *const PIKE_FRAMES[4]   = { npc_pike_1, npc_pike_2, npc_pike_3, npc_pike_4 };
static const u16 *const BRAM_FRAMES[4]   = { npc_bram_1, npc_bram_2, npc_bram_3, npc_bram_4 };
static const u16 *const CALDER_FRAMES[4] = { npc_calder_1, npc_calder_2, npc_calder_3, npc_calder_4 };
static const u16 *const SHINIGAMI_FRAMES[4] = { npc_shinigami_1, npc_shinigami_2, npc_shinigami_3, npc_shinigami_4 };
static const u16 *const OREN_FRAMES[4]  = { npc_oren_1, npc_oren_2, npc_oren_3, npc_oren_4 };
static const u16 *const TESSA_FRAMES[4] = { npc_tessa_1, npc_tessa_2, npc_tessa_3, npc_tessa_4 };
static const u16 *const BIRCH_FRAMES[4] = { npc_birch_1, npc_birch_2, npc_birch_3, npc_birch_4 };
static const u16 *const SABLE_FRAMES[4] = { npc_sable_1, npc_sable_2, npc_sable_3, npc_sable_4 };
static const u16 *const CROSS_FRAMES[4]      = { npc_cross_1, npc_cross_2, npc_cross_3, npc_cross_4 };
static const u16 *const COMMANDER_FRAMES[4]  = { npc_commander_1, npc_commander_2, npc_commander_3, npc_commander_4 };
static const u16 *const CONSCRIPT_FRAMES[4]  = { npc_conscript_1, npc_conscript_2, npc_conscript_3, npc_conscript_4 };
static const u16 *const ENFORCER_FRAMES[4]   = { npc_enforcer_1, npc_enforcer_2, npc_enforcer_3, npc_enforcer_4 };
static const u16 *const SENTRY_FRAMES[4]     = { npc_sentry_1, npc_sentry_2, npc_sentry_3, npc_sentry_4 };
static const u16 *const RANGER_FRAMES[4]     = { npc_ranger_1, npc_ranger_2, npc_ranger_3, npc_ranger_4 };
static const u16 *const SCOUT_FRAMES[4]      = { npc_scout_1, npc_scout_2, npc_scout_3, npc_scout_4 };
static const u16 *const KEEPER_FRAMES[4]     = { npc_keeper_1, npc_keeper_2, npc_keeper_3, npc_keeper_4 };
static const u16 *const WARDEN_FRAMES[4]     = { npc_warden_1, npc_warden_2, npc_warden_3, npc_warden_4 };
static const u16 *const HEAVENFALLPRIESTESS_FRAMES[4] = { npc_heavenfallPriestess_1, npc_heavenfallPriestess_2, npc_heavenfallPriestess_3, npc_heavenfallPriestess_4 };
static const u16 *const SHINIGAMIBOULDER_FRAMES[4] = { npc_shinigamiBoulder_1, npc_shinigamiBoulder_2, npc_shinigamiBoulder_3, npc_shinigamiBoulder_4 };
/* npc_father_1..4 (Father's walk frames) aren't used -- he's bedridden
   and only ever appears via his portrait (SPK_FATHER), never placed as
   a WorldSprite. */

/* Insertion sort by cy (small n, not worth anything fancier) then
   blit back-to-front: lower feet (larger cy) draw last, i.e. on top,
   matching the usual 2D convention that standing further down the
   screen means standing closer to the camera. */
static void ws_sort_and_draw(WorldSprite *list, int n, int cam_x, int cam_y) {
    int i, j;
    for(i = 1; i < n; i++) {
        WorldSprite key = list[i];
        j = i - 1;
        while(j >= 0 && list[j].cy > key.cy) {
            list[j + 1] = list[j];
            j--;
        }
        list[j + 1] = key;
    }
    for(i = 0; i < n; i++) {
        const WorldSprite *s = &list[i];
        int sc = s->scale > 1 ? s->scale : 1;
        int dw = s->w * sc, dh = s->h * sc;
        int dx = s->cx - cam_x - dw / 2;
        int dy = s->cy - cam_y - dh;
        if(sc == 2) blit_sprite_2x(s->px, s->w, s->h, dx, dy);
        else blit_sprite(s->px, s->w, s->h, dx, dy);
    }
}

/* Player sprite, bottom-center anchored at (cx, cy) same as every
   other world actor above -- pushed into the same WorldSprite list as
   the NPCs now (see main()'s draw dispatch) instead of always being
   blit last/on top, so the depth sort in ws_sort_and_draw() applies
   to the player too. dir matches the sprite arrays below: 0=down,
   1=up,2=left,3=right. Walk-cycle animation matches state.lua's
   G.panim/G.pframe: 4 frames per direction, stepping to the next one
   every 10 frames while moving (dt*6 per frame at our fixed ~60fps
   vblank rate takes 10 frames to cross 1.0, same as the reference),
   frozen on frame 0 while standing still. main() drives anim_frame
   the same way G.pframe is driven. */
static const u16 *const MAX_FRAMES[4][4] = {
    { max_down_1,  max_down_2,  max_down_3,  max_down_4 },
    { max_up_1,    max_up_2,    max_up_3,    max_up_4 },
    { max_left_1,  max_left_2,  max_left_3,  max_left_4 },
    { max_right_1, max_right_2, max_right_3, max_right_4 },
};

/* ----------------------------------------------------------------------
 * Interact dialogue: full multi-beat sequences from data.TALK.father /
 * fatherAfter / bed / shelf / shelfEmpty / crate / crateEmpty (also
 * cross-checked against the canonical src/game/data.ts, which is
 * where every TALK_* array's actual text below was pulled from --
 * verbatim except upper-cased, our font having no lowercase set).
 * Each sequence is shown one beat per A-press (matching sayn()'s
 * one-beat-per-advance in the reference), word-wrapped into the
 * dialogue box.
 *
 * Each beat also carries a speaker id (data.ts's own beat.speaker,
 * "none" mapped to SPK_NONE), ported here for the first time: the
 * reference shows a real character portrait next to the text whenever
 * speaker isn't "none" (drawWorld()'s `drawSprite('port-${speaker}', ...)`).
 * SPEAKER_PORTRAIT below is the id -> sprite lookup draw_dialogue_box
 * uses; SPK_NONE (soldiers' anonymous lines, plain narration beats)
 * draws no portrait, same as the reference. */
typedef struct {
    const char *text;
    unsigned char speaker;
} TalkBeat;

#define SPK_NONE      0
#define SPK_MAX       1
#define SPK_ANNE      2
#define SPK_MASON     3
#define SPK_WREN      4
#define SPK_MAE       5
#define SPK_IVO       6
#define SPK_NELL      7
#define SPK_PIKE      8
#define SPK_CALDER    9
#define SPK_BRAM      10
#define SPK_CATHLEEN  11
#define SPK_SHINIGAMI 12
#define SPK_OREN      13
#define SPK_TESSA     14
#define SPK_BIRCH     15
#define SPK_SABLE     16
#define SPK_CROSS     17
#define SPK_COMMANDER 18
#define SPK_CONSCRIPT 19
#define SPK_ENFORCER  20
#define SPK_SENTRY    21
#define SPK_FATHER    22
#define SPK_HEAVENFALL 23
/* 24-36 are unused speaker ids on the web side (e.g. "system", id 36 --
   narration/system-voiced lines with no portrait) that were never given
   a Dreamcast portrait slot; the gap is intentional, not a bug, filled
   with { 0, 0, 0 } (no portrait) below. SPK_HEAVENFALLPRIESTESS must
   stay exactly 37 -- it has to match content_talk.inc's baked speaker
   id (tools/bake_content.py's SPEAKER dict), the same requirement
   every other SPK_* here already has, just with a real gap before it
   instead of a contiguous run. */
#define SPK_HEAVENFALLPRIESTESS 37
#define SPK_COUNT     38

/* Each portrait keeps its source art's own aspect ratio (gen_sprites.py
   scales every one by the same factor on both axes to fill as much of
   PORTRAIT_BOX_W x PORTRAIT_BOX_H as possible -- "contain" scaling,
   no cropping or stretching), so unlike every other sprite table in
   this file they're not all the same size: this carries each one's
   own w/h alongside its pixels for draw_dialogue_box to center. */
typedef struct {
    const u16 *px;
    int w, h;
} Portrait;

static const Portrait SPEAKER_PORTRAIT[SPK_COUNT] = {
    { 0, 0, 0 }, /* SPK_NONE */
    { port_max,       PORT_MAX_W,       PORT_MAX_H },
    { port_anne,      PORT_ANNE_W,      PORT_ANNE_H },
    { port_mason,     PORT_MASON_W,     PORT_MASON_H },
    { port_wren,      PORT_WREN_W,      PORT_WREN_H },
    { port_mae,       PORT_MAE_W,       PORT_MAE_H },
    { port_ivo,       PORT_IVO_W,       PORT_IVO_H },
    { port_nell,      PORT_NELL_W,      PORT_NELL_H },
    { port_pike,      PORT_PIKE_W,      PORT_PIKE_H },
    { port_calder,    PORT_CALDER_W,    PORT_CALDER_H },
    { port_bram,      PORT_BRAM_W,      PORT_BRAM_H },
    { port_cathleen,  PORT_CATHLEEN_W,  PORT_CATHLEEN_H },
    { port_shinigami, PORT_SHINIGAMI_W, PORT_SHINIGAMI_H },
    { port_oren,      PORT_OREN_W,      PORT_OREN_H },
    { port_tessa,     PORT_TESSA_W,     PORT_TESSA_H },
    { port_birch,     PORT_BIRCH_W,     PORT_BIRCH_H },
    { port_sable,     PORT_SABLE_W,     PORT_SABLE_H },
    { port_cross,     PORT_CROSS_W,     PORT_CROSS_H },
    { port_commander, PORT_COMMANDER_W, PORT_COMMANDER_H },
    { port_conscript, PORT_CONSCRIPT_W, PORT_CONSCRIPT_H },
    { port_enforcer,  PORT_ENFORCER_W,  PORT_ENFORCER_H },
    { port_sentry,    PORT_SENTRY_W,    PORT_SENTRY_H },
    { port_father,    PORT_FATHER_W,    PORT_FATHER_H },
    { port_heavenfall,PORT_HEAVENFALL_W,PORT_HEAVENFALL_H },
    { 0, 0, 0 }, /* 24 */
    { 0, 0, 0 }, /* 25 */
    { 0, 0, 0 }, /* 26 */
    { 0, 0, 0 }, /* 27 */
    { 0, 0, 0 }, /* 28 */
    { 0, 0, 0 }, /* 29 */
    { 0, 0, 0 }, /* 30 */
    { 0, 0, 0 }, /* 31 */
    { 0, 0, 0 }, /* 32 */
    { 0, 0, 0 }, /* 33 */
    { 0, 0, 0 }, /* 34 */
    { 0, 0, 0 }, /* 35 */
    { 0, 0, 0 }, /* 36 -- SPK_NONE/"system" territory, no portrait */
    { port_heavenfallPriestess, PORT_HEAVENFALLPRIESTESS_W, PORT_HEAVENFALLPRIESTESS_H }, /* 37 */
};

#include "content_talk.inc"

/* The portrait now dominates the screen instead of sitting in a small
   column: nothing else on screen matters while someone's talking
   besides their portrait and what they're saying, so it gets the
   whole width and everything between the top-left HUD (draw_hud,
   0-22ish) and the text strip at the bottom. PORTRAIT_BOX_W/H (from
   sprites.h, gen_sprites.py's own generation box) exactly fill that
   remaining area -- 24 (below the HUD) + PORTRAIT_BOX_H (176) +
   DIALOGUE_TEXT_H (40) == SCREEN_H (240) -- so there's no dead gap
   and no overlap on either side. Each portrait already comes out of
   sprites.h sized to fit inside that box without cropping or
   stretching (gen_sprites.py's own contain-scaling, preserving each
   character's real aspect ratio); this just centers whatever size
   that is. */
#define PORTRAIT_BOX_X     4
#define PORTRAIT_BOX_Y     24
#define DIALOGUE_TEXT_H    40
#define DIALOGUE_TEXT_Y    (SCREEN_H - DIALOGUE_TEXT_H)
#define DIALOGUE_MAX_CHARS ((SCREEN_W - 16) / CHAR_CELL(DIALOGUE_SCALE))
#define DIALOGUE_LINE_H    9

/* No background panel -- outlined text (draw_glyph's own 1px black
   border) reads fine directly over the world/battle scene, so the
   dialogue box is really just a portrait plus wrapped text at a fixed
   screen position now, not an actual drawn box.

   Horizontal placement now tells the two sides apart at a glance:
   Max (the player) sits flush against the box's own left edge --
   already a safe 4px in from the screen edge, PORTRAIT_BOX_X's own
   buffer, so nothing crops -- and every NPC sits flush against the
   right edge instead of the old dead-center placement. Vertical
   centering is unchanged. */
static void draw_dialogue_box(const TalkBeat *beat) {
    if(beat->speaker != SPK_NONE) {
        const Portrait *p = &SPEAKER_PORTRAIT[beat->speaker];
        int px = (beat->speaker == SPK_MAX)
                     ? PORTRAIT_BOX_X
                     : PORTRAIT_BOX_X + PORTRAIT_BOX_W - p->w;
        blit_sprite(p->px, p->w, p->h, px, PORTRAIT_BOX_Y + (PORTRAIT_BOX_H - p->h) / 2);
        if(beat->speaker == SPK_MAX && g_player_renamed)
            draw_text_s(g_player_name, 8, DIALOGUE_TEXT_Y - DIALOGUE_LINE_H,
                        rgb565(197, 206, 198), DIALOGUE_SCALE);
    }
    draw_wrapped(beat->text, 8, DIALOGUE_TEXT_Y + 8,
                 0xFFFF, DIALOGUE_SCALE,
                 DIALOGUE_MAX_CHARS, DIALOGUE_LINE_H);
}

/* HUD toast (state.lua's G.hud/note()): a small one-line banner near
   the top of the screen, distinct from the dialogue box at the bottom
   so the two are never confused even though they never actually show
   at once (say() always clears hudT, and every note() call site is
   reached from plain world state, not mid-dialogue). No background
   panel, same as the dialogue box above -- just outlined text. */
static void draw_hud_toast(const char *text) {
    draw_text_s(text, 26, 10, 0xFFFF, DIALOGUE_SCALE);
}

/* Map-name banner: replaces the old per-door TALK_*_ENTER/LEAVE
   flavor lines (do_warp() sets this instead of seq_lines now) with a
   plain text fade-in/hold/fade-out showing where the player just
   arrived, independent of the dialogue system entirely -- it needs no
   A press and never blocks movement. The fade is a straight color
   lerp from black to the text's own color and back (there's no true
   alpha layer in this RGB565 framebuffer), driven by a countdown that
   ticks every frame regardless of what else is on screen. */
#define MAP_BANNER_IN    16
#define MAP_BANNER_HOLD  70
#define MAP_BANNER_OUT   16
#define MAP_BANNER_TOTAL (MAP_BANNER_IN + MAP_BANNER_HOLD + MAP_BANNER_OUT)

static void draw_map_title(int map_id) {
    const char *name;
    int w;
    if(map_id < 0 || map_id >= MAP_N) map_id = MAP_HOUSE;
    name = MAP_DISPLAY_NAME[map_id];
    w = text_width_s(name, 2);
    draw_text_s(name, SCREEN_W - 6 - w, 4, rgb565(232, 228, 216), 2);
}

static void draw_map_banner(int map_id, int timer) {
    (void)timer;
    draw_map_title(map_id);
}

/* Small HUD in the screen's top-left corner (fixed there regardless
   of camera position), showing what interacting has granted so far
   -- there's no inventory/party HUD overlay in the reference, but
   there's also no way to see this port's bag/party menus without
   opening them, so this stays as a quick-glance confirmation. */
static void draw_hud(int got_shelf, int looted_crate, int bag_bandage, int has_scroll, int reputation) {
    int y = 2;
    {
        char rep_buf[20];
        int n = 0;
        int v = reputation;
        n = s_cat(rep_buf, 0, "REP ");
        if(v < 0) { n = s_cat(rep_buf, n, "-"); v = -v; }
        else if(v > 0) { n = s_cat(rep_buf, n, "+"); }
        n = s_cat_uint(rep_buf, n, (unsigned)v);
        rep_buf[n] = 0;
        {
            u16 col = 0xFFFF;
            if(reputation > 0) col = rgb565(80, 180, 80);
            else if(reputation < 0) col = rgb565(200, 60, 60);
            draw_text_s(rep_buf, 4, y, col, DIALOGUE_SCALE);
        }
        y += DIALOGUE_LINE_H;
    }

    if(g_player_renamed) {
        draw_text_s(g_player_name, 4, y, 0xFFFF, DIALOGUE_SCALE);
        y += DIALOGUE_LINE_H;
    }
    if(got_shelf) {
        const char *label = "QUILLPUP LV";
        draw_text_s(label, 4, y, 0xFFFF, DIALOGUE_SCALE);
        draw_glyph(4 + text_width_s(label, DIALOGUE_SCALE), y,
                   font_09[3], 0xFFFF, DIALOGUE_SCALE);
        y += DIALOGUE_LINE_H;
    }
    if(looted_crate) {
        const char *label = "BANDAGE X";
        draw_text_s(label, 4, y, 0xFFFF, DIALOGUE_SCALE);
        draw_glyph(4 + text_width_s(label, DIALOGUE_SCALE), y,
                   font_09[bag_bandage % 10], 0xFFFF, DIALOGUE_SCALE);
        y += DIALOGUE_LINE_H;
    }
    if(has_scroll)
        draw_text_s("LEGENDARY REANIMATION", 4, y, 0xFFFF, DIALOGUE_SCALE);
}

/* ----------------------------------------------------------------------
 * Species/monster data and battle math, verbatim from data.lua's
 * SPECIES table, mintMonster(), grantXp(), and captureChance(). Move
 * names are upper-cased/depunctuated for our font; multi-word names
 * keep their space ("FIRE BOLT"). Cathleen alone carries a spells[]
 * list (spells_n > 0 for no other entry below) -- SPELL_FIREBOLT/
 * ICEBEAM/LIGHTNING/MANASURGE (0-3, defined by battle_cast_spell()
 * further down) matching data.ts's own spell id order for her. Every
 * other species leaves spells_n at 0 and never touches battle_cast_spell.
 * ---------------------------------------------------------------------- */
/* Every attack (basic, special, spell, Toxic Burst, crystal secondary)
   is atkStat(str or mag) times the move's own power rating -- see
   content/logic.json's "combat" block. Agility is never an attack stat,
   only a speed one (used solely to resolve Dodge). */

typedef struct {
    const char *name, *basic, *special;
    int maxHp, str, agl, spc, spp;
    int basic_stat, special_stat;       /* ATK_STR / ATK_MAG */
    float basic_power, basic_speed;     /* 0.5-1.5, shown to the player x10 */
    float special_power, special_speed;
    int spells_n;      /* 0 for every species but Cathleen */
    int spells[4];     /* SPELL_* ids, spells_n of them valid */
    int nature;        /* index into NATURES -- a crystal belongs to the
                          species, so every one of them shares it */
    int evolves_to;    /* SPECIES index, or -1 if this form is final */
} Species;

/* Cathleen's fixed 4-spell kit. Every spell is tagged Magic (see
   content/species.json's spells[].stat), but power/speed still vary by
   spell so casting a spell goes through the exact same atkStat*power
   formula as every other move. */
typedef struct {
    int stat;
    float power, speed;
} SpellDef;

#include "content_species.inc"
#include "content_world.inc"

typedef struct {
    int species;
    int lv, xp;
    int maxHp, hp, str, agl, spc, spp, sppMax;
    int shiny; /* see mint_shiny() below */
    /* Leg 2.11: persists across battles for the player's own party (saved
       at SaveMon bytes 13-15); battle-scoped only for foes/trainer mons,
       which are freshly minted each fight anyway. */
    int status, status_turns, poison_stack;
} Monster;

/* A crystal belongs to the species, so every CryMon of a species shares it.
   Look it up rather than storing a copy on each monster. */
static int species_nature(int species) {
    if(species < 0 || species >= SPECIES_N) return 0;
    return SPECIES[species].nature;
}

static int nature_index_by_ring(int ring) {
    int i;
    for(i = 0; i < NATURE_N; i++) if(NATURES[i].ring == ring) return i;
    return 0;
}

#define UMOVE_BASIC 0
#define UMOVE_NMOVE 1
#define UMOVE_SPECIAL 2
#define UMOVE_SPELL 3
#define UMOVE_HYPE 4
#define UMOVE_WAIT 5
#define UMOVE_MAX 8

/* Leg 2.11: UMOVE_NMOVE replaces the old UMOVE_SECONDARY/UMOVE_TOXIC
   split -- both crystal secondaries and the shiny-exclusive move now
   carry the same shape (move_kind: stage or status), they just source
   from NATURE_MOVES[] vs SHINY_MOVE_*. Damage-dealing fields (stat/
   power/speed) stay for basic/special/spell; nmove/hype never deal
   damage, power is always 0. */
typedef struct {
    int kind;
    const char *name;
    int stat;
    float power, speed;
    int spell_id;
    int move_kind;     /* NMOVE_KIND_STAGE/STATUS, kind==UMOVE_NMOVE only */
    int stat_target;    /* STAT_STR/AGL/SPC, move_kind==stage only */
    int status_target;  /* STATUS_*, move_kind==status (or UMOVE_HYPE n/a) */
    int max_pp;          /* kind==UMOVE_NMOVE or UMOVE_HYPE only */
} UMove;

static const char *const SPELL_MENU_NAME[4] = {
    "FIRE BOLT", "ICE BEAM", "LIGHTNING STRIKE", "MANA SURGE"
};

static int str_same(const char *a, const char *b) {
    int i;
    if(!a || !b) return 0;
    for(i = 0; ; i++) {
        if(a[i] != b[i]) return 0;
        if(!a[i]) return 1;
    }
}

/* Leg 2.11: any species that is some other species' evolves_to target has
   evolved into its current form, and Hype Up is learned on evolving --
   deliberately not a persisted flag, just derived from SPECIES here. */
static int knows_hype_up(int species) {
    int i;
    for(i = 0; i < SPECIES_N; i++) if(SPECIES[i].evolves_to == species) return 1;
    return 0;
}

static int unlocked_moves(const Monster *m, int include_wait, UMove *out, int cap) {
    const Species *s;
    int n = 0;
    int i;
    if(!m || !out || cap <= 0) return 0;
    s = &SPECIES[m->species];
    out[n].kind = UMOVE_BASIC;
    out[n].name = s->basic;
    out[n].stat = s->basic_stat;
    out[n].power = s->basic_power;
    out[n].speed = s->basic_speed;
    out[n].spell_id = -1;
    out[n].move_kind = out[n].stat_target = out[n].status_target = out[n].max_pp = 0;
    n++;
    if(m->lv >= LV_SECONDARY && n < cap) {
        if(m->shiny) {
            out[n].kind = UMOVE_NMOVE;
            out[n].name = SHINY_MOVE_NAME;
            out[n].stat = ATK_STR;
            out[n].power = 0.0f;
            out[n].speed = 1.0f;
            out[n].spell_id = -1;
            out[n].move_kind = NMOVE_KIND_STATUS;
            out[n].stat_target = 0;
            out[n].status_target = SHINY_MOVE_STATUS;
            out[n].max_pp = SHINY_MOVE_MAX_PP;
            n++;
        } else {
            const NatureMove *nm = &NATURE_MOVES[species_nature(m->species)];
            out[n].kind = UMOVE_NMOVE;
            out[n].name = nm->name;
            out[n].stat = ATK_STR;
            out[n].power = 0.0f;
            out[n].speed = 1.0f;
            out[n].spell_id = -1;
            out[n].move_kind = nm->kind;
            out[n].stat_target = nm->stat;
            out[n].status_target = nm->status;
            out[n].max_pp = nm->max_pp;
            n++;
        }
    }
    if(knows_hype_up(m->species) && n < cap) {
        out[n].kind = UMOVE_HYPE;
        out[n].name = HYPE_UP_NAME;
        out[n].stat = ATK_STR;
        out[n].power = 0.0f;
        out[n].speed = 1.0f;
        out[n].spell_id = -1;
        out[n].move_kind = out[n].stat_target = out[n].status_target = 0;
        out[n].max_pp = HYPE_UP_MAX_PP;
        n++;
    }
    if(m->lv >= LV_SPECIAL) {
        if(s->spells_n > 0) {
            for(i = 0; i < s->spells_n && n < cap; i++) {
                int sid = s->spells[i];
                const SpellDef *sp;
                if(sid < 0 || sid > 3) continue;
                if(str_same(SPELL_MENU_NAME[sid], s->basic)) continue;
                sp = &SPELLS[sid];
                out[n].kind = UMOVE_SPELL;
                out[n].name = SPELL_MENU_NAME[sid];
                out[n].stat = sp->stat;
                out[n].power = sp->power;
                out[n].speed = sp->speed;
                out[n].spell_id = sid;
                out[n].move_kind = out[n].stat_target = out[n].status_target = out[n].max_pp = 0;
                n++;
            }
        } else if(n < cap) {
            out[n].kind = UMOVE_SPECIAL;
            out[n].name = s->special;
            out[n].stat = s->special_stat;
            out[n].power = s->special_power;
            out[n].speed = s->special_speed;
            out[n].spell_id = -1;
            out[n].move_kind = out[n].stat_target = out[n].status_target = out[n].max_pp = 0;
            n++;
        }
    }
    if(include_wait && n < cap) {
        out[n].kind = UMOVE_WAIT;
        out[n].name = "WAIT";
        out[n].stat = ATK_STR;
        out[n].power = 0;
        out[n].speed = 0;
        out[n].spell_id = -1;
        out[n].move_kind = out[n].stat_target = out[n].status_target = out[n].max_pp = 0;
        n++;
    }
    return n;
}

static unsigned char g_dex_seen[SAVE_DEX_BYTES];
static unsigned char g_dex_caught[SAVE_DEX_BYTES];
static Monster *g_xp_party;
static int g_xp_party_n, g_xp_lead;

static void dex_set(unsigned char *bits, int sp) {
    if(sp < 0 || sp > 31) return;
    bits[sp >> 3] |= (unsigned char)(1u << (sp & 7));
}
static int dex_get(const unsigned char *bits, int sp) {
    if(sp < 0 || sp > 31) return 0;
    return (bits[sp >> 3] >> (sp & 7)) & 1;
}
static void dex_note_seen(int sp) { dex_set(g_dex_seen, sp); }
static void dex_note_caught(int sp) { dex_note_seen(sp); dex_set(g_dex_caught, sp); }
static void dex_clear(void) {
    int i;
    for(i = 0; i < SAVE_DEX_BYTES; i++) g_dex_seen[i] = g_dex_caught[i] = 0;
}

/* xorshift32, seeded from the frame counter at title-screen dismissal
   (see main()) -- there's no RTC/libc rand() in this freestanding
   build, so this stands in for math.random()/irand() throughout the
   ported formulas below. Not cryptographic, just enough variance for
   a homebrew game. */
static u32 rng_state = 0x9e3779b9u;
static u32 rng_next(void) {
    rng_state ^= rng_state << 13;
    rng_state ^= rng_state >> 17;
    rng_state ^= rng_state << 5;
    return rng_state;
}
static int irand(int a, int b) {
    return a + (int)(rng_next() % (u32)(b - a + 1));
}

static int jground(float x) {
    return (int)(x + 0.5f);
}

static int clampi(int v, int lo, int hi) {
    if(v < lo) return lo;
    if(v > hi) return hi;
    return v;
}

/* No libc/math.h here, so a hand-rolled Newton-Raphson sqrt for the
   actor-movement code below (normalizing a chase/approach direction
   vector needs a real magnitude, not just the squared distance used
   everywhere else's proximity checks). 12 iterations is overkill for
   the small pixel distances involved but costs nothing on the SH4's
   single-precision FPU. */
static float f_sqrt(float x) {
    float guess;
    int i;
    if(x <= 0.0f) return 0.0f;
    guess = x > 1.0f ? x : 1.0f;
    for(i = 0; i < 12; i++)
        guess = 0.5f * (guess + x / guess);
    return guess;
}

static Monster mint_monster(int species, int lv) {
    const Species *s = &SPECIES[species];
    float g;
    Monster m;
    const NatureDef *nat;
    if(lv < 1) lv = 1;
    if(lv > LEVEL_CAP) lv = LEVEL_CAP;
    g = 1.0f + (float)(lv - 3) * 0.12f;
    m.species = species;
    m.lv = lv;
    m.xp = 0;
    m.maxHp = jground((float)s->maxHp * g);
    m.str = jground((float)s->str * g);
    m.agl = jground((float)s->agl * g);
    m.spc = jground((float)s->spc * g);
    m.spp = s->spp;
    m.sppMax = s->spp;
    m.hp = m.maxHp;
    m.shiny = 0;
    nat = &NATURES[species_nature(species)];
    m.str += nat->str;
    m.agl += nat->agl;
    m.spc += nat->spc;
    m.status = STATUS_NONE;
    m.status_turns = 0;
    m.poison_stack = 0;
    dex_note_seen(species);
    return m;
}

/* Shiny variant: a rare (1/64) wild-encounter-only recolor, minted at
   double the level try_encounter() would otherwise have picked (capped),
   with Toxic Burst at LV_SECONDARY instead of the shared crystal secondary.
   Never rolled for a scripted trainer/NPC fight. */
static Monster mint_shiny(int species, int lv) {
    int slv = lv * 2;
    Monster m;
    if(slv < lv) slv = lv;
    if(slv > LEVEL_CAP) slv = LEVEL_CAP;
    m = mint_monster(species, slv);
    m.shiny = 1;
    return m;
}
static int roll_shiny(void) {
    return irand(0, SHINY_DENOM - 1) == 0;
}

/* data.grantXp: +xpBase+xpPerLevel*foeLv xp per win, level up
   (+levelHp maxHp, +levelStat each stat) while xp >= lv*levelXpMul,
   capped at LEVEL_CAP. Evolves at LV_EVOLVE when the species has
   evolves_to. Returns 1 if it leveled or evolved. */
static char g_evo_note[48];

static int try_evolve(Monster *m) {
    const Species *s;
    int to, from, old_hp, old_max, shiny, xp, n, hp;
    Monster next;
    if(!m) return 0;
    s = &SPECIES[m->species];
    to = s->evolves_to;
    if(to < 0 || to >= SPECIES_N || m->lv < LV_EVOLVE) return 0;
    from = m->species;
    old_hp = m->hp;
    old_max = m->maxHp;
    shiny = m->shiny;
    xp = m->xp;
    next = mint_monster(to, m->lv);
    next.shiny = shiny;
    next.xp = xp;
    /* Leg 2.11: status persists through evolution, same as web's tryEvolve
       (which never touches it since it copies fields onto the existing
       object instead of overwriting -- this path does overwrite, so it
       has to be carried across explicitly). */
    next.status = m->status;
    next.status_turns = m->status_turns;
    next.poison_stack = m->poison_stack;
    if(old_max > 0) {
        hp = old_hp * next.maxHp / old_max;
        if(hp < 1) hp = 1;
        if(hp > next.maxHp) hp = next.maxHp;
        next.hp = hp;
    }
    n = s_cat(g_evo_note, 0, SPECIES[from].name);
    n = s_cat(g_evo_note, n, " EVOLVED INTO ");
    n = s_cat(g_evo_note, n, SPECIES[to].name);
    g_evo_note[n] = 0;
    *m = next;
    dex_note_caught(to);
    return 1;
}

static int grant_xp(Monster *m, int foe_lv, int pct) {
    int grew = 0;
    m->xp += (XP_BASE + foe_lv * XP_PER_LEVEL) * pct / 100;
    while(m->xp >= m->lv * LEVEL_XP_MUL && m->lv < LEVEL_CAP) {
        m->xp -= m->lv * LEVEL_XP_MUL;
        m->lv++;
        m->maxHp += LEVEL_HP;
        m->hp += LEVEL_HP;
        if(m->hp > m->maxHp) m->hp = m->maxHp;
        m->str += LEVEL_STAT;
        m->agl += LEVEL_STAT;
        m->spc += LEVEL_STAT;
        grew = 1;
    }
    if(try_evolve(m)) grew = 1;
    return grew;
}

static int grant_party_xp(Monster *party, int party_n, int lead, int foe_lv) {
    int i, grew = 0;
    g_evo_note[0] = 0;
    for(i = 0; i < party_n; i++) {
        int pct;
        if(party[i].hp <= 0) continue;
        pct = (i == lead) ? 100 : BENCH_XP_PCT;
        if(grant_xp(&party[i], foe_lv, pct)) grew = 1;
    }
    return grew;
}

/* fullHeal(), also used by the bed and by a party wipe's fade-and-
   teleport-home (see main()'s FADE_ACTION_BED/FADE_ACTION_LOSS). */
static void roll_all_shop_stock(void); /* defined below, once ITEM_COUNT/SHOP_CRYSTAL_MASK_N are #include'd */

static void heal_party(Monster *party, int party_n) {
    int i;
    roll_all_shop_stock();
    for(i = 0; i < party_n; i++) {
        party[i].hp = party[i].maxHp;
        party[i].spp = party[i].sppMax;
    }
}

/* Leg 2.5: base% (per crystal tier, default 100) minus the foe's
   level, strength, and current HP, all in raw stat units. A status
   condition adds a flat +50. Mirrors src/game/data.ts's
   captureChance() exactly -- see its comment for why. Replaces the
   old agl/missing-hp%-based formula (CAPTURE_AGL/CAPTURE_VULN are
   retired, still baked from logic.json but no longer read here). */
static int capture_chance(int level, int str, int hp, int vulnerable, int base) {
    int chance = base - level - str - hp;
    if(vulnerable) chance += 50;
    return clampi(chance, 0, 100);
}

/* ----------------------------------------------------------------------
 * Bag and party menus, ported from render.lua's drawBag()/drawParty().
 * Opened from the world with Y (bag) or START (party), closed with B;
 * items are actually used from the battle system's own item menu
 * (below), not from here -- these two screens stay read-only info
 * views outside battle, matching state.lua's BAG/PARTY mode update
 * (open/close only, no cursor/use logic there either). No
 * lead-switching menu here since this port has no multi-monster
 * roster to switch within (see Monster/party_mon). data.lua's
 * START_BAG gives the starting counts (salve 2, bandage 2, bitterroot
 * 1, dust 1, gem 0) and START_MARKS (16); both bag counts and marks
 * are now real, mutable state once the battle system below uses/
 * grants them. Item icons (render.lua's "item-<id>" sprites) aren't
 * ported -- text rows only, like the rest of this port's UI.
 * ---------------------------------------------------------------------- */
typedef struct {
    int salve, bandage, bitterroot, dust, gem;
    int sunbalm, warroot, smokebomb, greatcrystal, cageKey;
    int megacrystal, ultimatecrystal, perfectcrystal; /* Leg 2.5 */
    int calmdraft, burnsalve, antidote, clearmind, numbroot, panacea; /* Leg 2.11 */
    int bowieKnife; /* Dray's one-of-a-kind Backstab item */
} Bag;

typedef struct {
    const char *name;
    int buy, sell;
} ItemDef;
#include "content_items.inc"

static int *bag_field(Bag *bag, int idx) {
    switch(idx) {
        case 0: return &bag->salve;
        case 1: return &bag->bandage;
        case 2: return &bag->bitterroot;
        case 3: return &bag->dust;
        case 4: return &bag->gem;
        case 5: return &bag->sunbalm;
        case 6: return &bag->warroot;
        case 7: return &bag->smokebomb;
        case 8: return &bag->greatcrystal;
        case 9: return &bag->cageKey;
        case 10: return &bag->megacrystal;
        case 11: return &bag->ultimatecrystal;
        case 12: return &bag->perfectcrystal;
        case 13: return &bag->calmdraft;
        case 14: return &bag->burnsalve;
        case 15: return &bag->antidote;
        case 16: return &bag->clearmind;
        case 17: return &bag->numbroot;
        case 18: return &bag->panacea;
        default: return &bag->bowieKnife;
    }
}

#define MENU_X 20
#define MENU_Y 20
#define MENU_W (SCREEN_W - 2 * MENU_X)
#define MENU_H (SCREEN_H - 2 * MENU_Y)
#define MENU_SCALE 1
#define MENU_ROW_H 16

/* No background panel -- outlined text reads fine directly over
   whatever's behind the menu (the world scene, since draw_bag_menu/
   draw_party_menu/draw_shop are all drawn as an overlay after it). */
static void draw_menu_frame(const char *title, const char *footer) {
    draw_text_s(title, MENU_X + 8, MENU_Y + 8, 0xFFFF, MENU_SCALE);
    draw_text_s(footer, MENU_X + 8, MENU_Y + MENU_H - 16,
                rgb565(180, 220, 170), MENU_SCALE);
}

static void draw_pause_menu(int cur) {
    static const char *const rows[6] = { "PARTY", "BAG", "CRYDEX", "SETTINGS", "SAVE", "CLOSE" };
    int i;
    draw_menu_frame("PAUSE", "A SELECT  B CLOSE");
    for(i = 0; i < 6; i++)
        draw_text_s(rows[i], MENU_X + 16, MENU_Y + 24 + i * MENU_ROW_H,
                    i == cur ? rgb565(90, 122, 82) : rgb565(197, 206, 198), MENU_SCALE);
}

static void draw_crydex(int cur, int entry) {
    char buf[48];
    int i, n, caught_n = 0, seen_n = 0, vis = 8, start, y;
    for(i = 0; i < SPECIES_N; i++) {
        if(dex_get(g_dex_caught, i)) caught_n++;
        if(dex_get(g_dex_seen, i)) seen_n++;
    }
    if(entry && cur >= 0 && cur < SPECIES_N && dex_get(g_dex_caught, cur)) {
        int nat = species_nature(cur);
        int pos = NATURES[nat].ring;
        int k;
        draw_menu_frame("CRYDEX", "A/B BACK");
        draw_text_s(SPECIES[cur].name, MENU_X + 8, MENU_Y + 24, 0xFFFF, MENU_SCALE);
        n = s_cat(buf, 0, NATURES[nat].name);
        n = s_cat(buf, n, " CRYSTAL");        buf[n] = 0;
        draw_text_s(buf, MENU_X + 8, MENU_Y + 24 + MENU_ROW_H, rgb565(197, 206, 198), MENU_SCALE);
        draw_text_s("WEAK TO", MENU_X + 8, MENU_Y + 24 + MENU_ROW_H * 3, rgb565(143, 74, 64), MENU_SCALE);
        n = 0;
        buf[0] = 0;
        for(k = 1; k <= NATURE_BEATS_AHEAD; k++) {
            int wr = (pos - k + NATURE_RING_N) % NATURE_RING_N;
            if(n) n = s_cat(buf, n, ", ");
            n = s_cat(buf, n, NATURES[nature_index_by_ring(wr)].name);
        }
        buf[n] = 0;
        draw_text_s(buf, MENU_X + 8, MENU_Y + 24 + MENU_ROW_H * 4, rgb565(232, 228, 216), MENU_SCALE);
        draw_text_s("RESISTS", MENU_X + 8, MENU_Y + 24 + MENU_ROW_H * 6, rgb565(90, 122, 82), MENU_SCALE);
        n = 0;
        buf[0] = 0;
        for(k = 1; k <= NATURE_BEATS_AHEAD; k++) {
            int rr = (pos + k) % NATURE_RING_N;
            if(n) n = s_cat(buf, n, ", ");
            n = s_cat(buf, n, NATURES[nature_index_by_ring(rr)].name);
        }
        buf[n] = 0;
        draw_text_s(buf, MENU_X + 8, MENU_Y + 24 + MENU_ROW_H * 7, rgb565(232, 228, 216), MENU_SCALE);
        return;
    }
    draw_menu_frame("CRYDEX", dex_get(g_dex_caught, cur) ? "A MATCHUP  B BACK" : "UP/DOWN  B BACK");
    n = s_cat(buf, 0, "");
    n = s_cat_uint(buf, 0, caught_n);
    n = s_cat(buf, n, "/");
    n = s_cat_uint(buf, n, SPECIES_N);
    n = s_cat(buf, n, " CAUGHT  ");
    n = s_cat_uint(buf, n, seen_n);
    n = s_cat(buf, n, " SEEN");
    buf[n] = 0;
    draw_text_s(buf, MENU_X + 8, MENU_Y + 22, rgb565(197, 206, 198), MENU_SCALE);
    start = cur - vis / 2;
    if(start < 0) start = 0;
    if(start > SPECIES_N - vis) start = SPECIES_N - vis;
    if(start < 0) start = 0;
    y = MENU_Y + 36;
    for(i = 0; i < vis; i++) {
        int idx = start + i;
        u16 color;
        if(idx >= SPECIES_N) break;
        n = s_cat(buf, 0, (idx == cur) ? ">" : " ");
        n = s_cat_uint(buf, n, idx + 1);
        n = s_cat(buf, n, " ");
        if(dex_get(g_dex_caught, idx)) {
            n = s_cat(buf, n, SPECIES[idx].name);
            n = s_cat(buf, n, "  ");
            n = s_cat(buf, n, NATURES[species_nature(idx)].name);
            color = rgb565(232, 228, 216);
        } else if(dex_get(g_dex_seen, idx)) {
            n = s_cat(buf, n, SPECIES[idx].name);
            color = rgb565(180, 180, 160);
        } else {
            n = s_cat(buf, n, "?????");
            color = rgb565(90, 88, 78);
        }
        buf[n] = 0;
        draw_text_s(buf, MENU_X + 8, y, color, MENU_SCALE);
        y += MENU_ROW_H;
    }
}

/* ITEM_COUNT-indexed icon lookup (ITEM_SALVE..ITEM_GEM, defined
   further down with the rest of the item-menu kinds) -- shared by the
   bag, shop, and battle item-menu rows below, all of which previously
   showed items as bare text. icon may be null (the item-menu's "PASS"
   row has no matching icon). */
static const u16 *const ITEM_ICONS[] = {
    icon_salve, icon_bandage, icon_bitterroot, icon_dust, icon_gem,
    icon_sunbalm, icon_warroot, icon_smokebomb, icon_greatcrystal, icon_cageKey,
    icon_megacrystal, icon_ultimatecrystal, icon_perfectcrystal,
    icon_calmdraft, icon_burnsalve, icon_antidote, icon_clearmind, icon_numbroot, icon_panacea
};

/* Effect text is stripped out of the row's own title now (matching
   the battle item menu below) and only drawn when the row is the one
   under the cursor, so the list reads as plain item names/counts
   until the player actually navigates onto one. */
static const char *const ITEM_EFFECT_DESC[] = {
    "+22 HP", "+12 HP", "STR+4", "-3/-2/-2", "CATCH",
    "+40 HP", "AGL+4", "FLEE", "CATCH+", "CAGE KEY",
    "CATCH++", "CATCH+++", "ALWAYS CATCH",
    "RESET STAGES", "CURE BURN", "CURE POISON", "CURE CONFUSE",
    "CURE PARALYZE", "CURE ANY"
};

static void draw_bag_row(const u16 *icon, const char *label, int count,
                          int idx, int cur, int y) {
    char buf[48];
    int n;
    u16 color = (idx == cur) ? rgb565(232, 228, 216) : rgb565(138, 134, 120);

    draw_text_s(idx == cur ? ">" : " ", MENU_X + 8, y, color, MENU_SCALE);
    if(icon)
        blit_sprite(icon, ITEM_ICON_W, ITEM_ICON_H, MENU_X + 16, y - 1);

    n = s_cat(buf, 0, label);
    n = s_cat(buf, n, " X");
    n = s_cat_uint(buf, n, count);
    if(idx == cur) {
        n = s_cat(buf, n, "  ");
        n = s_cat(buf, n, ITEM_EFFECT_DESC[idx]);
    }
    buf[n] = 0;
    draw_text_s(buf, MENU_X + 16 + ITEM_ICON_W + 4, y, color, MENU_SCALE);
}

/* Leg 2.5: item count grew past what fits in the fixed menu box in one
   screen (13 rows * 16px > the ~200px box), so this is now a
   cursor-following scroll window (matching the web bag's own
   shown=4-with-scroll pattern) instead of 10 hardcoded rows. */
#define BAG_ROWS_SHOWN 10
static void draw_bag_menu(const Bag *bag, int marks, int cur) {
    int y = MENU_Y + 24;
    char marks_buf[16];
    int n, i, start, max_start;

    draw_menu_frame("BAG", "UP/DOWN A USE  B CLOSE");

    n = s_cat(marks_buf, 0, "MARKS ");
    n = s_cat_uint(marks_buf, n, marks);
    marks_buf[n] = 0;
    draw_text_s(marks_buf, MENU_X + MENU_W - 8 - text_width_s(marks_buf, MENU_SCALE),
                MENU_Y + 8, rgb565(143, 74, 64), MENU_SCALE);

    max_start = ITEM_COUNT - BAG_ROWS_SHOWN;
    if(max_start < 0) max_start = 0;
    start = cur - BAG_ROWS_SHOWN / 2;
    if(start < 0) start = 0;
    if(start > max_start) start = max_start;
    for(i = start; i < start + BAG_ROWS_SHOWN && i < ITEM_COUNT; i++) {
        draw_bag_row(ITEM_ICONS[i], ITEMS[i].name, *bag_field((Bag *)bag, i), i, cur, y);
        y += MENU_ROW_H;
    }
}

/* drawParty(): lists every party member (up to data.PARTY_MAX -- see
   Monster party[6] in main()), with a ">" prefix and brighter color on
   the current lead, plus a cursor ("*") on party_cur -- cycleParty(to)
   ported: pressing A on a living, non-lead row makes it the new lead
   (main()'s menu_mode==2 input handling), matching the reference's
   own Digit1-6 hotkeys adapted to a dpad+cursor since there's no
   number row on a Dreamcast pad. */
/* Y opens this from the list for whichever row party_cur is on --
   attacks (basic/special, or the full spell list for a caster like
   Cathleen), stats, and where the CryMon sits in the party order
   (main()'s menu_mode==2 input handling keeps party_cur live under
   up/down while this is open, so browsing the whole party doesn't
   need to back out to the list each time). */
static void draw_move_facts(const char *name, int stat, float power, float speed, int atk, int *y) {
    char buf[48];
    int n;
    int dmg = jground((float)atk * power);
    int spd = jground(speed * 10.0f);
    if(dmg < 1) dmg = 1;
    n = s_cat(buf, 0, name);
    n = s_cat(buf, n, stat == ATK_STR ? "  STR " : "  MAG ");
    n = s_cat(buf, n, "DMG");
    n = s_cat_uint(buf, n, (unsigned)dmg);
    n = s_cat(buf, n, " SPD");
    n = s_cat_uint(buf, n, (unsigned)spd);
    buf[n] = 0;
    draw_text_s(buf, MENU_X + 8, *y, rgb565(232, 228, 216), MENU_SCALE);
    *y += MENU_ROW_H;
}

static void draw_party_detail(const Monster *party, int party_n, int idx) {
    const Monster *m = &party[idx];
    const Species *s = &SPECIES[m->species];
    char buf[48];
    int n, y = MENU_Y + 24;

    draw_menu_frame("CRYMON", "UP/DOWN SWITCH  B BACK");

    n = s_cat(buf, 0, m->shiny ? "SHINY " : "");
    n = s_cat(buf, n, s->name);
    buf[n] = 0;
    draw_text_s(buf, MENU_X + 8, y, 0xFFFF, MENU_SCALE); y += MENU_ROW_H;

    n = s_cat(buf, 0, "LV");
    n = s_cat_uint(buf, n, m->lv);
    n = s_cat(buf, n, "  ");
    n = s_cat(buf, n, NATURES[species_nature(m->species)].name);
    n = s_cat(buf, n, "  HP ");
    n = s_cat_uint(buf, n, m->hp);
    n = s_cat(buf, n, "/");
    n = s_cat_uint(buf, n, m->maxHp);
    buf[n] = 0;
    draw_text_s(buf, MENU_X + 8, y, rgb565(232, 228, 216), MENU_SCALE); y += MENU_ROW_H;

    n = s_cat(buf, 0, "STR ");
    n = s_cat_uint(buf, n, m->str);
    n = s_cat(buf, n, "  AGL ");
    n = s_cat_uint(buf, n, m->agl);
    n = s_cat(buf, n, "  MAG ");
    n = s_cat_uint(buf, n, m->spc);
    buf[n] = 0;
    draw_text_s(buf, MENU_X + 8, y, rgb565(232, 228, 216), MENU_SCALE); y += MENU_ROW_H * 2;

    draw_text_s("ATTACKS", MENU_X + 8, y, rgb565(180, 220, 170), MENU_SCALE); y += MENU_ROW_H;
    {
        UMove moves[UMOVE_MAX];
        int mn = unlocked_moves(m, 0, moves, UMOVE_MAX);
        int i;
        for(i = 0; i < mn; i++) {
            int atk = moves[i].stat == ATK_STR ? m->str : m->spc;
            draw_move_facts(moves[i].name, moves[i].stat, moves[i].power, moves[i].speed,
                            atk, &y);
        }
    }
    y += MENU_ROW_H;

    n = s_cat(buf, 0, "ORDER ");
    n = s_cat_uint(buf, n, idx + 1);
    n = s_cat(buf, n, " OF ");
    n = s_cat_uint(buf, n, party_n);
    buf[n] = 0;
    draw_text_s(buf, MENU_X + 8, y, rgb565(180, 220, 170), MENU_SCALE);

}

static int party_release(Monster *party, int *party_n, int *lead, int idx) {
    int i;
    if(*party_n <= 1 || idx < 0 || idx >= *party_n) return 0;
    for(i = idx; i < *party_n - 1; i++) party[i] = party[i + 1];
    (*party_n)--;
    if(*lead == idx) *lead = 0;
    else if(*lead > idx) (*lead)--;
    return 1;
}

/* heal_item selects who a salve/wrap/sunbalm picked from the bag menu
   goes to (0 salve, 1 wrap, 5 sunbalm, -1 not healing) -- same list as
   the plain party menu, just with a different title/footer and A
   applying the item to party_cur instead of setting the lead (see
   main()'s menu_mode==2 input handling). */
static void draw_settings_menu(void) {
    int pct = chip_volume_pct();
    int bar_w = MENU_W - 24;
    int fill = chip_volume_fill(bar_w);
    char line[40];
    int n;
    int y = MENU_Y + 24;
    draw_menu_frame("SETTINGS", "UP/DOWN VOLUME  B BACK");
    n = s_cat(line, 0, "VOLUME ");
    n = s_cat_uint(line, n, (unsigned)pct);
    n = s_cat(line, n, "%");
    line[n] = 0;
    draw_text_s(line, MENU_X + 8, y, rgb565(197, 206, 198), MENU_SCALE);
    y += MENU_ROW_H;
    fill_rect(MENU_X + 8, y, bar_w, 8, rgb565(42, 38, 32));
    fill_rect(MENU_X + 8, y, fill, 8, rgb565(90, 122, 82));
    y += MENU_ROW_H;
    draw_text_s("200% IS TWICE THE OLD MAX", MENU_X + 8, y, rgb565(138, 134, 120), MENU_SCALE);
}

static void draw_party_menu(const Monster *party, int party_n, int lead, int party_cur,
                             int party_detail, int heal_item, int catch_swap) {
    int y = MENU_Y + 24;

    if(party_detail && party_n > 0 && !catch_swap) {
        draw_party_detail(party, party_n, party_cur);
        return;
    }

    if(catch_swap)
        draw_menu_frame("PARTY FULL. RELEASE WHO?", "A RELEASE  B LET NEW GO");
    else if(heal_item >= 0) {
        const char *title = heal_item == 0 ? "USE MOSS SALVE ON WHO?"
                           : heal_item == 1 ? "USE LINEN WRAP ON WHO?"
                                             : "USE SUNBALM ON WHO?";
        draw_menu_frame(title, "A HEAL  B CANCEL");
    }
    else
        draw_menu_frame("CRYMON", "B CLOSE");

    if(party_n > 0) {
        int i;
        for(i = 0; i < party_n; i++) {
            char buf[40];
            u16 color = (i == lead) ? rgb565(232, 228, 216) : rgb565(138, 134, 120);
            int n;
            draw_party_mon_icon(party[i].species, MENU_X + 8, y - 2);
            n = s_cat(buf, 0, (i == party_cur) ? "*" : " ");
            n = s_cat(buf, n, (i == lead) ? "> " : "  ");
            if(party[i].shiny) n = s_cat(buf, n, "SHINY ");
            n = s_cat(buf, n, SPECIES[party[i].species].name);
            n = s_cat(buf, n, " LV");
            n = s_cat_uint(buf, n, party[i].lv);
            n = s_cat(buf, n, " HP ");
            n = s_cat_uint(buf, n, party[i].hp);
            n = s_cat(buf, n, "/");
            n = s_cat_uint(buf, n, party[i].maxHp);
            buf[n] = 0;
            draw_text_s(buf, MENU_X + 28, y, color, MENU_SCALE);
            y += 20;
        }
        if(heal_item < 0 && !catch_swap)
            draw_text_s("A LEAD  X RELEASE  Y VIEW", MENU_X + 8, MENU_Y + MENU_H - 32,
                        rgb565(138, 134, 120), MENU_SCALE);
    }
    else {
        draw_text_s("NO CRYMON YET", MENU_X + 8, y, rgb565(138, 134, 120), MENU_SCALE);
    }
}

/* The father-vs-Heavenfall resurrection choice, armed by
   POST_OPEN_CHOICE once TALK_SHINIGAMI_WIN closes (main()'s
   choice_mode) -- Anne's reveal (TALK_ANNE_RETURN) already happened
   earlier, right after Cathleen, so by the time the scroll actually
   exists this is just the payoff. Same frame/menu-row visual language
   as every other full-screen menu here, just with only 2 rows and no
   way to back out -- this is the one decision in the whole game that
   isn't optional, matching "present the player with a choice" rather
   than a plain dialogue beat with no real branch. */
static void draw_choice_row(const char *label, int idx, int cur, int y) {
    u16 color = (idx == cur) ? rgb565(232, 228, 216) : rgb565(138, 134, 120);
    draw_text_s(idx == cur ? ">" : " ", MENU_X + 8, y, color, MENU_SCALE);
    draw_text_s(label, MENU_X + 16, y, color, MENU_SCALE);
}

static void draw_choice(int cur) {
    int y = MENU_Y + 24;

    draw_menu_frame("THE SCROLL", "A CHOOSE");
    draw_wrapped("THE SCROLL CAN WAKE ONE OF THE DEAD.",
                 MENU_X + 8, y, rgb565(197, 206, 198), MENU_SCALE,
                 (MENU_W - 16) / CHAR_CELL(MENU_SCALE), 9);
    y += 28;

    draw_choice_row("RESURRECT FATHER", 0, cur, y); y += MENU_ROW_H;
    draw_choice_row("RESURRECT HEAVENFALL", 1, cur, y); y += MENU_ROW_H * 2;

    draw_wrapped(cur == 0 ? "HE COMES BACK AS HE WAS. HUMAN, AND HERS."
                          : "AN ANCIENT CRYMON WAKES. VAST AND UNKNOWN.",
                 MENU_X + 8, y, rgb565(138, 134, 120), MENU_SCALE,
                 (MENU_W - 16) / CHAR_CELL(MENU_SCALE), 9);
}

static void draw_mercy(int cur, const char *foe_name)
{
    int y = MENU_Y + 20;
    char sub[48];
    draw_menu_frame("AFTER THE FIGHT", "A CHOOSE");
    if(foe_name && foe_name[0]) {
        int i = 0;
        while(i < 40 && foe_name[i]) { sub[i] = foe_name[i]; i++; }
        sub[i] = 0;
        draw_wrapped(sub, MENU_X + 8, y, rgb565(138, 134, 120), MENU_SCALE,
                     (MENU_W - 16) / CHAR_CELL(MENU_SCALE), 9);
        y += 18;
    }
    draw_choice_row("LET THEM GO", 0, cur, y); y += MENU_ROW_H;
    draw_choice_row("THREATEN FOR MARKS", 1, cur, y); y += MENU_ROW_H;
    draw_choice_row("THREATEN FOR AN ITEM", 2, cur, y); y += MENU_ROW_H;
    draw_choice_row("EXECUTE", 3, cur, y);
}

/* Leg 2.12 Bowie Knife: 2-row Approach/Backstab prompt, shown instead
 * of normal dialogue when the player carries the knife and interacts
 * with a roamable wsoldier trainer that hasn't spotted them yet
 * (mirrors engine.ts's drawBackstabChoice()). */
static void draw_backstab(int cur) {
    int y = MENU_Y + 20;
    draw_menu_frame("BOWIE KNIFE", "A CHOOSE  B CANCEL");
    draw_wrapped("THEY HAVEN'T SEEN YOU.",
                 MENU_X + 8, y, rgb565(138, 134, 120), MENU_SCALE,
                 (MENU_W - 16) / CHAR_CELL(MENU_SCALE), 9);
    y += 18;
    draw_choice_row("APPROACH", 0, cur, y); y += MENU_ROW_H;
    draw_choice_row("BACKSTAB", 1, cur, y);
}


/* ----------------------------------------------------------------------
 * Battle system, ported from state.lua's updateBattle()/pickAtk()/
 * pickGuard()/pickItem()/applyHit()/finishWin() and captureChanceNow().
 * Wild encounters (tryEncounter()/startBattle()) and trainer battles
 * both use this same struct/update loop, matching state.lua (which
 * shares updateBattle() between them too): trainer_kind names who
 * G.bTrainer would be, bench holds Shinigami's 2 backup CryMare
 * (data.lua's only nbench > 0 fight). Cathleen's real castSpell() kit
 * (Fire Bolt/Ice Beam/Lightning Strike/Mana Surge) is ported --
 * battle_cast_spell()/battle_pick_spell(), further down -- for both
 * her wild GROVE fight and as a captured player lead.
 *
 * The post-win "grew to lv N"/"stands over the grass" line is a real
 * timed-fade HUD toast (main()'s hud_flash/hud_t, set at the tail of
 * this switch below), matching state.lua's note()/G.hudT exactly
 * instead of an extra clickable battle message.
 * ---------------------------------------------------------------------- */
typedef struct {
    Monster pl, foe;
    int wild;
    int phase;      /* 0 msg, 1 item, 2 attack, 3 guard, 4 special minigame */
    char msg[3][80];  /* a move label plus damage, a crystal-matchup tag and
                         a poison tick can share one line; draw_wrapped()
                         re-flows it to fit the box */
    int msg_n, msg_i;
    int after;
    int cur;        /* menu cursor for phases 1-3 */
    int mods_self_str, mods_self_agl, mods_self_spc;
    int mods_foe_str, mods_foe_agl, mods_foe_spc;
    int pend_str, pend_agl, pend_spc; /* crystal secondary, applied on hit */
    int pl_poisoned, foe_poisoned; /* retired by Leg 2.11 -- pl/foe.status
                                       replaces these; the fields stay to
                                       avoid touching every struct literal,
                                       but nothing sets or reads them now */
    /* Leg 2.11: stage-based stat drops (Proud Roar etc.), battle-scoped,
       mirrors the mods_self_ / mods_foe_ fields above in shape. Real
       status conditions (burned/poisoned/confused/paralyzed/exhausted)
       live on pl.status/foe.status instead -- see Monster below. */
    int stage_self_str, stage_self_agl, stage_self_spc;
    int stage_foe_str, stage_foe_agl, stage_foe_spc;
    int hype_self, hype_foe; /* Hype Up active this battle, non-stacking */
    int nmove_pl_used, hype_pl_used, nmove_foe_used, hype_foe_used; /* PP */
    char pend_effect[24]; /* nmove/hype's effect text, staged for battle_apply_hit */
    int dmg;
    float mg;           /* special timing needle 0-100 */
    int mg_dir;
    char label[28];
    int grew;       /* set by finish_win() below, read by the WIN_NOTE beat */
    int trainer_kind;      /* TRAINER_* below */
    int soldier_id;        /* valid when trainer_kind == TRAINER_SOLDIER */
    Monster bench[2];
    int bench_n;
    int catch_full;
} Battle;

#define TRAINER_WILD     0
#define TRAINER_SOLDIER  1
#define TRAINER_MASON    2
#define TRAINER_SHINIGAMI 3
#define TRAINER_CALDER   4
#define TRAINER_MASON2   5
#define TRAINER_WSOLDIER_CLIFFS 6
#define TRAINER_WSOLDIER_CAMP1  7
#define TRAINER_WSOLDIER_CAMP2  8
#define TRAINER_WSOLDIER_GROVE  9
#define TRAINER_WSOLDIER_RANGER 10
#define TRAINER_WSOLDIER_SCOUT  11
#define TRAINER_WSOLDIER_KEEPER 12
#define TRAINER_WSOLDIER_WARDEN 13
#define TRAINER_WSOLDIER_QUARTZ 14
#define TRAINER_WSOLDIER_QUARRY_DRILLER 15
#define TRAINER_WSOLDIER_OPAL 16
#define TRAINER_WSOLDIER_MARSH_BOG 17
#define TRAINER_WSOLDIER_MARSH_REED 18
#define TRAINER_WSOLDIER_COMMANDER_FINAL 19
#define TRAINER_WSOLDIER_LEAD 20
#define TRAINER_WSOLDIER_HEAVENFALL_GRAVE 21

#define BAFTER_ITEM      1
#define BAFTER_ATK       2
#define BAFTER_GUARD     3
#define BAFTER_WIN       5
#define BAFTER_WORLD     6
#define BAFTER_LOSS      7
#define BAFTER_WIN_NOTE  9

static int battle_foe_debuffed(const Battle *b) {
    return b->mods_foe_str < 0 || b->mods_foe_agl < 0 || b->mods_foe_spc < 0 ||
           b->stage_foe_str > 0 || b->stage_foe_agl > 0 || b->stage_foe_spc > 0;
}
/* selfDebuffed(): mirror of the above, checked from the foe's side of
   castSpell's Mana Surge branch (whether the *player* is debuffed
   decides the foe's 2x multiplier and their 55% chance to prioritize
   casting it -- see battle_pick_guard's Cathleen branch below). */
static int battle_self_debuffed(const Battle *b) {
    return b->mods_self_str < 0 || b->mods_self_agl < 0 || b->mods_self_spc < 0 ||
           b->stage_self_str > 0 || b->stage_self_agl > 0 || b->stage_self_spc > 0;
}
/* Capture-only: a stat debuff OR any status condition counts as
   "vulnerable" for the crystal's flat +50, matching every capture
   item's own description text ("Status adds +50"). Kept separate from
   battle_foe_debuffed() itself, which Mana Surge's own 2x-damage check
   also reads -- status conditions shouldn't widen that unrelated
   mechanic just because they now count here. */
static int battle_foe_vulnerable(const Battle *b) {
    return battle_foe_debuffed(b) || b->foe.status != STATUS_NONE;
}
static int battle_capture_chance(const Battle *b, int base) {
    return capture_chance(b->foe.lv, b->foe.str, b->foe.hp, battle_foe_vulnerable(b), base);
}

/* Cathleen's spell kit (castSpell()): the only species in data.ts with
   a `spells` list, so this only ever fires for her, on either side of
   the fight (as the player's own captured lead, or as the wild foe).
   from_player picks which side's mods get debuffed by the elemental
   spells and, for Mana Surge, which side's debuff state doubles the
   damage. Returns 0 (and leaves *out_dmg/out_label untouched) only for
   a spent-PP Mana Surge cast, matching castSpell()'s early return
   there. */
#define SPELL_FIREBOLT  0
#define SPELL_ICEBEAM   1
#define SPELL_LIGHTNING 2
#define SPELL_MANASURGE 3
/* Every spell is Magic (see SPELLS[] -- baked from species.json's
   spells[].stat), so caster->spc is always the right stat here. Damage is
   the same atkStat*power formula every other move uses (SPELLS[spell_id]
   supplies the power); the three elemental bolts keep their stat-debuff
   side effect and Mana Surge keeps its doubled-when-debuffed multiplier,
   both untouched by the formula rewrite -- those are move-specific
   effects layered on top of the shared damage core, not part of it. */
static int battle_cast_spell(Battle *b, int spell_id, int from_player, int *out_dmg, char *out_label) {
    Monster *caster = from_player ? &b->pl : &b->foe;
    int dmg = 0, n = 0;
    char label[40];

    if(spell_id == SPELL_FIREBOLT) {
        if(from_player) b->mods_foe_str -= 4; else b->mods_self_str -= 4;
        dmg = jground((float)caster->spc * SPELLS[SPELL_FIREBOLT].power);
        if(dmg < 1) dmg = 1;
        n = s_cat(label, 0, "FIRE BOLT  STR-4");
    }
    else if(spell_id == SPELL_ICEBEAM) {
        if(from_player) b->mods_foe_agl -= 4; else b->mods_self_agl -= 4;
        dmg = jground((float)caster->spc * SPELLS[SPELL_ICEBEAM].power);
        if(dmg < 1) dmg = 1;
        n = s_cat(label, 0, "ICE BEAM  AGI-4");
    }
    else if(spell_id == SPELL_LIGHTNING) {
        if(from_player) b->mods_foe_spc -= 4; else b->mods_self_spc -= 4;
        dmg = jground((float)caster->spc * SPELLS[SPELL_LIGHTNING].power);
        if(dmg < 1) dmg = 1;
        n = s_cat(label, 0, "LIGHTNING STRIKE  MAG-4");
    }
    else {
        int debuffed;
        float mul;
        if(caster->spp <= 0) return 0;
        caster->spp--;
        debuffed = from_player ? battle_foe_debuffed(b) : battle_self_debuffed(b);
        mul = debuffed ? 2.0f : 1.0f;
        dmg = jground((float)caster->spc * SPELLS[SPELL_MANASURGE].power * mul);
        if(dmg < 1) dmg = 1;
        n = s_cat(label, 0, debuffed ? "MANA SURGE  2X" : "MANA SURGE");
    }
    label[n] = 0;
    { int i; for(i = 0; label[i]; i++) out_label[i] = label[i]; out_label[i] = 0; }
    *out_dmg = dmg;
    return 1;
}

/* Crystal matchup between two party/foe natures. Returns +1 when the
   attacker's crystal splits the defender's, -1 when it is split by it, 0
   for neutral. Ring position and the reach come from content/logic.json
   via content_logic.inc, so the web port uses the same table. */
static int nature_matchup(int atk_nat, int def_nat) {
    int a, d, step;
    if(atk_nat < 0 || atk_nat >= NATURE_N || def_nat < 0 || def_nat >= NATURE_N)
        return 0;
    a = NATURES[atk_nat].ring;
    d = NATURES[def_nat].ring;
    step = d - a;
    if(step < 0) step += NATURE_RING_N;
    if(step >= 1 && step <= NATURE_BEATS_AHEAD) return 1;
    if(step >= NATURE_RING_N - NATURE_BEATS_AHEAD) return -1;
    return 0;
}

static int nature_scale_dmg(int dmg, int atk_nat, int def_nat, int *out_sign) {
    int sign = nature_matchup(atk_nat, def_nat);
    if(out_sign) *out_sign = sign;
    if(sign > 0)      dmg = jground((float)dmg * NATURE_STRONG_MUL);
    else if(sign < 0) dmg = jground((float)dmg * NATURE_WEAK_MUL);
    if(dmg < 1) dmg = 1;
    return dmg;
}

/* Uniform-ish float in [lo, hi], built on irand() so it shares the same
   rng_state every other roll in this file uses. Used by the Dodge/Block/
   Barrier resolution below, which needs a random multiplier rather than a
   random int. */
static float frand(float lo, float hi) {
    return lo + (hi - lo) * ((float)irand(0, 1000) / 1000.0f);
}

/* Shared bench-swap-or-win tail for whenever the foe's hp drops to 0 or
   below, whether from a normal hit (battle_apply_hit) or a Parried counter-
   blow (battle_pick_guard). Assumes the caller already wrote the turn's
   hit-description line into b->msg[0]; fallen_prefix lets the caller mark a
   parry-kill in msg[1] ("PARRIED! X FALLS") without a 4th message slot.
   Returns 1 if it took over b->msg/phase/after (caller should return
   immediately), 0 if the foe is still standing. */
static int battle_foe_maybe_fall(Battle *b, const char *fallen_prefix) {
    int n;
    if(b->foe.hp > 0) return 0;
    if(b->bench_n > 0) {
        /* Shinigami's fight, and Mason's rematch too -- the two nbench > 0
           fights. Grants XP for the fallen bench member (unlike the final
           win, which grants XP once the whole fight ends), swaps the next
           bench monster in, and clears the foe-side stat mods, matching
           applyHit's bench branch. */
        char fallen[24];
        int fn = s_cat(fallen, 0, SPECIES[b->foe.species].name);
        fallen[fn] = 0;

        if(g_xp_party) {
            g_xp_party[g_xp_lead] = b->pl;
            grant_party_xp(g_xp_party, g_xp_party_n, g_xp_lead, b->foe.lv);
            b->pl = g_xp_party[g_xp_lead];
        } else {
            grant_xp(&b->pl, b->foe.lv, 100);
        }
        b->foe = b->bench[0];
        if(b->bench_n == 2) b->bench[0] = b->bench[1];
        b->bench_n--;
        b->mods_foe_str = b->mods_foe_agl = b->mods_foe_spc = 0;
        b->pend_str = b->pend_agl = b->pend_spc = 0;
        b->foe_poisoned = 0; /* fresh bench monster, not the fallen one */
        b->stage_foe_str = b->stage_foe_agl = b->stage_foe_spc = 0;
        b->hype_foe = 0;
        b->nmove_foe_used = b->hype_foe_used = 0;

        n = s_cat(b->msg[1], 0, fallen_prefix);
        n = s_cat(b->msg[1], n, fallen);
        n = s_cat(b->msg[1], n, " FALLS");
        b->msg[1][n] = 0;

        n = s_cat(b->msg[2], 0,
                  b->trainer_kind == TRAINER_MASON2 ? "MASON SENDS " : "SHINIGAMI SENDS ");
        n = s_cat(b->msg[2], n, SPECIES[b->foe.species].name);
        b->msg[2][n] = 0;

        b->msg_n = 3; b->msg_i = 0; b->phase = 0; b->after = BAFTER_ITEM;
        return 1;
    }
    n = s_cat(b->msg[1], 0, fallen_prefix);
    n = s_cat(b->msg[1], n, SPECIES[b->foe.species].name);
    n = s_cat(b->msg[1], n, " FALLS");
    b->msg[1][n] = 0;
    b->msg_n = 2; b->msg_i = 0; b->phase = 0; b->after = BAFTER_WIN;
    return 1;
}

/* Leg 2.11: stage-based stat drops + real status conditions, replacing
 * the old flat mods-only secondary moves and TOXIC BURST's hardcoded
 * poison. Mirrors src/game/engine.ts's effStat()/tickStatus()/
 * inflictStatus()/confusionOutcome() -- keep the two in sync. */
static int eff_stat(int base, int stage, int hyped) {
    int v;
    if(stage >= STAT_STAGE_MAX) v = STAT_STAGE_FLOOR;
    else v = jground((float)base * STAT_STAGE_MULT[stage]);
    if(hyped) v += jground((float)base * (float)HYPE_UP_PCT / 100.0f);
    return v;
}
static int dmg_stat_pl(const Battle *b, int stat) {
    if(stat == ATK_STR) return eff_stat(b->pl.str, b->stage_self_str, b->hype_self) + b->mods_self_str;
    return eff_stat(b->pl.spc, b->stage_self_spc, b->hype_self) + b->mods_self_spc;
}
static int dmg_stat_foe(const Battle *b, int stat) {
    if(stat == ATK_STR) return eff_stat(b->foe.str, b->stage_foe_str, b->hype_foe) + b->mods_foe_str;
    return eff_stat(b->foe.spc, b->stage_foe_spc, b->hype_foe) + b->mods_foe_spc;
}
static int eff_agl_pl(const Battle *b) {
    return eff_stat(b->pl.agl, b->stage_self_agl, b->hype_self) + b->mods_self_agl;
}
static int eff_agl_foe(const Battle *b) {
    return eff_stat(b->foe.agl, b->stage_foe_agl, b->hype_foe) + b->mods_foe_agl;
}
static void clear_status(Monster *m) {
    m->status = STATUS_NONE;
    m->status_turns = 0;
    m->poison_stack = 0;
}
static void inflict_status(Monster *m, int status) {
    m->status = status;
    m->poison_stack = 0;
    if(status == STATUS_BURNED) m->status_turns = irand(STATUS_BURN_TURNS_MIN, STATUS_BURN_TURNS_MAX);
    else if(status == STATUS_PARALYZED) m->status_turns = irand(STATUS_PARALYZE_TURNS_MIN, STATUS_PARALYZE_TURNS_MAX);
    else m->status_turns = 0;
}
/* One status tick (HP drain + turn countdown), once per side per round --
   called from battle_apply_hit() (foe's status, player's turn) and
   battle_pick_guard() (player's status, foe's turn), same placement as
   the old poison-only tick this replaces. Appends " BURN-N"/" PSN-N" to
   buf at n, returns the new n (unchanged if nothing happened). */
static int tick_status(Monster *m, char *buf, int n) {
    if(m->status == STATUS_NONE || m->hp <= 0) return n;
    if(m->status == STATUS_BURNED) {
        int tick = m->maxHp * STATUS_BURN_PCT / 100;
        if(tick < 1) tick = 1;
        m->hp -= tick;
        if(m->hp < 0) m->hp = 0;
        m->status_turns--;
        if(m->status_turns <= 0) clear_status(m);
        n = s_cat(buf, n, " BURN-");
        n = s_cat_uint(buf, n, tick);
        return n;
    }
    if(m->status == STATUS_POISONED) {
        int pct, tick;
        m->poison_stack++;
        pct = STATUS_POISON_START_PCT + (m->poison_stack - 1) * STATUS_POISON_STEP_PCT;
        tick = m->maxHp * pct / 100;
        if(tick < 1) tick = 1;
        m->hp -= tick;
        if(m->hp < 0) m->hp = 0;
        n = s_cat(buf, n, " PSN-");
        n = s_cat_uint(buf, n, tick);
        return n;
    }
    if(m->status == STATUS_PARALYZED) {
        m->status_turns--;
        if(m->status_turns <= 0) clear_status(m);
        return n;
    }
    return n;
}
/* Confusion's 4-way roll (0 normal / 1 none / 2 self / 3 ally), mirroring
   confusionOutcome() in engine.ts. self_dmg is the confused CryMon's own
   basic-power self-hit; ally_idx/has_ally describe the bench-hit case
   (self=1: player's own party bench via g_xp_party; self=0: b->bench[]) --
   caller resolves ally_idx into an actual HP change, this just rolls. */
typedef struct { int kind; int dmg; int ally_idx; } ConfuseRoll;
#define CONFUSE_NORMAL 0
#define CONFUSE_NONE 1
#define CONFUSE_SELF 2
#define CONFUSE_ALLY 3
static ConfuseRoll confusion_roll(const Monster *m, int has_ally, int ally_n, const int *ally_hp, int ally_cap) {
    ConfuseRoll r;
    int roll;
    (void)ally_cap;
    r.kind = CONFUSE_NORMAL;
    r.dmg = 0;
    r.ally_idx = -1;
    if(m->status != STATUS_CONFUSED) return r;
    roll = irand(0, 3);
    if(roll == 0) return r;
    if(roll == 1) { r.kind = CONFUSE_NONE; return r; }
    r.dmg = jground((float)m->str * SPECIES[m->species].basic_power);
    if(r.dmg < 1) r.dmg = 1;
    if(roll == 2 || !has_ally) { r.kind = CONFUSE_SELF; return r; }
    {
        int i, n = 0, choices[6];
        for(i = 0; i < ally_n; i++) if(ally_hp[i] > 0) choices[n++] = i;
        if(!n) { r.kind = CONFUSE_SELF; return r; }
        r.kind = CONFUSE_ALLY;
        r.ally_idx = choices[irand(0, n - 1)];
        return r;
    }
}

static void battle_apply_hit(Battle *b) {
    int n = 0;
    int nat_sign = 0;
    char tick_buf[24];
    int tick_n;

    tick_n = tick_status(&b->foe, tick_buf, 0);
    tick_buf[tick_n] = 0;

    if(b->dmg > 0) {
        /* Crystal matchup, applied once here rather than in each of the
           move branches that feed this, so every player attack is scaled
           exactly once and by the same rule the foe's attacks get in
           battle_pick_guard(). */
        b->dmg = nature_scale_dmg(b->dmg, species_nature(b->pl.species),
                                  species_nature(b->foe.species), &nat_sign);
        b->foe.hp -= b->dmg;
        if(b->foe.hp < 0) b->foe.hp = 0;
        n = s_cat(b->msg[0], 0, b->label);
        n = s_cat(b->msg[0], n, " ");
        n = s_cat_uint(b->msg[0], n, b->dmg);
        n = s_cat(b->msg[0], n, " DMG");
        if(nat_sign > 0)      n = s_cat(b->msg[0], n, " " NATURE_STRONG_TEXT);
        else if(nat_sign < 0) n = s_cat(b->msg[0], n, " " NATURE_WEAK_TEXT);
    } else {
        /* Leg 2.11: a stage/status/hype move -- no damage, just the
           effect text battle_pick_nmove()/battle_pick_hype() staged in
           b->pend_effect before calling here. */
        n = s_cat(b->msg[0], 0, b->label);
        if(b->pend_effect[0]) {
            n = s_cat(b->msg[0], n, " ");
            n = s_cat(b->msg[0], n, b->pend_effect);
        }
    }
    n = s_cat(b->msg[0], n, tick_buf);
    b->pend_effect[0] = 0;
    b->msg[0][n] = 0;

    if(battle_foe_maybe_fall(b, "")) return;

    n = s_cat(b->msg[1], 0, "FOE ANSWERS CHOOSE A GUARD");
    b->msg[1][n] = 0;
    b->msg_n = 2; b->msg_i = 0; b->phase = 0; b->after = BAFTER_GUARD;
}

/* Raw stat a move draws on (str or mag), mods included -- the one shared
   lookup every attacker-side move (basic/special/spell) and every
   guard-side foe move go through. Leg 2.11: nmove/hype moves bypass this
   entirely (they deal no damage), and basic/special now fold in stage/
   hype via dmg_stat_pl()/dmg_stat_foe() instead of calling this directly
   with raw mods -- kept for the two guard-defense reads (block/barrier
   scores) that still want the player's own raw-ish stat. */
static int atk_stat_value(const Monster *m, int mods_str, int mods_agl, int mods_spc, int stat) {
    (void)mods_agl;
    return stat == ATK_STR ? m->str + mods_str : m->spc + mods_spc;
}

static const char *const STATUS_NAME[6] = { "", "BURNED", "POISONED", "CONFUSED", "PARALYZED", "EXHAUSTED" };

/* pickAtk's basic-move branch. Only reached for a non-spellcaster
   lead -- see battle_pick_spell() further down for Cathleen's own
   branch, dispatched separately in main()'s battle-phase-2 handling.
   Damage is the shared formula every move now uses: atkStat * power,
   no defense term -- what the defender eats is decided entirely at the
   guard step (Dodge/Block/Barrier), not baked into the attack. */
static void battle_pick_umove(Battle *b, const UMove *mv) {
    int atk, n = 0;
    atk = dmg_stat_pl(b, mv->stat);
    b->dmg = jground((float)atk * mv->power);
    if(b->dmg < 1) b->dmg = 1;
    n = s_cat(b->label, n, mv->name);
    b->label[n] = 0;
    battle_apply_hit(b);
}

/* Leg 2.11: the crystal secondary (or Overload for a shiny lead) -- a
   stage drop on one foe stat, or a status condition, never damage.
   PP is battle-scoped (see Battle.nmove_pl_used), gated by the caller
   (main()'s phase-2 dispatch) before this ever runs. */
static void battle_pick_nmove(Battle *b, const UMove *mv) {
    int n = 0;
    b->nmove_pl_used++;
    b->dmg = 0;
    n = s_cat(b->label, 0, mv->name);
    b->label[n] = 0;
    if(mv->move_kind == NMOVE_KIND_STAGE) {
        int *stage = mv->stat_target == STAT_STR ? &b->stage_foe_str
                    : mv->stat_target == STAT_AGL ? &b->stage_foe_agl : &b->stage_foe_spc;
        if(*stage < STAT_STAGE_MAX) (*stage)++;
        n = s_cat(b->pend_effect, 0, mv->stat_target == STAT_STR ? "STR FALLS"
                                     : mv->stat_target == STAT_AGL ? "AGL FALLS" : "MAG FALLS");
        b->pend_effect[n] = 0;
    } else {
        inflict_status(&b->foe, mv->status_target);
        n = s_cat(b->pend_effect, 0, STATUS_NAME[mv->status_target]);
        b->pend_effect[n] = 0;
    }
    battle_apply_hit(b);
}

/* Leg 2.11: Hype Up -- self-buff, all 3 stats, lasts until battle end. */
static void battle_pick_hype(Battle *b, const UMove *mv) {
    int n = 0;
    b->hype_pl_used++;
    b->hype_self = 1;
    b->dmg = 0;
    n = s_cat(b->label, 0, mv->name);
    b->label[n] = 0;
    n = s_cat(b->pend_effect, 0, "STATS UP");
    b->pend_effect[n] = 0;
    battle_apply_hit(b);
}

/* Leg 2.11: paralysis/confusion intercept for the player's own turn,
   called from main()'s phase-2 input dispatch before it looks at
   battle.cur/mv at all. Returns 1 if it took over battle.msg/phase/after
   (caller must not dispatch the chosen move), 0 if the player's turn
   proceeds normally. The turn-countdown/HP-tick itself happens once per
   round in battle_pick_guard(), not here -- this only checks and
   bypasses, mirroring pickAttack()'s intercept in engine.ts. */
static int battle_pl_status_intercept(Battle *b, Monster *party, int party_n, int lead) {
    if(b->pl.status == STATUS_PARALYZED) {
        int n = s_cat(b->msg[0], 0, g_player_name);
        n = s_cat(b->msg[0], n, " IS PARALYZED AND CANT MOVE");
        b->msg[0][n] = 0;
        b->msg_n = 1; b->msg_i = 0; b->phase = 0; b->after = BAFTER_GUARD;
        return 1;
    }
    if(b->pl.status == STATUS_CONFUSED) {
        int party_hp[6], pi, n;
        ConfuseRoll cr;
        for(pi = 0; pi < party_n && pi < 6; pi++) party_hp[pi] = (pi == lead) ? 0 : party[pi].hp;
        cr = confusion_roll(&b->pl, party_n > 1, party_n < 6 ? party_n : 6, party_hp, 6);
        if(cr.kind == CONFUSE_NORMAL) return 0;
        n = s_cat(b->msg[0], 0, g_player_name);
        if(cr.kind == CONFUSE_NONE) {
            n = s_cat(b->msg[0], n, " IS TOO CONFUSED TO ACT");
        } else if(cr.kind == CONFUSE_SELF) {
            int d = cr.dmg;
            if(d > b->pl.hp - 1) d = b->pl.hp - 1;
            if(d < 0) d = 0;
            b->pl.hp -= d;
            if(b->pl.hp < 1) b->pl.hp = 1;
            n = s_cat(b->msg[0], n, " IS CONFUSED AND HITS ITSELF");
        } else {
            party[cr.ally_idx].hp -= cr.dmg;
            if(party[cr.ally_idx].hp < 0) party[cr.ally_idx].hp = 0;
            n = s_cat(b->msg[0], n, " IS CONFUSED AND HITS AN ALLY");
        }
        b->msg[0][n] = 0;
        b->msg_n = 1; b->msg_i = 0; b->phase = 0; b->after = BAFTER_GUARD;
        return 1;
    }
    return 0;
}

static void battle_pick_special(Battle *b) {
    const Species *s = &SPECIES[b->pl.species];
    int atk = atk_stat_value(&b->pl, b->mods_self_str, b->mods_self_agl, b->mods_self_spc, s->special_stat);
    float mul = SPEC_MUL_FIZZ;
    const char *tag = "FIZZLED";
    int n = 0;

    if(b->mg >= SPEC_PERFECT_LO && b->mg <= SPEC_PERFECT_HI) {
        mul = SPEC_MUL_PERFECT;
        tag = "PERFECT";
    } else if(b->mg >= SPEC_CONN_LO && b->mg <= SPEC_CONN_HI) {
        mul = SPEC_MUL_CONN;
        tag = "CONNECTED";
    }

    b->dmg = jground((float)atk * s->special_power * mul);
    if(b->dmg < 1) b->dmg = 1;

    n = s_cat(b->label, n, s->special);
    n = s_cat(b->label, n, " ");
    n = s_cat(b->label, n, tag);
    b->label[n] = 0;
    battle_apply_hit(b);
}

/* pickAttack()'s spell branch: for a Cathleen lead, every attack-menu
   row is a direct spell cast (no minigame, no separate guard row --
   her attackMenu() is just her 4 spell names, matching data.ts). Does
   nothing if the row was Mana Surge with no PP left, same as
   castSpell()'s early return (the message/phase change that produces
   is handled by the caller, matching pickAttack's own silent-return
   there). */
static int battle_pick_spell(Battle *b, int spell_id) {
    int dmg;
    char label[40];
    b->pend_str = b->pend_agl = b->pend_spc = 0;
    if(!battle_cast_spell(b, spell_id, 1, &dmg, label))
        return 0;
    b->dmg = dmg;
    { int i; for(i = 0; label[i]; i++) b->label[i] = label[i]; b->label[i] = 0; }
    battle_apply_hit(b);
    return 1;
}

/* pickGuard(): the foe picks its own move (28% chance of its special if
   it has spp left, otherwise basic). Guard resolution has no percentage
   roll any more -- see content/logic.json's combat block:
     Dodge:   a speed contest. attackerScore = foe's agl * the move's
              speed rating; defenderScore = player's agl * a random
              0.75-1.25x. attackerScore - defenderScore > 0 lands the hit
              anyway; <= 0 the dodge succeeds outright.
     Block:   blockScore = player's str * a random 0.25-0.75x, subtracted
              from the incoming (matchup-scaled) damage. Reduced to 0 or
              below and it's Parried -- the player takes nothing and the
              FOE takes the full damage it would have dealt, which can
              itself end the fight (battle_foe_maybe_fall() handles that).
     Barrier: same shape off the player's mag, but a full negate is
              Absorbed instead of reflected -- the player heals half the
              would-be damage rather than dealing it back.
   Needs the live party array to resolve a faint the same way state.lua
   does inline: swap in the next living member if one exists (message
   becomes "<line>" + "<name> JUMPS IN", battle continues at the item
   menu) or end the battle if none do ("<line>" + "<name> CANNOT STAND",
   BAFTER_LOSS). */
static void battle_pick_guard(Battle *b, int kind, Monster *party, int party_n, int *lead) {
    const Species *foe_sp = &SPECIES[b->foe.species];
    char move_name_buf[40];
    const char *move_name = "";
    int atk_stat_raw = 0, dmg = 0, counter_dmg = 0;
    float move_power = 1.0f, move_speed = 1.0f;
    char line[96];
    char effect_text[24];
    char self_tick[24];
    int self_tick_n;
    int n = 0;
    int nat_sign = 0;
    int landed = 1;
    UMove umoves[UMOVE_MAX];
    int un, ui, pick_i = 0;
    int n_special = 0, n_nmove = 0, n_hype = 0, n_basic = 0;
    int specials[UMOVE_MAX], nmoves_idx[UMOVE_MAX], hypes_idx[UMOVE_MAX], basics[UMOVE_MAX];
    const UMove *pick;

    effect_text[0] = 0;
    line[0] = 0;
    self_tick_n = tick_status(&b->pl, self_tick, 0);
    self_tick[self_tick_n] = 0;

    if(b->pl.hp <= 0) {
        /* The status tick itself (burn/poison) just finished the player
           off before the foe even got to act -- same swap-or-lose branch
           the foe's attack uses further down, just reached earlier. */
        int i, nxt = -1;
        for(i = 0; i < party_n; i++)
            if(i != *lead && party[i].hp > 0) { nxt = i; break; }

        n = s_cat(b->msg[0], 0, SPECIES[b->pl.species].name);
        n = s_cat(b->msg[0], n, self_tick);
        b->msg[0][n] = 0;

        if(nxt >= 0) {
            *lead = nxt;
            b->pl = party[nxt];
            b->mods_self_str = b->mods_self_agl = b->mods_self_spc = 0;
            b->stage_self_str = b->stage_self_agl = b->stage_self_spc = 0;
            b->hype_self = 0;
            b->nmove_pl_used = b->hype_pl_used = 0;            n = s_cat(b->msg[1], 0, SPECIES[b->pl.species].name);
            n = s_cat(b->msg[1], n, " JUMPS IN");
            b->msg[1][n] = 0;
            b->msg_n = 2; b->msg_i = 0; b->phase = 0; b->after = BAFTER_ITEM;
        }
        else {
            n = s_cat(b->msg[1], 0, SPECIES[b->pl.species].name);
            n = s_cat(b->msg[1], n, " CANNOT STAND");
            b->msg[1][n] = 0;
            b->msg_n = 2; b->msg_i = 0; b->phase = 0; b->after = BAFTER_LOSS;
        }
        return;
    }

    if(b->foe.status == STATUS_PARALYZED) {
        b->foe.status_turns--;
        if(b->foe.status_turns <= 0) clear_status(&b->foe);
        n = s_cat(b->msg[0], 0, SPECIES[b->foe.species].name);
        n = s_cat(b->msg[0], n, " IS PARALYZED");
        n = s_cat(b->msg[0], n, self_tick);
        b->msg[0][n] = 0;
        b->msg_n = 1; b->msg_i = 0; b->phase = 0; b->after = BAFTER_ITEM;
        return;
    }
    {
        int ally_hp[2];
        int ai;
        ConfuseRoll cr;
        for(ai = 0; ai < b->bench_n && ai < 2; ai++) ally_hp[ai] = b->bench[ai].hp;
        cr = confusion_roll(&b->foe, b->bench_n > 0, b->bench_n, ally_hp, 2);
        if(cr.kind != CONFUSE_NORMAL) {
            if(cr.kind == CONFUSE_NONE) {
                n = s_cat(b->msg[0], 0, SPECIES[b->foe.species].name);
                n = s_cat(b->msg[0], n, " IS TOO CONFUSED TO ACT");
            } else if(cr.kind == CONFUSE_SELF) {
                int d = cr.dmg;
                if(d > b->foe.hp - 1) d = b->foe.hp - 1;
                if(d < 0) d = 0;
                b->foe.hp -= d;
                if(b->foe.hp < 1) b->foe.hp = 1;
                n = s_cat(b->msg[0], 0, SPECIES[b->foe.species].name);
                n = s_cat(b->msg[0], n, " IS CONFUSED AND HITS ITSELF");
            } else {
                b->bench[cr.ally_idx].hp -= cr.dmg;
                if(b->bench[cr.ally_idx].hp < 0) b->bench[cr.ally_idx].hp = 0;
                n = s_cat(b->msg[0], 0, SPECIES[b->foe.species].name);
                n = s_cat(b->msg[0], n, " IS CONFUSED AND HITS AN ALLY");
            }
            n = s_cat(b->msg[0], n, self_tick);
            b->msg[0][n] = 0;
            b->msg_n = 1; b->msg_i = 0; b->phase = 0; b->after = BAFTER_ITEM;
            return;
        }
    }

    un = unlocked_moves(&b->foe, 0, umoves, UMOVE_MAX);
    for(ui = 0; ui < un; ui++) {
        if(umoves[ui].kind == UMOVE_SPECIAL ||
           (umoves[ui].kind == UMOVE_SPELL && umoves[ui].spell_id == SPELL_MANASURGE))
            specials[n_special++] = ui;
        else if(umoves[ui].kind == UMOVE_NMOVE && b->nmove_foe_used < umoves[ui].max_pp)
            nmoves_idx[n_nmove++] = ui;
        else if(umoves[ui].kind == UMOVE_HYPE && b->hype_foe_used < umoves[ui].max_pp)
            hypes_idx[n_hype++] = ui;
        else if(umoves[ui].kind != UMOVE_NMOVE && umoves[ui].kind != UMOVE_HYPE)
            basics[n_basic++] = ui;
    }
    if(n_basic) pick_i = basics[irand(0, n_basic - 1)];
    if(n_special && b->foe.spp > 0 && irand(0, 99) < 28) {
        pick_i = specials[irand(0, n_special - 1)];
    } else if(n_hype && !b->hype_foe && irand(0, 99) < 15) {
        pick_i = hypes_idx[0];
    } else if(n_nmove && irand(0, 99) < 35) {
        pick_i = nmoves_idx[irand(0, n_nmove - 1)];
    } else if(n_basic) {
        pick_i = basics[irand(0, n_basic - 1)];
    }
    if(b->foe.lv >= LV_SPECIAL && foe_sp->spells_n > 0 &&
       battle_self_debuffed(b) && b->foe.spp > 0 && irand(0, 99) < 55) {
        for(ui = 0; ui < un; ui++)
            if(umoves[ui].kind == UMOVE_SPELL && umoves[ui].spell_id == SPELL_MANASURGE)
                pick_i = ui;
    }
    pick = &umoves[pick_i];
    if(pick->kind == UMOVE_SPELL) {
        int spell_id = pick->spell_id;
        if(battle_cast_spell(b, spell_id, 0, &dmg, move_name_buf)) {
            move_name = move_name_buf;
        } else {
            dmg = 1;
            move_name = SPELL_MENU_NAME[spell_id];
        }
        move_speed = SPELLS[spell_id].speed;
        goto guard_resolve;
    }
    if(pick->kind == UMOVE_SPECIAL) {
        b->foe.spp--;
        atk_stat_raw = dmg_stat_foe(b, pick->stat);
        move_power = pick->power;
        move_speed = pick->speed;
        move_name = pick->name;
        dmg = jground((float)atk_stat_raw * move_power);
        if(dmg < 1) dmg = 1;
    } else if(pick->kind == UMOVE_NMOVE) {
        b->nmove_foe_used++;
        move_name = pick->name;
        move_speed = pick->speed;
        dmg = 0;
        if(pick->move_kind == NMOVE_KIND_STAGE) {
            n = s_cat(effect_text, 0, pick->stat_target == STAT_STR ? "STR FALLS"
                                     : pick->stat_target == STAT_AGL ? "AGL FALLS" : "MAG FALLS");
        } else {
            n = s_cat(effect_text, 0, STATUS_NAME[pick->status_target]);
        }
        effect_text[n] = 0;
    } else if(pick->kind == UMOVE_HYPE) {
        /* Self-buff -- always applies regardless of the player's guard
           choice, unlike an nmove aimed at the player (landed, below). */
        b->hype_foe_used++;
        b->hype_foe = 1;
        move_name = pick->name;
        move_speed = pick->speed;
        dmg = 0;
        n = s_cat(effect_text, 0, "STATS UP");
        effect_text[n] = 0;
    } else {
        atk_stat_raw = dmg_stat_foe(b, pick->stat);
        move_power = pick->power;
        move_speed = pick->speed;
        move_name = pick->name;
        dmg = jground((float)atk_stat_raw * move_power);
        if(dmg < 1) dmg = 1;
    }

guard_resolve:
    /* Crystal matchup on the incoming hit, before the guard reduces it: the
       matchup decides how hard the blow lands, the guard decides how much of
       it the player eats. Zero-damage nmove/hype moves scale to 0 harmlessly. */
    dmg = nature_scale_dmg(dmg, species_nature(b->foe.species),
                           species_nature(b->pl.species), &nat_sign);

    if(kind == 0) {
        /* Dodge: a speed contest, not a percentage roll. The move's own
           speed rating only matters for the attacker's side; the
           defender's is a flat random reaction roll off raw agility. */
        float atk_speed = (float)eff_agl_foe(b) * move_speed;
        float def_speed = (float)eff_agl_pl(b)
                           * frand(DODGE_DEF_RAND_MIN, DODGE_DEF_RAND_MAX);
        if(atk_speed - def_speed > 0.0f) {
            if(dmg > 0) {
                n = s_cat(line, 0, "THE DODGE FAILS ");
                n = s_cat_uint(line, n, dmg);
                n = s_cat(line, n, " DMG");
            } else {
                n = s_cat(line, 0, "THE DODGE FAILS");
            }
        }
        else {
            dmg = 0;
            landed = 0;
            n = s_cat(line, 0, SPECIES[b->pl.species].name);
            n = s_cat(line, n, " SLIPS ASIDE");
        }
    }
    else if(kind == 1) {
        int block_score = jground((float)dmg_stat_pl(b, ATK_STR) * frand(GUARD_RAND_MIN, GUARD_RAND_MAX));
        int reduced = dmg - block_score;
        if(reduced <= 0) {
            /* Parried: the player takes nothing, and the full blow that
               would have landed hits the foe instead -- possibly ending
               the fight right here, handled after this if-chain. */
            counter_dmg = dmg;
            dmg = 0;
            if(counter_dmg > 0) {
                n = s_cat(line, 0, GUARD_PARRIED_TEXT);
                n = s_cat(line, n, " FOE TAKES ");
                n = s_cat_uint(line, n, counter_dmg);
                n = s_cat(line, n, " DMG");
            }
        }
        else {
            dmg = reduced;
            n = s_cat(line, 0, "BLOCKED ");
            n = s_cat_uint(line, n, dmg);
            n = s_cat(line, n, " DMG LEAKS THROUGH");
        }
    }
    else {
        int barrier_score = jground((float)dmg_stat_pl(b, ATK_MAG) * frand(GUARD_RAND_MIN, GUARD_RAND_MAX));
        int reduced = dmg - barrier_score;
        if(reduced <= 0) {
            /* Absorbed: the player takes nothing and heals half of what
               would have landed instead. */
            int heal = dmg / BARRIER_HEAL_DIVISOR;
            dmg = 0;
            b->pl.hp += heal;
            if(b->pl.hp > b->pl.maxHp) b->pl.hp = b->pl.maxHp;
            if(heal > 0) {
                n = s_cat(line, 0, GUARD_ABSORBED_TEXT);
                n = s_cat(line, n, " +");
                n = s_cat_uint(line, n, heal);
                n = s_cat(line, n, " HP");
            }
        }
        else {
            dmg = reduced;
            n = s_cat(line, 0, "A THIN BARRIER HOLDS ");
            n = s_cat_uint(line, n, dmg);
            n = s_cat(line, n, " DMG");
        }
    }
    /* Only worth saying when something landed: a clean dodge/parry/absorb
       zeroes dmg, and a matchup tag on a hit that never connected reads as
       a contradiction. */
    if(dmg > 0) {
        if(nat_sign > 0)      n = s_cat(line, n, " " NATURE_STRONG_TEXT);
        else if(nat_sign < 0) n = s_cat(line, n, " " NATURE_WEAK_TEXT);
    }
    if(pick->kind == UMOVE_HYPE || (landed && pick->kind == UMOVE_NMOVE)) {
        if(pick->kind == UMOVE_NMOVE) {
            if(pick->move_kind == NMOVE_KIND_STAGE) {
                int *stage = pick->stat_target == STAT_STR ? &b->stage_self_str
                            : pick->stat_target == STAT_AGL ? &b->stage_self_agl : &b->stage_self_spc;
                if(*stage < STAT_STAGE_MAX) (*stage)++;
            } else {
                inflict_status(&b->pl, pick->status_target);
            }
        }
        if(n > 0) n = s_cat(line, n, " ");
        n = s_cat(line, n, effect_text);
    }
    line[n] = 0;

    b->pl.hp -= dmg;
    if(b->pl.hp < 0) b->pl.hp = 0;
    party[*lead] = b->pl;

    if(b->pl.hp <= 0) {
        int i, nxt = -1;
        for(i = 0; i < party_n; i++)
            if(i != *lead && party[i].hp > 0) { nxt = i; break; }

        n = s_cat(b->msg[0], 0, line);
        n = s_cat(b->msg[0], n, self_tick);
        b->msg[0][n] = 0;

        if(nxt >= 0) {
            *lead = nxt;
            b->pl = party[nxt];
            b->mods_self_str = b->mods_self_agl = b->mods_self_spc = 0;
            b->stage_self_str = b->stage_self_agl = b->stage_self_spc = 0;
            b->hype_self = 0;
            b->nmove_pl_used = b->hype_pl_used = 0;
            n = s_cat(b->msg[1], 0, SPECIES[b->pl.species].name);
            n = s_cat(b->msg[1], n, " JUMPS IN");
            b->msg[1][n] = 0;
            b->msg_n = 2; b->msg_i = 0; b->phase = 0; b->after = BAFTER_ITEM;
        }
        else {
            n = s_cat(b->msg[1], 0, SPECIES[b->pl.species].name);
            n = s_cat(b->msg[1], n, " CANNOT STAND");
            b->msg[1][n] = 0;
            b->msg_n = 2; b->msg_i = 0; b->phase = 0; b->after = BAFTER_LOSS;
        }
        return;
    }

    n = s_cat(b->msg[0], 0, SPECIES[b->foe.species].name);
    n = s_cat(b->msg[0], n, " USES ");
    n = s_cat(b->msg[0], n, move_name);
    b->msg[0][n] = 0;

    /* A Parry's counter-blow can itself finish the foe -- msg[0] above is
       already set, so the shared helper only needs to fill msg[1] (and
       msg[2] on a bench swap) with the prefix marking it a Parry-kill. */
    if(counter_dmg > 0) {
        b->foe.hp -= counter_dmg;
        if(b->foe.hp < 0) b->foe.hp = 0;
        if(battle_foe_maybe_fall(b, "PARRIED! ")) return;
    }

    n = s_cat(b->msg[1], 0, line);
    n = s_cat(b->msg[1], n, self_tick);
    b->msg[1][n] = 0;
    b->msg_n = 2; b->msg_i = 0; b->phase = 0; b->after = BAFTER_ITEM;
}

/* Item menu kinds, matching fillItemMenu's row order (state.lua's
   "switch" row is skipped -- see the item-menu drawing/input code in
   main() for why). */
#define ITEM_PASS       0
#define ITEM_SALVE      1
#define ITEM_BANDAGE    2
#define ITEM_BITTERROOT 3
#define ITEM_DUST       4
#define ITEM_GEM        5
#define ITEM_SUNBALM      6
#define ITEM_WARROOT      7
#define ITEM_SMOKEBOMB    8
#define ITEM_GREATCRYSTAL 9

/* pickItem(): items (heal/buff/debuff) are "free" -- they route back
   to the attack menu (BAFTER_ATK), never to the guard phase, matching
   state.lua exactly (only an actual attack or Wait lets the foe act).
   A successful capture ends the battle outright (BAFTER_WORLD); every
   other outcome, including a failed capture, also returns to the
   attack menu. party/party_n are only touched by a successful
   capture. */
static void battle_pick_item(Battle *b, Bag *bag, int kind,
                              Monster *party, int *party_n, int lead) {
    int n = 0;
    int idx, heal;
    const ItemFx *fx;
    int *slot;

    if(kind == ITEM_PASS) {
        b->phase = 2;
        b->cur = 0;
        return;
    }

    idx = kind - 1;
    if(idx < 0 || idx >= ITEM_COUNT) {
        n = s_cat(b->msg[0], 0, "NOTHING HAPPENS");
        b->msg[0][n] = 0;
        b->msg_n = 1; b->msg_i = 0; b->phase = 0; b->after = BAFTER_ATK;
        party[lead] = b->pl;
        return;
    }
    fx = &ITEM_FX[idx];
    slot = bag_field(bag, idx);
    if(*slot <= 0) {
        n = s_cat(b->msg[0], 0, "NOTHING HAPPENS");
        b->msg[0][n] = 0;
        b->msg_n = 1; b->msg_i = 0; b->phase = 0; b->after = BAFTER_ATK;
        party[lead] = b->pl;
        return;
    }

    if(fx->kind == 1) { /* heal */
        heal = b->pl.maxHp - b->pl.hp;
        if(heal > fx->amount) heal = fx->amount;
        (*slot)--;
        b->pl.hp += heal;
        n = s_cat(b->msg[0], 0, ITEMS[idx].name);
        n = s_cat(b->msg[0], n, " ");
        n = s_cat_uint(b->msg[0], n, heal);
        n = s_cat(b->msg[0], n, " HP");
    }
    else if(fx->kind == 2) { /* buff */
        (*slot)--;
        b->mods_self_str += fx->str;
        b->mods_self_agl += fx->agl;
        b->mods_self_spc += fx->spc;
        n = s_cat(b->msg[0], 0, ITEMS[idx].name);
        if(fx->str) { n = s_cat(b->msg[0], n, " STR+"); n = s_cat_uint(b->msg[0], n, fx->str); n = s_cat(b->msg[0], n, " THIS FIGHT"); }
        else if(fx->agl) { n = s_cat(b->msg[0], n, " AGL+"); n = s_cat_uint(b->msg[0], n, fx->agl); n = s_cat(b->msg[0], n, " THIS FIGHT"); }
    }
    else if(fx->kind == 3) { /* debuff */
        (*slot)--;
        b->mods_foe_str += fx->str;
        b->mods_foe_agl += fx->agl;
        b->mods_foe_spc += fx->spc;
        n = s_cat(b->msg[0], 0, ITEMS[idx].name);
        n = s_cat(b->msg[0], n, " FOE STR");
        /* dust amounts are negative; print as written */
        n = s_cat(b->msg[0], n, "-");
        n = s_cat_uint(b->msg[0], n, fx->str < 0 ? -fx->str : fx->str);
        n = s_cat(b->msg[0], n, " AGI-");
        n = s_cat_uint(b->msg[0], n, fx->agl < 0 ? -fx->agl : fx->agl);
        n = s_cat(b->msg[0], n, " MAG-");
        n = s_cat_uint(b->msg[0], n, fx->spc < 0 ? -fx->spc : fx->spc);
    }
    else if(fx->kind == 6) { /* cleanse: reset temporary stat changes */
        (*slot)--;
        b->mods_self_str = b->mods_self_agl = b->mods_self_spc = 0;
        b->stage_self_str = b->stage_self_agl = b->stage_self_spc = 0;
        b->hype_self = 0;
        n = s_cat(b->msg[0], 0, ITEMS[idx].name);
        n = s_cat(b->msg[0], n, " TEMPORARY CHANGES CLEARED");
    }
    else if(fx->kind == 7) { /* cure */
        if(b->pl.status == STATUS_NONE ||
           (fx->status != ITEM_STATUS_ALL && b->pl.status != fx->status)) {
            n = s_cat(b->msg[0], 0, ITEMS[idx].name);
            n = s_cat(b->msg[0], n, " HAS NO EFFECT");
        } else {
            (*slot)--;
            clear_status(&b->pl);
            n = s_cat(b->msg[0], 0, ITEMS[idx].name);
            n = s_cat(b->msg[0], n, " CURED");
        }
    }
    else if(fx->kind == 5) { /* flee */
        if(!b->wild) {
            n = s_cat(b->msg[0], 0, "CANNOT FLEE A TAMER'S FIGHT");
        } else {
            (*slot)--;
            n = s_cat(b->msg[0], 0, ITEMS[idx].name);
            n = s_cat(b->msg[0], n, " ");
            n = s_cat(b->msg[0], n, g_player_name);
            n = s_cat(b->msg[0], n, " SLIPS AWAY");
            b->msg[0][n] = 0;
            b->msg_n = 1; b->msg_i = 0; b->phase = 0; b->after = BAFTER_WORLD;
            party[lead] = b->pl;
            return;
        }
    }
    else if(fx->kind == 4) { /* capture */
        (*slot)--;
        b->catch_full = 0;
        if(!b->wild) {
            (*slot)++;
            n = s_cat(b->msg[0], 0, "CRYSTALS WILL NOT TAKE A TAMERS CRYMON");
        }
        else {
            int chance = battle_capture_chance(b, fx->base);
            if(irand(1, 100) <= chance) {
                Monster c = b->foe;
                c.hp = c.maxHp * 2 / 5;
                if(c.hp < 1) c.hp = 1;
                if(*party_n < 6) {
                    party[*party_n] = c;
                    (*party_n)++;
                    dex_note_caught(c.species);
                    n = s_cat(b->msg[0], 0, ITEMS[idx].name);
                    n = s_cat(b->msg[0], n, " TAKES ");
                    n = s_cat(b->msg[0], n, SPECIES[c.species].name);
                    n = s_cat(b->msg[0], n, " IS YOURS");
                    b->msg[0][n] = 0;
                    b->msg_n = 1;
                } else {
                    b->foe = c;
                    b->catch_full = 1;
                    dex_note_caught(c.species);
                    n = s_cat(b->msg[0], 0, ITEMS[idx].name);
                    n = s_cat(b->msg[0], n, " TAKES");
                    b->msg[0][n] = 0;
                    n = s_cat(b->msg[1], 0, "PARTY FULL. RELEASE ONE.");
                    b->msg[1][n] = 0;
                    b->msg_n = 2;
                }
                b->msg_i = 0; b->phase = 0; b->after = BAFTER_WORLD;
                party[lead] = b->pl;
                return;
            }
            n = s_cat(b->msg[0], 0, ITEMS[idx].name);
            n = s_cat(b->msg[0], n, " CRACKS DARK IT SLIPS FREE");
        }
    }
    else {
        n = s_cat(b->msg[0], 0, "NOTHING HAPPENS");
    }

    b->msg[0][n] = 0;
    b->msg_n = 1; b->msg_i = 0; b->phase = 0; b->after = BAFTER_ATK;
    party[lead] = b->pl;
}

/* finishWin()'s generic wild-win tail (the trainer-specific branches
   above it in state.lua all need NPCs this port doesn't have yet --
   see the section comment). Grants XP to the party lead and marks+3;
   the grow/no-grow note is queued by the caller as a WIN_NOTE beat
   rather than shown here (see the section comment on why). */
/* XP is granted on every win regardless of trainer_kind (matches
   finishWin() granting it unconditionally before any trainer branch);
   marks and the mode/flag changes per trainer differ and are handled
   by the caller in main(), which is where all that state (soldiers,
   beat_calder, ending mode...) lives. */
static void battle_finish_win(Battle *b, Monster *party, int lead, int party_n) {
    party[lead] = b->pl;
    b->grew = grant_party_xp(party, party_n, lead, b->foe.lv);
    b->pl = party[lead];
}

/* tryEncounter(): checked once per tile the player steps onto (not
   every frame -- last_tx/last_ty track the last checked tile, exactly
   like G.lastTx/G.lastTy). Only 'T' tiles trigger, at an 18% chance
   (irand(0,99) < 18, not <= -- data.ts's exact 18-of-100 trigger set),
   gated by a 3-frame cooldown (enc_lock) after each check. Species
   pool/level range matches state.lua exactly; the reference's
   "if MAP_FOREST ... else (implicitly VELD)" is safe to mirror as
   written because HOUSE and GROVE have no 'T' tiles at all (checked
   against the map data above), so the else branch only ever runs for
   VELD in practice. Does nothing if the party is empty (leader(G) ==
   nil guard in startBattle). On a trigger, fills *out (except pl,
   which the caller sets from party[lead]) and returns 1. */
static int try_encounter(int map_id, int px, int py, int party_n,
                          int *enc_lock, int *last_tx, int *last_ty,
                          Battle *out) {
    int tx = px / TILE, ty = py / TILE;
    int id, lv, n, i, shiny;
    const EncDef *e = 0;

    if(tx == *last_tx && ty == *last_ty) return 0;
    *last_tx = tx;
    *last_ty = ty;
    if(*enc_lock > 0) { (*enc_lock)--; return 0; }
    if(party_n <= 0) return 0;

    for(i = 0; i < ENC_N; i++) {
        if(ENCOUNTERS[i].map_id == map_id &&
           tile_at(map_id, tx, ty) == ENCOUNTERS[i].tile) {
            e = &ENCOUNTERS[i];
            break;
        }
    }
    if(!e) return 0;
    if(irand(0, 99) >= e->rate) return 0;

    *enc_lock = 3;
    id = e->pool[irand(0, e->pool_n - 1)];
    lv = e->lv_min + irand(0, e->lv_max - e->lv_min);
    if(e->ty_bonus_gt >= 0 && ty > e->ty_bonus_gt) lv += 1;

    /* mint_shiny() doubles whatever level it's given, so the pre-mint
       cap must already account for that doubling -- halve
       WILD_LEVEL_CAP going in, not after, or a shiny roll could still
       land above the cap. */
    shiny = roll_shiny();
    {
        int cap = shiny ? WILD_LEVEL_CAP / 2 : WILD_LEVEL_CAP;
        if(lv > cap) lv = cap;
    }
    out->foe = shiny ? mint_shiny(id, lv) : mint_monster(id, lv);
    out->wild = 1;
    out->trainer_kind = TRAINER_WILD;
    out->soldier_id = 0;
    out->bench_n = 0;
    out->catch_full = 0;
    out->phase = 0;
    n = s_cat(out->msg[0], 0, out->foe.shiny ? "A SHINY " : "A WILD ");
    n = s_cat(out->msg[0], n, SPECIES[id].name);
    out->msg[0][n] = 0;
    out->msg_n = 1;
    out->msg_i = 0;
    out->after = BAFTER_ITEM;
    out->cur = 0;
    out->mods_self_str = out->mods_self_agl = out->mods_self_spc = 0;
    out->mods_foe_str = out->mods_foe_agl = out->mods_foe_spc = 0;
    out->pend_str = out->pend_agl = out->pend_spc = 0;
    out->pl_poisoned = out->foe_poisoned = 0;
    out->stage_self_str = out->stage_self_agl = out->stage_self_spc = 0;
    out->stage_foe_str = out->stage_foe_agl = out->stage_foe_spc = 0;
    out->hype_self = out->hype_foe = 0;
    out->nmove_pl_used = out->hype_pl_used = out->nmove_foe_used = out->hype_foe_used = 0;
    out->grew = 0;
    return 1;
}

/* ----------------------------------------------------------------------
 * Battle drawing. Unlike the bag/party/shop menus (one big centered
 * panel -- fine for those, they have no background scene behind
 * them), this uses drawBattle()'s own layout: small boxed status
 * readouts and a content box, both far short of the full screen, so
 * the battle-bg.png background and both sprites stay visible in
 * between them. No background panels (see draw_dialogue_box's own
 * comment) -- status text and the message/menu area both sit
 * directly over the battle background/sprites now, just outlined.
 * ---------------------------------------------------------------------- */

/* BCONTENT (the message/item/attack/guard menu box) is sized tight
   against its own content now that the mid-combat item menu no longer
   carries effect text (see draw_battle_item_menu) -- its widest row
   is the attack menu's "LIGHTNING STRIKE", not an item line, and its
   height is still just the item menu's worst case (PASS + 5 items).
   Shrinking it pushes it further right and further down (it's still
   anchored to the bottom-right corner), which is what actually frees
   the room the two status boxes and MONSTER_SPRITE_W/H below now use.

   The foe's status box takes the top-right edge (as high and as far
   right as it can sit without risking the edge) instead of tucking
   under the foe's sprite; the foe's sprite goes directly below the
   box instead, sized as large as it can get while still clearing
   BCONTENT_Y. Max's status box sits lower, near the screen's vertical
   middle and as far left as it can go -- it doesn't need to clear the
   foe's sprite at all (their X ranges don't overlap: the sprite is
   flush against the right edge, the box flush against the left), only
   the foe's own box (BGAP above it) and BCONTENT_Y (BGAP below it).
   That's what lets the sprite grow far past what stacking both boxes
   in the foe's own column allowed. Max's sprite, still flush in the
   true lower-left corner, isn't part of any of this -- its width
   alone keeps it clear of BCONTENT regardless of height. BGAP is the
   fixed clearance kept between every pair of these elements. */
#define BGAP          4

#define BCONTENT_W    180
#define BCONTENT_H    112
#define BCONTENT_X    (SCREEN_W - 4 - BCONTENT_W)
#define BCONTENT_Y    (SCREEN_H - 4 - BCONTENT_H)

#define BSTATUS_BOX_W 208
#define BSTATUS_BOX_H 18

#define BFOE_BOX_W    BSTATUS_BOX_W
#define BFOE_BOX_H    BSTATUS_BOX_H
#define BFOE_BOX_X    (SCREEN_W - 4 - BSTATUS_BOX_W)
#define BFOE_BOX_Y    4

#define BFOE_SPRITE_X (SCREEN_W - 8 - MONSTER_SPRITE_W)
#define BFOE_SPRITE_Y (BFOE_BOX_Y + BSTATUS_BOX_H + BGAP)

#define BPL_SPRITE_X  8
#define BPL_SPRITE_Y  (SCREEN_H - 4 - MONSTER_SPRITE_H)

#define BPL_BOX_W     BSTATUS_BOX_W
#define BPL_BOX_H     BSTATUS_BOX_H
#define BPL_BOX_X     4
#define BPL_BOX_Y     (BCONTENT_Y - BGAP - BSTATUS_BOX_H)

#define BROW_H        16

/* Index order matches SP_QUILLPUP..SP_CRYMARE and gen_sprites.py's
   MONSTERS list. Used for both the foe's sprite and -- new here --
   "Max's CryMon" (the player's own active monster; Max herself
   already has her own walk sprite on the world map, so this is what
   "the player's battle sprite" actually means in this game). */
static const u16 *const MONSTER_SPRITES[SPECIES_N][4] = {
    { monster_quillpup_1, monster_quillpup_2, monster_quillpup_3, monster_quillpup_4 },
    { monster_glimmoth_1, monster_glimmoth_2, monster_glimmoth_3, monster_glimmoth_4 },
    { monster_tortcask_1, monster_tortcask_2, monster_tortcask_3, monster_tortcask_4 },
    { monster_razorbat_1, monster_razorbat_2, monster_razorbat_3, monster_razorbat_4 },
    { monster_mossback_1, monster_mossback_2, monster_mossback_3, monster_mossback_4 },
    { monster_briarfox_1, monster_briarfox_2, monster_briarfox_3, monster_briarfox_4 },
    { monster_fenwisp_1, monster_fenwisp_2, monster_fenwisp_3, monster_fenwisp_4 },
    { monster_duskhorn_1, monster_duskhorn_2, monster_duskhorn_3, monster_duskhorn_4 },
    { monster_needleroot_1, monster_needleroot_2, monster_needleroot_3, monster_needleroot_4 },
    { monster_cathleen_1, monster_cathleen_2, monster_cathleen_3, monster_cathleen_4 },
    { monster_crymare_1, monster_crymare_2, monster_crymare_3, monster_crymare_4 },
    { monster_emberling_1, monster_emberling_2, monster_emberling_3, monster_emberling_4 },
    { monster_frostail_1, monster_frostail_2, monster_frostail_3, monster_frostail_4 },
    { monster_boulderam_1, monster_boulderam_2, monster_boulderam_3, monster_boulderam_4 },
    { monster_stormwing_1, monster_stormwing_2, monster_stormwing_3, monster_stormwing_4 },
    { monster_sableclaw_1, monster_sableclaw_2, monster_sableclaw_3, monster_sableclaw_4 },
    { monster_thornhide_1, monster_thornhide_2, monster_thornhide_3, monster_thornhide_4 },
    { monster_glasswisp_1, monster_glasswisp_2, monster_glasswisp_3, monster_glasswisp_4 },
    { monster_ashenmaw_1, monster_ashenmaw_2, monster_ashenmaw_3, monster_ashenmaw_4 },
    { monster_heavenfall_1, monster_heavenfall_2, monster_heavenfall_3, monster_heavenfall_4 },
    { monster_peatling_1, monster_peatling_2, monster_peatling_3, monster_peatling_4 },
    { monster_mireback_1, monster_mireback_2, monster_mireback_3, monster_mireback_4 },
    { monster_glowcap_1, monster_glowcap_2, monster_glowcap_3, monster_glowcap_4 },
    { monster_slatekin_1, monster_slatekin_2, monster_slatekin_3, monster_slatekin_4 },
    { monster_gravelurk_1, monster_gravelurk_2, monster_gravelurk_3, monster_gravelurk_4 },
    { monster_cindermite_1, monster_cindermite_2, monster_cindermite_3, monster_cindermite_4 },
    { monster_veilcap_1, monster_veilcap_2, monster_veilcap_3, monster_veilcap_4 },
    { monster_kilnback_1, monster_kilnback_2, monster_kilnback_3, monster_kilnback_4 },
};

static void draw_party_mon_icon(int species, int x, int y) {
    if(species < 0) return;
    blit_sprite_fit(MONSTER_SPRITES[species][0], MONSTER_SPRITE_W, MONSTER_SPRITE_H, x, y, 16, 16);
}

/* Idle-animated like the stationary world NPCs (drawBattle()'s own
   `Math.floor(b.t * 4) % 4 + 1`, shared by foe and player sprite) --
   frame_count/15 matches the same 4fps cadence draw_npc_idle() uses.
   enter_t/faint_t are frame_count timestamps (main()'s battle_*_t
   locals): 0 means "no animation in progress" for that side, matching
   frame_count never legitimately being 0 once the title screen has
   run a single frame. enter plays once per fresh monster (a new
   battle, or a bench monster swapping in after a faint); faint plays
   once hp actually hits 0 and holds on its last (fully faded) frame
   for as long as the 0-hp monster stays on screen -- both read from
   the same blit_sprite_anim so a sprite that's both "just entered"
   and immediately guarded (impossible, but if timers ever overlapped)
   would still draw sanely rather than double-applying either effect
   twice. */
#define BATTLE_ANIM_ENTER_FRAMES 18
#define BATTLE_ANIM_FAINT_FRAMES 24
static void draw_battle_sprites(const Battle *b, u32 frame_count,
                                 u32 foe_enter_t, u32 foe_faint_t,
                                 u32 pl_enter_t, u32 pl_faint_t) {
    int f = (int)((frame_count / 15u) % 4u);
    int foe_revealed = MONSTER_SPRITE_H, foe_fade = 16;
    int pl_revealed = MONSTER_SPRITE_H, pl_fade = 16;

    if(foe_faint_t && frame_count >= foe_faint_t) {
        u32 el = frame_count - foe_faint_t;
        foe_fade = (el >= BATTLE_ANIM_FAINT_FRAMES) ? 0
                       : 16 - (int)(el * 16u / BATTLE_ANIM_FAINT_FRAMES);
    }
    else if(foe_enter_t && frame_count >= foe_enter_t) {
        u32 el = frame_count - foe_enter_t;
        foe_revealed = (el >= BATTLE_ANIM_ENTER_FRAMES) ? MONSTER_SPRITE_H
                           : (int)(el * (u32)MONSTER_SPRITE_H / BATTLE_ANIM_ENTER_FRAMES);
    }
    if(pl_faint_t && frame_count >= pl_faint_t) {
        u32 el = frame_count - pl_faint_t;
        pl_fade = (el >= BATTLE_ANIM_FAINT_FRAMES) ? 0
                      : 16 - (int)(el * 16u / BATTLE_ANIM_FAINT_FRAMES);
    }
    else if(pl_enter_t && frame_count >= pl_enter_t) {
        u32 el = frame_count - pl_enter_t;
        pl_revealed = (el >= BATTLE_ANIM_ENTER_FRAMES) ? MONSTER_SPRITE_H
                          : (int)(el * (u32)MONSTER_SPRITE_H / BATTLE_ANIM_ENTER_FRAMES);
    }

    blit_sprite_anim(MONSTER_SPRITES[b->foe.species][f], MONSTER_SPRITE_W, MONSTER_SPRITE_H,
                      BFOE_SPRITE_X, BFOE_SPRITE_Y, b->foe.shiny, foe_revealed, foe_fade);
    blit_sprite_anim(MONSTER_SPRITES[b->pl.species][f], MONSTER_SPRITE_W, MONSTER_SPRITE_H,
                      BPL_SPRITE_X, BPL_SPRITE_Y, b->pl.shiny, pl_revealed, pl_fade);
}

/* One line each -- "*NAME LVxx hp/maxHp" -- sized to BSTATUS_BOX_W's
   worst case (see the layout comment above). */
static void draw_battle_status(const Battle *b) {
    char buf[40];
    int n;

    n = s_cat(buf, 0, b->foe.shiny ? "*" : "");
    n = s_cat(buf, n, SPECIES[b->foe.species].name);
    n = s_cat(buf, n, " LV");
    n = s_cat_uint(buf, n, b->foe.lv);
    n = s_cat(buf, n, " ");
    n = s_cat_uint(buf, n, b->foe.hp);
    n = s_cat(buf, n, "/");
    n = s_cat_uint(buf, n, b->foe.maxHp);
    if(b->foe.status != STATUS_NONE) {
        n = s_cat(buf, n, " ");
        n = s_cat(buf, n, STATUS_NAME[b->foe.status]);
    }
    buf[n] = 0;
    draw_text_s(buf, BFOE_BOX_X + 4, BFOE_BOX_Y + 4, 0xFFFF, MENU_SCALE);

    n = s_cat(buf, 0, b->pl.shiny ? "*" : "");
    n = s_cat(buf, n, SPECIES[b->pl.species].name);
    n = s_cat(buf, n, " LV");
    n = s_cat_uint(buf, n, b->pl.lv);
    n = s_cat(buf, n, " ");
    n = s_cat_uint(buf, n, b->pl.hp);
    n = s_cat(buf, n, "/");
    n = s_cat_uint(buf, n, b->pl.maxHp);
    if(b->pl.status != STATUS_NONE) {
        n = s_cat(buf, n, " ");
        n = s_cat(buf, n, STATUS_NAME[b->pl.status]);
    }
    buf[n] = 0;
    draw_text_s(buf, BPL_BOX_X + 4, BPL_BOX_Y + 4, 0xFFFF, MENU_SCALE);
}

static void draw_battle_menu_row(const char *label, int idx, int cur, int y) {
    u16 color = (idx == cur) ? rgb565(232, 228, 216) : rgb565(138, 134, 120);
    draw_text_s(idx == cur ? ">" : " ", BCONTENT_X + 8, y, color, MENU_SCALE);
    draw_text_s(label, BCONTENT_X + 16, y, color, MENU_SCALE);
}

/* Icon variant of the above, for menus with room for one (the shop --
   the battle item menu's own rows stay text-only, BCONTENT_W is
   already tight against their longer stat strings). */
static void draw_menu_row_icon(const u16 *icon, const char *label, int idx, int cur, int y) {
    u16 color = (idx == cur) ? rgb565(232, 228, 216) : rgb565(138, 134, 120);
    draw_text_s(idx == cur ? ">" : " ", MENU_X + 8, y, color, MENU_SCALE);
    if(icon)
        blit_sprite(icon, ITEM_ICON_W, ITEM_ICON_H, MENU_X + 16, y - 1);
    draw_text_s(label, MENU_X + 16 + ITEM_ICON_W + 4, y, color, MENU_SCALE);
}

/* Row count/kind-at-cursor for the item menu, kept in exact lockstep
   with draw_battle_item_menu's own conditional row order below (both
   walk PASS, salve, bandage, bitterroot, dust, gem in that order,
   skipping any the bag is empty of). Used by main()'s input handling,
   which needs the mapping without actually drawing. */
static int battle_item_menu_count(const Bag *bag) {
    int n = 1; /* PASS always present */
    if(bag->salve > 0) n++;
    if(bag->bandage > 0) n++;
    if(bag->bitterroot > 0) n++;
    if(bag->dust > 0) n++;
    if(bag->gem > 0) n++;
    if(bag->sunbalm > 0) n++;
    if(bag->warroot > 0) n++;
    if(bag->smokebomb > 0) n++;
    if(bag->greatcrystal > 0) n++;
    return n;
}

static int battle_item_menu_kind(const Bag *bag, int idx) {
    int i = 0;
    if(idx == i++) return ITEM_PASS;
    if(bag->salve > 0)        { if(idx == i++) return ITEM_SALVE; }
    if(bag->bandage > 0)      { if(idx == i++) return ITEM_BANDAGE; }
    if(bag->bitterroot > 0)   { if(idx == i++) return ITEM_BITTERROOT; }
    if(bag->dust > 0)         { if(idx == i++) return ITEM_DUST; }
    if(bag->gem > 0)          { if(idx == i++) return ITEM_GEM; }
    if(bag->sunbalm > 0)      { if(idx == i++) return ITEM_SUNBALM; }
    if(bag->warroot > 0)      { if(idx == i++) return ITEM_WARROOT; }
    if(bag->smokebomb > 0)    { if(idx == i++) return ITEM_SMOKEBOMB; }
    if(bag->greatcrystal > 0) { if(idx == i++) return ITEM_GREATCRYSTAL; }
    return ITEM_PASS; /* unreachable: idx is always < battle_item_menu_count() */
}

/* fillItemMenu, minus the "switch" row (this port's party has no
   manual-switch UI -- see the item-menu comment in main()). Capture
   Crystal's label includes the live capture chance, matching
   fillItemMenu's wild-battle branch (the trainer branch, plain
   "Capture Crystal xN", is dead code here -- b->wild is always 1).

   BCONTENT_H only has room for BATTLE_ITEM_VISIBLE_ROWS at once (the
   layout was sized for the original PASS+5 items, not PASS+9) -- with
   9 possible item types now, a player who's collected one of
   everything needs to scroll. Paged in fixed BATTLE_ITEM_VISIBLE_ROWS
   chunks rather than a smooth 1-row scroll so the visible window is a
   pure function of `cur` (which page cur falls on), no extra
   persisted scroll state needed. */
#define BATTLE_ITEM_VISIBLE_ROWS 6
static int draw_battle_item_menu(const Bag *bag, int cur) {
    int y = BCONTENT_Y + 8;
    int i = 0;
    char buf[40];
    int n;
    int total, page, first, last;
    const char *kinds_label[9];
    int kinds_count[9];
    int kn = 0;

    kinds_label[kn] = "PASS"; kinds_count[kn] = -1; kn++;
    if(bag->salve > 0)        { kinds_label[kn] = "SALVE X";     kinds_count[kn] = bag->salve; kn++; }
    if(bag->bandage > 0)      { kinds_label[kn] = "WRAP X";      kinds_count[kn] = bag->bandage; kn++; }
    if(bag->bitterroot > 0)   { kinds_label[kn] = "BITTERROOT X"; kinds_count[kn] = bag->bitterroot; kn++; }
    if(bag->dust > 0)         { kinds_label[kn] = "DUST X";      kinds_count[kn] = bag->dust; kn++; }
    if(bag->gem > 0)          { kinds_label[kn] = "CRYSTAL X";   kinds_count[kn] = bag->gem; kn++; }
    if(bag->sunbalm > 0)      { kinds_label[kn] = "SUNBALM X";   kinds_count[kn] = bag->sunbalm; kn++; }
    if(bag->warroot > 0)      { kinds_label[kn] = "WARROOT X";   kinds_count[kn] = bag->warroot; kn++; }
    if(bag->smokebomb > 0)    { kinds_label[kn] = "SMOKE BOMB X"; kinds_count[kn] = bag->smokebomb; kn++; }
    if(bag->greatcrystal > 0) { kinds_label[kn] = "GR CRYSTAL X"; kinds_count[kn] = bag->greatcrystal; kn++; }

    total = kn;
    page = (cur / BATTLE_ITEM_VISIBLE_ROWS) * BATTLE_ITEM_VISIBLE_ROWS;
    first = page;
    last = first + BATTLE_ITEM_VISIBLE_ROWS;
    if(last > total) last = total;

    for(i = first; i < last; i++) {
        if(kinds_count[i] < 0) {
            draw_battle_menu_row(kinds_label[i], i, cur, y);
        }
        else {
            n = s_cat(buf, 0, kinds_label[i]);
            n = s_cat_uint(buf, n, kinds_count[i]);
            buf[n] = 0;
            draw_battle_menu_row(buf, i, cur, y);
        }
        y += MENU_ROW_H;
    }
    return total; /* row count, for input handling to map kinds <-> cursor */
}

/* attackMenu(): a spellcaster lead's attack menu is just their spell
   names (4 rows for Cathleen, PP shown only next to Mana Surge, the
   one with a pp cost -- matches data.ts's spells[].pp flag), no
   basic/special/wait rows at all. */
/* "should be apparent when selecting an attack" -- a move's power/speed
   design values (0.5-1.5) are shown x10 as friendly 5-15 integers, one
   shared detail line below the row list rather than crammed onto each
   row: BCONTENT_W (180px) is too narrow to fit a 16-char move name like
   "LIGHTNING STRIKE" AND a stat/power/speed suffix on the same line, but
   the box has ~40px of headroom below up to 4 rows, easily enough for
   this. Nothing is drawn for a stat-less row (WAIT). */
static void draw_atk_detail(int stat, float power, float speed, int y) {
    char buf[24];
    int n = s_cat(buf, 0, stat == ATK_STR ? "STR PWR" : "MAG PWR");
    n = s_cat_uint(buf, n, (unsigned)jground(power * 10.0f));
    n = s_cat(buf, n, " SPD");
    n = s_cat_uint(buf, n, (unsigned)jground(speed * 10.0f));
    buf[n] = 0;
    draw_text_s(buf, BCONTENT_X + 8, y, rgb565(180, 220, 170), MENU_SCALE);
}

#define ATK_MENU_VISIBLE 4

static int battle_atk_count(const Battle *b) {
    UMove moves[UMOVE_MAX];
    return unlocked_moves(&b->pl, 1, moves, UMOVE_MAX);
}

static void draw_battle_atk_menu(const Battle *b, int cur) {
    int y = BCONTENT_Y + 8;
    int i, n, start, shown;
    char buf[32];
    UMove moves[UMOVE_MAX];
    int mn = unlocked_moves(&b->pl, 1, moves, UMOVE_MAX);

    shown = mn < ATK_MENU_VISIBLE ? mn : ATK_MENU_VISIBLE;
    start = cur - shown + 1;
    if(start < 0) start = 0;
    if(start > mn - shown) start = mn - shown;
    if(start < 0) start = 0;
    for(i = 0; i < shown; i++) {
        int idx = start + i;
        const UMove *mv = &moves[idx];
        if(mv->kind == UMOVE_SPECIAL || (mv->kind == UMOVE_SPELL && mv->spell_id == SPELL_MANASURGE)) {
            n = s_cat(buf, 0, mv->name);
            n = s_cat(buf, n, " ");
            n = s_cat_uint(buf, n, b->pl.spp);
            n = s_cat(buf, n, "/");
            n = s_cat_uint(buf, n, b->pl.sppMax);
            buf[n] = 0;
            draw_battle_menu_row(buf, idx, cur, y);
        } else {
            draw_battle_menu_row(mv->name, idx, cur, y);
        }
        y += MENU_ROW_H;
    }
    if(cur >= 0 && cur < mn && moves[cur].kind != UMOVE_WAIT)
        draw_atk_detail(moves[cur].stat, moves[cur].power, moves[cur].speed, y + 8);
}

static void draw_battle_guard_menu(int cur) {
    int y = BCONTENT_Y + 8;
    draw_battle_menu_row("DODGE AGI", 0, cur, y); y += MENU_ROW_H;
    draw_battle_menu_row("BLOCK STR", 1, cur, y); y += MENU_ROW_H;
    draw_battle_menu_row("BARRIER MAG", 2, cur, y);
}

/* drawBattle()'s full-screen background, drawn before the status
   boxes/sprites/content box, all of which are individually small so
   the background (and both battle sprites) stay visible around them
   -- see the section comment above. */
static void draw_battle_bg(void) {
    blit_sprite(battle_bg, BATTLE_BG_W, BATTLE_BG_H, 0, 0);
}

static void draw_battle(const Battle *b, const Bag *bag, u32 frame_count,
                         u32 foe_enter_t, u32 foe_faint_t, u32 pl_enter_t, u32 pl_faint_t) {
    draw_battle_bg();
    draw_battle_status(b);
    draw_battle_sprites(b, frame_count, foe_enter_t, foe_faint_t, pl_enter_t, pl_faint_t);

    switch(b->phase) {
        case 0:
            draw_wrapped(b->msg[b->msg_i], BCONTENT_X + 8, BCONTENT_Y + 8,
                         rgb565(232, 228, 216), MENU_SCALE, BCONTENT_W / CHAR_CELL(MENU_SCALE) - 2, 9);
            break;
        case 1:
            draw_battle_item_menu(bag, b->cur);
            break;
        case 2:
            draw_battle_atk_menu(b, b->cur);
            break;
        case 3:
            draw_battle_guard_menu(b->cur);
            break;
        case 4: {
            int bx = BCONTENT_X + 8, by = BCONTENT_Y + 32;
            int bw = BCONTENT_W - 16, bh = 10;
            int c0 = (int)(SPEC_CONN_LO / 100.0f * (float)bw);
            int c1 = (int)(SPEC_CONN_HI / 100.0f * (float)bw);
            int p0 = (int)(SPEC_PERFECT_LO / 100.0f * (float)bw);
            int p1 = (int)(SPEC_PERFECT_HI / 100.0f * (float)bw);
            int nx = bx + (int)(b->mg / 100.0f * (float)bw) - 1;
            draw_text_s("SPECIAL  HIT THE MARK", BCONTENT_X + 8, BCONTENT_Y + 8,
                        rgb565(197, 206, 198), MENU_SCALE);
            fill_rect(bx, by, bw, bh, rgb565(139, 48, 48));
            fill_rect(bx + c0, by, c1 - c0, bh, rgb565(201, 162, 39));
            fill_rect(bx + p0, by, p1 - p0, bh, rgb565(74, 154, 74));
            fill_rect(nx, by - 4, 3, bh + 8, rgb565(232, 228, 216));
            break;
        }
        default:
            break;
    }
}

/* ----------------------------------------------------------------------
 * World NPCs. Wren/Mae/Ivo/Nell/Pike/Bram/Calder/Shinigami/Cathleen
 * are stationary proximity-interact points (this port's own
 * interact()/closest_mark pattern, already used for HOUSE's bed/
 * shelf/crate) -- engine.ts never moves them either, so this is a
 * faithful 1:1. Mason, Anne and the three FOREST soldiers are real
 * engine.ts actors with float positions and per-frame movement
 * (approach/chase/patrol/leave, all ported below with the same speed
 * constants engine.ts uses, scaled by this port's TILE=20 vs the
 * original's TILE=32): Mason force-walks toward the player the moment
 * they leave the house and ambushes them into masonFight on contact
 * (mason_state 0 off/1 approach/2 standing-post-ambush/3 leaving);
 * Anne does the same after the player's first battle, gifts gems on
 * contact, then walks off (anne_state 0/1/2 done-pending/3 leaving);
 * soldiers patrol a fixed axis around their spawn mark and give chase
 * once the player crosses their line of sight (soldier_update()'s
 * raycast below, ported from soldierLos()), ambushing the same way
 * Mason does once they catch up.
 *
 * Anne, corrected: an earlier pass here concluded she was unreachable
 * because state.lua defines maybeAnne() but never calls it from
 * anywhere in state.lua or input.lua (true, checked directly). What
 * that pass missed is that state.lua's own header names
 * src/game/engine.ts as the single source of truth this Lua is
 * ported from, and engine.ts's equivalent, maybeStartAnne(), IS
 * called -- from updateWorld() every frame (gated on
 * !talking() && hudT<=0) and after cycling the party. So the Lua
 * intermediate has a real porting gap (a missing call site), not the
 * TS/canonical game; the faithful port includes Anne.
 * ---------------------------------------------------------------------- */
static int __attribute__((unused))
near_mark(int map_id, char mark, int px, int py, int radius_sq) {
    int mx, my, dx, dy;
    mark_center(map_id, mark, &mx, &my);
    dx = px - mx;
    dy = py - my;
    return dx * dx + dy * dy <= radius_sq;}

static int npc_flag_on(int id, int **ft, int party_n) {
    if(id == FLAG_HAS_PARTY2) return party_n > 1;
    if(id < 0 || id >= FLAG_N || ft[id] == 0) return 0;
    return *ft[id] != 0;
}

static void npc_flag_set(int id, int **ft) {
    if(id < 0 || id >= FLAG_N || ft[id] == 0) return;
    *ft[id] = 1;
}

static int npc_match_step(const NpcDef *d, int **ft, int party_n) {
    int i;
    for(i = 0; i < d->stepn; i++) {
        const NpcStep *st = &NPC_STEPS[d->step0 + i];
        if(st->hide_if >= 0) {
            if(npc_flag_on(st->hide_if, ft, party_n)) return -1;
            continue;
        }
        if(st->if_flag >= 0 && !npc_flag_on(st->if_flag, ft, party_n)) continue;
        if(st->if_not >= 0 && npc_flag_on(st->if_not, ft, party_n)) continue;
        return d->step0 + i;
    }
    return -2;
}

/* Chase state for a stationary wsoldier-style trainer -- generalizes
   the hand-written FOREST Soldier[3] patrol/chase to every NPC_DEFS
   entry whose script leads to a wsoldier battle (mirrors engine.ts's
   Roamer/roamers). Indexed by NPC_DEFS index, lazily positioned at
   its mark on first touch; gate-blockers (Calder, the Priestess)
   never have such a step, so they're excluded automatically. */
typedef struct {
    float x, y;
    int chase, inited;
    int dir; /* 0=down 1=up 2=left 3=right */
} Roamer;
static Roamer g_roamers[NPC_DEF_N];

static int npc_def_roamable(int i) {
    const NpcDef *d = &NPC_DEFS[i];
    int k;
    for(k = 0; k < d->stepn; k++)
        if(NPC_STEPS[d->step0 + k].after == NPC_AFTER_WSOLDIER) return 1;
    return 0;
}

static void roamer_ensure(int i) {
    Roamer *r = &g_roamers[i];
    if(!r->inited) {
        int cx, cy;
        mark_center(NPC_DEFS[i].map_id, NPC_DEFS[i].mark, &cx, &cy);
        r->x = (float)cx;
        r->y = (float)cy;
        r->chase = 0;
        {
            int mid_x = (MAPS[NPC_DEFS[i].map_id].cols * TILE) / 2;
            int mid_y = (MAPS[NPC_DEFS[i].map_id].rows_n * TILE) / 2;
            int adx = mid_x - cx; if(adx < 0) adx = -adx;
            int ady = mid_y - cy; if(ady < 0) ady = -ady;
            if(adx >= ady) r->dir = (mid_x < cx) ? 2 : 3;
            else r->dir = (mid_y < cy) ? 1 : 0;
        }
        r->inited = 1;
    }
}

/* Facing-only LOS — same ray as soldier_los. dir: 0=down 1=up 2=left 3=right. */
static int roamer_los(int map_id, float x, float y, int dir, int ptx, int pty) {
    int stx = (int)x / TILE, sty = (int)y / TILE;
    int dx = (dir == 2) ? -1 : (dir == 3) ? 1 : 0;
    int dy = (dir == 1) ? -1 : (dir == 0) ? 1 : 0;
    int i, max, tx, ty;
    if(dx == 0 && dy == 0) return 0;
    max = MAPS[map_id].cols > MAPS[map_id].rows_n ? MAPS[map_id].cols : MAPS[map_id].rows_n;
    for(i = 1; i <= max; i++) {
        tx = stx + dx * i;
        ty = sty + dy * i;
        if(tile_is_solid(tile_at(map_id, tx, ty))) return 0;
        if(tx == ptx && ty == pty) return 1;
    }
    return 0;
}

static int npc_def_index_for(int map_id, char mark) {
    int i;
    for(i = 0; i < NPC_DEF_N; i++)
        if(NPC_DEFS[i].map_id == map_id && NPC_DEFS[i].mark == mark) return i;
    return -1;
}

/* Same as ws_push_mark_idle, but drawn at a roamer's live chase
   position instead of its fixed mark once one is tracked -- matches
   engine.ts's roamer-aware NPC draw loop. Anything not a roamable
   NpcDef, or one the per-frame update hasn't touched yet this map
   visit, falls straight through to the plain mark position. */
static void ws_push_mark_idle_roam(WorldSprite *list, int *n, int map_id, char mark,
                                    const u16 *const frames[4], u32 frame_count,
                                    int frames_per_step, int w, int h) {
    int f = (int)((frame_count / (u32)frames_per_step) % 4u);
    int idx = npc_def_index_for(map_id, mark);
    int cx, cy, ebit;
    ebit = npc_exec_bit(map_id, mark);
    if(ebit >= 0 && (g_executed_mask & (1u << ebit))) return;
    if(idx >= 0 && npc_def_roamable(idx) && g_roamers[idx].inited) {
        cx = (int)g_roamers[idx].x;
        cy = (int)g_roamers[idx].y;
    } else {
        mark_center(map_id, mark, &cx, &cy);
    }
    ws_push(list, n, frames[f], w, h, cx, cy);
}

static void collect_npcs(WorldSprite *list, int *n, int map_id, u32 frame_count,
                          int mason_state, float mason_x, float mason_y, int mason_dir, int mason_frame,
                          int anne_state, float anne_x, float anne_y, int anne_dir, int anne_frame,
                          int cath_caught, int beat_shin, int saw_shinigami_rock,
                          const Soldier *soldiers, const int *soldier_beaten,
                          int beat_calder, int has_scroll,
                          int chest_looted, int quarry_crate_looted, int quarry_shelf_searched) {
    if(map_id == MAP_VELD) {
        ws_push_mark_idle(list, n, map_id, 'K', WREN_FRAMES, frame_count, 15, NPC_SPRITE_W, NPC_SPRITE_H);
        ws_push_mark_idle(list, n, map_id, 'I', MAE_FRAMES, frame_count, 15, NPC_SPRITE_W, NPC_SPRITE_H);
        ws_push_mark_idle(list, n, map_id, 'V', IVO_FRAMES, frame_count, 15, NPC_SPRITE_W, NPC_SPRITE_H);
        ws_push_mark_idle(list, n, map_id, 'A', NELL_FRAMES, frame_count, 15, NPC_SPRITE_W, NPC_SPRITE_H);
        ws_push_mark_idle(list, n, map_id, 'Q', PIKE_FRAMES, frame_count, 15, NPC_SPRITE_W, NPC_SPRITE_H);
        ws_push_mark_idle(list, n, map_id, 'J', BRAM_FRAMES, frame_count, 15, NPC_SPRITE_W, NPC_SPRITE_H);
        /* Calder and the Priestess guard the only walkable approach to
           their gates -- once beaten (any mercy outcome; execute hides
           them entirely via g_executed_mask, same as every other NPC),
           they step aside one tile instead of lingering exactly on the
           spot they used to block. Offsets are hand-picked open ground
           next to each gate (see maps.json's VELD rows around 'E'/'4'
           -- Calder steps south, the Priestess steps southeast onto
           the open tile beside the gauntlet door). Matches engine.ts's
           npcPassOffset(). */
        ws_push_mark_idle_off(list, n, map_id, 'E', CALDER_FRAMES, frame_count, 15, NPC_SPRITE_W, NPC_SPRITE_H,
                               0, beat_calder ? TILE : 0);
        ws_push_mark_idle_off(list, n, map_id, '4', HEAVENFALLPRIESTESS_FRAMES, frame_count, 15, NPC_SPRITE_W, NPC_SPRITE_H,
                               has_scroll ? TILE : 0, has_scroll ? TILE : 0);
        /* PLACEHOLDER_ART: no real boulder art exists yet, see
           public/sprites/npc/shinigamiBoulder-*.png and CURRENT_WORK.md.
           Seals the west gate until the rock-shatter event actually
           plays (saw_shinigami_rock), not merely until Shinigami is
           beaten -- he still has to walk into view first (see the
           beat_shin && !saw_shinigami_rock trigger below). His own
           sprite (mark '9', below) appears for that whole window. */
        if(!saw_shinigami_rock)
            ws_push_mark_idle(list, n, map_id, 'Y', SHINIGAMIBOULDER_FRAMES, frame_count, 15, NPC_SPRITE_W, NPC_SPRITE_H);
        if(beat_shin && !saw_shinigami_rock)
            ws_push_mark_idle(list, n, map_id, '9', SHINIGAMI_FRAMES, frame_count, 20, NPC_SPRITE_W, NPC_SPRITE_H);
        if(mason_state) {
            ws_push_walker(list, n, MASON_FRAMES, mason_x, mason_y, mason_dir, mason_frame);
            if(*n > 0) list[*n - 1].scale = SPR_SCALE_MASON;
        }
    }
    else if(map_id == MAP_FOREST) {
        int i;
        for(i = 0; i < 3; i++) {
            if(soldier_beaten[i]) continue;
            ws_push_walker(list, n, SOLDIER_FRAMES, soldiers[i].x, soldiers[i].y, soldiers[i].dir,
                            (int)soldiers[i].anim);
        }
        ws_push_mark_idle_roam(list, n, map_id, '4', RANGER_FRAMES, frame_count, 15, NPC_SPRITE_W, NPC_SPRITE_H);
        ws_push_mark_idle_roam(list, n, map_id, '5', SCOUT_FRAMES, frame_count, 15, NPC_SPRITE_W, NPC_SPRITE_H);
    }
    else if(map_id == MAP_GROVE) {
        if(!beat_shin)
            ws_push_mark_idle(list, n, map_id, '9', SHINIGAMI_FRAMES, frame_count, 20, NPC_SPRITE_W, NPC_SPRITE_H);
        if(!cath_caught)
            ws_push_mark(list, n, map_id, '8', npc_cathleen, CATHLEEN_WORLD_W, CATHLEEN_WORLD_H);
        ws_push_mark_idle_roam(list, n, map_id, 'K', CROSS_FRAMES, frame_count, 15, NPC_SPRITE_W, NPC_SPRITE_H);
    }
    else if(map_id == MAP_CAMP) {
        ws_push_mark_idle(list, n, map_id, 'I', COMMANDER_FRAMES, frame_count, 15, NPC_SPRITE_W, NPC_SPRITE_H);
        ws_push_mark_idle_roam(list, n, map_id, 'K', CONSCRIPT_FRAMES, frame_count, 15, NPC_SPRITE_W, NPC_SPRITE_H);
        ws_push_mark_idle_roam(list, n, map_id, 'A', ENFORCER_FRAMES, frame_count, 15, NPC_SPRITE_W, NPC_SPRITE_H);
    }
    else if(map_id == MAP_CLIFFS) {
        ws_push_mark_idle_roam(list, n, map_id, 'V', SENTRY_FRAMES, frame_count, 15, NPC_SPRITE_W, NPC_SPRITE_H);
        ws_push_mark_idle(list, n, map_id, 'Y', TESSA_FRAMES, frame_count, 15, NPC_SPRITE_W, NPC_SPRITE_H);
        /* Treasure chest: reuses the existing crate prop art rather
           than needing new placeholder art -- close enough visually
           (a wooden storage box) that it doesn't need its own tag. */
        if(!chest_looted)
            ws_push_mark(list, n, map_id, 'C', prop_crate, PROP_CRATE_W, PROP_CRATE_H);
    }
    else if(map_id == MAP_RUINS) {
        ws_push_mark_idle(list, n, map_id, 'J', OREN_FRAMES, frame_count, 15, NPC_SPRITE_W, NPC_SPRITE_H);
        ws_push_mark_idle(list, n, map_id, 'K', BIRCH_FRAMES, frame_count, 15, NPC_SPRITE_W, NPC_SPRITE_H);
        ws_push_mark_idle(list, n, map_id, 'A', SABLE_FRAMES, frame_count, 15, NPC_SPRITE_W, NPC_SPRITE_H);
        ws_push_mark_idle_roam(list, n, map_id, '6', KEEPER_FRAMES, frame_count, 15, NPC_SPRITE_W, NPC_SPRITE_H);
        ws_push_mark_idle_roam(list, n, map_id, '7', WARDEN_FRAMES, frame_count, 15, NPC_SPRITE_W, NPC_SPRITE_H);
    }
    else if(map_id == MAP_QUARRY) {
        /* Quarry crate/shelf: same reused prop art as the CLIFFS chest
           above, just placed on their own marks instead of HOUSE's
           draw_props-only 'C'/'S' (see that function's HOUSE-only
           note) so they actually draw on this map. */
        if(!quarry_crate_looted)
            ws_push_mark(list, n, map_id, 'C', prop_crate, PROP_CRATE_W, PROP_CRATE_H);
        if(!quarry_shelf_searched)
            ws_push_mark(list, n, map_id, 'S', prop_shelf, PROP_SHELF_W, PROP_SHELF_H);
    }
    else if(map_id == MAP_REACH) {
        /* Shinigami's second appearance, once freed from the Prison --
           reuses his existing GROVE sprite/frames, same character. He
           isn't here at all until saw_shinigami_rock (not merely
           beat_shin -- he's still standing at the boulder in VELD
           until the rock-shatter event actually plays there; showing
           him here any earlier would put him in two places at once). */
        if(saw_shinigami_rock)
            ws_push_mark_idle(list, n, map_id, 'Y', SHINIGAMI_FRAMES, frame_count, 20, NPC_SPRITE_W, NPC_SPRITE_H);
    }

    /* Anne isn't tied to one map like the stationary VELD NPCs --
       her second approach now meets Max wherever she is right after
       the Cathleen fight (the GROVE, not necessarily VELD), so this
       is unconditional instead of living inside the MAP_VELD branch
       above. */
    if(anne_state)
        ws_push_walker(list, n, ANNE_FRAMES, anne_x, anne_y, anne_dir, anne_frame);
}

typedef struct {
    int map_id, px, py, party_n;
    int **ft;
    Bag *bag;
    int *marks;
    Monster *party;
    int *pn, *lead;
    const TalkBeat **seq_lines;
    int *seq_len;
    int *after, *pending;
} NpcRun;


/* Map overworld NPC mark → g_executed_mask bit (mirrors engine.ts mercyExecBit). */
static int npc_exec_bit(int map_id, char mark) {
    if(map_id == MAP_VELD && mark == 'E') return 0; /* Calder */
    if(map_id == MAP_FOREST && mark == '1') return 1;
    if(map_id == MAP_FOREST && mark == '2') return 2;
    if(map_id == MAP_FOREST && mark == '3') return 3;
    if(map_id == MAP_CLIFFS && mark == 'V') return 4; /* Sentry */
    if(map_id == MAP_CAMP && mark == 'K') return 5; /* Conscript */
    if(map_id == MAP_CAMP && mark == 'A') return 6; /* Enforcer */
    if(map_id == MAP_GROVE && mark == 'K') return 7; /* Cross */
    if(map_id == MAP_FOREST && mark == '4') return 8; /* Ranger */
    if(map_id == MAP_FOREST && mark == '5') return 9; /* Scout */
    if(map_id == MAP_RUINS && mark == '6') return 10;
    if(map_id == MAP_RUINS && mark == '7') return 11;
    if(map_id == MAP_MARSH && mark == '1') return 12;
    if(map_id == MAP_MARSH && mark == '2') return 13;
    if(map_id == MAP_REACH && mark == 'Q') return 14;
    if(map_id == MAP_REACH && mark == 'O') return 15;
    if(map_id == MAP_QUARRY && mark == '1') return 16;
    return -1;
}
/* Map trainer_kind (+ soldier_id for the generic TRAINER_SOLDIER case)
 * to the same g_executed_mask bit npc_exec_bit() assigns that NPC on
 * the map, so executing a trainer in battle actually hides them
 * afterward. Needed because trainer_kind alone doesn't distinguish
 * which of the 3 forest patrol soldiers it was -- soldier_id (their
 * index in soldiers[], 0-2) does, and lines up directly with
 * npc_exec_bit()'s forest marks '1'/'2'/'3' -> bits 1/2/3. */
static int mercy_exec_bit(int trainer_kind, int soldier_id) {
    switch(trainer_kind) {
        case TRAINER_CALDER: return 0;
        case TRAINER_SOLDIER: return (soldier_id >= 0 && soldier_id <= 2) ? soldier_id + 1 : -1;
        case TRAINER_WSOLDIER_CLIFFS: return 4;
        case TRAINER_WSOLDIER_CAMP1: return 5;
        case TRAINER_WSOLDIER_CAMP2: return 6;
        case TRAINER_WSOLDIER_GROVE: return 7;
        case TRAINER_WSOLDIER_RANGER: return 8;
        case TRAINER_WSOLDIER_SCOUT: return 9;
        case TRAINER_WSOLDIER_KEEPER: return 10;
        case TRAINER_WSOLDIER_WARDEN: return 11;
        case TRAINER_WSOLDIER_MARSH_BOG: return 12;
        case TRAINER_WSOLDIER_MARSH_REED: return 13;
        case TRAINER_WSOLDIER_QUARTZ: return 14;
        case TRAINER_WSOLDIER_OPAL: return 15;
        case TRAINER_WSOLDIER_QUARRY_DRILLER: return 16;
        default: return -1; /* wild/Mason/Mason2/Shinigami/commanderFinal: no exec bit */
    }
}
/* Applies NPC_DEFS[idx]'s currently-matched script step's effects
 * (grant/heal/marks/take_item/talk/after/pending) onto R, exactly as
 * try_npc_script()'s inner loop does once it has picked a best-match
 * index -- factored out so a direct index (already known, no
 * proximity re-scan needed) can reuse it too. See run_npc_at() below,
 * used by the Backstab "Approach" row so it triggers the same normal
 * dialogue/battle immediately instead of leaving it to a re-scan that
 * would just reopen the same Backstab prompt (the target's still
 * unspotted). Returns 0 if idx has no currently-active step (hidden/
 * flag-gated this frame). */
static int apply_npc_step(NpcRun *R, int idx) {
    int si, talk, gi;
    const NpcStep *st;
    si = npc_match_step(&NPC_DEFS[idx], R->ft, R->party_n);
    if(si < 0) return 0;
    st = &NPC_STEPS[si];
    talk = st->talk;
    if(st->talk_if >= 0)
        talk = npc_flag_on(st->talk_if, R->ft, R->party_n) ? st->talk : st->talk_else;
    if(st->set_flag >= 0) npc_flag_set(st->set_flag, R->ft);
    for(gi = 0; gi < st->g_n; gi++) {
        int *slot = bag_field(R->bag, st->g_item[gi]);
        *slot += st->g_qty[gi];
    }
    if(st->g_sp >= 0 && *R->pn == 0) {
        R->party[0] = mint_monster(st->g_sp, st->g_lv);
        *R->pn = 1;
        *R->lead = 0;
        dex_note_caught(st->g_sp);
    }
    if(st->take_item >= 0) {
        int *slot = bag_field(R->bag, st->take_item);
        if(*slot > 0) (*slot)--;
    }
    if(st->heal) heal_party(R->party, *R->pn);
    if(st->marks) *R->marks += st->marks;
    if(talk >= 0 && talk < TALK_TABLE_N) {
        *R->seq_lines = TALK_PTRS[talk];
        *R->seq_len = TALK_COUNTS[talk];
    }
    *R->after = st->after;
    *R->pending = st->pending;
    return 1;
}

static int try_npc_script(NpcRun *R) {
    unsigned char used[64];
    int i, guard;
    if(NPC_DEF_N > 64) return 0;
    for(i = 0; i < NPC_DEF_N; i++) used[i] = 0;
    for(guard = 0; guard < NPC_DEF_N; guard++) {
        int best = -1, best_d = 0x7fffffff;
        for(i = 0; i < NPC_DEF_N; i++) {
            int mx, my, dx, dy, d;
            int half_w, left, right, top, bottom;
            if(used[i] || NPC_DEFS[i].map_id != R->map_id) continue;
            {
                int ebit = npc_exec_bit(NPC_DEFS[i].map_id, NPC_DEFS[i].mark);
                if(ebit >= 0 && (g_executed_mask & (1u << ebit))) continue;
            }
            mark_center(R->map_id, NPC_DEFS[i].mark, &mx, &my);
            /* Box test against the target's own footprint (NPC_DEFS[i].w/h,
               already scaled to this port's tile size by the baker) plus
               INTERACT_BUFFER on every side, feet-anchored the same way
               it's drawn: box bottom = mark y, box top = mark y - h.
               Matches engine.ts's runClosestNpc() exactly -- neither port
               has ever used facing/direction here, only proximity, and
               now both size that proximity off the sprite itself instead
               of one flat radius. */
            half_w = NPC_DEFS[i].w / 2 + INTERACT_BUFFER;
            left = mx - half_w;
            right = mx + half_w;
            bottom = my + INTERACT_BUFFER;
            top = my - NPC_DEFS[i].h - INTERACT_BUFFER;
            if(R->px < left || R->px > right || R->py < top || R->py > bottom) continue;
            dx = R->px - mx; dy = R->py - my;
            d = dx * dx + dy * dy;
            if(d <= best_d) { best_d = d; best = i; }
        }
        if(best < 0) return 0;
        used[best] = 1;
        if(apply_npc_step(R, best)) return 1;
    }
    return 0;
}

/* Leg 2.12 Bowie Knife: maps an NPC_PENDING_* id to its TRAINER_KITS
 * index, the same lookup each POST_WSOLDIER_* battle-start case does
 * inline -- reused here to sum a Backstab target's foe levels (for
 * the marks payout) without ever building a battle struct. -1 for a
 * pending with no kit (shouldn't happen for a roamable wsoldier). */
static int kit_for_pending(int pending) {
    switch(pending) {
        case NPC_PENDING_CROSS: return KIT_CROSS;
        case NPC_PENDING_CONSCRIPT: return KIT_CONSCRIPT;
        case NPC_PENDING_ENFORCER: return KIT_ENFORCER;
        case NPC_PENDING_SENTRY: return KIT_SENTRY;
        case NPC_PENDING_FOREST_RANGER: return KIT_FOREST_RANGER;
        case NPC_PENDING_FOREST_SCOUT: return KIT_FOREST_SCOUT;
        case NPC_PENDING_RUINS_KEEPER: return KIT_RUINS_KEEPER;
        case NPC_PENDING_RUINS_WARDEN: return KIT_RUINS_WARDEN;
        case NPC_PENDING_QUARTZ: return KIT_QUARTZ;
        case NPC_PENDING_QUARRY_DRILLER: return KIT_QUARRY_DRILLER;
        case NPC_PENDING_OPAL: return KIT_OPAL;
        case NPC_PENDING_MARSH_BOG: return KIT_MARSH_BOG;
        case NPC_PENDING_MARSH_REED: return KIT_MARSH_REED;
        case NPC_PENDING_COMMANDER_FINAL: return KIT_COMMANDER_FINAL;
        case NPC_PENDING_LEAD: return KIT_LIEUTENANT_LEAD;
        case NPC_PENDING_HEAVENFALL_GRAVE: return KIT_HEAVENFALL_GRAVE;
        default: return -1;
    }
}

/* Leg 2.12 Bowie Knife: best-match proximity scan for a Backstab
 * target, mirroring try_npc_script()'s own box test exactly (same
 * NPC_DEFS[i].w/h + INTERACT_BUFFER footprint) but filtered down to
 * roamable wsoldier trainers that are still fightable and haven't
 * started a chase (g_roamers[i].chase) -- i.e. "hasn't spotted the
 * player first". Only called from the manual Z/A interact path, and
 * only while bag.bowieKnife > 0, so a knifeless player always falls
 * straight through to normal try_npc_script() dialogue. Returns the
 * nearest matching NPC_DEFS index, or -1. */
/* Cathleen and Shinigami deliberately excluded (per request): both
   still fight normally via the ordinary talk-then-battle path, just
   never through Backstab -- matches engine.ts's isFightAfter(). */
static int npc_after_is_fight(int after) {
    return after == NPC_AFTER_WSOLDIER
        || after == NPC_AFTER_CALDER;
}

static int npc_on_warp_gate(int map_id, char mark) {
    int i;
    for(i = 0; i < WARP_N; i++)
        if(WARPS[i].from_map == map_id && WARPS[i].tile == mark) return 1;
    return 0;
}

static int find_backstab_target(int map_id, int ppx, int ppy, int **ft, int party_n) {
    int i, best = -1, best_d = 0x7fffffff;
    for(i = 0; i < NPC_DEF_N; i++) {
        int mx, my, dx, dy, d;
        int half_w, left, right, top, bottom;
        int si, ebit;
        const NpcStep *st;
        if(NPC_DEFS[i].map_id != map_id) continue;
        if(npc_on_warp_gate(map_id, NPC_DEFS[i].mark)) continue;
        ebit = npc_exec_bit(NPC_DEFS[i].map_id, NPC_DEFS[i].mark);
        if(ebit >= 0 && (g_executed_mask & (1u << ebit))) continue;
        si = npc_match_step(&NPC_DEFS[i], ft, party_n);
        if(si < 0) continue;
        st = &NPC_STEPS[si];
        if(!npc_after_is_fight(st->after)) continue;
        if(npc_def_roamable(i)) {
            roamer_ensure(i);
            if(g_roamers[i].chase) continue;
            if(roamer_los(map_id, g_roamers[i].x, g_roamers[i].y, g_roamers[i].dir, ppx / TILE, ppy / TILE)) continue;
            mx = (int)g_roamers[i].x; my = (int)g_roamers[i].y;
        } else {
            mark_center(map_id, NPC_DEFS[i].mark, &mx, &my);
        }
        half_w = NPC_DEFS[i].w / 2 + INTERACT_BUFFER;
        left = mx - half_w;
        right = mx + half_w;
        bottom = my + INTERACT_BUFFER;
        top = my - NPC_DEFS[i].h - INTERACT_BUFFER;
        if(ppx < left || ppx > right || ppy < top || ppy > bottom) continue;
        dx = ppx - mx; dy = ppy - my;
        d = dx * dx + dy * dy;
        if(d <= best_d) { best_d = d; best = i; }
    }
    return best;
}


/* ensureSoldiers(): id/name/species/level, matching state.lua's
   patrol/scout/sentry entries (their patrol minv/maxv/axis/LOS isn't
   ported -- see the section comment above). */
typedef struct {
    char mark;
    const char *name;
    int species;
    int lv;
} SoldierDef;

static const SoldierDef SOLDIERS[3] = {
    { '1', "PATROL", SP_BRIARFOX, 4 },
    { '2', "SCOUT",  SP_MOSSBACK, 4 },
    { '3', "SENTRY", SP_RAZORBAT, 5 },
};

/* Real-time actor movement constants, ported from engine.ts's own
   dt-based speeds (52/36/112/80 px/sec for approach/patrol/chase/
   leave) scaled by this port's TILE=20 vs the original's TILE=32
   (0.625x), then converted to a fixed per-frame step assuming a
   60Hz vblank-paced loop (dt = 1/60) since this port has no real
   delta-time -- see the "no dt" note in the movement update below. */
#define ACTOR_SPD_APPROACH (32.5f / 60.0f)
#define ACTOR_SPD_PATROL   (22.5f / 60.0f)
#define ACTOR_SPD_CHASE    (70.0f / 60.0f)
#define ACTOR_SPD_LEAVE    (50.0f / 60.0f)
#define ACTOR_REACH_DIST   22.5f   /* 36 * 0.625, engine.ts's dist<36 */
#define ACTOR_CHASE_CATCH  22.5f

/* soldierLos(): raycast one tile at a time along the soldier's facing
   direction until it hits a solid tile (miss) or the player's tile
   (spotted). dir codes match pdir: 0=down,1=up,2=left,3=right. */
static int soldier_los(int map_id, float sx, float sy, int dir, int ppx, int ppy) {
    int stx = (int)sx / TILE, sty = (int)sy / TILE;
    int ptx = ppx / TILE, pty = ppy / TILE;
    int dx = (dir == 2) ? -1 : (dir == 3) ? 1 : 0;
    int dy = (dir == 1) ? -1 : (dir == 0) ? 1 : 0;
    int i, maxs;
    if(dx == 0 && dy == 0) return 0;
    maxs = MAPS[map_id].cols > MAPS[map_id].rows_n ? MAPS[map_id].cols : MAPS[map_id].rows_n;
    for(i = 1; i <= maxs; i++) {
        int tx = stx + dx * i, ty = sty + dy * i;
        char ch = tile_at(map_id, tx, ty);
        if(tile_is_solid(ch)) return 0;
        if(tx == ptx && ty == pty) return 1;
    }
    return 0;
}

/* hitActor(): a live world actor blocks player movement like a solid
   tile, matching state.lua's blocked() actor check. Only actors that
   are actually standing in the world block -- Mason/Anne mid-approach
   or mid-leave don't (the reference doesn't collide against them
   either while they're walking toward/away from the player), nor does
   a beaten soldier (soldier_beaten). Radius is a small fixed circle
   around the actor's feet, not its full sprite box, so the player can
   still walk up close enough to trigger the proximity-interact/ambush
   checks that sit right next to this collision radius. */
static int mark_hit(int map_id, char mark, int cx, int cy, int r2) {
    int mx, my, dx, dy;
    mark_center(map_id, mark, &mx, &my);
    dx = cx - mx; dy = cy - my;
    return dx * dx + dy * dy <= r2;
}

/* Drop-in for mark_hit() that follows a roaming trainer to its live
   chase position instead of its fixed mark, and isn't solid at all
   while mid-chase (it catches the player by proximity, not by
   blocking their tile -- same as the FOREST soldiers just above).
   Any mark that isn't a roamable NpcDef (or hasn't been touched by
   update_roamers() yet) falls straight through to plain mark_hit(). */
static int roamer_hit(int map_id, char mark, int cx, int cy, int r2) {
    int idx = npc_def_index_for(map_id, mark);
    int dx, dy;
    if(idx < 0 || !npc_def_roamable(idx) || !g_roamers[idx].inited)
        return mark_hit(map_id, mark, cx, cy, r2);
    if(g_roamers[idx].chase) return 0;
    dx = cx - (int)g_roamers[idx].x;
    dy = cy - (int)g_roamers[idx].y;
    return dx * dx + dy * dy <= r2;
}

static int actor_blocks(int map_id, int cx, int cy,
                         int mason_state, float mason_x, float mason_y,
                         int anne_state, float anne_x, float anne_y,
                         const Soldier *soldiers, const int *soldier_beaten,
                         int cath_caught, int beat_shin,
                         int beat_calder, int has_scroll, int saw_shinigami_rock) {
    int dx, dy;
#define HIT_R2 81 /* 9px radius, squared */
    if(map_id == MAP_VELD) {
        if(mason_state == 2) {
            dx = cx - (int)mason_x; dy = cy - (int)mason_y;
            if(dx * dx + dy * dy <= HIT_R2) return 1;
        }
        if(anne_state == 2) {
            dx = cx - (int)anne_x; dy = cy - (int)anne_y;
            if(dx * dx + dy * dy <= HIT_R2) return 1;
        }
        if(mark_hit(map_id, 'K', cx, cy, HIT_R2)) return 1;
        if(mark_hit(map_id, 'I', cx, cy, HIT_R2)) return 1;
        if(roamer_hit(map_id, 'V', cx, cy, HIT_R2)) return 1;
        if(mark_hit(map_id, 'A', cx, cy, HIT_R2)) return 1;
        if(mark_hit(map_id, 'Q', cx, cy, HIT_R2)) return 1;
        if(mark_hit(map_id, 'J', cx, cy, HIT_R2)) return 1;
        if(roamer_hit(map_id, 'S', cx, cy, HIT_R2)) return 1;
        /* Calder and the Heavenfall Priestess stand directly in the
           only walkable approach to their gates (east/south) -- see
           the wall edits around VELD marks 'E'/'4' in maps.json. Each
           steps aside (stops blocking, matches web's npcPassable())
           once its condition is met, without disappearing. */
        if(!beat_calder && mark_hit(map_id, 'E', cx, cy, HIT_R2)) return 1;
        if(!has_scroll && mark_hit(map_id, '4', cx, cy, HIT_R2)) return 1;
        /* The boulder (mark 'Y') seals the sole approach to the west
           gate until the rock-shatter event actually plays, not merely
           until Shinigami is beaten (see collect_npcs() above); his
           own sprite (mark '9') takes over blocking for that window. */
        if(!saw_shinigami_rock && mark_hit(map_id, 'Y', cx, cy, HIT_R2)) return 1;
        if(beat_shin && !saw_shinigami_rock && mark_hit(map_id, '9', cx, cy, HIT_R2)) return 1;
    }
    else if(map_id == MAP_FOREST && soldiers) {
        int i;
        for(i = 0; i < 3; i++) {
            if(soldier_beaten[i]) continue;
            dx = cx - (int)soldiers[i].x; dy = cy - (int)soldiers[i].y;
            if(dx * dx + dy * dy <= HIT_R2) return 1;
        }
    }
    else if(map_id == MAP_GROVE) {
        if(!beat_shin && mark_hit(map_id, '9', cx, cy, HIT_R2)) return 1;
        if(!cath_caught && mark_hit(map_id, '8', cx, cy, HIT_R2)) return 1;
        if(roamer_hit(map_id, 'K', cx, cy, HIT_R2)) return 1;
    }
    else if(map_id == MAP_CAMP) {
        if(mark_hit(map_id, 'I', cx, cy, HIT_R2)) return 1;
        if(roamer_hit(map_id, 'K', cx, cy, HIT_R2)) return 1;
        if(roamer_hit(map_id, 'A', cx, cy, HIT_R2)) return 1;
    }
    else if(map_id == MAP_CLIFFS) {
        if(roamer_hit(map_id, 'V', cx, cy, HIT_R2)) return 1;
        if(mark_hit(map_id, 'Y', cx, cy, HIT_R2)) return 1;
    }
    else if(map_id == MAP_RUINS) {
        if(mark_hit(map_id, 'J', cx, cy, HIT_R2)) return 1;
        if(mark_hit(map_id, 'K', cx, cy, HIT_R2)) return 1;
        if(mark_hit(map_id, 'A', cx, cy, HIT_R2)) return 1;
    }
#undef HIT_R2
    return 0;
}

/* ----------------------------------------------------------------------
 * Bram's shop, ported from state.lua's updateShop() -- data.lua notes
 * this is a deliberate deviation from native/crymon.c (which only
 * draws the shop, no purchase logic at all): the reference itself
 * ports engine.ts's working buy/sell UI instead, and so does this.
 * ---------------------------------------------------------------------- */
/* ItemDef, ITEMS, bag_field: see Bag typedef above. */

/* Buy tab always lists all 5 items; sell tab only ones actually owned
   (ownedItems()). Returns the row count and fills *rows with item
   indices (0-4) in display order, for main()'s input handling and
   draw_shop() to stay in lockstep, same pattern as the battle item
   menu above. */
#define SHOP_ROWS_SHOWN 9
/* Leg 2.6: capture crystals are the only items a shopkeeper's stock
   restricts (see SHOP_CRYSTAL_MASK) -- every other purchasable item is
   sold everywhere, same as before. Selling isn't restricted either,
   matching the web engine. */
/* Per-keeper shelf stock, 1-10 units per item, rolled fresh by
   roll_all_shop_stock() (called from heal_party() -- every rest, real
   bed or script `heal`, refreshes every merchant at once, matching
   web's sleepHeal()). A plain global rather than threaded through
   every shop function's parameter list (shop_free[] does that, but
   as a flat 1-D array threading it is cheap; this is a 2-D per-item
   table and the extra parameter would touch shop_rows/draw_shop/the
   buy handler/try_npc_script's NpcRun all at once for no real
   benefit in a single-threaded game). */
static int shop_stock[SHOP_CRYSTAL_MASK_N][ITEM_COUNT];

static void roll_shop_stock(int keeper) {
    int i;
    for(i = 0; i < ITEM_COUNT; i++) shop_stock[keeper][i] = irand(1, 10);
}

static void roll_all_shop_stock(void) {
    int k;
    for(k = 0; k < SHOP_CRYSTAL_MASK_N; k++) roll_shop_stock(k);
}

static int shop_rows(const Bag *bag, int sell_tab, int shop_keep_id, int dray_knife_offered, int rows[ITEM_COUNT]) {
    int n = 0, i;
    int mask = (shop_keep_id >= 0 && shop_keep_id < SHOP_CRYSTAL_MASK_N)
        ? SHOP_CRYSTAL_MASK[shop_keep_id] : SHOP_CRYSTAL_DEFAULT_MASK;
    for(i = 0; i < ITEM_COUNT; i++) {
        int owned = *bag_field((Bag *)bag, i);
        if(!sell_tab) {
            if(ITEMS[i].buy <= 0) continue;
            if(ITEM_FX[i].kind == 4 && !((mask >> i) & 1)) continue;
            if(shop_keep_id >= 0 && shop_keep_id < SHOP_CRYSTAL_MASK_N && shop_stock[shop_keep_id][i] <= 0) continue;
            /* Bowie Knife (item index 19, matches bag_field()'s new
               case 19): Dray-only (shop_keep_id 3, see SHOP_IDS in
               bake_content.py), only after his one-time reputation-
               warning line, and only until the player owns one --
               there's only ever one in the game. */
            if(i == 19 && (shop_keep_id != 3 || !dray_knife_offered || owned > 0)) continue;
            rows[n++] = i;
        } else if(owned > 0 && ITEMS[i].sell > 0) {
            rows[n++] = i;
        }
    }
    /* Bowie Knife (item 19) at top of Dray's buy list when present. */
    if(!sell_tab && n > 1) {
        int j, knife = -1;
        for(j = 0; j < n; j++) if(rows[j] == 19) { knife = j; break; }
        if(knife > 0) {
            int tmp = rows[knife];
            for(j = knife; j > 0; j--) rows[j] = rows[j - 1];
            rows[0] = tmp;
        }
    }
    return n;
}

static const char *const SHOP_TITLES[SHOP_CRYSTAL_MASK_N] = {
    "BRAMS STALL", "ORENS STALL", "FENNS STALL", "DRAYS STALL",
};

/* Leg 2.10: buy prices scale with reputation. Positive: -1% per point
   (floor LOGIC_REP_MIN_PRICE, never free from this alone). Negative:
   +5% per point. Sell prices are unchanged. At +100 the next purchase
   from this merchant is free once (shop_free[]). */
static int shop_buy_price(int base, int reputation) {
    int p;
    if(reputation > 0) {
        p = base * (100 - reputation * LOGIC_REP_PRICE_POS_PCT) / 100;
        if(p < LOGIC_REP_MIN_PRICE) p = LOGIC_REP_MIN_PRICE;
        return p;
    }
    if(reputation < 0) {
        p = base * (100 + (-reputation) * LOGIC_REP_PRICE_NEG_PCT) / 100;
        if(p < LOGIC_REP_MIN_PRICE) p = LOGIC_REP_MIN_PRICE;
        return p;
    }
    return base;
}

/* Half of list buy price, then +1% per +rep / -1% per -rep. Floor 1 mark. */
static int shop_sell_price(int buy, int reputation) {
    int base = buy / 2;
    int p = base * (100 + reputation) / 100;
    if(p < LOGIC_REP_MIN_PRICE) p = LOGIC_REP_MIN_PRICE;
    return p;
}

static int shop_gift_open(int reputation, int shop_keep_id, const int *shop_free) {
    if(reputation < LOGIC_REP_FREE_AT) return 0;
    if(shop_keep_id < 0 || shop_keep_id >= SHOP_CRYSTAL_MASK_N) return 0;
    return !shop_free[shop_keep_id];
}

static void draw_shop(const Bag *bag, int marks, int sell_tab, int cur, int shop_keep_id,
                      int reputation, const int *shop_free, int dray_knife_offered) {
    int rows[ITEM_COUNT];
    int n = shop_rows(bag, sell_tab, shop_keep_id, dray_knife_offered, rows);
    int y = MENU_Y + 40;
    int i;
    char buf[16];
    const char *title = (shop_keep_id >= 0 && shop_keep_id < SHOP_CRYSTAL_MASK_N)
        ? SHOP_TITLES[shop_keep_id] : "TRADERS STALL";

    draw_menu_frame(title, "B CLOSE");

    draw_text_s(sell_tab ? "BUY  >SELL" : ">BUY  SELL", MENU_X + 8, MENU_Y + 24,
                rgb565(197, 206, 198), MENU_SCALE);
    {
        int mn = s_cat(buf, 0, "MARKS ");
        mn = s_cat_uint(buf, mn, marks);
        buf[mn] = 0;
        draw_text_s(buf, MENU_X + MENU_W - 8 - text_width_s(buf, MENU_SCALE),
                    MENU_Y + 24, rgb565(143, 74, 64), MENU_SCALE);
    }

    /* Leg 2.5: more buyable items than fit in one screen now (n can
       exceed what SHOP_ROWS_SHOWN rows of MENU_ROW_H leave room for),
       so this scrolls around cur the same way draw_bag_menu does. */
    {
        int start = cur - SHOP_ROWS_SHOWN / 2;
        int max_start = n - SHOP_ROWS_SHOWN;
        if(max_start < 0) max_start = 0;
        if(start < 0) start = 0;
        if(start > max_start) start = max_start;
        for(i = start; i < start + SHOP_ROWS_SHOWN && i < n; i++) {
            int idx = rows[i];
            int price = sell_tab ? shop_sell_price(ITEMS[idx].buy, reputation) : shop_buy_price(ITEMS[idx].buy, reputation);
            int owned = *bag_field((Bag *)bag, idx);
            int qty = sell_tab ? owned
                : (shop_keep_id >= 0 && shop_keep_id < SHOP_CRYSTAL_MASK_N ? shop_stock[shop_keep_id][idx] : 0);
            int gift = !sell_tab && shop_gift_open(reputation, shop_keep_id, shop_free);
            char row[40];
            int rn = s_cat(row, 0, ITEMS[idx].name);
            if(gift) {
                rn = s_cat(row, rn, " FREE X");
            } else {
                rn = s_cat(row, rn, " ");
                rn = s_cat_uint(row, rn, price);
                rn = s_cat(row, rn, "M X");
            }
            rn = s_cat_uint(row, rn, qty);
            row[rn] = 0;
            draw_menu_row_icon(ITEM_ICONS[idx], row, i, cur, y);
            y += MENU_ROW_H;
        }
    }
}

/* ----------------------------------------------------------------------
 * Ending screen, ported from render.lua's drawDemoEnd(): data.DEMO_END,
 * reached via the Grove/Shinigami/Anne chain and the resurrection
 * choice (draw_choice()) regardless of which the player picks. Steps
 * through its lines on A and returns to the title screen at the end.
 * ---------------------------------------------------------------------- */
static void draw_ending(const char *const *lines, int n, int i) {
    vram_clear();
    draw_text_center_s("CRYMON", SCREEN_W / 2, 24, 0xFFFF, 2);
    draw_text_center_s("GAME OVER", SCREEN_W / 2, 48, rgb565(143, 74, 64), 1);
    if(i < n)
        draw_wrapped(lines[i], 12, 80, rgb565(197, 206, 198), DIALOGUE_SCALE,
                     (SCREEN_W - 24) / CHAR_CELL(DIALOGUE_SCALE), 9);
    draw_text_center_s("A TO CONTINUE", SCREEN_W / 2, SCREEN_H - 20,
                        rgb565(90, 122, 82), DIALOGUE_SCALE);
}

/* interact() in state.lua: closest of U/B/S/C within a 36px radius
   (36*36=1296) in the original's 32px-tile space; scaled to our 20px
   tiles that's a 22.5px radius (22*22=484). */
/* HOUSE-only, matching interact()'s MAP_HOUSE branch -- callers only
   invoke this when map_id == MAP_HOUSE. */
static char __attribute__((unused))
closest_mark(int px, int py) {
    static const char marks[4] = { 'U', 'B', 'S', 'C' };
    int i;
    int best = 484, best_i = -1;

    for(i = 0; i < 4; i++) {
        int mx, my, dx, dy, d;
        mark_center(MAP_HOUSE, marks[i], &mx, &my);
        dx = px - mx;
        dy = py - my;
        d = dx * dx + dy * dy;
        if(d <= best) {
            best = d;
            best_i = i;
        }
    }
    return best_i >= 0 ? marks[best_i] : 0;
}

/* state.lua's warp(): places the player just past the destination
   mark, facing back the way they came (down if arriving from the
   south, up otherwise) -- matches doorLock's 20-frame cooldown below
   against instantly re-triggering the door tile on arrival. */
/* dir: 0=down,1=up,2=left,3=right (matches WarpDef.dir/pdir). The spawn
   tile is pushed one tile-plus-a-bit further along the arrival facing so
   the player lands just clear of the door instead of on top of it --
   mirrors web's warpTo() oy/ox nudge, same +TILE+8 / -TILE magnitudes on
   whichever axis the direction moves along. */
static void do_warp(int *map_id, int *px, int *py, int *pdir,
                     int to_map, char mark, int dir,
                     int *banner_timer) {
    int col, row, sx, sy;
    *map_id = to_map;
    find_mark(to_map, mark, &col, &row);
    sx = col * TILE + TILE / 2;
    sy = row * TILE + TILE / 2;
    switch(dir) {
        case 2: /* left */
            *px = sx - TILE;
            *py = sy;
            break;
        case 3: /* right */
            *px = sx + TILE + 8;
            *py = sy;
            break;
        case 1: /* up */
            *px = sx;
            *py = sy - TILE;
            break;
        default: /* 0 = down */
            *px = sx;
            *py = sy + TILE + 8;
            break;
    }
    *pdir = dir;
    *banner_timer = MAP_BANNER_TOTAL;
}

/* post_action values -- moved to file scope (originally a run of
   #defines partway through main()'s own locals) so npc_after_to_post_
   action() below, a top-level function, can use them too; the
   preprocessor doesn't care about C block scope either way, so this
   is a pure relocation with no behavior change. */
#define POST_NONE        0
#define POST_CALDER      1
#define POST_MASON       2
#define POST_SHINIGAMI   3
#define POST_SOLDIER     4
#define POST_CATHLEEN    5
#define POST_SHOP        6
#define POST_DRAY_KNIFE_SHOP 35
#define POST_MASON_LEAVE 7
#define POST_ANNE_LEAVE  8
#define POST_BED_HEAL    10
#define POST_MASON2      11
#define POST_OPEN_CHOICE 12
#define POST_ENDING_FINAL 13
#define POST_WSOLDIER_CLIFFS 14
#define POST_WSOLDIER_CAMP1  15
#define POST_WSOLDIER_CAMP2  16
#define POST_WSOLDIER_GROVE  17
#define POST_WSOLDIER_RANGER 18
#define POST_WSOLDIER_SCOUT  19
#define POST_WSOLDIER_KEEPER 20
#define POST_WSOLDIER_WARDEN 21
#define POST_WSOLDIER_QUARTZ 22
#define POST_WSOLDIER_QUARRY_DRILLER 23
#define POST_WSOLDIER_OPAL 24
#define POST_WSOLDIER_MARSH_BOG 25
#define POST_WSOLDIER_MARSH_REED 26
#define POST_WSOLDIER_COMMANDER_FINAL 27
#define POST_CREDITS_FINAL 28
#define POST_OPEN_MERCY 29
#define POST_WSOLDIER_LEAD 30
#define POST_WSOLDIER_HEAVENFALL_GRAVE 31
#define POST_LEAD_GAMEOVER 32
#define POST_HFGAMEOVER_SCREAM 33
#define POST_PRIESTESS_TELEPORT 34
/* Every shopkeeper reuses POST_SHOP/draw_shop() -- shop_keep_id (set
   from the NpcStep's pending slot, see NPC_AFTER_SHOP above) picks the
   title and crystal-tier stock, no separate post_action per merchant. */

/* Maps an applied step's (after, pending) pair to the post_action the
 * manual interact handler dispatches on once its dialogue closes --
 * factored out of that handler so run_npc_at() (Backstab's Approach
 * row) can reach the exact same post_action from a direct index
 * instead of duplicating this switch. *shop_keep_id_out is only
 * written for NPC_AFTER_SHOP. */
static int npc_after_to_post_action(int npc_after, int npc_pending, int *shop_keep_id_out) {
    switch(npc_after) {
        case NPC_AFTER_BED_HEAL:
            return POST_BED_HEAL;
        case NPC_AFTER_SHOP:
            *shop_keep_id_out = npc_pending;
            return POST_SHOP;
        case NPC_AFTER_CALDER:
            return POST_CALDER;
        case NPC_AFTER_CATHLEEN:
            return POST_CATHLEEN;
        case NPC_AFTER_SHINIGAMI:
            return POST_SHINIGAMI;
        case NPC_AFTER_WSOLDIER:
            if(npc_pending == NPC_PENDING_CROSS) return POST_WSOLDIER_GROVE;
            if(npc_pending == NPC_PENDING_CONSCRIPT) return POST_WSOLDIER_CAMP1;
            if(npc_pending == NPC_PENDING_ENFORCER) return POST_WSOLDIER_CAMP2;
            if(npc_pending == NPC_PENDING_SENTRY) return POST_WSOLDIER_CLIFFS;
            if(npc_pending == NPC_PENDING_FOREST_RANGER) return POST_WSOLDIER_RANGER;
            if(npc_pending == NPC_PENDING_FOREST_SCOUT) return POST_WSOLDIER_SCOUT;
            if(npc_pending == NPC_PENDING_RUINS_KEEPER) return POST_WSOLDIER_KEEPER;
            if(npc_pending == NPC_PENDING_RUINS_WARDEN) return POST_WSOLDIER_WARDEN;
            if(npc_pending == NPC_PENDING_QUARTZ) return POST_WSOLDIER_QUARTZ;
            if(npc_pending == NPC_PENDING_QUARRY_DRILLER) return POST_WSOLDIER_QUARRY_DRILLER;
            if(npc_pending == NPC_PENDING_OPAL) return POST_WSOLDIER_OPAL;
            if(npc_pending == NPC_PENDING_MARSH_BOG) return POST_WSOLDIER_MARSH_BOG;
            if(npc_pending == NPC_PENDING_MARSH_REED) return POST_WSOLDIER_MARSH_REED;
            if(npc_pending == NPC_PENDING_COMMANDER_FINAL) return POST_WSOLDIER_COMMANDER_FINAL;
            if(npc_pending == NPC_PENDING_LEAD) return POST_WSOLDIER_LEAD;
            if(npc_pending == NPC_PENDING_HEAVENFALL_GRAVE) return POST_WSOLDIER_HEAVENFALL_GRAVE;
            return POST_NONE;
        case NPC_AFTER_PRIESTESS_TELEPORT:
            return POST_PRIESTESS_TELEPORT;
        default:
            return POST_NONE;
    }
}

void main(void) {
    int state = 0; /* 0 = title screen, 1 = starting room */
    u32 frame_count = 0;
    int prev_start = 0, prev_a = 0, prev_b = 0, prev_y = 0, prev_x = 0;
    int prev_up = 0, prev_down = 0, prev_left = 0, prev_right = 0;
    int map_id = MAP_HOUSE;
    int px, py, pdir = 0; /* dir: 0=down,1=up,2=left,3=right */
    int anim_counter = 0; /* see draw_player's comment */
    int player_speed_frac = 0; /* Leg 2.1: sub-pixel accumulator so the
                                   player's average speed matches web's
                                   84 px/sec despite only ever moving a
                                   whole number of pixels per frame --
                                   see the movement block below */
    int col, row;
    int cam_x, cam_y;
    u16 raw;
    int start_now, a_now, b_now, y_now, x_now, up_now, down_now, left_now, right_now;

    /* Frames left before a door tile can trigger another warp,
       matching state.lua's G.doorLock (set to 20 on spawn/warp,
       ticked down by 1 per world-state frame). */
    int door_lock = 0;

    /* Room state, matching state.lua's G.gotShelf / G.lootedCrate /
       G.bag (data.START_BAG) / G.marks (data.START_MARKS). No HP/SP
       system existed until this step; the bed's "full heal"
       (state.lua's fullHeal()) still has nothing to do here beyond
       showing its dialogue, since it's a full-party heal and this
       port's only source of a party member is the shelf. */
    int got_shelf = 0, looted_crate = 0;
    /* salve, bandage, bitterroot, dust, gem, sunbalm, warroot, smokebomb, greatcrystal */
    Bag bag = START_BAG_INIT;
    int marks = START_MARKS;

    /* G.party, capped at data.PARTY_MAX (6); this port's only ways to
       grow it are the shelf's starter grant and a battle capture --
       no NPC gifts, no other starters. lead mirrors G.lead (0-based
       here). */
    Monster party[6];
    int party_n = 0, lead = 0;
    int catch_swap = 0;
    Monster pending_catch;

    /* In-battle state (see the Battle section above); in_battle == 0
       means the world is showing normally. enc_lock/last_tx/last_ty
       are tryEncounter()'s G.encLock/G.lastTx/G.lastTy. */
    int in_battle = 0;
    Battle battle;
    int enc_lock = 8, last_tx = -1, last_ty = -1;

    /* draw_battle_sprites' enter/faint animation timestamps -- see its
       own comment. Tracked here by comparing each side's species/hp
       frame to frame rather than threading state through every single
       mint_monster()/battle.pl = party[lead] call site: a species
       change (a fresh battle, or a bench monster swapping in) arms
       enter_t, hp dropping to 0 arms faint_t, and leaving battle
       clears every timer so the next one starts clean. 0 means "no
       timer armed" (frame_count is never 0 by the time a battle can
       start). */
    u32 battle_foe_enter_t = 0, battle_foe_faint_t = 0;
    u32 battle_pl_enter_t = 0, battle_pl_faint_t = 0;
    int battle_prev_foe_species = -1, battle_prev_pl_species = -1;
    int battle_prev_foe_hp = -1, battle_prev_pl_hp = -1;
    int battle_prev_after = -1;
    int battle_was_active = 0;

    /* 0 = no menu, 1 = bag, 2 = party. Opened from the world with Y /
       START (state.lua's selectPressed()/startPressed() -- there's no
       Select button on a Dreamcast pad, so Y stands in for it), closed
       with B (state.lua's cancelPressed(), which also accepts start
       and select; B alone is enough here since neither Y nor START
       need a second meaning while a menu is open). */
    int menu_mode = 0;
    int pause_cur = 0;
    int dex_cur = 0;
    int dex_entry = 0;
    int title_cur = 0;
    int have_save = 0;
    int party_cur = 0; /* cursor row inside the party menu */
    int party_detail = 0; /* party menu: 0 list, 1 viewing party_cur's detail */
    int bag_cur = 0; /* cursor row inside the bag menu */
    int heal_item = -1; /* -1 = not choosing a heal target, else bag_cur (0 salve, 1 wrap) */

    /* HUD toast, matching state.lua's G.hud/G.hudT/note(): a small
       banner (lead-switch confirmation, the post-win "grew to lv N"/
       "stands over the grass" line) that freezes world movement like
       a dialogue box until it either times out or the player presses
       A/B to dismiss it early. 720 frames at 60fps == note()'s own
       12-second hudT budget. */
    char hud_flash[40] = { 0 };
    int hud_t = 0;
#define HUD_NOTE_FRAMES 720

    /* draw_map_banner()'s countdown -- armed by do_warp() on every map
       transition, ticks down every frame regardless of menus/dialogue
       so it always finishes fading out on its own. */
    int map_banner_timer = 0;

    /* Screen fade (bed heal, a party wipe teleporting home): 0 idle,
       1 fading to black, 2 holding one black frame while fade_action
       actually happens (teleport/heal, so it's never visible mid-
       transition), 3 fading back in. Runs as a straight post-process
       over whatever's drawn each frame (apply_fade(), called at the
       very end of the draw dispatch below), so it doesn't care
       whether the world or the battle screen is underneath it, and
       ticks/draws every frame regardless of state/in_battle --
       world movement and battle input are the only things gated on
       fade_state == 0 (see their own gates further down). */
    int fade_state = 0;
    int fade_timer = 0;
    int fade_action = 0;
/* FADE_NONE/OUT/HOLD/IN live up by apply_fade(), which fade_level() needs. */
#define FADE_ACTION_BED  1
#define FADE_ACTION_LOSS 2
#define FADE_ACTION_HFGAMEOVER 3
#define FADE_ACTION_PRIESTESS 4

    /* Active dialogue sequence: seq_lines/seq_len name the current
       TALK_* array, seq_beat indexes into it. seq_lines == 0 means no
       dialogue is showing. post_action fires once the sequence
       finishes (state.lua's afterTalk/beginTalkEnd): starting a
       trainer battle or opening the shop. */
    const TalkBeat *seq_lines = 0;
    int seq_len = 0, seq_beat = 0;
    int post_action = 0, post_soldier_id = 0;

    /* World NPC/pickup flags, matching state.lua's G.talkedWren etc.
       (see the world-NPC section comment above for what's ported vs
       simplified). */
    int talked_wren = 0, talked_mae = 0, talked_ivo = 0, talked_nell = 0;
    int talked_pike = 0, pike_helped = 0, nell_bonus = 0;
    int got_herb = 0, got_gem = 0, got_stump = 0, read_cart = 0;
    int beat_calder = 0, beat_mason = 0, beat_shin = 0, cath_caught = 0;
    int beat_cathleen = 0; /* set on any win vs her, not just a capture -- see tile_blocked's GROVE gate */
    int beat_wsoldier_cliffs = 0, beat_wsoldier_camp1 = 0;
    int beat_wsoldier_camp2 = 0, beat_wsoldier_grove = 0;
    int beat_forest_ranger = 0, beat_forest_scout = 0;
    int beat_ruins_keeper = 0, beat_ruins_warden = 0, badge_quartz = 0;
    int beat_quarry_driller = 0;
    int beat_marsh_bog = 0, beat_marsh_reed = 0, badge_opal = 0;
    int chose_heavenfall = 0, gauntlet_unlocked = 0, beat_heavenfall = 0, heavenfall_rep_warned = 0, title_slayer = 0, title_tamer = 0, beat_commander = 0;
    int beat_lieutenant_lead = 0;
    int dray_knife_offered = 0;
    int revived_father = 0;
    int got_chest = 0;
    int talked_tessa = 0, talked_birch = 0, talked_sable = 0;
    int talked_reach = 0;
    int saw_shinigami_rock = 0;
    int quarry_crate_looted = 0, quarry_shelf_searched = 0;
    int cage_open = 0;
    int has_scroll = 0; /* Legendary Reanimation, granted once Shinigami's win dialogue closes */
    int anne2_told = 0; /* gates Anne's second (father-died/choice) approach to firing once */
    int choice_mode = 0, choice_cur = 0; /* father-vs-Heavenfall resurrection choice screen */
    int mercy_mode = 0, mercy_cur = 0; /* Leg 2.9 post-battle mercy menu */
    int mercy_foe_levels = 0;
    /* g_executed_mask is g_executed_mask (file-static) */
        char mercy_foe_name[32];    /* Leg 2.12 Bowie Knife: Approach/Backstab prompt, opened instead of
       try_npc_script()'s normal dialogue when find_backstab_target()
       finds an eligible target (see the manual interact path below). */
    int backstab_mode = 0, backstab_cur = 0;
    int backstab_npc_idx = -1;
    /* FOREST patrol/scout/sentry live in soldiers[]/SOLDIERS[], not
       NPC_DEFS -- find_backstab_target() never sees them, so a
       Backstab prompt opened on one is tracked here instead, kept
       mutually exclusive with backstab_npc_idx (only one is ever >= 0
       at a time). */
    int backstab_soldier_idx = -1;
    int backstab_levels = 0;
    int soldier_beaten[3] = { 0, 0, 0 };
    int talked_father = 0;
    int *ft[FLAG_N];

    /* Mason/Anne real movement, matching state.lua's rival/anne
       phase machines (see the world-actors section comment further
       down for the full state chart and the formulas each number
       comes from). Positions are float since chase/approach movement
       is a normalized direction vector times a per-frame speed, not
       a whole-pixel step like the player's own dpad movement. */
    int mason_state = 0; /* 0 off, 1 approach, 2 standing (post-ambush), 3 leaving */
    float mason_x = 0.0f, mason_y = 0.0f;
    int mason_dir = 0;
    float mason_anim = 0.0f;
    int mason_rematch = 0; /* which loadout/dialogue the next ambush uses */

    /* Mason's rematch: once he's beaten AND Calder's beaten (the
       player has cleared the main VELD gauntlet), he reappears on a
       random open-world map, force-walks up and ambushes the player
       exactly like the first encounter (reusing the same mason_state
       machine, just with mason_rematch=1 picking a 3-CryMon loadout
       and different dialogue) the moment they set foot on that map.
       mason2_map is rolled once, right when beat_calder flips to 1. */
    int mason2_map = -1;
    /* -100..100, see logic.json reputation. Clamped on every write. */
    int reputation = 0;
    int mason2_done = 0;
    int shop_free[4] = { 0, 0, 0, 0 };

    /* Anne: engine.ts's maybeStartAnne() gate is battlesDone>=1 while
       on VELD (onBattleOver()/battlesDone++ fires on soldier, Mason,
       and generic wild wins -- not Calder or Shinigami, matching the
       Lua port's own audited note on selective battlesDone calls). */
    int battles = 0;
    int anne_state = 0; /* 0 off, 1 approach, 2 done-pending (gift dialogue), 3 leaving */
    float anne_x = 0.0f, anne_y = 0.0f;
    int anne_dir = 0;
    float anne_anim = 0.0f;
    int anne_gifted = 0;

    /* Soldiers: ensureSoldiers()'s 3 fixed NPCs, only meaningful once
       FOREST has been visited (soldiers_init latches that, matching
       ensureSoldiers()'s own "if already built, skip" guard). Type
       is file-scope (see above draw_npcs) since that draw function
       needs it too. */
    Soldier soldiers[3];
    int soldiers_init = 0;

    /* Shop (Bram) and ending screens. */
    int shop_open = 0, shop_sell_tab = 0, shop_cur = 0, shop_keep_id = 0;
    int ending_mode = 0; /* 0 none, 1 showing DEMO_END (the single ending) */
    int ending_i = 0;

    video_init();
    maple_init();
    chip_init();
    {
        SaveLive probe;
        have_save = save_restore(&probe);
        if(!have_save) title_cur = 1;
    }

    find_mark(MAP_HOUSE, 'P', &col, &row);
    px = col * TILE + TILE / 2;
    py = row * TILE + TILE / 2;

    /* Prime both buffers with the title screen before the main loop
       starts flipping, so the first flip doesn't show whatever
       garbage was in VRAM at boot. */
    draw_press_start(title_cur, have_save);
    fb_flip();
    draw_press_start(title_cur, have_save);

    {
        int fi;
        for(fi = 0; fi < FLAG_N; fi++) ft[fi] = 0;
        ft[FLAG_TOOK_STARTER] = &got_shelf;
        ft[FLAG_TALKED_FATHER] = &talked_father;
        ft[FLAG_LOOTED_CRATE] = &looted_crate;
        ft[FLAG_TALKED_WREN] = &talked_wren;
        ft[FLAG_BEAT_CALDER] = &beat_calder;
        ft[FLAG_READ_CART] = &read_cart;
        ft[FLAG_TALKED_MAE] = &talked_mae;
        ft[FLAG_TALKED_IVO] = &talked_ivo;
        ft[FLAG_TALKED_NELL] = &talked_nell;
        ft[FLAG_NELL_BONUS] = &nell_bonus;
        ft[FLAG_GOT_FIELD_GEM] = &got_gem;
        ft[FLAG_PIKE_HELPED] = &pike_helped;
        ft[FLAG_TALKED_PIKE] = &talked_pike;
        ft[FLAG_GOT_HERB] = &got_herb;
        ft[FLAG_GOT_STUMP] = &got_stump;
        ft[FLAG_CATHLEEN_CAUGHT] = &cath_caught;
        ft[FLAG_BEAT_SHINIGAMI] = &beat_shin;
        ft[FLAG_BEAT_CROSS] = &beat_wsoldier_grove;
        ft[FLAG_BEAT_CONSCRIPT] = &beat_wsoldier_camp1;
        ft[FLAG_BEAT_ENFORCER] = &beat_wsoldier_camp2;
        ft[FLAG_BEAT_SENTRY] = &beat_wsoldier_cliffs;
        ft[FLAG_BEAT_FOREST_RANGER] = &beat_forest_ranger;
        ft[FLAG_BEAT_FOREST_SCOUT] = &beat_forest_scout;
        ft[FLAG_BEAT_RUINS_KEEPER] = &beat_ruins_keeper;
        ft[FLAG_BEAT_RUINS_WARDEN] = &beat_ruins_warden;
        ft[FLAG_BADGE_QUARTZ] = &badge_quartz;
        ft[FLAG_BEAT_QUARRY_DRILLER] = &beat_quarry_driller;
        ft[FLAG_BEAT_MARSH_BOG] = &beat_marsh_bog;
        ft[FLAG_BEAT_MARSH_REED] = &beat_marsh_reed;
        ft[FLAG_BADGE_OPAL] = &badge_opal;
        ft[FLAG_CHOSE_HEAVENFALL] = &chose_heavenfall;
        ft[FLAG_REVIVED_FATHER] = &revived_father;
        ft[FLAG_SHOP_FREE_BRAM] = &shop_free[0];
        ft[FLAG_SHOP_FREE_OREN] = &shop_free[1];
        ft[FLAG_SHOP_FREE_FENN] = &shop_free[2];
        ft[FLAG_SHOP_FREE_DRAY] = &shop_free[3];
        ft[FLAG_BEAT_COMMANDER] = &beat_commander;
        ft[FLAG_BEAT_LIEUTENANT_LEAD] = &beat_lieutenant_lead;
        ft[FLAG_TESSA_GIFTED] = &talked_tessa;
        ft[FLAG_CHEST_LOOTED] = &got_chest;
        ft[FLAG_BIRCH_GIFTED] = &talked_birch;
        ft[FLAG_SABLE_GIFTED] = &talked_sable;
        ft[FLAG_CAGE_OPEN] = &cage_open;
        ft[FLAG_HAS_CAGE_KEY] = &bag.cageKey;
        ft[FLAG_TALKED_REACH] = &talked_reach;
        ft[FLAG_SAW_SHINIGAMI_ROCK] = &saw_shinigami_rock;
        ft[FLAG_QUARRY_CRATE_LOOTED] = &quarry_crate_looted;
        ft[FLAG_QUARRY_SHELF_SEARCHED] = &quarry_shelf_searched;
    }

    for(;;) {
        wait_vblank();
        fb_flip();
        frame_count++;
        g_xp_party = party;
        g_xp_party_n = party_n;
        g_xp_lead = lead;
        if(state == 0) chip_set_song(chip_song_title());
        else if(ending_mode) chip_set_song(chip_song_ending());
        else if(in_battle) chip_set_song(chip_song_battle(battle.wild ? 0 : 1));
        else chip_set_song(chip_song_map(map_id));
        chip_tick();

        if(map_banner_timer > 0) map_banner_timer--;

        /* Battle enter/faint animation tracking -- see the locals'
           comment. Runs before input so a faint detected by the hit
           that just landed (still this same frame, phase already
           moved to the "X FALLS" message) is caught the very next
           frame's draw, not one frame late. */
        if(in_battle) {
            if(!battle_was_active) {
                battle_prev_foe_species = -1;
                battle_prev_pl_species = -1;
                battle_prev_after = -1;
            }
            if(battle.foe.species != battle_prev_foe_species) {
                battle_foe_enter_t = frame_count;
                battle_foe_faint_t = 0;
                battle_prev_foe_species = battle.foe.species;
                battle_prev_foe_hp = battle.foe.hp;
            }
            else if(battle.foe.hp <= 0 && battle_prev_foe_hp > 0 && !battle_foe_faint_t) {
                battle_foe_faint_t = frame_count;
            }
            /* A successful capture (BAFTER_WORLD, see battle_pick_item)
               withdraws the foe from battle without necessarily
               dropping its hp to 0 -- reuses the same fade-out as
               fainting, which reads fine for "leaving the screen"
               either way instead of needing a third visual language. */
            else if(battle.after == BAFTER_WORLD && battle_prev_after != BAFTER_WORLD &&
                    !battle_foe_faint_t) {
                battle_foe_faint_t = frame_count;
            }
            battle_prev_foe_hp = battle.foe.hp;
            battle_prev_after = battle.after;

            if(battle.pl.species != battle_prev_pl_species) {
                battle_pl_enter_t = frame_count;
                battle_pl_faint_t = 0;
                battle_prev_pl_species = battle.pl.species;
                battle_prev_pl_hp = battle.pl.hp;
            }
            else if(battle.pl.hp <= 0 && battle_prev_pl_hp > 0 && !battle_pl_faint_t) {
                battle_pl_faint_t = frame_count;
            }
            battle_prev_pl_hp = battle.pl.hp;
        }
        else if(battle_was_active) {
            battle_foe_enter_t = battle_foe_faint_t = 0;
            battle_pl_enter_t = battle_pl_faint_t = 0;
            battle_prev_foe_species = battle_prev_pl_species = -1;
            battle_prev_after = -1;
        }
        battle_was_active = in_battle;

        raw = maple_poll_buttons();
        start_now = pressed(raw, CONT_START);
        a_now     = pressed(raw, CONT_A);
        b_now     = pressed(raw, CONT_B);
        y_now     = pressed(raw, CONT_Y);
        x_now     = pressed(raw, CONT_X);
        up_now    = pressed(raw, CONT_DPAD_UP);
        down_now  = pressed(raw, CONT_DPAD_DOWN);
        left_now  = pressed(raw, CONT_DPAD_LEFT);
        right_now = pressed(raw, CONT_DPAD_RIGHT);

        /* Fade tick: runs every frame regardless of state/menu/battle
           (world movement and battle input are what gate on
           fade_state == 0, not this). Each phase lasts its own budget
           from content/logic.json, so this matches the web's
           updateFade() beat for beat.

           The teleport/heal fires on ENTERING the hold, exactly as the
           web's applyFadeHold() does, so the whole hold renders fully
           black with the new scene already in place and neither scene is
           ever visible mid-transition. */
        if(fade_state == FADE_OUT) {
            fade_timer++;
            if(fade_timer >= LOGIC_FADE_OUT_FRAMES) {
                fade_state = FADE_HOLD;
                fade_timer = 0;
                if(fade_action == FADE_ACTION_BED) {
                    heal_party(party, party_n);
                }
                else if(fade_action == FADE_ACTION_LOSS) {
                    /* Only reached when !chose_heavenfall -- see
                       BAFTER_LOSS, which routes the Heavenfall-path
                       wipe through the heavenfallDevour dialogue +
                       FADE_ACTION_HFGAMEOVER instead (Leg 2 wrap gate:
                       "not a soft trip home") -- the old soft-regret
                       stub that used to live here is gone. */
                    heal_party(party, party_n);
                    map_id = MAP_HOUSE;
                    find_mark(MAP_HOUSE, 'U', &col, &row);
                    px = (col + 1) * TILE + TILE / 2;
                    py = row * TILE + TILE / 2;
                    pdir = 1; /* facing up, toward the bed */
                    last_tx = -1;
                    last_ty = -1;
                    door_lock = 20;
                }
                else if(fade_action == FADE_ACTION_PRIESTESS) {
                    /* The Heavenfall Priestess turning Max away without
                       the scroll -- same house teleport as a party
                       wipe, minus the heal (nothing was lost here). */
                    map_id = MAP_HOUSE;
                    find_mark(MAP_HOUSE, 'U', &col, &row);
                    px = (col + 1) * TILE + TILE / 2;
                    py = row * TILE + TILE / 2;
                    pdir = 1; /* facing up, toward the bed */
                    last_tx = -1;
                    last_ty = -1;
                    door_lock = 20;
                }
                else if(fade_action == FADE_ACTION_HFGAMEOVER) {
                    /* Shared by both Heavenfall-path wipes (BAFTER_LOSS)
                       and beating Lead (POST_LEAD_GAMEOVER): reload the
                       last save if one exists, else drop to the title
                       screen -- matches web's reloadLastSaveOrTitle(),
                       adapted to this port's title-screen state machine
                       instead of a silent in-place reload. */
                    SaveLive probe;
                    have_save = save_restore(&probe);
                    state = 0;
                    title_cur = have_save ? 0 : 1;
                    in_battle = 0;
                    choice_mode = 0;
                    mercy_mode = 0;
                }
            }
        }
        else if(fade_state == FADE_HOLD) {
            fade_timer++;
            if(fade_timer >= LOGIC_FADE_HOLD_FRAMES) {
                fade_state = FADE_IN;
                fade_timer = 0;
            }
        }
        else if(fade_state == FADE_IN) {
            fade_timer++;
            if(fade_timer >= LOGIC_FADE_IN_FRAMES) {
                fade_state = FADE_NONE;
                fade_timer = 0;
                g_mercy_red_fade = 0;
                fade_action = 0;
            }
        }

        if(state == 0) {
            chip_set_song(chip_song_title());
            if(up_now && !prev_up) { title_cur = 0; chip_sfx_ui(); }
            if(down_now && !prev_down) { title_cur = 1; chip_sfx_ui(); }
            if((start_now && !prev_start) || (a_now && !prev_a)) {
                int do_new = (title_cur == 1) || !have_save;
                if(title_cur == 0 && have_save) {
                    SaveLive sl;
                    if(save_restore(&sl)) {
                        int pi;
                        dex_clear();
                        map_id = sl.map_id;
                        if(map_id < 0 || map_id >= MAP_N) map_id = MAP_HOUSE;
                        px = sl.x;
                        py = sl.y;
                        pdir = sl.dir;
                        if(pdir < 0 || pdir > 3) pdir = 0;
                        marks = sl.marks;
                        g_executed_mask = sl.executed_mask;
                        lead = sl.lead;
                        party_n = sl.party_n;
                        if(party_n > 6) party_n = 6;
                        battles = sl.battles;
                        mason2_map = sl.mason2_map == 0xff ? -1 : sl.mason2_map;
                        reputation = (int)sl.reputation - 100;
                        if(reputation > LOGIC_REP_MAX) reputation = LOGIC_REP_MAX;
                        if(reputation < LOGIC_REP_MIN) reputation = LOGIC_REP_MIN;
                        bag.salve = sl.bag[0]; bag.bandage = sl.bag[1];
                        bag.bitterroot = sl.bag[2]; bag.dust = sl.bag[3];
                        bag.gem = sl.bag[4]; bag.sunbalm = sl.bag[5];
                        bag.warroot = sl.bag[6]; bag.smokebomb = sl.bag[7];
                        bag.greatcrystal = sl.bag[8]; bag.cageKey = sl.bag[9];
                        bag.megacrystal = sl.bag[10]; bag.ultimatecrystal = sl.bag[11];
                        bag.perfectcrystal = sl.bag[12];
                        bag.calmdraft = sl.bag[13]; bag.burnsalve = sl.bag[14];
                        bag.antidote = sl.bag[15]; bag.clearmind = sl.bag[16];
                        bag.numbroot = sl.bag[17]; bag.panacea = sl.bag[18];
                        bag.bowieKnife = sl.bag[19];
                        for(pi = 0; pi < party_n; pi++) {
                            party[pi].species = sl.party[pi].species;
                            party[pi].lv = sl.party[pi].lv;
                            party[pi].hp = sl.party[pi].hp;
                            party[pi].maxHp = sl.party[pi].maxHp;
                            party[pi].str = sl.party[pi].str;
                            party[pi].agl = sl.party[pi].agl;
                            party[pi].spc = sl.party[pi].spc;
                            party[pi].spp = sl.party[pi].spp;
                            party[pi].sppMax = sl.party[pi].sppMax;
                            party[pi].shiny = sl.party[pi].shiny;
                            party[pi].xp = sl.party[pi].xp;
                            /* slot byte 12 (was a per-monster crystal) is
                               reserved now -- the crystal comes from the
                               species, so old saves need no migration. */
                            party[pi].status = sl.party[pi].status;
                            party[pi].status_turns = sl.party[pi].status_turns;
                            party[pi].poison_stack = sl.party[pi].poison_stack;
                            dex_note_caught(party[pi].species);
                        }
                        {
                            int di;
                            for(di = 0; di < SAVE_DEX_BYTES; di++) {
                                g_dex_seen[di] |= sl.dex_seen[di];
                                g_dex_caught[di] |= sl.dex_caught[di];
                            }
                        }
                        got_shelf = save_flag_get(&sl, SAVE_FLAG_TOOK_STARTER);
                        talked_father = save_flag_get(&sl, SAVE_FLAG_TALKED_FATHER);
                        looted_crate = save_flag_get(&sl, SAVE_FLAG_LOOTED_CRATE);
                        talked_wren = save_flag_get(&sl, SAVE_FLAG_TALKED_WREN);
                        beat_calder = save_flag_get(&sl, SAVE_FLAG_BEAT_CALDER);
                        read_cart = save_flag_get(&sl, SAVE_FLAG_READ_CART);
                        talked_mae = save_flag_get(&sl, SAVE_FLAG_TALKED_MAE);
                        talked_ivo = save_flag_get(&sl, SAVE_FLAG_TALKED_IVO);
                        talked_nell = save_flag_get(&sl, SAVE_FLAG_TALKED_NELL);
                        nell_bonus = save_flag_get(&sl, SAVE_FLAG_NELL_BONUS);
                        got_gem = save_flag_get(&sl, SAVE_FLAG_GOT_FIELD_GEM);
                        pike_helped = save_flag_get(&sl, SAVE_FLAG_PIKE_HELPED);
                        talked_pike = save_flag_get(&sl, SAVE_FLAG_TALKED_PIKE);
                        got_herb = save_flag_get(&sl, SAVE_FLAG_GOT_HERB);
                        got_stump = save_flag_get(&sl, SAVE_FLAG_GOT_STUMP);
                        cath_caught = save_flag_get(&sl, SAVE_FLAG_CATHLEEN_CAUGHT);
                        beat_shin = save_flag_get(&sl, SAVE_FLAG_BEAT_SHINIGAMI);
                        beat_wsoldier_grove = save_flag_get(&sl, SAVE_FLAG_BEAT_CROSS);
                        beat_wsoldier_camp1 = save_flag_get(&sl, SAVE_FLAG_BEAT_CONSCRIPT);
                        beat_wsoldier_camp2 = save_flag_get(&sl, SAVE_FLAG_BEAT_ENFORCER);
                        beat_wsoldier_cliffs = save_flag_get(&sl, SAVE_FLAG_BEAT_SENTRY);
                        beat_forest_ranger = save_flag_get(&sl, SAVE_FLAG_BEAT_FOREST_RANGER);
                        beat_forest_scout = save_flag_get(&sl, SAVE_FLAG_BEAT_FOREST_SCOUT);
                        beat_ruins_keeper = save_flag_get(&sl, SAVE_FLAG_BEAT_RUINS_KEEPER);
                        beat_ruins_warden = save_flag_get(&sl, SAVE_FLAG_BEAT_RUINS_WARDEN);
                        badge_quartz = save_flag_get(&sl, SAVE_FLAG_BADGE_QUARTZ);
                        beat_quarry_driller = save_flag_get(&sl, SAVE_FLAG_BEAT_QUARRY_DRILLER);
                        beat_marsh_bog = save_flag_get(&sl, SAVE_FLAG_BEAT_MARSH_BOG);
                        beat_marsh_reed = save_flag_get(&sl, SAVE_FLAG_BEAT_MARSH_REED);
                        badge_opal = save_flag_get(&sl, SAVE_FLAG_BADGE_OPAL);
                        chose_heavenfall = save_flag_get(&sl, SAVE_FLAG_CHOSE_HEAVENFALL);
                        revived_father = save_flag_get(&sl, SAVE_FLAG_REVIVED_FATHER);
                        title_slayer = save_flag_get(&sl, SAVE_FLAG_TITLE_SLAYER);
                        title_tamer = save_flag_get(&sl, SAVE_FLAG_TITLE_TAMER);
                        apply_player_name(revived_father, title_slayer, title_tamer);
                        shop_free[0] = save_flag_get(&sl, SAVE_FLAG_SHOP_FREE_BRAM);
                        shop_free[1] = save_flag_get(&sl, SAVE_FLAG_SHOP_FREE_OREN);
                        shop_free[2] = save_flag_get(&sl, SAVE_FLAG_SHOP_FREE_FENN);
                        shop_free[3] = save_flag_get(&sl, SAVE_FLAG_SHOP_FREE_DRAY);
                        beat_commander = save_flag_get(&sl, SAVE_FLAG_BEAT_COMMANDER);
                        beat_heavenfall = save_flag_get(&sl, SAVE_FLAG_BEAT_HEAVENFALL);
                        heavenfall_rep_warned = save_flag_get(&sl, SAVE_FLAG_HEAVENFALL_REP_WARNED);
                        gauntlet_unlocked = save_flag_get(&sl, SAVE_FLAG_GAUNTLET_UNLOCKED);
                        beat_lieutenant_lead = save_flag_get(&sl, SAVE_FLAG_BEAT_LIEUTENANT_LEAD);
                        talked_tessa = save_flag_get(&sl, SAVE_FLAG_TESSA_GIFTED);
                        got_chest = save_flag_get(&sl, SAVE_FLAG_CHEST_LOOTED);
                        talked_birch = save_flag_get(&sl, SAVE_FLAG_BIRCH_GIFTED);
                        talked_sable = save_flag_get(&sl, SAVE_FLAG_SABLE_GIFTED);
                        cage_open = save_flag_get(&sl, SAVE_FLAG_CAGE_OPEN);
                        beat_mason = save_flag_get(&sl, SAVE_FLAG_FOUGHT_MASON);
                        anne_gifted = save_flag_get(&sl, SAVE_FLAG_ANNE_GIFTED);
                        beat_cathleen = save_flag_get(&sl, SAVE_FLAG_BEAT_CATHLEEN);
                        has_scroll = save_flag_get(&sl, SAVE_FLAG_HAS_SCROLL);
                        anne2_told = save_flag_get(&sl, SAVE_FLAG_ANNE2_TOLD);
                        mason2_done = save_flag_get(&sl, SAVE_FLAG_MASON2_DONE);
                        talked_reach = save_flag_get(&sl, SAVE_FLAG_TALKED_REACH);
                        saw_shinigami_rock = save_flag_get(&sl, SAVE_FLAG_SAW_SHINIGAMI_ROCK);
                        dray_knife_offered = save_flag_get(&sl, SAVE_FLAG_DRAY_KNIFE_OFFERED);
                        soldier_beaten[0] = save_flag_get(&sl, SAVE_FLAG_SOLDIER_BEATEN0);
                        soldier_beaten[1] = save_flag_get(&sl, SAVE_FLAG_SOLDIER_BEATEN1);
                        soldier_beaten[2] = save_flag_get(&sl, SAVE_FLAG_SOLDIER_BEATEN2);
                        quarry_crate_looted = save_flag_get(&sl, SAVE_FLAG_QUARRY_CRATE_LOOTED);
                        quarry_shelf_searched = save_flag_get(&sl, SAVE_FLAG_QUARRY_SHELF_SEARCHED);
                        soldiers_init = soldier_beaten[0] || soldier_beaten[1] || soldier_beaten[2];
                        door_lock = 8;
                        enc_lock = 8;
                        state = 1;
                        /* Shop stock isn't part of the save format (see
                           shop_stock's own comment) -- roll it fresh on
                           every load, same as a brand-new run. */
                        roll_all_shop_stock();
                        chip_sfx_ok();
                        do_new = 0;
                    } else {
                        chip_sfx_miss();
                        do_new = 0;
                    }
                }
                if(do_new) {
                /* resetRun(): every run-scoped variable back to its
                   startup value, matching state.lua's own resetRun()
                   (called on the title screen's next confirm/start
                   after MODE.TITLE). Harmless -- and a no-op -- on the
                   very first boot, since everything below is already
                   sitting at exactly these values; the only path that
                   actually needs it is looping back here from an
                   ending (ending_mode's a_now handler sets state = 0
                   without touching any of this), where without a
                   reset the "new" run would silently resume with the
                   previous one's party/bag/map/flags still live. */
                map_id = MAP_HOUSE;
                find_mark(MAP_HOUSE, 'P', &col, &row);
                px = col * TILE + TILE / 2;
                py = row * TILE + TILE / 2;
                pdir = 0;
                anim_counter = 0;
                door_lock = 0;
                got_shelf = 0; looted_crate = 0; talked_father = 0;
                quarry_crate_looted = 0; quarry_shelf_searched = 0;
                { Bag start = START_BAG_INIT; bag = start; }
                marks = START_MARKS;
                party_n = 0; lead = 0;
                catch_swap = 0;
                in_battle = 0;
                enc_lock = 8; last_tx = -1; last_ty = -1;
                menu_mode = 0; party_cur = 0; party_detail = 0; bag_cur = 0; heal_item = -1;
                hud_flash[0] = 0; hud_t = 0; map_banner_timer = 0;
                seq_lines = 0; seq_len = 0; seq_beat = 0;
                post_action = POST_NONE; post_soldier_id = 0;
                talked_wren = talked_mae = talked_ivo = talked_nell = 0;
                talked_pike = pike_helped = nell_bonus = 0;
                got_herb = got_gem = got_stump = read_cart = 0;
                beat_calder = beat_mason = beat_shin = cath_caught = 0;
                beat_cathleen = 0; has_scroll = 0; anne2_told = 0;
                beat_wsoldier_cliffs = 0; beat_wsoldier_camp1 = 0;
                beat_wsoldier_camp2 = 0; beat_wsoldier_grove = 0;
                beat_forest_ranger = 0; beat_forest_scout = 0;
                beat_ruins_keeper = 0; beat_ruins_warden = 0; badge_quartz = 0;
                beat_quarry_driller = 0;
                beat_marsh_bog = 0; beat_marsh_reed = 0; badge_opal = 0;
                chose_heavenfall = 0; beat_commander = 0;
                beat_lieutenant_lead = 0;
                dray_knife_offered = 0;
                beat_heavenfall = 0; heavenfall_rep_warned = 0; gauntlet_unlocked = 0;
                title_slayer = 0; title_tamer = 0;
                revived_father = 0;
                reputation = 0;
                apply_player_name(0, 0, 0);
                shop_free[0] = shop_free[1] = shop_free[2] = shop_free[3] = 0;
                got_chest = 0;
                talked_tessa = 0; talked_birch = 0; talked_sable = 0;
                cage_open = 0;
                talked_reach = 0;
                saw_shinigami_rock = 0;
                dex_clear();
                choice_mode = 0; choice_cur = 0;
                mercy_mode = 0; mercy_cur = 0; mercy_foe_levels = 0; mercy_foe_name[0] = 0; g_executed_mask = 0;
                soldier_beaten[0] = soldier_beaten[1] = soldier_beaten[2] = 0;
                mason_state = 0; mason_x = mason_y = 0.0f; mason_dir = 0; mason_anim = 0.0f;
                mason_rematch = 0; mason2_map = -1; mason2_done = 0;
                battles = 0;
                anne_state = 0; anne_x = anne_y = 0.0f; anne_dir = 0; anne_anim = 0.0f;
                anne_gifted = 0;
                soldiers_init = 0;
                shop_open = 0; shop_sell_tab = 0; shop_cur = 0;
                ending_mode = 0; ending_i = 0;

                state = 1;
                /* Seeds the battle RNG from however many vblanks
                   passed while the player sat at the title screen --
                   see rng_next()'s comment for why this stands in for
                   a real RTC/rand() source. */
                rng_state ^= frame_count | 1u;
                roll_all_shop_stock();
                chip_sfx_ok();
                }
            }
        }
        else if(menu_mode == 3) {
            if(up_now && !prev_up) {
                pause_cur = (pause_cur + 5) % 6;
                chip_sfx_ui();
            }
            if(down_now && !prev_down) {
                pause_cur = (pause_cur + 1) % 6;
                chip_sfx_ui();
            }
            if(b_now && !prev_b) {
                menu_mode = 0;
                chip_sfx_ui();
            }
            else if((a_now && !prev_a) || (start_now && !prev_start && pause_cur == 5)) {
                if(pause_cur == 0) {
                    menu_mode = 2;
                    party_detail = 0;
                    heal_item = -1;
                    chip_sfx_ui();
                } else if(pause_cur == 1) {
                    menu_mode = 1;
                    bag_cur = 0;
                    heal_item = -1;
                    chip_sfx_ui();
                } else if(pause_cur == 2) {
                    menu_mode = 4;
                    dex_cur = 0;
                    dex_entry = 0;
                    chip_sfx_ui();
                } else if(pause_cur == 3) {
                    menu_mode = 5;
                    chip_sfx_ui();
                } else if(pause_cur == 4) {
                    SaveLive sl;
                    int i, pi;
                    for(i = 0; i < (int)sizeof(sl); i++) ((unsigned char *)&sl)[i] = 0;
                    sl.map_id = (unsigned char)map_id;
                    sl.dir = (unsigned char)pdir;
                    sl.party_n = (unsigned char)party_n;
                    sl.lead = (unsigned char)lead;
                    sl.battles = (unsigned char)battles;
                    sl.mason2_map = (unsigned char)(mason2_map < 0 ? 0xff : mason2_map);
                    {
                        int rep = reputation + 100;
                        if(rep < 0) rep = 0;
                        if(rep > 200) rep = 200;
                        sl.reputation = (unsigned char)rep;
                    }
                    sl.x = (unsigned short)px;
                    sl.y = (unsigned short)py;
                    sl.marks = (unsigned short)marks;
                    sl.bag[0] = (unsigned char)bag.salve; sl.bag[1] = (unsigned char)bag.bandage;
                    sl.bag[2] = (unsigned char)bag.bitterroot; sl.bag[3] = (unsigned char)bag.dust;
                    sl.bag[4] = (unsigned char)bag.gem; sl.bag[5] = (unsigned char)bag.sunbalm;
                    sl.bag[6] = (unsigned char)bag.warroot; sl.bag[7] = (unsigned char)bag.smokebomb;
                    sl.bag[8] = (unsigned char)bag.greatcrystal; sl.bag[9] = (unsigned char)bag.cageKey;
                    sl.bag[10] = (unsigned char)bag.megacrystal; sl.bag[11] = (unsigned char)bag.ultimatecrystal;
                    sl.bag[12] = (unsigned char)bag.perfectcrystal;
                    sl.bag[13] = (unsigned char)bag.calmdraft; sl.bag[14] = (unsigned char)bag.burnsalve;
                    sl.bag[15] = (unsigned char)bag.antidote; sl.bag[16] = (unsigned char)bag.clearmind;
                    sl.bag[17] = (unsigned char)bag.numbroot; sl.bag[18] = (unsigned char)bag.panacea;
                    sl.bag[19] = (unsigned char)bag.bowieKnife;
                    for(pi = 0; pi < party_n && pi < 6; pi++) {
                        sl.party[pi].species = (unsigned char)party[pi].species;
                        sl.party[pi].lv = (unsigned char)party[pi].lv;
                        sl.party[pi].hp = (unsigned char)party[pi].hp;
                        sl.party[pi].maxHp = (unsigned char)party[pi].maxHp;
                        sl.party[pi].str = (unsigned char)party[pi].str;
                        sl.party[pi].agl = (unsigned char)party[pi].agl;
                        sl.party[pi].spc = (unsigned char)party[pi].spc;
                        sl.party[pi].spp = (unsigned char)party[pi].spp;
                        sl.party[pi].sppMax = (unsigned char)party[pi].sppMax;
                        sl.party[pi].shiny = (unsigned char)party[pi].shiny;
                        sl.party[pi].xp = (unsigned short)party[pi].xp;
                        sl.party[pi].nature = 0; /* reserved, see the reader */
                        sl.party[pi].status = (unsigned char)party[pi].status;
                        sl.party[pi].status_turns = (unsigned char)party[pi].status_turns;
                        sl.party[pi].poison_stack = (unsigned char)party[pi].poison_stack;
                    }
                    {
                        int di;
                        for(di = 0; di < SAVE_DEX_BYTES; di++) {
                            sl.dex_seen[di] = g_dex_seen[di];
                            sl.dex_caught[di] = g_dex_caught[di];
                        }
                    }
                    save_flag_put(&sl, SAVE_FLAG_TOOK_STARTER, got_shelf);
                    save_flag_put(&sl, SAVE_FLAG_TALKED_FATHER, talked_father);
                    save_flag_put(&sl, SAVE_FLAG_LOOTED_CRATE, looted_crate);
                    save_flag_put(&sl, SAVE_FLAG_TALKED_WREN, talked_wren);
                    save_flag_put(&sl, SAVE_FLAG_BEAT_CALDER, beat_calder);
                    save_flag_put(&sl, SAVE_FLAG_READ_CART, read_cart);
                    save_flag_put(&sl, SAVE_FLAG_TALKED_MAE, talked_mae);
                    save_flag_put(&sl, SAVE_FLAG_TALKED_IVO, talked_ivo);
                    save_flag_put(&sl, SAVE_FLAG_TALKED_NELL, talked_nell);
                    save_flag_put(&sl, SAVE_FLAG_NELL_BONUS, nell_bonus);
                    save_flag_put(&sl, SAVE_FLAG_GOT_FIELD_GEM, got_gem);
                    save_flag_put(&sl, SAVE_FLAG_PIKE_HELPED, pike_helped);
                    save_flag_put(&sl, SAVE_FLAG_TALKED_PIKE, talked_pike);
                    save_flag_put(&sl, SAVE_FLAG_GOT_HERB, got_herb);
                    save_flag_put(&sl, SAVE_FLAG_GOT_STUMP, got_stump);
                    save_flag_put(&sl, SAVE_FLAG_CATHLEEN_CAUGHT, cath_caught);
                    save_flag_put(&sl, SAVE_FLAG_BEAT_SHINIGAMI, beat_shin);
                    save_flag_put(&sl, SAVE_FLAG_BEAT_CROSS, beat_wsoldier_grove);
                    save_flag_put(&sl, SAVE_FLAG_BEAT_CONSCRIPT, beat_wsoldier_camp1);
                    save_flag_put(&sl, SAVE_FLAG_BEAT_ENFORCER, beat_wsoldier_camp2);
                    save_flag_put(&sl, SAVE_FLAG_BEAT_SENTRY, beat_wsoldier_cliffs);
                    save_flag_put(&sl, SAVE_FLAG_BEAT_FOREST_RANGER, beat_forest_ranger);
                    save_flag_put(&sl, SAVE_FLAG_BEAT_FOREST_SCOUT, beat_forest_scout);
                    save_flag_put(&sl, SAVE_FLAG_BEAT_RUINS_KEEPER, beat_ruins_keeper);
                    save_flag_put(&sl, SAVE_FLAG_BEAT_RUINS_WARDEN, beat_ruins_warden);
                    save_flag_put(&sl, SAVE_FLAG_BADGE_QUARTZ, badge_quartz);
                    save_flag_put(&sl, SAVE_FLAG_BEAT_QUARRY_DRILLER, beat_quarry_driller);
                    save_flag_put(&sl, SAVE_FLAG_BEAT_MARSH_BOG, beat_marsh_bog);
                    save_flag_put(&sl, SAVE_FLAG_BEAT_MARSH_REED, beat_marsh_reed);
                    save_flag_put(&sl, SAVE_FLAG_BADGE_OPAL, badge_opal);
                    save_flag_put(&sl, SAVE_FLAG_CHOSE_HEAVENFALL, chose_heavenfall);
                    save_flag_put(&sl, SAVE_FLAG_REVIVED_FATHER, revived_father);
                    save_flag_put(&sl, SAVE_FLAG_SHOP_FREE_BRAM, shop_free[0]);
                    save_flag_put(&sl, SAVE_FLAG_SHOP_FREE_OREN, shop_free[1]);
                    save_flag_put(&sl, SAVE_FLAG_SHOP_FREE_FENN, shop_free[2]);
                    save_flag_put(&sl, SAVE_FLAG_SHOP_FREE_DRAY, shop_free[3]);
                    save_flag_put(&sl, SAVE_FLAG_BEAT_COMMANDER, beat_commander);
                    save_flag_put(&sl, SAVE_FLAG_BEAT_HEAVENFALL, beat_heavenfall);
                    save_flag_put(&sl, SAVE_FLAG_HEAVENFALL_REP_WARNED, heavenfall_rep_warned);
                    save_flag_put(&sl, SAVE_FLAG_GAUNTLET_UNLOCKED, gauntlet_unlocked);
                    save_flag_put(&sl, SAVE_FLAG_TITLE_SLAYER, title_slayer);
                    save_flag_put(&sl, SAVE_FLAG_TITLE_TAMER, title_tamer);
                    save_flag_put(&sl, SAVE_FLAG_BEAT_LIEUTENANT_LEAD, beat_lieutenant_lead);
                    save_flag_put(&sl, SAVE_FLAG_TESSA_GIFTED, talked_tessa);
                    save_flag_put(&sl, SAVE_FLAG_CHEST_LOOTED, got_chest);
                    save_flag_put(&sl, SAVE_FLAG_BIRCH_GIFTED, talked_birch);
                    save_flag_put(&sl, SAVE_FLAG_SABLE_GIFTED, talked_sable);
                    save_flag_put(&sl, SAVE_FLAG_CAGE_OPEN, cage_open);
                    save_flag_put(&sl, SAVE_FLAG_FOUGHT_MASON, beat_mason);
                    save_flag_put(&sl, SAVE_FLAG_ANNE_GIFTED, anne_gifted);
                    save_flag_put(&sl, SAVE_FLAG_BEAT_CATHLEEN, beat_cathleen);
                    save_flag_put(&sl, SAVE_FLAG_HAS_SCROLL, has_scroll);
                    save_flag_put(&sl, SAVE_FLAG_ANNE2_TOLD, anne2_told);
                    save_flag_put(&sl, SAVE_FLAG_MASON2_DONE, mason2_done);
                    save_flag_put(&sl, SAVE_FLAG_TALKED_REACH, talked_reach);
                    save_flag_put(&sl, SAVE_FLAG_SAW_SHINIGAMI_ROCK, saw_shinigami_rock);
                    save_flag_put(&sl, SAVE_FLAG_DRAY_KNIFE_OFFERED, dray_knife_offered);
                    save_flag_put(&sl, SAVE_FLAG_SOLDIER_BEATEN0, soldier_beaten[0]);
                    save_flag_put(&sl, SAVE_FLAG_SOLDIER_BEATEN1, soldier_beaten[1]);
                    save_flag_put(&sl, SAVE_FLAG_SOLDIER_BEATEN2, soldier_beaten[2]);
                    save_flag_put(&sl, SAVE_FLAG_QUARRY_CRATE_LOOTED, quarry_crate_looted);
                    save_flag_put(&sl, SAVE_FLAG_QUARRY_SHELF_SEARCHED, quarry_shelf_searched);
                    sl.executed_mask = g_executed_mask;
                    if(save_store(&sl)) {
                        int n = s_cat(hud_flash, 0, "SAVED");
                        hud_flash[n] = 0;
                        hud_t = HUD_NOTE_FRAMES;
                        have_save = 1;
                        chip_sfx_save();
                    } else {
                        int n = s_cat(hud_flash, 0, "SAVE FAILED");
                        hud_flash[n] = 0;
                        hud_t = HUD_NOTE_FRAMES;
                        chip_sfx_miss();
                    }
                    menu_mode = 0;
                } else {
                    menu_mode = 0;
                    chip_sfx_ui();
                }
            }
        }
        else if(menu_mode == 4) {
            if(dex_entry) {
                if((a_now && !prev_a) || (b_now && !prev_b) || (start_now && !prev_start)) {
                    dex_entry = 0;
                    chip_sfx_ui();
                }
            } else {
                if(up_now && !prev_up) {
                    dex_cur = (dex_cur + SPECIES_N - 1) % SPECIES_N;
                    chip_sfx_ui();
                }
                if(down_now && !prev_down) {
                    dex_cur = (dex_cur + 1) % SPECIES_N;
                    chip_sfx_ui();
                }
                if(a_now && !prev_a) {
                    if(dex_get(g_dex_caught, dex_cur)) {
                        dex_entry = 1;
                        chip_sfx_ui();
                    } else {
                        chip_sfx_miss();
                    }
                }
                if((b_now && !prev_b) || (start_now && !prev_start)) {
                    menu_mode = 0;
                    chip_sfx_ui();
                }
            }
        }
        else if(menu_mode) {
            /* MODE.BAG/MODE.PARTY update. BAG has its own cursor/use
               logic (up/down picks a row, A uses it); bitterroot/
               dust/gem are battle-only mods with nothing to apply
               outside one, so A just says so, but salve/wrap heal
               *some* CryMon, and outside a battle that's a choice --
               picking either one hands off to the party menu
               (heal_item tracks which item this is, so this isn't
               read as an ordinary party-menu visit) where up/down
               now picks who receives it and A applies it, instead of
               always healing the lead. PARTY still has cycleParty(to)
               otherwise (A sets the lead), plus Y opens a detail view
               for party_cur (attacks, stats, party order) that
               up/down keeps browsing live and B backs out of before
               closing the menu itself. */
            if(menu_mode == 1) {
                if(up_now && !prev_up)
                    bag_cur = (bag_cur - 1 + ITEM_COUNT) % ITEM_COUNT;
                if(down_now && !prev_down)
                    bag_cur = (bag_cur + 1) % ITEM_COUNT;
                if(a_now && !prev_a) {
                    int *count = bag_field(&bag, bag_cur);
                    if(*count <= 0) {
                        int n = s_cat(hud_flash, 0, "NONE LEFT");
                        hud_flash[n] = 0;
                        hud_t = HUD_NOTE_FRAMES;
                    }
                    else if(bag_cur == 0 || bag_cur == 1 || bag_cur == 5) {
                        /* salve, bandage, sunbalm: the only healing
                           items that mean anything outside a battle --
                           hand off to the party menu to pick who gets
                           it. */
                        if(party_n <= 0) {
                            int n = s_cat(hud_flash, 0, "NO CRYMON TO HEAL");
                            hud_flash[n] = 0;
                            hud_t = HUD_NOTE_FRAMES;
                        }
                        else {
                            heal_item = bag_cur;
                            party_cur = lead;
                            party_detail = 0;
                            menu_mode = 2;
                        }
                    }
                    else {
                        int n = s_cat(hud_flash, 0, "ONLY USABLE IN BATTLE");
                        hud_flash[n] = 0;
                        hud_t = HUD_NOTE_FRAMES;
                    }
                }
            }
            else if(menu_mode == 5) {
                /* Settings now lives as its own row in the pause menu;
                   B/Start return to it, handled below with the other
                   modes' back-out logic. */
                if(up_now && !prev_up) {
                    chip_nudge_volume(1);
                    chip_sfx_ui();
                }
                if(down_now && !prev_down) {
                    chip_nudge_volume(-1);
                    chip_sfx_ui();
                }
            }
            else if(menu_mode == 2) {
                if(party_n <= 0) {
                    /* nothing else to do with an empty party */
                }
                else {
                if(up_now && !prev_up)
                    party_cur = (party_cur - 1 + party_n) % party_n;
                if(down_now && !prev_down)
                    party_cur = (party_cur + 1) % party_n;
                if(heal_item < 0 && !catch_swap && y_now && !prev_y)
                    party_detail = !party_detail;
                if(catch_swap && a_now && !prev_a) {
                    int n;
                    party[party_cur] = pending_catch;
                    n = s_cat(hud_flash, 0, SPECIES[pending_catch.species].name);
                    n = s_cat(hud_flash, n, " STAYS");
                    hud_flash[n] = 0;
                    hud_t = HUD_NOTE_FRAMES;
                    catch_swap = 0;
                    menu_mode = 0;
                }
                else if(a_now && !prev_a) {
                    if(heal_item >= 0) {
                        int *count = bag_field(&bag, heal_item);
                        int heal = party[party_cur].maxHp - party[party_cur].hp;
                        int cap = (heal_item == 0) ? 22 : (heal_item == 5) ? 40 : 12;
                        int n;
                        if(heal <= 0) {
                            n = s_cat(hud_flash, 0, SPECIES[party[party_cur].species].name);
                            n = s_cat(hud_flash, n, " IS AT FULL HP");
                        }
                        else {
                            if(heal > cap) heal = cap;
                            party[party_cur].hp += heal;
                            (*count)--;
                            n = s_cat(hud_flash, 0, SPECIES[party[party_cur].species].name);
                            n = s_cat(hud_flash, n, " HEALED ");
                            n = s_cat_uint(hud_flash, n, heal);
                            n = s_cat(hud_flash, n, " HP");
                        }
                        hud_flash[n] = 0;
                        hud_t = HUD_NOTE_FRAMES;
                        heal_item = -1;
                        menu_mode = 0;
                    }
                    else if(!party_detail) {
                        if(party[party_cur].hp > 0 && party_cur != lead) {
                            int n;
                            lead = party_cur;
                            n = s_cat(hud_flash, 0, SPECIES[party[lead].species].name);
                            n = s_cat(hud_flash, n, " TAKES THE LEAD");
                            hud_flash[n] = 0;
                            hud_t = HUD_NOTE_FRAMES;
                        }
                    }
                }
                if(!catch_swap && heal_item < 0 && x_now && !prev_x) {
                    if(party_n <= 1) {
                        int n = s_cat(hud_flash, 0, "WILL NOT RELEASE THE LAST");
                        hud_flash[n] = 0;
                        hud_t = HUD_NOTE_FRAMES;
                    } else if(party_release(party, &party_n, &lead, party_cur)) {
                        int n = s_cat(hud_flash, 0, "RELEASED");
                        hud_flash[n] = 0;
                        hud_t = HUD_NOTE_FRAMES;
                        if(party_cur >= party_n) party_cur = party_n - 1;
                    }
                }
                }
            }
            if(b_now && !prev_b) {
                if(catch_swap) {
                    int n = s_cat(hud_flash, 0, SPECIES[pending_catch.species].name);
                    n = s_cat(hud_flash, n, " SLIPS AWAY");
                    hud_flash[n] = 0;
                    hud_t = HUD_NOTE_FRAMES;
                    catch_swap = 0;
                    menu_mode = 0;
                }
                else if(menu_mode == 5)
                    menu_mode = 3;
                else if(menu_mode == 2 && heal_item >= 0) {
                    heal_item = -1;
                    menu_mode = 1;
                }
                else if(menu_mode == 2 && party_detail)
                    party_detail = 0;
                else
                    menu_mode = 0;
            }
            else if(start_now && !prev_start) {
                if(catch_swap) {
                    int n = s_cat(hud_flash, 0, SPECIES[pending_catch.species].name);
                    n = s_cat(hud_flash, n, " SLIPS AWAY");
                    hud_flash[n] = 0;
                    hud_t = HUD_NOTE_FRAMES;
                    catch_swap = 0;
                }
                menu_mode = menu_mode == 5 ? 3 : 0;
                heal_item = -1;
                party_detail = 0;
            }
        }
        else if(in_battle) {
            /* updateBattle(), matching state.lua's bPhase dispatch:
               0 = message (A advances; past the last beat, bAfter
               says what's next), 4 = special-move timing minigame
               (A locks it in), else = a menu (dpad nav, A confirms;
               B backs out of the attack menu to the item menu, only
               there). */
            if(battle.phase == 0) {
                if(a_now && !prev_a) {
                    battle.msg_i++;
                    if(battle.msg_i >= battle.msg_n) {
                        switch(battle.after) {
                            case BAFTER_ITEM:  battle.phase = 1; battle.cur = 0; break;
                            case BAFTER_ATK:   battle.phase = 2; battle.cur = 0; break;
                            case BAFTER_GUARD: battle.phase = 3; battle.cur = 0; break;
                            case BAFTER_WIN: {
                                /* finishWin(): XP is granted regardless
                                   of trainer_kind; marks and what
                                   happens next differ per trainer,
                                   matching the reference's branch
                                   order (Calder, soldier, Mason,
                                   Shinigami, then the generic/wild
                                   tail -- Cathleen included, since a
                                   win here means she was defeated, not
                                   captured; capture ends the battle
                                   earlier via BAFTER_WORLD). */
                                battle_finish_win(&battle, party, lead, party_n);

                                if(battle.trainer_kind == TRAINER_CALDER) {
                                    /* No ending cut here at all anymore
                                       -- see MAP_CAMP's section comment.
                                       Beating him just opens VELD's 'F'
                                       door; the camp officer further
                                       south is a taunt, not the game's
                                       ending (that's the Grove/
                                       Shinigami/Anne chain now). */
                                    beat_calder = 1;
                                    marks += 18;
                                    in_battle = 0;
                                    enc_lock = 3;
                                    seq_lines = TALK_CALDER_WIN;
                                    seq_len = TALK_LEN(TALK_CALDER_WIN);
                                    seq_beat = 0;
                                    /* Mason's rematch unlocks the
                                       moment Calder's beaten -- rolled
                                       once here, not re-rolled if the
                                       player revisits this map again.
                                       Not gated on beat_mason: his
                                       first ambush is practically
                                       unavoidable (he force-walks up
                                       the moment you leave the house),
                                       so this never actually fires
                                       without it, but nothing here
                                       depends on it having happened
                                       either. */
                                    if(!mason2_done && mason2_map < 0) {
                                        mason2_map = LOGIC_MASON2_MAPS[irand(0, LOGIC_MASON2_MAP_N - 1)];
                                    }
                                }
                                else if(battle.trainer_kind == TRAINER_WSOLDIER_CLIFFS) {
                                    beat_wsoldier_cliffs = 1;
                                    bag.cageKey += 1; /* trainers.sentry.grant */
                                    marks += 12;
                                    battles++;
                                    in_battle = 0;
                                    enc_lock = 3;
                                    seq_lines = TALK_WSOLDIER_CLIFFS_WIN;
                                    seq_len = TALK_LEN(TALK_WSOLDIER_CLIFFS_WIN);
                                    seq_beat = 0;
                                    post_action = POST_OPEN_MERCY;
                                }
                                else if(battle.trainer_kind == TRAINER_WSOLDIER_CAMP1) {
                                    beat_wsoldier_camp1 = 1;
                                    marks += 14;
                                    battles++;
                                    in_battle = 0;
                                    enc_lock = 3;
                                    seq_lines = TALK_WSOLDIER_CAMP1_WIN;
                                    seq_len = TALK_LEN(TALK_WSOLDIER_CAMP1_WIN);
                                    seq_beat = 0;
                                    post_action = POST_OPEN_MERCY;
                                }
                                else if(battle.trainer_kind == TRAINER_WSOLDIER_CAMP2) {
                                    beat_wsoldier_camp2 = 1;
                                    marks += 15;
                                    battles++;
                                    in_battle = 0;
                                    enc_lock = 3;
                                    seq_lines = TALK_WSOLDIER_CAMP2_WIN;
                                    seq_len = TALK_LEN(TALK_WSOLDIER_CAMP2_WIN);
                                    seq_beat = 0;
                                    post_action = POST_OPEN_MERCY;
                                }
                                else if(battle.trainer_kind == TRAINER_WSOLDIER_GROVE) {
                                    beat_wsoldier_grove = 1;
                                    marks += 18;
                                    battles++;
                                    in_battle = 0;
                                    enc_lock = 3;
                                    seq_lines = TALK_WSOLDIER_GROVE_WIN;
                                    seq_len = TALK_LEN(TALK_WSOLDIER_GROVE_WIN);
                                    seq_beat = 0;
                                    post_action = POST_OPEN_MERCY;
                                }
                                else if(battle.trainer_kind == TRAINER_WSOLDIER_RANGER) {
                                    beat_forest_ranger = 1;
                                    marks += 10;
                                    battles++;
                                    in_battle = 0;
                                    enc_lock = 3;
                                    seq_lines = TALK_FOREST_RANGER_WIN;
                                    seq_len = TALK_LEN(TALK_FOREST_RANGER_WIN);
                                    seq_beat = 0;
                                    post_action = POST_OPEN_MERCY;
                                }
                                else if(battle.trainer_kind == TRAINER_WSOLDIER_SCOUT) {
                                    beat_forest_scout = 1;
                                    marks += 11;
                                    battles++;
                                    in_battle = 0;
                                    enc_lock = 3;
                                    seq_lines = TALK_FOREST_SCOUT_WIN;                                    seq_len = TALK_LEN(TALK_FOREST_SCOUT_WIN);
                                    seq_beat = 0;
                                    post_action = POST_OPEN_MERCY;
                                }
                                else if(battle.trainer_kind == TRAINER_WSOLDIER_KEEPER) {
                                    beat_ruins_keeper = 1;
                                    marks += 13;
                                    battles++;
                                    in_battle = 0;
                                    enc_lock = 3;
                                    seq_lines = TALK_RUINS_KEEPER_WIN;
                                    seq_len = TALK_LEN(TALK_RUINS_KEEPER_WIN);
                                    seq_beat = 0;
                                    post_action = POST_OPEN_MERCY;
                                }
                                else if(battle.trainer_kind == TRAINER_WSOLDIER_WARDEN) {
                                    beat_ruins_warden = 1;
                                    marks += 14;
                                    battles++;
                                    in_battle = 0;
                                    enc_lock = 3;
                                    seq_lines = TALK_RUINS_WARDEN_WIN;
                                    seq_len = TALK_LEN(TALK_RUINS_WARDEN_WIN);
                                    seq_beat = 0;
                                    post_action = POST_OPEN_MERCY;
                                }
                                else if(battle.trainer_kind == TRAINER_WSOLDIER_QUARTZ) {
                                    badge_quartz = 1;
                                    marks += 16;
                                    battles++;
                                    in_battle = 0;
                                    enc_lock = 3;
                                    seq_lines = TALK_QUARTZ_WIN;
                                    seq_len = TALK_LEN(TALK_QUARTZ_WIN);
                                    seq_beat = 0;
                                    post_action = POST_OPEN_MERCY;
                                }
                                else if(battle.trainer_kind == TRAINER_WSOLDIER_QUARRY_DRILLER) {
                                    beat_quarry_driller = 1;
                                    marks += 15;
                                    battles++;
                                    in_battle = 0;
                                    enc_lock = 3;
                                    seq_lines = TALK_QUARRY_DRILLER_WIN;
                                    seq_len = TALK_LEN(TALK_QUARRY_DRILLER_WIN);
                                    seq_beat = 0;
                                    post_action = POST_OPEN_MERCY;
                                }
                                else if(battle.trainer_kind == TRAINER_WSOLDIER_OPAL) {
                                    badge_opal = 1;
                                    marks += 17;
                                    battles++;
                                    in_battle = 0;
                                    enc_lock = 3;
                                    seq_lines = TALK_OPAL_WIN;
                                    seq_len = TALK_LEN(TALK_OPAL_WIN);
                                    seq_beat = 0;
                                    post_action = POST_OPEN_MERCY;
                                }
                                else if(battle.trainer_kind == TRAINER_WSOLDIER_MARSH_BOG) {
                                    beat_marsh_bog = 1;
                                    marks += 11;
                                    battles++;
                                    in_battle = 0;
                                    enc_lock = 3;
                                    seq_lines = TALK_MARSH_BOG_WIN;
                                    seq_len = TALK_LEN(TALK_MARSH_BOG_WIN);
                                    seq_beat = 0;
                                    post_action = POST_OPEN_MERCY;
                                }
                                else if(battle.trainer_kind == TRAINER_WSOLDIER_MARSH_REED) {
                                    beat_marsh_reed = 1;
                                    marks += 12;
                                    battles++;
                                    in_battle = 0;
                                    enc_lock = 3;
                                    seq_lines = TALK_MARSH_REED_WIN;
                                    seq_len = TALK_LEN(TALK_MARSH_REED_WIN);
                                    seq_beat = 0;
                                    post_action = POST_OPEN_MERCY;
                                }
                                else if(battle.trainer_kind == TRAINER_WSOLDIER_COMMANDER_FINAL) {
                                    beat_commander = 1;
                                    marks += 25;
                                    battles++;
                                    in_battle = 0;
                                    enc_lock = 3;
                                    seq_lines = TALK_COMMANDER_FINAL_WIN;
                                    seq_len = TALK_LEN(TALK_COMMANDER_FINAL_WIN);
                                    seq_beat = 0;
                                    post_action = POST_CREDITS_FINAL;
                                }
                                else if(battle.trainer_kind == TRAINER_WSOLDIER_LEAD) {
                                    /* Placeholder ending (Leg 2 wrap
                                       gate): no mercy menu, straight to
                                       "Thank you for playing" then a
                                       plain (non-red, no scream) fade
                                       that reloads the last save --
                                       matches web's leadThanksGO ->
                                       startFade("hfGameOver") exactly.
                                       Beating him never opens the north
                                       road; that's Leg 3's job. */
                                    beat_lieutenant_lead = 1;
                                    marks += 20;
                                    battles++;
                                    in_battle = 0;
                                    enc_lock = 3;
                                    seq_lines = TALK_LEAD_WIN_PLACEHOLDER;
                                    seq_len = TALK_LEN(TALK_LEAD_WIN_PLACEHOLDER);
                                    seq_beat = 0;
                                    post_action = POST_LEAD_GAMEOVER;
                                }
                                else if(battle.trainer_kind == TRAINER_WSOLDIER_HEAVENFALL_GRAVE) {
                                    if(!beat_heavenfall) {
                                        beat_heavenfall = 1;
                                        reputation += LOGIC_REP_HEAVENFALL_REVIVE;
                                        if(reputation > LOGIC_REP_MAX) reputation = LOGIC_REP_MAX;
                                        if(reputation < LOGIC_REP_MIN) reputation = LOGIC_REP_MIN;
                                    }
                                    title_slayer = 1; title_tamer = 0;
                                    apply_player_name(revived_father, title_slayer, title_tamer);
                                    marks += 30; battles++;
                                    in_battle = 0; enc_lock = 3;
                                    seq_lines = TALK_GAUNTLET_GRAVE_WIN;
                                    seq_len = TALK_LEN(TALK_GAUNTLET_GRAVE_WIN);
                                    seq_beat = 0;
                                    post_action = POST_CREDITS_FINAL;
                                }
                                else if(battle.trainer_kind == TRAINER_SOLDIER) {
                                    soldier_beaten[battle.soldier_id] = 1;
                                    marks += 8;
                                    battles++;
                                    in_battle = 0;
                                    enc_lock = 3;
                                    seq_lines = TALK_SOLDIER_AFTER;
                                    seq_len = TALK_LEN(TALK_SOLDIER_AFTER);
                                    seq_beat = 0;
                                    post_action = POST_OPEN_MERCY;
                                }
                                else if(battle.trainer_kind == TRAINER_MASON) {
                                    /* He leaves the instant this
                                       closes, same as the rematch --
                                       no more standing-and-wait step
                                       requiring a second walk-up. */
                                    beat_mason = 1;
                                    marks += 10;
                                    battles++;
                                    in_battle = 0;
                                    enc_lock = 3;
                                    seq_lines = TALK_MASON_WIN;
                                    seq_len = TALK_LEN(TALK_MASON_WIN);
                                    seq_beat = 0;
                                    post_action = POST_MASON_LEAVE;
                                }
                                else if(battle.trainer_kind == TRAINER_MASON2) {
                                    /* No standing/re-interact step this
                                       time (unlike the first fight) --
                                       he leaves the instant this
                                       closes, via the same
                                       POST_MASON_LEAVE the first
                                       encounter's re-interact uses. */
                                    mason2_done = 1;
                                    marks += 20;
                                    battles++;
                                    in_battle = 0;
                                    enc_lock = 3;
                                    seq_lines = TALK_MASON_WIN2;
                                    seq_len = TALK_LEN(TALK_MASON_WIN2);
                                    seq_beat = 0;
                                    post_action = POST_MASON_LEAVE;
                                }
                                else if(battle.trainer_kind == TRAINER_SHINIGAMI) {
                                    /* No instant cut to an ending
                                       screen anymore -- he hands over
                                       the scroll and vanishes from the
                                       map (see TALK_SHINIGAMI_WIN and
                                       collect_npcs' beat_shin guard on
                                       mark '9'). Anne already told Max
                                       about her father right after
                                       Cathleen, so this dialogue closing
                                       goes straight into the
                                       resurrection choice (POST_OPEN_
                                       CHOICE) instead of ending here. */
                                    beat_shin = 1;
                                    has_scroll = 1;
                                    marks += 14;
                                    battles++;
                                    in_battle = 0;
                                    enc_lock = 3;
                                    seq_lines = TALK_SHINIGAMI_WIN;
                                    seq_len = TALK_LEN(TALK_SHINIGAMI_WIN);
                                    seq_beat = 0;
                                    post_action = POST_OPEN_CHOICE;
                                }
                                else {
                                    int n;
                                    marks += 3;
                                    battles++;
                                    if(battle.foe.species == SP_CATHLEEN) {
                                        beat_cathleen = 1;
                                        seq_lines = TALK_CATHLEEN_AFTER;
                                        seq_len = TALK_LEN(TALK_CATHLEEN_AFTER);
                                        seq_beat = 0;
                                        in_battle = 0;
                                        enc_lock = 3;
                                        /* Without this, post_action is
                                           still POST_CATHLEEN from
                                           starting the fight -- closing
                                           this dialogue would silently
                                           re-trigger case POST_CATHLEEN
                                           below and restart the battle
                                           (its own !cath_caught guard
                                           doesn't stop a beaten-not-
                                           captured Cathleen). */
                                        post_action = POST_OPEN_MERCY;
                                    }
                                    else {
                                        /* note(): a HUD toast, not a
                                           clickable battle message --
                                           the battle ends immediately,
                                           same as the reference (which
                                           sets mode="world" before
                                           calling note()). */
                                        n = s_cat(hud_flash, 0, SPECIES[party[lead].species].name);
                                        if(g_evo_note[0]) {
                                            n = s_cat(hud_flash, 0, g_evo_note);
                                        }
                                        else if(battle.grew) {
                                            n = s_cat(hud_flash, n, " GREW TO LV");
                                            n = s_cat_uint(hud_flash, n, party[lead].lv);
                                        }
                                        else {
                                            n = s_cat(hud_flash, n, " STANDS OVER THE GRASS");
                                        }
                                        hud_flash[n] = 0;
                                        hud_t = HUD_NOTE_FRAMES;
                                        in_battle = 0;
                                        enc_lock = 3;
                                    }
                                }
                                break;
                            }
                            case BAFTER_WIN_NOTE:
                                /* Dead as an actual battle.after target
                                   now (the tail above ends the battle
                                   directly), kept only so the #define
                                   and this switch arm still exist for
                                   anything that might still reference
                                   the enum value. */
                                in_battle = 0;
                                enc_lock = 3;
                                break;
                            case BAFTER_WORLD:
                                /* A successful capture (pickItem's gem
                                   branch) always targets battle.foe --
                                   if it was Cathleen, this is the one
                                   and only place G.cathCaught gets set
                                   (matches the source setting it
                                   inline inside pickItem's gem
                                   branch). */
                                if(battle.foe.species == SP_CATHLEEN)
                                    cath_caught = 1;
                                if(battle.foe.species == SP_HEAVENFALL) {
                                    if(!beat_heavenfall) {
                                        beat_heavenfall = 1;
                                        reputation += LOGIC_REP_HEAVENFALL_REVIVE;
                                        if(reputation > LOGIC_REP_MAX) reputation = LOGIC_REP_MAX;
                                        if(reputation < LOGIC_REP_MIN) reputation = LOGIC_REP_MIN;
                                    }
                                    title_tamer = 1; title_slayer = 0;
                                    apply_player_name(revived_father, title_slayer, title_tamer);
                                }
                                if(battle.catch_full) {
                                    pending_catch = battle.foe;
                                    catch_swap = 1;
                                    menu_mode = 2;
                                    party_detail = 0;
                                    heal_item = -1;
                                    party_cur = 0;
                                }
                                in_battle = 0;
                                enc_lock = 3;
                                break;
                            case BAFTER_LOSS:
                                /* Every party CryMon is at 0 HP (the
                                   only way battle_pick_guard ever
                                   reaches BAFTER_LOSS -- no living
                                   member left to jump in). On the
                                   Heavenfall path (Leg 2 wrap gate:
                                   "not a soft trip home") this is a
                                   real Game Over -- heavenfallDevour
                                   plays, then POST_HFGAMEOVER_SCREAM's
                                   scream + red fade reload/title.
                                   Otherwise: fade to black, teleport
                                   home next to the bed, fully heal,
                                   fade back in -- see FADE_ACTION_LOSS
                                   in the draw dispatch below. */
                                in_battle = 0;
                                enc_lock = 3;
                                if(chose_heavenfall) {
                                    seq_lines = TALK_HEAVENFALL_DEVOUR;
                                    seq_len = TALK_LEN(TALK_HEAVENFALL_DEVOUR);
                                    seq_beat = 0;
                                    post_action = POST_HFGAMEOVER_SCREAM;
                                } else {
                                    fade_state = FADE_OUT;
                                    fade_timer = 0;
                                    fade_action = FADE_ACTION_LOSS;
                                }
                                break;
                            default:
                                break;
                        }
                    }
                }
            }
            else if(battle.phase == 4) {
                /* Special timing needle. 60Hz, same 0-100 range as web. */
                battle.mg += (float)battle.mg_dir * (SPEC_NEEDLE_SPEED / 60.0f);
                if(battle.mg > 100.0f) { battle.mg = 100.0f; battle.mg_dir = -1; }
                if(battle.mg < 0.0f)   { battle.mg = 0.0f;   battle.mg_dir = 1; }
                if(a_now && !prev_a) {
                    battle_pick_special(&battle);
                    party[lead] = battle.pl;
                }
            }
            else {
                int n_rows = (battle.phase == 1) ? battle_item_menu_count(&bag)
                             : (battle.phase == 2) ? battle_atk_count(&battle)
                             : 3;
                if(n_rows < 1) n_rows = 1;

                if(up_now && !prev_up)
                    battle.cur = (battle.cur - 1 + n_rows) % n_rows;
                if(down_now && !prev_down)
                    battle.cur = (battle.cur + 1) % n_rows;

                if(battle.phase == 2 && b_now && !prev_b) {
                    battle.phase = 1;
                    battle.cur = 0;
                }

                if(a_now && !prev_a) {
                    if(battle.phase == 1) {
                        int kind = battle_item_menu_kind(&bag, battle.cur);
                        battle_pick_item(&battle, &bag, kind, party, &party_n, lead);
                    }
                    else if(battle.phase == 2) {
                        UMove moves[UMOVE_MAX];
                        int mn = unlocked_moves(&battle.pl, 1, moves, UMOVE_MAX);
                        const UMove *mv = (battle.cur >= 0 && battle.cur < mn) ? &moves[battle.cur] : 0;
                        if(battle_pl_status_intercept(&battle, party, party_n, lead)) {
                            /* paralyzed/confused -- handled inside, turn used */
                        } else if(!mv) {
                            /* empty */
                        } else if(mv->kind == UMOVE_WAIT) {
                            int n = s_cat(battle.msg[0], 0, g_player_name);
                            n = s_cat(battle.msg[0], n, " HOLDS");
                            battle.msg[0][n] = 0;
                            battle.msg_n = 1;
                            battle.msg_i = 0;
                            battle.phase = 0;
                            battle.after = BAFTER_GUARD;
                        } else if(mv->kind == UMOVE_SPELL) {
                            if(battle_pick_spell(&battle, mv->spell_id))
                                party[lead] = battle.pl;
                            else {
                                int n = s_cat(battle.msg[0], 0, "MANA SURGE IS SPENT");
                                battle.msg[0][n] = 0;
                                battle.msg_n = 1;
                                battle.msg_i = 0;
                                battle.phase = 0;
                                battle.after = BAFTER_ATK;
                            }
                        } else if(mv->kind == UMOVE_NMOVE) {
                            if(battle.nmove_pl_used >= mv->max_pp) {
                                int n = s_cat(battle.msg[0], 0, mv->name);
                                n = s_cat(battle.msg[0], n, " IS SPENT");
                                battle.msg[0][n] = 0;
                                battle.msg_n = 1;
                                battle.msg_i = 0;
                                battle.phase = 0;
                                battle.after = BAFTER_ATK;
                            } else {
                                battle_pick_nmove(&battle, mv);
                                party[lead] = battle.pl;
                            }
                        } else if(mv->kind == UMOVE_HYPE) {
                            if(battle.hype_pl_used >= mv->max_pp) {
                                int n = s_cat(battle.msg[0], 0, mv->name);
                                n = s_cat(battle.msg[0], n, " IS SPENT");
                                battle.msg[0][n] = 0;
                                battle.msg_n = 1;
                                battle.msg_i = 0;
                                battle.phase = 0;
                                battle.after = BAFTER_ATK;
                            } else {
                                battle_pick_hype(&battle, mv);
                                party[lead] = battle.pl;
                            }
                        } else if(mv->kind == UMOVE_SPECIAL) {
                            if(battle.pl.spp <= 0) {
                                int n = s_cat(battle.msg[0], 0, mv->name);
                                n = s_cat(battle.msg[0], n, " IS SPENT");
                                battle.msg[0][n] = 0;
                                battle.msg_n = 1;
                                battle.msg_i = 0;
                                battle.phase = 0;
                                battle.after = BAFTER_ATK;
                            } else {
                                battle.pl.spp--;
                                battle.mg = 8.0f;
                                battle.mg_dir = 1;
                                battle.phase = 4;
                            }
                        } else {
                            battle_pick_umove(&battle, mv);
                            party[lead] = battle.pl;
                        }
                    }
                    else {
                        battle_pick_guard(&battle, battle.cur, party, party_n, &lead);
                    }
                }
            }
        }
        else if(shop_open) {
            /* updateShop(): tab toggle (left/right), row cursor
               (up/down), confirm buys/sells, cancel/start/select all
               close (B stands in for select here, same as the bag/
               party menus). */
            int rows[ITEM_COUNT];
            int n_rows = shop_rows(&bag, shop_sell_tab, shop_keep_id, dray_knife_offered, rows);

            if((b_now && !prev_b) || (start_now && !prev_start)) {
                shop_open = 0;
            }
            else {
                if(up_now && !prev_up && n_rows > 0)
                    shop_cur = (shop_cur - 1 + n_rows) % n_rows;
                if(down_now && !prev_down && n_rows > 0)
                    shop_cur = (shop_cur + 1) % n_rows;
                if((left_now && !prev_left) || (right_now && !prev_right)) {
                    shop_sell_tab = !shop_sell_tab;
                    shop_cur = 0;
                }
                if(a_now && !prev_a && n_rows > 0) {
                    int idx = rows[shop_cur];
                    if(!shop_sell_tab) {
                        int in_range = shop_keep_id >= 0 && shop_keep_id < SHOP_CRYSTAL_MASK_N;
                        int stock_left = in_range ? shop_stock[shop_keep_id][idx] : 1;
                        int gift = shop_gift_open(reputation, shop_keep_id, shop_free);
                        int cost = gift ? 0 : shop_buy_price(ITEMS[idx].buy, reputation);
                        if(stock_left > 0 && marks >= cost) {
                            marks -= cost;
                            (*bag_field(&bag, idx))++;
                            if(in_range) {
                                shop_stock[shop_keep_id][idx]--;
                                if(shop_stock[shop_keep_id][idx] <= 0) shop_cur = 0;
                            }
                            if(gift && in_range)
                                shop_free[shop_keep_id] = 1;
                        }
                    }
                    else {
                        int *owned = bag_field(&bag, idx);
                        if(*owned > 0) {
                            (*owned)--;
                            marks += shop_sell_price(ITEMS[idx].buy, reputation);
                            if(*owned == 0) shop_cur = 0;
                        }
                    }
                }
            }
        }
        
        else if(mercy_mode) {
            /* Leg 2.9 mercy: up/down among 4 rows, A resolves choice. */
            if(up_now && !prev_up) {
                mercy_cur = (mercy_cur + 3) & 3;
                chip_sfx_ui();
            }
            if(down_now && !prev_down) {
                mercy_cur = (mercy_cur + 1) & 3;
                chip_sfx_ui();
            }
            if(a_now && !prev_a) {
                int levels = mercy_foe_levels > 0 ? mercy_foe_levels : 1;
                chip_sfx_ok();
                mercy_mode = 0;
                if(mercy_cur == 0) {
                    /* Let them go: +1 rep + random dismiss line */
                    reputation += 1;
                    if(reputation > LOGIC_REP_MAX) reputation = LOGIC_REP_MAX;
                    {
                        int n = s_cat(hud_flash, 0, "LET THEM GO. +1 REP");
                        hud_flash[n] = 0; hud_t = 90;
                    }
                } else if(mercy_cur == 1) {
                    reputation -= 1;
                    if(reputation < LOGIC_REP_MIN) reputation = LOGIC_REP_MIN;
                    marks += levels;
                    {
                        int n = s_cat(hud_flash, 0, "TOOK MARKS");
                        hud_flash[n] = 0; hud_t = 90;
                    }
                } else if(mercy_cur == 2) {
                    int idx = (int)(frand(0.0f, 1.0f) * (ITEM_COUNT > 1 ? ITEM_COUNT - 1 : 1));
                    int *slot;
                    reputation -= 2;
                    if(reputation < LOGIC_REP_MIN) reputation = LOGIC_REP_MIN;
                    if(idx < 0) idx = 0;
                    if(idx >= ITEM_COUNT) idx = 0;
                    slot = bag_field(&bag, idx);
                    if(slot) (*slot)++;
                    {
                        int n = s_cat(hud_flash, 0, "TOOK AN ITEM");
                        hud_flash[n] = 0; hud_t = 90;
                    }
                } else {
                    int a = (int)(frand(0.0f, 1.0f) * (ITEM_COUNT > 1 ? ITEM_COUNT - 1 : 1));
                    int b = (int)(frand(0.0f, 1.0f) * (ITEM_COUNT > 1 ? ITEM_COUNT - 1 : 1));
                    int *sa, *sb;
                    int ebit = -1;
                    reputation -= 10;
                    if(reputation < LOGIC_REP_MIN) reputation = LOGIC_REP_MIN;
                    marks += levels * 10;
                    if(a < 0) a = 0; if(a >= ITEM_COUNT) a = 0;
                    if(b < 0) b = 0; if(b >= ITEM_COUNT) b = 0;
                    sa = bag_field(&bag, a); sb = bag_field(&bag, b);
                    if(sa) (*sa)++;
                    if(sb) (*sb)++;
                    /* Permanent delete bit from last trainer_kind -- must
                       match npc_exec_bit()'s scheme or the executed NPC
                       never actually gets hidden on the map. */
                    ebit = mercy_exec_bit(battle.trainer_kind, battle.soldier_id);
                    if(ebit >= 0 && ebit < 31) g_executed_mask |= (1u << ebit);
                    chip_sfx_faint(); /* stand-in scream until dedicated SFX exists */
                    g_mercy_red_fade = 1;
                    fade_state = FADE_OUT;
                    fade_timer = 0;
                    chip_sfx_faint();
                    {
                        int n = s_cat(hud_flash, 0, "NO SURVIVORS");
                        hud_flash[n] = 0; hud_t = 90;
                    }
                }
            }
        }

        else if(backstab_mode) {
            /* draw_backstab()'s input: up/down toggles Approach/Backstab,
               A resolves, B cancels outright (unlike mercy_mode, this
               choice has a genuine "never mind" -- the target hasn't
               noticed Max yet either way). Approach immediately runs the
               same normal talk/battle flow a manual interact would've
               triggered (apply_npc_step()+npc_after_to_post_action() for
               an NPC_DEFS target, or the same TALK_SOLDIER_SPOT/
               POST_SOLDIER handoff the auto-chase catch uses for a
               forest soldier) -- matches web's updateBackstabChoice(),
               which calls runNpc(pb.npc) on Approach rather than leaving
               it to a re-scan next frame (which would just reopen this
               same prompt, since the target's still unspotted either way). */
            if(up_now && !prev_up) { backstab_cur = 1 - backstab_cur; chip_sfx_ui(); }
            if(down_now && !prev_down) { backstab_cur = 1 - backstab_cur; chip_sfx_ui(); }
            if(b_now && !prev_b) {
                backstab_mode = 0;
                backstab_npc_idx = -1;
                backstab_soldier_idx = -1;
                chip_sfx_ui();
            }
            if(a_now && !prev_a) {
                int idx = backstab_npc_idx;
                int sidx = backstab_soldier_idx;
                backstab_mode = 0;
                backstab_npc_idx = -1;
                backstab_soldier_idx = -1;
                chip_sfx_ok();
                if(backstab_cur == 0) {
                    if(idx >= 0) {
                        int npc_after2 = 0, npc_pending2 = -1;
                        NpcRun nr2;
                        nr2.map_id = map_id; nr2.px = px; nr2.py = py; nr2.party_n = party_n;
                        nr2.ft = ft; nr2.bag = &bag; nr2.marks = &marks; nr2.party = party;
                        nr2.pn = &party_n; nr2.lead = &lead; nr2.seq_lines = &seq_lines;
                        nr2.seq_len = &seq_len; nr2.after = &npc_after2; nr2.pending = &npc_pending2;
                        if(apply_npc_step(&nr2, idx)) {
                            seq_beat = 0;
                            post_action = npc_after_to_post_action(npc_after2, npc_pending2, &shop_keep_id);
                        }
                    } else if(sidx >= 0) {
                        seq_lines = TALK_SOLDIER_SPOT;
                        seq_len = TALK_LEN(TALK_SOLDIER_SPOT);
                        seq_beat = 0;
                        post_action = POST_SOLDIER;
                        post_soldier_id = sidx;
                    }
                }
                else if(backstab_cur == 1 && sidx >= 0) {
                    /* Backstab a forest soldier: same execute shape as
                       the NPC_DEFS branch below, but soldier_beaten[]
                       is the actual (and only) source of truth these
                       trainers check anywhere -- see finishWin()'s web
                       equivalent, which sets sol.beaten the same way
                       regardless of which mercy/Backstab choice follows.
                       Never touch npc_exec_bit()/TRAINER_KITS/beat_* via
                       a pending lookup here: SOLDIERS[]' ids ("sentry")
                       collide with an unrelated wsoldier's NPC_PENDING_*
                       name-space on the web side (fixed there the same
                       way -- kept isolated, not reused here either). */
                    int levels = backstab_levels > 0 ? backstab_levels : 1;
                    int ia = (int)(frand(0.0f, 1.0f) * (ITEM_COUNT > 1 ? ITEM_COUNT - 1 : 1));
                    int ib = (int)(frand(0.0f, 1.0f) * (ITEM_COUNT > 1 ? ITEM_COUNT - 1 : 1));
                    int *sa, *sb;
                    reputation -= 25;
                    if(reputation < LOGIC_REP_MIN) reputation = LOGIC_REP_MIN;
                    marks += levels * 10;
                    if(ia < 0) ia = 0; if(ia >= ITEM_COUNT) ia = 0;
                    if(ib < 0) ib = 0; if(ib >= ITEM_COUNT) ib = 0;
                    sa = bag_field(&bag, ia); sb = bag_field(&bag, ib);
                    if(sa) (*sa)++;
                    if(sb) (*sb)++;
                    soldier_beaten[sidx] = 1;
                    chip_sfx_faint();
                    g_mercy_red_fade = 1;
                    fade_state = FADE_OUT;
                    fade_timer = 0;
                    seq_lines = TALK_BACKSTAB_EXECUTE;
                    seq_len = TALK_LEN(TALK_BACKSTAB_EXECUTE);
                    seq_beat = 0;
                    {
                        int n = s_cat(hud_flash, 0, "NO SURVIVORS");
                        hud_flash[n] = 0; hud_t = 90;
                    }
                }
                else if(backstab_cur == 1 && idx >= 0) {
                    /* Resolve: same "execute" shape resolveMercy()'s
                       Execute row reaches after a real battle win
                       (permanent delete, loot, scream/red fade), but
                       -25 rep instead of -10 -- unprovoked, not a
                       post-fight choice. */
                    int ebit = npc_exec_bit(NPC_DEFS[idx].map_id, NPC_DEFS[idx].mark);
                    int levels = backstab_levels > 0 ? backstab_levels : 1;
                    int ia = (int)(frand(0.0f, 1.0f) * (ITEM_COUNT > 1 ? ITEM_COUNT - 1 : 1));
                    int ib = (int)(frand(0.0f, 1.0f) * (ITEM_COUNT > 1 ? ITEM_COUNT - 1 : 1));
                    int *sa, *sb;
                    reputation -= 25;
                    if(reputation < LOGIC_REP_MIN) reputation = LOGIC_REP_MIN;
                    marks += levels * 10;
                    if(ia < 0) ia = 0; if(ia >= ITEM_COUNT) ia = 0;
                    if(ib < 0) ib = 0; if(ib >= ITEM_COUNT) ib = 0;
                    sa = bag_field(&bag, ia); sb = bag_field(&bag, ib);
                    if(sa) (*sa)++;
                    if(sb) (*sb)++;
                    if(ebit >= 0 && ebit < 31) g_executed_mask |= (1u << ebit);
                    if(g_roamers[idx].inited) g_roamers[idx].chase = 0;
                    {
                        int bsi = npc_match_step(&NPC_DEFS[idx], ft, party_n);
                        const NpcStep *bst = (bsi >= 0) ? &NPC_STEPS[bsi] : 0;
                        if(bst) {
                            if(bst->pending == NPC_PENDING_SENTRY) { beat_wsoldier_cliffs = 1; bag.cageKey += 1; }
                            else if(bst->pending == NPC_PENDING_CONSCRIPT) beat_wsoldier_camp1 = 1;
                            else if(bst->pending == NPC_PENDING_ENFORCER) beat_wsoldier_camp2 = 1;
                            else if(bst->pending == NPC_PENDING_CROSS) beat_wsoldier_grove = 1;
                            else if(bst->pending == NPC_PENDING_FOREST_RANGER) beat_forest_ranger = 1;
                            else if(bst->pending == NPC_PENDING_FOREST_SCOUT) beat_forest_scout = 1;
                            else if(bst->pending == NPC_PENDING_RUINS_KEEPER) beat_ruins_keeper = 1;
                            else if(bst->pending == NPC_PENDING_RUINS_WARDEN) beat_ruins_warden = 1;
                            else if(bst->pending == NPC_PENDING_MARSH_BOG) beat_marsh_bog = 1;
                            else if(bst->pending == NPC_PENDING_MARSH_REED) beat_marsh_reed = 1;
                            else if(bst->pending == NPC_PENDING_QUARTZ) badge_quartz = 1;
                            else if(bst->pending == NPC_PENDING_OPAL) badge_opal = 1;
                            else if(bst->pending == NPC_PENDING_QUARRY_DRILLER) beat_quarry_driller = 1;
                        }
                    }
                    chip_sfx_faint();
                    g_mercy_red_fade = 1;
                    fade_state = FADE_OUT;
                    fade_timer = 0;
                    seq_lines = TALK_BACKSTAB_EXECUTE;
                    seq_len = TALK_LEN(TALK_BACKSTAB_EXECUTE);
                    seq_beat = 0;
                    {
                        int n = s_cat(hud_flash, 0, "NO SURVIVORS");
                        hud_flash[n] = 0; hud_t = 90;
                    }
                }
            }
        }

        else if(choice_mode) {
            /* draw_choice()'s input: up/down between the 2 rows, A
               locks it in -- no B, this choice doesn't have a "never
               mind" (matches "present the player with a choice", not
               an optional detour). Resolution beat picked by
               choice_cur; POST_ENDING_FINAL then warps onto the
               gauntlet map (see its case below) instead of jumping
               straight to the ending -- the Commander's win-handler is
               what actually fires the credits now, via
               POST_CREDITS_FINAL. */
            if(up_now && !prev_up) choice_cur = 1 - choice_cur;
            if(down_now && !prev_down) choice_cur = 1 - choice_cur;
            if(a_now && !prev_a) {
                choice_mode = 0;
                chose_heavenfall = choice_cur;
                if(chose_heavenfall) gauntlet_unlocked = 1;
                if(choice_cur == 0) {
                    revived_father = 1;
                    apply_player_name(1, title_slayer, title_tamer);
                    reputation += LOGIC_REP_FATHER_REVIVE;
                    if(reputation > LOGIC_REP_MAX) reputation = LOGIC_REP_MAX;
                    if(reputation < LOGIC_REP_MIN) reputation = LOGIC_REP_MIN;
                    find_mark(MAP_HOUSE, 'P', &col, &row);
                    map_id = MAP_HOUSE;
                    px = col * TILE + TILE / 2;
                    py = row * TILE + TILE / 2;
                    pdir = 1; /* facing up, toward father */
                    door_lock = 20;
                    map_banner_timer = MAP_BANNER_TOTAL;
                    seq_lines = TALK_CHOICE_FATHER;
                    seq_len = TALK_LEN(TALK_CHOICE_FATHER);
                }
                else {
                    seq_lines = TALK_CHOICE_HEAVENFALL;
                    seq_len = TALK_LEN(TALK_CHOICE_HEAVENFALL);
                }
                seq_beat = 0;
                post_action = POST_ENDING_FINAL;
            }
        }
        else if(ending_mode) {
            /* drawDemoEnd(): step through data.DEMO_END on A, return
               to the title screen after the last line (state.lua
               returns to MODE.TITLE, which resetRun()s on the next
               confirm/start -- ported above, in the state == 0
               branch's start_now handler). */
            if(a_now && !prev_a) {
                ending_i++;
                {
                    int n = chose_heavenfall ? TALK_LEN(DEMO_END_HEAVENFALL) : TALK_LEN(DEMO_END);
                    if(ending_i >= n) {
                        ending_mode = 0;
                        state = 0;
                    }
                }
            }
        }
        else {
            /* Movement is frozen while a dialogue sequence is active,
               matching state.lua's MODE.TALK (movement there is only
               processed in MODE.WALK). */
            if(door_lock > 0)
                door_lock--;

            /* HUD toast countdown/dismiss: ticks down every world
               frame regardless (matches update()'s unconditional
               `if (hudT > 0) hudT -= dt`), and A/B dismiss it early,
               same as the reference's confirm()/cancel() check.
               hud_dismissed_now suppresses the interact-chain further
               down for this same frame -- otherwise the very A press
               that dismisses the toast would immediately fall through
               into a fresh interact/dialogue-advance check, the same
               same-frame-reactivation bug the Mason ambush comment
               elsewhere in this file describes. */
            int hud_dismissed_now = 0;
            if(hud_t > 0) {
                hud_t--;
                if((a_now && !prev_a) || (b_now && !prev_b)) {
                    hud_t = 0;
                    hud_dismissed_now = 1;
                }
            }

            /* maybeStartAnne(): battlesDone>=1 while on VELD, gated
               on not already talking (matches its !talking() check
               closely enough). Spawns her at the player's own spot
               plus a fixed offset, exactly like spawnRival below,
               so she starts walking in from off to one side rather
               than appearing at a fixed VELD landmark.

               Her second approach is no longer tied to VELD at all --
               she meets Max immediately after the Cathleen fight,
               wherever that leaves her (the GROVE), rather than
               waiting for a trip back to town. Gated on
               (beat_cathleen || cath_caught) instead of beat_shin. */
            if(anne_state == 0 && !seq_lines &&
               ((!anne_gifted && battles >= ANNE_GIFT_AFTER && map_id == MAP_VELD) ||
                (anne_gifted && (beat_cathleen || cath_caught) && !anne2_told))) {
                anne_state = 1;
                anne_x = (float)px;
                anne_y = (float)py + 45.0f; /* 72 * 0.625 */
                anne_dir = 1; /* up */
                anne_anim = 0.0f;
            }

            /* Mason's rematch: fires the instant the player sets foot
               on mason2_map (rolled once, back at the Calder win --
               see there), reusing the exact same mason_state machine
               as his first ambush (approach -> ambush -> standing ->
               leave), just with mason_rematch=1 so the ambush trigger
               further down picks TALK_MASON_FIGHT2/POST_MASON2's
               3-CryMon loadout instead. Guarded on mason_state == 0
               so it can't retrigger while he's already approaching/
               standing/leaving from this same rematch. */
            if(mason2_map >= 0 && !mason2_done && mason_state == 0 &&
               map_id == mason2_map && !seq_lines) {
                mason_state = 1;
                mason_rematch = 1;
                mason_x = (float)px;
                mason_y = (float)py + 100.0f;
                mason_dir = 1; /* up */
                mason_anim = 0.0f;
            }

            /* Shinigami, freed in the Prison, stands beside the boulder
               blocking CryTown's west gate. No walk-cycle cutscene --
               he's just already there (VELD mark '9', collect_npcs()
               above), and the moment the player's viewport reaches him
               the rock event fires once. The boulder "exploding" is
               narrated in TALK_SHINIGAMI_ROCK_EVENT's text only; a real
               particle-burst animation is a marked TODO, not
               implemented here. Matches engine.ts's maybeShinigamiRock(). */
            if(map_id == MAP_VELD && beat_shin && !saw_shinigami_rock && !seq_lines) {
                int sx, sy, ddx, ddy;
                mark_center(MAP_VELD, '9', &sx, &sy);
                ddx = sx - px; if(ddx < 0) ddx = -ddx;
                ddy = sy - py; if(ddy < 0) ddy = -ddy;
                if(ddx < SCREEN_W / 2 && ddy < SCREEN_H / 2) {
                    saw_shinigami_rock = 1;
                    seq_lines = TALK_SHINIGAMI_ROCK_EVENT;
                    seq_len = TALK_LEN(TALK_SHINIGAMI_ROCK_EVENT);
                    seq_beat = 0;
                }
            }

            /* ensureSoldiers(): lazily place the 3 FOREST soldiers at
               their patrol-origin marks the first time the map is
               entered, matching engine.ts's own lazy build. */
            if(!soldiers_init && map_id == MAP_FOREST) {
                int i;
                for(i = 0; i < 3; i++) {
                    int sx, sy;
                    mark_center(MAP_FOREST, SOLDIERS[i].mark, &sx, &sy);
                    soldiers[i].x = (float)sx;
                    soldiers[i].y = (float)sy;
                    soldiers[i].anim = 0.0f;
                    soldiers[i].chase = 0;
                }
                /* Patrol (soldier 0): x-axis, +-90/-10px around spawn
                   (144/16 * 0.625). Scout (soldier 1): y-axis, +-50px
                   (80 * 0.625). Sentry (soldier 2): stationary,
                   facing up -- matches ensureSoldiers()'s 3 entries. */
                soldiers[0].dir = 3; soldiers[0].axis = 0; soldiers[0].sign = 1;
                soldiers[0].minv = soldiers[0].x - 10.0f; soldiers[0].maxv = soldiers[0].x + 90.0f;
                soldiers[1].dir = 2; soldiers[1].axis = 1; soldiers[1].sign = -1;
                soldiers[1].minv = soldiers[1].y - 50.0f; soldiers[1].maxv = soldiers[1].y + 50.0f;
                soldiers[2].dir = 1; soldiers[2].axis = 2; soldiers[2].sign = 0;
                soldiers[2].minv = soldiers[2].maxv = 0.0f;
                soldiers_init = 1;
            }

            /* Mason/Anne approach: force-walk toward the player,
               freezing all other world movement/interaction until
               they either reach the player (ambush) or the map
               changes out from under them. Matches engine.ts's own
               early-return while rival.phase/anne.phase === "approach". */
            if(mason_state == 1) {
                float dx = (float)px - mason_x, dy = (float)py - mason_y;
                float dist = f_sqrt(dx * dx + dy * dy);
                if(dist < ACTOR_REACH_DIST) {
                    mason_state = 2;
                    if(mason_rematch) {
                        seq_lines = TALK_MASON_FIGHT2;
                        seq_len = TALK_LEN(TALK_MASON_FIGHT2);
                        post_action = POST_MASON2;
                    }
                    else {
                        seq_lines = TALK_MASON_FIGHT;
                        seq_len = TALK_LEN(TALK_MASON_FIGHT);
                        post_action = POST_MASON;
                    }
                    seq_beat = 0;
                }
                else {
                    mason_x += dx / dist * ACTOR_SPD_APPROACH;
                    mason_y += dy / dist * ACTOR_SPD_APPROACH;
                    mason_dir = (dx < 0 ? -dx : dx) > (dy < 0 ? -dy : dy)
                                    ? (dx < 0 ? 2 : 3) : (dy < 0 ? 1 : 0);
                    mason_anim += 8.0f / 60.0f;
                }
            }
            else if(anne_state == 1) {
                float dx = (float)px - anne_x, dy = (float)py - anne_y;
                float dist = f_sqrt(dx * dx + dy * dy);
                if(dist < ACTOR_REACH_DIST) {
                    anne_state = 2;
                    if(!anne_gifted) {
                        anne_gifted = 1;
                        bag.gem += ANNE_GIFT_QTY;
                        seq_lines = TALK_ANNE_GIFT;
                        seq_len = TALK_LEN(TALK_ANNE_GIFT);
                        seq_beat = 0;
                        post_action = POST_ANNE_LEAVE;
                    }
                    else {
                        /* Second approach, right after the Cathleen
                           fight (not gated on returning to VELD): the
                           father-died reveal. She just walks off after
                           this one, same as her first visit -- the
                           resurrection choice itself doesn't open
                           until Shinigami actually hands over the
                           scroll (POST_OPEN_CHOICE, see
                           TRAINER_SHINIGAMI's win branch). */
                        anne2_told = 1;
                        seq_lines = TALK_ANNE_RETURN;
                        seq_len = TALK_LEN(TALK_ANNE_RETURN);
                        seq_beat = 0;
                        post_action = POST_ANNE_LEAVE;
                    }
                }
                else {
                    anne_x += dx / dist * ACTOR_SPD_APPROACH;
                    anne_y += dy / dist * ACTOR_SPD_APPROACH;
                    anne_dir = (dx < 0 ? -dx : dx) > (dy < 0 ? -dy : dy)
                                   ? (dx < 0 ? 2 : 3) : (dy < 0 ? 1 : 0);
                    anne_anim += 8.0f / 60.0f;
                }
            }

            /* Mason/Anne leaving: walk straight down off VELD, only
               while no dialogue box is up (matches engine.ts's
               talking()/hudT early-returns sitting ahead of these two
               blocks in updateWorld()). */
            if(mason_state == 3 && !seq_lines) {
                mason_y += ACTOR_SPD_LEAVE;
                mason_dir = 0;
                mason_anim += 8.0f / 60.0f;
                if(mason_y > (float)py + 150.0f) mason_state = 0;
            }
            if(anne_state == 3 && !seq_lines) {
                anne_y += ACTOR_SPD_LEAVE;
                anne_dir = 0;
                anne_anim += 8.0f / 60.0f;
                if(anne_y > (float)py + 150.0f) anne_state = 0;
            }

            /* Soldiers: patrol their axis, chase on line-of-sight,
               ambush like Mason once they catch up. Matches
               updateSoldiers()/soldierLos(). */
            if(map_id == MAP_FOREST && !seq_lines) {
                int i;
                for(i = 0; i < 3; i++) {
                    Soldier *s = &soldiers[i];
                    if(soldier_beaten[i]) continue;
                    if(s->chase) {
                        float dx = (float)px - s->x, dy = (float)py - s->y;
                        float dist = f_sqrt(dx * dx + dy * dy);
                        if(dist < ACTOR_CHASE_CATCH) {
                            s->chase = 0;
                            seq_lines = TALK_SOLDIER_SPOT;
                            seq_len = TALK_LEN(TALK_SOLDIER_SPOT);
                            seq_beat = 0;
                            post_action = POST_SOLDIER;
                            post_soldier_id = i;
                            break;
                        }
                        s->x += dx / dist * ACTOR_SPD_CHASE;
                        s->y += dy / dist * ACTOR_SPD_CHASE;
                        s->dir = (dx < 0 ? -dx : dx) > (dy < 0 ? -dy : dy)
                                     ? (dx < 0 ? 2 : 3) : (dy < 0 ? 1 : 0);
                        s->anim += 8.0f / 60.0f;
                        continue;
                    }
                    if(s->axis == 0) {
                        s->x += s->sign * ACTOR_SPD_PATROL;
                        if(s->x > s->maxv) { s->x = s->maxv; s->sign = -1; s->dir = 2; }
                        else if(s->x < s->minv) { s->x = s->minv; s->sign = 1; s->dir = 3; }
                        s->anim += 4.0f / 60.0f;
                    }
                    else if(s->axis == 1) {
                        s->y += s->sign * ACTOR_SPD_PATROL;
                        if(s->y > s->maxv) { s->y = s->maxv; s->sign = -1; s->dir = 1; }
                        else if(s->y < s->minv) { s->y = s->minv; s->sign = 1; s->dir = 0; }
                        s->anim += 4.0f / 60.0f;
                    }
                    if(soldier_los(map_id, s->x, s->y, s->dir, px, py))
                        s->chase = 1;
                }
            }

            /* Every other wsoldier trainer (not the 3 FOREST patrol
               soldiers above): no patrol movement -- see
               npc_def_roamable()'s doc comment for why (no walk-cycle
               art) -- just stationary until spotted, then close in and
               trigger its own battle the same way walking up and
               talking would (same TALK line via TALK_PTRS/TALK_COUNTS,
               same npc_pending -> POST_WSOLDIER_* mapping the manual
               interact path below uses). Matches engine.ts's
               updateRoamers(). A beaten one (its matched step no
               longer leads to NPC_AFTER_WSOLDIER) just freezes in
               place, chase cleared, same as the manual path finding
               nothing left to fight. */
            if(!seq_lines) {
                int i;
                for(i = 0; i < NPC_DEF_N; i++) {
                    const NpcDef *d = &NPC_DEFS[i];
                    int si, ebit;
                    const NpcStep *st;
                    Roamer *r;
                    if(d->map_id != map_id || !npc_def_roamable(i)) continue;
                    ebit = npc_exec_bit(d->map_id, d->mark);
                    if(ebit >= 0 && (g_executed_mask & (1u << ebit))) continue;
                    si = npc_match_step(d, ft, party_n);
                    if(si < 0) continue; /* hidden */
                    st = &NPC_STEPS[si];
                    if(st->after != NPC_AFTER_WSOLDIER) {
                        if(g_roamers[i].inited) g_roamers[i].chase = 0;
                        continue;
                    }
                    roamer_ensure(i);
                    r = &g_roamers[i];
                    if(r->chase) {
                        float dx = (float)px - r->x, dy = (float)py - r->y;
                        float dist = f_sqrt(dx * dx + dy * dy);
                        if(dist < ACTOR_CHASE_CATCH) {
                            r->chase = 0;
                            if(st->talk >= 0 && st->talk < TALK_TABLE_N) {
                                seq_lines = TALK_PTRS[st->talk];
                                seq_len = TALK_COUNTS[st->talk];
                            }
                            seq_beat = 0;
                            if(st->pending == NPC_PENDING_CROSS) post_action = POST_WSOLDIER_GROVE;
                            else if(st->pending == NPC_PENDING_CONSCRIPT) post_action = POST_WSOLDIER_CAMP1;
                            else if(st->pending == NPC_PENDING_ENFORCER) post_action = POST_WSOLDIER_CAMP2;
                            else if(st->pending == NPC_PENDING_SENTRY) post_action = POST_WSOLDIER_CLIFFS;
                            else if(st->pending == NPC_PENDING_FOREST_RANGER) post_action = POST_WSOLDIER_RANGER;
                            else if(st->pending == NPC_PENDING_FOREST_SCOUT) post_action = POST_WSOLDIER_SCOUT;
                            else if(st->pending == NPC_PENDING_RUINS_KEEPER) post_action = POST_WSOLDIER_KEEPER;
                            else if(st->pending == NPC_PENDING_RUINS_WARDEN) post_action = POST_WSOLDIER_WARDEN;
                            else if(st->pending == NPC_PENDING_QUARTZ) post_action = POST_WSOLDIER_QUARTZ;
                            else if(st->pending == NPC_PENDING_QUARRY_DRILLER) post_action = POST_WSOLDIER_QUARRY_DRILLER;
                            else if(st->pending == NPC_PENDING_OPAL) post_action = POST_WSOLDIER_OPAL;
                            else if(st->pending == NPC_PENDING_MARSH_BOG) post_action = POST_WSOLDIER_MARSH_BOG;
                            else if(st->pending == NPC_PENDING_MARSH_REED) post_action = POST_WSOLDIER_MARSH_REED;
                            else if(st->pending == NPC_PENDING_LEAD) post_action = POST_WSOLDIER_LEAD;
                            break;
                        }
                        dx /= dist; dy /= dist;
                        r->x += dx * ACTOR_SPD_CHASE;
                        r->y += dy * ACTOR_SPD_CHASE;
                        continue;
                    }
                    if(roamer_los(map_id, r->x, r->y, r->dir, px / TILE, py / TILE))
                        r->chase = 1;
                }
            }

            if(!seq_lines && hud_t <= 0 && fade_state == FADE_NONE && mason_state != 1 && anne_state != 1) {
                int dx = 0, dy = 0;
                int map_w = MAPS[map_id].cols * TILE;
                int map_h = MAPS[map_id].rows_n * TILE;

                if(pressed(raw, CONT_DPAD_LEFT))  { dx = -1; pdir = 2; }
                if(pressed(raw, CONT_DPAD_RIGHT)) { dx = 1;  pdir = 3; }
                if(pressed(raw, CONT_DPAD_UP))    { dy = -1; pdir = 1; }
                if(pressed(raw, CONT_DPAD_DOWN))  { dy = 1;  pdir = 0; }

                if(dx == 0 && dy == 0) {
                    anim_counter = 0;
                }
                else {
                    anim_counter++;
                }

                if(dx != 0 || dy != 0) {
                    /* Axis-separated movement so the player slides
                       along walls instead of stopping dead on a
                       diagonal. Half the collision box (6px) is
                       checked at the candidate feet position. */
                    /* Leg 2.1 fix: was a flat `int speed = 1` (exactly
                       60px/sec at our fixed 60fps vblank), 29% slower                       than web's delta-time `const sp = 84` in
                       engine.ts. A plain integer per-frame step can
                       never hit 84 exactly (84/60 = 1.4px/frame), so
                       accumulate the fractional remainder in 1/256ths
                       of a pixel and only spend whole pixels once
                       they've accrued -- averages ~83.9px/sec over
                       time instead of a hard 60. */
                    int speed;
                    player_speed_frac += 358; /* 84 * 256 / 60 ~= 358.4 */
                    speed = player_speed_frac >> 8;
                    player_speed_frac &= 255;
                    int nx = px + dx * speed;
                    int ny = py + dy * speed;

                    /* hitActor(): a live NPC blocks movement like a
                       solid tile (see actor_blocks() above). */
                    if(dx != 0 && !tile_blocked(map_id, tile_at(map_id, (nx + (dx > 0 ? 6 : -6)) / TILE,
                                                                 py / TILE), cath_caught || beat_cathleen, beat_calder, beat_shin, cage_open) &&
                       !actor_blocks(map_id, nx, py, mason_state, mason_x, mason_y,
                                     anne_state, anne_x, anne_y, soldiers, soldier_beaten,
                                     cath_caught || beat_cathleen, beat_shin,
                                     beat_calder, has_scroll, saw_shinigami_rock)) {
                        px = nx;
                    }
                    if(dy != 0 && !tile_blocked(map_id, tile_at(map_id, px / TILE,
                                                                 (ny + (dy > 0 ? 6 : -6)) / TILE), cath_caught || beat_cathleen, beat_calder, beat_shin, cage_open) &&
                       !actor_blocks(map_id, px, ny, mason_state, mason_x, mason_y,
                                     anne_state, anne_x, anne_y, soldiers, soldier_beaten,
                                     cath_caught || beat_cathleen, beat_shin,
                                     beat_calder, has_scroll, saw_shinigami_rock)) {
                        py = ny;
                    }

                    if(px < 8) px = 8;
                    if(px > map_w - 8) px = map_w - 8;
                    if(py < 8) py = 8;
                    if(py > map_h - 4) py = map_h - 4;

                    if(try_encounter(map_id, px, py, party_n, &enc_lock,
                                      &last_tx, &last_ty, &battle)) {
                        battle.pl = party[lead];
                        in_battle = 1;
                    }
                }

                /* Door/warp tiles, matching state.lua's chain of
                   mapId/tile checks (doorLock gates it, same as the
                   reference). GROVE has no exit warp of its own in
                   this step -- data.lua's GROVE only defines the 'O'
                   entrance shared with FOREST, and the far side (past
                   Shinigami) is battle-gated content not built yet. */
                if(door_lock <= 0) {
                    char here = tile_at(map_id, px / TILE, py / TILE);
                    int wi;
                    for(wi = 0; wi < WARP_N; wi++) {
                        const WarpDef *w = &WARPS[wi];
                        int need_ok;
                        if(w->from_map != map_id || w->tile != here) continue;
                        need_ok = 1;
                        if(w->need == 1) need_ok = got_shelf;
                        else if(w->need == 2) need_ok = beat_calder;
                        else if(w->need == 3) need_ok = beat_shin;
                        else if(w->need == 4) need_ok = has_scroll;
                        else if(w->need == 5) need_ok = beat_wsoldier_cliffs;
                        else if(w->need == 6) need_ok = (chose_heavenfall || gauntlet_unlocked);
                        if(!need_ok) {
                            if(w->fail_talk >= 0 && w->fail_talk < TALK_TABLE_N) {
                                find_mark(map_id, w->tile, &col, &row);
                                /* Push the player back off the locked door
                                   tile, away from whichever direction they'd
                                   be facing on arrival -- same nudge web's
                                   applyWarp() does before showing the
                                   fail-talk line. */
                                if(w->dir == 0)      py = row * TILE + TILE / 2 - TILE;
                                else if(w->dir == 1) py = row * TILE + TILE / 2 + TILE;
                                else if(w->dir == 2) px = col * TILE + TILE / 2 + TILE;
                                else if(w->dir == 3) px = col * TILE + TILE / 2 - TILE;
                                door_lock = 20;
                                seq_lines = TALK_PTRS[w->fail_talk];
                                seq_len = TALK_COUNTS[w->fail_talk];
                                seq_beat = 0;
                            }
                            break;
                        }
                        do_warp(&map_id, &px, &py, &pdir, w->to_map, w->spawn, w->dir, &map_banner_timer);
                        door_lock = 20;
                        if(w->on_arrive == 1 && mason_state == 0
                           && (!LOGIC_MASON_AMBUSH_UNLESS_BEAT || !beat_mason)
                           && (!LOGIC_MASON_AMBUSH_NEED_PARTY || party_n >= 1)) {
                            mason_state = 1;
                            mason_x = (float)px;
                            mason_y = (float)py + 100.0f;
                            mason_dir = 1;
                            mason_anim = 0.0f;
                        }
                        break;
                    }
                }
            }

            if(a_now && !prev_a && !hud_dismissed_now && fade_state == FADE_NONE) {
                if(seq_lines) {
                    /* Advance to the next beat; close the box (and
                       fire any queued post_action -- beginTalkEnd())
                       after the last one. */
                    seq_beat++;
                    if(seq_beat >= seq_len) {
                        seq_lines = 0;
                        seq_len = 0;
                        seq_beat = 0;

                        /* startBattle()'s leader-nil guard applies to
                           every battle-starting post_action, but not
                           to opening the shop (beginTalkEnd's a==9
                           branch has no such check). */
                        if(party_n > 0 || post_action == POST_SHOP ||
                           post_action == POST_MASON_LEAVE || post_action == POST_ANNE_LEAVE ||
                           post_action == POST_OPEN_CHOICE || post_action == POST_ENDING_FINAL ||
                           post_action == POST_BED_HEAL) {
                            switch(post_action) {
                                case POST_CALDER:
                                    battle.foe = mint_monster(SP_RAZORBAT, 4);
                                    battle.wild = 0;
                                    battle.trainer_kind = TRAINER_CALDER;
                                    battle.phase = 0;
                                    { int n = s_cat(battle.msg[0], 0, "CALDER SENDS RAZORBAT");
                                      battle.msg[0][n] = 0; }
                                    battle.msg_n = 1; battle.msg_i = 0; battle.after = BAFTER_ITEM;
                                    battle.cur = 0;
                                    battle.mods_self_str = battle.mods_self_agl = battle.mods_self_spc = 0;
                                    battle.mods_foe_str = battle.mods_foe_agl = battle.mods_foe_spc = 0;
                                    battle.pend_str = battle.pend_agl = battle.pend_spc = 0;
                                    battle.pl_poisoned = battle.foe_poisoned = 0;
                                    battle.stage_self_str = battle.stage_self_agl = battle.stage_self_spc = 0;
                                    battle.stage_foe_str = battle.stage_foe_agl = battle.stage_foe_spc = 0;
                                    battle.hype_self = battle.hype_foe = 0;
                                    battle.nmove_pl_used = battle.hype_pl_used = battle.nmove_foe_used = battle.hype_foe_used = 0;
                                    battle.bench_n = 0;
                                    battle.grew = 0;
                                    battle.pl = party[lead];
                                    in_battle = 1;
                                    break;
                                case POST_MASON:
                                    battle.foe = mint_monster(SP_GLIMMOTH, 3);
                                    battle.wild = 0;
                                    battle.trainer_kind = TRAINER_MASON;
                                    battle.phase = 0;
                                    { int n = s_cat(battle.msg[0], 0, "MASON SENDS GLIMMOTH");
                                      battle.msg[0][n] = 0; }
                                    battle.msg_n = 1; battle.msg_i = 0; battle.after = BAFTER_ITEM;
                                    battle.cur = 0;
                                    battle.mods_self_str = battle.mods_self_agl = battle.mods_self_spc = 0;
                                    battle.mods_foe_str = battle.mods_foe_agl = battle.mods_foe_spc = 0;
                                    battle.pend_str = battle.pend_agl = battle.pend_spc = 0;
                                    battle.pl_poisoned = battle.foe_poisoned = 0;
                                    battle.stage_self_str = battle.stage_self_agl = battle.stage_self_spc = 0;
                                    battle.stage_foe_str = battle.stage_foe_agl = battle.stage_foe_spc = 0;
                                    battle.hype_self = battle.hype_foe = 0;
                                    battle.nmove_pl_used = battle.hype_pl_used = battle.nmove_foe_used = battle.hype_foe_used = 0;
                                    battle.bench_n = 0;
                                    battle.grew = 0;
                                    battle.pl = party[lead];
                                    in_battle = 1;
                                    break;
                                case POST_MASON2:
                                    /* Rematch: 3 CryMon back to back
                                       (Shinigami's bench mechanic,
                                       reused), all higher level than
                                       the lv3 Glimmoth he opened with
                                       the first time. */
                                    battle.foe = mint_monster(SP_GLIMMOTH, 6);
                                    battle.wild = 0;
                                    battle.trainer_kind = TRAINER_MASON2;
                                    battle.phase = 0;
                                    { int n = s_cat(battle.msg[0], 0, "MASON SENDS GLIMMOTH");
                                      battle.msg[0][n] = 0; }
                                    battle.msg_n = 1; battle.msg_i = 0; battle.after = BAFTER_ITEM;
                                    battle.cur = 0;
                                    battle.mods_self_str = battle.mods_self_agl = battle.mods_self_spc = 0;
                                    battle.mods_foe_str = battle.mods_foe_agl = battle.mods_foe_spc = 0;
                                    battle.pend_str = battle.pend_agl = battle.pend_spc = 0;
                                    battle.pl_poisoned = battle.foe_poisoned = 0;
                                    battle.stage_self_str = battle.stage_self_agl = battle.stage_self_spc = 0;
                                    battle.stage_foe_str = battle.stage_foe_agl = battle.stage_foe_spc = 0;
                                    battle.hype_self = battle.hype_foe = 0;
                                    battle.nmove_pl_used = battle.hype_pl_used = battle.nmove_foe_used = battle.hype_foe_used = 0;
                                    battle.bench[0] = mint_monster(SP_BRIARFOX, 7);
                                    battle.bench[1] = mint_monster(SP_DUSKHORN, 8);
                                    battle.bench_n = 2;
                                    battle.grew = 0;
                                    battle.pl = party[lead];
                                    in_battle = 1;
                                    break;
                                case POST_WSOLDIER_CLIFFS:
                                    battle.foe = mint_monster(TRAINER_KITS[KIT_SENTRY].lead_sp, TRAINER_KITS[KIT_SENTRY].lead_lv);
                                    battle.wild = 0;
                                    battle.trainer_kind = TRAINER_WSOLDIER_CLIFFS;
                                    battle.phase = 0;
                                    { int n = s_cat(battle.msg[0], 0, "SENTRY SENDS EMBERLING");
                                      battle.msg[0][n] = 0; }
                                    battle.msg_n = 1; battle.msg_i = 0; battle.after = BAFTER_ITEM;
                                    battle.cur = 0;
                                    battle.mods_self_str = battle.mods_self_agl = battle.mods_self_spc = 0;
                                    battle.mods_foe_str = battle.mods_foe_agl = battle.mods_foe_spc = 0;
                                    battle.pend_str = battle.pend_agl = battle.pend_spc = 0;
                                    battle.pl_poisoned = battle.foe_poisoned = 0;
                                    battle.stage_self_str = battle.stage_self_agl = battle.stage_self_spc = 0;
                                    battle.stage_foe_str = battle.stage_foe_agl = battle.stage_foe_spc = 0;
                                    battle.hype_self = battle.hype_foe = 0;
                                    battle.nmove_pl_used = battle.hype_pl_used = battle.nmove_foe_used = battle.hype_foe_used = 0;
                                    battle.bench[0] = mint_monster(TRAINER_KITS[KIT_SENTRY].bench_sp[0], TRAINER_KITS[KIT_SENTRY].bench_lv[0]);
                                    battle.bench[1] = mint_monster(TRAINER_KITS[KIT_SENTRY].bench_sp[1], TRAINER_KITS[KIT_SENTRY].bench_lv[1]);
                                    battle.bench_n = TRAINER_KITS[KIT_SENTRY].bench_n;
                                    battle.grew = 0;
                                    battle.pl = party[lead];
                                    in_battle = 1;
                                    break;
                                case POST_WSOLDIER_CAMP1:
                                    battle.foe = mint_monster(TRAINER_KITS[KIT_CONSCRIPT].lead_sp, TRAINER_KITS[KIT_CONSCRIPT].lead_lv);
                                    battle.wild = 0;
                                    battle.trainer_kind = TRAINER_WSOLDIER_CAMP1;
                                    battle.phase = 0;
                                    { int n = s_cat(battle.msg[0], 0, "CONSCRIPT SENDS SABLECLAW");
                                      battle.msg[0][n] = 0; }
                                    battle.msg_n = 1; battle.msg_i = 0; battle.after = BAFTER_ITEM;
                                    battle.cur = 0;
                                    battle.mods_self_str = battle.mods_self_agl = battle.mods_self_spc = 0;
                                    battle.mods_foe_str = battle.mods_foe_agl = battle.mods_foe_spc = 0;
                                    battle.pend_str = battle.pend_agl = battle.pend_spc = 0;
                                    battle.pl_poisoned = battle.foe_poisoned = 0;
                                    battle.stage_self_str = battle.stage_self_agl = battle.stage_self_spc = 0;
                                    battle.stage_foe_str = battle.stage_foe_agl = battle.stage_foe_spc = 0;
                                    battle.hype_self = battle.hype_foe = 0;
                                    battle.nmove_pl_used = battle.hype_pl_used = battle.nmove_foe_used = battle.hype_foe_used = 0;
                                    battle.bench[0] = mint_monster(TRAINER_KITS[KIT_CONSCRIPT].bench_sp[0], TRAINER_KITS[KIT_CONSCRIPT].bench_lv[0]);
                                    battle.bench[1] = mint_monster(TRAINER_KITS[KIT_CONSCRIPT].bench_sp[1], TRAINER_KITS[KIT_CONSCRIPT].bench_lv[1]);
                                    battle.bench_n = TRAINER_KITS[KIT_CONSCRIPT].bench_n;
                                    battle.grew = 0;
                                    battle.pl = party[lead];
                                    in_battle = 1;
                                    break;
                                case POST_WSOLDIER_CAMP2:
                                    battle.foe = mint_monster(TRAINER_KITS[KIT_ENFORCER].lead_sp, TRAINER_KITS[KIT_ENFORCER].lead_lv);
                                    battle.wild = 0;
                                    battle.trainer_kind = TRAINER_WSOLDIER_CAMP2;
                                    battle.phase = 0;
                                    { int n = s_cat(battle.msg[0], 0, "ENFORCER SENDS THORNHIDE");
                                      battle.msg[0][n] = 0; }
                                    battle.msg_n = 1; battle.msg_i = 0; battle.after = BAFTER_ITEM;
                                    battle.cur = 0;
                                    battle.mods_self_str = battle.mods_self_agl = battle.mods_self_spc = 0;
                                    battle.mods_foe_str = battle.mods_foe_agl = battle.mods_foe_spc = 0;
                                    battle.pend_str = battle.pend_agl = battle.pend_spc = 0;
                                    battle.pl_poisoned = battle.foe_poisoned = 0;
                                    battle.stage_self_str = battle.stage_self_agl = battle.stage_self_spc = 0;
                                    battle.stage_foe_str = battle.stage_foe_agl = battle.stage_foe_spc = 0;
                                    battle.hype_self = battle.hype_foe = 0;
                                    battle.nmove_pl_used = battle.hype_pl_used = battle.nmove_foe_used = battle.hype_foe_used = 0;
                                    battle.bench[0] = mint_monster(TRAINER_KITS[KIT_ENFORCER].bench_sp[0], TRAINER_KITS[KIT_ENFORCER].bench_lv[0]);
                                    battle.bench[1] = mint_monster(TRAINER_KITS[KIT_ENFORCER].bench_sp[1], TRAINER_KITS[KIT_ENFORCER].bench_lv[1]);
                                    battle.bench_n = TRAINER_KITS[KIT_ENFORCER].bench_n;
                                    battle.grew = 0;
                                    battle.pl = party[lead];
                                    in_battle = 1;
                                    break;
                                case POST_WSOLDIER_GROVE:
                                    battle.foe = mint_monster(TRAINER_KITS[KIT_CROSS].lead_sp, TRAINER_KITS[KIT_CROSS].lead_lv);
                                    battle.wild = 0;
                                    battle.trainer_kind = TRAINER_WSOLDIER_GROVE;
                                    battle.phase = 0;
                                    { int n = s_cat(battle.msg[0], 0, "WARDEN SENDS CRYMARE");
                                      battle.msg[0][n] = 0; }
                                    battle.msg_n = 1; battle.msg_i = 0; battle.after = BAFTER_ITEM;
                                    battle.cur = 0;
                                    battle.mods_self_str = battle.mods_self_agl = battle.mods_self_spc = 0;
                                    battle.mods_foe_str = battle.mods_foe_agl = battle.mods_foe_spc = 0;
                                    battle.pend_str = battle.pend_agl = battle.pend_spc = 0;
                                    battle.pl_poisoned = battle.foe_poisoned = 0;
                                    battle.stage_self_str = battle.stage_self_agl = battle.stage_self_spc = 0;
                                    battle.stage_foe_str = battle.stage_foe_agl = battle.stage_foe_spc = 0;
                                    battle.hype_self = battle.hype_foe = 0;
                                    battle.nmove_pl_used = battle.hype_pl_used = battle.nmove_foe_used = battle.hype_foe_used = 0;
                                    battle.bench[0] = mint_monster(TRAINER_KITS[KIT_CROSS].bench_sp[0], TRAINER_KITS[KIT_CROSS].bench_lv[0]);
                                    battle.bench[1] = mint_monster(TRAINER_KITS[KIT_CROSS].bench_sp[1], TRAINER_KITS[KIT_CROSS].bench_lv[1]);
                                    battle.bench_n = TRAINER_KITS[KIT_CROSS].bench_n;
                                    battle.grew = 0;
                                    battle.pl = party[lead];
                                    in_battle = 1;
                                    break;
                                case POST_WSOLDIER_RANGER:
                                    battle.foe = mint_monster(TRAINER_KITS[KIT_FOREST_RANGER].lead_sp, TRAINER_KITS[KIT_FOREST_RANGER].lead_lv);
                                    battle.wild = 0;
                                    battle.trainer_kind = TRAINER_WSOLDIER_RANGER;
                                    battle.phase = 0;
                                    { int n = s_cat(battle.msg[0], 0, "RANGER SENDS BRIARFOX");
                                      battle.msg[0][n] = 0; }
                                    battle.msg_n = 1; battle.msg_i = 0; battle.after = BAFTER_ITEM;
                                    battle.cur = 0;
                                    battle.mods_self_str = battle.mods_self_agl = battle.mods_self_spc = 0;
                                    battle.mods_foe_str = battle.mods_foe_agl = battle.mods_foe_spc = 0;
                                    battle.pend_str = battle.pend_agl = battle.pend_spc = 0;
                                    battle.pl_poisoned = battle.foe_poisoned = 0;
                                    battle.stage_self_str = battle.stage_self_agl = battle.stage_self_spc = 0;
                                    battle.stage_foe_str = battle.stage_foe_agl = battle.stage_foe_spc = 0;
                                    battle.hype_self = battle.hype_foe = 0;
                                    battle.nmove_pl_used = battle.hype_pl_used = battle.nmove_foe_used = battle.hype_foe_used = 0;
                                    battle.bench[0] = mint_monster(TRAINER_KITS[KIT_FOREST_RANGER].bench_sp[0], TRAINER_KITS[KIT_FOREST_RANGER].bench_lv[0]);
                                    battle.bench[1] = mint_monster(TRAINER_KITS[KIT_FOREST_RANGER].bench_sp[1], TRAINER_KITS[KIT_FOREST_RANGER].bench_lv[1]);
                                    battle.bench_n = TRAINER_KITS[KIT_FOREST_RANGER].bench_n;
                                    battle.grew = 0;
                                    battle.pl = party[lead];
                                    in_battle = 1;
                                    break;
                                case POST_WSOLDIER_SCOUT:
                                    battle.foe = mint_monster(TRAINER_KITS[KIT_FOREST_SCOUT].lead_sp, TRAINER_KITS[KIT_FOREST_SCOUT].lead_lv);
                                    battle.wild = 0;
                                    battle.trainer_kind = TRAINER_WSOLDIER_SCOUT;
                                    battle.phase = 0;
                                    { int n = s_cat(battle.msg[0], 0, "SCOUT SENDS DUSKHORN");
                                      battle.msg[0][n] = 0; }
                                    battle.msg_n = 1; battle.msg_i = 0; battle.after = BAFTER_ITEM;
                                    battle.cur = 0;
                                    battle.mods_self_str = battle.mods_self_agl = battle.mods_self_spc = 0;
                                    battle.mods_foe_str = battle.mods_foe_agl = battle.mods_foe_spc = 0;
                                    battle.pend_str = battle.pend_agl = battle.pend_spc = 0;
                                    battle.pl_poisoned = battle.foe_poisoned = 0;
                                    battle.stage_self_str = battle.stage_self_agl = battle.stage_self_spc = 0;
                                    battle.stage_foe_str = battle.stage_foe_agl = battle.stage_foe_spc = 0;
                                    battle.hype_self = battle.hype_foe = 0;
                                    battle.nmove_pl_used = battle.hype_pl_used = battle.nmove_foe_used = battle.hype_foe_used = 0;
                                    battle.bench[0] = mint_monster(TRAINER_KITS[KIT_FOREST_SCOUT].bench_sp[0], TRAINER_KITS[KIT_FOREST_SCOUT].bench_lv[0]);
                                    battle.bench[1] = mint_monster(TRAINER_KITS[KIT_FOREST_SCOUT].bench_sp[1], TRAINER_KITS[KIT_FOREST_SCOUT].bench_lv[1]);
                                    battle.bench_n = TRAINER_KITS[KIT_FOREST_SCOUT].bench_n;
                                    battle.grew = 0;
                                    battle.pl = party[lead];
                                    in_battle = 1;
                                    break;
                                case POST_WSOLDIER_KEEPER:
                                    battle.foe = mint_monster(TRAINER_KITS[KIT_RUINS_KEEPER].lead_sp, TRAINER_KITS[KIT_RUINS_KEEPER].lead_lv);
                                    battle.wild = 0;
                                    battle.trainer_kind = TRAINER_WSOLDIER_KEEPER;
                                    battle.phase = 0;
                                    { int n = s_cat(battle.msg[0], 0, "KEEPER SENDS MOSSBACK");
                                      battle.msg[0][n] = 0; }
                                    battle.msg_n = 1; battle.msg_i = 0; battle.after = BAFTER_ITEM;
                                    battle.cur = 0;
                                    battle.mods_self_str = battle.mods_self_agl = battle.mods_self_spc = 0;
                                    battle.mods_foe_str = battle.mods_foe_agl = battle.mods_foe_spc = 0;
                                    battle.pend_str = battle.pend_agl = battle.pend_spc = 0;
                                    battle.pl_poisoned = battle.foe_poisoned = 0;
                                    battle.stage_self_str = battle.stage_self_agl = battle.stage_self_spc = 0;
                                    battle.stage_foe_str = battle.stage_foe_agl = battle.stage_foe_spc = 0;
                                    battle.hype_self = battle.hype_foe = 0;
                                    battle.nmove_pl_used = battle.hype_pl_used = battle.nmove_foe_used = battle.hype_foe_used = 0;
                                    battle.bench[0] = mint_monster(TRAINER_KITS[KIT_RUINS_KEEPER].bench_sp[0], TRAINER_KITS[KIT_RUINS_KEEPER].bench_lv[0]);
                                    battle.bench[1] = mint_monster(TRAINER_KITS[KIT_RUINS_KEEPER].bench_sp[1], TRAINER_KITS[KIT_RUINS_KEEPER].bench_lv[1]);
                                    battle.bench_n = TRAINER_KITS[KIT_RUINS_KEEPER].bench_n;
                                    battle.grew = 0;
                                    battle.pl = party[lead];
                                    in_battle = 1;
                                    break;
                                case POST_WSOLDIER_QUARTZ:
                                    battle.foe = mint_monster(TRAINER_KITS[KIT_QUARTZ].lead_sp, TRAINER_KITS[KIT_QUARTZ].lead_lv);
                                    battle.wild = 0;
                                    battle.trainer_kind = TRAINER_WSOLDIER_QUARTZ;
                                    battle.phase = 0;
                                    { int n = s_cat(battle.msg[0], 0, "QUARTZ SENDS MOSSBACK");
                                      battle.msg[0][n] = 0; }
                                    battle.msg_n = 1; battle.msg_i = 0; battle.after = BAFTER_ITEM;
                                    battle.cur = 0;
                                    battle.mods_self_str = battle.mods_self_agl = battle.mods_self_spc = 0;
                                    battle.mods_foe_str = battle.mods_foe_agl = battle.mods_foe_spc = 0;
                                    battle.pend_str = battle.pend_agl = battle.pend_spc = 0;
                                    battle.pl_poisoned = battle.foe_poisoned = 0;
                                    battle.stage_self_str = battle.stage_self_agl = battle.stage_self_spc = 0;
                                    battle.stage_foe_str = battle.stage_foe_agl = battle.stage_foe_spc = 0;
                                    battle.hype_self = battle.hype_foe = 0;
                                    battle.nmove_pl_used = battle.hype_pl_used = battle.nmove_foe_used = battle.hype_foe_used = 0;
                                    battle.bench[0] = mint_monster(TRAINER_KITS[KIT_QUARTZ].bench_sp[0], TRAINER_KITS[KIT_QUARTZ].bench_lv[0]);
                                    battle.bench[1] = mint_monster(TRAINER_KITS[KIT_QUARTZ].bench_sp[1], TRAINER_KITS[KIT_QUARTZ].bench_lv[1]);
                                    battle.bench_n = TRAINER_KITS[KIT_QUARTZ].bench_n;
                                    battle.grew = 0;
                                    battle.pl = party[lead];
                                    in_battle = 1;
                                    break;
                                case POST_WSOLDIER_QUARRY_DRILLER:
                                    battle.foe = mint_monster(TRAINER_KITS[KIT_QUARRY_DRILLER].lead_sp, TRAINER_KITS[KIT_QUARRY_DRILLER].lead_lv);
                                    battle.wild = 0;
                                    battle.trainer_kind = TRAINER_WSOLDIER_QUARRY_DRILLER;
                                    battle.phase = 0;
                                    { int n = s_cat(battle.msg[0], 0, "DRILLER SENDS SLATEKIN");
                                      battle.msg[0][n] = 0; }
                                    battle.msg_n = 1; battle.msg_i = 0; battle.after = BAFTER_ITEM;
                                    battle.cur = 0;
                                    battle.mods_self_str = battle.mods_self_agl = battle.mods_self_spc = 0;
                                    battle.mods_foe_str = battle.mods_foe_agl = battle.mods_foe_spc = 0;
                                    battle.pend_str = battle.pend_agl = battle.pend_spc = 0;
                                    battle.pl_poisoned = battle.foe_poisoned = 0;
                                    battle.stage_self_str = battle.stage_self_agl = battle.stage_self_spc = 0;
                                    battle.stage_foe_str = battle.stage_foe_agl = battle.stage_foe_spc = 0;
                                    battle.hype_self = battle.hype_foe = 0;
                                    battle.nmove_pl_used = battle.hype_pl_used = battle.nmove_foe_used = battle.hype_foe_used = 0;
                                    battle.bench[0] = mint_monster(TRAINER_KITS[KIT_QUARRY_DRILLER].bench_sp[0], TRAINER_KITS[KIT_QUARRY_DRILLER].bench_lv[0]);
                                    battle.bench[1] = mint_monster(TRAINER_KITS[KIT_QUARRY_DRILLER].bench_sp[1], TRAINER_KITS[KIT_QUARRY_DRILLER].bench_lv[1]);
                                    battle.bench_n = TRAINER_KITS[KIT_QUARRY_DRILLER].bench_n;
                                    battle.grew = 0;
                                    battle.pl = party[lead];
                                    in_battle = 1;
                                    break;
                                case POST_WSOLDIER_OPAL:
                                    battle.foe = mint_monster(TRAINER_KITS[KIT_OPAL].lead_sp, TRAINER_KITS[KIT_OPAL].lead_lv);
                                    battle.wild = 0;
                                    battle.trainer_kind = TRAINER_WSOLDIER_OPAL;
                                    battle.phase = 0;
                                    { int n = s_cat(battle.msg[0], 0, "OPAL SENDS GLASSWISP");
                                      battle.msg[0][n] = 0; }
                                    battle.msg_n = 1; battle.msg_i = 0; battle.after = BAFTER_ITEM;
                                    battle.cur = 0;
                                    battle.mods_self_str = battle.mods_self_agl = battle.mods_self_spc = 0;
                                    battle.mods_foe_str = battle.mods_foe_agl = battle.mods_foe_spc = 0;
                                    battle.pend_str = battle.pend_agl = battle.pend_spc = 0;
                                    battle.pl_poisoned = battle.foe_poisoned = 0;
                                    battle.stage_self_str = battle.stage_self_agl = battle.stage_self_spc = 0;
                                    battle.stage_foe_str = battle.stage_foe_agl = battle.stage_foe_spc = 0;
                                    battle.hype_self = battle.hype_foe = 0;
                                    battle.nmove_pl_used = battle.hype_pl_used = battle.nmove_foe_used = battle.hype_foe_used = 0;
                                    battle.bench[0] = mint_monster(TRAINER_KITS[KIT_OPAL].bench_sp[0], TRAINER_KITS[KIT_OPAL].bench_lv[0]);
                                    battle.bench[1] = mint_monster(TRAINER_KITS[KIT_OPAL].bench_sp[1], TRAINER_KITS[KIT_OPAL].bench_lv[1]);
                                    battle.bench_n = TRAINER_KITS[KIT_OPAL].bench_n;
                                    battle.grew = 0;
                                    battle.pl = party[lead];
                                    in_battle = 1;
                                    break;
                                case POST_WSOLDIER_MARSH_BOG:
                                    battle.foe = mint_monster(TRAINER_KITS[KIT_MARSH_BOG].lead_sp, TRAINER_KITS[KIT_MARSH_BOG].lead_lv);
                                    battle.wild = 0;
                                    battle.trainer_kind = TRAINER_WSOLDIER_MARSH_BOG;
                                    battle.phase = 0;
                                    { int n = s_cat(battle.msg[0], 0, "BOGWALKER SENDS PEATLING");
                                      battle.msg[0][n] = 0; }
                                    battle.msg_n = 1; battle.msg_i = 0; battle.after = BAFTER_ITEM;
                                    battle.cur = 0;
                                    battle.mods_self_str = battle.mods_self_agl = battle.mods_self_spc = 0;
                                    battle.mods_foe_str = battle.mods_foe_agl = battle.mods_foe_spc = 0;
                                    battle.pend_str = battle.pend_agl = battle.pend_spc = 0;
                                    battle.pl_poisoned = battle.foe_poisoned = 0;
                                    battle.stage_self_str = battle.stage_self_agl = battle.stage_self_spc = 0;
                                    battle.stage_foe_str = battle.stage_foe_agl = battle.stage_foe_spc = 0;
                                    battle.hype_self = battle.hype_foe = 0;
                                    battle.nmove_pl_used = battle.hype_pl_used = battle.nmove_foe_used = battle.hype_foe_used = 0;
                                    battle.bench[0] = mint_monster(TRAINER_KITS[KIT_MARSH_BOG].bench_sp[0], TRAINER_KITS[KIT_MARSH_BOG].bench_lv[0]);
                                    battle.bench[1] = mint_monster(TRAINER_KITS[KIT_MARSH_BOG].bench_sp[1], TRAINER_KITS[KIT_MARSH_BOG].bench_lv[1]);
                                    battle.bench_n = TRAINER_KITS[KIT_MARSH_BOG].bench_n;
                                    battle.grew = 0;
                                    battle.pl = party[lead];
                                    in_battle = 1;
                                    break;
                                case POST_WSOLDIER_MARSH_REED:
                                    battle.foe = mint_monster(TRAINER_KITS[KIT_MARSH_REED].lead_sp, TRAINER_KITS[KIT_MARSH_REED].lead_lv);
                                    battle.wild = 0;
                                    battle.trainer_kind = TRAINER_WSOLDIER_MARSH_REED;
                                    battle.phase = 0;
                                    { int n = s_cat(battle.msg[0], 0, "REEDGUARD SENDS FENWISP");
                                      battle.msg[0][n] = 0; }
                                    battle.msg_n = 1; battle.msg_i = 0; battle.after = BAFTER_ITEM;
                                    battle.cur = 0;
                                    battle.mods_self_str = battle.mods_self_agl = battle.mods_self_spc = 0;
                                    battle.mods_foe_str = battle.mods_foe_agl = battle.mods_foe_spc = 0;
                                    battle.pend_str = battle.pend_agl = battle.pend_spc = 0;
                                    battle.pl_poisoned = battle.foe_poisoned = 0;
                                    battle.stage_self_str = battle.stage_self_agl = battle.stage_self_spc = 0;
                                    battle.stage_foe_str = battle.stage_foe_agl = battle.stage_foe_spc = 0;
                                    battle.hype_self = battle.hype_foe = 0;
                                    battle.nmove_pl_used = battle.hype_pl_used = battle.nmove_foe_used = battle.hype_foe_used = 0;
                                    battle.bench[0] = mint_monster(TRAINER_KITS[KIT_MARSH_REED].bench_sp[0], TRAINER_KITS[KIT_MARSH_REED].bench_lv[0]);
                                    battle.bench[1] = mint_monster(TRAINER_KITS[KIT_MARSH_REED].bench_sp[1], TRAINER_KITS[KIT_MARSH_REED].bench_lv[1]);
                                    battle.bench_n = TRAINER_KITS[KIT_MARSH_REED].bench_n;
                                    battle.grew = 0;
                                    battle.pl = party[lead];
                                    in_battle = 1;
                                    break;
                                case POST_WSOLDIER_COMMANDER_FINAL:
                                    battle.foe = mint_monster(TRAINER_KITS[KIT_COMMANDER_FINAL].lead_sp, TRAINER_KITS[KIT_COMMANDER_FINAL].lead_lv);
                                    battle.wild = 0;
                                    battle.trainer_kind = TRAINER_WSOLDIER_COMMANDER_FINAL;
                                    battle.phase = 0;
                                    { int n = s_cat(battle.msg[0], 0, "COMMANDER SENDS BOULDERAM");
                                      battle.msg[0][n] = 0; }
                                    battle.msg_n = 1; battle.msg_i = 0; battle.after = BAFTER_ITEM;
                                    battle.cur = 0;
                                    battle.mods_self_str = battle.mods_self_agl = battle.mods_self_spc = 0;
                                    battle.mods_foe_str = battle.mods_foe_agl = battle.mods_foe_spc = 0;
                                    battle.pend_str = battle.pend_agl = battle.pend_spc = 0;
                                    battle.pl_poisoned = battle.foe_poisoned = 0;
                                    battle.stage_self_str = battle.stage_self_agl = battle.stage_self_spc = 0;
                                    battle.stage_foe_str = battle.stage_foe_agl = battle.stage_foe_spc = 0;
                                    battle.hype_self = battle.hype_foe = 0;
                                    battle.nmove_pl_used = battle.hype_pl_used = battle.nmove_foe_used = battle.hype_foe_used = 0;
                                    battle.bench[0] = mint_monster(TRAINER_KITS[KIT_COMMANDER_FINAL].bench_sp[0], TRAINER_KITS[KIT_COMMANDER_FINAL].bench_lv[0]);
                                    battle.bench[1] = mint_monster(TRAINER_KITS[KIT_COMMANDER_FINAL].bench_sp[1], TRAINER_KITS[KIT_COMMANDER_FINAL].bench_lv[1]);
                                    battle.bench_n = TRAINER_KITS[KIT_COMMANDER_FINAL].bench_n;
                                    battle.grew = 0;
                                    battle.pl = party[lead];
                                    in_battle = 1;
                                    break;
                                case POST_WSOLDIER_LEAD:
                                    /* Lead fights as himself -- a
                                       single pseudo-species foe, no
                                       bench (KIT_LIEUTENANT_LEAD.
                                       bench_n is baked 0). */
                                    battle.foe = mint_monster(TRAINER_KITS[KIT_LIEUTENANT_LEAD].lead_sp, TRAINER_KITS[KIT_LIEUTENANT_LEAD].lead_lv);
                                    battle.wild = 0;
                                    battle.trainer_kind = TRAINER_WSOLDIER_LEAD;
                                    battle.phase = 0;
                                    { int n = s_cat(battle.msg[0], 0, "LIEUTENANT LEAD BLOCKS THE WAY");
                                      battle.msg[0][n] = 0; }
                                    battle.msg_n = 1; battle.msg_i = 0; battle.after = BAFTER_ITEM;
                                    battle.cur = 0;
                                    battle.mods_self_str = battle.mods_self_agl = battle.mods_self_spc = 0;
                                    battle.mods_foe_str = battle.mods_foe_agl = battle.mods_foe_spc = 0;
                                    battle.pend_str = battle.pend_agl = battle.pend_spc = 0;
                                    battle.pl_poisoned = battle.foe_poisoned = 0;
                                    battle.stage_self_str = battle.stage_self_agl = battle.stage_self_spc = 0;
                                    battle.stage_foe_str = battle.stage_foe_agl = battle.stage_foe_spc = 0;
                                    battle.hype_self = battle.hype_foe = 0;
                                    battle.nmove_pl_used = battle.hype_pl_used = battle.nmove_foe_used = battle.hype_foe_used = 0;
                                    battle.bench_n = 0;
                                    battle.grew = 0;

                                case POST_WSOLDIER_HEAVENFALL_GRAVE:
                                    battle.foe = mint_monster(TRAINER_KITS[KIT_HEAVENFALL_GRAVE].lead_sp, TRAINER_KITS[KIT_HEAVENFALL_GRAVE].lead_lv);
                                    battle.wild = 0;
                                    battle.trainer_kind = TRAINER_WSOLDIER_HEAVENFALL_GRAVE;
                                    battle.phase = 0;
                                    { int n = s_cat(battle.msg[0], 0, "HEAVENFALL ANSWERS THE SCROLL");
                                      battle.msg[0][n] = 0; }
                                    battle.msg_n = 1; battle.msg_i = 0; battle.after = BAFTER_ITEM;
                                    battle.cur = 0;
                                    battle.mods_self_str = battle.mods_self_agl = battle.mods_self_spc = 0;
                                    battle.mods_foe_str = battle.mods_foe_agl = battle.mods_foe_spc = 0;
                                    battle.pend_str = battle.pend_agl = battle.pend_spc = 0;
                                    battle.pl_poisoned = battle.foe_poisoned = 0;
                                    battle.stage_self_str = battle.stage_self_agl = battle.stage_self_spc = 0;
                                    battle.stage_foe_str = battle.stage_foe_agl = battle.stage_foe_spc = 0;
                                    battle.hype_self = battle.hype_foe = 0;
                                    battle.nmove_pl_used = battle.hype_pl_used = battle.nmove_foe_used = battle.hype_foe_used = 0;
                                    battle.bench_n = 0;
                                    battle.grew = 0;
                                    battle.pl = party[lead];
                                    in_battle = 1;
                                    break;

                                    battle.pl = party[lead];
                                    in_battle = 1;
                                    break;
                                case POST_WSOLDIER_WARDEN:
                                    battle.foe = mint_monster(TRAINER_KITS[KIT_RUINS_WARDEN].lead_sp, TRAINER_KITS[KIT_RUINS_WARDEN].lead_lv);
                                    battle.wild = 0;
                                    battle.trainer_kind = TRAINER_WSOLDIER_WARDEN;
                                    battle.phase = 0;
                                    { int n = s_cat(battle.msg[0], 0, "WARDEN SENDS TORTCASK");
                                      battle.msg[0][n] = 0; }
                                    battle.msg_n = 1; battle.msg_i = 0; battle.after = BAFTER_ITEM;
                                    battle.cur = 0;
                                    battle.mods_self_str = battle.mods_self_agl = battle.mods_self_spc = 0;
                                    battle.mods_foe_str = battle.mods_foe_agl = battle.mods_foe_spc = 0;
                                    battle.pend_str = battle.pend_agl = battle.pend_spc = 0;
                                    battle.pl_poisoned = battle.foe_poisoned = 0;
                                    battle.stage_self_str = battle.stage_self_agl = battle.stage_self_spc = 0;
                                    battle.stage_foe_str = battle.stage_foe_agl = battle.stage_foe_spc = 0;
                                    battle.hype_self = battle.hype_foe = 0;
                                    battle.nmove_pl_used = battle.hype_pl_used = battle.nmove_foe_used = battle.hype_foe_used = 0;
                                    battle.bench[0] = mint_monster(TRAINER_KITS[KIT_RUINS_WARDEN].bench_sp[0], TRAINER_KITS[KIT_RUINS_WARDEN].bench_lv[0]);
                                    battle.bench[1] = mint_monster(TRAINER_KITS[KIT_RUINS_WARDEN].bench_sp[1], TRAINER_KITS[KIT_RUINS_WARDEN].bench_lv[1]);
                                    battle.bench_n = TRAINER_KITS[KIT_RUINS_WARDEN].bench_n;
                                    battle.grew = 0;
                                    battle.pl = party[lead];
                                    in_battle = 1;
                                    break;
                                case POST_SHINIGAMI:
                                    battle.foe = mint_monster(SP_CRYMARE, KIT_SHINIGAMI_LEAD_LV);
                                    battle.wild = 0;
                                    battle.trainer_kind = TRAINER_SHINIGAMI;
                                    battle.phase = 0;
                                    { int n = s_cat(battle.msg[0], 0, "SHINIGAMI SENDS CRYMARE");
                                      battle.msg[0][n] = 0; }
                                    battle.msg_n = 1; battle.msg_i = 0; battle.after = BAFTER_ITEM;
                                    battle.cur = 0;
                                    battle.mods_self_str = battle.mods_self_agl = battle.mods_self_spc = 0;
                                    battle.mods_foe_str = battle.mods_foe_agl = battle.mods_foe_spc = 0;
                                    battle.pend_str = battle.pend_agl = battle.pend_spc = 0;
                                    battle.pl_poisoned = battle.foe_poisoned = 0;
                                    battle.stage_self_str = battle.stage_self_agl = battle.stage_self_spc = 0;
                                    battle.stage_foe_str = battle.stage_foe_agl = battle.stage_foe_spc = 0;
                                    battle.hype_self = battle.hype_foe = 0;
                                    battle.nmove_pl_used = battle.hype_pl_used = battle.nmove_foe_used = battle.hype_foe_used = 0;
                                    battle.bench[0] = mint_monster(SP_CRYMARE, KIT_SHINIGAMI_B0_LV);
                                    battle.bench[1] = mint_monster(SP_CRYMARE, KIT_SHINIGAMI_B1_LV);
                                    battle.bench_n = 2;
                                    battle.grew = 0;
                                    battle.pl = party[lead];
                                    in_battle = 1;
                                    break;
                                case POST_SOLDIER: {
                                    const SoldierDef *sd = &SOLDIERS[post_soldier_id];
                                    int n;
                                    battle.foe = mint_monster(sd->species, sd->lv);
                                    battle.wild = 0;
                                    battle.trainer_kind = TRAINER_SOLDIER;
                                    battle.soldier_id = post_soldier_id;
                                    battle.phase = 0;
                                    n = s_cat(battle.msg[0], 0, sd->name);
                                    n = s_cat(battle.msg[0], n, " SENDS ");
                                    n = s_cat(battle.msg[0], n, SPECIES[sd->species].name);
                                    battle.msg[0][n] = 0;
                                    battle.msg_n = 1; battle.msg_i = 0; battle.after = BAFTER_ITEM;
                                    battle.cur = 0;
                                    battle.mods_self_str = battle.mods_self_agl = battle.mods_self_spc = 0;
                                    battle.mods_foe_str = battle.mods_foe_agl = battle.mods_foe_spc = 0;
                                    battle.pend_str = battle.pend_agl = battle.pend_spc = 0;
                                    battle.pl_poisoned = battle.foe_poisoned = 0;
                                    battle.stage_self_str = battle.stage_self_agl = battle.stage_self_spc = 0;
                                    battle.stage_foe_str = battle.stage_foe_agl = battle.stage_foe_spc = 0;
                                    battle.hype_self = battle.hype_foe = 0;
                                    battle.nmove_pl_used = battle.hype_pl_used = battle.nmove_foe_used = battle.hype_foe_used = 0;
                                    battle.bench_n = 0;
                                    battle.grew = 0;
                                    battle.pl = party[lead];
                                    in_battle = 1;
                                    break;
                                }
                                case POST_CATHLEEN:
                                    if(!cath_caught) {
                                        int n;
        battle.foe = mint_monster(SP_CATHLEEN, KIT_CATHLEEN_LV);
                                        battle.wild = 1;
                                        battle.trainer_kind = TRAINER_WILD;
                                        battle.phase = 0;
                                        n = s_cat(battle.msg[0], 0, "CATHLEEN STANDS AGAINST YOU");
                                        battle.msg[0][n] = 0;
                                        battle.msg_n = 1; battle.msg_i = 0; battle.after = BAFTER_ITEM;
                                        battle.cur = 0;
                                        battle.mods_self_str = battle.mods_self_agl = battle.mods_self_spc = 0;
                                        battle.mods_foe_str = battle.mods_foe_agl = battle.mods_foe_spc = 0;
                                    battle.pend_str = battle.pend_agl = battle.pend_spc = 0;
                                    battle.pl_poisoned = battle.foe_poisoned = 0;
                                    battle.stage_self_str = battle.stage_self_agl = battle.stage_self_spc = 0;
                                    battle.stage_foe_str = battle.stage_foe_agl = battle.stage_foe_spc = 0;
                                    battle.hype_self = battle.hype_foe = 0;
                                    battle.nmove_pl_used = battle.hype_pl_used = battle.nmove_foe_used = battle.hype_foe_used = 0;
                                        battle.bench_n = 0;
                                        battle.grew = 0;
                                        battle.pl = party[lead];
                                        in_battle = 1;
                                    }
                                    break;
                                case POST_SHOP:
                                    if(reputation <= LOGIC_REP_REFUSE_AT) {
                                        seq_lines = TALK_SHOP_REFUSE;
                                        seq_len = TALK_LEN(TALK_SHOP_REFUSE);
                                        seq_beat = 0;
                                        post_action = POST_NONE;
                                    } else if(beat_heavenfall && !heavenfall_rep_warned) {
                                        heavenfall_rep_warned = 1;
                                        seq_lines = TALK_HEAVENFALL_SHOP_WARN;
                                        seq_len = TALK_LEN(TALK_HEAVENFALL_SHOP_WARN);
                                        seq_beat = 0;
                                        post_action = POST_SHOP;
                                    } else if(shop_keep_id == 3 && reputation < 0 && *bag_field(&bag, 19) <= 0) {
                                        /* The offer is followed by a dedicated one-item shop. */
                                        dray_knife_offered = 1;
                                        seq_lines = TALK_DRAY_KNIFE_OFFER;
                                        seq_len = TALK_LEN(TALK_DRAY_KNIFE_OFFER);
                                        seq_beat = 0;
                                        post_action = POST_DRAY_KNIFE_SHOP;
                                    } else {
                                        shop_open = 1;
                                        shop_sell_tab = 0;
                                        shop_cur = 0;
                                    }
                                    break;
                                case POST_DRAY_KNIFE_SHOP:
                                    /* The offer dialogue has finished. Add the
                                       knife to Dray's existing stock (already
                                       rolled by roll_all_shop_stock() at boot/
                                       reset/rest) instead of replacing it --
                                       there's only ever one in the game, so
                                       its own quantity is forced to 1
                                       regardless of the roll, but every other
                                       item he carries stays untouched. */
                                    shop_stock[3][19] = 1;
                                    shop_open = 1;
                                    shop_sell_tab = 0;
                                    shop_cur = 0;
                                    break;
                                case POST_MASON_LEAVE:
                                    /* startRivalLeave(). */
                                    mason_state = 3;
                                    mason_dir = 0;
                                    mason_anim = 0.0f;
                                    break;
                                case POST_ANNE_LEAVE:
                                    /* startAnneLeave(). anne_state is
                                       already 2 from the gift-reach
                                       trigger above; this just kicks
                                       off the actual walk-away once
                                       her gift dialogue has closed. */
                                    anne_state = 3;
                                    anne_dir = 0;
                                    anne_anim = 0.0f;
                                    break;
                                
                                case POST_OPEN_MERCY:
                                    /* Leg 2.9.2: open post-battle mercy menu. */
                                    mercy_mode = 1;
                                    mercy_cur = 0;
                                    {
                                        int bi, lv = battle.foe.lv;
                                        for(bi = 0; bi < battle.bench_n && bi < 2; bi++)
                                            lv += battle.bench[bi].lv;
                                        mercy_foe_levels = lv > 0 ? lv : 1;
                                    }
                                    {
                                        const char *nm = "Trainer";
                                        if(battle.trainer_kind == TRAINER_CALDER) nm = "Calder";
                                        else if(battle.trainer_kind == TRAINER_SHINIGAMI) nm = "Shinigami";
                                        else nm = "Trainer";
                                        int i; for(i = 0; i < 31 && nm[i]; i++) mercy_foe_name[i] = nm[i];
                                        mercy_foe_name[i] = 0;
                                    }
                                    break;

                                case POST_OPEN_CHOICE:
                                    /* Opens draw_choice() once
                                       TALK_SHINIGAMI_WIN closes -- Anne
                                       already delivered the reveal
                                       right after Cathleen, so this is
                                       just the scroll/choice payoff,
                                       no walk-up needed. */
                                    choice_mode = 1;
                                    choice_cur = 0;
                                    break;
                                case POST_ENDING_FINAL:
                                /* 2.4: no auto-gauntlet. Heavenfall path unlocks grove entrance. */
                                if (chose_heavenfall) {
                                    /* flag already set; player uses grove G when maps rebaked */
                                }
                                break;
                                case POST_CREDITS_FINAL:
                                    ending_mode = 1;
                                    ending_i = 0;
                                    break;
                                case POST_BED_HEAL:
                                    fade_state = FADE_OUT;
                                    fade_timer = 0;
                                    fade_action = FADE_ACTION_BED;
                                    break;
                                case POST_PRIESTESS_TELEPORT:
                                    fade_state = FADE_OUT;
                                    fade_timer = 0;
                                    fade_action = FADE_ACTION_PRIESTESS;
                                    break;
                                case POST_LEAD_GAMEOVER:
                                    /* Plain black fade (no scream, no
                                       red tint -- that's the genuine
                                       party-wipe path, POST_HFGAMEOVER_
                                       SCREAM below). Matches web's
                                       leadThanksGO -> startFade(
                                       "hfGameOver"). */
                                    fade_state = FADE_OUT;
                                    fade_timer = 0;
                                    fade_action = FADE_ACTION_HFGAMEOVER;
                                    break;
                                case POST_HFGAMEOVER_SCREAM:
                                    /* Matches web's runHeavenfallGameOverFx():
                                       scream + red fade, same stand-in
                                       SFX and red-tint flag the mercy
                                       execute path uses (Leg 2.9). */
                                    chip_sfx_faint();
                                    g_mercy_red_fade = 1;
                                    fade_state = FADE_OUT;
                                    fade_timer = 0;
                                    fade_action = FADE_ACTION_HFGAMEOVER;
                                    break;
                                default:
                                    break;
                            }
                        }
                        post_action = POST_NONE;
                    }
                }
                else if(bag.bowieKnife > 0 &&
                        find_backstab_target(map_id, px, py, ft, party_n) >= 0) {
                    /* Leg 2.12 Bowie Knife: an eligible, unspotted
                       roamable trainer is in interact range -- open the
                       Approach/Backstab prompt instead of the normal
                       try_npc_script() dialogue. Re-derive the target's
                       levels here (kit_for_pending()) rather than
                       threading them out of find_backstab_target(),
                       matching openBackstabChoice()'s own TRAINERS[]
                       lookup on the web side. */
                    int idx = find_backstab_target(map_id, px, py, ft, party_n);
                    int si2 = npc_match_step(&NPC_DEFS[idx], ft, party_n);
                    const NpcStep *bst = &NPC_STEPS[si2];
                    int kit = kit_for_pending(bst->pending);
                    int lv = 1;
                    if(kit >= 0) {
                        int bi;
                        lv = TRAINER_KITS[kit].lead_lv;
                        for(bi = 0; bi < TRAINER_KITS[kit].bench_n; bi++)
                            lv += TRAINER_KITS[kit].bench_lv[bi];
                    }
                    backstab_npc_idx = idx;
                    backstab_levels = lv > 0 ? lv : 1;
                    backstab_mode = 1;
                    backstab_cur = 0;
                    chip_sfx_ui();
                }
                else {
                    /* Scripted NPCs from content/world.json (first-match).
                       Forest soldiers still move, so beaten-soldier talk
                       stays as a special case after the table miss. */
                    int npc_after = 0, npc_pending = -1;
                    NpcRun nr;
                    nr.map_id = map_id;
                    nr.px = px;
                    nr.py = py;
                    nr.party_n = party_n;
                    nr.ft = ft;
                    nr.bag = &bag;
                    nr.marks = &marks;
                    nr.party = party;
                    nr.pn = &party_n;
                    nr.lead = &lead;
                    nr.seq_lines = &seq_lines;
                    nr.seq_len = &seq_len;
                    nr.after = &npc_after;
                    nr.pending = &npc_pending;
                    if(try_npc_script(&nr)) {
                        seq_beat = 0;
                        post_action = npc_after_to_post_action(npc_after, npc_pending, &shop_keep_id);
                    }
                    else if(map_id == MAP_FOREST) {
                        int si;
                        for(si = 0; si < 3; si++) {
                            if(!soldier_beaten[si] &&
                               bag.bowieKnife > 0 && !soldiers[si].chase &&
                               soldier_los(map_id, soldiers[si].x, soldiers[si].y, soldiers[si].dir, px, py) == 0) {
                                float ddxf = (float)px - soldiers[si].x, ddyf = (float)py - soldiers[si].y;
                                float d2f = ddxf * ddxf + ddyf * ddyf;
                                if(d2f <= ACTOR_CHASE_CATCH * ACTOR_CHASE_CATCH) {
                                    /* Leg 2.12 Bowie Knife, forest soldiers:
                                       patrol/scout/sentry live in soldiers[]/
                                       SOLDIERS[], not NPC_DEFS, so
                                       find_backstab_target() never reaches
                                       them -- this is their own eligibility
                                       check, same shape (knife carried, not
                                       beaten, hasn't started a chase, hasn't
                                       spotted the player via soldier_los()'s
                                       one-direction facing ray). No warp-gate
                                       check needed: none of marks '1'/'2'/'3'
                                       are ever a warp tile on FOREST. */
                                    backstab_soldier_idx = si;
                                    backstab_levels = SOLDIERS[si].lv > 0 ? SOLDIERS[si].lv : 1;
                                    backstab_mode = 1;
                                    backstab_cur = 0;
                                    chip_sfx_ui();
                                    break;
                                }
                            }
                            int ddx = px - (int)soldiers[si].x, ddy = py - (int)soldiers[si].y;
                            if(soldier_beaten[si] && ddx * ddx + ddy * ddy <= 676) {
                                seq_lines = TALK_SOLDIER_DONE;
                                seq_len = TALK_LEN(TALK_SOLDIER_DONE);
                                seq_beat = 0;
                                break;
                            }
                        }
                    }
                }
            }

                        /* Menu open, only from plain world state (state.lua only
               reaches selectPressed()/startPressed() outside TALK/
               BATTLE/etc, which here just means no dialogue active). */
            if(!seq_lines && fade_state == FADE_NONE) {
                if(y_now && !prev_y) {
                    menu_mode = 1;
                    bag_cur = 0;
                    heal_item = -1;
                }
                else if(start_now && !prev_start) {
                    menu_mode = 3;
                    pause_cur = 0;
                    chip_sfx_ui();
                }
            }
        }

        /* Draw every frame, unconditionally, into the buffer that was
           just hidden by the flip above. See the fb_flip comment for
           why this has to be unconditional now, unlike the earlier
           dirty-check versions. */
        if(state == 0) {
            draw_press_start(title_cur, have_save);
        }
        else if(ending_mode) {
            if(chose_heavenfall)
                draw_ending(DEMO_END_HEAVENFALL, TALK_LEN(DEMO_END_HEAVENFALL), ending_i);
            else
                draw_ending(DEMO_END, TALK_LEN(DEMO_END), ending_i);
        }
        else {
            compute_camera(map_id, px, py, &cam_x, &cam_y);
            draw_map(map_id, cam_x, cam_y);
            draw_props(map_id, cam_x, cam_y, looted_crate);
            {
                WorldSprite ws_list[MAX_WORLD_SPRITES];
                int ws_n = 0;
                int mason_frame = (mason_state == 1 || mason_state == 3) ? (int)mason_anim % 4 : 0;
                int anne_frame = (anne_state == 1 || anne_state == 3) ? (int)anne_anim % 4 : 0;
                collect_npcs(ws_list, &ws_n, map_id, frame_count,
                             mason_state, mason_x, mason_y, mason_dir, mason_frame,
                             anne_state, anne_x, anne_y, anne_dir, anne_frame,
                             cath_caught, beat_shin, saw_shinigami_rock, soldiers, soldier_beaten,
                             beat_calder, has_scroll,
                             got_chest, quarry_crate_looted, quarry_shelf_searched);
                ws_push(ws_list, &ws_n, MAX_FRAMES[pdir][(anim_counter / 10) & 3],
                        MAX_SPRITE_W, MAX_SPRITE_H, px, py);
                ws_sort_and_draw(ws_list, ws_n, cam_x, cam_y);
            }
            draw_hud(got_shelf, looted_crate, bag.bandage, has_scroll, reputation);
            if(seq_lines)
                draw_dialogue_box(&seq_lines[seq_beat]);
            else if(hud_t > 0)
                draw_hud_toast(hud_flash);
            draw_map_title(map_id);
            if(menu_mode == 1)
                draw_bag_menu(&bag, marks, bag_cur);
            else if(menu_mode == 2)
                draw_party_menu(party, party_n, lead, party_cur, party_detail, heal_item, catch_swap);
            else if(menu_mode == 3)
                draw_pause_menu(pause_cur);
            else if(menu_mode == 4)
                draw_crydex(dex_cur, dex_entry);
            else if(menu_mode == 5)
                draw_settings_menu();
            if(in_battle)
                draw_battle(&battle, &bag, frame_count,
                            battle_foe_enter_t, battle_foe_faint_t,
                            battle_pl_enter_t, battle_pl_faint_t);
            if(shop_open)
                draw_shop(&bag, marks, shop_sell_tab, shop_cur, shop_keep_id,
                          reputation, shop_free, dray_knife_offered);
            if(choice_mode)
                draw_choice(choice_cur);
            if(mercy_mode)
                draw_mercy(mercy_cur, mercy_foe_name);
            if(backstab_mode)
                draw_backstab(backstab_cur);
        }

        /* Post-process over whatever was just drawn, whatever it was
           -- see the fade_state comment up at its declaration. */
        apply_fade(fade_level(fade_state, fade_timer));

        prev_start = start_now;
        prev_b = b_now;
        prev_y = y_now;
        prev_x = x_now;
        prev_a = a_now;
        prev_up = up_now;
        prev_down = down_now;
        prev_left = left_now;
        prev_right = right_now;
    }
}
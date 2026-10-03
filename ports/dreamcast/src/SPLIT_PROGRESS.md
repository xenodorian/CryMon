# Dreamcast main.c split: progress

Goal: replace the single 522 KB `src/main.c` with small files under folders,
included back in the original order, so each edit touches one small file.
`src/main.c` is NOT modified until every piece below exists; then it becomes a
list of `#include` lines in this order.

## Done (copies of main.c, original order)
1. `src/core/prelude.inc` - header comment, typedefs, memset/memcpy, includes
2. `src/video/framebuffer.inc` - PVR regs, video_init, fb_put/get, fade, rects
   (SCREEN_W/SCREEN_H/FB_SCALE are now `#ifndef` macros; fb_put loops FB_SCALE)
3. `src/video/sprite_blit.inc` - blit_sprite*, shiny_tint, blit_sprite_anim
4. `src/font/glyphs_az09.inc` - font banner, font_AZ, font_09
5. `src/font/glyphs_symbols.inc` - minus/plus/slash and punctuation glyphs
6. `src/font/text.inc` - draw_glyph, draw_text_s, word wrap, draw_wrapped*
7. `src/ui/strings.inc` - s_cat, s_cat_uint
8. `src/ui/title_screen.inc` - TITLE_SCALE, DIALOGUE_SCALE, draw_press_start
9. `src/input/maple.inc` - Maple bus driver, pressed()
10. `src/world/map_defs.inc` - world banner, `#define TILE 20`, ATK_*, Map typedef

## Next
Resume at main.c char offset 37927, which starts with
`#include "content_maps.inc"` (check the first characters before copying).
main.c is 522,138 bytes.

## Facts found while splitting
- The Dreamcast build uses `TILE 20` at 320x240, so its view is 16 x 12 tiles.
  The web build uses 32 px tiles at 640x480, so 20 x 15 tiles.

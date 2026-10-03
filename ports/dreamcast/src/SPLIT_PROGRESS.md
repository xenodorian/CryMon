# Dreamcast main.c split: progress

Goal: replace the single 522 KB `src/main.c` with small files under folders,
included back in the original order, so each edit touches one small file.
`src/main.c` is NOT modified until every piece below exists; then it becomes a
list of `#include` lines in this order. Work directly on `main`, no branches.

Status as of 2026-10-03: about 7% done (38 KB of 522,138 bytes).

## Done (hand-copied from main.c, original order, not yet compiled)
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
Reads return at most 8,000 characters; several reads can be issued in parallel
with different offsets. A chunk usually ends mid-line: start the next read at
the beginning of that partial line.

## Final switch (do last)
- Replace `src/main.c` with `#include` lines for every part, in order.
- Makefile: `src/main.o` currently compiles `build/main_native.c`, produced by
  `tools/native480.sed` from main.c. After the switch, drop the sed step and
  pass `-DSCREEN_W=640 -DSCREEN_H=480 -DFB_SCALE=1` for NATIVE=1 instead
  (NATIVE=0 passes nothing, giving the original 320x240 look).
- Do not switch until CI can compile. As of this note, the "Build Dreamcast CDI"
  workflow fails at the "Generate sprites" step, before the compile step, and
  failed the same way before the native-480p commit (`ca1be47`).

## Facts found while splitting
- The Dreamcast build uses `TILE 20` at 320x240, so its view is 16 x 12 tiles.
  The web build uses 32 px tiles at 640x480, so 20 x 15 tiles.
- Layout code is written in 320x240 coordinates, so native 640x480 needs the
  layout reworked (phases 2 to 4 of the 480p plan), not just the constants.

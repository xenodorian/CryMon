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

## Next
Resume at main.c char offset 21942, which starts with the comment
`/* '-', '+', '/', needed by the battle system's stat-mod a...`
(check the first characters before copying). main.c is 522,138 bytes.

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

/* Logical screen size and framebuffer scale. The defaults are the original
   320x240 layout drawn as 2x2 blocks. The Makefile passes
   -DSCREEN_W=640 -DSCREEN_H=480 -DFB_SCALE=1 for the native 640x480 build
   (NATIVE=1, the default). */
#ifndef SCREEN_W
#define SCREEN_W 320
#endif
#ifndef SCREEN_H
#define SCREEN_H 240
#endif

/* Flycast high-res reads the software framebuffer, not a scaled-up 3D
   render, so the picture has to actually be 640x480. Layout, tiles,
   camera, menus and collision stay in the SCREEN_W x SCREEN_H coordinates
   above. With FB_SCALE 2, put_pixel writes each of those as a 2x2 block.
   KallistiOS DM_640x480_VGA, RGB565, progressive 60Hz. Hardware pixel-double
   stays off: turning it on would double this buffer again. */
#ifndef FB_SCALE
#define FB_SCALE 2
#endif
#define FB_W (SCREEN_W * FB_SCALE)
#define FB_H (SCREEN_H * FB_SCALE)
#define FB_PIXELS ((u32)FB_W * (u32)FB_H)

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
#define FB_OFFSET1 0x00096000u /* FB_W * FB_H * 2 = 614400 */

static u32 fb_back_offset = FB_OFFSET1;
static volatile u16 *draw_fb = (volatile u16 *)(0xa5000000u + FB_OFFSET1);

static void fb_flip(void) {
    PVR(PVR_FB_ADDR) = fb_back_offset;
    fb_back_offset = (fb_back_offset == FB_OFFSET0) ? FB_OFFSET1 : FB_OFFSET0;
    draw_fb = (volatile u16 *)(0xa5000000u + fb_back_offset);
}

/* DM_640x480_VGA, from KallistiOS vid_builtin (hardware/video.c).
   On VGA the second scanline interrupt is stored << 1, matching
   vid_set_mode_ex. FB_CFG_1 bit 23 is the VGA cable select. */
#define SCANLINES 524
#define CLOCKS    857
#define BITMAPX   172
#define BITMAPY   40
#define SCANINT1  21
#define SCANINT2  260
#define BORDERX1  126
#define BORDERX2  837
#define BORDERY1  36
#define BORDERY2  516

static void video_init(void) {
    PVR(PVR_VIDEO_CFG) = PVR(PVR_VIDEO_CFG) | 0x8u;
    PVR(PVR_FB_CFG_1)  = PVR(PVR_FB_CFG_1) & ~1u;

    PVR(PVR_BORDER_COLOR) = 0;

    /* PM_RGB565 is 1, so pixel mode lives in bits 2-3. Bit 23 = VGA.
       No line-double (that bit is 1, only set with VID_LINEDOUBLE). */
    PVR(PVR_FB_CFG_1) = (1u << 2) | (1u << 23);
    PVR(PVR_FB_CFG_2) = 1u | (1u << 3);

    PVR(PVR_RENDER_MODULO) = (FB_W * 2) / 8;
    PVR(PVR_FB_ADDR) = 0;

    PVR(PVR_FB_SIZE) = (((FB_W * 2) / 4) - 1)
                      | (1u << 20)
                      | ((FB_H - 1u) << 10);

    PVR(PVR_VPOS_IRQ) = (SCANINT1 << 16) | (SCANINT2 << 1);
    PVR(PVR_IL_CFG) = 0x100;

    PVR(PVR_BORDER_X) = (BORDERX1 << 16) | BORDERX2;
    PVR(PVR_BORDER_Y) = (BORDERY1 << 16) | BORDERY2;
    PVR(PVR_SCAN_CLK) = (SCANLINES << 16) | CLOCKS;

    /* 640x480 progressive is 1:1. Bit 0x100 is VID_PIXELDOUBLE. */
    PVR(PVR_VIDEO_CFG) = PVR(PVR_VIDEO_CFG) & ~0x100u;

    PVR(PVR_BITMAP_X) = BITMAPX;
    PVR(PVR_BITMAP_Y) = (BITMAPY << 16) | BITMAPY;

    /* Cable type in bits 8-9: 0 VGA, 2 RGB, 3 composite. */
    *(volatile u32 *)0xa0702c00 =
        *(volatile u32 *)0xa0702c00 & 0xfffffcffu;

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
    for(i = 0; i < FB_PIXELS; i++)
        draw_fb[i] = 0x0000;
}

/* Screen fade to/from black (bed heal, a party wipe teleporting home
   -- see main()'s fade_state machine). There's no alpha channel to
   composite with here, so this darkens whatever was already drawn
   into draw_fb this frame, in place, as the very last step before
   fb_flip -- level is 0 (untouched) to FADE_STEPS (fully black).
   FADE_STEPS is a power of 2 so the per-channel scale is a multiply
   + shift, not a divide, cheap enough to run over the whole
   framebuffer every frame a fade is in progress.

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
            for(j = 0; j < FB_PIXELS; j++) draw_fb[j] = ((u16)(((80 >> 3) << 11) | ((8 >> 2) << 5) | (8 >> 3)));
        } else {
            vram_clear();
        }
        return;
    }
    keep = (u32)(FADE_STEPS - level);
    for(i = 0; i < FB_PIXELS; i++) {
        u16 c = draw_fb[i];
        u16 r = (u16)(((u32)((c >> 11) & 0x1Fu) * keep) >> 4);
        u16 g = (u16)(((u32)((c >> 5) & 0x3Fu) * keep) >> 4);
        u16 b = (u16)(((u32)(c & 0x1Fu) * keep) >> 4);
        draw_fb[i] = (u16)((r << 11) | (g << 5) | b);
    }
}

/* Logical (x, y) is one cell of the SCREEN_W x SCREEN_H layout. The
   framebuffer is 640x480, so with FB_SCALE 2 that cell is the 2x2 block at
   (x*2, y*2); with FB_SCALE 1 it is a single pixel. */
static u16 fb_get(int x, int y) {
    return draw_fb[(y * FB_SCALE) * FB_W + (x * FB_SCALE)];
}

static void fb_put(int x, int y, u16 color) {
    int px = x * FB_SCALE;
    int py = y * FB_SCALE;
    int bx, by;
    for(by = 0; by < FB_SCALE; by++)
        for(bx = 0; bx < FB_SCALE; bx++)
            draw_fb[(py + by) * FB_W + px + bx] = color;
}

static void put_pixel(int x, int y, u16 color) {
    if(x < 0 || x >= SCREEN_W || y < 0 || y >= SCREEN_H)
        return;
    fb_put(x, y, color);
}

static void fill_rect(int x, int y, int w, int h, u16 color) {
    int px, py;
    for(py = y; py < y + h; py++)
        for(px = x; px < x + w; px++)
            put_pixel(px, py, color);
}

/* Halves what is already drawn in a rect: a see-through dark panel that
   keeps battle text readable over the painted backdrops. */
static void dim_rect(int x, int y, int w, int h) {
    int px, py;
    for(py = y; py < y + h; py++) {
        if(py < 0 || py >= SCREEN_H) continue;
        for(px = x; px < x + w; px++) {
            u16 c;
            if(px < 0 || px >= SCREEN_W) continue;
            c = (u16)((fb_get(px, py) >> 1) & 0x7BEFu);
            fb_put(px, py, c);
        }
    }
}

static u16 rgb565(u8 r, u8 g, u8 b) {
    return (u16)(((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3));
}


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
static void draw_title_sprites(void);

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
/* Set by draw_battle_sprites() around one blit: 1 = draw the sprite
   washed toward white (the hurt blink). */
static int anim_flash = 0;

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
            if(anim_flash)
                c = (u16)(((((c >> 11) & 0x1Fu) + 0x1Fu) / 2u << 11) |
                          ((((c >> 5) & 0x3Fu) + 0x3Fu) / 2u << 5) | (((c & 0x1Fu) + 0x1Fu) / 2u));
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


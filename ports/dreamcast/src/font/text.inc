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
        else if(*s == '>')
            draw_glyph(cx, y, glyph_gt, color, scale);
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

/* Word-wrap into a fixed number of visible lines per dialogue page.
   The Dreamcast text strip is only 40px tall, so at the 9px line spacing
   used here it safely fits THREE 8px glyph rows. Older code kept drawing
   every wrapped line, which meant a fourth line was rendered below the
   framebuffer/text strip and got clipped. Long beats are now split into
   sequential pages; A advances the page before advancing to the next beat. */
#define WRAP_BUF_MAX 40
#define DIALOGUE_LINES_PER_PAGE 3

static int wrapped_line_count(const char *s, int max_chars) {
    int lines = 0, buf_len = 0;
    const char *p = s;

    if(!s || !*s) return 1;

    for(;;) {
        int wlen = word_len(p);
        int need = wlen + (buf_len > 0 ? 1 : 0);

        if(buf_len > 0 && buf_len + need > max_chars) {
            lines++;
            buf_len = 0;
        }

        if(buf_len > 0)
            buf_len++;
        {
            int i;
            for(i = 0; i < wlen && buf_len < WRAP_BUF_MAX; i++)
                buf_len++;
        }

        p += wlen;
        if(*p != ' ')
            break;
        p++;
    }
    return lines + 1;
}

static int wrapped_page_count(const char *s, int max_chars) {
    int lines = wrapped_line_count(s, max_chars);
    return (lines + DIALOGUE_LINES_PER_PAGE - 1) / DIALOGUE_LINES_PER_PAGE;
}

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


static void draw_wrapped_page(const char *s, int x, int y, u16 color, int scale,
                              int max_chars, int line_h, int page) {
    char buf[WRAP_BUF_MAX + 1];
    int buf_len = 0;
    int line = 0;
    const char *p = s;
    int first_line = page * DIALOGUE_LINES_PER_PAGE;
    int last_line = first_line + DIALOGUE_LINES_PER_PAGE;

    if(page < 0) page = 0;
    first_line = page * DIALOGUE_LINES_PER_PAGE;
    last_line = first_line + DIALOGUE_LINES_PER_PAGE;

    for(;;) {
        int wlen = word_len(p);
        int need = wlen + (buf_len > 0 ? 1 : 0);

        if(buf_len > 0 && buf_len + need > max_chars) {
            buf[buf_len] = 0;
            if(line >= first_line && line < last_line)
                draw_text_s(buf, x, y + (line - first_line) * line_h, color, scale);
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
    if(line >= first_line && line < last_line)
        draw_text_s(buf, x, y + (line - first_line) * line_h, color, scale);
}


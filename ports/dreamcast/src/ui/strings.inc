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


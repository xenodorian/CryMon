/* Software SDL2 stand-in for PortMaster inspect dumps (no GPU). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

typedef struct SDL_Window SDL_Window;
typedef struct SDL_Renderer SDL_Renderer;
typedef struct { int x, y, w, h; } SDL_Rect;
typedef struct { uint32_t type; uint8_t pad[56]; } SDL_Event;
typedef struct {
	int w, h;
	uint8_t *pix; /* ABGR bytes */
} SDL_Texture;

#define VW 640
#define VH 480

static uint8_t fb[VW * VH * 4];
static uint8_t draw_rgba[4] = {18, 17, 14, 255};
static uint8_t kbd[512];
static uint32_t t0;

static void putp(int x, int y, uint8_t r, uint8_t g, uint8_t b, uint8_t a) {
	if ((unsigned)x >= VW || (unsigned)y >= VH || a == 0) return;
	uint8_t *p = fb + (y * VW + x) * 4;
	if (a >= 255) {
		p[0] = r;
		p[1] = g;
		p[2] = b;
		p[3] = 255;
		return;
	}
	uint8_t ia = 255 - a;
	p[0] = (uint8_t)((r * a + p[0] * ia) / 255);
	p[1] = (uint8_t)((g * a + p[1] * ia) / 255);
	p[2] = (uint8_t)((b * a + p[2] * ia) / 255);
	p[3] = 255;
}

int SDL_Init(uint32_t f) {
	(void)f;
	t0 = 0;
	memset(kbd, 0, sizeof kbd);
	memset(fb, 18, sizeof fb);
	return 0;
}
void SDL_Quit(void) {}
int SDL_SetHint(const char *n, const char *v) {
	(void)n;
	(void)v;
	return 1;
}
void SDL_ShowCursor(int v) { (void)v; }
const char *SDL_GetError(void) { return ""; }
SDL_Window *SDL_CreateWindow(const char *t, int x, int y, int w, int h, uint32_t f) {
	(void)t;
	(void)x;
	(void)y;
	(void)w;
	(void)h;
	(void)f;
	return (SDL_Window *)1;
}
SDL_Renderer *SDL_CreateRenderer(SDL_Window *w, int i, uint32_t f) {
	(void)w;
	(void)i;
	(void)f;
	return (SDL_Renderer *)1;
}
int SDL_RenderSetLogicalSize(SDL_Renderer *r, int w, int h) {
	(void)r;
	(void)w;
	(void)h;
	return 0;
}
int SDL_RenderSetIntegerScale(SDL_Renderer *r, int v) {
	(void)r;
	(void)v;
	return 0;
}
SDL_Texture *SDL_CreateTexture(SDL_Renderer *r, uint32_t fmt, int acc, int w, int h) {
	(void)r;
	(void)fmt;
	(void)acc;
	SDL_Texture *t = (SDL_Texture *)calloc(1, sizeof *t);
	if (!t) return NULL;
	t->w = w;
	t->h = h;
	t->pix = (uint8_t *)calloc((size_t)w * h, 4);
	return t;
}
int SDL_UpdateTexture(SDL_Texture *t, const SDL_Rect *rect, const void *pix, int pitch) {
	(void)rect;
	if (!t || !t->pix) return -1;
	const uint8_t *s = (const uint8_t *)pix;
	for (int y = 0; y < t->h; y++) memcpy(t->pix + y * t->w * 4, s + y * pitch, (size_t)t->w * 4);
	return 0;
}
int SDL_SetTextureBlendMode(SDL_Texture *t, int m) {
	(void)t;
	(void)m;
	return 0;
}
int SDL_RenderCopy(SDL_Renderer *r, SDL_Texture *t, const SDL_Rect *src, const SDL_Rect *dst) {
	(void)r;
	(void)src;
	if (!t || !t->pix || !dst) return -1;
	int dw = dst->w, dh = dst->h;
	if (dw <= 0 || dh <= 0) return 0;
	for (int y = 0; y < dh; y++) {
		int sy = y * t->h / dh;
		for (int x = 0; x < dw; x++) {
			int sx = x * t->w / dw;
			uint8_t *p = t->pix + (sy * t->w + sx) * 4;
			putp(dst->x + x, dst->y + y, p[0], p[1], p[2], p[3]);
		}
	}
	return 0;
}
int SDL_SetRenderDrawColor(SDL_Renderer *r, uint8_t R, uint8_t G, uint8_t B, uint8_t A) {
	(void)r;
	draw_rgba[0] = R;
	draw_rgba[1] = G;
	draw_rgba[2] = B;
	draw_rgba[3] = A;
	return 0;
}
int SDL_SetRenderDrawBlendMode(SDL_Renderer *r, int m) {
	(void)r;
	(void)m;
	return 0;
}
int SDL_RenderClear(SDL_Renderer *r) {
	(void)r;
	for (int i = 0; i < VW * VH; i++) {
		fb[i * 4] = draw_rgba[0];
		fb[i * 4 + 1] = draw_rgba[1];
		fb[i * 4 + 2] = draw_rgba[2];
		fb[i * 4 + 3] = 255;
	}
	return 0;
}
int SDL_RenderFillRect(SDL_Renderer *r, const SDL_Rect *rc) {
	(void)r;
	if (!rc) return 0;
	for (int y = 0; y < rc->h; y++)
		for (int x = 0; x < rc->w; x++)
			putp(rc->x + x, rc->y + y, draw_rgba[0], draw_rgba[1], draw_rgba[2], draw_rgba[3]);
	return 0;
}
void SDL_RenderPresent(SDL_Renderer *r) { (void)r; }
int SDL_PollEvent(SDL_Event *e) {
	(void)e;
	return 0;
}
const uint8_t *SDL_GetKeyboardState(int *n) {
	if (n) *n = 512;
	return kbd;
}
uint32_t SDL_GetTicks(void) {
	return (uint32_t)(clock() * 1000 / CLOCKS_PER_SEC) + t0;
}
void SDL_Delay(uint32_t ms) { (void)ms; }
void SDL_DestroyTexture(SDL_Texture *t) {
	if (!t) return;
	free(t->pix);
	free(t);
}
void SDL_DestroyRenderer(SDL_Renderer *r) { (void)r; }
void SDL_DestroyWindow(SDL_Window *w) { (void)w; }

void SDLSOFT_Dump(const char *path) {
	FILE *f = fopen(path, "wb");
	if (!f) return;
	int row = VW * 3, pad = (4 - (row % 4)) & 3;
	int img = (row + pad) * VH;
	uint8_t hdr[54];
	memset(hdr, 0, 54);
	hdr[0] = 'B';
	hdr[1] = 'M';
	uint32_t sz = 54 + img;
	memcpy(hdr + 2, &sz, 4);
	hdr[10] = 54;
	hdr[14] = 40;
	int32_t w = VW, h = -VH;
	memcpy(hdr + 18, &w, 4);
	memcpy(hdr + 22, &h, 4);
	hdr[26] = 1;
	hdr[28] = 24;
	fwrite(hdr, 1, 54, f);
	uint8_t z[4] = {0};
	for (int y = 0; y < VH; y++) {
		for (int x = 0; x < VW; x++) {
			uint8_t *p = fb + (y * VW + x) * 4;
			uint8_t bgr[3] = {p[2], p[1], p[0]};
			fwrite(bgr, 1, 3, f);
		}
		if (pad) fwrite(z, 1, pad, f);
	}
	fclose(f);
}

/* Link-only SDL2 stub. Device loads real libSDL2-2.0.so.0 at runtime. */
typedef struct SDL_Window SDL_Window;
typedef struct SDL_Renderer SDL_Renderer;
typedef struct SDL_Texture SDL_Texture;
typedef struct { int x, y, w, h; } SDL_Rect;
typedef struct { unsigned type; unsigned char pad[56]; } SDL_Event;
int SDL_Init(unsigned x) { (void)x; return 0; }
void SDL_Quit(void) {}
SDL_Window *SDL_CreateWindow(const char *a, int b, int c, int d, int e, unsigned f) {
	(void)a;(void)b;(void)c;(void)d;(void)e;(void)f; return 0;
}
SDL_Renderer *SDL_CreateRenderer(SDL_Window *w, int i, unsigned f) { (void)w;(void)i;(void)f; return 0; }
int SDL_RenderSetLogicalSize(SDL_Renderer *r, int w, int h) { (void)r;(void)w;(void)h; return 0; }
int SDL_RenderSetIntegerScale(SDL_Renderer *r, int v) { (void)r;(void)v; return 0; }
SDL_Texture *SDL_CreateTexture(SDL_Renderer *r, unsigned f, int a, int w, int h) {
	(void)r;(void)f;(void)a;(void)w;(void)h; return 0;
}
int SDL_UpdateTexture(SDL_Texture *t, const SDL_Rect *r, const void *p, int n) {
	(void)t;(void)r;(void)p;(void)n; return 0;
}
int SDL_SetTextureBlendMode(SDL_Texture *t, int m) { (void)t;(void)m; return 0; }
int SDL_RenderCopy(SDL_Renderer *r, SDL_Texture *t, const SDL_Rect *s, const SDL_Rect *d) {
	(void)r;(void)t;(void)s;(void)d; return 0;
}
int SDL_SetRenderDrawColor(SDL_Renderer *r, unsigned char a, unsigned char b, unsigned char c, unsigned char d) {
	(void)r;(void)a;(void)b;(void)c;(void)d; return 0;
}
int SDL_SetRenderDrawBlendMode(SDL_Renderer *r, int m) { (void)r;(void)m; return 0; }
int SDL_RenderClear(SDL_Renderer *r) { (void)r; return 0; }
int SDL_RenderFillRect(SDL_Renderer *r, const SDL_Rect *rc) { (void)r;(void)rc; return 0; }
void SDL_RenderPresent(SDL_Renderer *r) { (void)r; }
int SDL_PollEvent(SDL_Event *e) { (void)e; return 0; }
const unsigned char *SDL_GetKeyboardState(int *n) { static unsigned char k[512]; if (n) *n = 512; return k; }
unsigned SDL_GetTicks(void) { return 0; }
void SDL_Delay(unsigned m) { (void)m; }
int SDL_SetHint(const char *n, const char *v) { (void)n;(void)v; return 1; }
void SDL_ShowCursor(int v) { (void)v; }
void SDL_DestroyTexture(SDL_Texture *t) { (void)t; }
void SDL_DestroyRenderer(SDL_Renderer *r) { (void)r; }
void SDL_DestroyWindow(SDL_Window *w) { (void)w; }
const char *SDL_GetError(void) { return ""; }

/* CryMon — native 640x480 SDL2 port for PortMaster / R36S (RK3326). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#include <time.h>
#include <unistd.h>
#include <libgen.h>
#include "font8.h"

typedef struct SDL_Window SDL_Window;
typedef struct SDL_Renderer SDL_Renderer;
typedef struct SDL_Texture SDL_Texture;
typedef struct { int x, y, w, h; } SDL_Rect;
typedef struct { uint32_t type; uint8_t pad[56]; } SDL_Event;

#define SDL_INIT_VIDEO 0x00000020u
#define SDL_INIT_EVENTS 0x00004000u
#define SDL_WINDOW_FULLSCREEN 0x00000001u
#define SDL_WINDOW_SHOWN 0x00000004u
#define SDL_RENDERER_ACCELERATED 0x00000002u
#define SDL_RENDERER_PRESENTVSYNC 0x00000004u
#define SDL_PIXELFORMAT_ABGR8888 376840196u
#define SDL_TEXTUREACCESS_STATIC 0
#define SDL_BLENDMODE_BLEND 1
#define SDL_WINDOWPOS_CENTERED 0x2FFF0000
#define SDL_QUIT 0x100
#define SDL_SCANCODE_A 4
#define SDL_SCANCODE_C 6
#define SDL_SCANCODE_D 7
#define SDL_SCANCODE_Q 20
#define SDL_SCANCODE_S 22
#define SDL_SCANCODE_W 26
#define SDL_SCANCODE_X 27
#define SDL_SCANCODE_Z 29
#define SDL_SCANCODE_1 30
#define SDL_SCANCODE_2 31
#define SDL_SCANCODE_3 32
#define SDL_SCANCODE_4 33
#define SDL_SCANCODE_5 34
#define SDL_SCANCODE_6 35
#define SDL_SCANCODE_RETURN 40
#define SDL_SCANCODE_ESCAPE 41
#define SDL_SCANCODE_TAB 43
#define SDL_SCANCODE_SPACE 44
#define SDL_SCANCODE_RIGHT 79
#define SDL_SCANCODE_LEFT 80
#define SDL_SCANCODE_DOWN 81
#define SDL_SCANCODE_UP 82

int SDL_Init(uint32_t);
void SDL_Quit(void);
SDL_Window *SDL_CreateWindow(const char *, int, int, int, int, uint32_t);
SDL_Renderer *SDL_CreateRenderer(SDL_Window *, int, uint32_t);
int SDL_RenderSetLogicalSize(SDL_Renderer *, int, int);
int SDL_RenderSetIntegerScale(SDL_Renderer *, int);
SDL_Texture *SDL_CreateTexture(SDL_Renderer *, uint32_t, int, int, int);
int SDL_UpdateTexture(SDL_Texture *, const SDL_Rect *, const void *, int);
int SDL_SetTextureBlendMode(SDL_Texture *, int);
int SDL_RenderCopy(SDL_Renderer *, SDL_Texture *, const SDL_Rect *, const SDL_Rect *);
int SDL_SetRenderDrawColor(SDL_Renderer *, uint8_t, uint8_t, uint8_t, uint8_t);
int SDL_SetRenderDrawBlendMode(SDL_Renderer *, int);
int SDL_RenderClear(SDL_Renderer *);
int SDL_RenderFillRect(SDL_Renderer *, const SDL_Rect *);
void SDL_RenderPresent(SDL_Renderer *);
int SDL_PollEvent(SDL_Event *);
const uint8_t *SDL_GetKeyboardState(int *);
uint32_t SDL_GetTicks(void);
void SDL_Delay(uint32_t);
int SDL_SetHint(const char *, const char *);
void SDL_ShowCursor(int);
void SDL_DestroyTexture(SDL_Texture *);
void SDL_DestroyRenderer(SDL_Renderer *);
void SDL_DestroyWindow(SDL_Window *);
const char *SDL_GetError(void);

#define VW 640
#define VH 480
#define TILE 32
#define PARTY_MAX 6
#define SPR_MAX 256

enum { M_TITLE, M_WORLD, M_BATTLE, M_TALK, M_BAG, M_PARTY, M_SHOP, M_END };
enum { DIR_DOWN, DIR_LEFT, DIR_RIGHT, DIR_UP };

static const char *DIRN[] = {"down", "left", "right", "up"};

typedef struct {
	char name[48];
	int w, h;
	SDL_Texture *tex;
} Spr;

typedef struct {
	char id[16], name[20], basic[20], special[20];
	int maxHp, str, agl, spc, spp, wild;
} Spec;

typedef struct {
	char id[16], name[20], species[16];
	int hp, maxHp, str, agl, spc, spp, sppm, lv, xp;
} Mon;

typedef struct {
	int x, y, dir, frame, beaten, chase, axis; /* 0 none 1 x 2 y */
	float fx, fy, minv, maxv, sign, anim;
	char id[12], name[16], spec[16];
	int lv;
} Sol;

static SDL_Window *win;
static SDL_Renderer *ren;
static Spr sprs[SPR_MAX];
static int nspr;
static const uint8_t *keys;
static uint8_t prev[512];
static int nkeys;

static int mode = M_TITLE;
static int mapId; /* 0 house 1 veld 2 forest 3 grove */
static float px, py;
static int pdir, pframe, moving;
static float panim, clockt;
static Mon party[PARTY_MAX];
static int nparty, lead;
static int bag_salve, bag_band, bag_root, bag_dust, bag_gem, marks;
static int talkedWren, beatCalder, caughtOnce, battles, anneGift, beatShin, cathCaught;
static int annePh; /* 0 off 1 approach 2 talk 3 leave */
static float ax, ay, aanim;
static int adir, aframe;
static Sol sols[3];
static int nsol;
static int doorLock;
static int lastTx = -1, lastTy = -1, encLock;

static char talk[8][96];
static char talkWho[8][16];
static int ntalk, talki, afterTalk; /* 0 none 1 anneLeave 2 cath 3 shini 4 calder 5 mason */
static char hud[96];
static float hudT;

/* battle */
static int bWild, bPhase; /* 0 msg 1 item 2 atk 3 guard 4 mg 5 win */
static Mon bPl, bFoe, bBench[2];
static int nbench;
static char bFoeName[20], bTrainer[16];
static char bMsg[3][80];
static int bMsgN, bMsgI, bAfter, bCur, bMenuN;
static char bMenu[8][40];
static int bDmg, mods_selfStr, mods_foeStr, mods_foeAgl, mods_foeSpc;
static float bT, mg;

static Spec SPEC[] = {
	{"quillpup", "Quillpup", "Nip", "Quillburst", 34, 15, 10, 7, 3, 0},
	{"glimmoth", "Glimmoth", "Dustwing", "Lampflare", 26, 7, 13, 16, 3, 1},
	{"tortcask", "Tortcask", "Shove", "Shellslam", 42, 13, 5, 8, 3, 1},
	{"razorbat", "Razorbat", "Rake", "Swoopcut", 30, 14, 16, 9, 3, 0},
	{"mossback", "Mossback", "Squelch", "Mossguard", 38, 12, 6, 11, 3, 1},
	{"briarfox", "Briarfox", "Bramble", "Thornrush", 28, 13, 17, 10, 3, 1},
	{"fenwisp", "Fenwisp", "Glim", "Fenflare", 24, 8, 16, 17, 3, 1},
	{"duskhorn", "Duskhorn", "Gore", "Duskram", 36, 16, 8, 7, 3, 1},
	{"needleroot", "Needleroot", "Prick", "Sapdrain", 32, 12, 7, 14, 3, 1},
	{"cathleen", "Cathleen", "Fire Bolt", "Mana Surge", 38, 11, 13, 19, 4, 1},
	{"crymare", "CryMare", "Wail", "Nightbridle", 30, 9, 14, 18, 3, 0},
};
static int NSPEC = 11;

static const char *HOUSE[] = {
	"HHHHHHHHHHHHHH",
	"HFFFFFFFFFFFFH",
	"HFFFFFFFFFFFFH",
	"HFFFFFFFFFFFFH",
	"HFBFFFFSFFFCFH",
	"HFFFFFFFFFFFFH",
	"HUFFFFFFFFFFFH",
	"HFFFFPFFFFFFFH",
	"HFFFFFFFFFFFFH",
	"HFFFFFFFFFFFFH",
	"HHHHHHDHHHHHHH",
	NULL};
static const char *VELD[] = {
	"##############################",
	"####..........RRRR..........##",
	"##.Q.^^.......HHHH......WWW.##",
	"##............HDH......WWA..##",
	"##..K.........===.......W....#",
	"##...TTT.....=====.....TTT..G#",
	"##...TTT....===,===....TTT...#",
	"##....M......=====....**.....#",
	"##.V.TTT......===......TTT...#",
	"##............===............#",
	"###....X...J.=====...........#",
	"##...TTT......===............#",
	"##............===.......L....#",
	"##...TTT.....=====......TTT..#",
	"##............===......^^....#",
	"##....TTT....=====......TTT..#",
	"##....TTT.....===......TTT...#",
	"##............===............#",
	"##...........=====.....NNNN..#",
	"##............===.......NE...#",
	"###...........===...........##",
	"#############=Z=##############",
	NULL};
static const char *FOREST[] = {
	"##########################",
	"####.........Y.........###",
	"###.........===.........##",
	"##...TTT....===....TTT..##",
	"##...TTT...=====...TTT..##",
	"##.1........===.......2.##",
	"##...TTT....===....TTT..##",
	"##..........=====.......##",
	"##...TTT....===....TTT..##",
	"##...........===........##",
	"##...TTT....=====..TTT..##",
	"##...........===........##",
	"##...TTT.....===...TTT..##",
	"##...........=====......##",
	"##....TTT....===...TTT..##",
	"##............===.......##",
	"##...TTT......===..TTT..##",
	"##............===....3..##",
	"###...........===......###",
	"#############=O=##########",
	NULL};
static const char *GROVE[] = {
	"##########################",
	"####.........O.........###",
	"###.........===.........##",
	"##..........===.........##",
	"##.........=====........##",
	"##..........===.........##",
	"##.........=====........##",
	"##..........===.........##",
	"##.........=====........##",
	"##..........===.........##",
	"##........=======.......##",
	"##........===8===.......##",
	"##........=======.......##",
	"##.........=====........##",
	"##..........===.........##",
	"##.........=====........##",
	"##..........===.........##",
	"##...........9..........##",
	"###....................###",
	"##########################",
	NULL};

static const char **maps[4] = {HOUSE, VELD, FOREST, GROVE};
static int mw[4], mh[4];

static int irand(int a, int b) { return a + rand() % (b - a + 1); }
static int clampi(int v, int a, int b) { return v < a ? a : v > b ? b : v; }
static float clampf(float v, float a, float b) { return v < a ? a : v > b ? b : v; }

static int down(int sc) { return nkeys > sc && keys[sc]; }
static int pressed(int sc) { return down(sc) && !prev[sc]; }
static int confirm(void) { return pressed(SDL_SCANCODE_Z) || pressed(SDL_SCANCODE_SPACE) || pressed(SDL_SCANCODE_RETURN); }
static int cancel(void) { return pressed(SDL_SCANCODE_X) || pressed(SDL_SCANCODE_C) || pressed(SDL_SCANCODE_ESCAPE); }
static int startp(void) { return pressed(SDL_SCANCODE_RETURN); }
static int selectp(void) { return pressed(SDL_SCANCODE_TAB) || pressed(SDL_SCANCODE_Q); }

static Spec *spec_of(const char *id) {
	for (int i = 0; i < NSPEC; i++) if (!strcmp(SPEC[i].id, id)) return &SPEC[i];
	return &SPEC[0];
}

static Mon mint(const char *id, int lv) {
	Spec *s = spec_of(id);
	float g = 1.f + (lv - 3) * 0.12f;
	Mon m;
	memset(&m, 0, sizeof m);
	snprintf(m.id, sizeof m.id, "%s", id);
	snprintf(m.name, sizeof m.name, "%s", s->name);
	snprintf(m.species, sizeof m.species, "%s", id);
	m.maxHp = (int)(s->maxHp * g + 0.5f);
	m.hp = m.maxHp;
	m.str = (int)(s->str * g + 0.5f);
	m.agl = (int)(s->agl * g + 0.5f);
	m.spc = (int)(s->spc * g + 0.5f);
	m.spp = s->spp;
	m.sppm = s->spp;
	m.lv = lv;
	return m;
}

static void grant(Mon *m, int flv) {
	m->xp += 6 + flv * 4;
	while (m->xp >= m->lv * 10 && m->lv < 12) {
		m->xp -= m->lv * 10;
		m->lv++;
		m->maxHp += 3;
		m->hp = m->hp + 3 > m->maxHp ? m->maxHp : m->hp + 3;
		m->str++;
		m->agl++;
		m->spc++;
	}
}

static const char **curmap(void) { return maps[mapId]; }
static int mapw(void) { return mw[mapId]; }
static int maph(void) { return mh[mapId]; }

static char tile(int tx, int ty) {
	const char **m = curmap();
	if (ty < 0 || ty >= maph() || tx < 0 || tx >= mapw()) return '#';
	return m[ty][tx];
}
static char tileAt(float x, float y) { return tile((int)(x / TILE), (int)(y / TILE)); }
static int solid(char c) { return strchr("#HWRBC^NKEVAQXUJ", c) != NULL; }

static int spawn(const char **m, char mark, float *ox, float *oy) {
	for (int y = 0; m[y]; y++) {
		const char *p = strchr(m[y], mark);
		if (p) {
			*ox = (p - m[y]) * TILE + TILE / 2.f;
			*oy = y * TILE + TILE / 2.f;
			return 1;
		}
	}
	*ox = TILE * 2;
	*oy = TILE * 2;
	return 0;
}

static Spr *findspr(const char *n) {
	for (int i = 0; i < nspr; i++) if (!strcmp(sprs[i].name, n)) return &sprs[i];
	return NULL;
}

static void blit(const char *n, int x, int y, int dw, int dh) {
	Spr *s = findspr(n);
	if (!s || !s->tex) return;
	SDL_Rect d = {x, y, dw, dh};
	SDL_RenderCopy(ren, s->tex, NULL, &d);
}
static void blit_px(const char *n, int x, int y, int boxw, int boxh, int top) {
	Spr *s = findspr(n);
	if (!s || !s->tex) return;
	float fit = fminf((float)boxw / s->w, (float)boxh / s->h);
	int sc = (int)(fit + 0.45f);
	if (sc < 1) sc = 1;
	if (sc < 2 && s->h * 2 <= boxh + 24) sc = 2;
	int dw = s->w * sc, dh = s->h * sc;
	int dx = x + (boxw - dw) / 2;
	int dy = top ? y : y + boxh - dh;
	SDL_Rect d = {dx, dy, dw, dh};
	SDL_RenderCopy(ren, s->tex, NULL, &d);
}
static void fill(int r, int g, int b, int a, int x, int y, int w, int h) {
	SDL_SetRenderDrawColor(ren, (uint8_t)r, (uint8_t)g, (uint8_t)b, (uint8_t)a);
	SDL_Rect rc = {x, y, w, h};
	SDL_RenderFillRect(ren, &rc);
}
static void box(int x, int y, int w, int h) {
	fill(18, 17, 14, 255, x, y, w, h);
	fill(197, 206, 198, 255, x, y, w, 2);
	fill(197, 206, 198, 255, x, y + h - 2, w, 2);
	fill(197, 206, 198, 255, x, y, 2, h);
	fill(197, 206, 198, 255, x + w - 2, y, 2, h);
}
static void glyph(int x, int y, char c, int r, int g, int b, int sc) {
	unsigned char uc = (unsigned char)c;
	if (uc > 127) uc = '?';
	const unsigned char *row = FONT8[uc];
	for (int j = 0; j < 8; j++) {
		unsigned char bits = row[j];
		for (int i = 0; i < 8; i++) if (bits & (1 << (7 - i)))
			fill(r, g, b, 255, x + i * sc, y + j * sc, sc, sc);
	}
}
static void text(const char *s, int x, int y, int r, int g, int b, int sc) {
	for (int i = 0; s[i]; i++) glyph(x + i * 8 * sc, y, s[i], r, g, b, sc);
}

static int load_gfx(const char *path) {
	FILE *f = fopen(path, "rb");
	if (!f) return 0;
	char mag[4];
	if (fread(mag, 1, 4, f) != 4 || memcmp(mag, "CMGX", 4)) { fclose(f); return 0; }
	uint32_t n = 0;
	fread(&n, 4, 1, f);
	for (uint32_t i = 0; i < n && nspr < SPR_MAX; i++) {
		uint16_t ln = 0, w = 0, h = 0;
		uint32_t nb = 0;
		fread(&ln, 2, 1, f);
		char name[48];
		memset(name, 0, sizeof name);
		if (ln >= sizeof name) ln = sizeof name - 1;
		fread(name, 1, ln, f);
		fread(&w, 2, 1, f);
		fread(&h, 2, 1, f);
		fread(&nb, 4, 1, f);
		uint8_t *pix = (uint8_t *)malloc(nb);
		if (!pix) { fclose(f); return 0; }
		fread(pix, 1, nb, f);
		SDL_Texture *t = SDL_CreateTexture(ren, SDL_PIXELFORMAT_ABGR8888, SDL_TEXTUREACCESS_STATIC, w, h);
		if (t) {
			SDL_SetTextureBlendMode(t, SDL_BLENDMODE_BLEND);
			SDL_UpdateTexture(t, NULL, pix, w * 4);
			snprintf(sprs[nspr].name, sizeof sprs[nspr].name, "%s", name);
			sprs[nspr].w = w;
			sprs[nspr].h = h;
			sprs[nspr].tex = t;
			nspr++;
		}
		free(pix);
	}
	fclose(f);
	return nspr > 0;
}

static void say1(const char *who, const char *t) {
	ntalk = 1;
	talki = 0;
	snprintf(talkWho[0], sizeof talkWho[0], "%s", who);
	snprintf(talk[0], sizeof talk[0], "%s", t);
	mode = M_TALK;
	afterTalk = 0;
}
static void sayn(int n, const char **who, const char **t, int after) {
	ntalk = n;
	talki = 0;
	afterTalk = after;
	for (int i = 0; i < n; i++) {
		snprintf(talkWho[i], sizeof talkWho[i], "%s", who[i]);
		snprintf(talk[i], sizeof talk[i], "%s", t[i]);
	}
	mode = M_TALK;
}
static void note(const char *s) { snprintf(hud, sizeof hud, "%s", s); hudT = 8; }

static Mon *leader(void) {
	if (lead >= 0 && lead < nparty && party[lead].hp > 0) return &party[lead];
	for (int i = 0; i < nparty; i++) if (party[i].hp > 0) { lead = i; return &party[i]; }
	return &party[0];
}

static void start_battle(Mon foe, int wild, const char *title, const char *trainer) {
	bPl = *leader();
	bFoe = foe;
	bWild = wild;
	snprintf(bTrainer, sizeof bTrainer, "%s", trainer);
	snprintf(bFoeName, sizeof bFoeName, "%s", wild ? foe.name : trainer);
	bPhase = 0;
	snprintf(bMsg[0], sizeof bMsg[0], "%s!", title);
	bMsgN = 1;
	bMsgI = 0;
	bAfter = 1;
	bT = 0;
	mods_selfStr = mods_foeStr = mods_foeAgl = mods_foeSpc = 0;
	mode = M_BATTLE;
	nbench = 0;
}

static void paint_tile(char ch, int dx, int dy) {
	int t = TILE;
	if (ch == 'H') { fill(42, 30, 22, 255, dx, dy, t, t); return; }
	if (ch == 'R') { fill(106, 64, 48, 255, dx, dy, t, t); return; }
	if (ch == 'F' || ch == 'P') { fill(106, 82, 56, 255, dx, dy, t, t); return; }
	if (ch == 'D') { fill(26, 18, 12, 255, dx, dy, t, t); return; }
	if (ch == 'B' || ch == 'U' || ch == 'C' || ch == 'S') { fill(106, 82, 56, 255, dx, dy, t, t); return; }
	if (ch == '.') { fill(61, 90, 56, 255, dx, dy, t, t); fill(90, 122, 82, 255, dx + 4, dy + 6, 2, 2); return; }
	if (ch == 'T') { fill(47, 74, 44, 255, dx, dy, t, t); fill(106, 138, 58, 255, dx + 6, dy + 4, 4, 24); fill(90, 122, 82, 255, dx + 16, dy + 2, 4, 26); return; }
	if (ch == '=' || ch == ',' || ch == 'Z' || ch == 'Y' || ch == '3' || ch == 'O' || ch == '8' || ch == '9') {
		fill(ch == ',' ? 90 : 107, ch == ',' ? 74 : 90, 58, 255, dx, dy, t, t);
		return;
	}
	if (ch == '#') { fill(28, 36, 24, 255, dx, dy, t, t); fill(61, 90, 56, 255, dx + 4, dy + 2, 24, 18); return; }
	if (ch == 'W') { fill(42, 58, 68, 255, dx, dy, t, t); return; }
	if (ch == '^') { fill(74, 64, 48, 255, dx, dy, t, t); return; }
	if (ch == 'N' || ch == 'E') { fill(90, 70, 48, 255, dx, dy, t, t); return; }
	if (ch == '*') { fill(61, 90, 56, 255, dx, dy, t, t); fill(180, 60, 80, 255, dx + 12, dy + 12, 6, 6); return; }
	fill(61, 90, 56, 255, dx, dy, t, t);
}

static void cam(int *cx, int *cy) {
	int W = mapw() * TILE, H = maph() * TILE;
	*cx = (int)(px - VW / 2);
	*cy = (int)(py - VH / 2);
	if (*cx < 0) *cx = 0;
	if (*cy < 0) *cy = 0;
	if (*cx > W - VW) *cx = W - VW > 0 ? W - VW : 0;
	if (*cy > H - VH) *cy = H - VH > 0 ? H - VH : 0;
}

static int blocked(float x, float y) {
	int r = 10;
	float pts[4][2] = {{x - r, y}, {x + r, y}, {x, y - 2}, {x, y + r}};
	for (int i = 0; i < 4; i++) if (solid(tileAt(pts[i][0], pts[i][1]))) return 1;
	return 0;
}

static void ensure_soldiers(void) {
	if (nsol) return;
	float x, y;
	spawn(FOREST, '1', &x, &y);
	sols[0] = (Sol){.fx = x, .fy = y, .dir = DIR_RIGHT, .axis = 1, .minv = x - 16, .maxv = x + 144, .sign = 1, .lv = 4};
	snprintf(sols[0].id, 12, "patrol");
	snprintf(sols[0].name, 16, "Patrol");
	snprintf(sols[0].spec, 16, "briarfox");
	spawn(FOREST, '2', &x, &y);
	sols[1] = (Sol){.fx = x, .fy = y, .dir = DIR_LEFT, .axis = 2, .minv = y - 80, .maxv = y + 80, .sign = -1, .lv = 4};
	snprintf(sols[1].id, 12, "scout");
	snprintf(sols[1].name, 16, "Scout");
	snprintf(sols[1].spec, 16, "mossback");
	spawn(FOREST, '3', &x, &y);
	sols[2] = (Sol){.fx = x, .fy = y, .dir = DIR_UP, .axis = 0, .lv = 5};
	snprintf(sols[2].id, 12, "sentry");
	snprintf(sols[2].name, 16, "Sentry");
	snprintf(sols[2].spec, 16, "razorbat");
	nsol = 3;
}

static int soldier_los(Sol *s) {
	if (s->beaten || s->chase) return 0;
	int stx = (int)(s->fx / TILE), sty = (int)(s->fy / TILE);
	int ptx = (int)(px / TILE), pty = (int)(py / TILE);
	int dx = s->dir == DIR_LEFT ? -1 : s->dir == DIR_RIGHT ? 1 : 0;
	int dy = s->dir == DIR_UP ? -1 : s->dir == DIR_DOWN ? 1 : 0;
	if (!dx && !dy) return 0;
	int max = mapw() > maph() ? mapw() : maph();
	for (int i = 1; i <= max; i++) {
		int tx = stx + dx * i, ty = sty + dy * i;
		char ch = tile(tx, ty);
		if (solid(ch)) return 0;
		if (tx == ptx && ty == pty) return 1;
	}
	return 0;
}

static void draw_actor(const char *key, float wx, float wy, int cx, int cy) {
	blit(key, (int)wx - cx - 24, (int)wy - cy - 48, 48, 52);
}

static void draw_map(int cx, int cy) {
	if (mapId == 0) fill(26, 20, 16, 255, 0, 0, VW, VH);
	else if (mapId == 2) fill(18, 24, 16, 255, 0, 0, VW, VH);
	else if (mapId == 3) fill(22, 18, 24, 255, 0, 0, VW, VH);
	else fill(28, 36, 24, 255, 0, 0, VW, VH);
	int x0 = cx / TILE - 1, y0 = cy / TILE - 1;
	int x1 = (cx + VW) / TILE + 2, y1 = (cy + VH) / TILE + 2;
	if (x0 < 0) x0 = 0;
	if (y0 < 0) y0 = 0;
	if (x1 > mapw()) x1 = mapw();
	if (y1 > maph()) y1 = maph();
	for (int y = y0; y < y1; y++)
		for (int x = x0; x < x1; x++)
			paint_tile(tile(x, y), x * TILE - cx, y * TILE - cy);
}

static void reset_run(void) {
	mapId = 0;
	float sx, sy;
	spawn(HOUSE, 'P', &sx, &sy);
	px = sx;
	py = sy;
	pdir = DIR_DOWN;
	nparty = 1;
	party[0] = mint("quillpup", 3);
	lead = 0;
	bag_salve = 2;
	bag_band = 2;
	bag_root = 1;
	bag_dust = 1;
	bag_gem = 0;
	marks = 16;
	talkedWren = beatCalder = caughtOnce = battles = anneGift = beatShin = cathCaught = 0;
	annePh = 0;
	nsol = 0;
	mode = M_WORLD;
	encLock = 8;
}

static void warp(int to, char mark, int fromSouth) {
	mapId = to;
	float sx, sy;
	spawn(curmap(), mark, &sx, &sy);
	px = sx;
	py = fromSouth ? sy + TILE + 8 : sy - TILE;
	pdir = fromSouth ? DIR_DOWN : DIR_UP;
	doorLock = 20;
	encLock = 3;
	lastTx = lastTy = -1;
}

static void begin_talk_end(void) {
	mode = M_WORLD;
	if (afterTalk == 1) {
		annePh = 3;
		adir = DIR_DOWN;
	} else if (afterTalk == 2 && !cathCaught) {
		start_battle(mint("cathleen", 6), 1, "Cathleen stands against you", "Cathleen");
	} else if (afterTalk == 3 && !beatShin) {
		start_battle(mint("crymare", 5), 0, "Shinigami sends CryMare", "Shinigami");
		bBench[0] = mint("crymare", 6);
		bBench[1] = mint("crymare", 7);
		nbench = 2;
	} else if (afterTalk == 4) {
		start_battle(mint("razorbat", 4), 0, "Calder sends Razorbat", "Calder");
	}
	afterTalk = 0;
}

static void interact(void) {
	if (mapId == 0) {
		float hx, hy;
		spawn(HOUSE, 'B', &hx, &hy);
		if ((hx - px) * (hx - px) + (hy - py) * (hy - py) < 2704) { say1("Max", "I'll bring the medicine. Sleep."); return; }
		spawn(HOUSE, 'U', &hx, &hy);
		if ((hx - px) * (hx - px) + (hy - py) * (hy - py) < 2704) {
			for (int i = 0; i < nparty; i++) { party[i].hp = party[i].maxHp; party[i].spp = party[i].sppm; }
			say1("Max", "Cuts close. Specials return.");
			return;
		}
		spawn(HOUSE, 'S', &hx, &hy);
		if ((hx - px) * (hx - px) + (hy - py) * (hy - py) < 2704) { say1("Max", "Gone. Father sold the last crystals."); return; }
		return;
	}
	if (mapId == 2) {
		ensure_soldiers();
		for (int i = 0; i < nsol; i++) {
			float dx = sols[i].fx - px, dy = sols[i].fy - py;
			if (dx * dx + dy * dy > 1600) continue;
			if (sols[i].beaten) { say1("", "They already lost."); return; }
			start_battle(mint(sols[i].spec, sols[i].lv), 0, "A soldier sends a CryMon", sols[i].name);
			snprintf(bTrainer, sizeof bTrainer, "soldier:%s", sols[i].id);
			return;
		}
		return;
	}
	if (mapId == 3) {
		float cx, cy;
		spawn(GROVE, '8', &cx, &cy);
		float d8 = (cx - px) * (cx - px) + (cy - py) * (cy - py);
		spawn(GROVE, '9', &cx, &cy);
		float d9 = (cx - px) * (cx - px) + (cy - py) * (cy - py);
		if (d9 < 2704 && (cathCaught || d9 <= d8 || d8 > 2704)) {
			if (beatShin) say1("Shinigami", "The graves are quiet. Go.");
			else {
				const char *w[] = {"Shinigami", "Max", "Shinigami"};
				const char *t[] = {"Three names. Three graves. I keep them.", "You're in the way.", "CryMare. Come."};
				sayn(3, w, t, 3);
			}
			return;
		}
		if (!cathCaught && d8 < 2704) {
			const char *w[] = {"Cathleen", "Max", "Cathleen"};
			const char *t[] = {"You walked the path. I am the path's answer.", "You're a CryMon.", "I am Cathleen. I fight as myself."};
			sayn(3, w, t, 2);
			return;
		}
		return;
	}
	if (mapId == 1) {
		float nx, ny;
		spawn(VELD, 'K', &nx, &ny);
		if ((nx - px) * (nx - px) + (ny - py) * (ny - py) < 2704) {
			if (!talkedWren) { talkedWren = 1; bag_salve++; say1("Wren", "Too young. Take the salve. Calder camps south."); }
			else { for (int i = 0; i < nparty; i++) { party[i].hp = party[i].maxHp; party[i].spp = party[i].sppm; } say1("Wren", "Cuts bound. Specials return."); }
			return;
		}
		spawn(VELD, 'J', &nx, &ny);
		if ((nx - px) * (nx - px) + (ny - py) * (ny - py) < 2704) { mode = M_SHOP; return; }
		spawn(VELD, 'E', &nx, &ny);
		if (!beatCalder && (nx - px) * (nx - px) + (ny - py) * (ny - py) < 2704) {
			const char *w[] = {"Calder", "Max"};
			const char *t[] = {"The camp takes strays.", "I'm not stray."};
			sayn(2, w, t, 4);
			return;
		}
		spawn(VELD, 'G', &nx, &ny);
		if ((nx - px) * (nx - px) + (ny - py) * (ny - py) < 2704) { bag_gem++; say1("Max", "A Capture Crystal."); return; }
	}
}

static void try_encounter(void) {
	int tx = (int)(px / TILE), ty = (int)(py / TILE);
	if (tx == lastTx && ty == lastTy) return;
	lastTx = tx;
	lastTy = ty;
	if (tileAt(px, py) != 'T') return;
	if (encLock > 0) { encLock--; return; }
	if (irand(0, 99) > 18) return;
	encLock = 3;
	const char *id = "glimmoth";
	int lv = 2 + irand(0, 1);
	if (mapId == 2) {
		const char *pool[3] = {"fenwisp", "duskhorn", "needleroot"};
		id = pool[irand(0, 2)];
		lv = 3 + irand(0, 2);
	} else if (tx > 18) id = "tortcask";
	char title[48];
	snprintf(title, sizeof title, "A wild %s", spec_of(id)->name);
	start_battle(mint(id, lv), 1, title, "wild");
}

static void maybe_anne(void) {
	if (anneGift || annePh) return;
	if (battles < 1 || mapId != 1) return;
	annePh = 1;
	ax = px;
	ay = py + 72;
	adir = DIR_UP;
}

static void draw_world(void) {
	int cx, cy;
	cam(&cx, &cy);
	draw_map(cx, cy);
	int wf = ((int)(clockt * 4) % 4) + 1;
	char key[48];
	if (mapId == 0) {
		float hx, hy;
		spawn(HOUSE, 'B', &hx, &hy);
		blit("props/bed-father", (int)hx - cx - 32, (int)hy - cy - 44, 64, 56);
		spawn(HOUSE, 'U', &hx, &hy);
		blit("props/bed-empty", (int)hx - cx - 32, (int)hy - cy - 44, 64, 56);
	}
	if (mapId == 1) {
		float nx, ny;
		spawn(VELD, 'K', &nx, &ny);
		snprintf(key, sizeof key, "npc/wren-%d", wf);
		draw_actor(key, nx, ny, cx, cy);
		spawn(VELD, 'J', &nx, &ny);
		snprintf(key, sizeof key, "npc/bram-%d", wf);
		draw_actor(key, nx, ny, cx, cy);
		if (!beatCalder) {
			spawn(VELD, 'E', &nx, &ny);
			snprintf(key, sizeof key, "npc/calder-%d", wf);
			draw_actor(key, nx, ny, cx, cy);
		}
		if (annePh) {
			snprintf(key, sizeof key, "anne/%s-%d", DIRN[adir], (annePh == 1 || annePh == 3) ? aframe + 1 : 1);
			draw_actor(key, ax, ay, cx, cy);
		}
	}
	if (mapId == 2) {
		ensure_soldiers();
		for (int i = 0; i < nsol; i++) {
			snprintf(key, sizeof key, "npc/soldier/%s-%d", DIRN[sols[i].dir], sols[i].beaten ? 1 : sols[i].frame + 1);
			draw_actor(key, sols[i].fx, sols[i].fy, cx, cy);
		}
	}
	if (mapId == 3) {
		float nx, ny;
		if (!cathCaught) {
			spawn(GROVE, '8', &nx, &ny);
			blit("npc/cathleen", (int)nx - cx - 36, (int)ny - cy - 68, 72, 72);
		}
		spawn(GROVE, '9', &nx, &ny);
		snprintf(key, sizeof key, "shinigami/down-%d", wf);
		draw_actor(key, nx, ny, cx, cy);
	}
	int fr = moving ? pframe + 1 : 1;
	snprintf(key, sizeof key, "max/%s-%d", DIRN[pdir], fr);
	draw_actor(key, px, py, cx, cy);
	/* hud */
	box(8, 8, 300, 36);
	text("MAX", 16, 14, 232, 228, 216, 1);
	Mon *L = leader();
	char line[64];
	snprintf(line, sizeof line, "%s  %d/%d", L->name, L->hp, L->maxHp);
	text(line, 70, 14, 197, 206, 198, 1);
	if (hudT > 0) {
		box(16, 360, 608, 100);
		text(hud, 28, 376, 232, 228, 216, 1);
	}
}

static void draw_talk(void) {
	draw_world();
	const char *who = talkWho[talki];
	if (who[0] && strcmp(who, "none")) {
		char low[16];
		snprintf(low, sizeof low, "%s", who);
		for (int i = 0; low[i]; i++) if (low[i] >= 'A' && low[i] <= 'Z') low[i] += 32;
		char pk[48];
		snprintf(pk, sizeof pk, "portraits/%s", low);
		blit_px(pk, -8, 16, 320, 450, 1);
		fill(18, 17, 14, 140, 288, 0, VW - 288, VH);
		box(300, 16, 324, 180);
		text(who, 316, 28, 197, 206, 198, 1);
		text(talk[talki], 316, 56, 232, 228, 216, 1);
	} else {
		box(16, 360, 608, 100);
		text(talk[talki], 28, 376, 232, 228, 216, 1);
	}
}

static void draw_battle(void) {
	if (findspr("battle-bg")) blit("battle-bg", 0, 0, VW, VH);
	else fill(42, 36, 24, 255, 0, 0, VW, VH);
	int pf = ((int)(bT * 4) % 4) + 1;
	char k[48];
	snprintf(k, sizeof k, "monsters/%s/%d", bFoe.species, pf);
	blit(k, 430, 20, 160, 160);
	snprintf(k, sizeof k, "monsters/%s/%d", bPl.species, pf);
	blit(k, 30, 140, 140, 140);
	box(16, 16, 300, 70);
	text(bFoe.name, 28, 24, 232, 228, 216, 1);
	fill(42, 38, 32, 255, 28, 48, 220, 14);
	fill(90, 122, 82, 255, 28, 48, bFoe.maxHp ? 220 * bFoe.hp / bFoe.maxHp : 0, 14);
	box(280, 230, 340, 70);
	char ln[64];
	snprintf(ln, sizeof ln, "%s Lv%d", bPl.name, bPl.lv);
	text(ln, 292, 238, 232, 228, 216, 1);
	fill(42, 38, 32, 255, 292, 262, 220, 14);
	fill(90, 122, 82, 255, 292, 262, bPl.maxHp ? 220 * bPl.hp / bPl.maxHp : 0, 14);
	box(16, 330, 608, 140);
	if (bPhase == 0) {
		text(bMsg[bMsgI], 32, 350, 232, 228, 216, 1);
		return;
	}
	if (bPhase == 4) {
		text("SPECIAL  hit the mark", 32, 350, 197, 206, 198, 1);
		fill(42, 38, 32, 255, 40, 390, 560, 24);
		fill(90, 122, 82, 255, 250, 390, 140, 24);
		fill(232, 228, 216, 255, 40 + (int)(mg / 100.f * 560), 380, 8, 44);
		return;
	}
	const char *ttl = bPhase == 1 ? "ITEMS" : bPhase == 2 ? "ATTACK" : "GUARD";
	text(ttl, 32, 344, 138, 134, 120, 1);
	for (int i = 0; i < bMenuN && i < 4; i++) {
		int on = i == bCur;
		char row[48];
		snprintf(row, sizeof row, "%s %s", on ? ">" : " ", bMenu[i]);
		text(row, 180, 344 + i * 28, on ? 232 : 138, on ? 228 : 134, on ? 216 : 120, 1);
	}
}

static void draw_title(void) {
	mapId = 1;
	int cx = 8 * TILE, cy = 0;
	draw_map(cx, cy);
	fill(18, 17, 14, 70, 0, 0, VW, VH);
	blit("max/down-1", 90, 260, 48, 52);
	blit("monsters/quillpup/1", 430, 180, 160, 160);
	box(160, 100, 320, 110);
	text("CRYMON", 250, 118, 232, 228, 216, 2);
	text("MAX'S RUN", 250, 165, 197, 206, 198, 1);
	box(180, 390, 280, 50);
	text("Z / A  begin", 230, 404, 90, 122, 82, 1);
}

static void fill_item_menu(void) {
	bMenuN = 0;
	snprintf(bMenu[bMenuN++], 40, "Pass");
	if (bag_salve) snprintf(bMenu[bMenuN++], 40, "Moss salve x%d", bag_salve);
	if (bag_band) snprintf(bMenu[bMenuN++], 40, "Linen wrap x%d", bag_band);
	if (bag_root) snprintf(bMenu[bMenuN++], 40, "Bitterroot x%d", bag_root);
	if (bag_dust) snprintf(bMenu[bMenuN++], 40, "Ash dust x%d", bag_dust);
	if (bag_gem) snprintf(bMenu[bMenuN++], 40, "Capture Crystal x%d", bag_gem);
	bCur = 0;
}
static void fill_atk_menu(void) {
	Spec *s = spec_of(bPl.species);
	bMenuN = 0;
	if (!strcmp(bPl.species, "cathleen")) {
		snprintf(bMenu[bMenuN++], 40, "Fire Bolt");
		snprintf(bMenu[bMenuN++], 40, "Ice Beam");
		snprintf(bMenu[bMenuN++], 40, "Lightning Strike");
		snprintf(bMenu[bMenuN++], 40, "Mana Surge  %d/%d", bPl.spp, bPl.sppm);
	} else {
		snprintf(bMenu[bMenuN++], 40, "%s", s->basic);
		snprintf(bMenu[bMenuN++], 40, "%s  %d/%d", s->special, bPl.spp, bPl.sppm);
		snprintf(bMenu[bMenuN++], 40, "Wait");
	}
	bCur = 0;
}

static void finish_win(void) {
	party[lead] = bPl;
	grant(&party[lead], bFoe.lv);
	battles++;
	maybe_anne();
	if (!bWild && !strcmp(bTrainer, "Calder")) {
		beatCalder = 1;
		marks += 18;
		mode = M_END;
		return;
	}
	if (!strncmp(bTrainer, "soldier:", 8)) {
		for (int i = 0; i < nsol; i++) if (!strcmp(sols[i].id, bTrainer + 8)) sols[i].beaten = 1;
		marks += 8;
		mode = M_WORLD;
		note("The soldier sits.");
		return;
	}
	if (!strcmp(bTrainer, "Shinigami")) {
		beatShin = 1;
		marks += 14;
		mode = M_WORLD;
		say1("Shinigami", "The mares return to fog. You may pass.");
		return;
	}
	marks += 3;
	mode = M_WORLD;
	if (!strcmp(bFoe.species, "cathleen") && !cathCaught) say1("Cathleen", "You stand. Come again if you mean to keep me.");
	else note("The grass goes still.");
	encLock = 3;
}

static void apply_hit(void) {
	bFoe.hp -= bDmg;
	if (bFoe.hp < 0) bFoe.hp = 0;
	if (bFoe.hp <= 0) {
		if (nbench > 0) {
			grant(&bPl, bFoe.lv);
			bFoe = bBench[0];
			if (nbench == 2) bBench[0] = bBench[1];
			nbench--;
			mods_foeStr = mods_foeAgl = mods_foeSpc = 0;
			snprintf(bMsg[0], 80, "It falls.");
			snprintf(bMsg[1], 80, "%s sends %s.", bFoeName, bFoe.name);
			bMsgN = 2;
			bMsgI = 0;
			bPhase = 0;
			bAfter = 1;
			return;
		}
		snprintf(bMsg[0], 80, "%s  %d dmg.", spec_of(bPl.species)->basic, bDmg);
		snprintf(bMsg[1], 80, "%s falls.", bFoe.name);
		bMsgN = 2;
		bMsgI = 0;
		bPhase = 0;
		bAfter = 5;
		return;
	}
	snprintf(bMsg[0], 80, "Hit  %d dmg.", bDmg);
	snprintf(bMsg[1], 80, "Choose a guard.");
	bMsgN = 2;
	bMsgI = 0;
	bPhase = 0;
	bAfter = 3;
}

static void pick_item(void) {
	const char *row = bMenu[bCur];
	if (!strncmp(row, "Pass", 4)) {
		bPhase = 2;
		fill_atk_menu();
		return;
	}
	if (!strncmp(row, "Moss", 4) && bag_salve) {
		bag_salve--;
		int n = 22;
		if (bPl.hp + n > bPl.maxHp) n = bPl.maxHp - bPl.hp;
		bPl.hp += n;
		snprintf(bMsg[0], 80, "Moss salve. %d HP.", n);
	} else if (!strncmp(row, "Linen", 5) && bag_band) {
		bag_band--;
		int n = 12;
		if (bPl.hp + n > bPl.maxHp) n = bPl.maxHp - bPl.hp;
		bPl.hp += n;
		snprintf(bMsg[0], 80, "Linen wrap. %d HP.", n);
	} else if (!strncmp(row, "Bitter", 6) && bag_root) {
		bag_root--;
		mods_selfStr += 4;
		snprintf(bMsg[0], 80, "Bitterroot. STR +4.");
	} else if (!strncmp(row, "Ash", 3) && bag_dust) {
		bag_dust--;
		mods_foeStr -= 3;
		mods_foeAgl -= 2;
		mods_foeSpc -= 2;
		snprintf(bMsg[0], 80, "Ash dust. Foe stats drop.");
	} else if (!strncmp(row, "Capture", 7) && bag_gem) {
		bag_gem--;
		if (!bWild) {
			bag_gem++;
			snprintf(bMsg[0], 80, "Crystals will not take a tamer's CryMon.");
		} else if (nparty >= PARTY_MAX) {
			bag_gem++;
			snprintf(bMsg[0], 80, "Six is all Max can hold.");
		} else {
			int chance = 48 + (int)((1.f - (float)bFoe.hp / bFoe.maxHp) * 42);
			if (irand(1, 100) <= chance) {
				Mon c = bFoe;
				c.hp = c.maxHp * 2 / 5;
				if (c.hp < 1) c.hp = 1;
				party[nparty++] = c;
				caughtOnce = 1;
				if (!strcmp(c.species, "cathleen")) cathCaught = 1;
				snprintf(bMsg[0], 80, "The crystal takes. %s is yours.", c.name);
				bMsgN = 1;
				bMsgI = 0;
				bPhase = 0;
				bAfter = 6;
				return;
			}
			snprintf(bMsg[0], 80, "The crystal cracks dark. It slips free.");
		}
	}
	bMsgN = 1;
	bMsgI = 0;
	bPhase = 0;
	bAfter = 2;
}

static void pick_atk(void) {
	Spec *s = spec_of(bPl.species);
	if (!strcmp(bPl.species, "cathleen")) {
		if (bCur == 0) { mods_foeStr -= 4; bDmg = 5 + bPl.spc / 3; }
		else if (bCur == 1) { mods_foeAgl -= 4; bDmg = 5 + bPl.spc / 3; }
		else if (bCur == 2) { mods_foeSpc -= 4; bDmg = 5 + bPl.spc / 3; }
		else {
			if (bPl.spp <= 0) { snprintf(bMsg[0], 80, "Mana Surge is spent."); bMsgN = 1; bMsgI = 0; bPhase = 0; bAfter = 2; return; }
			bPl.spp--;
			int deb = mods_foeStr < 0 || mods_foeAgl < 0 || mods_foeSpc < 0;
			bDmg = (11 + bPl.spc) * (deb ? 2 : 1) / 2;
		}
		apply_hit();
		return;
	}
	if (bCur == 2) {
		snprintf(bMsg[0], 80, "Max holds.");
		bMsgN = 1;
		bMsgI = 0;
		bPhase = 0;
		bAfter = 3;
		return;
	}
	if (bCur == 1) {
		if (bPl.spp <= 0) { snprintf(bMsg[0], 80, "%s is spent.", s->special); bMsgN = 1; bMsgI = 0; bPhase = 0; bAfter = 2; return; }
		bPl.spp--;
		mg = 8;
		bPhase = 4;
		return;
	}
	int atk = bPl.str + mods_selfStr;
	int def = bFoe.str + mods_foeStr;
	bDmg = 6 + atk * 62 / 100 - def * 16 / 100 + irand(0, 3);
	if (bDmg < 1) bDmg = 1;
	apply_hit();
}

static void pick_guard(void) {
	int dmg = 6 + (bFoe.str + mods_foeStr) * 6 / 10;
	if (dmg < 1) dmg = 1;
	if (bCur == 0 && irand(0, 99) < 50) dmg = 0;
	else if (bCur == 1) dmg = dmg / 2 + 1;
	else dmg = dmg * 2 / 5 + 1;
	bPl.hp -= dmg;
	if (bPl.hp < 0) bPl.hp = 0;
	if (bPl.hp <= 0) {
		party[lead] = bPl;
		int nxt = -1;
		for (int i = 0; i < nparty; i++) if (i != lead && party[i].hp > 0) { nxt = i; break; }
		if (nxt >= 0) {
			lead = nxt;
			bPl = party[lead];
			snprintf(bMsg[0], 80, "%s jumps in.", bPl.name);
			bMsgN = 1;
			bMsgI = 0;
			bPhase = 0;
			bAfter = 1;
			return;
		}
		snprintf(bMsg[0], 80, "%s cannot stand.", bPl.name);
		bMsgN = 1;
		bMsgI = 0;
		bPhase = 0;
		bAfter = 7;
		return;
	}
	snprintf(bMsg[0], 80, "Took %d. Your turn.", dmg);
	bMsgN = 1;
	bMsgI = 0;
	bPhase = 0;
	bAfter = 1;
}

static void update_battle(float dt) {
	bT += dt;
	if (bPhase == 0) {
		if (confirm()) {
			bMsgI++;
			if (bMsgI >= bMsgN) {
				if (bAfter == 5) { finish_win(); return; }
				if (bAfter == 6) { mode = M_WORLD; encLock = 3; return; }
				if (bAfter == 7) {
					mode = M_WORLD;
					leader()->hp = leader()->maxHp * 2 / 5;
					if (leader()->hp < 1) leader()->hp = 1;
					encLock = 3;
					say1("Max", "We still breathe. Crawl back.");
					return;
				}
				bPhase = bAfter;
				if (bPhase == 1) fill_item_menu();
				if (bPhase == 2) fill_atk_menu();
				if (bPhase == 3) {
					bMenuN = 3;
					snprintf(bMenu[0], 40, "Dodge  AGI");
					snprintf(bMenu[1], 40, "Block  STR");
					snprintf(bMenu[2], 40, "Barrier  SPC");
					bCur = 0;
				}
			}
		}
		return;
	}
	if (bPhase == 4) {
		mg += dt * 110;
		if (mg > 100) mg = 0;
		if (confirm()) {
			float mul = (mg >= 46 && mg <= 54) ? 2.f : (mg >= 38 && mg <= 62) ? 1.45f : 0.7f;
			bDmg = (int)((11 + bPl.spc * 0.75f) * mul);
			if (bDmg < 1) bDmg = 1;
			apply_hit();
		}
		return;
	}
	if (pressed(SDL_SCANCODE_UP) || pressed(SDL_SCANCODE_W)) bCur = (bCur + bMenuN - 1) % bMenuN;
	if (pressed(SDL_SCANCODE_DOWN) || pressed(SDL_SCANCODE_S)) bCur = (bCur + 1) % bMenuN;
	if (cancel() && bPhase == 2) { bPhase = 1; fill_item_menu(); return; }
	if (confirm()) {
		if (bPhase == 1) pick_item();
		else if (bPhase == 2) pick_atk();
		else pick_guard();
	}
}

static void update_world(float dt) {
	if (doorLock > 0) doorLock--;
	if (annePh == 1) {
		float dx = px - ax, dy = py - ay, dist = hypotf(dx, dy);
		if (dist < 36) {
			annePh = 2;
			anneGift = 1;
			bag_gem += 5;
			const char *w[] = {"Anne", "Anne", "Max"};
			const char *t[] = {"Max. You actually fought.", "Take these. Five crystals.", "I won't."};
			sayn(3, w, t, 1);
			return;
		}
		float sp = 52 * dt;
		ax += dx / dist * sp;
		ay += dy / dist * sp;
		adir = fabsf(dx) > fabsf(dy) ? (dx < 0 ? DIR_LEFT : DIR_RIGHT) : (dy < 0 ? DIR_UP : DIR_DOWN);
		aanim += dt * 8;
		aframe = ((int)aanim) % 4;
		return;
	}
	if (annePh == 3) {
		ay += 80 * dt;
		adir = DIR_DOWN;
		aanim += dt * 8;
		aframe = ((int)aanim) % 4;
		if (ay > py + 300) annePh = 0;
	}
	if (mapId == 2) {
		ensure_soldiers();
		for (int i = 0; i < nsol; i++) {
			Sol *s = &sols[i];
			if (s->beaten) continue;
			if (s->chase) {
				float dx = px - s->fx, dy = py - s->fy, dist = hypotf(dx, dy);
				if (dist < 36) {
					s->chase = 0;
					start_battle(mint(s->spec, s->lv), 0, "A soldier sends a CryMon", s->name);
					snprintf(bTrainer, sizeof bTrainer, "soldier:%s", s->id);
					return;
				}
				s->fx += dx / dist * 112 * dt;
				s->fy += dy / dist * 112 * dt;
				s->anim += dt * 8;
				s->frame = ((int)s->anim) % 4;
				continue;
			}
			if (s->axis == 1) {
				s->fx += s->sign * 36 * dt;
				if (s->fx > s->maxv) { s->fx = s->maxv; s->sign = -1; s->dir = DIR_LEFT; }
				if (s->fx < s->minv) { s->fx = s->minv; s->sign = 1; s->dir = DIR_RIGHT; }
				s->anim += dt * 4;
				s->frame = ((int)s->anim) % 4;
			} else if (s->axis == 2) {
				s->fy += s->sign * 36 * dt;
				if (s->fy > s->maxv) { s->fy = s->maxv; s->sign = -1; s->dir = DIR_UP; }
				if (s->fy < s->minv) { s->fy = s->minv; s->sign = 1; s->dir = DIR_DOWN; }
				s->anim += dt * 4;
				s->frame = ((int)s->anim) % 4;
			}
			if (soldier_los(s)) s->chase = 1;
		}
	}

	int dx = 0, dy = 0;
	if (down(SDL_SCANCODE_LEFT) || down(SDL_SCANCODE_A)) { dx = -1; pdir = DIR_LEFT; }
	if (down(SDL_SCANCODE_RIGHT) || down(SDL_SCANCODE_D)) { dx = 1; pdir = DIR_RIGHT; }
	if (down(SDL_SCANCODE_UP) || down(SDL_SCANCODE_W)) { dy = -1; pdir = DIR_UP; }
	if (down(SDL_SCANCODE_DOWN) || down(SDL_SCANCODE_S)) { dy = 1; pdir = DIR_DOWN; }
	moving = dx || dy;
	if (moving) {
		float sp = 110;
		float nx = px + dx * sp * dt, ny = py + dy * sp * dt;
		if (!blocked(nx, py)) px = nx;
		if (!blocked(px, ny)) py = ny;
		px = clampf(px, 24, mapw() * TILE - 24);
		py = clampf(py, 40, maph() * TILE - 16);
		panim += dt * 6;
		pframe = ((int)panim) % 4;
		try_encounter();
	} else pframe = 0;

	/* warps */
	char ch = tileAt(px, py);
	if (doorLock <= 0) {
		if (mapId == 0 && ch == 'D') { warp(1, 'D', 1); say1("Max", "Night air. I can do this."); }
		else if (mapId == 1 && ch == 'D') warp(0, 'D', 0);
		else if (mapId == 1 && ch == 'Z') { warp(2, 'Y', 1); ensure_soldiers(); say1("Max", "The trees close over the path."); }
		else if (mapId == 2 && ch == 'Y') warp(1, 'Z', 0);
		else if (mapId == 2 && ch == 'O') { warp(3, 'O', 1); say1("Max", "The grass dies out. Stone and hush."); }
		else if (mapId == 3 && ch == 'O') warp(2, 'O', 0);
	}
	if (confirm()) interact();
	if (startp()) mode = M_PARTY;
	if (selectp()) mode = M_BAG;
	if (pressed(SDL_SCANCODE_1)) lead = 0;
	if (pressed(SDL_SCANCODE_2) && nparty > 1) lead = 1;
	if (pressed(SDL_SCANCODE_3) && nparty > 2) lead = 2;
	if (pressed(SDL_SCANCODE_4) && nparty > 3) lead = 3;
	if (pressed(SDL_SCANCODE_5) && nparty > 4) lead = 4;
	if (pressed(SDL_SCANCODE_6) && nparty > 5) lead = 5;
}

static void tick(float dt) {
	clockt += dt;
	if (hudT > 0) hudT -= dt;
	if (mode == M_TITLE) {
		if (confirm() || startp()) reset_run();
		return;
	}
	if (mode == M_END) {
		if (confirm()) mode = M_TITLE;
		return;
	}
	if (mode == M_TALK) {
		if (confirm()) {
			talki++;
			if (talki >= ntalk) begin_talk_end();
		}
		return;
	}
	if (mode == M_BATTLE) { update_battle(dt); return; }
	if (mode == M_BAG || mode == M_PARTY || mode == M_SHOP) {
		if (cancel() || startp() || selectp()) mode = M_WORLD;
		return;
	}
	update_world(dt);
}

static void draw(void) {
	SDL_SetRenderDrawBlendMode(ren, SDL_BLENDMODE_BLEND);
	if (mode == M_TITLE) draw_title();
	else if (mode == M_END) {
		fill(18, 17, 14, 255, 0, 0, VW, VH);
		text("CRYMON", 240, 160, 232, 228, 216, 2);
		text("The road continues. Walk. Catch. Survive.", 80, 240, 197, 206, 198, 1);
	} else if (mode == M_BATTLE) draw_battle();
	else if (mode == M_TALK) draw_talk();
	else if (mode == M_BAG) {
		draw_world();
		fill(18, 17, 14, 140, 0, 0, VW, VH);
		box(40, 40, 560, 400);
		text("BAG", 60, 56, 197, 206, 198, 1);
		char ln[64];
		snprintf(ln, sizeof ln, "Marks %d", marks);
		text(ln, 400, 56, 143, 74, 64, 1);
		snprintf(ln, sizeof ln, "Moss salve x%d", bag_salve);
		text(ln, 60, 100, 232, 228, 216, 1);
		snprintf(ln, sizeof ln, "Linen wrap x%d", bag_band);
		text(ln, 60, 130, 232, 228, 216, 1);
		snprintf(ln, sizeof ln, "Bitterroot x%d", bag_root);
		text(ln, 60, 160, 232, 228, 216, 1);
		snprintf(ln, sizeof ln, "Ash dust x%d", bag_dust);
		text(ln, 60, 190, 232, 228, 216, 1);
		snprintf(ln, sizeof ln, "Capture Crystal x%d", bag_gem);
		text(ln, 60, 220, 232, 228, 216, 1);
		text("X close", 60, 400, 90, 122, 82, 1);
	} else if (mode == M_PARTY) {
		draw_world();
		fill(18, 17, 14, 140, 0, 0, VW, VH);
		box(24, 20, 592, 440);
		text("CRYMON", 40, 32, 197, 206, 198, 1);
		for (int i = 0; i < nparty; i++) {
			int y = 70 + i * 56;
			char ln[80];
			snprintf(ln, sizeof ln, "%s%s  Lv%d  %d/%d", i == lead ? "> " : "  ", party[i].name, party[i].lv, party[i].hp, party[i].maxHp);
			text(ln, 48, y, i == lead ? 232 : 138, i == lead ? 228 : 134, i == lead ? 216 : 120, 1);
		}
		text("1-6 lead   X close", 40, 420, 90, 122, 82, 1);
	} else if (mode == M_SHOP) {
		draw_world();
		fill(18, 17, 14, 140, 0, 0, VW, VH);
		box(40, 40, 560, 400);
		text("BRAM'S STALL", 60, 56, 197, 206, 198, 1);
		text("Salve 10m   Wrap 6m   Root 8m   Dust 8m   Crystal 20m", 60, 120, 232, 228, 216, 1);
		text("Z buy salve   X leave", 60, 400, 90, 122, 82, 1);
	} else draw_world();
}

static char *exe_dir(void) {
	static char buf[512], dir[512];
	ssize_t n = readlink("/proc/self/exe", buf, sizeof buf - 1);
	if (n < 0) return ".";
	buf[n] = 0;
	snprintf(dir, sizeof dir, "%s", buf);
	char *s = strrchr(dir, '/');
	if (s) *s = 0;
	return dir;
}

int main(int argc, char **argv) {
	(void)argc;
	(void)argv;
	srand((unsigned)time(NULL));
	for (int i = 0; i < 4; i++) {
		mh[i] = 0;
		mw[i] = 0;
		for (int y = 0; maps[i][y]; y++) {
			int l = (int)strlen(maps[i][y]);
			if (l > mw[i]) mw[i] = l;
			mh[i] = y + 1;
		}
	}
	SDL_SetHint("SDL_HINT_RENDER_SCALE_QUALITY", "0");
	SDL_SetHint("SDL_RENDER_SCALE_QUALITY", "0");
	if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_EVENTS) != 0) {
		fprintf(stderr, "SDL_Init: %s\n", SDL_GetError());
		return 1;
	}
	int flags = SDL_WINDOW_SHOWN;
	if (!getenv("CRYMON_WINDOW")) flags |= SDL_WINDOW_FULLSCREEN;
	win = SDL_CreateWindow("CryMon", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, VW, VH, flags);
	ren = SDL_CreateRenderer(win, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
	if (!ren) ren = SDL_CreateRenderer(win, -1, SDL_RENDERER_ACCELERATED);
	SDL_RenderSetLogicalSize(ren, VW, VH);
	SDL_RenderSetIntegerScale(ren, 1);
	SDL_ShowCursor(0);
	char blob[512];
	snprintf(blob, sizeof blob, "%s/gfx_blob.bin", exe_dir());
	if (!load_gfx(blob)) {
		snprintf(blob, sizeof blob, "./gfx_blob.bin");
		if (!load_gfx(blob)) {
			fprintf(stderr, "CryMon: missing gfx_blob.bin\n");
			return 1;
		}
	}
	uint32_t last = SDL_GetTicks();
	int run = 1;
	while (run) {
		SDL_Event e;
		while (SDL_PollEvent(&e)) if (e.type == SDL_QUIT) run = 0;
		keys = SDL_GetKeyboardState(&nkeys);
		uint32_t now = SDL_GetTicks();
		float dt = (now - last) / 1000.f;
		if (dt > 0.05f) dt = 0.05f;
		last = now;
		tick(dt);
		SDL_SetRenderDrawColor(ren, 18, 17, 14, 255);
		SDL_RenderClear(ren);
		draw();
		SDL_RenderPresent(ren);
		if (nkeys > 0 && nkeys < 512) memcpy(prev, keys, (size_t)nkeys);
		SDL_Delay(8);
	}
	SDL_DestroyRenderer(ren);
	SDL_DestroyWindow(win);
	SDL_Quit();
	return 0;
}

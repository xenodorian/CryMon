/* Minimal libretro host: run a SNES ROM in Snes9x and dump RGB frames. */
#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include "libretro.h"

static uint16_t *g_frame;
static unsigned g_w, g_h;
static int g_got;
static unsigned g_buttons;
static char g_sysdir[256] = "/tmp/snes-sys";
static char g_savedir[256] = "/tmp/snes-save";
static int g_allow_invalid_vram;

static void video_cb(const void *data, unsigned width, unsigned height, size_t pitch) {
	if (!data || width == 0 || height == 0) return;
	if (!g_frame || g_w != width || g_h != height) {
		free(g_frame);
		g_frame = (uint16_t *)malloc(width * height * 2);
		g_w = width;
		g_h = height;
	}
	const uint8_t *src = (const uint8_t *)data;
	for (unsigned y = 0; y < height; y++)
		memcpy(g_frame + y * width, src + y * pitch, width * 2);
	g_got = 1;
}

static void input_poll(void) {}

static int16_t input_state(unsigned port, unsigned device, unsigned index, unsigned id) {
	(void)index;
	if (port != 0 || device != RETRO_DEVICE_JOYPAD) return 0;
	if (id >= 16) return 0;
	return (g_buttons >> id) & 1;
}

static size_t audio_batch(const int16_t *data, size_t frames) {
	(void)data;
	return frames;
}
static void audio_sample(int16_t l, int16_t r) {
	(void)l;
	(void)r;
}

static bool env_cb(unsigned cmd, void *data) {
	switch (cmd) {
	case RETRO_ENVIRONMENT_SET_PIXEL_FORMAT: {
		enum retro_pixel_format *fmt = (enum retro_pixel_format *)data;
		return *fmt == RETRO_PIXEL_FORMAT_RGB565 || *fmt == RETRO_PIXEL_FORMAT_0RGB1555;
	}
	case RETRO_ENVIRONMENT_GET_SYSTEM_DIRECTORY:
		*(const char **)data = g_sysdir;
		return true;
	case RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY:
		*(const char **)data = g_savedir;
		return true;
	case RETRO_ENVIRONMENT_GET_CAN_DUPE:
		*(bool *)data = true;
		return true;
	case RETRO_ENVIRONMENT_GET_VARIABLE: {
		struct retro_variable *var = (struct retro_variable *)data;
		if (!var || !var->key) return false;
		if (!strcmp(var->key, "snes9x_block_invalid_vram_access")) {
			var->value = g_allow_invalid_vram ? "disabled" : "enabled";
			return true;
		}
		return false;
	}
	case RETRO_ENVIRONMENT_GET_VARIABLE_UPDATE:
		*(bool *)data = false;
		return true;
	case RETRO_ENVIRONMENT_SET_VARIABLES:
	case RETRO_ENVIRONMENT_SET_CONTROLLER_INFO:
	case RETRO_ENVIRONMENT_SET_INPUT_DESCRIPTORS:
	case RETRO_ENVIRONMENT_SET_SUPPORT_ACHIEVEMENTS:
	case RETRO_ENVIRONMENT_SET_PERFORMANCE_LEVEL:
	case RETRO_ENVIRONMENT_SET_MEMORY_MAPS:
	case RETRO_ENVIRONMENT_SET_GEOMETRY:
	case RETRO_ENVIRONMENT_SET_SUBSYSTEM_INFO:
		return true;
	default:
		return false;
	}
}

static void write_ppm(const char *path, const uint16_t *px, unsigned w, unsigned h) {
	FILE *f = fopen(path, "wb");
	if (!f) return;
	fprintf(f, "P6\n%u %u\n255\n", w, h);
	for (unsigned i = 0; i < w * h; i++) {
		uint16_t p = px[i];
		uint8_t r = (uint8_t)(((p >> 11) & 31) * 255 / 31);
		uint8_t g = (uint8_t)(((p >> 5) & 63) * 255 / 63);
		uint8_t b = (uint8_t)((p & 31) * 255 / 31);
		fputc(r, f);
		fputc(g, f);
		fputc(b, f);
	}
	fclose(f);
}

static unsigned brightness(const uint16_t *px, unsigned n) {
	unsigned long s = 0;
	for (unsigned i = 0; i < n; i++) {
		uint16_t p = px[i];
		s += ((p >> 11) & 31) + ((p >> 5) & 63) + (p & 31);
	}
	return (unsigned)(s / (n ? n : 1));
}

static unsigned uniq_colors(const uint16_t *px, unsigned n) {
	unsigned char seen[8192];
	memset(seen, 0, sizeof seen);
	unsigned u = 0;
	for (unsigned i = 0; i < n; i++) {
		unsigned v = px[i] & 0xFFFF;
		unsigned b = v >> 3, m = 1u << (v & 7);
		if (!(seen[b] & m)) {
			seen[b] |= (unsigned char)m;
			u++;
		}
	}
	return u;
}

typedef struct {
	int lo, hi;
	unsigned btn;
} Step;

int main(int argc, char **argv) {
	if (argc < 3) {
		fprintf(stderr, "usage: %s rom.sfc outdir [core.so] [allow_invalid_vram]\n", argv[0]);
		return 1;
	}
	const char *rom_path = argv[1];
	const char *outdir = argv[2];
	const char *core = argc > 3 ? argv[3] : "/tmp/snes9x-src/snes9x/libretro/snes9x_libretro.so";
	g_allow_invalid_vram = argc > 4 && argv[4][0] == '1';
	mkdir(g_sysdir, 0755);
	mkdir(g_savedir, 0755);
	mkdir(outdir, 0755);

	void *h = dlopen(core, RTLD_NOW);
	if (!h) {
		fprintf(stderr, "dlopen: %s\n", dlerror());
		return 1;
	}

	void (*p_set_env)(retro_environment_t) = dlsym(h, "retro_set_environment");
	void (*p_set_video)(retro_video_refresh_t) = dlsym(h, "retro_set_video_refresh");
	void (*p_set_audio)(retro_audio_sample_t) = dlsym(h, "retro_set_audio_sample");
	void (*p_set_batch)(retro_audio_sample_batch_t) = dlsym(h, "retro_set_audio_sample_batch");
	void (*p_set_poll)(retro_input_poll_t) = dlsym(h, "retro_set_input_poll");
	void (*p_set_state)(retro_input_state_t) = dlsym(h, "retro_set_input_state");
	void (*p_init)(void) = dlsym(h, "retro_init");
	bool (*p_load)(const struct retro_game_info *) = dlsym(h, "retro_load_game");
	void (*p_run)(void) = dlsym(h, "retro_run");
	void *(*p_mem)(unsigned) = dlsym(h, "retro_get_memory_data");
	void (*p_ctrl)(unsigned, unsigned) = dlsym(h, "retro_set_controller_port_device");
	if (!p_init || !p_load || !p_run || !p_set_env) {
		fprintf(stderr, "missing symbols\n");
		return 1;
	}

	p_set_env(env_cb);
	fprintf(stderr, "init (allow_invalid_vram=%d)...\n", g_allow_invalid_vram);
	p_init();
	fprintf(stderr, "init ok\n");
	p_set_video(video_cb);
	p_set_audio(audio_sample);
	p_set_batch(audio_batch);
	p_set_poll(input_poll);
	p_set_state(input_state);

	FILE *rf = fopen(rom_path, "rb");
	if (!rf) {
		perror(rom_path);
		return 1;
	}
	fseek(rf, 0, SEEK_END);
	long sz = ftell(rf);
	fseek(rf, 0, SEEK_SET);
	void *rom = malloc((size_t)sz);
	if (fread(rom, 1, (size_t)sz, rf) != (size_t)sz) {
		fprintf(stderr, "short rom read\n");
		return 1;
	}
	fclose(rf);

	struct retro_game_info info;
	memset(&info, 0, sizeof info);
	info.path = rom_path;
	info.data = rom;
	info.size = (size_t)sz;
	fprintf(stderr, "load %ld bytes...\n", sz);
	if (!p_load(&info)) {
		fprintf(stderr, "retro_load_game failed\n");
		return 1;
	}
	fprintf(stderr, "load ok\n");
	if (p_ctrl)
		p_ctrl(0, RETRO_DEVICE_JOYPAD);

	enum {
		B_B = 1u << 0,
		B_SEL = 1u << 2,
		B_ST = 1u << 3,
		B_U = 1u << 4,
		B_D = 1u << 5,
		B_L = 1u << 6,
		B_R = 1u << 7,
		B_A = 1u << 8
	};

	Step tas[] = {
		{0, 80, 0},
		{81, 110, B_A | B_ST},
		{111, 140, 0},
		{141, 190, B_U | B_L},
		{191, 205, 0},
		{206, 220, B_A},
		{221, 250, 0},
		{251, 265, B_A},
		{266, 290, 0},
		{291, 305, B_A},
		{306, 330, 0},
		{331, 345, B_A},
		{346, 370, 0},
		{371, 385, B_A},
		{386, 420, 0},
		{421, 470, B_R | B_U},
		{471, 490, 0},
		{491, 505, B_A},
		{506, 540, 0},
		{541, 555, B_A},
		{556, 600, 0},
		{601, 680, B_D},
		{681, 720, 0},
		{721, 800, B_R},
		{801, 840, 0},
		{841, 900, B_L},
		{901, 1100, 0},
		{-1, -1, 0}
	};

	int dump_at[] = {2, 70, 130, 200, 240, 280, 360, 500, 650, 780, 1100, -1};
	int di = 0;
	int shot = 0;

	for (int f = 0; f <= 1100; f++) {
		g_buttons = 0;
		for (int i = 0; tas[i].lo >= 0; i++) {
			if (f >= tas[i].lo && f <= tas[i].hi) {
				g_buttons = tas[i].btn;
				break;
			}
		}
		g_got = 0;
		p_run();
		if (dump_at[di] >= 0 && f == dump_at[di]) {
			char path[512];
			snprintf(path, sizeof path, "%s/%02d-f%04d.ppm", outdir, shot, f);
			if (g_frame && g_got) {
				write_ppm(path, g_frame, g_w, g_h);
				unsigned br = brightness(g_frame, g_w * g_h);
				unsigned uq = uniq_colors(g_frame, g_w * g_h);
				fprintf(stderr, "shot %s %ux%u br=%u uniq=%u btn=%04x\n", path, g_w, g_h, br, uq, g_buttons);
			} else {
				fprintf(stderr, "no frame at %d w=%u h=%u\n", f, g_w, g_h);
			}
			if (p_mem) {
				uint8_t *ram = (uint8_t *)p_mem(RETRO_MEMORY_SYSTEM_RAM);
				if (ram) {
					fprintf(stderr, "zp:");
					for (int i = 0; i < 32; i++) fprintf(stderr, " %02x", ram[i]);
					fprintf(stderr, "\nneed=%02x mode=%02x map=%02x cam=%02x%02x joy=%02x%02x n=%02x%02x\n",
						ram[0x6A], ram[0x01], ram[0x02], ram[0x11], ram[0x10],
						ram[0x04], ram[0x03], ram[0x08], ram[0x07]);
					fprintf(stderr, "oam:");
					for (int i = 0; i < 16; i++) fprintf(stderr, " %02x", ram[0x200 + i]);
					fprintf(stderr, " bg3+214:");
					for (int i = 0; i < 16; i++) fprintf(stderr, " %02x", ram[0x500 + 0x214 + i]);
					fprintf(stderr, " dma=%02x%02x%02x x=%02x%02x\n", ram[0xF0], ram[0xF1], ram[0xF2], ram[0xF5], ram[0xF4]);
				}
				uint8_t *vram = (uint8_t *)p_mem(RETRO_MEMORY_VIDEO_RAM);
				if (vram) {
					unsigned nz = 0;
					for (int i = 0; i < 65536; i++) if (vram[i]) nz++;
					fprintf(stderr, "vram nz=%u t0:", nz);
					for (int i = 0; i < 16; i++) fprintf(stderr, " %02x", vram[i]);
					fprintf(stderr, " t1:");
					for (int i = 0; i < 16; i++) fprintf(stderr, " %02x", vram[32 + i]);
					fprintf(stderr, " map:");
					for (int i = 0; i < 16; i++) fprintf(stderr, " %02x", vram[0x8000 + i]);
					fprintf(stderr, " font:");
					for (int i = 0; i < 16; i++) fprintf(stderr, " %02x", vram[0x6000 + i]);
					fprintf(stderr, " font1:");
					for (int i = 0; i < 16; i++) fprintf(stderr, " %02x", vram[0x6010 + i]);
					fprintf(stderr, " spr:");
					for (int i = 0; i < 16; i++) fprintf(stderr, " %02x", vram[0x4000 + i]);
					fprintf(stderr, " bg3m:");
					for (int i = 0; i < 16; i++) fprintf(stderr, " %02x", vram[0x7000 + i]);
					fprintf(stderr, "\n");
				}
			}
			shot++;
			di++;
		}
	}
	free(g_frame);
	free(rom);
	return 0;
}

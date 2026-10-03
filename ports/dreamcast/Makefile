# CryMon Dreamcast port. Shared content lives in the web tree:
#   ../../content/*.json
#   ../../public/sprites
# See ../../docs/CRYMON.md

CC      = sh-elf-gcc
AS      = sh-elf-gcc
LD      = sh-elf-gcc
OBJCOPY = sh-elf-objcopy

ROOT      = ../..
CONTENT   = $(ROOT)/content
BAKE      = $(ROOT)/tools/bake_content.py
SPRITES   = $(ROOT)/public/sprites

ARCHFLAGS = -m4-single-only -ml
CFLAGS    = $(ARCHFLAGS) -O2 -fno-builtin -ffreestanding -fomit-frame-pointer \
            -Wall -Wextra -nostdlib -nostartfiles -nodefaultlibs
LDFLAGS   = $(ARCHFLAGS) -nostdlib -nostartfiles -nodefaultlibs -T dc.ld -Wl,--build-id=none

# STREAM=1 (default): monster battle frames go to disc/MONSTERS.BIN and are
# read off the disc at runtime (src/disc.c). STREAM=0: embed them in the ELF
# like before -- a known-good fallback build that never touches the disc.
STREAM ?= 1

# NATIVE=1 (default): build at native 640x480. tools/native480.sed rewrites
# src/main.c into build/main_native.c (src/main.c itself is not modified).
# NATIVE=0: compile src/main.c as is (320x240 logical, 2x2 pixel blocks).
NATIVE ?= 1
ifeq ($(NATIVE),1)
MAIN_SRC = build/main_native.c
else
MAIN_SRC = src/main.c
endif

OBJS = src/start.o src/main.o src/chip.o src/save.o src/disc.o

CONTENT_JSON = $(wildcard $(CONTENT)/*.json)
CONTENT_INC  = src/content_maps.inc src/content_talk.inc \
               src/content_species.inc src/content_items.inc src/content_logic.inc \
               src/content_world.inc src/content_audio.inc src/content_save.inc

all: crymon.elf

$(CONTENT_INC): $(CONTENT_JSON) $(BAKE)
	python3 $(BAKE) --content $(CONTENT) --out src

src/sprites.h: $(SPRITES) $(CONTENT)/sprites.json tools/gen_sprites.py
	CRYMON_STREAM=$(STREAM) python3 tools/gen_sprites.py $(SPRITES)

# Switching STREAM: `make sprites STREAM=0 && make STREAM=0 && make cdi STREAM=0`
# (sprites.h does not notice a STREAM change on its own).
sprites:
	CRYMON_STREAM=$(STREAM) python3 tools/gen_sprites.py $(SPRITES)

src/start.o: src/start.S
	$(AS) $(ARCHFLAGS) -c -o $@ $<

# Fails the build if the sed script stopped matching main.c, so a native
# build can never silently fall back to 320x240.
build/main_native.c: src/main.c tools/native480.sed
	mkdir -p build
	sed -f tools/native480.sed src/main.c > $@
	grep -q '^#define SCREEN_W 640' $@ && grep -q '^#define SCREEN_H 480' $@ && grep -q '^#define FB_SCALE 1' $@ || (rm -f $@; echo 'native480.sed did not apply to src/main.c'; exit 1)

src/main.o: $(MAIN_SRC) src/sprites.h src/chip.h src/save.h src/disc.h $(CONTENT_INC)
	$(CC) $(CFLAGS) -Isrc -c -o $@ $<

src/chip.o: src/chip.c src/chip.h src/content_audio.inc
	$(CC) $(CFLAGS) -c -o $@ $<

# vmu_icon.h (memory-card save icon) is written by gen_sprites.py with sprites.h.
src/vmu_icon.h: src/sprites.h

src/save.o: src/save.c src/save.h src/vmu_icon.h src/content_save.inc
	$(CC) $(CFLAGS) -c -o $@ $<

src/disc.o: src/disc.c src/disc.h
	$(CC) $(CFLAGS) -c -o $@ $<

crymon.elf: $(OBJS) dc.ld
	$(LD) $(LDFLAGS) -o $@ $(OBJS) -lgcc

cdi: crymon.elf
	mkdcdisc -e crymon.elf $(if $(filter 1,$(STREAM)),-f disc/MONSTERS.BIN) \
		-o crymon.cdi -n "CryMon" -a "CryMon" -N --allow-overwrite

clean:
	rm -rf $(OBJS) crymon.elf crymon.cdi build

.PHONY: all cdi clean sprites

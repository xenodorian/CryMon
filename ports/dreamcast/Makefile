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

OBJS = src/start.o src/main.o

CONTENT_JSON = $(wildcard $(CONTENT)/*.json)
CONTENT_INC  = src/content_maps.inc src/content_talk.inc \
               src/content_species.inc src/content_items.inc src/content_logic.inc

all: crymon.elf

$(CONTENT_INC): $(CONTENT_JSON) $(BAKE)
	python3 $(BAKE) --content $(CONTENT) --out src

src/sprites.h: $(SPRITES) tools/gen_sprites.py
	python3 tools/gen_sprites.py $(SPRITES)

src/start.o: src/start.S
	$(AS) $(ARCHFLAGS) -c -o $@ $<

src/main.o: src/main.c src/sprites.h $(CONTENT_INC)
	$(CC) $(CFLAGS) -c -o $@ $<

crymon.elf: $(OBJS) dc.ld
	$(LD) $(LDFLAGS) -o $@ $(OBJS) -lgcc

cdi: crymon.elf
	mkdcdisc -e crymon.elf -o crymon.cdi -n "CryMon" -a "BeelzFight" \
		-N --allow-overwrite

clean:
	rm -f $(OBJS) crymon.elf crymon.cdi

.PHONY: all cdi clean

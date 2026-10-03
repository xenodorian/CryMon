# Native 640x480 (phase 1). Applied to src/main.c at build time by the Makefile
# (NATIVE=1, the default). Output goes to build/main_native.c; src/main.c is
# not modified. Build with NATIVE=0 to compile src/main.c unchanged (320x240
# logical, 2x2 pixel blocks).
#
# Video hardware setup is already 640x480; only the logical size and the 2x2
# block write need to change. FB_OFFSET1 (0x96000) is already 640*480*2.
s/^#define SCREEN_W 320/#define SCREEN_W 640/
s/^#define SCREEN_H 240/#define SCREEN_H 480/
s/^#define FB_SCALE 2/#define FB_SCALE 1/
/^static void fb_put(/,/^}/{
/^[[:space:]]*p\[1\] = color;/d
/^[[:space:]]*p\[FB_W\] = color;/d
/^[[:space:]]*p\[FB_W + 1\] = color;/d
}

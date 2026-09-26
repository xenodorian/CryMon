/* Disc file reads for a bare-metal (no KOS) Dreamcast program.
 *
 * Uses the console BIOS's GD-ROM system calls, the same ones KallistiOS
 * wraps (kernel/arch/dreamcast/hardware/{syscalls,cdrom}.c and
 * fs/fs_iso9660.c were the reference for every number below):
 *
 *   - The function pointer lives at 0x8c0000bc. Arguments go in r4-r6,
 *     the function number in r7; r6 selects the GD-ROM "super function" (0).
 *   - A command is sent (SEND_COMMAND), then driven by calling EXEC_SERVER
 *     and polling CHECK_COMMAND until it stops being BUSY/PROCESSING.
 *   - Reads are PIO (the CPU copies the data), so there is no DMA setup,
 *     no interrupt handler and no cache maintenance to get wrong.
 *   - Sector addresses the drive takes are FADs: ISO9660 block + 150.
 *   - The TOC's last data track (CTRL == 4) is where the ISO lives on a
 *     MIL-CD like ours; its volume descriptor is 16 blocks in.
 *
 * Everything polls with a spin budget, so a missing disc or an emulator
 * without GD-ROM support fails (returns 0) instead of hanging.
 */
#include "disc.h"

typedef unsigned int u32;
typedef unsigned short u16;
typedef unsigned char u8;

#define GD_VECTOR        0x8c0000bcu
#define GD_SUPER         0          /* r6: GD-ROM functions (-1 = MISC) */
#define GD_SEND_COMMAND  0
#define GD_CHECK_COMMAND 1
#define GD_EXEC_SERVER   2
#define GD_INIT          3
#define GD_DRIVE_STATUS  4
#define GD_SECTOR_MODE   10

#define CMD_PIOREAD      16
#define CMD_GETTOC2      19
#define CMD_INIT         24

#define CHK_PROCESSING   1
#define CHK_COMPLETED    2
#define CHK_BUSY         4

#define DISC_TYPE_CDROM_XA 0x20
#define READ_DATA_AREA     0x2000

#define SPIN_BUDGET 4000000u

static int gd_call(int r4, int r5, int r7) {
    int (*fn)(int, int, int, int) =
        (int (*)(int, int, int, int))(*(volatile u32 *)GD_VECTOR);
    return fn(r4, r5, GD_SUPER, r7);
}

static int gd_exec(int cmd, void *params) {
    int status[4];
    int hnd, r;
    u32 spins;
    hnd = gd_call(cmd, (int)params, GD_SEND_COMMAND);
    if(hnd <= 0) return 0;
    for(spins = 0; spins < SPIN_BUDGET; spins++) {
        gd_call(0, 0, GD_EXEC_SERVER);
        r = gd_call(hnd, (int)status, GD_CHECK_COMMAND);
        if(r == CHK_PROCESSING || r == CHK_BUSY) continue;
        return r == CHK_COMPLETED;
    }
    return 0;
}

/* The G1 bus refuses the drive until the BIOS has been read across it once.
   The boot ROM does this before running us, so this is normally a no-op;
   it matters after a reset path that skipped it. (KOS cdrom_init.) */
static void g1_unlock(void) {
    volatile u32 *react = (volatile u32 *)0xa05f74e4u;
    volatile u32 *state = (volatile u32 *)0xa05f74ecu;
    volatile u32 *bios = (volatile u32 *)0xa0000000u;
    u32 i, n;
    if(*state == 3) return;                     /* already passed */
    if(*(volatile u16 *)0xa0000000u == 0xe6ff) { *react = 0x3ff;    n = 0x400 / 4; }
    else                                       { *react = 0x1fffff; n = 0x200000 / 4; }
    for(i = 0; i < n; i++) (void)bios[i];
}

static u32 le32(const u8 *p) {
    return (u32)p[0] | ((u32)p[1] << 8) | ((u32)p[2] << 16) | ((u32)p[3] << 24);
}

static int read_fad(u32 fad, u32 count, void *dst) {
    struct { u32 start_sec, num_sec; void *buffer; u32 is_test; } p;
    p.start_sec = fad;
    p.num_sec = count;
    p.buffer = dst;
    p.is_test = 0;
    return gd_exec(CMD_PIOREAD, &p);
}

static int g_ready = -1;        /* -1 untried, 0 failed, 1 ok */
static u32 g_root_lba, g_root_size;
static u8 g_sector[DISC_SECTOR] __attribute__((aligned(32)));

int disc_init(void) {
    static u32 toc[102];        /* entry[99], first, last, leadout */
    int drive[2];
    struct { u32 area; u32 *buffer; } tp;
    struct { u32 rw; u32 sector_part; int track_type; int sector_size; } sm;
    u32 session_fad = 0, first, last, i;
    int tries;

    if(g_ready >= 0) return g_ready;
    g_ready = 0;

    g1_unlock();
    gd_call(0, 0, GD_INIT);
    for(tries = 0; tries < 2 && !gd_exec(CMD_INIT, 0); tries++) {}
    if(tries == 2) return 0;

    drive[0] = drive[1] = 0;
    gd_call((int)drive, 0, GD_DRIVE_STATUS);
    sm.rw = 0;
    sm.sector_part = READ_DATA_AREA;
    sm.track_type = drive[1] == DISC_TYPE_CDROM_XA ? 2048 : 1024;
    sm.sector_size = DISC_SECTOR;
    gd_call((int)&sm, 0, GD_SECTOR_MODE);

    tp.area = 0;                /* low-density area: a CD / MIL-CD */
    tp.buffer = toc;
    if(!gd_exec(CMD_GETTOC2, &tp)) return 0;
    first = (toc[99] >> 16) & 0xff;
    last = (toc[100] >> 16) & 0xff;
    if(first < 1 || last > 99 || first > last) return 0;
    for(i = last; i >= first; i--) {
        if(((toc[i - 1] >> 28) & 0xf) == 4) { session_fad = toc[i - 1] & 0x00ffffff; break; }
    }
    if(!session_fad) return 0;

    /* Primary volume descriptor, 16 blocks into the data track. */
    if(!read_fad(session_fad + 16, 1, g_sector)) return 0;
    if(g_sector[0] != 1 || g_sector[1] != 'C' || g_sector[2] != 'D' ||
       g_sector[3] != '0' || g_sector[4] != '0' || g_sector[5] != '1') return 0;
    g_root_lba = le32(g_sector + 156 + 2);
    g_root_size = le32(g_sector + 156 + 10);
    g_ready = 1;
    return 1;
}

static int upper(int c) { return (c >= 'a' && c <= 'z') ? c - 32 : c; }

static int name_match(const u8 *rec_name, int len, const char *want) {
    int i;
    for(i = 0; i < len && rec_name[i] != ';'; i++) {
        if(!want[i] || upper(rec_name[i]) != upper(want[i])) return 0;
    }
    return want[i] == 0;
}

int disc_find(const char *name, DiscFile *out) {
    u32 sec, off, nsec;
    if(!disc_init()) return 0;
    nsec = (g_root_size + DISC_SECTOR - 1) / DISC_SECTOR;
    for(sec = 0; sec < nsec; sec++) {
        if(!read_fad(g_root_lba + sec + 150, 1, g_sector)) return 0;
        for(off = 0; off < DISC_SECTOR; ) {
            u8 len = g_sector[off];
            if(len == 0) break;                 /* rest of this sector is padding */
            if(off + len > DISC_SECTOR) break;
            if(!(g_sector[off + 25] & 2) &&     /* not a directory */
               name_match(g_sector + off + 33, g_sector[off + 32], name)) {
                out->lba = le32(g_sector + off + 2);
                out->size = le32(g_sector + off + 10);
                return 1;
            }
            off += len;
        }
    }
    return 0;
}

int disc_read_sectors(const DiscFile *f, unsigned int first, unsigned int count, void *dst) {
    if(!f || !disc_init()) return 0;
    if(((u32)dst & 1) || (first + count) * DISC_SECTOR > f->size + DISC_SECTOR - 1) return 0;
    return read_fad(f->lba + first + 150, count, dst);
}

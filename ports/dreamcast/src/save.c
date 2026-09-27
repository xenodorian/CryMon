/* Shared 256-byte save blob (content/save.json) + Dreamcast VMU I/O.
 * Byte layout matches src/game/save.ts exactly. */
#include <stdint.h>
#include "save.h"

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

#define MAPLE_BASE      0xa05f6c00u
#define MAPLE_DMA_ADDR  (*(volatile u32 *)(MAPLE_BASE + 0x04))
#define MAPLE_STATE     (*(volatile u32 *)(MAPLE_BASE + 0x18))
#define MAPLE_CMD_BREAD  11
#define MAPLE_CMD_BWRITE 12
#define MAPLE_RESP_DATA  8
#define MAPLE_FUNC_MEM   0x02000000u
#define MAPLE_DEST_VMU   0x01

#define P2(p)   ((volatile u32 *)(((u32)(p)) | 0x20000000u))
#define PHYS(p) (((u32)(p)) & 0x1fffffffu)

static u32 vmu_cmd[160] __attribute__((aligned(32)));
static u32 vmu_resp[160] __attribute__((aligned(32)));

static void put_u16(u8 *p, u16 v) {
    p[0] = (u8)(v & 0xff);
    p[1] = (u8)((v >> 8) & 0xff);
}
static u16 get_u16(const u8 *p) {
    return (u16)(p[0] | (p[1] << 8));
}

static u16 checksum(const u8 *buf) {
    int i;
    u16 s = 0;
    for(i = 0; i < 142; i++)
        s = (u16)((s + buf[i]) & 0xffff);
    return s;
}

void save_pack(u8 *dst, const SaveLive *s) {
    int i, p;
    for(i = 0; i < SAVE_SIZE; i++) dst[i] = 0;
    dst[0] = 'C'; dst[1] = 'R'; dst[2] = 'Y'; dst[3] = 'M';
    dst[4] = SAVE_VERSION;
    dst[5] = s->map_id;
    dst[6] = s->dir;
    dst[7] = s->party_n > SAVE_PARTY_MAX ? SAVE_PARTY_MAX : s->party_n;
    put_u16(dst + 8, s->x);
    put_u16(dst + 10, s->y);
    put_u16(dst + 12, s->marks);
    dst[14] = s->lead;
    dst[15] = s->battles;
    dst[16] = s->mason2_map;
    dst[17] = s->reputation;
    for(i = 0; i < SAVE_ITEM_N; i++) dst[SAVE_BAG_OFF[i]] = s->bag[i];
    for(i = 0; i < SAVE_FLAG_BYTES; i++) dst[SAVE_FLAG_OFF[i]] = s->flags[i];
    for(p = 0; p < dst[7]; p++) {
        u8 *o = dst + 46 + p * SAVE_PARTY_SLOT;
        o[0] = s->party[p].species;
        o[1] = s->party[p].lv;
        o[2] = s->party[p].hp;
        o[3] = s->party[p].maxHp;
        o[4] = s->party[p].str;
        o[5] = s->party[p].agl;
        o[6] = s->party[p].spc;
        o[7] = s->party[p].spp;
        o[8] = s->party[p].sppMax;
        o[9] = s->party[p].shiny;
        put_u16(o + 10, s->party[p].xp);
        o[SAVE_PARTY_NATURE] = s->party[p].nature;
        o[13] = s->party[p].status;
        o[14] = s->party[p].status_turns;
        o[15] = s->party[p].poison_stack;
    }
    /* party2 @156, active_party @252, party2_n @253, executed_mask @152 */
    {
        int n2 = s->party2_n > SAVE_PARTY_MAX ? SAVE_PARTY_MAX : s->party2_n;
        dst[252] = s->active_party ? 1 : 0;
        dst[253] = (u8)n2;
        put_u16(dst + 152, (u16)(s->executed_mask & 0xffff));
        put_u16(dst + 154, (u16)((s->executed_mask >> 16) & 0xffff));
        for(p = 0; p < n2; p++) {
            u8 *o = dst + 156 + p * SAVE_PARTY_SLOT;
            o[0] = s->party2[p].species;
            o[1] = s->party2[p].lv;
            o[2] = s->party2[p].hp;
            o[3] = s->party2[p].maxHp;
            o[4] = s->party2[p].str;
            o[5] = s->party2[p].agl;
            o[6] = s->party2[p].spc;
            o[7] = s->party2[p].spp;
            o[8] = s->party2[p].sppMax;
            o[9] = s->party2[p].shiny;
            put_u16(o + 10, s->party2[p].xp);
            o[SAVE_PARTY_NATURE] = s->party2[p].nature;
            o[13] = s->party2[p].status;
            o[14] = s->party2[p].status_turns;
            o[15] = s->party2[p].poison_stack;
        }
    }
        put_u16(dst + 142, checksum(dst));
    for(i = 0; i < SAVE_DEX_BYTES; i++) {
        int so = SAVE_DEX_SEEN_OFF[i];
        int co = SAVE_DEX_CAUGHT_OFF[i];
        dst[so] = s->dex_seen[i];
        dst[co] = s->dex_caught[i];
    }
}

void save_flag_put(SaveLive *s, int id, int v) {
    if(id < 0 || id >= SAVE_FLAG_N) return;
    if(v) s->flags[id >> 3] |= (unsigned char)(1 << (id & 7));
    else s->flags[id >> 3] &= (unsigned char)~(1 << (id & 7));
}

int save_flag_get(const SaveLive *s, int id) {
    if(id < 0 || id >= SAVE_FLAG_N) return 0;
    return (s->flags[id >> 3] >> (id & 7)) & 1;
}

int save_unpack(const u8 *src, SaveLive *s) {
    int i, p, n;
    if(src[0] != 'C' || src[1] != 'R' || src[2] != 'Y' || src[3] != 'M') return 0;
    if(src[4] != SAVE_VERSION) return 0;
    if(get_u16(src + 142) != checksum(src)) return 0;
    s->map_id = src[5];
    s->dir = src[6];
    n = src[7];
    if(n > SAVE_PARTY_MAX) n = SAVE_PARTY_MAX;
    s->party_n = (unsigned char)n;
    s->x = get_u16(src + 8);
    s->y = get_u16(src + 10);
    s->marks = get_u16(src + 12);
    s->lead = src[14];
    s->battles = src[15];
    s->mason2_map = src[16];
    s->reputation = src[17];
    for(i = 0; i < SAVE_ITEM_N; i++) s->bag[i] = src[SAVE_BAG_OFF[i]];
    for(i = 0; i < SAVE_FLAG_BYTES; i++) s->flags[i] = src[SAVE_FLAG_OFF[i]];
    for(p = 0; p < n; p++) {
        const u8 *o = src + 46 + p * SAVE_PARTY_SLOT;
        s->party[p].species = o[0];
        s->party[p].lv = o[1];
        s->party[p].hp = o[2];
        s->party[p].maxHp = o[3];
        s->party[p].str = o[4];
        s->party[p].agl = o[5];
        s->party[p].spc = o[6];
        s->party[p].spp = o[7];
        s->party[p].sppMax = o[8];
        s->party[p].shiny = o[9];
        s->party[p].xp = get_u16(o + 10);
        s->party[p].nature = o[SAVE_PARTY_NATURE];
        s->party[p].status = o[13];
        s->party[p].status_turns = o[14];
        s->party[p].poison_stack = o[15];
    }
    for(i = 0; i < SAVE_DEX_BYTES; i++) {
        int so = SAVE_DEX_SEEN_OFF[i];
        int co = SAVE_DEX_CAUGHT_OFF[i];
        s->dex_seen[i] = src[so];
        s->dex_caught[i] = src[co];
    }
    s->active_party = src[252] ? 1 : 0;
    s->party2_n = src[253] > SAVE_PARTY_MAX ? SAVE_PARTY_MAX : src[253];
    s->executed_mask = (unsigned int)get_u16(src + 152) | ((unsigned int)get_u16(src + 154) << 16);
    for(p = 0; p < (int)s->party2_n; p++) {
        const u8 *o = src + 156 + p * SAVE_PARTY_SLOT;
        s->party2[p].species = o[0];
        s->party2[p].lv = o[1];
        s->party2[p].hp = o[2];
        s->party2[p].maxHp = o[3];
        s->party2[p].str = o[4];
        s->party2[p].agl = o[5];
        s->party2[p].spc = o[6];
        s->party2[p].spp = o[7];
        s->party2[p].sppMax = o[8];
        s->party2[p].shiny = o[9];
        s->party2[p].xp = get_u16(o + 10);
        s->party2[p].nature = o[SAVE_PARTY_NATURE];
        s->party2[p].status = o[13];
        s->party2[p].status_turns = o[14];
        s->party2[p].poison_stack = o[15];
    }
    return 1;
}

/* ----------------------------------------------------------------------
 * VMU (memory card) block I/O over the maple bus, no KOS.
 *
 * Rewritten to match KallistiOS (hardware/maple/vmu.c, fs/vmufs.c,
 * include/dc/{maple,vmufs}.h), which is where every constant below comes
 * from. The first version of this file had four bugs that made every save
 * fail: raw block numbers instead of the (block << 24 | ...) id, one
 * 512-byte write instead of 4 x 128-byte phases + BSYNC, requiring a
 * DATATRF reply from commands that answer OK, and the FAT's free /
 * end-of-file markers swapped.
 *
 * Card layout (standard 128 KB VMU): root block 255 says where the FAT
 * (one block of 256 little-endian u16s) and the directory (dir_size blocks
 * counting DOWN from dir_loc, 16 x 32-byte entries each) live. Our save is
 * one data file, one block long: dir entry type 0x33, name CRYMON_DAT.
 * ---------------------------------------------------------------------- */

#define MAPLE_CMD_BSYNC      13
#define MAPLE_RESP_OK        7
#define VMU_ROOT_BLOCK       255
#define VMU_FAT_FREE         0xfffcu
#define VMU_FAT_LAST         0xfffau
#define VMU_DIR_ENTRY        32
#define VMU_FILE_DATA        0x33

/* One maple frame to the VMU, waiting for the reply. `want` is the reply
   code that means success for this command. */
static int maple_xfer(u32 cmd, u32 nwords, const u32 *words, u32 want) {
    volatile u32 *c = P2(vmu_cmd);
    volatile u32 *r = P2(vmu_resp);
    u32 timeout, i;
    c[0] = nwords | 0x80000000u;            /* data words, port A, last frame */
    c[1] = PHYS(vmu_resp);
    c[2] = cmd | (MAPLE_DEST_VMU << 8) | (0u << 16) | (nwords << 24);
    for(i = 0; i < nwords; i++) c[3 + i] = words[i];
    r[0] = 0xffffffffu;
    MAPLE_DMA_ADDR = PHYS(vmu_cmd);
    MAPLE_STATE = 1;
    for(timeout = 0; timeout < 4000000u; timeout++)
        if(MAPLE_STATE == 0) break;
    if(MAPLE_STATE != 0) return 0;
    return (r[0] & 0xffu) == want;
}

static u32 vmu_blkid(u16 blk, u32 phase) {
    return ((u32)(blk & 0xff) << 24) | ((u32)(blk >> 8) << 16) | (phase << 8);
}

static int vmu_read_block(u16 blk, u8 *out) {
    u32 w[2];
    volatile u32 *r = P2(vmu_resp);
    int i;
    w[0] = MAPLE_FUNC_MEM;
    w[1] = vmu_blkid(blk, 0);
    if(!maple_xfer(MAPLE_CMD_BREAD, 2, w, MAPLE_RESP_DATA)) return 0;
    /* reply: r[1] function, r[2] block id, r[3..130] the 512 bytes */
    if(r[1] != MAPLE_FUNC_MEM || r[2] != w[1]) return 0;
    for(i = 0; i < 128; i++) {
        u32 v = r[3 + i];
        out[i * 4 + 0] = (u8)(v & 0xff);
        out[i * 4 + 1] = (u8)((v >> 8) & 0xff);
        out[i * 4 + 2] = (u8)((v >> 16) & 0xff);
        out[i * 4 + 3] = (u8)((v >> 24) & 0xff);
    }
    return 1;
}

static int vmu_write_block_once(u16 blk, const u8 *in) {
    u32 w[2 + 32];
    u32 phase;
    int i;
    for(phase = 0; phase < 4; phase++) {
        const u8 *src = in + phase * 128;
        w[0] = MAPLE_FUNC_MEM;
        w[1] = vmu_blkid(blk, phase);
        for(i = 0; i < 32; i++)
            w[2 + i] = (u32)src[i * 4] | ((u32)src[i * 4 + 1] << 8) |
                       ((u32)src[i * 4 + 2] << 16) | ((u32)src[i * 4 + 3] << 24);
        if(!maple_xfer(MAPLE_CMD_BWRITE, 2 + 32, w, MAPLE_RESP_OK)) return 0;
    }
    w[0] = MAPLE_FUNC_MEM;
    w[1] = vmu_blkid(blk, 4);
    return maple_xfer(MAPLE_CMD_BSYNC, 2, w, MAPLE_RESP_OK);
}

/* Real cards are sometimes busy right after a write; KOS retries too. */
static int vmu_write_block(u16 blk, const u8 *in) {
    int tries;
    for(tries = 0; tries < 3; tries++)
        if(vmu_write_block_once(blk, in)) return 1;
    return 0;
}

static u16 le16(const u8 *p) { return (u16)(p[0] | (p[1] << 8)); }

typedef struct { u16 fat_loc, dir_loc, dir_size, user_blocks; } VmuLayout;

static int vmu_layout(VmuLayout *L) {
    u8 root[512];
    int i;
    if(!vmu_read_block(VMU_ROOT_BLOCK, root)) return 0;
    for(i = 0; i < 16; i++) if(root[i] != 0x55) return 0;   /* not formatted */
    L->fat_loc = le16(root + 0x46);
    L->dir_loc = le16(root + 0x4a);
    L->dir_size = le16(root + 0x4c);
    L->user_blocks = le16(root + 0x50);
    return L->dir_size > 0 && L->dir_size <= 32 && L->user_blocks <= 256;
}

static const char SAVE_NAME[12] = {
    'C','R','Y','M','O','N','_','D','A','T',' ',' '
};

static int name_eq(const u8 *e) {
    int i;
    for(i = 0; i < 12; i++) if(e[4 + i] != (u8)SAVE_NAME[i]) return 0;
    return 1;
}

/* Walk every directory block. Returns 1 if our file exists (*file_blk set).
   Also reports the first free entry (*free_dblk / *free_ent, -1 if none)
   so the caller can create the file without a second pass. */
static int vmu_find(const VmuLayout *L, u16 *file_blk, int *free_dblk, int *free_ent) {
    u8 dir[512];
    int d, ent;
    *free_dblk = -1;
    *free_ent = -1;
    for(d = 0; d < L->dir_size; d++) {
        u16 blk = (u16)(L->dir_loc - d);
        if(!vmu_read_block(blk, dir)) return 0;
        for(ent = 0; ent < 512 / VMU_DIR_ENTRY; ent++) {
            const u8 *e = dir + ent * VMU_DIR_ENTRY;
            if(e[0] == VMU_FILE_DATA && name_eq(e)) {
                *file_blk = le16(e + 2);
                return 1;
            }
            if(e[0] == 0x00 && *free_dblk < 0) { *free_dblk = blk; *free_ent = ent; }
        }
    }
    return 0;
}

int save_present(void) {
    VmuLayout L;
    return vmu_layout(&L);
}

/* ----------------------------------------------------------------------
 * VMS file header (what the Dreamcast BIOS file manager and the VMU show):
 * layout from KallistiOS include/dc/vmu_pkg.h + util/vmu_pkg.c.
 *   0x00 desc_short[16]  space padded      0x10 desc_long[32] space padded
 *   0x30 app_id[16]      NUL padded        0x40 icon_cnt u16
 *   0x42 icon_anim_speed 0x44 eyecatch_type 0x46 crc u16
 *   0x48 data_len u32    0x4c reserved[20]  0x60 icon_pal[16] ARGB4444
 *   0x80 icon bitmap 32x32 @ 4bpp (512 bytes), then the payload.
 * crc = CRC-16/CCITT (KOS net_crc16ccitt, start 0) over header + icon +
 * payload with the crc field zeroed. Icon art: vmu_icon.h (gen_sprites.py).
 * The file is VMS_BLOCKS blocks, chained in the FAT, header at block 0.
 * ---------------------------------------------------------------------- */
#include "vmu_icon.h"

#define VMS_HDR_BYTES   0x80
#define VMS_DATA_OFF    (VMS_HDR_BYTES + 512)
#define VMS_FILE_BYTES  (VMS_DATA_OFF + SAVE_SIZE)
#define VMS_BLOCKS      ((VMS_FILE_BYTES + 511) / 512)
#define VMS_MAX_BLOCKS  4

static u16 crc16_ccitt(const u8 *d, int n) {
    u16 rv = 0, tmp;
    while(n--) {
        tmp = (u16)((rv >> 8) ^ *d++);
        tmp ^= tmp >> 4;
        rv = (u16)((rv << 8) ^ (tmp << 12) ^ (tmp << 5) ^ tmp);
    }
    return rv;
}

static void put_text(u8 *dst, int n, const char *s, u8 pad) {
    int i;
    for(i = 0; i < n; i++) dst[i] = pad;
    for(i = 0; i < n && s[i]; i++) dst[i] = (u8)s[i];
}

static void vms_build(u8 *file, const SaveLive *s) {
    int i;
    u16 crc;
    for(i = 0; i < VMS_BLOCKS * 512; i++) file[i] = 0;
    put_text(file + 0x00, 16, "CRYMON", ' ');
    put_text(file + 0x10, 32, "CryMon save", ' ');
    put_text(file + 0x30, 16, "CRYMON", 0);
    file[0x40] = 1;                                    /* one icon frame */
    file[0x48] = (u8)(SAVE_SIZE & 0xff);
    file[0x49] = (u8)((SAVE_SIZE >> 8) & 0xff);
    for(i = 0; i < 16; i++) put_u16(file + 0x60 + i * 2, VMU_ICON_PAL[i]);
    for(i = 0; i < 512; i++) file[VMS_HDR_BYTES + i] = VMU_ICON[i];
    save_pack(file + VMS_DATA_OFF, s);
    crc = crc16_ccitt(file, VMS_FILE_BYTES);           /* crc field is 0 here */
    put_u16(file + 0x46, crc);
}

static u16 fat_get(const u8 *fat, int i) { return le16(fat + i * 2); }
static void fat_set(u8 *fat, int i, u16 v) { fat[i * 2] = (u8)(v & 0xff); fat[i * 2 + 1] = (u8)(v >> 8); }

/* Follow a file's FAT chain into blks[]; returns how many were found. */
static int vmu_chain(const u8 *fat, u16 first, u16 *blks, int max) {
    int n = 0;
    u16 b = first;
    while(n < max && b < 256) {
        blks[n++] = b;
        b = fat_get(fat, b);
        if(b == VMU_FAT_LAST || b == VMU_FAT_FREE) break;
    }
    return n;
}

/* Locate our directory entry: its block/index, or -1. */
static int vmu_find_entry(const VmuLayout *L, int *dblk, int *dent, u8 *dir) {
    int d, ent;
    for(d = 0; d < L->dir_size; d++) {
        u16 blk = (u16)(L->dir_loc - d);
        if(!vmu_read_block(blk, dir)) return -1;
        for(ent = 0; ent < 512 / VMU_DIR_ENTRY; ent++) {
            const u8 *e = dir + ent * VMU_DIR_ENTRY;
            if(e[0] == VMU_FILE_DATA && name_eq(e)) { *dblk = blk; *dent = ent; return 1; }
        }
    }
    return 0;
}

int save_store(const SaveLive *s) {
    VmuLayout L;
    u8 file[VMS_BLOCKS * 512];
    u8 fat[512], dir[512];
    u16 blks[VMS_MAX_BLOCKS];
    int dblk, dent, found, i, n;

    vms_build(file, s);
    if(!vmu_layout(&L)) return 0;
    if(!vmu_read_block(L.fat_loc, fat)) return 0;
    found = vmu_find_entry(&L, &dblk, &dent, dir);
    if(found < 0) return 0;

    if(found) {
        u8 *e = dir + dent * VMU_DIR_ENTRY;
        n = vmu_chain(fat, le16(e + 2), blks, VMS_MAX_BLOCKS);
        if(n == VMS_BLOCKS && le16(e + 0x18) == VMS_BLOCKS) {
            /* Same size as before: overwrite the blocks in place. */
            for(i = 0; i < VMS_BLOCKS; i++)
                if(!vmu_write_block(blks[i], file + i * 512)) return 0;
            return 1;
        }
        /* Older/other-size save (e.g. the headerless 1-block format):
           release its blocks and entry, then write a fresh file below. */
        for(i = 0; i < n; i++) fat_set(fat, blks[i], VMU_FAT_FREE);
        for(i = 0; i < VMU_DIR_ENTRY; i++) e[i] = 0;
    } else {
        /* New file: find a free directory slot. */
        u16 unused;
        int free_dblk, free_ent;
        if(vmu_find(&L, &unused, &free_dblk, &free_ent)) return 0;   /* can't happen */
        if(free_dblk < 0) return 0;                                  /* directory full */
        dblk = free_dblk;
        dent = free_ent;
        if(!vmu_read_block((u16)dblk, dir)) return 0;
    }

    /* Allocate VMS_BLOCKS free blocks from the top, as the BIOS does. */
    n = 0;
    for(i = L.user_blocks - 1; i >= 0 && n < VMS_BLOCKS; i--)
        if(fat_get(fat, i) == VMU_FAT_FREE) blks[n++] = (u16)i;
    if(n < VMS_BLOCKS) return 0;                                     /* card full */
    for(i = 0; i < VMS_BLOCKS; i++)
        fat_set(fat, blks[i], i + 1 < VMS_BLOCKS ? blks[i + 1] : VMU_FAT_LAST);
    {
        u8 *e = dir + dent * VMU_DIR_ENTRY;
        int k;
        for(k = 0; k < VMU_DIR_ENTRY; k++) e[k] = 0;
        e[0] = VMU_FILE_DATA;
        e[2] = (u8)(blks[0] & 0xff);
        e[3] = (u8)(blks[0] >> 8);
        for(k = 0; k < 12; k++) e[4 + k] = (u8)SAVE_NAME[k];
        e[0x18] = VMS_BLOCKS;                            /* size in blocks */
        e[0x1a] = 0;                                     /* header at block 0 */
    }
    /* Data into the (still free) blocks first, then FAT, then directory:
       a crash part-way leaves either the old state or a leaked block,
       never a directory entry pointing at unwritten data. */
    for(i = 0; i < VMS_BLOCKS; i++)
        if(!vmu_write_block(blks[i], file + i * 512)) return 0;
    if(!vmu_write_block(L.fat_loc, fat)) return 0;
    return vmu_write_block((u16)dblk, dir);
}

int save_restore(SaveLive *s) {
    VmuLayout L;
    u8 fat[512], dir[512];
    u8 file[VMS_MAX_BLOCKS * 512];
    u16 blks[VMS_MAX_BLOCKS];
    int dblk, dent, n, i, len;
    u16 crc_saved;
    if(!vmu_layout(&L)) return 0;
    if(vmu_find_entry(&L, &dblk, &dent, dir) != 1) return 0;
    if(!vmu_read_block(L.fat_loc, fat)) return 0;
    n = vmu_chain(fat, le16(dir + dent * VMU_DIR_ENTRY + 2), blks, VMS_MAX_BLOCKS);
    if(n < 1) return 0;
    for(i = 0; i < n; i++)
        if(!vmu_read_block(blks[i], file + i * 512)) return 0;
    /* Headerless 1-block saves written before the VMS header existed start
       "CRYM" + version byte (< 0x20). The VMS header's desc_short is the
       printable "CRYMON  ...", so byte 4 ('O') tells the two apart. */
    if(file[0] == 'C' && file[1] == 'R' && file[2] == 'Y' && file[3] == 'M' && file[4] < 0x20)
        return save_unpack(file, s);
    if(n < VMS_BLOCKS) return 0;
    /* data_len comes from the header, not SAVE_SIZE: a file written by an
       older build holds a shorter blob (280 before Leg 3). The CRC covers
       only what was written; the missing tail reads as zero. */
    len = le16(file + 0x48);
    if(len < 144 || len > SAVE_SIZE || file[0x4a] || file[0x4b]) return 0;
    crc_saved = le16(file + 0x46);
    file[0x46] = file[0x47] = 0;
    if(crc16_ccitt(file, VMS_DATA_OFF + len) != crc_saved) return 0;
    for(i = VMS_DATA_OFF + len; i < VMS_FILE_BYTES; i++) file[i] = 0;
    return save_unpack(file + VMS_DATA_OFF, s);
}

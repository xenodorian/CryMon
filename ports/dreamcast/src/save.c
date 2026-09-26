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
    for(i = 0; i < SAVE_ITEM_N; i++) dst[18 + i] = s->bag[i];
    for(i = 0; i < 8; i++) dst[38 + i] = s->flags[i];
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
    for(i = 0; i < SAVE_ITEM_N; i++) s->bag[i] = src[18 + i];
    for(i = 0; i < 8; i++) s->flags[i] = src[38 + i];
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

static int vmu_find_or_alloc(u16 *file_blk) {
    VmuLayout L;
    u8 fat[512], dir[512];
    int free_dblk, free_ent, i, free_blk = -1;
    if(!vmu_layout(&L)) return 0;
    if(vmu_find(&L, file_blk, &free_dblk, &free_ent)) return 1;
    if(free_dblk < 0) return 0;                      /* directory full */
    if(!vmu_read_block(L.fat_loc, fat)) return 0;
    for(i = L.user_blocks - 1; i >= 0; i--) {        /* VMU allocates from the top */
        if(le16(fat + i * 2) == VMU_FAT_FREE) { free_blk = i; break; }
    }
    if(free_blk < 0) return 0;                       /* card full */
    fat[free_blk * 2] = (u8)(VMU_FAT_LAST & 0xff);
    fat[free_blk * 2 + 1] = (u8)(VMU_FAT_LAST >> 8);
    if(!vmu_read_block((u16)free_dblk, dir)) return 0;
    {
        u8 *e = dir + free_ent * VMU_DIR_ENTRY;
        int k;
        for(k = 0; k < VMU_DIR_ENTRY; k++) e[k] = 0;
        e[0] = VMU_FILE_DATA;
        e[2] = (u8)(free_blk & 0xff);
        e[3] = (u8)(free_blk >> 8);
        for(k = 0; k < 12; k++) e[4 + k] = (u8)SAVE_NAME[k];
        e[0x18] = 1;                                 /* size: 1 block */
    }
    /* FAT first: a crash after it only leaks one block, never points the
       directory at a block the FAT still calls free. */
    if(!vmu_write_block(L.fat_loc, fat)) return 0;
    if(!vmu_write_block((u16)free_dblk, dir)) return 0;
    *file_blk = (u16)free_blk;
    return 1;
}

int save_store(const SaveLive *s) {
    u8 blob[SAVE_SIZE];
    u8 blk[512];
    u16 file_blk;
    int i;
    save_pack(blob, s);
    if(!vmu_find_or_alloc(&file_blk)) return 0;
    for(i = 0; i < 512; i++) blk[i] = 0;
    for(i = 0; i < SAVE_SIZE; i++) blk[i] = blob[i];
    return vmu_write_block(file_blk, blk);
}

int save_restore(SaveLive *s) {
    VmuLayout L;
    u8 blk[512];
    u16 file_blk = 0;
    int free_dblk, free_ent;
    if(!vmu_layout(&L)) return 0;
    if(!vmu_find(&L, &file_blk, &free_dblk, &free_ent)) return 0;
    if(!vmu_read_block(file_blk, blk)) return 0;
    return save_unpack(blk, s);
}

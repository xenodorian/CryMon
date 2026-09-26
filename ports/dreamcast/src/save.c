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
#define MAPLE_CMD_MINFO  10
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
        int so = i < SAVE_DEX_LO_BYTES ? SAVE_DEX_SEEN + i : SAVE_DEX_SEEN_HI + i - SAVE_DEX_LO_BYTES;
        int co = i < SAVE_DEX_LO_BYTES ? SAVE_DEX_CAUGHT + i : SAVE_DEX_CAUGHT_HI + i - SAVE_DEX_LO_BYTES;
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
        int so = i < SAVE_DEX_LO_BYTES ? SAVE_DEX_SEEN + i : SAVE_DEX_SEEN_HI + i - SAVE_DEX_LO_BYTES;
        int co = i < SAVE_DEX_LO_BYTES ? SAVE_DEX_CAUGHT + i : SAVE_DEX_CAUGHT_HI + i - SAVE_DEX_LO_BYTES;
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

static int maple_xfer(u32 dest, u32 cmd, u32 extra_words, const u32 *extra) {
    volatile u32 *c = P2(vmu_cmd);
    volatile u32 *r = P2(vmu_resp);
    u32 timeout;
    u32 i;
    c[0] = extra_words + 1u;
    if(extra_words + 1u > 1u) c[0] |= 0x80000000u;
    else c[0] |= 0x80000000u;
    c[1] = PHYS(vmu_resp);
    c[2] = cmd | (dest << 8) | (0u << 16) | ((extra_words + 1u) << 24);
    for(i = 0; i < extra_words + 1u && i < 150; i++)
        c[3 + i] = extra[i];
    r[0] = 0xffffffffu;
    MAPLE_DMA_ADDR = PHYS(vmu_cmd);
    MAPLE_STATE = 1;
    for(timeout = 0; timeout < 4000000u; timeout++) {
        if(MAPLE_STATE == 0) break;
    }
    if(MAPLE_STATE != 0) return 0;
    if((r[0] & 0xffu) != MAPLE_RESP_DATA) return 0;
    return 1;
}

static int vmu_minfo(u16 *fat_blk, u16 *dir_blk, u16 *user_blk) {
    u32 extra[1];
    volatile u32 *r = P2(vmu_resp);
    extra[0] = MAPLE_FUNC_MEM;
    if(!maple_xfer(MAPLE_DEST_VMU, MAPLE_CMD_MINFO, 0, extra)) return 0;
    /* minfo payload after function word */
    *fat_blk = (u16)(r[4] & 0xffffu);
    *dir_blk = (u16)((r[4] >> 16) & 0xffffu);
    *user_blk = (u16)(r[5] & 0xffffu);
    return 1;
}

static int vmu_read_block(u16 blk, u8 *out) {
    u32 extra[2];
    volatile u32 *r = P2(vmu_resp);
    int i;
    extra[0] = MAPLE_FUNC_MEM;
    extra[1] = blk;
    if(!maple_xfer(MAPLE_DEST_VMU, MAPLE_CMD_BREAD, 1, extra)) return 0;
    for(i = 0; i < 128; i++) {
        u32 w = r[3 + i];
        out[i * 4 + 0] = (u8)(w & 0xff);
        out[i * 4 + 1] = (u8)((w >> 8) & 0xff);
        out[i * 4 + 2] = (u8)((w >> 16) & 0xff);
        out[i * 4 + 3] = (u8)((w >> 24) & 0xff);
    }
    return 1;
}

static int vmu_write_block(u16 blk, const u8 *in) {
    u32 extra[130];
    int i;
    extra[0] = MAPLE_FUNC_MEM;
    extra[1] = blk;
    for(i = 0; i < 128; i++) {
        extra[2 + i] =
            (u32)in[i * 4] |
            ((u32)in[i * 4 + 1] << 8) |
            ((u32)in[i * 4 + 2] << 16) |
            ((u32)in[i * 4 + 3] << 24);
    }
    return maple_xfer(MAPLE_DEST_VMU, MAPLE_CMD_BWRITE, 129, extra);
}

static const char SAVE_NAME[12] = {
    'C','R','Y','M','O','N','_','D','A','T',' ',' '
};

static int name_eq(const u8 *e) {
    int i;
    for(i = 0; i < 12; i++) if(e[4 + i] != (u8)SAVE_NAME[i]) return 0;
    return 1;
}

int save_present(void) {
    u16 fat, dir, user;
    return vmu_minfo(&fat, &dir, &user);
}

static int vmu_find_or_alloc(u16 *file_blk, u16 *fat_blk, u16 *dir_blk) {
    u8 fat[512], dir[512];
    int i, ent, free_blk = -1, free_ent = -1;
    u16 user;
    if(!vmu_minfo(fat_blk, dir_blk, &user)) return 0;
    if(!vmu_read_block(*fat_blk, fat)) return 0;
    if(!vmu_read_block(*dir_blk, dir)) return 0;
    for(ent = 0; ent < 16; ent++) {
        u8 *e = dir + ent * 32;
        if(e[0] == 0x33 && name_eq(e)) {
            *file_blk = (u16)(e[2] | (e[3] << 8));
            return 1;
        }
        if(e[0] == 0x00 && free_ent < 0) free_ent = ent;
    }
    for(i = 1; i < 200; i++) {
        u16 f = (u16)(fat[i * 2] | (fat[i * 2 + 1] << 8));
        if(f == 0xfffa) { free_blk = i; break; }
    }
    if(free_ent < 0 || free_blk < 0) return 0;
    fat[free_blk * 2] = 0xfc;
    fat[free_blk * 2 + 1] = 0xff;
    {
        u8 *e = dir + free_ent * 32;
        int k;
        for(k = 0; k < 32; k++) e[k] = 0;
        e[0] = 0x33;
        e[2] = (u8)(free_blk & 0xff);
        e[3] = (u8)(free_blk >> 8);
        for(k = 0; k < 12; k++) e[4 + k] = (u8)SAVE_NAME[k];
        e[0x18] = 1;
    }
    if(!vmu_write_block(*fat_blk, fat)) return 0;
    if(!vmu_write_block(*dir_blk, dir)) return 0;
    *file_blk = (u16)free_blk;
    return 1;
}

int save_store(const SaveLive *s) {
    u8 blob[SAVE_SIZE];
    u8 blk[512];
    u16 file_blk, fat_blk, dir_blk;
    int i;
    save_pack(blob, s);
    if(!vmu_find_or_alloc(&file_blk, &fat_blk, &dir_blk)) return 0;
    for(i = 0; i < 512; i++) blk[i] = 0;
    for(i = 0; i < SAVE_SIZE; i++) blk[i] = blob[i];
    return vmu_write_block(file_blk, blk);
}

int save_restore(SaveLive *s) {
    u8 fat[512], dir[512], blk[512];
    u16 fat_blk, dir_blk, user, file_blk = 0;
    int ent, found = 0;
    if(!vmu_minfo(&fat_blk, &dir_blk, &user)) return 0;
    if(!vmu_read_block(dir_blk, dir)) return 0;
    (void)fat;
    for(ent = 0; ent < 16; ent++) {
        u8 *e = dir + ent * 32;
        if(e[0] == 0x33 && name_eq(e)) {
            file_blk = (u16)(e[2] | (e[3] << 8));
            found = 1;
            break;
        }
    }
    if(!found) return 0;
    if(!vmu_read_block(file_blk, blk)) return 0;
    return save_unpack(blk, s);
}

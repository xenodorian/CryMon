#ifndef CRYMON_SAVE_H
#define CRYMON_SAVE_H

#include "content_save.inc"

typedef struct {
    unsigned char species, lv, hp, maxHp, str, agl, spc, spp, sppMax, shiny, nature;
    unsigned short xp;
} SaveMon;

typedef struct {
    unsigned char map_id, dir, party_n, lead, battles, mason2_map, reputation;
    unsigned short x, y, marks;
    unsigned char bag[SAVE_ITEM_N];
    unsigned char flags[8];
    SaveMon party[SAVE_PARTY_MAX];
    unsigned char dex_seen[SAVE_DEX_BYTES];
    unsigned char dex_caught[SAVE_DEX_BYTES];
    /* Leg 2.7.3: father's party + active selector (save bytes 149+). */
    unsigned char party2_n, active_party;
    SaveMon party2[SAVE_PARTY_MAX];
    unsigned int executed_mask;
} SaveLive;

void save_pack(unsigned char *dst, const SaveLive *s);
int save_unpack(const unsigned char *src, SaveLive *s);
int save_store(const SaveLive *s);
int save_restore(SaveLive *s);
int save_present(void);
void save_flag_put(SaveLive *s, int id, int v);
int save_flag_get(const SaveLive *s, int id);

#endif

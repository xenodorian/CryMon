#ifndef CRYMON_CHIP_H
#define CRYMON_CHIP_H

void chip_init(void);
void chip_tick(void);
void chip_set_song(int id);
void chip_sfx(int id);
void chip_sfx_ui(void);
void chip_sfx_ok(void);
void chip_sfx_miss(void);
void chip_sfx_hit(void);
void chip_sfx_special(void);
void chip_sfx_catch(void);
void chip_sfx_save(void);
void chip_sfx_heal(void);
void chip_sfx_faint(void);
int chip_song_title(void);
int chip_song_battle(int trainer);
int chip_song_map(int map_id);
int chip_song_ending(void);

#endif

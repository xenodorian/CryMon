/* Read files off the game disc at runtime, without KOS.
 *
 * The whole game used to be one executable loaded into RAM at boot. This
 * lets big data (monster battle frames today, region packs later) live as
 * plain files on the disc's ISO9660 data track and be read only when
 * needed. See disc.c for how, and the "Disc streaming" notes in
 * CURRENT_WORK.md for what uses it.
 */
#ifndef CRYMON_DISC_H
#define CRYMON_DISC_H

#define DISC_SECTOR 2048

typedef struct {
    unsigned int lba;   /* ISO9660 extent start (absolute logical block) */
    unsigned int size;  /* bytes */
} DiscFile;

/* Bring the drive up and find the data track's root directory. Safe to
 * call more than once; returns 1 when the disc is readable. */
int disc_init(void);

/* Look a file up in the disc's root directory by name ("MONSTERS.BIN"),
 * case-insensitive, ignoring the ";1" version suffix. Returns 1 if found. */
int disc_find(const char *name, DiscFile *out);

/* Read `count` whole sectors starting `first` sectors into `f` into dst
 * (2-byte aligned). Returns 1 on success. */
int disc_read_sectors(const DiscFile *f, unsigned int first, unsigned int count, void *dst);

#endif

/* Host-side check that the Dreamcast save code reads a web save blob.
 * Build: cc -w -Iports/dreamcast/src ports/dreamcast/tools/save_host_check.c -o save_host_check
 * Run:   ./save_host_check blob.bin [flag_id=expected ...]
 * Prints the decoded fields, repacks the blob with save_pack() and fails
 * (exit 1) if unpack fails, any byte differs, or an expected flag differs.
 * Only save_pack/save_unpack/save_flag_* run; the VMU/Maple code is
 * compiled in but never called. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../src/save.c"

int main(int argc, char **argv) {
    unsigned char buf[SAVE_SIZE], out[SAVE_SIZE];
    SaveLive s;
    FILE *f;
    size_t n;
    int i, diff = 0, bad = 0;
    if(argc < 2) { fprintf(stderr, "usage: %s blob.bin [flag=value ...]\n", argv[0]); return 2; }
    f = fopen(argv[1], "rb");
    if(!f) { perror(argv[1]); return 2; }
    n = fread(buf, 1, SAVE_SIZE, f);
    fclose(f);
    memset(&s, 0, sizeof s);
    if(n != SAVE_SIZE || !save_unpack(buf, &s)) { printf("unpack FAILED (read %zu of %d)\n", n, SAVE_SIZE); return 1; }
    printf("map=%d x=%u y=%u marks=%u battles=%u party_n=%d rep=%d\n",
           s.map_id, s.x, s.y, s.marks, s.battles, s.party_n, s.reputation - 100);
    memset(out, 0, sizeof out);
    save_pack(out, &s);
    for(i = 0; i < SAVE_SIZE; i++) if(out[i] != buf[i]) {
        if(diff < 8) printf("byte %d web=%02x dc=%02x\n", i, buf[i], out[i]);
        diff++;
    }
    printf("repack_diff_bytes=%d\n", diff);
    for(i = 2; i < argc; i++) {
        int id, want;
        if(sscanf(argv[i], "%d=%d", &id, &want) != 2) continue;
        if(save_flag_get(&s, id) != want) { printf("flag %d = %d, want %d\n", id, save_flag_get(&s, id), want); bad++; }
    }
    return (diff || bad) ? 1 : 0;
}

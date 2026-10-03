#define TITLE_SCALE 3
#define DIALOGUE_SCALE 1

static void draw_press_start(int cur, int has_save) {
#ifdef HAVE_SCREEN_ART
    blit_sprite_2x(screen_title, BATTLE_BG_W / 2, BATTLE_BG_H / 2, 0, 0);
    /* Max's portrait on the left and Quillpup on the right, as on the
       web title (drawTitle), before the panel so the menu sits on top. */
    draw_title_sprites();
    /* see-through menu panel: brass 1px outline, darkened middle */
    dim_rect(97, 113, 126, 40);
    fill_rect(96, 112, 128, 1, rgb565(150, 118, 64));
    fill_rect(96, 153, 128, 1, rgb565(150, 118, 64));
    fill_rect(96, 113, 1, 40, rgb565(150, 118, 64));
    fill_rect(223, 113, 1, 40, rgb565(150, 118, 64));
#else
    vram_clear();
#endif
    draw_text_center_s("CRYMON", SCREEN_W / 2, 48, 0xFFFF, 2);
    draw_text_center_s(cur == 0 ? "> CONTINUE" : "CONTINUE", SCREEN_W / 2, 120,
                        has_save ? (cur == 0 ? rgb565(168, 216, 144) : rgb565(197, 206, 198))
                                 : rgb565(138, 134, 120), 1);
    draw_text_center_s(cur == 1 ? "> NEW GAME" : "NEW GAME", SCREEN_W / 2, 140,
                        cur == 1 ? rgb565(168, 216, 144) : rgb565(197, 206, 198), 1);
    draw_text_center_s("A CONFIRM", SCREEN_W / 2, SCREEN_H - 28,
                        rgb565(168, 216, 144), 1);
}


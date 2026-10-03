/* '-', '+', '/', needed by the battle system's stat-mod and damage
   messages ("STR+4", "FOE STR-3", "HP N/N") -- font_AZ/font_09 alone
   can't render any of these. */
static const uint8_t glyph_minus[8] = {
    0, 0, 0, 0b00111100, 0, 0, 0, 0,
};
static const uint8_t glyph_plus[8] = {
    0, 0b00011000, 0b00011000, 0b01111110, 0b00011000, 0b00011000, 0, 0,
};
static const uint8_t glyph_slash[8] = {
    0b00000011, 0b00000110, 0b00001100, 0b00011000,
    0b00110000, 0b01100000, 0b01000000, 0,
};

/* Punctuation, added to restore the reference's actual TALK_* text
   (apostrophes/periods/commas/question and exclamation marks) instead
   of the all-depunctuated placeholder text this font's original A-Z/
   0-9/-+/ set forced. Same minimalist style as the digits above (a
   6-wide glyph inside the 8-wide cell). */
static const uint8_t glyph_apostrophe[8] = {
    0b00110000, 0b00110000, 0b00100000, 0, 0, 0, 0, 0,
};
static const uint8_t glyph_period[8] = {
    0, 0, 0, 0, 0, 0, 0b00110000, 0,
};
static const uint8_t glyph_comma[8] = {
    0, 0, 0, 0, 0, 0b00110000, 0b00110000, 0b00100000,
};
static const uint8_t glyph_question[8] = {
    0b00111100, 0b01100110, 0b00001100, 0b00011000,
    0b00011000, 0, 0b00011000, 0,
};
/* '>' menu cursor ("> NEW GAME", party/shop lists): without it the
   cursor fell through to a blank cell. */
static const uint8_t glyph_gt[8] = {
    0b01100000, 0b00110000, 0b00011000, 0b00001100,
    0b00011000, 0b00110000, 0b01100000, 0,
};
static const uint8_t glyph_exclaim[8] = {
    0b00011000, 0b00011000, 0b00011000, 0b00011000,
    0b00011000, 0, 0b00011000, 0,
};


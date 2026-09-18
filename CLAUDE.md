# CryMon — Claude stub

**Contract:** [`docs/CRYMON.md`](docs/CRYMON.md). Read it before editing.
You own the **Dreamcast runtime**. Grok owns the web runtime. Both edit
`content/*.json` and `public/sprites/`.

Canonical tree: `xenodorian/CryMon` `ports/dreamcast/`.

```
python3 tools/bake_content.py --content content --out ports/dreamcast/src
python3 ports/dreamcast/tools/gen_sprites.py
python3 tools/check_sync.py --strict
make -C ports/dreamcast
make -C ports/dreamcast cdi
```

JSON first for rules, then `main.c`. Never hand-edit `content_*.inc` or `sprites.h`.
If JSON and `main.c` disagree, JSON wins — re-bake.
Do not touch Max’s walk cycle unless the user names Max.
If art is missing, tag `PLACEHOLDER_ART`. Do not reuse another character’s sprite.

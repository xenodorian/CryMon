# CryMon — Grok stub

Platform rules in `AGENTS.md` still apply.

**Contract:** [`docs/CRYMON.md`](docs/CRYMON.md). Do not restate it here.
You own the **web runtime**. Claude owns the Dreamcast runtime. Both edit
`content/*.json` and `public/sprites/`.

```
npm run dev                          # leave running
npm run typecheck
python3 tools/check_sync.py          # after JSON / sprite catalog edits
python3 tools/bake_content.py --content content --out ports/dreamcast/src
python3 ports/dreamcast/tools/gen_sprites.py
```

Keep the preview playable. JSON first for rules. Never hand-edit
`ports/dreamcast/src/content_*.inc` or `sprites.h`. Never revive SNES / LÖVE / SDL.

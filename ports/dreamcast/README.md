# Dreamcast port

Runtime only. Contract: [`../../docs/CRYMON.md`](../../docs/CRYMON.md).

```
python3 ../../tools/bake_content.py --content ../../content --out src
python3 tools/gen_sprites.py
python3 ../../tools/check_sync.py --strict
make
make cdi
```

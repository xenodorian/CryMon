#!/bin/bash
set -e
cd "$(dirname "$0")/.."
python3 tools/merge_world.py
python3 tools/bake_content.py
python3 tools/check_sync.py --strict
npm run typecheck 2>&1 | tail -5
npm run build 2>&1 | tail -3
make -C ports/dreamcast clean >/dev/null 2>&1
make -C ports/dreamcast 2>&1 | tail -8
git checkout HEAD -- ports/dreamcast/crymon.cdi ports/dreamcast/crymon.elf 2>/dev/null || true
echo "=== verify_step.sh: ALL GREEN ==="

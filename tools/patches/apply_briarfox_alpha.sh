#!/bin/bash
set -e
for i in 1 2 3 4; do
  base64 -d < tools/patches/briarfox_${i}.b64 > public/sprites/monsters/briarfox/${i}.png
  echo "wrote $i $(wc -c < public/sprites/monsters/briarfox/${i}.png)"
done

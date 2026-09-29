#!/usr/bin/env python3
import base64, pathlib, importlib.util
root = pathlib.Path("public/sprites/npc")
for i in range(1,5):
    path = pathlib.Path(f"tools/opal_data_{i}.py")
    spec = importlib.util.spec_from_file_location(f"opal_data_{i}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    p = root / f"opal-{i}.png"
    p.write_bytes(base64.b64decode(mod.DATA))
    print("wrote", p, p.stat().st_size)

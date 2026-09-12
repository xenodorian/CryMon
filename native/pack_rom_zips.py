#!/usr/bin/env python3
"""Pack CryMon handheld zips.

Root of both zips is unpack-safe for /roms/ports:
  CryMon.sh
  crymon/
  READ_ME_FIRST.txt

Never put gameinfo.xml, gamelist.xml, port.json, cover.png, or screenshot.png
at the zip root. Those files at the ports folder root make ArkOS hide Ports.
"""
from __future__ import annotations

import json
import os
import shutil
import stat
import struct
import tempfile
import zipfile
from pathlib import Path

from PIL import Image

ROOT = Path("/workspace")
NATIVE = ROOT / "native"
SPRITES = ROOT / "public" / "sprites"
ROM = ROOT / "public" / "rom"
PM = NATIVE / "portmaster"

# Files allowed at the zip root. Anything else (especially XML) hides Ports.
ROOT_FORBID_SUFFIX = (".xml", ".json", ".png", ".jpg", ".jpeg")


def pack_blob() -> Path:
    entries = []
    for p in sorted(SPRITES.rglob("*.png")):
        rel = p.relative_to(SPRITES).as_posix()
        key = rel[:-4]
        im = Image.open(p).convert("RGBA")
        entries.append((key, im.size[0], im.size[1], im.tobytes()))
    blob = NATIVE / "gfx_blob.bin"
    with blob.open("wb") as f:
        f.write(b"CMGX")
        f.write(struct.pack("<I", len(entries)))
        for key, w, h, raw in entries:
            bkey = key.encode("ascii")
            f.write(struct.pack("<H", len(bkey)))
            f.write(bkey)
            f.write(struct.pack("<HH", w, h))
            f.write(struct.pack("<I", len(raw)))
            f.write(raw)
    return blob


def add_file(z: zipfile.ZipFile, src: Path, arc: str, executable: bool = False) -> None:
    zi = zipfile.ZipInfo(arc)
    mode = 0o755 if executable else 0o644
    zi.external_attr = (mode | stat.S_IFREG) << 16
    zi.compress_type = zipfile.ZIP_DEFLATED
    z.writestr(zi, src.read_bytes())


def add_dir(z: zipfile.ZipFile, arc: str) -> None:
    name = arc if arc.endswith("/") else arc + "/"
    zi = zipfile.ZipInfo(name)
    zi.external_attr = (0o755 | stat.S_IFDIR) << 16
    z.writestr(zi, b"")


def assert_unpack_safe(zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
    root_files = [n for n in names if "/" not in n]
    root_dirs = [n for n in names if n.count("/") == 1 and n.endswith("/")]
    bad = [n for n in root_files if n not in {"CryMon.sh", "READ_ME_FIRST.txt"}]
    bad += [n for n in root_dirs if n not in {"crymon/"}]
    xml_root = [n for n in root_files if n.lower().endswith(".xml")]
    if xml_root:
        raise SystemExit(f"{zip_path.name}: XML at zip root would hide Ports: {xml_root}")
    for n in root_files:
        if n.lower().endswith(ROOT_FORBID_SUFFIX):
            raise SystemExit(f"{zip_path.name}: forbidden root file {n}")
    if bad:
        raise SystemExit(f"{zip_path.name}: unpack-unsafe root {bad}")
    if "CryMon.sh" not in names or "crymon/" not in names:
        raise SystemExit(f"{zip_path.name}: missing CryMon.sh or crymon/")


def write_zip(path: Path, staging: Path, extra_in_game: list[tuple[Path, str]] | None = None) -> None:
    extra_in_game = extra_in_game or []
    with zipfile.ZipFile(path, "w") as z:
        add_file(z, staging / "CryMon.sh", "CryMon.sh", True)
        add_file(z, staging / "READ_ME_FIRST.txt", "READ_ME_FIRST.txt")
        add_dir(z, "crymon/")
        add_dir(z, "crymon/licenses/")
        add_file(z, staging / "crymon/crymon.aarch64", "crymon/crymon.aarch64", True)
        add_file(z, staging / "crymon/crymon.x86_64", "crymon/crymon.x86_64", True)
        add_file(z, staging / "crymon/crymon.gptk", "crymon/crymon.gptk")
        add_file(z, staging / "crymon/gfx_blob.bin", "crymon/gfx_blob.bin")
        add_file(z, staging / "crymon/licenses/LICENSE", "crymon/licenses/LICENSE")
        add_file(z, staging / "crymon/screenshot.png", "crymon/screenshot.png")
        for src, arc in extra_in_game:
            add_file(z, src, arc)
    assert_unpack_safe(path)


def main() -> None:
    blob = pack_blob()
    a64 = NATIVE / "crymon.aarch64"
    x64 = NATIVE / "crymon.x86_64"
    if not a64.exists() or not x64.exists():
        raise SystemExit("missing native binaries")

    ROM.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="crymon-zip-"))
    try:
        (staging / "crymon" / "licenses").mkdir(parents=True)
        shutil.copy2(PM / "CryMon.sh", staging / "CryMon.sh")
        shutil.copy2(PM / "READ_ME_FIRST.txt", staging / "READ_ME_FIRST.txt")
        shutil.copy2(a64, staging / "crymon/crymon.aarch64")
        shutil.copy2(x64, staging / "crymon/crymon.x86_64")
        os.chmod(staging / "crymon/crymon.aarch64", 0o755)
        os.chmod(staging / "crymon/crymon.x86_64", 0o755)
        os.chmod(staging / "CryMon.sh", 0o755)
        shutil.copy2(PM / "crymon.gptk", staging / "crymon/crymon.gptk")
        shutil.copy2(blob, staging / "crymon/gfx_blob.bin")
        shutil.copy2(PM / "LICENSE", staging / "crymon/licenses/LICENSE")
        shutil.copy2(PM / "screenshot.png", staging / "crymon/screenshot.png")

        ports = ROM / "CryMon-ports.zip"
        write_zip(ports, staging)

        port_json = json.loads((PM / "port.json").read_text())
        nested = staging / "crymon.port.json"
        nested.write_text(json.dumps(port_json, indent=2) + "\n")
        extra = [
            (nested, "crymon/crymon.port.json"),
            (PM / "cover.png", "crymon/cover.png"),
            (PM / "README.md", "crymon/README.md"),
        ]
        pmz = ROM / "CryMon-portmaster.zip"
        write_zip(pmz, staging, extra)

        print("blob", blob.stat().st_size)
        print("ports", ports, ports.stat().st_size)
        print("portmaster", pmz, pmz.stat().st_size)
    finally:
        shutil.rmtree(staging, ignore_errors=True)


if __name__ == "__main__":
    main()

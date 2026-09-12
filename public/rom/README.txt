CryMon
======

Both handheld zips are safe to unzip into the existing ports folder.
They do not include gameinfo.xml or gamelist.xml.

Copy into Ports (CryMon-ports.zip)
----------------------------------
Unzip into EASYROMS/ports or roms/ports. You should see:

  CryMon.sh
  crymon/

Do not replace the ports folder. Do not delete PortMaster.

If an older GEMWAR port is still installed, delete GEMWAR.sh and the
gemwar folder so you are not running the stale build.

If Ports vanished from the carousel (old zip):
  1. On the SD card, in ports, delete gamelist.xml and gameinfo.xml.
  2. Leave the PortMaster folder.
  3. Device: Start → UI Settings → Visible Systems → Ports on.
  4. Start → Advanced Settings → Parse Gamelists Only → Off.
  5. Start → Game Settings → Update Gamelists. Reboot.

PortMaster autoinstall (CryMon-portmaster.zip)
----------------------------------------------
Same unpack-safe root. Drop in PortMaster autoinstall, or unzip into ports.

The aarch64 binary is the R36S build (RK3326, native 640×480, SDL2,
glibc 2.17). The device already has libSDL2. gptokeyb maps the pad:
A confirm, B back, Start party, Y/Select bag.

Flycast disc
------------
Copy gemwar-480p.cdi into your Flycast games folder.
VGA cable, HLE BIOS on, Full Framebuffer Emulation on,
Linear Interpolation off, Delay Frame Swapping off.

CryMon
======

Copy into Ports (CryMon-ports.zip)
----------------------------------
This is the zip to use on an R36S. Unzip, then copy ONLY:

  CryMon.sh
  crymon/

into the EXISTING ports folder (EASYROMS/ports or roms/ports).
Do not replace the ports folder. Do not delete PortMaster.
Do not copy XML files into ports.

If an older GEMWAR port is still installed, delete GEMWAR.sh and the
gemwar folder so you are not running the stale build.

If Ports vanished from the carousel:
  1. On the SD card, in ports, delete gamelist.xml and gameinfo.xml.
  2. Leave the PortMaster folder.
  3. Device: Start → UI Settings → Visible Systems → Ports on.
  4. Start → Advanced Settings → Parse Gamelists Only → Off.
  5. Start → Game Settings → Update Gamelists. Reboot.

PortMaster autoinstall (CryMon-portmaster.zip)
----------------------------------------------
Drop in PortMaster autoinstall. Do not unzip this one over ports.

The aarch64 binary is the R36S build (RK3326, native 640×480, SDL2,
glibc 2.17). The device already has libSDL2. gptokeyb maps the pad:
A confirm, B back, Start party, Y/Select bag.

Flycast disc
------------
Copy gemwar-480p.cdi into your Flycast games folder.
VGA cable, HLE BIOS on, Full Framebuffer Emulation on,
Linear Interpolation off, Delay Frame Swapping off.

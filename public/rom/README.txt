CryMon
======

Two downloads on the cart page:

  Copy into Ports  — CryMon-ports.zip  (R36S / PortMaster SDL2, 640×480)
  SNES             — CryMon.sfc        (Super Nintendo LoROM, 256×224)

Neither zip dumps XML into the ports folder.


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

The aarch64 binary is the R36S build (RK3326, native 640×480, SDL2,
glibc 2.17). The device already has libSDL2. gptokeyb maps the pad:
A confirm, B back, Start party, Y/Select bag. In-game text is 32px
(2× the old port); the web preview stays 16px.


SNES cart (CryMon.sfc)
----------------------
256 KB LoROM. Mode 1, 256×224. Load it in Snes9x, bsnes, or any SNES
core (including the R36S RetroArch SNES core).

  A / Start  — begin
  D-pad      — walk
  A          — talk / confirm
  Start      — party
  Select     — bag

Same story as the 640×480 cart: Max, Quillpup, the cottage, the veld.


Flycast disc
------------
Copy gemwar-480p.cdi into your Flycast games folder.
VGA cable, HLE BIOS on, Full Framebuffer Emulation on,
Linear Interpolation off, Delay Frame Swapping off.

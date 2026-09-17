CryMon — unzip into the existing Ports folder
=============================================

This zip will not hide Ports. It only contains:

  CryMon.sh
  crymon     (the folder)
  this readme

On the SD card, open the EXISTING ports folder (EASYROMS/ports or roms/ports).
Unzip these into that folder. Do not replace the ports folder itself.
Do not delete the PortMaster folder.

If an older GEMWAR port is still there, delete GEMWAR.sh and the gemwar folder
so you are not running the stale build.

If Ports vanished from the R36S carousel (from an older zip):
  1. Plug the SD card into a computer.
  2. In the ports folder, delete gamelist.xml and gameinfo.xml if they are there.
  3. Leave the PortMaster folder alone.
  4. On the device, Start → UI Settings → Visible Systems → turn Ports on.
  5. Start → Advanced Settings → Parse Gamelists Only → Off.
  6. Start → Game Settings → Update Gamelists.
  7. Reboot.

The firmware is not bricked. Ports is hidden when a dumped gamelist.xml is empty.

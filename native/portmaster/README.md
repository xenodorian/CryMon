## Notes

CryMon is a 640×480 tamer walk. Same game as the in-browser cart.

Drop this zip in PortMaster autoinstall. It includes `screenshot.png` and
`cover.png` at the zip root so PortMaster can show the game instead of a
broken image.

There is no `gameinfo.xml` / `gamelist.xml`. Unzipping this into ports will
not replace the Ports list. Extra files at the ports root (`port.json`,
`screenshot.png`, `cover.png`) are harmless; delete them if you want a clean
folder, or use CryMon-ports.zip which only has `CryMon.sh` and `crymon/`.

Never delete the PortMaster folder.

If Ports vanished from the carousel after an older zip: delete `gamelist.xml`
and `gameinfo.xml` from the ports folder, Start → UI Settings → Visible Systems
→ Ports on, Advanced Settings → Parse Gamelists Only off, Game Settings →
Update Gamelists.

If an older GEMWAR port is still installed, delete `GEMWAR.sh` and the `gemwar`
folder first.

## Thanks

Homebrew original. HUD font is a public-domain 8×8 bitmap.

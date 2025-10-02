# Yet Another Blue Archive Mod Manager
Its yet another blue archive mod manager, now on v0.1b1!

Whats new in v0.1b2:

- Changes mod detection system/restore system to allow any mod that is in the normal gamedata windows folder or preload windows folder.
- Fixes an issue with the mod updater that I wasn't aware of, specfically models not getting updated, and also updates to the fixed version of BA-Modding-Toolkit
to resolve the other issue with model updates.
- Added zh translation (Chinese)
- Fixed a lot of bugs, including most bugs 
- Lots of changes to UI to handle large file names better.
- Fixes the fact that v0.1b1 was completely broken, oops (pls dont be broken).

Whats next for v0.1b3:
 - Making the code more ~~less horrid~~ more friendly.
 - Perhaps add more translations.
 - Adding contribution menu in settings.

## Features:
 - Creates basic mod loading system
 - Backs up / Load original bundles 
 - Automatically patches CRC using the actual game's bundle file from Deathemonic [BA-CY](https://github.com/Deathemonic/BA-CY)
 - Update broken mods after major game update, from Agent-0808 [BA-Modding-Toolkit](https://github.com/Agent-0808/BA-Modding-Toolkit)
 - Renaming / managing mods
 - Chinese translation

Please feel free to make an issue to request a feature.

## Issues:
 - None i'm aware of, please report them if you encounter any.
Please feel free to make an issue to report a bug, this project is in beta after all.

## Goals:
 - Restructure the code to make it be more neat, and handle user error/cases better.
 - Allow having multiple mods of the same bundle and switch between them
 - Handle CRC patching/Updating mods when they are applied better (by using backup).
 - Preview images ? (Making the app wider to allow for this)
 - Support different languages (Japanese/Chinese)
 - Changing color theme


## Huge thanks:
 - Agent-0808: Updating mods with [BA-Modding-Toolkit](https://github.com/Agent-0808/BA-Modding-Toolkit)
 - Deathemonic: Patching CRC with [BA-CY](https://github.com/Deathemonic/BA-CY)

## Development:
<pre>
git clone https://github.com/kalinaowo/yet-another-blue-archive-mod-manager.git
cd yet-another-blue-archive-mod-manager
pip install -r requirements.txt
python newGUI.py
</pre>

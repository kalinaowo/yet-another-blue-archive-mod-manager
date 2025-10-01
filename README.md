# Yet Another Blue Archive Mod Manager
Its yet another blue archive mod manager, now on v0.1b1!

Whats new in v0.1b1:
 - Fixes a ton of bugs that were in previous versions
 - Finishes the UI mostly, will tweak it most likely however
 - Batch update/CRC patch.

## Features:
 - Creates basic mod loading system
 - Backs up / Load original bundles 
 - Automatically patches CRC using the actual game's bundle file
 - Update broken mods after major game update
 - Renaming / managing mods

Please feel free to make an issue to request a feature.

## Issues:
 - Translations will fail to download and bug out when disconnect from wifi when downloading.
 - S.Hanako L2D seems to have a weird edge case where the manager thinks its applied when its really not.
 - Fix reset name feature.

Please feel free to make an issue to report a bug, this project is in beta after all.

## Goals:
 - Restructure the code to make it be more neat, and handle user error/cases better.
 - Allow having multiple mods of the same bundle and switch between them
 - Handle CRC patching/Updating mods when they are applied better (by using backup).
 - Preview images ? (Making the app wider to allow for this)
 - Support different languages (Japanese/Chinese)
 - Changing color theme

## Development:
<pre>
git clone https://github.com/kalinaowo/yet-another-blue-archive-mod-manager.git
cd yet-another-blue-archive-mod-manager
pip install -r requirements.txt
python newGUI.py
</pre>
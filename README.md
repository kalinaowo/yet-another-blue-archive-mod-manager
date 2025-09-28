# Yet Another Blue Archive Mod Manager
its yet another blue archive mod manager

Currently switching from thkiner to webview because ~~thkiner sucks~~ thkiner is... interesting. Because of this applying mods doesn't work so far, sorry about that, will be fixed soon

## Features:
 - Creates basic mod loading system
 - Backs up / Load original bundles 
 - Automatically patches CRC using the actual game's bundle file

## Issues:
 - If mods are applied after they have been applied already, CRC may applied more then once.

## Goals:
 - Maybe automatically updates mods if they break
 - Detect old mods that use an outdated spine version (this probably cannot be fixed however)
 - Add support for sounds/video assets

## Development:

Old Version:
<pre>
git clone https://github.com/kalinaowo/yet-another-blue-archive-mod-manager.git
cd yet-another-blue-archive-mod-manager
python -m pip install ttkbootstrap
python GUI.py
</pre>

New Version:
<pre>
git clone https://github.com/kalinaowo/yet-another-blue-archive-mod-manager.git
cd yet-another-blue-archive-mod-manager
python -m pip install webview  
python newGUI.py
</pre>

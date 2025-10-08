import webview
import os
import utils.modClass as modClass
import utils.Storage as Storage
import json
import base64
import gettext
from assets import HTMLTranslations

window = None
modObjects = None
LANGUAGE = "en"

DOMAIN = 'messages' 
LOCALE_DIR = os.path.join(os.path.dirname(__file__), 'locales')

def set_language(lang_code):
    try:
        translation = gettext.translation(
            domain=DOMAIN,
            localedir=LOCALE_DIR,
            languages=[lang_code],
            fallback=True
        )
    except FileNotFoundError:
        translation = gettext.NullTranslations()
    translation.install()
set_language(LANGUAGE)

import builtins
global _
_ = builtins._

class modLoading:
    def loadMod(self, PATH):
        return self.loadMods(PATH)
    
    def loadMods(self, MOD_PATH):
        global modObjects
        modObjects = []
        if MOD_PATH == "mod" and not os.path.exists(MOD_PATH):
            os.mkdir(MOD_PATH)
        if not os.path.exists(MOD_PATH):
            addLog(_("Invalid Path"))
            return "Invalid Mod Path!"
        
        modClass.MOD_DIRECTORY = MOD_PATH
        Storage.loadData()
        files = os.listdir(MOD_PATH)
        validMods = 0
        invalidMods = 0
        for x in files:
            newMod = modClass.mod(x)
            if not newMod.isValid:
                if x != "backup" and x != "desktop.ini" and x != "mod_data.json" and x != "student_names.json":
                    invalidMods += 1
                    addLog(_("Failed to load mod with path: ") + str(x))
                continue
            validMods += 1
            modObjects.append(newMod)
        addLog(_("Loading completed! Mods loaded successfully: ") + str(validMods) + "/" + str(invalidMods+validMods))
        self.sendModNames()
        Storage.addData("mod_path", MOD_PATH)
        return _("Mods loaded: ") + str(validMods) + "/" + str(invalidMods+validMods)
    
    def sendModNames(self):
        modNames = []
        for x in modObjects:
            modNames.append(x.modName)
        window.evaluate_js(f"displayAllMods({json.dumps(modNames)})")

    def openFilePicker(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        result = webview.windows[0].create_file_dialog(
            webview.FOLDER_DIALOG,
            directory=base_dir
        )
        if result:
            return result
        else:
            return ""
        
    def deleteMod(self, id):
        modObjects[id].deleteMod()
        modObjects.remove(modObjects[id])
        self.sendModNames()

    def changeModName(self, newModName, id):
        modObjects[id].changeModName(newModName)
        window.evaluate_js("cancelRenameMod()")
        
    
    def getModDetails(self, id):
        details = []
        details.append(modObjects[id].modName)
        details.append(modObjects[id].modActualName)
        details.append(modObjects[id].isApplied)
        return details
    
    def applyMod(self, modOptions):
        successfulApplications = 0
        failedApplications = 0
        applicationStatus = []
        for i, x in enumerate(modOptions):
            applyThisMod = False
            if x == "On" or x == "在":
                applyThisMod = True
            
            if applyThisMod:
                addLog("-----")
                status = modObjects[i].backupRealBundle()
                if status == -1:
                    addLog(_("A error occured when backing up mod ") + modObjects[i].modName + _(", mod will not be applied..."))
                    failedApplications+=1
                    applicationStatus.append("Fail")
                    continue
                elif status == 1:
                    addLog(_("Successfully backed up mod: ") + modObjects[i].modName)
                else:
                    addLog(_("Backup already exists for mod: ") + modObjects[i].modName)
                status = modObjects[i].patchCRC()
                if status == -2:
                    addLog(_("It seems like the mod has already been applied, skipping patching and mod application to avoid corruption") + modObjects[i].modName)
                    failedApplications+=1
                    applicationStatus.append("Fail")
                    continue
                elif status == -1:
                    addLog(_("A error occured when applying the CRC for mod ") + modObjects[i].modName)
                    failedApplications+=1
                    applicationStatus.append("Fail")
                    continue
                else:
                    addLog(_("Successfully patched CRC for mod ") + modObjects[i].modName)
                status = modObjects[i].applyMod()
                if status == -1:
                    addLog(_("A error occured when applying mod ") + modObjects[i].modName + _(", backup will be automatically restored."))
                    applicationStatus.append("Fail")
                    modObjects[i].restoreOriginalBundle()
                    failedApplications+=1
                    continue
                addLog(_("Mod ") + modObjects[i].modName + _(" successfully applied!"))
                applicationStatus.append("Success")
                successfulApplications+=1
                modObjects[i].isApplied = True
        addLog("=====")
        addLog(_("Finished applying mods, amount successful: ") + str(successfulApplications) + "/" + str(failedApplications+successfulApplications))
        addLog("=====")
        return applicationStatus
    
    def restoreSelectedMods(self, modOptions):
        successfulApplications = 0
        failedApplications = 0
        applicationStatus = []
        for i, x in enumerate(modOptions):
            applyThisMod = False
            if x == "On" or x == "在":
                applyThisMod = True
            if applyThisMod:
                if not modObjects[i].isApplied:
                    failedApplications+=1
                    applicationStatus.append(_("Fail"))
                    continue
                status = modObjects[i].restoreOriginalBundle()
                if status == -1:
                    addLog(_("Mod ") + modObjects[i].modName + _(" cannot be restored, no backup files found! You can verifiy integrity of game files in Steam to obtain the original bundle file (all mods will be removed however.)"))
                    failedApplications+=1
                    applicationStatus.append(_("Fail"))
                    continue
                else:
                    addLog(_("Mod ") + modObjects[i].modName + _(" successfully restored!"))
                successfulApplications+=1
                applicationStatus.append("Success")
        addLog("=====")
        addLog(_("Finished restoring mods, amount successful: ") + str(successfulApplications) + "/" + str(failedApplications+successfulApplications))
        addLog("=====")
        return applicationStatus
    
    def patchCRC(self, modID):
        status = modObjects[modID].patchCRC()
        if status == -2:
            addLog(_("CRC patch for mod ") + modObjects[modID].modName + _(" failed, mod is applied and a CRC patch may corrupt the CRC"))
        elif status == -1:
            addLog(_("CRC patch for mod ") + modObjects[modID].modName + _(" failed, an error occured."))
        else:
            addLog(_("Successfully applied patch for mod ") + modObjects[modID].modName)

    def recieveFileData(self, fileData):
        for x in fileData:
            if modClass.isValidModName(x["name"]):
                try:
                    data = ""
                    with open(os.path.join(modClass.MOD_DIRECTORY,x["name"]), "w", encoding="utf-8") as out:
                        data = x["data"]
                    try:
                        data_bytes = base64.b64decode(data)
                        output_path = os.path.join(modClass.MOD_DIRECTORY, x["name"])
                        with open(output_path, "wb") as f:
                            f.write(data_bytes)
                    except Exception as e:
                        print(e)
                    newMod = modClass.mod(x["name"])
                    if not newMod.isValid:
                        addLog(_("The file with path ") + x["name"] + _(" does not appear to be a valid mod!"))
                        os.remove(os.path.join(modClass.MOD_DIRECTORY,x["name"]))
                        continue
                    modObjects.append(newMod)
                    addLog(_("Successfully added mod ") + str(newMod.modName))
                except Exception as e:
                    print(e)
                    addLog(_("An error ocurred when processing file: ") + str(x["name"]))
            else:
                addLog(_("The file with path ") + x["name"] + _(" does not appear to be a valid mod!"))
        self.sendModNames()

    def updateMod(self, id):
        addLog(_("Starting mod update for ") + modObjects[id].modName + _("..., this may take some time."))
        response = modObjects[id].updateMod()  
        if response[0]:
            addLog(_("Mod update for ") + str(modObjects[id].modName) + _(" was successsful!"))
        else:
            addLog(_("Mod update for ") + str(modObjects[id].modName) + _(" had failed."))
            addLog(response[1])
    
    def submitGameDir(self, newDir):
        if not os.path.exists(newDir):
            addLog(_("New game directory path does not exist!"))
            return
        
        if not os.path.exists(os.path.join(newDir,"BlueArchive.exe")):
            addLog(_("This folder does not seem to contain Blue Archive! Please add the folder with BlueArchive.exe"))
            return
        
        modClass.GAME_LOCATION = newDir
        Storage.addData("default_game_directory", newDir)
        addLog(_("Updated game directory!"))
    
    def updateAllMods(self):
        successful = 0
        unsuccessful = 0
        for x in modObjects:
            addLog(_("Updating all mods, this make take a while, do not close the window."))
            response = x.updateMod()  
            if response[0]:
                addLog(_("Mod update for ") + str(x.modName) + _(" was successsful!"))
                successful+=1
            else:
                addLog(_("Mod update for ") + str(x.modName) +_( " had failed."))
                addLog(response[1])
                unsuccessful+=1
        addLog(_("Finished updating all mods. Successful updates: ") + str(successful) + "/" + str(unsuccessful+successful))

    def patchAllMods(self):
        successful = 0
        unsuccessful = 0
        for x in modObjects:
            addLog(_("Patching all mods..."))
            response = x.patchCRC()  
            if response == 1:
                addLog(_("Patch for ") + str(x.modName) + _(" was successsful!"))
                successful+=1
            else:
                addLog(_("Patch for " + str(x.modName) + _(" had failed.")))
                unsuccessful+=1
        addLog(_("Finished patching all mods. Successful patches: ") + str(successful) + "/" + str(unsuccessful+successful))
    
    def deleteTranslations(self):
        Storage.deleteTranslations()
        if not os.path.exists("student_names.json"):
            addLog(_("Deleted the mod translations, they will be reacquired the next time a path is loaded."))
        else:
            addLog(_("Something went wrong deleting the mod translations."))
        

    def deleteAllModData(self):
        Storage.deleteStorage()
        if not os.path.exists("mod_data.json"):
            addLog(_("Finished resetting the mod manager!"))
        else:
            addLog(_("Something went wrong resetting the mod manager."))
        self.loadMods(modClass.MOD_DIRECTORY)
        self.sendModNames()

    def resetModName(self, id):
        Storage.deleteModName(modObjects[id].modPath)
        self.loadMods(modClass.MOD_DIRECTORY)
        self.sendModNames()


html_data = Storage.load_ui_asset()

Storage.loadData()
storagePath = Storage.retrieveData("mod_path")
if storagePath == None:
    storagePath = "mod"

gameDir = Storage.retrieveData("default_game_directory")
if gameDir != None:
    modClass.GAME_LOCATION = gameDir

html_data = html_data.replace(r"mod\\", storagePath)
html_data = html_data.replace(r"-defaultGameDir-", modClass.GAME_LOCATION)

toReplace = 0
if LANGUAGE == "zh":
    toReplace = 1
for x in HTMLTranslations.translations:
    html_data = html_data.replace(x, HTMLTranslations.translations[x][toReplace])

def main():
    global window
    modManagerBackend = modLoading()
    window = webview.create_window("Yet Another Blue Archive Mod Manager", html=html_data, js_api=modManagerBackend, width=800, height=800, resizable=False)
    webview.start()

def addLog(log):
    global window
    window.evaluate_js(f"addLog('{log}')")


def on_resized(window, width, height):
    current_ratio = width / height
    if abs(current_ratio - 1) > 0.01:
        if current_ratio > 1:
            new_width = int(height)
            window.resize(new_width, height)
        else:
            new_height = int(width)
            window.resize(width, new_height)

if __name__ == "__main__":
    main()
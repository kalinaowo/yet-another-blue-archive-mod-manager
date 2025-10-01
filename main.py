import webview
import os
import modClass
import Storage
import json
import time
import base64

window = None
modObjects = None

class modLoading:
    def loadMod(self, PATH):
        return self.loadMods(PATH)
    
    def loadMods(self, MOD_PATH):
        global modObjects
        modObjects = []
        if MOD_PATH == "mod" and not os.path.exists(MOD_PATH):
            os.mkdir(MOD_PATH)
        if not os.path.exists(MOD_PATH):
            addLog("Invalid Path")
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
                    addLog("Failed to load mod with path: " + str(x))
                continue
            validMods += 1
            modObjects.append(newMod)
        addLog("Loading completed! Mods loaded successfully: " + str(validMods) + "/" + str(invalidMods+validMods))
        self.sendModNames()
        Storage.addData("mod_path", MOD_PATH)
        return "Mods loaded: " + str(validMods) + "/" + str(invalidMods+validMods)
    
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
        print("DELETE SENT")
        modObjects[id].deleteMod()
        modObjects.remove(modObjects[id])
        self.sendModNames()

    def changeModName(self, newModName, id):
        print(newModName)
        modObjects[id].changeModName(newModName)
        window.evaluate_js("cancelRenameMod()")
        
    
    def getModDetails(self, id):
        details = []
        details.append(modObjects[id].modName)
        details.append(modObjects[id].modActualName)
        details.append(modObjects[id].isApplied)
        return details
    
    def applyMod(self, modOptions):
        print(modOptions)
        successfulApplications = 0
        failedApplications = 0
        applicationStatus = []
        for i, x in enumerate(modOptions):
            print(i)
            applyThisMod = False
            if x == "On":
                applyThisMod = True
            
            if applyThisMod:
                addLog("-----")
                status = modObjects[i].backupRealBundle()
                if status == -1:
                    addLog("A error occured when backing up mod " + modObjects[i].modName + ", mod will not be applied...")
                    failedApplications+=1
                    applicationStatus.append("Fail")
                    continue
                elif status == 1:
                    addLog("Successfully backed up mod: " + modObjects[i].modName)
                else:
                    addLog("Backup already exists for mod: " + modObjects[i].modName + " skipping backup creation.")
                status = modObjects[i].patchCRC()
                if status == -2:
                    addLog("CRC patch cannot be applied for mod: " + modObjects[i].modName + ", it seems like the mod has already been applied, skipping mod application to avoid CRC corruption")
                    failedApplications+=1
                    applicationStatus.append("Fail")
                    continue
                elif status == -1:
                    addLog("A error occured when applying the CRC for mod " + modObjects[i].modName + ".")
                    failedApplications+=1
                    applicationStatus.append("Fail")
                    continue
                else:
                    addLog("Successfully patched CRC for mod " + modObjects[i].modName)
                status = modObjects[i].applyMod()
                if status == -1:
                    addLog("A error occured when applying mod " + modObjects[i].modName + ", backup will be automatically restored.")
                    applicationStatus.append("Fail")
                    modObjects[i].restoreOriginalBundle()
                    failedApplications+=1
                    continue
                addLog("Mod " + modObjects[i].modName + " successfully applied!")
                applicationStatus.append("Success")
                successfulApplications+=1
                modObjects[i].isApplied = True
        addLog("=====")
        addLog("Finished applying mods, amount successful: " + str(successfulApplications) + "/" + str(failedApplications+successfulApplications))
        addLog("=====")
        return applicationStatus
    
    def restoreSelectedMods(self, modOptions):
        print(modOptions)
        successfulApplications = 0
        failedApplications = 0
        applicationStatus = []
        for i, x in enumerate(modOptions):
            applyThisMod = False
            if x == "On":
                applyThisMod = True
            if applyThisMod:
                status = modObjects[i].restoreOriginalBundle()
                if status == -1:
                    addLog("Mod " + modObjects[i].modName + " cannot be restored, no backup files found! You can verifiy integrity of game files in Steam to obtain the original bundle file (all mods will be removed however.)")
                    failedApplications+=1
                    applicationStatus.append("Restore Fail")
                    continue
                else:
                    addLog("Mod " + modObjects[i].modName + " successfully restored!")
                successfulApplications+=1
                applicationStatus.append("Success")
        addLog("=====")
        addLog("Finished restoring mods, amount successful: " + str(successfulApplications) + "/" + str(failedApplications+successfulApplications))
        addLog("=====")
        return applicationStatus
    
    def patchCRC(self, modID):
        status = modObjects[modID].patchCRC()
        if status == -2:
            addLog("CRC patch for mod " + modObjects[modID].modName + " failed, mod is applied and a CRC patch may corrupt the CRC")
        elif status == -1:
            addLog("CRC patch for mod " + modObjects[modID].modName + " failed, an error occured.")
        else:
            addLog("Successfully applied patch for mod " + modObjects[modID].modName)

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
                        print(output_path)
                        with open(output_path, "wb") as f:
                            f.write(data_bytes)
                    except Exception as e:
                        print("Error processing file: "+ str(e))
                    newMod = modClass.mod(x["name"])
                    if not newMod.isValid:
                        addLog("The file with path " + x["name"] + " does not appear to be a valid mod!")
                        os.remove(os.path.join(modClass.MOD_DIRECTORY,x["name"]))
                        continue
                    modObjects.append(newMod)
                    addLog("Successfully added mod " + str(newMod.modName))
                except Exception as e:
                    print(e)
                    addLog("An error ocurred when processing file: " + str(x["name"]))
            else:
                addLog("The file with path " + x["name"] + " does not appear to be a valid mod!")
        self.sendModNames()

    def updateMod(self, id):
        addLog("Starting mod update for " + modObjects[id].modName + "..., this may take some time.")
        response = modObjects[id].updateMod()  
        if response[0]:
            addLog("Mod update for " + str(modObjects[id].modName) + " was successsful!")
        else:
            addLog("Mod update for " + str(modObjects[id].modName) + " had failed.")
            addLog(response[1])
    
    def submitGameDir(self, newDir):
        if not os.path.exists(newDir):
            addLog("New game directory path does not exist!")
            return
        
        if not os.path.exists(os.path.join(newDir,"BlueArchive.exe")):
            addLog("This folder does not seem to contain Blue Archive! Please add the folder with BlueArchive.exe")
            return
        
        modClass.GAME_LOCATION = newDir
        Storage.addData("default_game_directory", newDir)
        addLog("Updated game directory!")
    
    def updateAllMods():
        successful = 0
        unsuccessful = 0
        for x in modObjects:
            addLog("Updating all mods, this make take a while, do not close the window.")
            response = modObjects[id].updateMod()  
            if response[0]:
                addLog("Mod update for " + str(modObjects[id].modName) + " was successsful!")
                successful+=1
            else:
                addLog("Mod update for " + str(modObjects[id].modName) + " had failed.")
                addLog(response[1])
                unsuccessful+=1
            addLog("Finished updating all mods. Successful updates: " + str(successful) + "/" + str(unsuccessful+successful))

    def patchAllMods(self):
        successful = 0
        unsuccessful = 0
        for x in modObjects:
            addLog("Patching all mods...")
            response = modObjects[id].updateMod()  
            if response[0]:
                addLog("Patch for " + str(modObjects[id].modName) + " was successsful!")
                successful+=1
            else:
                addLog("Patch for " + str(modObjects[id].modName) + " had failed.")
                addLog(response[1])
                unsuccessful+=1
            addLog("Finished patching all mods. Successful patches: " + str(successful) + "/" + str(unsuccessful+successful))
    
    def deleteTranslations(self):
        Storage.deleteTranslations()
        if not os.path.exists("student_names.json"):
            addLog("Deleted the mod translations, they will be reacquired the next time a path is loaded.")
        else:
            addLog("Something went wrong deleting the mod translations.")
        

    def deleteAllModData(self):
        Storage.deleteStorage()
        if not os.path.exists("mod_data.json"):
            addLog("Finished resetting the mod manager!")
        else:
            addLog("Something went wrong resetting the mod manager.")
        self.loadMods(modClass.MOD_DIRECTORY)
        self.sendModNames()



base_path = os.path.dirname(__file__)
with open(os.path.join(base_path, "assets", "index.html"), encoding="utf-8") as f:
    html_data = f.read()

Storage.loadData()
storagePath = Storage.retrieveData("mod_path")
if storagePath == None:
    storagePath = "mod"

gameDir = Storage.retrieveData("default_game_directory")
if gameDir != None:
    modClass.GAME_LOCATION = gameDir

html_data = html_data.replace(r"mod\\", storagePath)
html_data = html_data.replace(r"-defaultGameDir-", modClass.GAME_LOCATION)

def main():
    global window
    modManagerBackend = modLoading()
    window = webview.create_window("My App", html=html_data, js_api=modManagerBackend, width=800, height=800)
    window.events.resized += on_resized
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

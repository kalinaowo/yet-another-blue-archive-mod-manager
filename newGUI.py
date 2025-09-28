import webview
import os
import modClass
import Storage
import json

window = None
modObjects = None

class modLoading:
    def loadMod(self, PATH):
        return self.loadMods(PATH)
    
    def loadMods(self, MOD_PATH):
        global modObjects
        modObjects = []
        if not os.path.exists(MOD_PATH):
            addLog("Invalid Path")
            return "Invalid Mod Path!"
        
        modClass.MOD_DIRECTORY = MOD_PATH
        Storage.loadData(modClass.MOD_DIRECTORY)
        files = os.listdir(MOD_PATH)
        validMods = 0
        invalidMods = 0
        for x in files:
            newMod = modClass.mod(x)
            if not newMod.isValid:
                if x != "backup" and x != "desktop.ini" and x != "modData.json":
                    invalidMods += 1
                    addLog("Failed to load mod with path: " + str(x))
                continue
            validMods += 1
            modObjects.append(newMod)
        addLog("Loading completed! Mods loaded successfully: " + str(validMods) + "/" + str(invalidMods+validMods))
        self.sendModNames()
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

    def changeModName(self, newModName, id):
        print(newModName)
        modObjects[id].changeModName(newModName)
        window.evaluate_js("cancelRenameMod()")
        

base_path = os.path.dirname(__file__)
with open(os.path.join(base_path, "assets", "index.html"), encoding="utf-8") as f:
    html_data = f.read()

def main():
    global window
    modManagerBackend = modLoading()
    window = webview.create_window("My App", html=html_data, js_api=modManagerBackend)
    webview.start()

def addLog(log):
    global window
    window.evaluate_js(f"addLog('{log}')")

if __name__ == "__main__":
    main()

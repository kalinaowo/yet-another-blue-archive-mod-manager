import json
import os

modData = {
    "mods": {
        
    },
    "defaultModDir" : "\\mod"
}

def loadData(MOD_DIRECTORY):
    global modData
    print(os.path.exists(MOD_DIRECTORY+"\\modData.json"))
    if os.path.exists(MOD_DIRECTORY+"\\modData.json"):
        with open(MOD_DIRECTORY+"\\modData.json", 'r') as f:
            modData = json.loads(f.read())
    else:
        saveDataFile(MOD_DIRECTORY)

def saveDataFile(MOD_DIRECTORY):
    with open(MOD_DIRECTORY+"\\modData.json", 'w') as f:
        f.write(json.dumps(modData))

def writeNewModName(modPath, newModName, MOD_DIRECTORY):
    modData["mods"][modPath] = {"name": newModName}
    saveDataFile(MOD_DIRECTORY)
    loadData(MOD_DIRECTORY)

def retrieveModName(modPath):
    try:
        return modData["mods"][modPath]["name"]
    except:
        return -1

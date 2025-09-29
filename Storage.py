import json
import os
import requests

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

def downloadNameTranslations(MOD_DIRECTORY):
    print("Downloading Name Translations...")
    save_path = MOD_DIRECTORY+"\\student_names.json"

    resp = requests.get("https://schaledb.com/data/en/students.json")
    resp.raise_for_status()

    print("Formatting Name Translations...")
    data = json.loads(resp.content)
    constructedNames = {}

    for obj in data.values():
        constructedNames[obj["DevName"].lower()] = {"name": obj["Name"]}
    constructedNames["file_data"] = {"version": 1}
    print("Saving Name Translations...")
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(constructedNames))

def retrieveCharacterNameTranslations(char_path, MOD_DIRECTORY):
    orgChar = char_path
    save_path = MOD_DIRECTORY+"\\student_names.json"

    if not os.path.exists(save_path):
        downloadNameTranslations(MOD_DIRECTORY)
    
    with open(save_path, "r", encoding="utf-8") as f:
        translations = json.loads(f.read())
    modType = " model"
    if char_path.endswith("_spr"):
        modType = " sprite"
        char_path = char_path[:-4]
    elif char_path.endswith("_home"):
        modType = " L2D"
        char_path = char_path[:-5]
    try:
        return translations[char_path]["name"]+modType
    except Exception as e:
        print("Error when translating mod name " + str(char_path) + ", " + str(e))
        return char_path.replace("_", " ").title()+modType
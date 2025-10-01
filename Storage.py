import json
import os
import requests
import sys


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
        
    return os.path.join(base_path, relative_path)

modData = {
    "mods": {},
    "defaultModDir" : "\\mod"
}

def load_ui_asset():
    try:
        file_path = resource_path(os.path.join("assets", "index.html"))
        
        with open(file_path, encoding="utf-8") as f:
            html_data = f.read()
            return html_data

    except FileNotFoundError as e:
        print("Big error, can't load index.html")
        print(e)
        sys.exit(1)


def loadData():
    global modData
    if os.path.exists("mod_data.json"):
        with open("mod_data.json", 'r') as f:
            modData = json.loads(f.read())
    else:
        saveDataFile()

def saveDataFile():
    with open("mod_data.json", 'w') as f:
        f.write(json.dumps(modData))

def writeNewModName(modPath, newModName):
    modData["mods"][modPath] = {"name": newModName}
    saveDataFile()
    loadData()

def retrieveModName(modPath):
    try:
        return modData["mods"][modPath]["name"]
    except:
        return -1
    
def addData(key, contents):
    modData[key] = contents
    print(modData[key])
    saveDataFile()

def retrieveData(key):
    try:
        return modData[key]
    except:
        return None

def downloadNameTranslations():
    print("Downloading Name Translations...")
    save_path = "student_names.json"

    try:
        resp = requests.get("https://schaledb.com/data/en/students.json")
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error downloading name translations: {e}")
        return

    print("Formatting Name Translations...")
    data = json.loads(resp.content)
    constructedNames = {}

    for obj in data.values():
        constructedNames[obj["DevName"].lower()] = {"name": obj["Name"]}
    constructedNames["file_data"] = {"version": 1}
    print("Saving Name Translations...")
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(constructedNames))

def retrieveCharacterNameTranslations(char_path):
    orgChar = char_path
    save_path = "student_names.json"

    if not os.path.exists(save_path):
        downloadNameTranslations()
    
    modType = " model"
    if char_path.endswith("_spr"):
        modType = " sprite"
        char_path = char_path[:-4]
    elif char_path.endswith("_home"):
        modType = " L2D"
        char_path = char_path[:-5]

    if not os.path.exists(save_path):
        return char_path.replace("_", " ").title()+modType

    with open(save_path, "r", encoding="utf-8") as f:
        translations = json.loads(f.read())
        
    try:
        return translations[char_path]["name"]+modType
    except Exception as e:
        print("Error when translating mod name " + str(char_path) + ", " + str(e))
        return char_path.replace("_", " ").title()+modType

def deleteTranslations():
    if os.path.exists("student_names.json"):
        os.remove("student_names.json")

def deleteStorage():
    global modData
    if os.path.exists("mod_data.json"):
        os.remove("mod_data.json")
    modData = {
        "mods": {},
        "defaultModDir" : "\\mod"
    }
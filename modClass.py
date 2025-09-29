import os
import CRC_tool
import shutil
import Storage
import requests
import json

MOD_DIRECTORY = "\\..\\BA Mod Manager\\mod"
GAME_LOCATION = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\BlueArchive"
PRELOAD_LOCATION = "BlueArchive_Data\\StreamingAssets\\PUB\\Resource\\Preload\\Windows"
DEFAULT_LOCATION = "BlueArchive_Data\\StreamingAssets\\PUB\\Resource\\GameData\\Windows"
MOD_BACKUP_LOCATION = MOD_DIRECTORY+"\\backup"
DATABASE_URL = "https://schaledb.com/data/en/students.json"

class mod():
    modName = ""
    modActualName = ""
    modPath = ""
    modType = ""
    prologdepengroup = False
    isValid = False
    CRCPatched = False
    realPath = ""
    isApplied = False

    def __init__(self, modL):
        self.modPath = modL
        self.__getInformation()

    def __getInformation(self):
        if self.modPath.startswith("assets-_mx-"):
            self.isValid = True
        elif self.modPath.startswith("prologdepengroup-assets-_mx-"):
            self.isValid = True
            self.prologdepengroup = True

        if self.isValid != True:
            self.modType = "None"
            self.modName = "Unknown"
            return

        strippedModString = ""
        if self.prologdepengroup == False:
            strippedModString = self.modPath[11:]
        else:
            strippedModString = self.modPath[28:]

        self.modType = strippedModString.split("-")[0]
        self.modName = strippedModString.split("-")[1]
        self.modActualName = self.modName

        self.CRCPatched = self.__checkCRCPatch()

        self.stripTrailingDigits()
        self.__obtainRealBundlePath()

        self.isApplied = self.__checkCRCPatch(self.realPath)

        self.modName = Storage.retrieveCharacterNameTranslations(self.modName, MOD_DIRECTORY)
        modName = Storage.retrieveModName(self.modPath)
        if modName != -1:
            self.modName = modName

    def __obtainRealBundlePath(self):
        prefix = self.modPath.split(".")[0]
        modLocation = GAME_LOCATION+"\\"

        if self.prologdepengroup:
            modLocation += PRELOAD_LOCATION
        else:
            modLocation += DEFAULT_LOCATION

        match = next((x for x in os.listdir(modLocation) if x.startswith(prefix)), None)
        if match == None:
            self.isValid = False
            return
        else:
            self.realPath = modLocation+"\\"+match

    def remove_CRCPatch(self):
        with open(MOD_DIRECTORY+"\\"+self.modPath, "rb+") as f:
            f.seek(0, 2)
            size = f.tell()
            f.truncate(size - 4)    
            
            self.CRCPatched = self.__checkCRCPatch() 

    def patchCRC(self):
        if self.isApplied:
            print("Cannot patch CRC, the mod is currently applied.")
            return -2

        if self.CRCPatched == True:
            print("Removed CRC Patch")
            self.remove_CRCPatch()
        try:
            CRC_tool.manipulate_crc(self.realPath, MOD_DIRECTORY+"\\"+self.modPath)
        except Exception as e:
            print("A error occured when applying CRC for mod: " + str(self.modName) + ", " + str(e))
            return -1
        self.CRCPatched = self.__checkCRCPatch() 
        return 1
    
    def __checkCRCPatch(self, path = ""):
        if path == "":
            path = MOD_DIRECTORY+"\\"+self.modPath
        with open(path, "rb") as f:
            f.seek(-1, 2)  
            last_byte = f.read(1)
            if not last_byte:
                return False  
            value = last_byte[0]
            last4 = value & 0b1111

            return last4 != 0

    def toString(self):
        print("Mod Name: " + str(self.modName))
        print("Mod Path: " + str(self.modPath))
        print("Mod Type: " + str(self.modType))
        print("Prologdepengroup?: " + str(self.prologdepengroup))
        print("Is Valid?: " + str(self.isValid))
        print("Is CRC patched?: " + str(self.CRCPatched))
        print("Real bundle path: " + str(self.realPath))

    def backupRealBundle(self):
        backup_path = MOD_DIRECTORY + "\\backup"
        if not os.path.exists(backup_path):
            os.mkdir(backup_path)
            print("Created backup folder")
        if os.path.exists(backup_path+"\\"+(self.realPath.split("\\")[-1])):
            print("Backup for " + str(self.modName) + " exists, skipping...")
            return 0
        try:
            shutil.copyfile(self.realPath, backup_path+"\\"+(self.realPath.split("\\")[-1]))
        except Exception as e:
            print("A error occured when backing up file: " + str(self.modName) + ", " + str(e))
            return -1
        print("Successfully backed up bundle files for " + str(self.modName))
        return 1
    
    def applyMod(self):
        if os.path.exists(self.realPath):
            os.remove(self.realPath)
        try:
            print(MOD_DIRECTORY+"\\"+self.modPath, self.realPath)
            shutil.copyfile(MOD_DIRECTORY+"\\"+self.modPath, self.realPath)
            print("Successfully applied mod for " + str(self.modName))
            return 1
        except Exception as e:
            print("A error occured when applying mod: " + str(self.modName) + ", " + str(e))
            return -1

    def restoreOriginalBundle(self):
        backup_path = MOD_DIRECTORY + "\\backup"
        
        if not os.path.exists(backup_path+"\\"+(self.realPath.split("\\")[-1])):
            print("No backup file found! You can Verify integiry of game files in Steam to obtain the original bundle, (it will remove all mods).")
            return -1

        if os.path.exists(self.realPath):
            os.remove(self.realPath)

        shutil.copyfile(backup_path+"\\"+(self.realPath.split("\\")[-1]), self.realPath)
        print("Original bundle restored for " + str(self.modName))
        return 1
    
    def stripTrailingDigits(self):
        if self.modPath.split(".")[0].split("_")[-1].isnumeric():
            os.rename(MOD_DIRECTORY+"\\"+self.modPath, MOD_DIRECTORY+"\\"+self.modPath[:-17]+".bundle")
            self.modPath = self.modPath[:-17]+".bundle"
    
    def deleteMod(self):
        if self.isApplied:
            self.restoreOriginalBundle()
        try:
            os.remove(MOD_DIRECTORY+"\\"+self.modPath)
            return 1
        except:
            return -1
    
    def changeModName(self, newName):
        Storage.writeNewModName(self.modPath, newName, MOD_DIRECTORY)
        self.modName = newName

def isValidModName(name):
    return name.startswith("assets-_mx-") or name.startswith("prologdepengroup-assets-_mx-")
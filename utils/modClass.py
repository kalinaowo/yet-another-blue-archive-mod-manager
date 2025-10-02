import os
import utils.CRC_tool as CRC_tool
import shutil
import utils.Storage as Storage
import utils.BA_Modding_Tools.mainUpdater as mainUpdater

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
        self.__validateMod()

        if self.isValid != True:
            self.modType = "None"
            self.modName = "Unknown"
            return

        strippedModString = ""
        if self.prologdepengroup == False:
            strippedModString = self.modPath[11:]
        else:
            strippedModString = self.modPath[28:]

        self.__determineNameAndType()
        self.modActualName = self.modName

        self.CRCPatched = self.__checkCRCPatch()
        self.__obtainRealBundlePath()

        if self.modPath != "":
            self.isApplied = Storage.getIsModApplied(self.modPath)

        self.modName = Storage.retrieveCharacterNameTranslations(self)

        modName = -1
        modName = Storage.retrieveModName(self.modPath)
        
        if modName != -1:
            self.modName = modName
        self.fixNaming()
    
    def __validateMod(self):
        preload_full = os.path.join(GAME_LOCATION, PRELOAD_LOCATION)
        default_full = os.path.join(GAME_LOCATION, DEFAULT_LOCATION)

        if os.path.exists(os.path.join(preload_full,self.modPath)):
            self.isValid = True
            self.prologdepengroup = True
        elif os.path.exists(os.path.join(default_full,self.modPath)):
            self.isValid = True
    
    def __determineNameAndType(self):
        
        strippedModString = ""
        if self.prologdepengroup == False:
            if self.modPath.startswith("assets-"):
                strippedModString = self.modPath[11:]
                self.modType = strippedModString.split("-")[0]
                self.modName = strippedModString.split("-")[1]
            else:
                self.modType = "other_mod"
                self.modName = self.modPath


        else:
            if self.modPath.startswith("prologdepengroup-assets-"):
                strippedModString = self.modPath[29:]
                self.modType = strippedModString.split("-")[0]
                self.modName = strippedModString.split("-")[1]
            elif self.modPath.startswith("prologgroup-assets-"):
                strippedModString = self.modPath[23:]
                self.modType = strippedModString.split("-")[0]
                self.modName = strippedModString.split("-")[1]

            
            if self.modPath.startswith("packages-"):
                strippedModString = self.modPath[9:]
                self.modType = strippedModString.split("-")[0]
                self.modName = strippedModString.split("-")[1]
        
    def fixNaming(self):
        if not self.isValid:
            return
        prefix = self.modPath.split(".")[0]
        modLocation = GAME_LOCATION

        if self.prologdepengroup:
            modLocation = os.path.join(modLocation,PRELOAD_LOCATION)
        else:
            modLocation = os.path.join(modLocation,DEFAULT_LOCATION)

        match = next((x for x in os.listdir(modLocation) if x.startswith(prefix)), None)
        if self.modPath!=match:
            print(MOD_DIRECTORY+"\\"+self.modPath,MOD_DIRECTORY+"\\"+match)
            try:
                os.rename(MOD_DIRECTORY+"\\"+self.modPath,MOD_DIRECTORY+"\\"+match)
                self.modPath = match
            except:
                print("Error in mod name fixing.")

    def __obtainRealBundlePath(self):
        prefix = self.modPath.split(".")[0]
        modLocation = GAME_LOCATION

        if self.prologdepengroup:
            modLocation = os.path.join(modLocation,PRELOAD_LOCATION)
        else:
            modLocation = os.path.join(modLocation,DEFAULT_LOCATION)

        match = next((x for x in os.listdir(modLocation) if x.startswith(prefix)), None)
        if match == None:
            self.isValid = False
            return
        else:
            self.realPath = os.path.join(modLocation,match)

    def remove_CRCPatch(self):
        with open(os.path.join(MOD_DIRECTORY,self.modPath), "rb+") as f:
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
            CRC_tool.manipulate_crc(self.realPath, os.path.join(MOD_DIRECTORY,self.modPath))
        except Exception as e:
            print("A error occured when applying CRC for mod: " + str(self.modName) + ", " + str(e))
            return -1
        self.CRCPatched = self.__checkCRCPatch() 
        return 1
    
    def __checkCRCPatch(self, path = ""):
        if path == "":
            path = os.path.join(MOD_DIRECTORY,self.modPath)
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
        backup_path = os.path.join(MOD_DIRECTORY,"backup")
        if not os.path.exists(backup_path):
            os.mkdir(backup_path)
            print("Created backup folder")
        if os.path.exists(os.path.join(backup_path,(self.realPath.split("\\")[-1]))):
            print("Backup for " + str(self.modName) + " exists, skipping...")
            return 0
        try:
            shutil.copyfile(self.realPath, os.path.join(backup_path,(self.realPath.split("\\")[-1])))
        except Exception as e:
            print("A error occured when backing up file: " + str(self.modName) + ", " + str(e))
            return -1
        print("Successfully backed up bundle files for " + str(self.modName))
        return 1
    
    def applyMod(self):
        try:
            if os.path.exists(self.realPath):
                os.remove(self.realPath)
            shutil.copyfile(os.path.join(MOD_DIRECTORY,self.modPath), self.realPath)
            Storage.setModApplied(self.modPath, True)
            print("Successfully applied mod for " + str(self.modName))
            return 1
        except Exception as e:
            print("A error occured when applying mod: " + str(self.modName) + ", " + str(e))
            return -1

    def restoreOriginalBundle(self):
        backup_path = os.path.join(MOD_DIRECTORY,"backup")
        
        if not os.path.exists(backup_path+"\\"+(self.realPath.split("\\")[-1])):
            print("No backup file found! You can Verify integiry of game files in Steam to obtain the original bundle, (it will remove all mods).")
            return -1

        if os.path.exists(self.realPath):
            os.remove(self.realPath)

        shutil.copyfile(os.path.join(backup_path,(self.realPath.split("\\")[-1])), self.realPath)
        Storage.setModApplied(self.modPath, False)
        self.isApplied = False
        print("Original bundle restored for " + str(self.modName))
        return 1
    
    def deleteMod(self):
        if self.isApplied:
            self.restoreOriginalBundle()
        try:
            os.remove(os.path.join(MOD_DIRECTORY,self.modPath))
            return 1
        except:
            return -1
    
    def changeModName(self, newName):
        Storage.writeNewModName(self.modPath, newName)
        self.modName = newName

    def updateMod(self):
        if self.isApplied:
            print("Mod applied, cannot update")
            return False, "Please unapply mod before updating first!", None
        sourceFile = GAME_LOCATION
        if self.prologdepengroup:
            sourceFile = os.path.join(sourceFile, PRELOAD_LOCATION) 
        else:
            sourceFile = os.path.join(sourceFile, DEFAULT_LOCATION)
        
        status = mainUpdater.updateMod(os.path.join(MOD_DIRECTORY,self.modPath), sourceFile, MOD_DIRECTORY)
        if os.path.exists(os.path.join(MOD_DIRECTORY,"uncrc_"+self.modPath)):
            os.remove(os.path.join(MOD_DIRECTORY,"uncrc_"+self.modPath))

        return status

def isValidModName(name):
    preload_full = os.path.join(GAME_LOCATION, PRELOAD_LOCATION)
    default_full = os.path.join(GAME_LOCATION, DEFAULT_LOCATION)

    if os.path.exists(os.path.join(preload_full,name)) or os.path.exists(os.path.join(default_full,name)):
        return True
    return False
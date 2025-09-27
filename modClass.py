import os
import CRC_tool
import shutil
# Automatically patch CRC/File name of Mods - No
# Automatically check for

MOD_DIRECTORY = "\\..\\BA Mod Manager\\mod"
GAME_LOCATION = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\BlueArchive"
PRELOAD_LOCATION = "BlueArchive_Data\\StreamingAssets\\PUB\\Resource\\Preload\\Windows"
DEFAULT_LOCATION = "BlueArchive_Data\\StreamingAssets\\PUB\\Resource\\GameData\\Windows"
MOD_BACKUP_LOCATION = MOD_DIRECTORY+"\\backup"

class mod():
    modName = ""
    modPath = ""
    modType = ""
    prologdepengroup = False
    isValid = False
    CRCPatched = False
    realPath = ""

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

        self.CRCPatched = self.__checkCRCPatch()

        self.__obtainRealBundlePath()

        if self.CRCPatched == True:
            self.remove_CRCPatch()
        self.patchCRC()

    def __obtainRealBundlePath(self):
        prefix = self.modPath.split(".")[0]
        modLocation = GAME_LOCATION+"\\"

        if self.prologdepengroup:
            modLocation += PRELOAD_LOCATION
        else:
            modLocation += DEFAULT_LOCATION

        match = next((x for x in os.listdir(modLocation) if x.startswith(prefix)), None)
        self.realPath = modLocation+"\\"+match

    def remove_CRCPatch(self):
        with open(MOD_DIRECTORY+"\\"+self.modPath, "rb+") as f:
            f.seek(0, 2)
            size = f.tell()
            f.truncate(size - 4)    
            
            self.CRCPatched = self.__checkCRCPatch() 

    def patchCRC(self):
        CRC_tool.manipulate_crc(self.realPath, MOD_DIRECTORY+"\\"+self.modPath)
        self.CRCPatched = self.__checkCRCPatch() 
        
    
    def __checkCRCPatch(self):
        with open(MOD_DIRECTORY+"\\"+self.modPath, "rb") as f:
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
        if os.path.exists(backup_path+"\\"+(self.realPath.split("\\")[-1])):
            print("Backup for " + str(self.modName) + " exists, skipping...")
            return
        try:
            shutil.copyfile(self.realPath, backup_path+"\\"+(self.realPath.split("\\")[-1]))
        except Exception as e:
            print("A error occured when backing up file: " + str(self.modName) + ", " + str(e))
            print("Skipping...")
            return
        print("Successfully backed up bundle files for " + str(self.modName))
    
    def applyMod(self):
        if os.path.exists(self.realPath):
            os.remove(self.realPath)
        
        shutil.copyfile(MOD_DIRECTORY+"\\"+self.modPath, self.realPath)
        print("Successfully applied mod for " + str(self.modName))

    def restoreOriginalBundle(self):
        backup_path = MOD_DIRECTORY + "\\backup"
        if os.path.exists(self.realPath):
            os.remove(self.realPath)
        
        if not os.path.exists(backup_path+"\\"+(self.realPath.split("\\")[-1])):
            print("No backup file found! You can Verify integiry of game files in Steam to obtain the original bundle, (it will remove all mods).")
            return

        shutil.copyfile(backup_path+"\\"+(self.realPath.split("\\")[-1]), self.realPath)
        print("Original bundle restored for " + str(self.modName))


def getModList():
    loadedMod = os.listdir(MOD_DIRECTORY)
    modObjects = []
    successfulCount = 0
    unsuccessfulCount = 0

    for x in loadedMod:
        modObject = mod(x)
        if modObject.isValid == True:
            modObjects.append(modObject)
            successfulCount += 1
            modObject.applyMod()
        else:
            if x != "backup":
                print("Failed to load mod with path: " + str(x))
                unsuccessfulCount += 1
    
    print("Total mods loaded: " + str(successfulCount) + " out of " + str(successfulCount+unsuccessfulCount) + ", " + str(unsuccessfulCount) + " mods failed to load.")


#getModList()
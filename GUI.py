from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import ttkbootstrap as tb
import tkinter as tk
import modClass
import os
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import ctypes as ct


def dark_title_bar(window):
    """
    MORE INFO:
    https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/ne-dwmapi-dwmwindowattribute
    """
    window.update()
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
    get_parent = ct.windll.user32.GetParent
    hwnd = get_parent(window.winfo_id())
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = 2
    value = ct.c_int(value)
    set_window_attribute(hwnd, rendering_policy, ct.byref(value),
                         ct.sizeof(value))

root = tb.Window(themename="darkly")
style = tb.Style()
style.load_user_themes("theme.json")
style.theme_use("newtheme")
root.title("Yet Another Blue Archive Mod Manager")

dark_title_bar(root)

root2 = None
modObjects = []
checkmarks = []

def openModFolderSelector():
    folder = filedialog.askdirectory()
    if folder:
        modLoc.delete(0, tk.END)
        modLoc.insert(0, folder.replace("/", "\\"))

def loadMods():
    if not os.path.exists(modLoc.get()):
        Messagebox.showerror("Error", "Invalid Path")
        return
    
    modClass.MOD_DIRECTORY = modLoc.get()
    files = os.listdir(modLoc.get())
    validMods = 0
    invalidMods = 0
    for x in files:
        newMod = modClass.mod(x)
        if not newMod.isValid:
            if x != "backup" and x != "desktop.ini":
                invalidMods += 1
                addLog("Failed to load mod with path: " + str(x))
            continue
        validMods += 1
        modObjects.append(newMod)
    addLog("Loading completed! Mods loaded successfully: " + str(validMods) + "/" + str(invalidMods+validMods))
    modLoadInformation["text"] = "Mods loaded: " + str(validMods) + "/" + str(invalidMods+validMods)
        
def addLog(logText):
    log.insert(tk.END, logText)
    log.see("end")

def applyModsGUI():
    global root2
    global checkmarks
    root2 = tb.Window(themename="darkly")
    style = tb.Style()
    style.load_user_themes("theme.json")
    style.theme_use("newtheme")
    root2.title("Yet Another Blue Archive Mod Manager")

    container = ttk.Frame(root2, padding=10)
    container.grid(sticky="nsew")

    ttk.Label(container, text="Select mods to apply").grid(row=0, column=0, sticky="w", columnspan=2)

    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.grid(row=1, column=0, sticky="nsew")
    scrollbar.grid(row=1, column=1, sticky="ns")

    button_frame = ttk.Frame(container)
    button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))

    apply_button = ttk.Button(button_frame, text="Apply", command=applySelectedMods)
    cancel_button = ttk.Button(button_frame, text="Cancel", command=root2.destroy)

    apply_button.pack(side="left", padx=5)
    cancel_button.pack(side="left", padx=5)

    checkmarks = []
    for i, x in enumerate(modObjects):
        check_var = tk.IntVar(master=root2)
        checkbutton = tk.Checkbutton(scrollable_frame, text=x.modName, variable=check_var)
        checkbutton.grid(row=i, column=0, sticky="w")
        checkbutton.select()
        checkmarks.append(check_var)
    root2.update_idletasks()
    container.rowconfigure(1, weight=1)
    container.columnconfigure(0, weight=1)

    root2.mainloop()

def restoreModsGUI():
    global root2
    global checkmarks
    root2 = tb.Window(themename="darkly")
    style = tb.Style()
    style.load_user_themes("theme.json")
    style.theme_use("newtheme")
    root2.title("Yet Another Blue Archive Mod Manager")

    container = ttk.Frame(root2, padding=10)
    container.grid(sticky="nsew")

    ttk.Label(container, text="Select mods to restore").grid(row=0, column=0, sticky="w", columnspan=2)

    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.grid(row=1, column=0, sticky="nsew")
    scrollbar.grid(row=1, column=1, sticky="ns")

    button_frame = ttk.Frame(container)
    button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))

    apply_button = ttk.Button(button_frame, text="Restore", command=restoreSelectedMods)
    cancel_button = ttk.Button(button_frame, text="Cancel", command=root2.destroy)

    apply_button.pack(side="left", padx=5)
    cancel_button.pack(side="left", padx=5)

    checkmarks = []
    for i, x in enumerate(modObjects):
        if x.isApplied:
            check_var = tk.IntVar(master=root2)
            checkbutton = tk.Checkbutton(scrollable_frame, text=x.modName, variable=check_var)
            checkbutton.grid(row=i, column=0, sticky="w")
            checkbutton.select()
            checkmarks.append(check_var)
    root2.update_idletasks()
    container.rowconfigure(1, weight=1)
    container.columnconfigure(0, weight=1)

    root2.mainloop()

def applySelectedMods():
    successfulApplications = 0
    failedApplications = 0
    for i, x in enumerate(checkmarks):
        if x.get():
            addLog("-----")
            status = modObjects[i].backupRealBundle()
            if status == -1:
                addLog("A error occured when backing up mod " + modObjects[i].modName + ", mod will not be applied...")
                failedApplications+=1
                continue
            elif status == 1:
                addLog("Successfully backed up mod: " + modObjects[i].modName)
            else:
                addLog("Backup already exists for mod: " + modObjects[i].modName + " skipping backup creation.")
            status = modObjects[i].patchCRC()
            if status == -2:
                addLog("CRC patch cannot be applied for mod: " + modObjects[i].modName + ", it seems like the mod has already been applied, skipping mod application to avoid CRC corruption")
                failedApplications+=1
                continue
            elif status == -1:
                addLog("A error occured when applying the CRC for mod " + modObjects[i].modName + ".")
                failedApplications+=1
                continue
            else:
                addLog("Successfully patched CRC for mod " + modObjects[i].modName)
            status = modObjects[i].applyMod()
            if status == -1:
                addLog("A error occured when applying mod " + modObjects[i].modName + ", backup will be automatically restored.")
                modObjects[i].restoreOriginalBundle()
                failedApplications+=1
                continue
            addLog("Mod " + modObjects[i].modName + " successfully applied!")
            successfulApplications+=1
    addLog("=====")
    addLog("Finished applying mods, amount successful: " + str(successfulApplications) + "/" + str(failedApplications+successfulApplications))
    addLog("=====")
    root2.destroy()

def restoreSelectedMods():
    successfulRestore = 0
    failedRestore = 0
    for i, x in enumerate(checkmarks):
        if x.get():
            status = modObjects[i].restoreOriginalBundle()
            if status == -1:
                addLog("Mod " + modObjects[i].modName + " cannot be restored, no backup files found! You can verifiy integrity of game files in Steam to obtain the original bundle file (all mods will be removed however.)")
                failedRestore+=1
                continue
            else:
                addLog("Mod " + modObjects[i].modName + " successfully restored!")
            successfulRestore+=1
    addLog("=====")
    addLog("Finished restoring mods, amount successful: " + str(successfulRestore) + "/" + str(failedRestore+successfulRestore))
    addLog("=====")
    root2.destroy()

frm = tk.Frame(root)
frm.grid( padx=5, pady=5)

ttk.Label(frm, text="Mod Files Location: ").grid(column=0, row=0)
modLoc = ttk.Entry(frm, width=50)
modLoc.insert(0, "mods/")
modLoc.grid(column=1, row=0, padx=5, pady=5)
modOpenFilePicker = ttk.Button(frm, text="Open", command=openModFolderSelector, bootstyle=(INFO, OUTLINE))
modOpenFilePicker.grid(column=2, row=0, padx=5, pady=5)

frmButtons = ttk.Frame(root, padding = 3)
frmButtons.grid()

loadModsButton = ttk.Button(frmButtons, text="Load Mods", command=loadMods, bootstyle=(INFO, OUTLINE))
loadModsButton.grid(column=0, row=1, padx=5, pady=5)

applyModsButton = ttk.Button(frmButtons, text="Apply Mods", command=applyModsGUI, bootstyle=(INFO, OUTLINE))
applyModsButton.grid(column=1, row=1, padx=5, pady=5)

restoreModsButton = ttk.Button(frmButtons, text="Restore Original", command=restoreModsGUI, bootstyle=(INFO, OUTLINE))
restoreModsButton.grid(column=2, row=1, padx=5, pady=5)

modLoadInformation = ttk.Label(frmButtons, text="No mods loaded.")
modLoadInformation.grid(column=1, row=2, padx=0, pady=5)

frmLog = tk.Frame(root, bg="red", padx=2, pady=2)
frmLog.grid()

log = tk.Listbox(frmLog, width=70, height=10, bd=0, relief="flat")
log.grid(column=3, row=0, padx=5, pady=12)

root.mainloop()
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
import shutil

def dark_title_bar(window):
    window.update()
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
    get_parent = ct.windll.user32.GetParent
    hwnd = get_parent(window.winfo_id())
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = 2
    value = ct.c_int(value)
    set_window_attribute(hwnd, rendering_policy, ct.byref(value), ct.sizeof(value))
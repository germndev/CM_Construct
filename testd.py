import os, winshell
from win32com.client import Dispatch

desktop = winshell.desktop()
path = os.path.join(desktop, "NAME.lnk")
target = r"D:\PyCharm\job\1.bat"
wDir = r"D:\PyCharm\job"
icon = r"D:\PyCharm\job\dist\main.exe"

shell = Dispatch('WScript.Shell')
shortcut = shell.CreateShortCut(path)
shortcut.Targetpath = target
shortcut.WorkingDirectory = wDir
shortcut.IconLocation = icon
shortcut.save()
from pyvda import AppView, VirtualDesktop, get_virtual_desktops
from subprocess import Popen
from global_hotkeys import *
import time
import json
import win32gui
import keyboard
# Make sure to add C:\Users\damian.jozwiak\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1
# Remove-PSReadlineKeyHandler -Key Alt+1

class App:
    def __init__(self, name, start):
        self.name = name
        self.start = start
        self.hwnd = None

    def callback(self, hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            if self.name in win32gui.GetWindowText(hwnd):
                print("Found the window for "+self.name +
                      ": " + win32gui.GetWindowText(hwnd))
                self.hwnd = hwnd

    def locate(self):
        win32gui.EnumWindows(
            lambda hwnd, extra: self.callback(hwnd, extra), None)
        if self.hwnd == None:
            self.start_app()
            win32gui.EnumWindows(
                lambda hwnd, extra: self.callback(hwnd, extra), None)
        return self.hwnd

    def start_app(self):
        if self.start is not None:
            print(("Trying to start %s") % (self.start))
            Popen([self.start])
            time.sleep(5)


class Desktop:
    def switchTo(self, activate=True):
        if activate == True:
            VirtualDesktop(self.id).go()
            keyboard.press_and_release("alt+esc")

    def __init__(self, id, apps):
        self.id = id
        self.apps = []
        for a in apps:
            app = App(**a)
            self.apps = [*self.apps, app]
        for a in self.apps:
            hwnd = a.locate()
            if hwnd != None:
                AppView(hwnd).move(VirtualDesktop(self.id))

class DesktopSwitcher:
    def __init__(self):
        self.desktops = []
        currentDesktopCount = len(get_virtual_desktops())
        for i in range(1, 10):
            desktop = Desktop(i, [])
            self.desktops = [*self.desktops, desktop]
            keyboard.add_hotkey('alt+'+str(i), desktop.switchTo, args=(not keyboard.is_pressed('shift'),))
            keyboard.add_hotkey('alt+shift+'+str(i), self.moveWindowTo, args=(desktop.id,))
        if currentDesktopCount < 9:
            for i in range(0, 9-currentDesktopCount):
                VirtualDesktop.create()
    def addDesktops(self, desktops):
        for desktop in desktops:
            self.desktops[desktop.id-1] = desktop
    def switchToDesktop(self, number):
        self.desktops[number-1].switchTo()
    def moveWindowTo(self, targetDesktop):
        currentWindow = AppView.current()
        currentWindow.move(VirtualDesktop(targetDesktop))
    def currentDesktop(self):
        return VirtualDesktop.current()

if __name__ == "__main__":
    # read number of desktops
    desktopSwitcher = DesktopSwitcher()
    desktops = []
    with open("config.json", 'r') as config:
        jj = json.load(config)
        for desktop in jj["desktops"]:
            d = Desktop(**desktop)
            desktops = [*desktops, d]
    desktopSwitcher.addDesktops(desktops)
    print("ready")
    keyboard.wait("alt+0")

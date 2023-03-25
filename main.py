from pyvda import AppView, get_apps_by_z_order, VirtualDesktop, get_virtual_desktops
from subprocess import Popen
from global_hotkeys import *
import time
import json
import win32gui
import win32con
from pynput.keyboard import Key, Controller
keyboard = Controller()
is_alive= True
def exit_application():
    global is_alive
    stop_checking_hotkeys()
    is_alive = False

class App:
    def __init__(self, name, start):
        self.name = name
        self.start = start
        self.hwnd = None
    def callback(self,hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            if self.name in win32gui.GetWindowText(hwnd):
                print("Found the window for "+self.name + ": " + win32gui.GetWindowText(hwnd))
                self.hwnd = hwnd
    def locate(self):
        win32gui.EnumWindows(lambda hwnd,extra: self.callback(hwnd,extra), None)
        if self.hwnd == None:
            self.start_app()
            win32gui.EnumWindows(lambda hwnd,extra: self.callback(hwnd,extra), None)
        return self.hwnd
    def start_app(self):
        print(("Trying to start %s") % (self.start))
        Popen([self.start])
        time.sleep(5)

class Desktop:
    def switchTo(self):
        global keyboard
        VirtualDesktop(self.id).go()
        with keyboard.pressed(Key.alt):
            keyboard.press(Key.esc)
            keyboard.release(Key.esc)
    def __init__(self, id, apps):
        self.id = id
        self.apps = []
        for a in apps:
            app = App(**a)
            self.apps = [*self.apps, app]
        for a in self.apps:
            hwnd = a.locate()
            if hwnd != None:
                print(("Moving %s to desktop #%d")% (a.name,self.id))
                AppView(hwnd).move(VirtualDesktop(self.id))
# Keep waiting until the user presses the exit_application keybinding.
# Note that the hotkey listener will exit when the main thread does.
class DesktopSwitcher:
    def __init__(self):
        self.desktops = []
        currentDesktopCount = len(get_virtual_desktops())
        for i in range(1,10):
            desktop = Desktop(i,[])
            self.desktops = [*self.desktops,desktop]
        if currentDesktopCount < 9:
            for i in range(0,9-currentDesktopCount):
                VirtualDesktop.create()
    def addDesktops(self,desktops):
        for desktop in desktops:
            self.desktops[desktop.id-1]= desktop
    def switchToDesktop(self,number):
        self.desktops[number-1].switchTo()
    def currentDesktop(self):
        return VirtualDesktop.current()

desktopSwitcher = DesktopSwitcher()
# Declare some key bindings.
# These take the format of [<key list>, <keydown handler callback>, <keyup handler callback>]
bindings = [
    [["alt", "1"], None, lambda: desktopSwitcher.switchToDesktop(1)],
    [["alt", "2"], None, lambda: desktopSwitcher.switchToDesktop(2)],
    [["alt", "3"], None, lambda: desktopSwitcher.switchToDesktop(3)],
    [["alt", "4"], None, lambda: desktopSwitcher.switchToDesktop(4)],
    [["alt", "5"], None, lambda: desktopSwitcher.switchToDesktop(5)],
    [["alt", "6"], None, lambda: desktopSwitcher.switchToDesktop(6)],
    [["alt", "7"], None, lambda: desktopSwitcher.switchToDesktop(7)],
    [["alt", "8"], None, lambda: desktopSwitcher.switchToDesktop(8)],
    [["alt", "9"], None, lambda: desktopSwitcher.switchToDesktop(9)],
    [["alt", "0"], None, exit_application],
]


if __name__ == "__main__":
    #read number of desktops
    desktops = []
    with open("config.json",'r') as config:
        jj = json.load(config)
        for desktop in jj["desktops"]:
            d = Desktop(**desktop)
            desktops = [*desktops,d]
    desktopSwitcher.addDesktops(desktops)
    currentDesktopCount = len(get_virtual_desktops())
    print("Active desktops:" + str(currentDesktopCount))
    register_hotkeys(bindings)
    # Finally, start listening for keypresses
    start_checking_hotkeys()
    print("ready")
    while is_alive:
        time.sleep(0.1)



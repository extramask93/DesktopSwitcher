from pyvda import AppView, get_apps_by_z_order, VirtualDesktop, get_virtual_desktops
from global_hotkeys import *
import time
import json
import win32gui

is_alive= True
def exit_application():
    global is_alive
    stop_checking_hotkeys()
    is_alive = False
# Declare some key bindings.
# These take the format of [<key list>, <keydown handler callback>, <keyup handler callback>]
bindings = [
    [["alt", "1"], None, lambda: DesktopSwitcher.switchToDesktop(1)],
    [["alt", "2"], None, lambda: DesktopSwitcher.switchToDesktop(2)],
    [["alt", "3"], None, lambda: DesktopSwitcher.switchToDesktop(3)],
    [["alt", "4"], None, lambda: DesktopSwitcher.switchToDesktop(4)],
    [["alt", "5"], None, lambda: DesktopSwitcher.switchToDesktop(5)],
    [["alt", "6"], None, lambda: DesktopSwitcher.switchToDesktop(6)],
    [["alt", "7"], None, lambda: DesktopSwitcher.switchToDesktop(7)],
    [["alt", "8"], None, lambda: DesktopSwitcher.switchToDesktop(8)],
    [["alt", "9"], None, lambda: DesktopSwitcher.switchToDesktop(9)],
    [["alt", "0"], None, exit_application],
]


# Keep waiting until the user presses the exit_application keybinding.
# Note that the hotkey listener will exit when the main thread does.
class DesktopSwitcher:
    def addDesktops(number,currentDesktopCount):
        assert number <= 9
        assert number > 0
        #add desktops if neccessary
        if currentDesktopCount < number:
            for i in range(0,number-currentDesktopCount):
                VirtualDesktop.create()
    def switchToDesktop(number):
        VirtualDesktop(number).go()
    def currentDesktop():
        return VirtualDesktop.current()
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
            return self.start()
        return self.hwnd
    def start():
        return None
class Desktop:
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

if __name__ == "__main__":
    #read number of desktops
    desktop_count = 1
    with open("config.json",'r') as config:
        jj = json.load(config)
        desktop_count = int(jj['desktop_count'])
        desktops = []
        for desktop in jj["desktops"]:
            d = Desktop(**desktop)
            desktops = [*desktops,d]
    currentDesktopCount = len(get_virtual_desktops())
    print("Active desktops:" + str(currentDesktopCount))
    print("Adding %d desktops" % (desktop_count))
    DesktopSwitcher.addDesktops(desktop_count,currentDesktopCount)
    register_hotkeys(bindings)
    # Finally, start listening for keypresses
    start_checking_hotkeys()
    while is_alive:
        time.sleep(0.1)



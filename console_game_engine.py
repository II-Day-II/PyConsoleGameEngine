# David Kaméus
# Translation of olcConsoleGameEngine.h

from ctypes import WINFUNCTYPE, windll, byref, sizeof, Structure, Union, c_ulong, c_uint, c_wchar
import ctypes.wintypes as wtps
from signal import CTRL_C_EVENT
from threading import Thread
from time import perf_counter

CTRL_CLOSE_EVENT = 2
PHANDLER_ROUTINE = WINFUNCTYPE(wtps.BOOL, wtps.DWORD)
STD_OUTPUT_HANDLE = -11
STD_INPUT_HANDLE = -10
GetStdHandle = windll.kernel32.GetStdHandle
GetConsoleScreenBufferInfo = windll.kernel32.GetConsoleScreenBufferInfo
SetConsoleWindowInfo = windll.kernel32.SetConsoleWindowInfo
SetConsoleScreenBufferSize = windll.kernel32.SetConsoleScreenBufferSize
SetConsoleActiveScreenBuffer = windll.kernel32.SetConsoleActiveScreenBuffer
SetCurrentConsoleFontEx = windll.kernel32.SetCurrentConsoleFontEx
SetConsoleCtrlHandler = windll.kernel32.SetConsoleCtrlHandler
WriteConsoleOutput = windll.kernel32.WriteConsoleOutputW
SetConsoleTitle = windll.kernel32.SetConsoleTitle

class CONSOLE_FONT_INFOEX(Structure):
    _fields_ = [
        ("cbSize", c_ulong),
        ("nFont", c_ulong),
        ("dwFontSize", wtps._COORD),
        ("FontFamily", c_uint),
        ("FontWeight", c_uint),
        ("FaceName", c_wchar * 32)
    ]

class CONSOLE_SCREEN_BUFFER_INFO(Structure):
    _fields_ = [
        ("dwSize", wtps._COORD),
        ("dwCursorPosition", wtps._COORD),
        ("wAttributes", wtps.WORD),
        ("srWindow", wtps.SMALL_RECT),
        ("dwMaximumWindowSize", wtps._COORD),
    ]

class Char(Union):
    _fields_ = [("UnicodeChar", wtps.WCHAR),
                ("AsciiChar", wtps.CHAR)]

class CHAR_INFO(Structure):
    _anonymous_ = ("Char",)
    _fields_ = [("Char", Char),
                ("Attributes", wtps.WORD)]

class CGE:
    def __init__(self):
        self.title = "Default"
        self.screen_width = 80
        self.screen_height = 30
        self.original_console_handle = wtps.HANDLE()
        self.console_handle = GetStdHandle(STD_OUTPUT_HANDLE)
        self.console_in_handle = GetStdHandle(STD_INPUT_HANDLE)
        # self.new_key_state = [0] * 256
        # self.old_key_state = [0] * 256
        # self.keys = [0] * 256
        # self.mouse_pos = (0,0)
        # self.sound = False
        self.active = False

    def CloseHandler(self, evt):
        if evt == CTRL_CLOSE_EVENT or evt == CTRL_C_EVENT:
            self.active = False
            # wait for thread or something here
            return 1
        return 0

    def Error(self, msg):
        SetConsoleActiveScreenBuffer(self.original_console_handle)
        raise msg

    def construct_console(self, width, height, fontw = None, fonth = None):
        self.screen_height = height
        self.screen_width = width
        self.rect_window = wtps.SMALL_RECT(0,0,1,1)
        if not SetConsoleWindowInfo(self.console_handle, True, byref(self.rect_window)):
            self.Error("SetConsoleWindowInfo")

        coord = wtps._COORD(self.screen_width, self.screen_height)
        if not SetConsoleScreenBufferSize(self.console_handle, coord):
            self.Error("SetConsoleScreenBufferSize")
        if not SetConsoleActiveScreenBuffer(self.console_handle):
            self.Error("SetConsoleActiveScreenBuffer")

        if fontw and fonth: # i've a feeling fonts are gonna be fucky
            font = CONSOLE_FONT_INFOEX()
            font.cbSize = sizeof(font)
            font.nFont = 0
            font.dwFontSize.X = fontw
            font.dwFontSize.Y = fonth
            font.FontFamily = 0 # FF_DONTCARE
            font.FontWeight = 400 # FW_NORMAL
            #font.FaceName = "Consolas"
            font.FaceName = "CascadiaCustomMono NF"

            if not SetCurrentConsoleFontEx(self.console_handle, False, byref(font)):
                self.Error("SetCurrentConsoleFontEx")
        
        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        if not GetConsoleScreenBufferInfo(self.console_handle, byref(csbi)):
            self.Error("GetConsoleScreenBufferInfo")
        if self.screen_height > csbi.dwMaximumWindowSize.Y:
            self.Error("Screen Height / Font Height Too Big!")
        if self.screen_width > csbi.dwMaximumWindowSize.X:
            self.Error("Screen Width / Font Width Too Big!")
        
        self.rect_window = wtps.SMALL_RECT(0, 0, self.screen_width - 1, self.screen_height - 1)
        if not SetConsoleWindowInfo(self.console_handle, True, byref(self.rect_window)):
            self.Error("SetConsoleWindowInfo")

        #set console mode to enable mouse here

        # allocate screen buffer
        self.screen_buffer = [CHAR_INFO()] * self.screen_height * self.screen_width

        # set a close handler or something???
        SetConsoleCtrlHandler(PHANDLER_ROUTINE(self.close_handler), True)

    def on_user_create(self):
        return False #self.Error("on_user_create must be overridden!!!!")
    def on_user_update(self, delta_time):
        return False #self.Error("on_user_update must be overridden!!!!")

    def start(self):
        self.active = True
        t = Thread(target=self.game_thread)
        t.start()
        t.join()
    
    def game_thread(self):
        if not self.on_user_create():
            self.active = False
        tp1 = perf_counter()
        tp2 = perf_counter()

        while self.active:
            tp2 = perf_counter()
            delta_time = tp2 - tp1
            tp1 = tp2
            # get keyboard input here
            # get mouse input
            # get events??
            if not self.on_user_update(delta_time):
                self.active = False

            s = f"PyConsoleGameEngine - {self.title} @ FPS: {1 / delta_time}"
            SetConsoleTitle(s)
            WriteConsoleOutput(self.console_handle, self.screen_buffer, wtps._COORD(self.screen_width, self.screen_height), wtps._COORD(0,0), byref(self.rect_window))
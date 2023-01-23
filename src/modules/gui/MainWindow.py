from tkinter import *
from tkinter import ttk
from os.path import join

class MainWindow:
    """
    This class creates the main application window and is responsible for the core layout
    """
    def __init__(self, approot):
        self._approot = approot
        self._moduleroot = join(self._approot, "modules")
        self._window_title = "X4 Save Manager"
        self._window = Tk()
        self.set_window_title()
        self.build_window()
        self.startup()

    def set_window_title(self, text=""):
        """
        Sets the window title
        """
        if not text:
            self._window.title(f"{self._window_title}")
        else:
            self._window.title(f"{self._window_title} - {text}")
    
    def startup(self):
        """
        starts the main window TK event loop
        """
        self._window.mainloop()
    
    def build_window(self):
        pass
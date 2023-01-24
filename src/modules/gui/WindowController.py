import tkinter as tk
import os.path as path
from .StartPage import StartPage

class WindowController(tk.Tk):
    """
    This class creates the main application window and is responsible for the core layout
    """
    def __init__(self, approot):
        super().__init__()

        self._approot = approot
        self._moduleroot = path.join(self._approot, "modules")
        self._window_title = "X4 Save Manager"

        ## all pages\page parts should inherit from tk.Frame and take a parameter for WindowController to store as the parent
        self.startpage = StartPage(self)
        
        self.set_window_title()
        self.startup()

    def set_window_title(self, text=""):
        """
        Sets the window title
        """
        if not text:
            self.title(f"{self._window_title}")
        else:
            self.title(f"{self._window_title} - {text}")
    
    def startup(self):
        """
        starts the main window TK event loop
        """
        self.mainloop()
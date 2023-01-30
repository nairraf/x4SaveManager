"""WindowController Definition

The WindowController is the entrypoint and main controller for the application
and is responsible for creating/managing the main GUI page as well
as the main Tk event loop.

Example:
    import sys
    import os.path as path
    from modules.gui import WindowController

    approot = path.realpath(path.dirname(__file__))
    moduleroot = path.join(approot, "modules")
    sys.path.append(moduleroot)

    WindowController(approot, moduleroot)
"""
import tkinter as tk
from .start_page import StartPage
from .status_bar import StatusBar


class WindowController(tk.Tk):
    """This class creates the main application window and is responsible
    for creating the core layout for the GUI

    Args:
        tk (tk.Tk): inherits from tk.Tk
    """

    def __init__(self, approot, moduleroot):
        """Initializes a new instance of WindowController

        Args:
            approot (str): filesystem full path of the application root folder
            moduleroot (str): filesystem path to the modules folder
        """
        super().__init__()

        self.approot = approot
        self.moduleroot = moduleroot
        self.window_title = "X4 Save Manager"

        # we set the root window row and column to be responsive
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.minsize(width=600, height=255)

        # we place a frame which is the size of the entire window, which is the
        # parent to all other page part objects. we also make this root level
        # content frame to be reponsive, and make the content container
        # grow and shrink with all window regions
        self.content = tk.Frame(self)
        self.content.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=1)
        self.content.grid(column=0, row=0, sticky=(tk.N, tk.E, tk.S, tk.W))

        # all pages parts should inherit from tk.Frame and
        # use self.content as their parent and take a second
        # argument to pass the WindowController instance (self)
        self.startpage = StartPage(self.content, self)
        self.statusbar = StatusBar(self.content, self)

        self.set_window_title()
        self.startup()

    def set_window_title(self, text=""):
        """Sets the window title
        """
        if not text:
            self.title(f"{self.window_title}")
        else:
            self.title(f"{self.window_title} - {text}")

    def startup(self):
        """starts the main window TK event loop
        """
        self.mainloop()

"""Base Class for all new toplevel windows

Centralizes the window title and icon settings and includes that appropriate
properties for the MessageWindow modal

Usage:
import tkinter as tk
from tkinter import ttk
from .new_page_root import NewPageRoot

class PageName(NewPageRoot):
    def __init__(self, caller, controller):
        super().__init__(caller, controller)

        self.set_title("PageName")
        self.minsize(300,300)

        self.show_window()
"""

from __future__ import annotations
from typing import TYPE_CHECKING

import tkinter as tk
from .gui_settings import GuiSettings
from .messages import MessageWindow

if TYPE_CHECKING:
    from modules.gui import WindowController

class NewPageRoot(tk.Toplevel):
    """Base clase for all toplevel windows
    """
    def __init__(self, caller, controller: WindowController):
        """NewPageRoot constructor
        
        Args:
            caller (tk.TK): the caller
            controller (WindowController): the application controller
        """
        super().__init__()
        self.caller = caller
        self.controller = controller
        self.modalresult = 0
        self.withdraw()
        
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.iconbitmap(GuiSettings.icon_path)
        self.config(
            padx=5,
            pady=5
        )

    def set_title(self, title):
        """Sets the window title
        """
        self.title("{} - {}".format(
            GuiSettings.window_title,
            title
        ))
    
    def show_window(self):
        """Shows the window

        By default all new toplevel windows are hidden to allow them to
        be built, sized, and positioned on the screen.

        Call show_window() when it's fully built and ready for the user so
        that the user doesn't see "flashing" where the window appears for a
        split second and then warps to it's final position
        """
        # place and show the window
        self.update()
        self.geometry("+{}+{}".format(
            self.master.winfo_x() + 50,
            self.master.winfo_y() + 50
        ))

        self.transient(self.master)
        self.deiconify()
        self.focus()

    def show_error(self, message):
        """wrapper for MessageWindow for displaying errors dialogs
        """
        MessageWindow(
            self,
            message,
            type="error"
        )

    def show_message(self, message):
        """wrapper for MessageWindow for displaying info dialogs
        """
        MessageWindow(
            self,
            message
        )

    def show_question(
        self,
        message,
        oktext="Yes",
        canceltext="No"
    ):
        """wrapper for MessageWindow for displaying question dialogs
        """
        MessageWindow(
            self,
            message=message,
            type="question",
            oktext=oktext,
            canceltext=canceltext
        )
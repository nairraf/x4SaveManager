from __future__ import annotations
from typing import TYPE_CHECKING

import tkinter as tk
from .gui_settings import GuiSettings
from .messages import MessageWindow

if TYPE_CHECKING:
    from modules.gui import WindowController

class NewPageRoot(tk.Toplevel):
    def __init__(self, caller, controller: WindowController):
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
        self.title("{} - {}".format(
            GuiSettings.window_title,
            title
        ))
    
    def show_window(self):
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
        MessageWindow(
            self,
            message,
            type="error"
        )

    def show_message(self, message):
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
        MessageWindow(
            self,
            message=message,
            type="question",
            oktext=oktext,
            canceltext=canceltext
        )
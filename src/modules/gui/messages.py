import tkinter as tk
from tkinter import ttk
from .gui_settings import GuiSettings

class MessageWindow(tk.Toplevel):
    """a configurable modal message window

    Args:
        tk (tk.Toplevel): inherits from tk.Toplevel
    """
    def __init__(self, caller, message, type="info", 
        oktext="OK", canceltext="Cancel", width=200, height=75
    ):
        """Creates a configurable modal window and returns the result to the
        modalresult attribute of the caller object (caller parameter).

        Args:
            caller (obj): the object which contains the modalresult attribute
            title (str): the title for the pop-up window
            message (str): the message for the pop-up window
            type (str, optional): info,question,error. Defaults to "info".
            oktext (str, optional): text for the OK button. Defaults to "OK".
            canceltext (str, optional): text for Cancel button. 
                                        Defaults to "Cancel".
            width (int, optional): the window width, default 200
            height (int, optional): the window height, default 75
        """
        super().__init__()
        # we hide the pop-up window, and then after it's built we show it with
        # self.deiconify() at the bottom
        # this works around the "flashing" bug where the window appears in 
        # one location for a brief second and the "relocates/warps" to 
        # the updated location (with the geometry call)
        self.withdraw()
        self.caller = caller
        self.type = type
        self.details_expanded = False
        self.title(GuiSettings.window_title)
        self.iconbitmap(GuiSettings.icon_path)
        
        self.geometry("{}x{}+{}+{}".format(
            width,
            height,
            int(self.master.winfo_x() + (self.master.winfo_width()/2-100)),
            int(self.master.winfo_y() + (self.master.winfo_height()/2-32)))
        )
        
        self.resizable(True, True)
        self.rowconfigure([0,1], weight=1)
        self.columnconfigure([0,1,2], weight=1)
        if type == "info":
            image = "::tk::icons::information"
            ttk.Button(self, text=oktext, command=self.ok).grid(
                row=1,
                column=0,
                columnspan=3
            )
        if type == "error":
            image = "::tk::icons::error"
            ttk.Button(self, text=oktext, command=self.ok).grid(
                row=1,
                column=0,
                columnspan=3
            )
        if type == "question":
            image = "::tk::icons::question"
            ttk.Button(self, text=oktext, command=self.ok).grid(
                row=1,
                column=1,
                sticky="e",
                padx=0,
                pady=0
            )
            ttk.Button(self, text=canceltext, command=self.cancel).grid(
                row=1,
                column=2,
                sticky="e",
                padx=(0, 5),
                pady=0
            )
        ttk.Label(self, image=image).grid(
            row=0,
            column=0,
            sticky="e"
        )
        ttk.Label(self, text=message).grid(
            row=0,
            column=1,
            columnspan=2,
            sticky="ew",
            padx=(5, 5)
        )
        self.transient(self.master)
        # show the window now that it's built and wait for the user click
        self.deiconify()
        self.wait_visibility()
        self.grab_set()
        self.wait_window()

    def ok(self):
        """writes the pass result to the caller's modalresult and exits
        """
        if self.type == "question":
            self.caller.modalresult = 1
        self.destroy()

    def cancel(self):
        """writes the fail result to the caller's modalresult and exits
        """
        if self.type == "question":
            self.caller.modalresult = 0
        self.destroy()
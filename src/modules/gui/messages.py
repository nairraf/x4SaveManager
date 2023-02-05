import tkinter as tk
from tkinter import ttk
from .gui_settings import GuiSettings

class MessageWindow(tk.Toplevel):
    """a configurable modal message window

    Args:
        tk (tk.Toplevel): inherits from tk.Toplevel
    """
    def __init__(self, caller, message, type="info", 
        oktext="OK", canceltext="Cancel"
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
        
        self.resizable(False, False)
        self.rowconfigure([0,1], weight=1)
        self.columnconfigure(1, weight=1)
        if type == "info":
            image = "::tk::icons::information"
            ttk.Button(self, text=oktext, command=self.ok).grid(
                row=1,
                column=0,
                columnspan=3,
                pady=5
            )
        if type == "error":
            image = "::tk::icons::error"
            ttk.Button(self, text=oktext, command=self.ok).grid(
                row=1,
                column=0,
                columnspan=3,
                pady=5
            )
        if type == "question":
            image = "::tk::icons::question"
            ttk.Button(self, text=oktext, command=self.ok).grid(
                row=1,
                column=1,
                sticky=tk.E,
                padx=0,
                pady=5,
                
            )
            ttk.Button(self, text=canceltext, command=self.cancel).grid(
                row=1,
                column=2,
                sticky=tk.W,
                padx=(0, 5),
                pady=5
            )
        ttk.Label(self, image=image).grid(
            row=0,
            column=0,
            sticky="e",
            padx=(10,0)
        )
        ttk.Label(self, text=message).grid(
            row=0,
            column=1,
            columnspan=2,
            sticky="ew",
            padx=(5, 5)
        )
        self.transient(self.caller)

        # position the window towards the center of the caller window
        # we have to detect the startpage vs other callers/windows
        x = 0
        y = 0
        caller_width = 0
        caller_height = 0
        if caller._name == '!startpage':
            x = self.master.winfo_x()
            y = self.master.winfo_y()
            caller_width = self.master.winfo_width()/2
            caller_height = self.master.winfo_height()/2
        else:
            x = self.caller.winfo_x()
            y = self.caller.winfo_y()
            caller_width = self.caller.winfo_width()/2
            caller_height = self.caller.winfo_height()/2
        
        self.geometry("+{}+{}".format(
            int( x + caller_width - self.winfo_reqwidth()/2),
            int( y + caller_height - self.winfo_reqheight()/8)
        ))

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
import tkinter as tk
from tkinter import ttk

class MessageWindow(tk.Toplevel):
    """a configurable modal message window

    Args:
        tk (tk.Toplevel): inherits from tk.Toplevel
    """
    def __init__(self, caller, title, message, type="info", 
        oktext="OK", canceltext="Cancel",
    ):
        """Creates a configurable modal window and returns the result to the
        modalresult attribute of the caller object (caller parameter).

        Args:
            caller (obj): the object which contains the modalresult attribute
            title (str): the title for the pop-up window
            message (str): the message for the pop-up window
            type (str, optional): info or question. Defaults to "info".
            oktext (str, optional): text for the OK button. Defaults to "OK".
            canceltext (str, optional): text for Cancel button. 
                                        Defaults to "Cancel".
        """
        super().__init__()
        self.caller = caller
        self.details_expanded = False
        self.title(title)
        
        self.geometry("200x75+{}+{}".format(
            int(self.master.winfo_x() + (self.master.winfo_width()/2-100)),
            int(self.master.winfo_y() + (self.master.winfo_height()/2-32)))
        )
        self.resizable(False, False)
        self.rowconfigure([0,1], weight=1)
        self.columnconfigure([0,1,2], weight=1)
        if type == "info":
            image = "::tk::icons::information"
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
        self.wait_visibility()
        self.grab_set()
        self.wait_window()

    def ok(self):
        """writes the pass result to the caller's modalresult and exits
        """
        self.caller.modalresult = 1
        self.destroy()

    def cancel(self):
        """writes the fail result to the caller's modalresult and exits
        """
        self.caller.modalresult = 0
        self.destroy()
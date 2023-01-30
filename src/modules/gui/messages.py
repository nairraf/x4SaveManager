import tkinter as tk
from tkinter import ttk

class MessageWindow(tk.Toplevel):
    def __init__(self, parent, title, message, type="info", 
        oktext="OK", canceltext="Cancel",
    ):
        super().__init__()
        self.parent = parent
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
        self.parent.modalresult = 1
        self.destroy()

    def cancel(self):
        self.parent.modalresult = 0
        self.destroy()
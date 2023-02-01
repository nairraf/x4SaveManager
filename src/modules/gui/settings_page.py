import tkinter as tk
from tkinter import ttk

class Settings(tk.Toplevel):
    def __init__(self, caller):
        super().__init__()
        self.caller = caller
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.title("{} - Settings".format(
            caller.root.window_title
        ))
        self.config(
            padx=5,
            pady=5
        )
        
        nb = ttk.Notebook(self, width=450, height=300)
        app_page = ttk.Frame(nb)
        db_page = ttk.Frame(nb)
        nb.add(app_page, text="App Settings")
        nb.add(db_page, text="Database Settings")
        nb.grid(
            column=0,
            columnspan=3,
            row=0,
            pady=(0, 2),
            sticky=(tk.N, tk.E, tk.S, tk.W)
        )

        ttk.Button(self, text="Save", command=self.save).grid(
            column=1,
            row=1,
            sticky=tk.E
        )

        ttk.Button(self, text="Close", command=self.close).grid(
            column=2,
            row=1,
            sticky=tk.E
        )

        self.update()
        self.geometry("{}x{}+{}+{}".format(
            self.winfo_width(),
            self.winfo_height(),
            self.master.winfo_x() + 50,
            self.master.winfo_y() + 50
        ))
        self.focus()

    def close(self):
        self.destroy()

    def save(self):
        print("saving settings")


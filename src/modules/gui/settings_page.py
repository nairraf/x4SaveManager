import tkinter as tk
from tkinter import ttk
from .gui_settings import GuiSettings

class Settings(tk.Toplevel):
    def __init__(self, caller):
        super().__init__()
        self.withdraw()
        self.status_text = tk.StringVar()
        self.app_config_path_text = tk.StringVar()
        self.caller = caller
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.title("{} - Settings".format(
            GuiSettings.window_title
        ))
        self.iconbitmap(GuiSettings.icon_path)
        self.config(
            padx=5,
            pady=5
        )
        self.minsize(450,300)
        
        nb = ttk.Notebook(
            self,
            width=450,
            height=300,
            padding=5
        )
        # app page
        app_page = ttk.Frame(nb, padding=5)
        app_page.grid_columnconfigure(1, weight=1)
        ttk.Label(app_page, text='Application Config Path:').grid(
            column=0,
            row=0,
            sticky=tk.W
        )
        self.app_config_path = ttk.Entry(
            app_page,
            textvariable=self.app_config_path_text,
            width=30
        )
        self.app_config_path.grid(
            column=1,
            row=0,
            sticky=(tk.E, tk.W)
        )
        # database page
        db_page = ttk.Frame(nb, padding=5)
        db_page.grid_columnconfigure(1, weight=1)

        # add the pages to our notebook
        nb.add(app_page, text="App Settings")
        nb.add(db_page, text="Database Settings")
        nb.grid(
            column=0,
            columnspan=3,
            row=0,
            pady=(0, 2),
            sticky=(tk.N, tk.E, tk.S, tk.W)
        )

        # status bar and save/close buttons
        self.status = ttk.Label(
            self,
            anchor=tk.E,
            textvariable=self.status_text
        )
        self.status.grid(
            column=0,
            row=1,
            sticky=(tk.E, tk.W)
        )
        self.save = ttk.Button(
            self,
            text="Save",
            state="disabled",
            command=self.save
        )
        self.save.grid(
            column=1,
            row=1,
            sticky=tk.E
        )

        ttk.Button(self, text="Close", command=self.close).grid(
            column=2,
            row=1,
            sticky=tk.E
        )

        # place and show the status page
        self.update()
        self.geometry("+{}+{}".format(
            self.master.winfo_x() + 50,
            self.master.winfo_y() + 50
        ))
        self.transient(self.master)
        self.deiconify()
        self.focus()

    def close(self):
        self.destroy()

    def save(self):
        self.status_text.set("Settings Saved")
        self.save.state(['disabled'])


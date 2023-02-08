import tkinter as tk
from tkinter import ttk
from .gui_settings import GuiSettings

class Settings(tk.Toplevel):
    def __init__(self, caller):
        super().__init__()
        self.caller = caller
        self.withdraw()
        self.status_text = tk.StringVar()
        self.db_path_text = tk.StringVar()
        self.backup_path_text = tk.StringVar()
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
        self.minsize(550,300)
        
        nb = ttk.Notebook(
            self,
            padding=5
        )
        # app page
        app_page = ttk.Frame(nb, padding=5)
        app_page.grid_columnconfigure(1, weight=1)

        ttk.Label(app_page, text='Database Path:').grid(
            column=0,
            row=0,
            sticky=tk.W
        )
        self.db_path = tk.Entry(
            app_page,
            textvariable=self.db_path_text
        )
        self.db_path.grid(
            column=1,
            row=0,
            sticky=(tk.E, tk.W),
            pady=5
        )

        ttk.Label(app_page, text='Backup Path:').grid(
            column=0,
            row=1,
            sticky=tk.W
        )
        self.backup_path = tk.Entry(
            app_page,
            textvariable=self.backup_path_text
        )
        self.backup_path.grid(
            column=1,
            row=1,
            sticky=(tk.W, tk.E)
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
        
        self.get_settings()
        self.db_path_text.trace_add('write', self.check_changes)
        self.backup_path_text.trace_add('write', self.check_changes)
        
        # place and show the status page
        self.update()
        self.geometry("+{}+{}".format(
            self.master.winfo_x() + 50,
            self.master.winfo_y() + 50
        ))
        self.transient(self.master)
        self.deiconify()
        self.focus()

    def get_settings(self):
        self.db_path_text.set(
            self.caller.controller.app_settings.get_app_setting('DBPATH')
        )
        self.backup_path_text.set(
            self.caller.controller.app_settings.get_app_setting('BACKUPPATH')
        )

    def check_changes(self, *args, clear_status=True):
        data_changed = False
        if clear_status:
            self.status_text.set("")

        if ( not self.backup_path.get() == 
                self.caller.controller.app_settings.get_app_setting('BACKUPPATH')):
            data_changed = True
            self.backup_path.config(bg="Yellow")
        else:
            self.backup_path.config(bg="White")
        
        if ( not self.db_path.get() == 
                self.caller.controller.app_settings.get_app_setting('DBPATH')):
            data_changed = True
            self.db_path.config(background="Yellow")
        else:
            self.db_path.config(background="White")
        
        if data_changed:
            self.save.state(['!disabled'])
        else:
            self.save.state(['disabled'])
            

    def close(self):
        self.destroy()

    def save(self):
        self.caller.controller.app_settings.update_app_setting(
            'DBPATH',
            self.db_path.get()
        )
        self.caller.controller.app_settings.update_app_setting(
            'BACKUPPATH',
            self.backup_path.get()
        )
        if self.caller.controller.app_settings.save():
            self.status_text.set("Settings Saved")
            self.save.state(['disabled'])
            self.check_changes(clear_status=False)
        else:
            self.status_text.set("Error Saving Settings")



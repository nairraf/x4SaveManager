import tkinter as tk
from tkinter import ttk, filedialog
from .gui_settings import GuiSettings
from .messages import MessageWindow
from .new_page_root import NewPageRoot
from os import path
from pathlib import PurePath
from modules.app import Validate

class Settings(NewPageRoot):
    def __init__(self, caller, controller):
        super().__init__(caller, controller)
        
        self.status_text = tk.StringVar()
        self.db_path_text = tk.StringVar()
        self.backup_path_text = tk.StringVar()
        self.x4save_path_text = tk.StringVar()
        self.backup_frequency_text = tk.StringVar()
        self.check_int_wrapper = (
            self.controller.register(Validate.integer_input),
            '%P'
        )

        self.set_title("Settings")
        
        self.minsize(650,300)
        
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
        ttk.Button(
            app_page,
            text='Browse',
            command=self.db_browse
        ).grid(
            column=2,
            row=0,
            sticky=tk.E,
            padx=2
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
        ttk.Button(
            app_page,
            text='Browse',
            command=self.backup_browse
        ).grid(
            column=2,
            row=1,
            sticky=tk.E,
            padx=2
        )

        ttk.Label(app_page, text='X4 Save Path:').grid(
            column=0,
            row=2,
            sticky=tk.W
        )
        self.x4save_path = tk.Entry(
            app_page,
            textvariable=self.x4save_path_text
        )
        self.x4save_path.grid(
            column=1,
            row=2,
            sticky=(tk.W, tk.E)
        )
        ttk.Button(
            app_page,
            text='Browse',
            command=self.X4save_browse
        ).grid(
            column=2,
            row=2,
            sticky=tk.E,
            padx=2
        )

        ttk.Label(app_page, text='Backup Frequency (sec):').grid(
            column=0,
            row=3,
            sticky=tk.W
        )
        self.backup_frequency = tk.Entry(
            app_page,
            textvariable=self.backup_frequency_text,
            validate='key',
            validatecommand=self.check_int_wrapper
        )
        self.backup_frequency.grid(
            column=1,
            row=3,
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
            columnspan=4,
            row=0,
            pady=(0, 2),
            sticky=(tk.N, tk.E, tk.S, tk.W)
        )

        # status bar and save/close buttons
        ttk.Label(
            self,
            anchor=tk.W,
            text="Config Version: {}, DB Version: {}".format(
                self.controller.app_settings.get_app_setting('VERSION'),
                self.controller.db.version
            )
        ).grid(
            column=0,
            row=1,
            sticky=(tk.W)
        )
        self.status = ttk.Label(
            self,
            anchor=tk.E,
            textvariable=self.status_text
        )
        self.status.grid(
            column=1,
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
            column=2,
            row=1,
            sticky=tk.E
        )

        ttk.Button(self, text="Close", command=self.close).grid(
            column=3,
            row=1,
            sticky=tk.E
        )
        
        self.get_settings()
        self.db_path_text.trace_add('write', self.check_changes)
        self.backup_path_text.trace_add('write', self.check_changes)
        self.x4save_path_text.trace_add('write', self.check_changes)
        self.backup_frequency_text.trace_add('write', self.check_changes)
        self.protocol("WM_DELETE_WINDOW", self.close)
        
        self.show_window()

    def get_settings(self):
        self.db_path_text.set(
            self.controller.app_settings.get_app_setting('DBPATH')
        )
        self.backup_path_text.set(
            self.controller.app_settings.get_app_setting('BACKUPPATH')
        )
        self.x4save_path_text.set(
            self.controller.app_settings.get_app_setting('X4SAVEPATH')
        )
        self.backup_frequency_text.set(
            self.controller.app_settings.get_app_setting('BACKUPFREQUENCY_SECONDS')
        )

    def check_changes(self, *args, clear_status=True):
        data_changed = False
        if clear_status:
            self.status_text.set("")

        if ( not Validate.text_input(self.backup_path.get()) == 
                self.controller.app_settings.get_app_setting('BACKUPPATH')
            ):
            data_changed = True
            self.backup_path.config(bg="Yellow")
        else:
            self.backup_path.config(bg="White")
        
        if ( not Validate.text_input(self.db_path.get()) == 
                self.controller.app_settings.get_app_setting('DBPATH')):
            data_changed = True
            self.db_path.config(background="Yellow")
        else:
            self.db_path.config(background="White")

        if ( not Validate.text_input(self.x4save_path.get()) == 
                self.controller.app_settings.get_app_setting('X4SAVEPATH')):
            data_changed = True
            self.x4save_path.config(background="Yellow")
        else:
            self.x4save_path.config(background="White")

        if ( len(self.backup_frequency.get()) > 0 and 
             not int(self.backup_frequency.get()) == 
             self.controller.app_settings.get_app_setting('BACKUPFREQUENCY_SECONDS')
            ):
            data_changed = True
            self.backup_frequency.config(background="Yellow")
        else:
            self.backup_frequency.config(background="White")

        if data_changed:
            self.save.state(['!disabled'])
        else:
            self.save.state(['disabled'])
            

    def close(self):
        if self.save.instate(['disabled']):
            self.destroy()
        else:
            MessageWindow(
                self,
                message="You have unsaved Changes.\nExit without saving changes?",
                type='question',
                canceltext="No",
                oktext="Yes"
            )

            if self.modalresult == 1:
                self.destroy()

    def save(self):
        self.controller.app_settings.update_app_setting(
            'DBPATH',
            self.db_path.get()
        )
        self.controller.app_settings.update_app_setting(
            'BACKUPPATH',
            self.backup_path.get()
        )
        self.controller.app_settings.update_app_setting(
            'X4SAVEPATH',
            self.x4save_path.get()
        )
        self.controller.app_settings.update_app_setting(
            'BACKUPFREQUENCY_SECONDS',
            int(self.backup_frequency.get())
        )
        if self.controller.app_settings.save():
            self.status_text.set("Settings Saved")
            self.save.state(['disabled'])
            self.check_changes(clear_status=False)
        else:
            self.status_text.set("Error Saving Settings")

    def db_browse(self):
        initialdir=PurePath(self.db_path_text.get()).parent.as_posix()
        folder=filedialog.askdirectory(
            mustexist=False,
            title="Database File Location",
            initialdir=initialdir
        )
        if not folder == '':
            folder=path.normpath(path.join(folder, "x4SaveManager.db"))
            self.db_path.delete(0,'end')
            self.db_path.insert(0, folder)

    def backup_browse(self):
        initialdir=PurePath(self.backup_path_text.get()).as_posix()
        folder=filedialog.askdirectory(
            mustexist=False,
            title="Backup Location",
            initialdir=initialdir
        )
        if not folder == '':
            folder=path.normpath(folder)
            self.backup_path.delete(0,'end')
            self.backup_path.insert(0, folder)

    def X4save_browse(self):
        initialdir=PurePath(self.x4save_path_text.get()).as_posix()
        folder=filedialog.askdirectory(
            mustexist=False,
            title="X4 Save Location",
            initialdir=initialdir
        )
        if not folder == '':
            folder=path.normpath(folder)
            self.x4save_path.delete(0,'end')
            self.x4save_path.insert(0, folder)


"""Main Application Settings Window
"""

import tkinter as tk
from tkinter import ttk, filedialog
from .messages import MessageWindow
from .new_page_root import NewPageRoot
from os import path
from pathlib import PurePath
from modules.app import Validate
from idlelib.tooltip import Hovertip

class Settings(NewPageRoot):
    """The main application settings window
    
    Responsible for managing all application settings
    Inherits from NewPageRoot
    """
    def __init__(self, caller, controller):
        """Constructor
        
        Args:
            caller (tk.Tk): caller object
            controller (WindowController): application controller
        """
        super().__init__(caller, controller)
        
        self.status_text = tk.StringVar()
        self.db_path_text = tk.StringVar()
        self.backup_path_text = tk.StringVar()
        self.old_backup_days_text = tk.StringVar()
        self.do_not_delete_backups_text = tk.StringVar()
        self.x4save_path_text = tk.StringVar()
        self.backup_frequency_text = tk.StringVar()
        self.check_int_wrapper = (
            self.controller.register(Validate.integer_input),
            '%P'
        )
        self.backup_pruning_var = tk.BooleanVar()
        self.backup_pruning_delete_var = tk.BooleanVar()
        self.delete_quicksaves_var = tk.BooleanVar()
        self.delete_autosaves_var = tk.BooleanVar()
        self.delete_saves_var = tk.BooleanVar()

        self.set_title("Settings")
        
        self.minsize(650,350)
        
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

        # database settings page
        backup_page = ttk.Frame(nb, padding=5)
        backup_page.grid_columnconfigure(1, weight=1)

        ttk.Label(backup_page, text='Backup Frequency (sec):').grid(
            column=0,
            row=0,
            sticky=tk.W
        )
        self.backup_frequency = tk.Entry(
            backup_page,
            textvariable=self.backup_frequency_text,
            validate='key',
            validatecommand=self.check_int_wrapper
        )
        self.backup_frequency.grid(
            column=1,
            row=0,
            sticky=(tk.W, tk.E)
        )
        Hovertip(
            self.backup_frequency,
            "The number of seconds to wait\nbefore checking for new X4 Save files"
        )

        pruning_frame = tk.LabelFrame(
            backup_page,
            text="Backup Pruning/Deletion settings"
        )
        pruning_frame.grid(
            column=0,
            columnspan=2,
            row=1,
            sticky=(tk.W, tk.N, tk.E, tk.S),
            pady=10,
        )

        tk.Label(pruning_frame, text="Old Backups (days): ").grid(
            column=0,
            row=0,
            pady=(5,2),
            sticky=tk.E
        )
        self.old_backup_days = tk.Entry(
            pruning_frame,
            textvariable=self.old_backup_days_text,
            validate='key',
            validatecommand=self.check_int_wrapper
        )
        self.old_backup_days.grid(
            column=1,
            row=0,
            sticky=(tk.W, tk.E)
        )
        Hovertip(
            self.old_backup_days,
            """Backups older than this amount of days
will be candidates for pruning.

NOTE: 
  backups that have their flag set will never be pruned."""
        )

        tk.Label(pruning_frame, text="Never prune the last backups:").grid(
            column=0,
            row=1,
            pady=2,
            sticky=tk.E
        )
        self.do_not_delete_backups = tk.Entry(
            pruning_frame,
            textvariable=self.do_not_delete_backups_text,
            validate='key',
            validatecommand=self.check_int_wrapper
        )
        self.do_not_delete_backups.grid(
            column=1,
            row=1,
            sticky=(tk.W, tk.E)
        )
        Hovertip(
            self.do_not_delete_backups,
        """Never prune this number of the latest backup files

NOTE: 
  backups that have their flag set will never be pruned."""
        )
        
        tk.Label(
            pruning_frame,
            text="Prune backups application startup"
        ).grid(
            column=0,
            row=2,
            pady=2,
            sticky=tk.E
        )
        self.backup_pruning = ttk.Checkbutton(
            pruning_frame,
            variable=self.backup_pruning_var,
            text='',
            command=self.flag_change
        )
        self.backup_pruning.grid(
            column=1,
            row=2,
            sticky=(tk.W, tk.E)
        )
        Hovertip(
            self.backup_pruning,
            """Should Pruning be run at application startup?

Note:
  Backups that are candidates for deletion will be marked
  for deletion by the pruning process.

  You can view all backups that have been marked for deletion
  in the __RECYCLE BIN__.
"""
        )

        tk.Label(
            pruning_frame,
            text="Delete marked backups\nat application startup"
        ).grid(
            column=0,
            row=3,
            pady=2,
            sticky=tk.E
        )
        self.backup_pruning_delete = ttk.Checkbutton(
            pruning_frame,
            variable=self.backup_pruning_delete_var,
            text='',
            command=self.flag_change
        )
        self.backup_pruning_delete.grid(
            column=1,
            row=3,
            sticky=(tk.W, tk.E)
        )
        Hovertip(
            self.backup_pruning_delete,
            """Should all marked backups be deleted application startup?

Note:
  Backups that are candidates for deletion will be marked
  for deletion by the pruning process.

  You can view all backups that have been marked for deletion
  in the __RECYCLE BIN__."""
        )
        tk.Label(
            pruning_frame,
            text="Delete Quick Save Backups:"
        ).grid(
            column=0,
            row=4,
            pady=2,
            sticky=tk.E
        )
        self.delete_quicksaves = ttk.Checkbutton(
            pruning_frame,
            variable=self.delete_quicksaves_var,
            text='',
            command=self.flag_change
        )
        self.delete_quicksaves.grid(
            column=1,
            row=4,
            sticky=(tk.W, tk.E)
        )
        Hovertip(
            self.delete_quicksaves,
            "Should backups of X4 quicksaves be eligiable for pruning/deletion?"
        )

        tk.Label(
            pruning_frame,
            text="Delete Auto Save Backups:"
        ).grid(
            column=0,
            row=5,
            pady=2,
            sticky=tk.E
        )
        self.delete_autosaves = ttk.Checkbutton(
            pruning_frame,
            variable=self.delete_autosaves_var,
            text='',
            command=self.flag_change
        )
        self.delete_autosaves.grid(
            column=1,
            row=5,
            sticky=(tk.W, tk.E)
        )
        Hovertip(
            self.delete_autosaves,
            "Should backups of X4 autosaves be eligiable for pruning/deletion?"
        )

        tk.Label(
            pruning_frame,
            text="Delete Normal Save Backups:"
        ).grid(
            column=0,
            row=6,
            pady=2,
            sticky=tk.E
        )
        self.delete_saves = ttk.Checkbutton(
            pruning_frame,
            variable=self.delete_saves_var,
            text='',
            command=self.flag_change
        )
        self.delete_saves.grid(
            column=1,
            row=6,
            sticky=(tk.W, tk.E)
        )
        Hovertip(
            self.delete_saves,
            """Should backups of X4 normal saves be eligiable for pruning/deletion?
            
Note:
  Normal saves are the save_001 through save_010 X4 saves.
  In the X4 load screen, these correlate to the 1 through 10 save slots"""
        )

        # add the pages to our notebook
        nb.add(app_page, text="App Settings")
        nb.add(backup_page, text="Backup Settings")
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
        self.old_backup_days_text.trace_add('write', self.check_changes)
        self.do_not_delete_backups_text.trace_add('write', self.check_changes)
        self.protocol("WM_DELETE_WINDOW", self.close)
        
        self.show_window()

    def get_settings(self):
        """Gets the current settings from the JSON file
        
        Populates the widgets with the corresponding setting
        """
        self.db_path_text.set(
            self.controller.app_settings.get_app_setting('DBPATH')
        )
        self.backup_path_text.set(
            self.controller.app_settings.get_app_setting('BACKUPPATH')
        )
        self.x4save_path_text.set(
            self.controller.app_settings.get_app_setting('X4SAVEPATH')
        )
        self.old_backup_days_text.set(
            self.controller.app_settings.get_app_setting(
                'DELETE_OLD_DAYS',
                category='BACKUP'
            )
        )
        self.do_not_delete_backups_text.set(
            self.controller.app_settings.get_app_setting(
                'DO_NOT_DELETE_LAST',
                category='BACKUP'
            )
        )
        self.backup_frequency_text.set(
            self.controller.app_settings.get_app_setting(
                'BACKUPFREQUENCY_SECONDS',
                category="BACKUP"
            )
        )
        self.delete_quicksaves_var.set(
            self.controller.app_settings.get_app_setting(
                "DELETE_QUICKSAVES",
                category="BACKUP"
            )
        )
        self.delete_autosaves_var.set(
            self.controller.app_settings.get_app_setting(
                "DELETE_AUTOSAVES",
                category="BACKUP"
            )
        )
        self.delete_saves_var.set(
            self.controller.app_settings.get_app_setting(
                "DELETE_SAVES",
                category="BACKUP"
            )
        )
        self.backup_pruning_var.set(
            self.controller.app_settings.get_app_setting(
                "PRUNE_MARK_DELETION",
                category="BACKUP"
            )
        )
        self.backup_pruning_delete_var.set(
            self.controller.app_settings.get_app_setting(
                "PRUNE_DELETE",
                category="BACKUP"
            )
        )

    def check_changes(self, *args, clear_status=True):
        """callback to detect changes and enable/disable the save button

        Args:
            clear_status (bool): a flag to clear the setting page status text
        """
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

        if ( len(self.backup_frequency.get()) > 0 
             and not int(self.backup_frequency.get()) == 
             self.controller.app_settings.get_app_setting(
                'BACKUPFREQUENCY_SECONDS',
                category="BACKUP"
             )
           ):
            data_changed = True
            self.backup_frequency.config(background="Yellow")
        else:
            self.backup_frequency.config(background="White")

        if ( len(self.old_backup_days.get()) > 0 
             and not int(self.old_backup_days.get()) == 
             self.controller.app_settings.get_app_setting(
                'DELETE_OLD_DAYS',
                category="BACKUP"
             )
           ):
            data_changed = True
            self.old_backup_days.config(background="Yellow")
        else:
            self.old_backup_days.config(background="White")

        if ( len(self.do_not_delete_backups.get()) > 0 
             and not int(self.do_not_delete_backups.get()) == 
             self.controller.app_settings.get_app_setting(
                'DO_NOT_DELETE_LAST',
                category="BACKUP"
             )
           ):
            data_changed = True
            self.do_not_delete_backups.config(background="Yellow")
        else:
            self.do_not_delete_backups.config(background="White")

        if (
            self.controller.app_settings.get_app_setting(
                "DELETE_QUICKSAVES",
                category="BACKUP"
            ) != self.delete_quicksaves_var.get()
        ):
            data_changed = True

        if (
            self.controller.app_settings.get_app_setting(
                "DELETE_AUTOSAVES",
                category="BACKUP"
            ) != self.delete_autosaves_var.get()
        ):
            data_changed = True

        if (
            self.controller.app_settings.get_app_setting(
                "DELETE_SAVES",
                category="BACKUP"
            ) != self.delete_saves_var.get()
        ):
            data_changed = True
        
        if (
            self.controller.app_settings.get_app_setting(
                "PRUNE_MARK_DELETION",
                category="BACKUP"
            ) != self.backup_pruning_var.get()
        ):
            data_changed = True

        if (
            self.controller.app_settings.get_app_setting(
                "PRUNE_DELETE",
                category="BACKUP"
            ) != self.backup_pruning_delete_var.get()
        ):
            data_changed = True

        if data_changed:
            self.save.state(['!disabled'])
        else:
            self.save.state(['disabled'])
            
    def flag_change(self):
        """Callback for the checkboxes on change
        """
        self.check_changes()
    
    def close(self):
        """Checks for changes and closes the settings window
        """
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
        """callback for the save button
        
        persists changes to the DB
        """
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
            int(self.backup_frequency.get()),
            category="BACKUP"
        )
        self.controller.app_settings.update_app_setting(
            'DELETE_OLD_DAYS',
            int(self.old_backup_days.get()),
            category="BACKUP"
        )
        self.controller.app_settings.update_app_setting(
            'DO_NOT_DELETE_LAST',
            int(self.do_not_delete_backups.get()),
            category="BACKUP"
        )
        self.controller.app_settings.update_app_setting(
            'DELETE_QUICKSAVES',
            self.delete_quicksaves_var.get(),
            category="BACKUP"
        )
        self.controller.app_settings.update_app_setting(
            'DELETE_AUTOSAVES',
            self.delete_autosaves_var.get(),
            category="BACKUP"
        )
        self.controller.app_settings.update_app_setting(
            'DELETE_SAVES',
            self.delete_saves_var.get(),
            category="BACKUP"
        )
        self.controller.app_settings.update_app_setting(
            'PRUNE_MARK_DELETION',
            self.backup_pruning_var.get(),
            category="BACKUP"
        )
        self.controller.app_settings.update_app_setting(
            'PRUNE_DELETE',
            self.backup_pruning_delete_var.get(),
            category="BACKUP"
        )
        if self.controller.app_settings.save():
            self.status_text.set("Settings Saved")
            self.save.state(['disabled'])
            self.check_changes(clear_status=False)
            self.controller.startpage.progress['maximum'] = int(self.backup_frequency.get())
        else:
            self.status_text.set("Error Saving Settings")

    def db_browse(self):
        """OS folder browser to change and browse to the new database folder
        """
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
        """OS folder browser to change and browse to the new backup root folder
        """
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
        """OS folder browser to change and browse to the X4 save parent folder
        """
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


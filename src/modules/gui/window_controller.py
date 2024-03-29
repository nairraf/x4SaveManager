"""WindowController Definition

The WindowController is the entrypoint and main controller for the application
and is responsible for creating/managing the main GUI page as well
as the main Tk event loop.

Example:
    import sys
    import os.path as path
    from modules.gui import WindowController

    approot = path.realpath(path.dirname(__file__))
    moduleroot = path.join(approot, "modules")
    sys.path.append(moduleroot)

    WindowController(approot, moduleroot)
"""
import tkinter as tk
import modules.app as appmod
import modules.gui as guimod
import json
import webbrowser
from os import path as ospath
from queue import Queue
from urllib.request import urlopen

class WindowController(tk.Tk):
    """This class creates the main application window and is responsible
    for creating the core layout for the GUI

    Args:
        tk (tk.Tk): inherits from tk.Tk
    """

    def __init__(self, approot, moduleroot):
        """Initializes a new instance of WindowController

        Args:
            approot (str): filesystem full path of the application root folder
            moduleroot (str): filesystem path to the modules folder
        """
        super().__init__()
        self.message_queue = Queue()
        self.approot = approot
        self.moduleroot = moduleroot
        self.modalresult = 0
        self.app_settings = appmod.AppSettings(self)
        self.db = appmod.Model(self, self.app_settings.get_app_setting("DBPATH"))
        self.selected_playthrough = None
        self.delete_selected = False
        self.save_manager = appmod.SaveManager(self)
        self.playthrough_manager = appmod.PlaythroughManager(self)
        try:
            with open(ospath.join(approot,'credits.json'), 'r') as f:
                self.credits = json.load(f)

            with open(ospath.join(approot,'version.json'), 'r') as f:
                self.version = json.load(f)
        except Exception as e:
            self.show_error(e)

        guimod.GuiSettings.icon_path = ospath.join(
            ospath.join(approot, "img"), "icon.ico"
        )
        self.iconpath = guimod.GuiSettings.icon_path
        self.iconbitmap(self.iconpath)

        # we set the root window row and column to be responsive
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.minsize(width=900, height=450)
        self.option_add('*tearOff', False)

        # we place a frame which is the size of the entire window, which is the
        # parent to all other page part objects. we also make this root level
        # content frame to be reponsive, and make the content container
        # grow and shrink with all window regions
        self.content = tk.Frame(self)
        self.content.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=1)
        self.content.grid(column=0, row=0, sticky=(tk.N, tk.E, tk.S, tk.W))

        # all pages parts should inherit from tk.Frame and
        # use self.content as their parent and take a second
        # argument to pass the WindowController instance (self)
        self.top_menu = guimod.MainMenu(self)
        self.startpage = guimod.StartPage(self.content, self)
        self.statusbar = guimod.StatusBar(self.content, self)

        self.set_window_title()
        
        if self.app_settings.get_app_setting('X4SAVEPATH') == 'None':
            msg = "Could not detect default X4 save location.\nPlease set the path for the X4 Save location in settings."
            self.show_error(msg)
        self.bind_events()
        self.check_update()
        if self.app_settings.get_app_setting('PRUNE_MARK_DELETION', category='BACKUP'):
            self.save_manager.mark_old_backups(silent=True)
        if self.app_settings.get_app_setting('PRUNE_DELETE', category='BACKUP'):
            self.save_manager.delete_backups(silent=True)
        self.startup()

    def set_window_title(self, text=""):
        """Sets the window title
        """
        if not text:
            self.title(f"{guimod.GuiSettings.window_title}")
        else:
            self.title(f"{guimod.GuiSettings.window_title} - {text}")

    def set_cursor(self, type):
        """Changes the mouse cursor to the specified type
        """
        self.config(cursor=type)
        self.update()

    def startup(self):
        """starts the main window TK event loop
        """
        self.mainloop()

    def show_error(self, message):
        """wrapper for MessageWindow to display application level error windows
        """
        guimod.MessageWindow(
            self,
            message,
            type="error"
        )

    def show_message(self, message):
        """wrapper for MessageWindow to display application level info windows
        """
        guimod.MessageWindow(
            self,
            message
        )

    def check_modal(self):
        """used to detect the answers to questions from show_question()
        """
        if self.modalresult==1:
            self.modalresult=0
            return True
        
        return False

    def show_question(
        self,
        message,
        oktext="Yes",
        canceltext="No"
    ):
        """wrapper for MessageWindow to display application level question windows
        """
        guimod.MessageWindow(
            self,
            message=message,
            type="question",
            oktext=oktext,
            canceltext=canceltext
        )
    
    def bind_events(self):
        """main application level event bindings
        """
        self.bind(
            "<<UpdateBackupProgress>>",
            lambda e: self.startpage.increment_progress()
        )
        self.bind(
            "<<BackupIdle>>",
            lambda e: self.statusbar.set_backup_status('idle')
        )
        self.bind(
            "<<BackupRunning>>",
            lambda e: self.statusbar.set_backup_status('backup running')
        )
        self.bind(
            "<<ImportingBackups>>",
            lambda e: self.statusbar.set_backup_status('Importing and Re-indexing Previous Backups')
        )
        self.bind(
            "<<BackupThreadStarted>>",
            lambda e: self.statusbar.set_backup_status('waiting for new save files')
        )
        self.bind(
            "<<NewQueueData>>",
            lambda e: self.startpage.update_backup_data()
        )
        self.bind(
            "<<RefreshBackupTreeview>>",
            lambda e: self.startpage.populate_tree()
        )
        self.protocol("WM_DELETE_WINDOW", self.close)

    def close(self):
        """Responsible for closing the main window"""
        # if the main GUI is closed, check for a running backup process
        # and cancel it
        if self.save_manager.backup_in_progress:
            self.save_manager.cancel_backup.set()
        self.destroy()

    def check_update(self, feedback=False):
        try:
            version_url = "https://raw.githubusercontent.com/nairraf/x4SaveManager/main/src/version.json"
            version_check = json.loads(urlopen(version_url).read())
            latest_version = float(version_check['version'])
            cur_version = float(self.version['version'])
            question = """A new version of xSaveManager is available.
Would you like to view the latest relases on the Github project page?"""
            if cur_version < latest_version:
                self.show_question(question)
                if self.modalresult:
                    self.open_url("https://github.com/nairraf/x4SaveManager/releases")
                    self.modalresult = 0
            elif cur_version == latest_version:
                if feedback:
                    self.show_message("You are on the latest version")
        except Exception as e:
            self.show_error("An Error occured while checking for updates")

    def open_url(self, url):
        webbrowser.open_new_tab(url)

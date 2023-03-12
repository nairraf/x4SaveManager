"""the main application menu"""

from __future__ import annotations
from typing import TYPE_CHECKING

import tkinter as tk
from tkinter import Menu
from .settings_page import Settings
from .playthrough_page import Playthrough
from .about_page import About

if TYPE_CHECKING:
    from modules.gui import WindowController

class MainMenu():
    """Binds the main menu to the root window
    """
    def __init__(self, controller: WindowController):
        """Creates the main menu and binds it to the root app window

        Args:
            controller (tk.Tk): the window_controller object
        """
        self.controller = controller
        self.settings = None
        self.about = None
        self.add_playthrough = None
        #create our top level menu's
        menubar = Menu(controller)
        self.controller['menu'] = menubar
        self.menu_file = Menu(menubar)
        self.menu_edit = Menu(menubar)
        self.menu_backup = Menu(menubar)
        self.menu_help = Menu(menubar)

        menubar.add_cascade(menu=self.menu_file, label='File')
        menubar.add_cascade(menu=self.menu_edit, label='Edit')
        menubar.add_cascade(menu=self.menu_backup, label='Backup')
        menubar.add_cascade(menu=self.menu_help, label='Help')

        # file menu
        self.menu_file.add_command(
            label='Create Playthrough',
            command=self.open_add_playthrough
        )
        self.menu_file.add_separator()
        self.menu_file.add_command(label='Exit', command=self.controller.destroy)

        # edit menu
        self.menu_edit.add_command(
            label='Edit Selected Playthrough',
            command=self.edit_playthrough
        )
        self.menu_edit.add_command(
            label='Delete Selected Playthrough',
            command=self.delete_playthrough
        )
        self.menu_edit.add_separator()
        self.menu_edit.add_command(label='Settings', command=self.open_settings)

        # backup menu
        self.menu_backup.add_command(
            label='Start Backup',
            command=self.start_backup,
            state='disabled'
        )
        self.menu_backup.add_command(
            label='Stop Backup',
            command=self.stop_backup,
            state='disabled'
        )
        self.menu_backup.add_separator()
        self.menu_backup.add_command(
            label='Mark Old Backups For Deletion',
            command=self.mark_old_backups
        )
        self.menu_backup.add_command(
            label='Delete Marked Backups',
            command=self.delete_backups
        )

        # help menu
        self.menu_help.add_command(
            label='Check Update',
            command=self.check_update
        )
        self.menu_help.add_separator()
        self.menu_help.add_command(
            label='About',
            command=self.open_about
        )

    def mark_old_backups(self):
        self.controller.save_manager.mark_old_backups()
        self.controller.startpage.populate_tree()

    def delete_backups(self):
        self.controller.save_manager.delete_backups()
        self.controller.startpage.populate_tree()
    
    def delete_playthrough(self):
        self.controller.playthrough_manager.delete_playthrough()
    
    def open_settings(self):
        """Open the application settings window
        """
        if self.settings == None:
            self.settings = Settings(self, self.controller)
            self.settings.bind('<Destroy>', self.settings_closed)
        else:
            self.settings.focus()

    def settings_closed(self, *args):
        """callback when the settings window closes
        we track if the window is open or not
        so we will only one window at a time
        """
        self.settings = None

    def open_about(self):
        """Opens the about window
        """
        if self.about == None:
            self.about = About(self, self.controller)
            self.about.bind('<Destroy>', self.about_closed)
        else:
            self.about.focus()

    def about_closed(self, *args):
        """callback when the about window closes
        we track if the window is open or not
        so we will only one window at a time
        """
        self.about = None

    def check_update(self):
        self.controller.check_update(feedback=True)

    def open_add_playthrough(self):
        """Open the add playthrough window
        """
        if self.add_playthrough == None:
            self.add_playthrough = Playthrough(self, self.controller)
            self.add_playthrough.bind('<Destroy>', self.add_playthrough_closed)
        else:
            self.add_playthrough.focus()

    def add_playthrough_closed(self, *args):
        """tracks if the add playthrough window is already open
        """
        self.add_playthrough = None

    def edit_playthrough(self):
        """opens the edit playthrough window
        """
        self.controller.startpage.edit_selected_playthrough()

    def start_backup(self):
        """Starts the backup thread for the currently selected playthrough
        """
        self.controller.save_manager.start_backup()
        self.menu_backup.entryconfigure('Start Backup', state='disabled')
        self.menu_backup.entryconfigure('Stop Backup', state='normal')

    def stop_backup(self):
        """stops the currently running backup thread
        """
        self.controller.save_manager.stop_backup()
        self.menu_backup.entryconfigure('Start Backup', state='normal')
        self.menu_backup.entryconfigure('Stop Backup', state='disabled')
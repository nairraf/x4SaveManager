import tkinter as tk
from tkinter import Menu
from .settings_page import Settings
from .playthrough_page import Playthrough

class MainMenu():
    """Binds the main menu to the root window
    """
    def __init__(self, controller):
        """Creates the main menu and binds it to the root app window

        Args:
            controller (tk.Tk): the window_controller object
        """
        self.controller = controller
        self.settings = None
        self.add_playthrough = None
        #create our top level menu's
        menubar = Menu(controller)
        self.controller['menu'] = menubar
        menu_file = Menu(menubar)
        menu_edit = Menu(menubar)
        menu_backup = Menu(menubar)
        menubar.add_cascade(menu=menu_file, label='File')
        menubar.add_cascade(menu=menu_edit, label='Edit')
        menubar.add_cascade(menu=menu_backup, label='Backup')

        # file menu
        menu_file.add_command(
            label='Create Playthrough',
            command=self.open_add_playthrough
        )
        menu_file.add_separator()
        menu_file.add_command(label='Exit', command=self.controller.destroy)

        # edit menu
        menu_edit.add_command(
            label='Edit Selected Playthrough',
            command=self.edit_playthrough
        )
        menu_edit.add_command(
            label='Delete Selected Playthrough',
            command=self.delete_playthrough
        )
        menu_edit.add_separator()
        menu_edit.add_command(label='Settings', command=self.open_settings)

        # backup menu
        menu_backup.add_command(
            label='Start Backup',
            command=self.start_backup
        )


    def delete_playthrough(self):
        if self.controller.selected_playthrough:
            self.controller.show_question(
                "Are you sure you want to delete Playthrough:\n{}".format(
                    self.controller.selected_playthrough["name"]
                )
            )
            
            if self.controller.check_modal():
                if self.controller.db.delete_playthrough_by_name(
                    self.controller.selected_playthrough["name"]
                ):
                    self.controller.show_message(
                        "Playthrough {} has been deleted".format(
                            self.controller.selected_playthrough["name"]
                        )
                    )
                    self.controller.selected_playthrough = None
                    self.controller.startpage.refresh_playthroughs()
                    self.controller.startpage.playthroughs.selection_clear(0)
                    self.controller.statusbar.set_playthrough("None")
                    self.controller.startpage.set_notes("")
    
    def open_settings(self):
        if self.settings == None:
            self.settings = Settings(self, self.controller)
            self.settings.bind('<Destroy>', self.settings_closed)
        else:
            self.settings.focus()

    def settings_closed(self, *args):
        self.settings = None

    def open_add_playthrough(self):
        if self.add_playthrough == None:
            self.add_playthrough = Playthrough(self, self.controller)
            self.add_playthrough.bind('<Destroy>', self.add_playthrough_closed)
        else:
            self.add_playthrough.focus()

    def add_playthrough_closed(self, *args):
        self.add_playthrough = None

    def edit_playthrough(self):
        self.controller.startpage.edit_selected_playthrough()

    def start_backup(self):
        if self.controller.selected_playthrough:
            self.controller.show_message('starting backup for playthrough:\n{}'.format(
                self.controller.selected_playthrough['name']
            ))

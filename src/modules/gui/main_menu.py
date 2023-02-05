import tkinter as tk
from tkinter import Menu
from .settings_page import Settings

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
        #create our top level menu's
        menubar = Menu(controller)
        self.controller['menu'] = menubar
        menu_file = Menu(menubar)
        menu_edit = Menu(menubar)
        menubar.add_cascade(menu=menu_file, label='File')
        menubar.add_cascade(menu=menu_edit, label='Edit')

        # file menu
        menu_file.add_separator()
        menu_file.add_command(label='Exit', command=self.controller.destroy)

        # edit menu
        menu_edit.add_command(label='Settings', command=self.open_settings)

    def open_settings(self):
        if self.settings == None:
            self.settings = Settings(self)
            self.settings.bind('<Destroy>', self.settings_closed)
        else:
            self.settings.focus()

    def settings_closed(self, *args):
        self.settings = None

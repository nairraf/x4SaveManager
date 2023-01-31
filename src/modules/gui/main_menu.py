import tkinter as tk
from tkinter import Menu

class MainMenu():
    def __init__(self, root):
        self.root = root
        #create our top level menu's
        menubar = Menu(root)
        self.root['menu'] = menubar
        menu_file = Menu(menubar)
        menu_edit = Menu(menubar)
        menubar.add_cascade(menu=menu_file, label='File')
        menubar.add_cascade(menu=menu_edit, label='Edit')

        # file menu
        menu_file.add_separator()
        menu_file.add_command(label='Exit', command=self.exit)

    def exit(self):
        self.root.destroy()

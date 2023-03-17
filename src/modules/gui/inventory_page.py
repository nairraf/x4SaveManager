"""Inventory Class

Responsible for showing the inventory to backup mapping
"""
import tkinter as tk
from tkinter import ttk
from .new_page_root import NewPageRoot
from os import path

class Inventory(NewPageRoot):
    """shows the X4 save to backup mapping
    """
    def __init__(self, caller, controller):
        """Constructor
        
        Args:
            caller (tk.Tk): the caller object
            controller (WindowController): the application controller
        """
        super().__init__(caller, controller)

        self.set_title("X4 Saves to backup mapping")

        self.minsize(800,300)

        tree_frame = tk.Frame(
            self
        )
        tree_frame.grid(
            column=0,
            row=0,
            sticky=(tk.W, tk.N, tk.E, tk.S)
        )
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        columns = (
            'Playthrough',
            'BackupFile',
            'SaveTime',
            'Playtime',
            'Branch',
            'Character',
            'Money',
            'Notes'
        )
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            displaycolumns=columns
        )
        self.tree.grid(
            column=0,
            row=0,
            sticky=(tk.N, tk.E, tk.S, tk.W)
        )

        self.tree.column('Playthrough', width=160, anchor='w')
        self.tree.heading('Playthrough', text='Playthrough')
        self.tree.column('BackupFile', width=180, anchor='w')
        self.tree.heading('BackupFile', text='BackupFile')
        self.tree.column('SaveTime', width=160, anchor='w')
        self.tree.heading('SaveTime', text='SaveTime')
        self.tree.column('Playtime', width=60, anchor='w')
        self.tree.heading('Playtime', text='Hours')
        self.tree.column('Branch', width=80, anchor='w')
        self.tree.heading('Branch', text='Branch')
        self.tree.column('Character', width=80, anchor='w')
        self.tree.heading('Character', text='Character')
        self.tree.column('Money', width=100, anchor='w')
        self.tree.heading('Money', text='Money')
        self.tree.column('Notes', width=200, anchor='w')
        self.tree.heading('Notes', text='Notes')

        # display the window, show a wait cursor and populate the page
        # the window must be displayed in order for the wait cursor to be
        # displayed
        self.controller.set_cursor(type="wait")
        self.show_window()
        self.populate_tree()
        self.controller.set_cursor(type='')
        

    def populate_tree(self):
        # populate the tree with saves that match the selected playthrough
        for save in self.controller.save_manager.inventory_saves():
            if save['backup']:
                playthrough = self.controller.db.get_playthrough_by_id(
                    save['backup']['playthrough_id']
                )['name']
                self.tree.insert('', 'end', text=save['save_file'].name, values=(
                    playthrough,
                    save['backup']['backup_filename'],
                    save['backup']['x4_save_time'],
                    "{:0.2f}".format(save['backup']['playtime']/60/60),
                    save['backup']['branch'],
                    save['backup']['character_name'],
                    "${:,.0f}".format(save['backup']['money']),
                    save['backup']['notes'].partition('\n')[0]
                ))
            else:
                self.tree.insert('', 'end', text=save['save_file'].name, values=(
                    '',
                    'None',
                    '',
                    '',
                    '',
                    '',
                    '',
                    ''
                ))

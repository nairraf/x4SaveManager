"""Definition for the StartPage Class
"""
from __future__ import annotations
from typing import TYPE_CHECKING

import tkinter as tk
from tkinter import ttk
from modules.app import Validate
from .messages import MessageWindow
from .playthrough_page import Playthrough

if TYPE_CHECKING:
    from modules.gui import WindowController

class StartPage(ttk.Frame):
    """Builds the main application page

    Args:
        tk (Frame): inherits from tk.Frame
    """

    def __init__(self, parent, controller: WindowController, **kwargs):
        """initializes the StatusPage

        Args:
            parent (tk.Frame): the parent tk container object
            controller (WindowController): the WindowController instance
        """
        super().__init__(parent, **kwargs)
        self._parent = parent
        self.controller = controller
        self.playthrough_var = tk.StringVar()
        self.playthrousghs_var = tk.StringVar()
        self.modalresult = None
        self.progressbar_count = 0
        self.build_page()
        self.refresh_playthroughs()

    def build_page(self):
        """builds the main start page
        """
        # 3 columns, sticky on all sides to be responsive
        # with a little inner padding
        self.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.S, tk.N))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        # padding = W, N, E, S
        # 25 padding at the bottom to float above the status bar
        self['padding'] = (10,5,10,25)
        # backup frame is only displayed during a backup
        self.backup_frame = tk.Frame(
            self
        )
        self.backup_frame.grid_forget()
        self.backup_frame.grid_columnconfigure(0, weight=1)
        self.progress = ttk.Progressbar(
            self.backup_frame,
            orient="horizontal",
            mode="determinate",
            maximum=10
        )
        self.progress.grid(
            column=0,
            row=0,
            sticky=(tk.W, tk.E),
            padx=5,
            pady=5
        )
        # add a main pane with two sides for resizable East and West sections
        self.pane = tk.PanedWindow(
            self,
            orient='horizontal',
            sashpad=2,
            handlepad=50,
            handlesize=7,
            showhandle=False,
            sashrelief='flat'
        )
        self.pane.grid(
            column=0,
            row=0,
            sticky=(tk.N, tk.E, tk.S, tk.W)
        )

        # create playthrough section
        lframe=ttk.Frame(
            self.pane
        )
        lframe.grid_columnconfigure(0, weight=1)
        lframe.grid_rowconfigure(1, weight=1)
        
        entry_frame = ttk.LabelFrame(lframe, text="Create Playthrough")
        entry_frame.grid_columnconfigure(1, weight=1)
        entry_frame.grid(
            column=0,
            row=0,
            ipadx=5,
            ipady=3,
            sticky=(tk.W, tk.E, tk.N)
        )
        entry_label = ttk.Label(entry_frame, text="Name:")
        entry_label.grid(
            column=0,
            row=0,
            sticky=tk.E
        )
        self.entry = ttk.Entry(
            entry_frame,
            textvariable=self.playthrough_var
        )
        self.entry.grid(
            column=1,
            row=0,
            padx=2,
            sticky=(tk.E, tk.W)
        )
        entry_button = ttk.Button(
            entry_frame,
            text="Create",
            command=self.create_playthrough
        )
        entry_button.grid(
            column=2,
            row=0,
            padx=2
        )
        # Playthrough Listbox
        playthrough_frame = ttk.LabelFrame(
           lframe,
           text='Playthroughs',
           padding=5
        )
        playthrough_frame.grid(
           column=0,
           row=1,
           sticky=(tk.W, tk.N, tk.S, tk.E)
        )
        playthrough_frame.grid_rowconfigure(0, weight=1)
        playthrough_frame.grid_columnconfigure(0, weight=1)
        self.playthroughs = tk.Listbox(
            playthrough_frame,
            listvariable=self.playthrousghs_var
        )
        self.playthroughs.grid(
            column=0,
            row=0,
            sticky=(tk.N, tk.E, tk.S, tk.W)
        )
        scrollbar = ttk.Scrollbar(
            playthrough_frame,
            orient='vertical',
            command=self.playthroughs.yview
        )
        self.playthroughs['yscrollcommand'] = scrollbar.set
        scrollbar.grid(
            column=1,
            row=0,
            sticky=(tk.N, tk.S)
        )

        self.playthroughs.bind("<<ListboxSelect>>", self.select_playthrough)
        self.playthroughs.bind("<Double-1>", self.edit_playthrough)

        # details section
        details_frame = ttk.LabelFrame(
            self.pane,
            text='Details',
            padding=5
        )
        details_frame.grid_rowconfigure(1, weight=1)
        details_frame.grid_columnconfigure(0, weight=1)
        details_frame.grid(
            column=2,
            row=0,
            rowspan=2,
            sticky=(tk.N, tk.E, tk.S, tk.W)
        )
        notes_frame=tk.Frame(details_frame)
        notes_frame.columnconfigure(0, weight=1)
        notes_frame.grid(
            column=0,
            row=0,
            sticky=(tk.E, tk.W),
            pady=(0,5)
        )
        self.notes = tk.Text(
            notes_frame,
            height=8,
            state='disabled',
            bg='#EEE',
            wrap='none'
        )
        self.notes.grid(
            column=0,
            row=0,
            sticky=(tk.W, tk.E)
        )
        notes_v_scroll = ttk.Scrollbar(
            notes_frame,
            orient='vertical',
            command=self.notes.yview
        )
        self.notes['yscrollcommand'] = notes_v_scroll.set
        notes_v_scroll.grid(
            column=1,
            row=0,
            sticky=(tk.N, tk.S)
        )

        notes_h_scroll = ttk.Scrollbar(
            notes_frame,
            orient='horizontal',
            command=self.notes.xview
        )
        self.notes['xscrollcommand'] = notes_h_scroll.set
        notes_h_scroll.grid(
            column=0,
            columnspan=2,
            row=1,
            sticky=(tk.W, tk.E)
        )

        tree = ttk.Treeview(
            details_frame
        )
        tree.grid(
            column=0,
            row=1,
            sticky=(tk.N, tk.E, tk.S, tk.W)
        )

        # add our root level frames to each side
        self.pane.add(lframe, minsize=250)
        self.pane.add(details_frame, minsize=200)

    def create_playthrough(self):
        """saves the new playthrough name
        """
        txt = Validate.text_input(self.playthrough_var.get())
        if txt:
            Playthrough(self, self.controller, txt)
            self.entry.delete(0,'end')
    
    def refresh_playthroughs(self):
        self.playthrousghs_var.set(
            self.controller.db.get_playthrough_names()
        )
    
    def select_playthrough(self, event):
        if event:
            cur_selection = event.widget.curselection()
            if cur_selection:
                index = cur_selection[0]
                name = event.widget.get(index)
                if hasattr(self.controller, 'statusbar'):
                    self.controller.statusbar.set_playthrough(name)
                self.controller.selected_playthrough = self.controller.db.get_playthrough_by_name(name)
                self.set_notes(self.controller.selected_playthrough['notes'])
                self.controller.top_menu.menu_backup.entryconfigure('Start Backup', state='normal')
    
    def edit_playthrough(self, event):
        if event:
            cur_selection = event.widget.curselection()
            if cur_selection:
                index = cur_selection[0]
                name = event.widget.get(index)
                Playthrough(self, self.controller, name=name)

    def edit_selected_playthrough(self):
        if self.controller.selected_playthrough:
            Playthrough(
                self,
                self.controller,
                name=self.controller.selected_playthrough['name']
            )

    def set_notes(self, note):
        self.notes.configure(state='normal')
        self.notes.delete('1.0', tk.END)
        self.notes.insert('1.0', note)
        self.notes.configure(state='disabled')

    def show_backup_frame(self):
        self.pane.grid_forget()
        self.backup_frame.grid(
            column=0,
            row=0,
            sticky=(tk.N, tk.E, tk.S, tk.W)
        )

    def hide_backup_frame(self):
        self.backup_frame.grid_forget()
        self.pane.grid(
            column=0,
            row=0,
            sticky=(tk.N, tk.E, tk.S, tk.W)
        )

    def set_progress_count(self, count):
        self.progressbar_count = count
        self.progress['value'] = self.progressbar_count

    def increment_progress(self):
        if self.progressbar_count < 10:
            self.progressbar_count += 1
        else:
            self.progressbar_count = 0

        self.progress['value'] = self.progressbar_count

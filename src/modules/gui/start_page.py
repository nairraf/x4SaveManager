"""Definition for the StartPage Class

Main Application page
"""
from __future__ import annotations
from typing import TYPE_CHECKING

import tkinter as tk
import os
from tkinter import ttk
from modules.app import Validate
from .messages import MessageWindow
from .playthrough_page import Playthrough
from .backup_page import Backup

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
        self.backup_note_var = tk.StringVar()
        self.backup_flag_checkbox_var = tk.BooleanVar()
        self.modalresult = None
        self.selected_branch = None
        self.user_selected_branch = None
        self.progressbar_count = self.controller.app_settings.get_app_setting(
            'BACKUPFREQUENCY_SECONDS',
            category="BACKUP"
        )
        self.last_backup_processed = None
        self.tree_cursort = {
            'column': 'x4_save_time',
            'direction': 'ASC',
            'heading': 'SaveTime'
        }
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
        self.backup_frame.grid_rowconfigure(2, weight=1)
        self.progress = ttk.Progressbar(
            self.backup_frame,
            orient="horizontal",
            mode="determinate",
            maximum=self.controller.app_settings.get_app_setting(
                'BACKUPFREQUENCY_SECONDS',
                category="BACKUP"
            )
        )
        self.progress.grid(
            column=0,
            row=0,
            sticky=(tk.W, tk.E),
            padx=5,
            pady=5
        )
        self.backup_options_frame = tk.Frame(
            self.backup_frame
        )
        self.backup_options_frame.grid(
            column=0,
            row=1,
            sticky=(tk.W, tk.E),
            padx=5,
            pady=5,
            ipadx=2,
            ipady=2
        )
        self.backup_options_frame.grid_columnconfigure(2, weight=1)
        self.backup_flag = ttk.Checkbutton(
            self.backup_options_frame,
            text="Flag backup",
            variable=self.backup_flag_checkbox_var
        )
        self.backup_flag.grid(
            column=0,
            row=0,
            padx=2
        )
        self.backup_note_label = tk.Label(
            self.backup_options_frame,
            text="Quick Note:"
        )
        self.backup_note_label.grid(
            column=1,
            row=0,
            padx=2
        )
        self.backup_note = tk.Entry(
            self.backup_options_frame,
            textvariable=self.backup_note_var
        )
        self.backup_note.grid(
            column=2,
            row=0,
            padx=2,
            sticky=(tk.E, tk.W)
        )
        self.backup_branch_label = tk.Label(
            self.backup_options_frame,
            text="Branch :"
        )
        self.backup_branch_label.grid(
            column=3,
            row=0,
            padx=2,
            sticky=tk.W
        )
        self.backup_branch_dropdown = ttk.Combobox(
            self.backup_options_frame
        )
        self.backup_branch_dropdown.grid(
            column=4,
            row=0,
            padx=2,
            sticky=tk.E
        )

        self.backup_data_frame = tk.Frame(
           self.backup_frame
        )
        self.backup_data_frame.grid(
            column=0,
            row=2,
            sticky=(tk.W, tk.N, tk.E, tk.S),
            padx=5,
            pady=5
        )
        self.backup_data_frame.grid_columnconfigure(1, weight=1)
        self.backup_data_frame.grid_rowconfigure(1, weight=1)
        self.countdown_label = ttk.Label(
            self.backup_data_frame,
            text="Next backup check in (seconds):"
        )
        self.countdown_label.grid(
            column=0,
            row=0,
            padx=2,
            pady=2,
            sticky=tk.E
        )
        self.countdown = tk.Label(
            self.backup_data_frame,
            anchor='w'
        )
        self.countdown.grid(
            column=1,
            row=0,
            padx=2,
            pady=2,
            sticky=tk.W
        )
        self.loop_label = tk.Label(
            self.backup_data_frame,
            text="Backup Loops:"
        )
        self.loop_label.grid(
            column=2,
            row=0,
            padx=2,
            pady=2,
            sticky=tk.E
        )
        self.loop = tk.Label(
            self.backup_data_frame
        )
        self.loop.grid(
            column=3,
            row=0,
            padx=2,
            pady=2,
            sticky=tk.W
        )
        self.backup_data = tk.Text(
            self.backup_data_frame,
            state='disabled',
            bg='#EEE'
        )
        self.backup_data.grid(
            column=0,
            columnspan=4,
            row=1,
            sticky=(tk.N, tk.E, tk.S, tk.W)
        )
        v_scrollbar = ttk.Scrollbar(
            self.backup_data_frame,
            orient='vertical',
            command=self.backup_data.yview
        )
        self.backup_data['yscrollcommand'] = v_scrollbar.set
        v_scrollbar.grid(
            column=4,
            row=1,
            sticky=(tk.N, tk.S)
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

        tree_frame = tk.Frame(
            details_frame
        )
        tree_frame.grid(
            column=0,
            row=1,
            sticky=(tk.W, tk.N, tk.E, tk.S)
        )
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(
            tree_frame,
            columns=(
                'SaveTime',
                'Branch',
                'Playtime',
                'Character',
                'Money',
                'Moded',
                'Flag',
                'Notes',
                'Hash'
            ),
            displaycolumns=(
                'SaveTime',
                'Branch',
                'Playtime',
                'Character',
                'Money',
                'Moded',
                'Flag',
                'Notes'
            )
        )
        self.tree.grid(
            column=0,
            row=0,
            sticky=(tk.N, tk.E, tk.S, tk.W)
        )

        tree_v_scroll = ttk.Scrollbar(
            tree_frame,
            orient='vertical',
            command=self.tree.yview
        )
        self.tree['yscrollcommand'] = tree_v_scroll.set
        tree_v_scroll.grid(
            column=1,
            row=0,
            sticky=(tk.N, tk.S)
        )

        self.up_arrow = tk.PhotoImage(
            file=os.path.join(self.controller.approot, 'img', 'up_arrow.png')
        )

        self.down_arrow = tk.PhotoImage(
            file=os.path.join(self.controller.approot, 'img', 'down_arrow.png')
        )

        self.tree.column('SaveTime', width=150, anchor='w')
        self.tree.heading(
            'SaveTime',
            text='Save Time',
            command=lambda: self.sort_tree('SaveTime', 'x4_save_time')
        )

        self.tree.column('Branch', width=100, anchor='center')
        self.tree.heading('Branch', text='Branch')
        self.tree.column('Playtime', width=80, anchor='e')

        self.tree.heading(
            'Playtime',
            text='Hours',
            command=lambda: self.sort_tree('Playtime', 'playtime')
        )
        self.tree.column('Character', width=150, anchor='center')
        self.tree.heading('Character', text='Character')
        self.tree.column('Money', width=100, anchor='e')
        self.tree.heading('Money', text='Money')
        self.tree.column('Moded', width=50, anchor='center')
        self.tree.heading('Moded', text='Moded')
        self.tree.column('Flag', width=50, anchor='center')
        self.tree.heading('Flag', text='Flag')
        self.tree.column('Notes', width=200, anchor='w')
        self.tree.heading('Notes', text='Notes')

        # treeview bindings
        self.tree.bind("<Double-1>", self.treeview_double_click)
        self.tree.bind("<Button-3>", self.treeview_right_click)
        
        # add our root level frames to each side
        self.pane.add(lframe, minsize=250)
        self.pane.add(details_frame, minsize=200)

    def treeview_right_click(self, event):
        """Right click context menu for the treeview

        Allows actions for multiple backups, such as editing and moving
        the backups to another playthrough
        """
        indexes = self.tree.selection()
        menu = tk.Menu(self, tearoff=0)
        
        menu.add_command(label="Edit", command=lambda: self.edit_save(indexes))
        menu.add_separator()
        menu.add_command(label="Set Flag", command=lambda: self.set_backup_flag(indexes))
        menu.add_command(label="Unset Flag", command=lambda: self.unset_backup_flag(indexes))
        menu.add_separator()
        menu.add_command(label="Mark for Deletion", command=lambda: self.set_backup_deleted(indexes))
        menu.add_command(label="Unmark for Deletion", command=lambda: self.unset_backup_deleted(indexes))
        if not self.controller.delete_selected:
            menu.add_separator()
            display_branch_submenu = tk.Menu(menu)
            branch_submenu = tk.Menu(menu)
            menu.add_cascade(menu=display_branch_submenu, label="Display Branch:")
            display_branch_submenu.add_command(
                label='All',
                command=lambda: self.display_branch('All')
            )

            menu.add_cascade(menu=branch_submenu, label="Set Branch:")
            for name in self.controller.db.get_branches(
                self.controller.selected_playthrough['id']
            ):
                branch_submenu.add_command(
                    label=name,
                    command=lambda name=name: self.set_branch(indexes, name)
                )

                display_branch_submenu.add_command(
                    label=name,
                    command=lambda name=name: self.display_branch(name)
                )
            menu.add_separator()

        # create our submenu of all playthrough indexes
        # this will allow us to bulk move saves to a selected playthrough
        submenu = tk.Menu(menu)
        menu.add_cascade(menu=submenu, label='Move to Playthough:')
        for p in self.controller.db.get_playthroughs():
            if p['name'] == '__RECYCLE BIN__':
                continue

            submenu.add_command(
                label=f"{p['name']}",
                command=lambda p=p: self.move_save(indexes, p['id'])
            )
        menu.add_separator()
        restore_menu = tk.Menu(menu)
        menu.add_cascade(menu=restore_menu, label="Restore Selected Backup To X4 Slot:")
        restore_menu.add_command(
            label="Quicksave",
            command=lambda: self.restore_save(indexes, slot='quicksave')
        )
        for slot in range(1, 11):
            if slot < 10:
                slotname=f"save_00{slot}"
            else:
                slotname=f"save_0{slot}"
            restore_menu.add_command(
                label=f"Save {slot}",
                command=lambda slotname=slotname: self.restore_save(indexes, slot=slotname)
            )
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def treeview_double_click(self, event):
        """Callback to edit the backup that the user double clicked
        in the treeview
        """
        index = self.tree.selection()
        if index:
            self.edit_save(index)
        
    def edit_save(self, indexes):
        """Open the edit backup window
        """
        # we ignore multi-selections and just edit the first selection          
        item = self.tree.item(indexes[0])
        Backup(self, self.controller, item['values'][8])
        
    def set_backup_deleted(self, indexes):
        """Removes the delete mark from the currently selected backups
        """

        for idx in indexes:
            item = self.tree.item(idx)
            hash= item['values'][8]
            filename=item['text']
            backup = self.controller.db.get_backup_by_hash(hash)
            if not backup['flag']:
                self.controller.db.backup_set_delete(hash)
            else:
                self.controller.show_error("Can't set backup {} for deletion as it has been flagged".format(
                    filename
                ))
        
        self.populate_tree()

    def restore_save(self, indexes, slot):
        """Restores the selected backup to a specific X4 slot
        """
        # make sure that there is a backup selected in the treeview
        if len(indexes) == 0:
            return
        
        # make sure there is only a single backup selected in the treeview
        if len(indexes) > 1:
            self.controller.show_error("You can only select a single backup when restoring")
            return
        
        # figure out which backup is selected, and pass it to save_manager to restore
        item = self.tree.item(indexes[0])
        filename=item['text']
        self.controller.save_manager.restore_backup(filename, slot)
        
    def set_branch(self, indexes, branch):
        """Sets the branch name on currently selected backups
        """
        for idx in indexes:
            item = self.tree.item(idx)
            hash= item['values'][8]
            self.controller.db.set_branch(
                branch=branch,
                hash=hash
            )
        
        self.populate_tree()

    def display_branch(self, branch):
        if branch == 'All':
            self.user_selected_branch = None
            self.controller.statusbar.set_branch_filter('All')
        else:
            self.user_selected_branch = branch
            self.controller.statusbar.set_branch_filter(branch)
        self.populate_tree()

    def unset_backup_deleted(self, indexes):
        """Removes the delete mark from the currently selected backups
        """

        for idx in indexes:
            item = self.tree.item(idx)
            hash= item['values'][8]
            filename=item['text']
            self.controller.db.backup_unset_delete(hash)
        
        self.populate_tree()

    def set_backup_flag(self, indexes):
        """sets the flag for the currently selected backups
        """

        for idx in indexes:
            item = self.tree.item(idx)
            hash = item['values'][8]
            filename=item['text']
            self.controller.db.update_backup_flag(True, hash)
            
        self.populate_tree()

    def unset_backup_flag(self, indexes):
        """unsets the flag for the currently selected backups
        """

        for idx in indexes:
            item = self.tree.item(idx)
            hash = item['values'][8]
            filename=item['text']
            self.controller.db.update_backup_flag(False, hash)
            
        self.populate_tree()

    def move_save(self, indexes, playthrough_id):
        """Moves the saves from one playthrough to another
        """
        entries = []
        for idx in indexes:
            item = self.tree.item(idx)
            entries.append({
                'hash': item['values'][8],
                'filename': item['text']
            })
        self.controller.playthrough_manager.move_backups_to_index(entries, playthrough_id)
        self.populate_tree()

    def populate_tree(self, sort_column=None, sort_direction=None):
        """Populates the treeview with a list of backups for the currently
        selected playthrough
        """
        self.clear_heading_images()

        if not sort_column and not sort_direction:
            sort_column = self.tree_cursort['column']
            sort_direction = self.tree_cursort['direction']
        
        if self.controller.delete_selected:
            backups = self.controller.db.get_backups_to_delete(
                sort_column=sort_column,
                sort_direction=sort_direction
            )

        if self.controller.selected_playthrough and not self.controller.delete_selected:
            backups = self.controller.db.get_backups_by_id(
                self.controller.selected_playthrough['id'],
                sort_column=sort_column,
                sort_direction=sort_direction,
                branch=self.user_selected_branch
            )
        
        # delete all previous items in the tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # populate the tree with saves that match the selected playthrough
        for save in backups:
            self.tree.insert('', 'end', text=save['backup_filename'], values=(
                save['x4_save_time'],
                save['branch'],
                "{:0.2f}".format(save['playtime']/60/60),
                save['character_name'],
                "${:,.0f}".format(save['money']),
                save['moded'],
                save['flag'],
                save['notes'].partition('\n')[0],
                save['file_hash']
            ))
        
        if self.tree_cursort['direction'] == 'ASC':
            self.tree.heading(
                self.tree_cursort['heading'],
                image=self.up_arrow
            )
        else:
            self.tree.heading(
                self.tree_cursort['heading'],
                image=self.down_arrow
            )
    
    def sort_tree(self, heading, column):
        # check if we are changing columns
        # if so, set the initial sort direction to DESC
        # this way the below logic will flip it to ASC
        # so that when you change columns, it will always
        # be ASC sorted by default
        if not column == self.tree_cursort['column']:
            self.tree_cursort['direction'] = 'DESC'

        self.tree_cursort['column'] = column
        self.tree_cursort['heading'] = heading

        if self.tree_cursort['direction'] == 'ASC':
            self.tree_cursort['direction'] = 'DESC'
        else:
            self.tree_cursort['direction'] = 'ASC'
                
        self.populate_tree()

    def create_playthrough(self):
        """Opens the create playthrough window
        """
        txt = Validate.text_input(self.playthrough_var.get())
        if txt:
            Playthrough(self, self.controller, txt)
            self.entry.delete(0,'end')
    
    def refresh_playthroughs(self):
        """re-populates the list of playthroughs
        """
        self.playthrousghs_var.set(
            self.controller.db.get_playthrough_names()
        )
    
    def select_playthrough(self, event):
        """Callback when the user selects a new playthrough

        Responsible for calling other application methods to re-organize
        the windows when the user selects a new playthrough

        Args:
            event: the tk event to track the current index for the user
                    selected playthrough
        """
        if event:
            cur_selection = event.widget.curselection()
            if cur_selection:
                index = cur_selection[0]
                name = event.widget.get(index)
                if name == "__RECYCLE BIN__":
                    self.controller.delete_selected = True
                    notes = self.controller.db.get_playthrough_by_name("__RECYCLE BIN__")['notes']
                else:
                    self.controller.delete_selected = False
                    self.controller.selected_playthrough = self.controller.db.get_playthrough_by_name(name)
                    if hasattr(self.controller, 'statusbar'):
                        self.controller.statusbar.set_playthrough(name)
                    notes = self.controller.selected_playthrough['notes']
                    self.controller.top_menu.menu_backup.entryconfigure('Start Backup', state='normal')
                
                self.clear_heading_images()
                self.set_notes(notes)
                self.user_selected_branch=None
                self.controller.statusbar.set_branch_filter('All')
                self.populate_tree()

    def clear_heading_images(self):
        self.tree.heading(
            'SaveTime',
            image=''
        )
        self.tree.heading(
            'Playtime',
            image=''
        )
    
    def edit_playthrough(self, event):
        """opens the edit playthrough window on double-click
        """
        if event:
            cur_selection = event.widget.curselection()
            if cur_selection:
                index = cur_selection[0]
                name = event.widget.get(index)
                if name == "__RECYCLE BIN__":
                    self.controller.show_error("Cannot edit the recycle bin")
                    return
                id = self.controller.db.get_playthrough_by_name(name)['id']
                Playthrough(self, self.controller, name=name, id=id)

    def edit_selected_playthrough(self):
        """Opens the edit playthrough window for the currently selected playthrough
        """
        if self.controller.selected_playthrough:
            Playthrough(
                self,
                self.controller,
                name=self.controller.selected_playthrough['name']
            )

    def set_notes(self, note):
        """callback to control the backup quick notes entry widget
        """
        self.notes.configure(state='normal')
        self.notes.delete('1.0', tk.END)
        self.notes.insert('1.0', note)
        self.notes.configure(state='disabled')

    def show_backup_frame(self):
        """hides the main frame, and displays the backup frame
        when the backup thread is running
        """
        self.update_branches_dropdown()
        self.pane.grid_forget()
        self.backup_frame.grid(
            column=0,
            row=0,
            sticky=(tk.N, tk.E, tk.S, tk.W)
        )

    def update_branches_dropdown(self):
        """Updates the branches dropdown in the backup page
        """
        branches = self.controller.db.get_branches(
            self.controller.selected_playthrough['id']
        )
        self.backup_branch_dropdown.configure(
            values=branches
        )
        if self.selected_branch:
            self.backup_branch_dropdown.set(
                self.selected_branch
            )
        else:
            self.backup_branch_dropdown.set(
                branches[0]
            )

    def hide_backup_frame(self):
        """hides the backup from and shows the main frame
        when the backup thread is stopped
        """
        self.backup_frame.grid_forget()
        self.pane.grid(
            column=0,
            row=0,
            sticky=(tk.N, tk.E, tk.S, tk.W)
        )
        self.backup_data.configure(state='normal')
        self.backup_data.delete('1.0', tk.END)
        self.backup_data.configure(state='disabled')

    def set_progress_count(self, count):
        """sets the progress bar max value

        this is needed when the user changes the number of seconds between
        backup loops.
        """
        self.progressbar_count = count
        self.progress['value'] = self.progressbar_count

    def increment_progress(self):
        """decrements the progress bar for a visual indicator of when
        the next backup loop will happen
        """
        count = self.controller.app_settings.get_app_setting(
            'BACKUPFREQUENCY_SECONDS',
            category="BACKUP"
        )
        if self.progressbar_count > 0:
            self.progressbar_count -= 1
        else:
            self.progressbar_count = count

        self.progress['value'] = self.progressbar_count

    def update_backup_data(self):
        """responsible for showing the user what is happening
        or what happened during the backup thread.
        
        controls what is shows in the data_box
        """
        update_data_box = False
        message = ''
        data = self.controller.message_queue.get()
        self.countdown['text'] = data['countdown']
        self.loop['text'] = data['loops']
        
        # if we just backed up a save, update the flag and notes DB columns
        if self.last_backup_processed:
            self.controller.db.update_backup_options(
                self.backup_flag_checkbox_var.get(),
                self.backup_note_var.get(),
                self.backup_branch_dropdown.get(),
                self.last_backup_processed['hash']
            )
            self.selected_branch = self.backup_branch_dropdown.get()
            self.update_branches_dropdown()
            self.last_backup_processed = None
            self.backup_flag_checkbox_var.set(False)
            self.backup_note.delete(0,'end')

            # if we are not processing a backup, display the history of backups
            # for this session
            if len(data['x4saves']) > 0 and data['processing'] == 0:
                message += "\nx4saves backed up:\n"
                for save in data['x4saves']:
                    message += "    {}  ->   {} in  {:0.4f} seconds\n".format(
                        save['x4save'],
                        save['backup_filename'],
                        save['backup_timespan']
                    )

            update_data_box = True

        # record the backup in progress details and display progress
        if data['processing'] == 1:
            message += "Backup now in progress\n\n"
            self.last_backup_processed = data['x4saves'][-1]
            message += "Now backing up file: {}   ->  {}\n".format(
                data['x4saves'][-1]['x4save'],
                data['x4saves'][-1]['backup_filename']
            )
            message += "this may take a few minutes\n"
            message += "    now backing up and extracting info from backup file\n\n"
            
            update_data_box = True
            
        if update_data_box:
            self.backup_data.configure(state='normal')
            self.backup_data.delete('1.0', tk.END)
            self.backup_data.insert('1.0', message)
            self.backup_data.configure(state='disabled')
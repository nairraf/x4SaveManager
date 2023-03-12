"""Class responsible for creating the edit backup functionality
"""

import tkinter as tk
from tkinter import ttk
from .new_page_root import NewPageRoot

class Backup(NewPageRoot):
    """The Backup Class which is responsible for the 
    edit backup functionality
    """
    def __init__(self, caller, controller, file_hash):
        """constructure to initialize the Edit backup window
        
        Args:
            caller (tk.Tk): the caller
            controller (WindowController): our application controller
            file_hash (str): the file hash to identify the backup to edit
        """
        super().__init__(caller, controller)
        self.set_title("Edit Backup")
        self.playthrough_names = self.controller.db.get_playthrough_names()
        self.playthroughs = self.controller.db.get_playthroughs()
        self.selected_backup = self.controller.db.get_backup_by_hash(file_hash)
        self.cur_playthrough = self.controller.db.get_playthrough_by_id(
            self.selected_backup['playthrough_id']
        )
        self.flag_var = tk.BooleanVar()
        self.delete_var = tk.BooleanVar()
        self.status_label_var = tk.StringVar()
        self.bfn_var = tk.StringVar()
        self.flag_var.set(self.selected_backup['flag'])
        self.delete_var.set(self.selected_backup['delete'])
        self.minsize(600,600)
        
        self.frame = ttk.Frame(self)
        self.frame.columnconfigure((2,4), weight=1)
        self.frame.rowconfigure(8, weight=1)

        self.frame.grid(
           column=0,
           row=0,
           sticky=(tk.W, tk.N, tk.E, tk.S),
           padx=5,
           pady=5
        )

        # Playthrough
        tk.Label(
            self.frame,
            text="Playthrough ID:"
        ).grid(
            column=0,
            row=0,
        )
        self.pid_dropdown = ttk.Combobox(
            self.frame,
            values=self.playthrough_names,
            state='readonly'
        )
        self.pid_dropdown.grid(
            column=1,
            row=0,
        )
        self.pid_dropdown.set(self.cur_playthrough['name'])

        # spacer
        tk.Label(
            self.frame,
            text='',
            width=10
        ).grid(
            column=2,
            row=0
        )
        # Original X4 filename
        tk.Label(
            self.frame,
            text="Original X4 save name:"
        ).grid(
            column=3,
            row=0,
            sticky=tk.E
        )
        og = tk.Entry(
            self.frame
        )
        og.grid(
            column=4,
            row=0,
            sticky=(tk.W, tk.E)
        )
        og.insert(0, self.selected_backup['x4_filename'])
        og.config(state="disabled")

        # Original X4 save time
        tk.Label(
            self.frame,
            text="Original X4 save time:"
        ).grid(
            column=3,
            row=1,
            sticky=tk.E
        )
        ogt = tk.Entry(
            self.frame
        )
        ogt.grid(
            column=4,
            row=1,
            sticky=(tk.W, tk.E)
        )
        ogt.insert(0, self.selected_backup['x4_save_time'])
        ogt.config(state="disabled")

        # backup time
        tk.Label(
            self.frame,
            text="Backup Time:"
        ).grid(
            column=3,
            row=2,
            sticky=tk.E
        )
        bt = tk.Entry(
            self.frame
        )
        bt.grid(
            column=4,
            row=2,
            sticky=(tk.W, tk.E)
        )
        bt.insert(0, self.selected_backup['backup_time'])
        bt.config(state="disabled")

        # backup filename
        tk.Label(
            self.frame,
            text="Backup Filename:"
        ).grid(
            column=3,
            row=3,
            sticky=tk.E
        )
        self.bfn = tk.Entry(
            self.frame,
            width=30,
            textvariable=self.bfn_var
        )
        self.bfn.grid(
            column=4,
            row=3,
            sticky=(tk.W, tk.E)
        )
        self.bfn_var.set(self.selected_backup['backup_filename'])
        self.bfn.config(state="disabled")

        # backup duration
        tk.Label(
            self.frame,
            text="Backup Duration (sec):"
        ).grid(
            column=3,
            row=4,
            sticky=tk.E
        )
        bd = tk.Entry(
            self.frame
        )
        bd.grid(
            column=4,
            row=4,
            sticky=(tk.W, tk.E)
        )
        bd.insert(0, f"{self.selected_backup['backup_duration']:0.4f}")
        bd.config(state='disabled')

        # moded
        tk.Label(
            self.frame,
            text="Moded:"
        ).grid(
            column=3,
            row=5,
            sticky=tk.E
        )
        mod = tk.Entry(
            self.frame
        )
        mod.grid(
            column=4,
            row=5,
            sticky=(tk.W, tk.E)
        )
        mod.insert(0, f"{(self.selected_backup['moded'])}")
        mod.config(state='disabled')

        # flag
        tk.Label(
            self.frame,
            text="Flag:"
        ).grid(
            column=3,
            row=6,
            sticky=tk.E
        )
        self.flag = ttk.Checkbutton(
            self.frame,
            variable=self.flag_var,
            text='',
            command=self.flag_change
        )
        self.flag.grid(
            column=4,
            row=6,
            sticky=(tk.W, tk.E)
        )

        # delete
        tk.Label(
            self.frame,
            text="Delete:"
        ).grid(
            column=3,
            row=7,
            sticky=tk.E
        )
        self.flag = ttk.Checkbutton(
            self.frame,
            variable=self.delete_var,
            text='',
            command=self.flag_change
        )
        self.flag.grid(
            column=4,
            row=7,
            sticky=(tk.W, tk.E)
        )

        # game version
        tk.Label(
            self.frame,
            text="Game Version:"
        ).grid(
            column=0,
            row=1,
            sticky=tk.E
        )
        gv = tk.Entry(
            self.frame
        )
        gv.grid(
            column=1,
            row=1,
            sticky=(tk.W, tk.E)
        )
        gv.insert(0, self.selected_backup['game_version'])
        gv.config(state='disabled')

        # original game version
        tk.Label(
            self.frame,
            text="Original Game Version:"
        ).grid(
            column=0,
            row=2,
            sticky=tk.E
        )
        ogv = tk.Entry(
            self.frame
        )
        ogv.grid(
            column=1,
            row=2,
            sticky=(tk.W, tk.E)
        )
        ogv.insert(0, self.selected_backup['original_game_version'])
        ogv.config(state='disabled')

        # play time
        tk.Label(
            self.frame,
            text="Playtime (hours):"
        ).grid(
            column=0,
            row=3,
            sticky=tk.E
        )
        pth = tk.Entry(
            self.frame
        )
        pth.grid(
            column=1,
            row=3,
            sticky=(tk.W, tk.E)
        )
        pth.insert(0, f"{self.selected_backup['playtime']/60/60:0.2f}")
        pth.config(state='disabled')

        # start type
        tk.Label(
            self.frame,
            text="X4 Start Type:"
        ).grid(
            column=0,
            row=4,
            sticky=tk.E
        )
        st = tk.Entry(
            self.frame
        )
        st.grid(
            column=1,
            row=4,
            sticky=(tk.W, tk.E)
        )
        st.insert(0, self.selected_backup['x4_start_type'])
        st.config(state='disabled')

        # character name
        tk.Label(
            self.frame,
            text="Character Name:"
        ).grid(
            column=0,
            row=5,
            sticky=tk.E
        )
        cn = tk.Entry(
            self.frame
        )
        cn.grid(
            column=1,
            row=5,
            sticky=(tk.W, tk.E)
        )
        cn.insert(0, self.selected_backup['character_name'])
        cn.config(state='disabled')

        # money
        tk.Label(
            self.frame,
            text="Money:"
        ).grid(
            column=0,
            row=6,
            sticky=tk.E
        )
        m = tk.Entry(
            self.frame
        )
        m.grid(
            column=1,
            row=6,
            sticky=(tk.W, tk.E)
        )
        m.insert(0, f"${self.selected_backup['money']:,.0f}")
        m.config(state='disabled')

        # notes
        self.notes_frame = tk.LabelFrame(
            self.frame,
            text="Notes"
        )
        self.notes_frame.grid(
            column=0,
            columnspan=5,
            row=8,
            sticky=(tk.W, tk.N, tk.E, tk.S),
            ipadx=5,
            ipady=5,
            pady=(5,0)
        )
        self.notes_frame.grid_columnconfigure(0, weight=1)
        self.notes_frame.grid_rowconfigure(0, weight=1)

        self.text_editor = tk.Text(
            self.notes_frame,
            width=40,
            height=15,
            wrap='none'
        )
        self.text_editor.grid(
           column=0,
           row=0,
           sticky=(tk.W, tk.N, tk.E, tk.S),
           padx=5,
           pady=(0,5)
        )
        v_scrollbar = ttk.Scrollbar(
            self.notes_frame,
            orient='vertical',
            command=self.text_editor.yview
        )
        self.text_editor['yscrollcommand'] = v_scrollbar.set
        v_scrollbar.grid(
            column=1,
            row=0,
            sticky=(tk.N, tk.S)
        )
        h_scrollbar = ttk.Scrollbar(
            self.notes_frame,
            orient='horizontal',
            command=self.text_editor.xview
        )
        self.text_editor['xscrollcommand'] = h_scrollbar.set
        h_scrollbar.grid(
            column=0,
            row=1,
            sticky=(tk.W, tk.E)
        )
        self.text_editor.insert('1.0',self.selected_backup['notes'])

        bottom_frame = tk.Frame(
            self.frame
        )
        bottom_frame.grid(
            column=0,
            columnspan=5,
            row=9,
            sticky=(tk.W, tk.E)
        )
        bottom_frame.grid_columnconfigure(2, weight=1)

        self.status_label = ttk.Label(
            bottom_frame,
            textvariable=self.status_label_var,
            anchor=tk.E
        )
        self.status_label.grid(
            column=2,
            row=0,
            sticky=(tk.E,tk.W),
            padx=2,
            pady=2
        )
        # buttons
        self.save_button = ttk.Button(
            bottom_frame,
            text="Save",
            command=self.save,
            state="disabled"
        )
        self.save_button.grid(
            column=3,
            row=0,
            sticky=(tk.S, tk.E),
            padx=2,
            pady=2
        )
        self.close_button = ttk.Button(
            bottom_frame,
            text="Close",
            command=self.close
        )
        self.close_button.grid(
            column=4,
            row=0,
            sticky=(tk.S, tk.E),
            padx=2,
            pady=2
        )

        # bindings
        self.text_editor.bind("<KeyPress>", self.check_changes)
        self.pid_dropdown.bind('<<ComboboxSelected>>', self.check_changes)

        self.show_window()

    def check_changes(self, *args):
        """Callback to identify window changes to enable the save button
        """
        self.save_button.state(['!disabled'])
        self.status_label_var.set('')

    def flag_change(self):
        """Callback for the flag and delete checkboxes on change
        """
        self.check_changes()

    def save(self):
        """Callback for the Save button
        
        Enables saving changes, persisting them to DB
        """
        selected_playthrough = self.controller.db.get_playthrough_by_name(self.pid_dropdown.get())
        pid = selected_playthrough['id']
        if (selected_playthrough['name'] == "__RECYCLE BIN__" and
            self.delete_var.get() == False
        ):
            self.show_error("""Cannot assign backup to playthrough '__RECYCLE BIN__'.
All backups assigned to __RECYCLE BIN__ must have the Delete checkbox selected.
Please choose a playthrough that isn't '__RECYCLE BIN__'""")
            return
        
        if self.selected_backup['playthrough_id'] != pid:
            # playthrough has changed, so update the playthrough properly first
            self.controller.playthrough_manager.move_backups_to_index(
                backups=[{
                    'hash': self.selected_backup['file_hash'],
                    'filename': self.selected_backup['backup_filename']
                },],
                playthrough_id=pid
            )
            # refresh the filename because of the move that just happened
            self.selected_backup = self.controller.db.get_backup_by_hash(
                self.selected_backup['file_hash']
            )
            self.bfn_var.set(self.selected_backup['backup_filename'])
        
        if self.controller.db.save_backup(
            playthrough_id=pid,
            flag=self.flag_var.get(),
            file_hash=self.selected_backup['file_hash'],
            notes=self.text_editor.get('1.0', 'end'),
            delete=self.delete_var.get()
        ):
            self.controller.startpage.populate_tree()
            self.status_label_var.set('Saved Successfully')
            self.save_button.state(['disabled'])
        
    def close(self):
        """Closes the window"""
        self.destroy()
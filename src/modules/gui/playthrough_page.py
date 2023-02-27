import tkinter as tk
from tkinter import ttk
from .new_page_root import NewPageRoot
from os import path

class Playthrough(NewPageRoot):
    def __init__(self, caller, controller, name='', notes='', id=None):
        super().__init__(caller, controller)
        
        self.playthrough_name_var = tk.StringVar()
        self.status_label_var = tk.StringVar()
        self.id = id
        initial_state='disabled'
        self.dbrecord = None
        if name:
            initial_state='!disabled'
            self.dbrecord = self.controller.db.get_playthrough_by_name(name)
            
        self.set_title("Playthrough")
        if name:
            self.playthrough_name_var.set(name)
        
        self.minsize(300,300)
        
        self.frame = ttk.Frame(self)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(1, weight=1)

        self.frame.grid(
           column=0,
           row=0,
           sticky=(tk.W, tk.N, tk.E, tk.S)
        )

        # Playthrough Name
        ttk.Label(self.frame, text='Playthrough Name:').grid(
            column=0,
            row=0,
            sticky=(tk.W, tk.N),
            padx=5,
            pady=5
        )

        self.playthrough_name = ttk.Entry(
            self.frame,
            textvariable=self.playthrough_name_var,

        )
        self.playthrough_name.grid(
            column=1,
            columnspan=2,
            row=0,
            sticky=(tk.E, tk.W, tk.N),
            padx=(0,5),
            pady=5
        )

        # Playthrough Notes
        self.notes_section = ttk.Labelframe(self.frame, text='Notes')
        self.notes_section.grid_columnconfigure(0, weight=1)
        self.notes_section.grid_rowconfigure(0, weight=1)
        self.notes_section.grid(
            column=0,
            columnspan=3,
            row=1,
            sticky=(tk.E,tk.W, tk.N, tk.S),
            padx=5,
            pady=5
        )

        self.text_editor = tk.Text(
            self.notes_section,
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
            self.notes_section,
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
            self.notes_section,
            orient='horizontal',
            command=self.text_editor.xview
        )
        self.text_editor['xscrollcommand'] = h_scrollbar.set
        h_scrollbar.grid(
            column=0,
            columnspan=2,
            row=1,
            sticky=(tk.W, tk.E)
        )
        if self.dbrecord:
            self.text_editor.insert('1.0',self.dbrecord['notes'])
        
        # bottom labels
        bottom_frame = ttk.Frame(self.frame)
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.grid(
            column=0,
            columnspan=2,
            row=2,
            sticky=(tk.W, tk.S, tk.E)
        )
        self.id_label = ttk.Label(
            bottom_frame,
            text=f"ID: {self.id}",
            anchor=tk.W
        )
        self.id_label.grid(
            column=0,
            row=0,
            sticky=tk.W,
            padx=2,
            pady=2
        )
        self.status_label = ttk.Label(
            bottom_frame,
            textvariable=self.status_label_var,
            anchor=tk.E
        )
        self.status_label.grid(
            column=1,
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
            state=initial_state
        )
        self.save_button.grid(
            column=2,
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
            column=3,
            row=0,
            sticky=(tk.S, tk.E),
            padx=2,
            pady=2
        )
        #self.text_editor.trace_add('write', self.check_changes)
        self.playthrough_name_var.trace_add('write', self.check_changes)
        self.text_editor.bind("<KeyPress>", self.check_changes)
        self.show_window()

    def close(self):
        self.destroy()

    def save(self):
        # see if we can find a playthrough with the specified name
        # ask the user if we want to overwrite it with the new data
        playthrough = self.controller.db.get_playthrough_by_name(
            self.playthrough_name_var.get()
        )
        overwrite = False
        if (
            self.id or (
              playthrough and 
              self.playthrough_name_var.get() == playthrough["name"]
            )
        ):
            self.show_question("Are you Sure?")
            if self.modalresult == 1:
                self.modalresult = 0
                overwrite = True
        

        if self.controller.db.save_playthrough(
            name = self.playthrough_name_var.get(),
            notes = self.text_editor.get('1.0', 'end'),
            id = self.id,
            overwrite = overwrite
        ):
            self.status_label_var.set('Saved Successfully')
            self.save_button.state(['disabled'])
            self.controller.startpage.refresh_playthroughs()
        else:
            self.status_label_var.set('Save Cancelled or Failed')

        if not self.id:
            self.id = self.controller.db.get_playthrough_by_name(
                self.playthrough_name_var.get()
            )['id']
            self.id_label['text']=f"ID: {self.id}"
    
    def check_changes(self, *args):
        if (
            self.playthrough_name_var.get() and
            self.text_editor.get('1.0', 'end')
        ):
            self.save_button.state(['!disabled'])
            self.status_label_var.set('')

        
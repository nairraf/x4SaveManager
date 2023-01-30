"""Definition for the StartPage Class
"""
import tkinter as tk
import modules.app as app
from .messages import MessageWindow
from tkinter import ttk

class StartPage(ttk.Frame):
    """Builds the main application page

    Args:
        tk (Frame): inherits from tk.Frame
    """

    def __init__(self, parent, controller, **kwargs):
        """initializes the StatusPage

        Args:
            parent (tk.Frame): the parent tk container object
            controller (WindowController): the WindowController instance
        """
        super().__init__(parent, **kwargs)
        self._parent = parent
        self._controller = controller
        self._playthroughs = []
        self.playthrousghs_var = tk.StringVar()
        self.modalresult = ''
        self.build_page()

    def build_page(self):
        """builds the main start page
        """
        # 3 columns, sticky on all sides to be responsive
        # with a little inner padding
        self.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.S, tk.N))
        self.columnconfigure(3, weight=1)
        self.rowconfigure(1, weight=1)
        # padding = W, N, E, S
        # 25 padding at the bottom to float above the status bar
        self['padding'] = (10,5,10,25)

        # create playthrough section
        self.playthrough = tk.StringVar()
        entry_frame = ttk.LabelFrame(self, text="Create Playthrough")
        entry_frame.grid(
            column=1,
            row=0,
            columnspan=2,
            ipadx=5,
            ipady=5,
            sticky=(tk.N, tk.W)
        )
        entry_label = ttk.Label(entry_frame, text="Name:")
        entry_label.grid(column=1, row=0)
        self.entry = ttk.Entry(
            entry_frame,
            textvariable=self.playthrough,
            width=20
        )
        self.entry.grid(column=2, row=0)
        space = tk.Label(entry_frame, text='')
        space.grid(column=3, row=0)
        entry_button = ttk.Button(
            entry_frame,
            text="Create",
            command=self.create_playthrough
        )
        entry_button.grid(
            column=4,
            row=0
        )

        # Playthrough Listbox
        playthrough_frame = ttk.LabelFrame(
           self,
           text='Playthroughs',
           padding=5
        )
        playthrough_frame.grid(
           column=1,
           columnspan=2,
           row=1,
           sticky=(tk.W, tk.N, tk.S, tk.E)
        )
        playthrough_frame.grid_rowconfigure(0, weight=1)
        playthrough_frame.grid_columnconfigure(0, weight=1)
        playthroughs = tk.Listbox(
            playthrough_frame,
            listvariable=self.playthrousghs_var
        )
        playthroughs.grid(
            column=0,
            row=0,
            sticky=(tk.N, tk.E, tk.S, tk.W)
        )
        scrollbar = ttk.Scrollbar(
            playthrough_frame,
            orient='vertical',
            command=playthroughs.yview
        )
        playthroughs['yscrollcommand'] = scrollbar.set
        scrollbar.grid(
            column=1,
            row=0,
            sticky=(tk.N, tk.S)
        )

    def create_playthrough(self):
        """saves the new playthrough name
        """
        txt = app.Validate.text_input(self.playthrough.get())
        if txt:
            MessageWindow(
                self,
                self._controller.window_title,
                "Add Playthrough:\n{}".format(
                    txt
                ),
                type="question",
                oktext="Yes",
                canceltext="No"
            )
            if self.modalresult:
                self._playthroughs.append(txt)
                self._playthroughs.sort()
                self.playthrousghs_var.set(self._playthroughs)
                self._controller.statusbar.set_playthrough(txt)
            
            self.entry.delete(0,'end')

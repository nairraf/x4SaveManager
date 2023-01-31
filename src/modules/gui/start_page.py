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
        self.playthrough_var = tk.StringVar()
        self.playthrousghs_var = tk.StringVar()
        self.modalresult = None
        self.build_page()

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
        # add a main pane with two sides for resizable East and West sections
        pane = tk.PanedWindow(
            self,
            orient='horizontal',
            sashpad=2,
            handlepad=0,
            handlesize=7,
            showhandle=True,
            sashrelief='ridge'
        )
        pane.grid(
            column=0,
            row=0,
            sticky=(tk.N, tk.E, tk.S, tk.W)
        )

        # create playthrough section
        lframe=ttk.Frame(
            pane
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

        # details section
        details_frame = ttk.LabelFrame(
            pane,
            text='Details',
            padding=5
        )
        details_frame.grid_rowconfigure(0, weight=1)
        details_frame.grid_columnconfigure(0, weight=1)
        details_frame.grid(
            column=2,
            row=0,
            rowspan=2,
            sticky=(tk.N, tk.E, tk.S, tk.W)
        )
        tree = ttk.Treeview(
            details_frame
        )
        tree.grid(
            column=0,
            row=0,
            sticky=(tk.N, tk.E, tk.S, tk.W)
        )
        # add our root level frames to each side
        pane.add(lframe, minsize=250)
        pane.add(details_frame, minsize=200)

    def create_playthrough(self):
        """saves the new playthrough name
        """
        txt = app.Validate.text_input(self.playthrough_var.get())
        if txt:
            MessageWindow(
                self,
                self._controller.window_title,
                "Add Playthrough:\n  {}".format(
                    txt
                ),
                type="question",
                oktext="Yes",
                canceltext="No"
            )
            if self.modalresult:
                # reset modalresult for future operations
                self.modalresult = None
                self._playthroughs.append(txt)
                self._playthroughs.sort()
                self.playthrousghs_var.set(self._playthroughs)
                self._controller.statusbar.set_playthrough(txt)
            
            self.entry.delete(0,'end')

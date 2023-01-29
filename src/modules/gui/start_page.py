"""Definition for the StartPage Class
"""
import tkinter as tk
import modules.app as app
from tkinter import ttk, messagebox

class StartPage(tk.Frame):
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
        self.build_page()

    def build_page(self):
        """builds the main start page
        """
        # 3 columns, sticky on all sides to be responsive
        # with a little inner padding
        self.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.S, tk.N))
        self.columnconfigure([2, 3], weight=1)
        self.config(padx=10, pady=10)

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
        entry = ttk.Entry(
            entry_frame,
            textvariable=self.playthrough,
            width=20
        )
        entry.grid(column=2, row=0)
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

    def create_playthrough(self):
        """saves the new playthrough name
        """
        txt = app.Validate.text_input(self.playthrough.get())
        if txt:
            messagebox.showinfo(
                message=f'Playthough: {txt}\nsuccessfully created!',
                title=self._controller.window_title
            )
            self._controller.statusbar.set_playthrough(txt)

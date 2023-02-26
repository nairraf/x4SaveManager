"""Definition for the StausBar class
"""
from __future__ import annotations
from typing import TYPE_CHECKING

import tkinter as tk
from tkinter import ttk

if TYPE_CHECKING:
    from modules.gui import WindowController

class StatusBar(ttk.Frame):
    """Provides a statusbar with a left, center, and right area
    and provides methods to write status messages into each

    Args:
        tk (Frame): inherits from tk.Frame
    """

    def __init__(self, parent, controller: WindowController, **kwargs):
        """initializes the statusbar

        Args:
            parent (tk.Frame): the parent tk container object
            controller (WindowController): the WindowController instance
        """
        super().__init__(parent, **kwargs)
        self._parent = parent
        self._controller = controller
        self._left_message = "Selected Playthrough:"
        self._center_message = "Backup Status:"

        # dictionary holding all the messages to display on the status bar
        # these variables will be watched for change by the appropriate
        # ttk.Label below
        self.messages = {
            "left" : tk.StringVar(),
            "center": tk.StringVar(),
            "right": tk.StringVar()
        }
        self.set_playthrough("None")
        self.set_backup_status("idle")
        
        self.build_statusbar()

    def build_statusbar(self):
        """Builds the status bar
        """
        self.config(border=2, relief='solid')
        self.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.S))
        self.columnconfigure([0, 2, 4], weight=1)

        # left status bar
        status_left = ttk.Label(
            self,
            textvariable=self.messages['left'],
            padding=(5, 0, 5, 0),
            relief='flat',
            anchor='w',
            width=30
        )
        status_left.grid(column=0, row=0, sticky=(tk.W, tk.E))

        # center status bar
        status_center = ttk.Label(
            self,
            textvariable=self.messages['center'],
            anchor='center',
            padding=(5, 0, 5, 0),
            relief='flat',
            width=30
        )
        status_center.grid(column=2, row=0, sticky=(tk.W, tk.E))
        lseperator = ttk.Separator(
            self,
            orient='vertical'
        )
        lseperator.grid(column=1, row=0, sticky=(tk.N, tk.S))
        rseperator = ttk.Separator(
            self,
            orient='vertical'
        )
        rseperator.grid(column=3, row=0, sticky=(tk.N, tk.S))

        # right status bar
        status_right = ttk.Label(
            self,
            textvariable=self.messages['right'],
            padding=(5, 0, 5, 0),
            relief='flat',
            anchor='e',
            width=30
        )
        status_right.grid(column=4, row=0, sticky=(tk.W, tk.E))

    def set_playthrough(self, message):
        """updates the left status area with 'message'

        'message' should be the name of the playthrough
        """
        self.messages['left'].set(f"{self._left_message} {message}")

    def set_backup_status(self, message):
        """updates the center status area with 'message'
        """
        self.messages['center'].set(f"{self._center_message} {message}")

    def set_message_right(self, message):
        """updates the right status area with 'message'
        """
        self.messages['right'].set(message)

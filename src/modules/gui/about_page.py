"""About Class

The About page which displays details about the application
"""
import tkinter as tk
from tkinter import ttk
from .new_page_root import NewPageRoot

class About(NewPageRoot):
    """Help displays the help window
    """
    def __init__(self, caller, controller):
        """Constructor
        
        Args:
            caller (tk.Tk): the caller object
            controller (WindowController): the application controller
        """
        super().__init__(caller, controller)

        self.set_title("About")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.minsize(300,300)

        self.style = ttk.Style(self)
        self.style.configure(
            'AboutHeading.TLabel',
            font=('helvetica', 24)
        )
        self.configure(
            padx=5,
            pady=5
        )

        self.about_frame = tk.Frame(self)
        self.about_frame.grid(
            column=0,
            row=0,
            sticky=(tk.W, tk.N, tk.E, tk.S),
            pady=(10,0)
        )
        self.about_frame.grid_columnconfigure(0, weight=1)
        self.about_frame.grid_rowconfigure(3, weight=1)

        ttk.Label(
            self.about_frame,
            text="x4SaveManager",
            style='AboutHeading.TLabel',
            anchor='center'
        ).grid(
            column=0,
            row=0,
            sticky=(tk.E, tk.W)
        )

        ttk.Label(
            self.about_frame,
            text="Author: {}".format(
                self.controller.credits['author']
            ),
            anchor='center'
        ).grid(
            column=0,
            row=1,
            sticky=(tk.W, tk.E),
            pady=(10,0)
        )

        ttk.Label(
            self.about_frame,
            text="Version: {}".format(
                self.controller.version['version_label']
            ),
            anchor='center'
        ).grid(
            column=0,
            row=2,
            sticky=(tk.W, tk.E),
            pady=(0,10)
        )

        # credits frame
        self.credits_frame = tk.LabelFrame(
            self.about_frame,
            text="Special Thanks to"
        )
        self.credits_frame.grid(
            column=0,
            row=3,
            ipadx=5,
            ipady=5,
            sticky=(tk.W, tk.N, tk.E, tk.S)
        )
        self.credits_frame.grid_columnconfigure(0, weight=1)
        self.credits_frame.grid_rowconfigure(0, weight=1)
        
        self.credits_canvas = tk.Canvas(self.credits_frame)
        self.credits_canvas.grid(
            column=0,
            row=0,
            sticky=(tk.W, tk.N, tk.E, tk.S)
        )
        self.v_scroll = ttk.Scrollbar(
            self.credits_frame,
            orient='vertical',
            command=self.credits_canvas.yview
        )
        self.v_scroll.grid(
            column=1,
            row=0,
            sticky=(tk.N, tk.S)
        )
        self.canvas_frame = ttk.Frame(self.credits_canvas)
        self.canvas_frame.bind(
            "<Configure>",
            lambda e: self.credits_canvas.configure(
                scrollregion=self.credits_canvas.bbox("all")
            )
        )
        self.credits_canvas.create_window(
            (0,0),
            window=self.canvas_frame,
            anchor='center'
        )
        self.credits_canvas.configure(
            yscrollcommand=self.v_scroll.set
        )

        row=0
        for name in self.controller.credits['contributors']:
            ttk.Label(
                self.canvas_frame,
                text=name
            ).grid(
                column=0,
                row=row
            )
            row+=1

        self.show_window()
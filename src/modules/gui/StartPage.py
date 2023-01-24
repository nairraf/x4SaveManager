import tkinter as tk

LARGE_FONT= ("Verdana", 12)

class StartPage(tk.Frame):
    """
    The initial page that is displayed in the app
    """

    def __init__(self, parent):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button_page1 = tk.Button(self, text = 'Visit Page 1')
        button_page1.pack()

        button_page2 = tk.Button(self, text = 'Visit Page 2')
        button_page2.pack()

        self.pack(side="right", fill="both", expand=True)

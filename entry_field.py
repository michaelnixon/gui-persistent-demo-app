import tkinter as tk
import sys


class EntryField(tk.Frame):
    def __init__(self, parent, label='', passwordField=False, *args, **kwargs):
        # keep in mind EntryField is a Frame widget so any args and kwargs apply only to it, not its children - the label and title
        super().__init__(parent, *args, **kwargs)
        self.dataentry = tk.StringVar()
        self.label = label

        self.title = tk.Label(self, text=label, width=10)
        self.title.grid(row=0, column=0, padx=10, sticky=(tk.W + tk.E))
        # args and kwargs are only sent in the super and this doesn't apply to the super construct but one of the children
        if passwordField:
            self.field = tk.Entry(
                self, width=30, textvariable=self.dataentry, show="*")
        else:
            self.field = tk.Entry(
                self, width=30, textvariable=self.dataentry)
        self.field.grid(row=0, column=1, padx=15, sticky=(tk.W + tk.E))

    def reset(self):
        self.dataentry.set("")

    def get(self):
        return self.dataentry.get()

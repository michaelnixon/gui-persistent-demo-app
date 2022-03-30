import tkinter as tk
from tkinter import font as tkfont
import tkinter.ttk as ttk  # just for treeview
import entry_field  # no particular good reason I did it the other way here
from models import *  # done this way to access classes just by name
import sys  # only used for flushing debug print statements


class App(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # this is the main database access object
        # note you must run the init_db.py script before using SQLStorage
        self.data = SQLStorage()

        # set a single font to be used throughout the app
        self.title_font = tkfont.Font(
            family='Helvetica', size=18, weight="bold", slant="italic")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        # for each other custom Frame class you make, you could add it to this tuple
        for F in (BrowsePage, ReadPage, CreatePage):
            page_name = F.__name__
            # last arg - send the object that accesses the db
            frame = F(parent=container, controller=self, persist=self.data)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("BrowsePage")

    def show_frame(self, page_name, rid=0):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        # the edit screen requires knowledge of the id of the item
        if not rid == 0:
            frame.update(rid)
        else:
            frame.update()
        # bring it to the front of the stacking order
        frame.tkraise()


class BrowsePage(tk.Frame):
    ''' the Browse page must show all the items in the database and allow
    access to editing and deleting, as well as the ability to go to a screen
    to add new ones. This is the 'home' screen.
    '''

    def __init__(self, parent, controller, persist=None):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Browse Contacts",
                         font=controller.title_font)
        label.grid(column=0, pady=10)

        ''' '''
        # set up the treeview
        contact_table = tk.Frame(self, width=500)
        contact_table.grid(column=0)
        scrollbarx = tk.Scrollbar(contact_table, orient=tk.HORIZONTAL)
        scrollbary = tk.Scrollbar(contact_table, orient=tk.VERTICAL)
        self.tree = ttk.Treeview(contact_table, columns=("id", "name", "email"),
                                 selectmode="extended", yscrollcommand=scrollbary.set, xscrollcommand=scrollbarx.set)
        scrollbary.config(command=self.tree.yview)
        scrollbary.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbarx.config(command=self.tree.xview)
        scrollbarx.pack(side=tk.BOTTOM, fill=tk.X)
        # this section would allow for expanding the viewable columns
        self.tree.heading('id', text="ID", anchor=tk.W)
        self.tree.heading('name', text="Name", anchor=tk.W)
        self.tree.heading('email', text="Email", anchor=tk.W)
        self.tree.column('#0', stretch=tk.NO, minwidth=0, width=0)
        self.tree.column('#1', stretch=tk.NO, minwidth=0, width=60)
        self.tree.column('#2', stretch=tk.NO, minwidth=0, width=200)
        self.tree.column('#3', stretch=tk.NO, minwidth=0, width=200)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.pack()
        self.selected = []

        # this object is the data persistence model
        self.persist = persist
        all_records = self.persist.get_all_sorted_records()
        # grab all records from db and add them to the treeview widget
        for record in all_records:
            self.tree.insert("", 0, values=(
                record.rid, record.name, record.email))

        ''' '''

        # I don't love clunkiness of vertical ordering here, should use horizontal space better
        edit_button = tk.Button(self, text="Edit Record",
                                command=self.edit_selected)
        edit_button.grid(column=0)

        delete_button = tk.Button(self, text="Delete Record(s)",
                                  command=self.delete_selected)
        delete_button.grid(column=0)

        new_button = tk.Button(self, text="Add New Record",
                               command=lambda: controller.show_frame("CreatePage"))
        new_button.grid(column=0)

    def edit_selected(self):
        idx = self.selected[0]  # use first selected item if multiple
        record_id = self.tree.item(idx)['values'][0]
        self.controller.show_frame("ReadPage", record_id)

    def on_select(self, event):
        ''' add the currently highlighted items to a list
        '''
        self.selected = event.widget.selection()

    def delete_selected(self):
        ''' uses the selected list to remove and delete certain records
        '''
        for idx in self.selected:
            record_id = self.tree.item(idx)['values'][0]
            # remove from the db
            self.persist.delete_record(record_id)
            # remove from the treeview
            self.tree.delete(idx)

    def update(self):
        ''' to refresh the treeview, delete all its rows and repopulate from the db 
        '''
        for row in self.tree.get_children():
            self.tree.delete(row)
        all_records = self.persist.get_all_sorted_records()
        for record in all_records:
            self.tree.insert("", 0, values=(
                record.rid, record.name, record.email))


class ReadPage(tk.Frame):
    ''' set up as an edit form the same as the create page form
    this is incredibly redundant, refactoring the similar behaviour into a
    separate function would be a key step before adding or changing the form
    '''

    def __init__(self, parent, controller, persist=None):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Edit Entry",
                         font=controller.title_font)
        label.grid(row=0, column=0)
        # this object is the data persistence model
        self.persist = persist
        # this empty dict will hold each of the data entry fields
        self.data = {}
        """ Use EntryField classes to set up the form, along with a submit button """
        self.data['Name'] = entry_field.EntryField(self, label='Name')
        self.data['Name'].grid(row=1, column=0, pady=2)

        self.data['Email'] = entry_field.EntryField(self, label='Email')
        self.data['Email'].grid(row=2, column=0, pady=2)

        self.Button1 = tk.Button(self, text='Update', activebackground="green",
                                 activeforeground="blue", command=self.submit)
        self.Button1.grid(row=3, column=0, pady=10)

        button = tk.Button(self, text="Return to the browse page",
                           command=lambda: controller.show_frame("BrowsePage"))
        button.grid(row=4, column=0)

    def update(self, rid):
        record = self.controller.data.get_record(rid)
        # expand this by adding each of the separate field names
        # or come up with an introspective method (for key in ..)
        self.data['Name'].dataentry.set(record.name)
        self.data['Email'].dataentry.set(record.email)
        self.contact = self.persist.get_record(rid)

    def submit(self):
        ''' grab the text placed in the entry widgets accessed through the dict 
        '''
        self.contact.name = self.data['Name'].get()
        self.contact.email = self.data['Email'].get()
        self.persist.save_record(self.contact)


class CreatePage(tk.Frame):
    ''' provides a form for creating a new Contact
    '''

    def __init__(self, parent, controller, persist=None):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Create New Entry",
                         font=controller.title_font)
        label.grid(row=0, column=0)
        # this object is the data persistence model
        self.persist = persist
        # this empty dict will hold each of the data entry fields
        self.data = {}
        """ Use EntryField classes to set up the form, along with a submit button """
        self.data['Name'] = entry_field.EntryField(self, label='Name')
        self.data['Name'].grid(row=1, column=0, pady=2)

        self.data['Email'] = entry_field.EntryField(self, label='Email')
        self.data['Email'].grid(row=2, column=0, pady=2)

        self.Button1 = tk.Button(self, text='Submit', activebackground="green",
                                 activeforeground="blue", command=self.submit)
        self.Button1.grid(row=3, column=0, pady=10)

        button = tk.Button(self, text="Return to the browse page",
                           command=lambda: controller.show_frame("BrowsePage"))
        button.grid(row=4, column=0)

    def reset(self):
        ''' on every new entry, blank out the fields
        '''
        for key in self.data:
            self.data[key].reset()

    def update(self):
        self.reset()

    def submit(self):
        ''' make a new contact based on the form
        '''
        c = Contact(name=self.data['Name'].get(),
                    email=self.data['Email'].get())
        self.persist.save_record(c)
        self.update()


if __name__ == "__main__":
    app = App()
    app.mainloop()

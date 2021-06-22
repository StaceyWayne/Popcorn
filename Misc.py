import tkinter as tk
import tkinter.ttk as ttk

NAME = 0
ROOM = 1
DOB = 2


class TextScrollCombo(tk.Frame):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

    # ensure a consistent GUI size
        self.grid_propagate(False)
    # implement stretchability
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    # create a Text widget
        self.txt = tk.Text(self, wrap=tk.WORD)
        self.txt.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

    # create a Scrollbar and associate it with txt
        scrollb = ttk.Scrollbar(self, command=self.txt.yview)
        scrollb.grid(row=0, column=1, sticky='nsew')
        self.txt['yscrollcommand'] = scrollb.set

    def gettext(self):
        # I seem to always get an extra '\n' this is how I'm correcting this
        temp=self.txt.get("1.0", tk.END)
        return temp[:len(temp)-1]

    def gettextaslines(self):
        return self.txt.get('1.0',tk.END).splitlines()

    def cleartext(self):
        self.txt.delete(1.0, tk.END)

    def settext(self, thistext):
        self.cleartext()
        self.txt.insert(tk.END, thistext)

    def setstate(self, newstate):
        self.txt.config(state=newstate)

    def appendtext(self, thistext):
        self.txt.insert(tk.END, thistext + "\n")


class MyListBox(tk.Frame):
    def __init__(self, boxfont, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.grid_columnconfigure(5, weight=1)
        thisrow = 1

        self.listbox = tk.Listbox(self, font=boxfont, exportselection=False, height=5)
        self.scrollbar = tk.Scrollbar(self)
        self.scrollbar.config(command=self.yview)

        self.listbox.grid(row=thisrow, column=1, sticky='news')
        self.scrollbar.grid(row=thisrow, column=2, sticky='ns')

        self.listbox.config(yscrollcommand=self.scrollbar.set)

        thisrow = thisrow + 1
        self.grid_rowconfigure(thisrow, weight=1)

    def yview(self, *args):
        self.listbox.yview(*args)

    def addpatient(self, thistext, index):
        self.listbox.insert(index, thistext)

    def clearlistboxes(self):
        self.listbox.delete(0, 'end')

    def populatelistbox(self, textarray):
        self.clearlistboxes()
        for index, element in enumerate(textarray):
            self.addpatient(element, index)

    def whichchosen(self):

        if len(self.listbox.curselection()) == 0:
            return -1
        else:
            return self.listbox.get(self.listbox.curselection()[0])


class MyMultiListBox(tk.Frame):
    def __init__(self, patient_obj, buttonfont, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.patient_obj = patient_obj

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.grid_columnconfigure(5, weight=1)
        thisrow = 1

        button_forwardjump = tk.Button(self, font=buttonfont, text="Scroll forward 10")
        button_forwardjump.config(command=lambda: self.scrolljump(1))
        button_forwardjump.grid(row=thisrow, column=1, sticky='news')

        button_backjump = tk.Button(self, font=buttonfont, text="Scroll backward 10")
        button_backjump.config(command=lambda: self.scrolljump(-1))
        button_backjump.grid(row=thisrow, column=3, sticky='news')

        thisrow = thisrow + 1

        button_sortbyname = tk.Button(self, text="Name", font=buttonfont, width=20)
        button_sortbyname.config(command=lambda: self.sortlist(NAME))
        button_sortbyname.grid(row=thisrow, column=1, sticky='news')

        button_sortbydob = tk.Button(self, text="Date of Birth", font=buttonfont, width=20)
        button_sortbydob.config(command=lambda: self.sortlist(DOB))
        button_sortbydob.grid(row=thisrow, column=2, sticky='news')

        button_sortbyroom = tk.Button(self, text="Room", width=20, font=buttonfont)
        button_sortbyroom.config(command=lambda: self.sortlist(ROOM))
        button_sortbyroom.grid(row=thisrow, column=3, sticky='news')

        thisrow = thisrow + 1
        self.listbox_name = tk.Listbox(self, exportselection=False, yscrollcommand = self.namescroll)
        self.listbox_dob = tk.Listbox(self, exportselection=False,  yscrollcommand = self.dobscroll)
        self.listbox_room = tk.Listbox(self, exportselection=False, yscrollcommand = self.roomscroll)
        self.scrollbar = tk.Scrollbar(self)
        self.scrollbar.config(command=self.yview)

        self.listbox_name.grid(row=thisrow, column=1, sticky='news')
        self.listbox_dob.grid(row=thisrow, column=2, sticky='news')
        self.listbox_room.grid(row=thisrow, column=3, sticky='news')
        self.scrollbar.grid(row=thisrow, column=4, sticky='ns')

        self.listbox_name.bind("<<ListboxSelect>>", self.listboxclicked)
        self.listbox_dob.bind("<<ListboxSelect>>", self.listboxclicked)
        self.listbox_room.bind("<<ListboxSelect>>", self.listboxclicked)

        #self.listbox_name.config(yscrollcommand=self.scrollbar.set)

        thisrow = thisrow + 1
        self.grid_rowconfigure(thisrow, weight=1)

    def namescroll(self, *args):
        if self.listbox_name.yview() != self.listbox_dob.yview():
            self.listbox_dob.yview_moveto(args[0])

        if self.listbox_name.yview() != self.listbox_room.yview():
            self.listbox_room.yview_moveto(args[0])

        self.scrollbar.set(*args)

    def dobscroll(self, *args):
        if self.listbox_dob.yview() != self.listbox_name.yview():
            self.listbox_name.yview_moveto(args[0])

        if self.listbox_dob.yview() != self.listbox_room.yview():
            self.listbox_room.yview_moveto(args[0])

        self.scrollbar.set(*args)

    def roomscroll(self, *args):
        if self.listbox_room.yview() != self.listbox_name.yview():
            self.listbox_name.yview_moveto(args[0])

        if self.listbox_room.yview() != self.listbox_dob.yview():
            self.listbox_dob.yview_moveto(args[0])

        self.scrollbar.set(*args)

    def whichchosen(self):
        if len(self.listbox_name.curselection()) == 0:
            return -1
        else:
            return self.listbox_name.curselection()[0]

    def listboxclicked(self, event=None):
        which = event.widget.curselection()[0]
        self.listbox_name.select_clear(0, tk.END)
        self.listbox_dob.select_clear(0, tk.END)
        self.listbox_room.select_clear(0, tk.END)

        self.listbox_name.select_set(which)
        self.listbox_dob.select_set(which)
        self.listbox_room.select_set(which)

    def yview(self, *args):
        self.listbox_name.yview(*args)
        self.listbox_dob.yview(*args)
        self.listbox_room.yview(*args)

    def scrolljump(self, direction):
        self.listbox_name.yview_scroll(direction, "pages")
        self.listbox_dob.yview_scroll(direction, "pages")
        self.listbox_room.yview_scroll(direction, "pages")

    def sortlist(self, which):
        self.patient_obj.sortpatients(which)
        self.clearlistboxes()

        for index, this_patient in enumerate(self.patient_obj.ThePatients):
            self.addpatient(this_patient, index)

    def addpatient(self, this_patient, index):
        self.listbox_name.insert(index, this_patient.name)
        self.listbox_dob.insert(index, this_patient.dobstr)
        self.listbox_room.insert(index, this_patient.roomnumber)

    def clearlistboxes(self):
        self.listbox_dob.delete(0, 'end')
        self.listbox_room.delete(0, 'end')
        self.listbox_name.delete(0, 'end')

    def populatelistbox(self):
        self.clearlistboxes()
        for index, this_patient in enumerate(self.patient_obj.ThePatients):
            self.addpatient(this_patient, index)

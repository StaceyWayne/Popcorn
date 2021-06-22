import tkinter as tk
#from tkinter import font as tkFont
from itertools import cycle
#The multilistbox makes little  sense to me - stole it from someone on line but it is over my head
#<script src="https://gist.github.com/novel-yet-trivial/49fa18828cddca44a2befae84cfd67ad.js"></script>
def multiple(*func_list):
    '''run multiple functions as one'''
    # I can't decide if this is ugly or pretty
    return lambda *args, **kw: [func(*args, **kw) for func in func_list];
    None


def scroll_to_view(scroll_set, *view_funcs):
    ''' Allows one widget to control the scroll bar and other widgets
    scroll set: the scrollbar set function
    view_funcs: other widget's view functions
    '''

    def closure(start, end):
        scroll_set(start, end)
        for func in view_funcs:
            func('moveto', start)

    return closure

class MultiListbox(tk.Frame):
    def __init__(self, master=None, columns=2, data=[], row_select=True, **kwargs):
        '''makes a multicolumn listbox by combining a bunch of single listboxes
        with a single scrollbar
        :columns:
          (int) the number of columns
          OR (1D list or strings) the column headers
        :data:
          (1D iterable) auto add some data
        :row_select:
          (boolean) When True, clicking a cell selects the entire row
        All other kwargs are passed to the Listboxes'''
        tk.Frame.__init__(self, master, borderwidth=1, highlightthickness=1, relief=tk.SUNKEN)
        self.rowconfigure(1, weight=1)
        self.columns = columns


        if isinstance(self.columns, (list, tuple)):
        #    for col, text in enumerate(self.columns):  #I don't need the lables - Stacey
        #        tk.Label(self, text=text).grid(row=0, column=col)
            self.columns = len(self.columns)

        self.boxes = []
        for col in range(self.columns):
            box = tk.Listbox(self, exportselection=not row_select, **kwargs)
            if row_select:
                box.bind('<<ListboxSelect>>', self.selected)
            box.grid(row=1, column=col, sticky='nsew')
            self.columnconfigure(col, weight=1)
            self.boxes.append(box)
        vsb = tk.Scrollbar(self, orient=tk.VERTICAL,
                           command=multiple(*[box.yview for box in self.boxes]))
        vsb.grid(row=1, column=col + 1, sticky='ns')
        for box in self.boxes:
            box.config(yscrollcommand=scroll_to_view(vsb.set,
                                                     *[b.yview for b in self.boxes if b is not box]))
        self.add_data(data)


    def set_demensions(self, thisheight, thiswidth):
        for box in self.boxes:
            box.config(height=thisheight, width=int(thiswidth/3))

    def whichchosen(self):  #Stacey added this
        if len(self.boxes[0].curselection())==0:
            return(-1)
        else:
            return(self.boxes[0].curselection()[0])

    def selected(self, event=None):
        row = event.widget.curselection()[0]
        for lbox in self.boxes:
            lbox.select_clear(0, tk.END)
            lbox.select_set(row)

    def add_patient(self, patient,index):#Stacey added this

        temp=1
        self.boxes[0].insert(index,patient.Name)
        self.boxes[1].insert(index, patient.RoomNumber)
        self.boxes[2].insert(index, patient.DOBStr)

#Can't figure out how to get add_data to work but made my own
    def add_data(self, data=[]):
        '''takes a 1D list of data and adds it row-wise
        If there is not enough data to fill the row, then the row is
        filled with empty strings
        these will not be back filled; every new call starts at column 0'''
        # it is essential that the listboxes all have the same length.
        # because the scroll works on "percent" ...
        # and 100% must mean the same in all cases
        boxes = cycle(self.boxes)
        idx = -1
        for idx, (item, box) in enumerate(zip(data, boxes)):
            box.insert(tk.END, item)
        for _ in range(self.columns - idx % self.columns - 1):
            next(boxes).insert(tk.END, '')

    def __getitem__(self, index):
        '''get a row'''
        return [box.get(index) for box in self.boxes]

    def __delitem__(self, index):
        '''delete a row'''
        [box.delete(index) for box in self.boxes]

    def curselection(self):
        '''get the currently selected row'''
        selection = self.boxes[0].curselection()
        return selection[0] if selection else None

    def Scroll(self,Direction):  #Direction is either +1 or -1
        self.boxes[0].yview_scroll(Direction,"pages")
        self.boxes[1].yview_scroll(Direction, "pages")
        self.boxes[2].yview_scroll(Direction, "pages")
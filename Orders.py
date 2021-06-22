from tkinter import font as tkfont
import tkinter as tk


class OrderScreenClass:
    def __init__(self, main_window, thispatientobj, labobj, radiologyobj, theotherodersobj):
        self.window = main_window
        self.patient_obj = thispatientobj
        self.labobj = labobj
        self.theotherodersobj = theotherodersobj
        self.radiologyobj = radiologyobj
        self.curselection = -1

    def buildorderframe(self):

        this_frame = self.window.nametowidget("add_order_frame")
        this_frame.rowconfigure(0, weight=1)
        this_frame.columnconfigure(0,  weight=1)
        this_frame.columnconfigure(5, weight=1)

        times14 = tkfont.Font(family="Times", size=14)
        times24 = tkfont.Font(family="Times", size=24)

        thisrow = 1
        labeltitle = tk.Label(this_frame, text="Add Order for Patient", height=2, font=times24)
        labeltitle.grid(column=2, row=thisrow, columnspan=3, stick="NEWS")

        thisrow = thisrow + 1
        labelpatient1 = tk.Label(this_frame, text="Patient", font=times14, width=15)
        labelpatient1.grid(column=2, row=thisrow, stick="NEWS")
        labeldob1 = tk.Label(this_frame, text="DOB", font=times14, width=15)
        labeldob1.grid(column=3, row=thisrow, stick="NEWS")
        labelroom1 = tk.Label(this_frame, text="Room Number", font=times14, width=15)
        labelroom1.grid(column=4, row=thisrow, stick="NEWS")

        thisrow = thisrow + 1
        labelpatient2 = tk.Label(this_frame, name="ptnamelabel", text="", width=15, font=times14, height=2, wraplength=150)
        labelpatient2.grid(column=2, row=thisrow, stick="NEWS")
        labeldob2 = tk.Label(this_frame, name="ptdoblabel", text="", width=15, font=times14)
        labeldob2.grid(column=3, row=thisrow, stick="NEWS")
        labelroom2 = tk.Label(this_frame, name="ptroomnumberlabel", text="", width=15, font=times14)
        labelroom2.grid(column=4, row=thisrow, stick="NEWS")

        def labbuttonpressed():
            self.labobj.setreturnframe(this_frame)
            self.labobj.setparententryorders(entryorders)
            self.window.nametowidget("lab_frame").tkraise()

        def radbuttonpressed():
            self.radiologyobj.setreturnframe(this_frame)
            self.radiologyobj.setparententryorders(entryorders)
            self.window.nametowidget("radiology_frame").tkraise()

        def ordersetpressed():
            self.theotherodersobj.setreturnframe(this_frame)
            self.theotherodersobj.setparententryorders(entryorders)
            self.window.nametowidget("other_order_frame").tkraise()

        def updateorders():

            if self.curselection>-1:
                self.patient_obj.ThePatients[self.curselection].order = entryorders.get(1.0, tk.END)

            displaycensusframe = self.window.nametowidget("display_census")
            oneframe = displaycensusframe.nametowidget("bottombuttonframe")

            printbutton = oneframe.nametowidget("printbutton")
            printbutton.config(state="normal")
            displaycensusframe.tkraise()

        def cancel():
            displaycensusframe = self.window.nametowidget("display_census")
            displaycensusframe.tkraise()

        thisrow = thisrow + 1
        presetorders = tk.Frame(this_frame)
        presetorders.grid(column=1, row=thisrow)
        labbutton = tk.Button(presetorders, font=times14, text="Add Labs", command=labbuttonpressed)
        labbutton.grid(column=1, row=1, sticky="NEWS")
        radbutton = tk.Button(presetorders, font=times14, text="Add Radiology", command=radbuttonpressed)
        radbutton.grid(column=1, row=2, sticky="NEWS")
        ordersetbutton = tk.Button(presetorders, font=times14, text="Order Sets", command=ordersetpressed)
        ordersetbutton.grid(column=1, row=3, sticky="NEWS")

        entryorders = tk.Text(this_frame, name="entryorders", width=45, height=13)
        entryorders.config(font=times14)
        entryorders.insert(tk.END,  "")
        entryorders.grid(row=thisrow, column=2, sticky="NEWS", columnspan=3)

        thisrow = thisrow + 1
        updatebutton = tk.Button(this_frame, text="Update Orders", font=times14, command=updateorders)
        updatebutton.grid(column=2, row=thisrow, sticky="NEWS")
        cancelbutton = tk.Button(this_frame, text="Cancel", font=times14, command=cancel)
        cancelbutton.grid(column=4, row=thisrow, sticky="NEWS")

        thisrow = thisrow + 1
        this_frame.rowconfigure(thisrow, weight=1)

    def setpatient(self, chosen):

        ptname = self.patient_obj.ThePatients[chosen].name
        ptroomnumber = self.patient_obj.ThePatients[chosen].roomnumber
        ptdob = self.patient_obj.ThePatients[chosen].dobstr

        thisframe = self.window.nametowidget("add_order_frame")

        templabel = thisframe.nametowidget("ptnamelabel")
        templabel.configure(text=ptname)

        templabel = thisframe.nametowidget("ptdoblabel")
        templabel.configure(text=ptdob)

        templabel = thisframe.nametowidget("ptroomnumberlabel")
        templabel.configure(text=ptroomnumber)

        temptextbox = thisframe.nametowidget("entryorders")
        temptextbox.delete("1.0", tk.END)
        temptextbox.insert(tk.END, self.patient_obj.ThePatients[chosen].order)

        self.curselection = chosen
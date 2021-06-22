import sys
import subprocess
import os
import sys
from tkinter import font as tkfont
import tkinter as tk
from tkinter import messagebox
from PatientClass import OnePatientClass
from PatientClass import PatientClass
from tkinter import messagebox
from Misc import TextScrollCombo
from Misc import MyMultiListBox
from Misc import MyListBox

NAME = 0
ROOM = 1
DOB = 2


class DisplayCensusClass:
    def __init__(self, main_window, thispatientobj, addorders, provider):
        self.window = main_window
        self.patient_obj = thispatientobj
        self.addorders_obj = addorders
        self.the_provider = provider
        self.census_file_names = []
        self.whichpatientforalterscreen = -1

    def create_new_census_frame(self):
        this_frame = self.window.nametowidget("create_census_frame")
        this_census = PatientClass(self.the_provider)

        def cancel():
            census_textbox.cleartext()
            census_name_entry.delete(0, tk.END)
            self.window.nametowidget("base_frame").tkraise()

        def save():
            name = census_name_entry.get()
            nonlocal this_census
            entries = os.listdir()
            continue_this = True

            for filename in entries:
                if filename == (name + ".csv"):
                    question = name + " already exits.  Overwrite?"
                    confirmation = tk.messagebox.askquestion("Overwrite", question, icon="warning")
                    continue_this = (confirmation == 'yes')

            if continue_this:
                this_census.CensusName = name
                this_census.savecensus()

                displaycensusframe = self.window.nametowidget("display_census")
                listboxcensus = displaycensusframe.nametowidget("listboxcensus")

                for index, one_patient in enumerate(self.patient_obj):
                    listboxcensus.addpatient(one_patient, index)
                cancel()

        def prasecensus():
            thetext = census_textbox.gettextaslines()

            nonlocal this_census
            badlines = 0
            for oneline in thetext:

                onepatient = OnePatientClass()
                if onepatient.parseoneline_bdayreport(oneline) == 1:
                    this_census.add_patient_one_patient(onepatient)
                else:
                    badlines = badlines + 1

            if badlines > 0:
                messagetxt = "There were " + str(badlines) + " unconverted lines"
                messagebox.showinfo("bad data", messagetxt)

            if len(this_census.ThePatients) == 0:
                messagebox.showinfo("Error", "Not able to parse this data as a census")
            else:
                self.patient_obj.clearcensus()
                for thispatient in this_census.ThePatients:
                    self.patient_obj.ThePatients.append(thispatient)

                census_textbox.cleartext()
                self.opendisplaycensusframe()

        times24 = tkfont.Font(family="Times", size=24)
        buttonfont = tkfont.Font(family="Times", size=18)
        #    times12 = tkfont.Font(family="Times", size=12)

        thisrow = 0
        this_frame.rowconfigure(thisrow, weight=1)
        this_frame.columnconfigure(0, weight=1)
        this_frame.columnconfigure(6, weight=1)

        thisrow = thisrow + 1
        lable_title = tk.Label(this_frame, text="Create a new census", width=45, height=1)
        lable_title.config(font=times24, anchor='center')
        lable_title.grid(row=thisrow, column=1, columnspan=5)

        thisrow = thisrow + 1
        census_textbox = TextScrollCombo(this_frame)
        census_textbox.grid(row=thisrow, column=1, columnspan=5)
        census_textbox.config(width=600, height=250)

        thisrow = thisrow + 1
        parsing_button = tk.Button(this_frame, anchor="e", text="Parse Data", font=buttonfont, command=prasecensus)
        parsing_button.grid(row=thisrow, column=1, sticky='e')

        save_button = tk.Button(this_frame, text="Save", font=buttonfont, command=save)
        save_button.grid(row=thisrow, column=3)
        save_button.config(state="disable")

        cancel_button = tk.Button(this_frame, anchor="w", text="Done", font=buttonfont, command=cancel)
        cancel_button.grid(row=thisrow, column=5, sticky='w')

        thisrow = thisrow + 1

        census_name_lable = tk.Label(this_frame, text="Name of Census", font=buttonfont)
        census_name_lable.grid(row=thisrow, column=2)

        census_name_entry = tk.Entry(this_frame, width=10, font=buttonfont)
        census_name_entry.grid(row=thisrow, column=4)
        census_name_entry.config(state="disable")

        thisrow = thisrow + 1
        this_frame.rowconfigure(thisrow, weight=1)

    def opendisplaycensusframe(self):
        nextframe = self.window.nametowidget("display_census")
        bottombuttonframe = nextframe.nametowidget("bottombuttonframe")
        censusnamebox = bottombuttonframe.nametowidget("censustextbox")
        censusnamebox.delete(0, 'end')
        censusnamebox.insert(tk.END,  self.patient_obj.CensusName)
        patientlistbox = nextframe.nametowidget("patientlistbox")
        patientlistbox.populatelistbox()


        printordersbutton = bottombuttonframe.nametowidget("printbutton")
        if self.patient_obj.arethereorders():
            printordersbutton["state"] = "normal"
        else:
            printordersbutton["state"] = "disable"

        nextframe.tkraise()

    def buildcensuslistnotempty(self):
        this_frame = self.window.nametowidget("patient_census_frame_not_empty")
        times24 = tkfont.Font(family="Times", size=24)
        thisrow = 0

        this_frame.rowconfigure(thisrow, weight=1)
        this_frame.columnconfigure(0, weight=1)
        this_frame.columnconfigure(2, weight=1)

        thisrow = thisrow + 1

        listboxcensus = MyListBox(times24, this_frame, name="listboxcensus")
        listboxcensus.grid(row=thisrow, column=1)

        thisrow = thisrow + 1
        labelspacer = tk.Label(this_frame, text='', height=3)
        labelspacer.grid(row=thisrow, column=0)

        thisrow = thisrow + 1

        choosebutton = tk.Button(this_frame, text="Load")
        choosebutton.config(command=lambda: self.loadpatientcensusfile(listboxcensus.whichchosen()))
        choosebutton.config(font=times24)
        choosebutton.grid(row=thisrow, column=1)

        thisrow = thisrow + 1
        cancelbutton = tk.Button(this_frame, text="Cancel")
        cancelbutton.config(command=self.window.nametowidget("base_frame").tkraise)
        cancelbutton.config(font=times24)
        cancelbutton.grid(row=thisrow, column=1)

        thisrow = thisrow + 1
        this_frame.rowconfigure(thisrow, weight=1)

    def buildcensuslistempty(self):
        thisrow = 0

        this_frame = self.window.nametowidget("patient_census_frame_empty")
        times24 = tkfont.Font(family="Times", size=24)
        this_frame.rowconfigure(thisrow, weight=1)
        this_frame.columnconfigure(0, weight=1)
        this_frame.columnconfigure(2, weight=1)

        choosebutton = tk.Button(this_frame, command=self.window.nametowidget("base_frame").tkraise)
        choosebutton.config(text="No Census to load")
        choosebutton.config(font=times24)
        choosebutton.grid(row=thisrow, column=1)
        thisrow = thisrow + 1
        this_frame.rowconfigure(thisrow, weight=1)

    def loadcensus_file_names(self):
        self.census_file_names = []
        entries = os.listdir()
        for thisfile in entries:
            tempstr = thisfile.partition(".")

            if tempstr[2] == "csv":
                self.census_file_names.append(tempstr[0])

        if len(self.census_file_names) == 0:
            return 0
        else:
            censusloadframe = self.window.nametowidget("patient_census_frame_not_empty")
            listboxcensus = censusloadframe.nametowidget("listboxcensus")
            listboxcensus.populatelistbox(self.census_file_names)
            return 1

    def loadpatientcensusfile(self, filename):

        self.patient_obj.clearcensus()
        nursinghomename = filename.partition('.')[0]

        filename = filename + '.csv'

        fileinput = open(filename, 'r')
        alllines = fileinput.readlines()

        for oneline in alllines:
            if oneline.count('@') == 2:
                self.patient_obj.add_patient_csv(oneline)

        self.patient_obj.sortpatients(2)
        self.patient_obj.CensusName = nursinghomename

        self.opendisplaycensusframe()

    def builddisplaycensusframe(self):

        def alterdata():

            chosen = patientlistbox.whichchosen()
            self.whichpatientforalterscreen = chosen

            if chosen == -1:
                messagebox.showinfo("Error", "Need to select a patient.")
                return
            #self.buildpatientchangeform(patientlistbox.whichchosen())
            self.settextforalterdatascreen()

        def savecensus():
            self.patient_obj.CensusName = censusnamevar.get()

            self.patient_obj.savecensus()

        def newpatient():
            anewpatient = OnePatientClass()
            self.patient_obj.ThePatients.append(anewpatient)
            self.window.nametowidget("change_patient_data").tkraise()

        def order():
            chosen = patientlistbox.whichchosen()
            if chosen == -1:
                messagebox.showinfo("Error", "Need to select a patient.")
                return

            self.addorders_obj.setpatient(chosen)
            #   self.addorders_obj.buildorderframe(chosen)
            self.window.nametowidget("add_order_frame").tkraise()

        def printorders():
            if not(self.patient_obj.arethereorders()):
                msg = 'There are no orders to print'
                messagebox.showinfo('Error', msg)
            else:
                self.patient_obj.printallorders()
                subprocess.Popen("orders.pdf", shell=True)

        def finish():
            baseframe = self.window.nametowidget("base_frame")
            baseframe.tkraise()

        def deletecensus():
            messagetxt = "Are you sure you want to delete this census?\n"
            messagetxt = messagetxt + "This will delete all data including current orders"
            confirmation = messagebox.askquestion("Delete Census", messagetxt, icon="warning")
            if confirmation == "yes":
                self.patient_obj.clearcensus()

            patientlistbox.populatelistbox()
            entryname.delete(0, tk.END)

        def deleteorders():
            messagetxt = "Are you sure you want to delete all orders?"

            confirmation = messagebox.askquestion("Delete Census", messagetxt, icon="warning")
            if confirmation == "yes":
                self.patient_obj.deleteorders()

            printordersbutton["state"] = "disable"

        def exitprogram():
            if self.patient_obj.arethereorders():
                confirmation = messagebox.askquestion("Exit", "The are orders on the current patient list.  Do you need to print them still?" )
                if not(confirmation=='yes'):
                    sys.exit()
            else:
              sys.exit()

        buttonfont = tkfont.Font(family="Times", size=14)
        times24 = tkfont.Font(family="Times", size=24)

        this_frame = self.window.nametowidget("display_census")

        thisrow = 0
        this_frame.rowconfigure(thisrow, weight=1)
        this_frame.columnconfigure(0, weight=1)
        this_frame.columnconfigure(2, weight=1)

        thisrow = thisrow + 1

        titletxt = "Census List For " + self.patient_obj.CensusName
        labeltitlebase = tk.Label(this_frame, text=titletxt, width=35, font=times24)
        labeltitlebase.grid(column=1, row=thisrow)

        thisrow = thisrow + 1
        patientlistbox = MyMultiListBox(self.patient_obj, buttonfont, this_frame, name="patientlistbox")

        patientlistbox.config(width=100)
        patientlistbox.grid(column=1, row=thisrow, sticky="NEWS", columnspan=2)

        thisrow = thisrow + 1

        bottombuttonframe = tk.Frame(this_frame, name="bottombuttonframe")
        bottombuttonframe.grid(column=1, row=thisrow, sticky='news')

        bottombuttonframe.columnconfigure(0, weight=1)
        bottombuttonframe.columnconfigure(4, weight=1)

        alterdatabutton = tk.Button(bottombuttonframe, text="Alter Patient's Data", command=alterdata)
        alterdatabutton.config(font=buttonfont, width=15)
        alterdatabutton.grid(row=1, column=1, sticky="w")

        savedatabutton = tk.Button(bottombuttonframe, text="Save Census", font=buttonfont, width=15, command=savecensus)
        savedatabutton.grid(row=1, column=2, columnspan=2)

        deletedatabutton = tk.Button(bottombuttonframe, text="Delete Census", command=deletecensus)
        deletedatabutton.config(font=buttonfont, width=15)
        deletedatabutton.grid(row=1, column=4, sticky="e")

        newpatientbutton = tk.Button(bottombuttonframe, text="Add Patient", width=15, command=newpatient)
        newpatientbutton.config(font=buttonfont)
        newpatientbutton.grid(row=2, column=1, sticky="w")

        censusnamelabel = tk.Label(bottombuttonframe, text=' Census Name:  ', font=buttonfont)
        censusnamelabel.grid(row=2, column=2, sticky="w")

        censusnamevar = tk.StringVar(bottombuttonframe, self.patient_obj.CensusName, name="censusname")
        entryname = tk.Entry(bottombuttonframe, font=buttonfont, name="censustextbox", width=10, textvariable=censusnamevar)
        entryname.grid(row=2, column=3, sticky="e")

        orderbutton = tk.Button(bottombuttonframe, text="Order", font=buttonfont, width=15, command=order)
        orderbutton.grid(row=2, column=4, sticky="e")

        printordersbutton = tk.Button(bottombuttonframe, name="printbutton", width=15, command=printorders)
        printordersbutton.config(font=buttonfont)
        printordersbutton.config(text="Print Orders")
        printordersbutton.grid(row=3, column=1, sticky="w")

        deleteordersbutton = tk.Button(bottombuttonframe, text="Delete Orders", width=15, command=deleteorders)
        deleteordersbutton.config(font=buttonfont)
        deleteordersbutton.grid(row=3, column=2, columnspan=2)

        finishbutton = tk.Button(bottombuttonframe, text="Finish", font=buttonfont, width=15, command=finish)
        finishbutton.grid(row=3, column=4, sticky="e")

        exitprogram = tk.Button(bottombuttonframe, text="Exit Program", font=buttonfont, width=15, command=exitprogram)
        exitprogram.grid(row=4, column=2, columnspan=2)

        # spacerlabel = tk.Label(bottombuttonframe, text="", width=100)
        # spacerlabel.grid(row=4, column=1, columnspan=3)

#   this needs to be done before each raise of frame
        if self.patient_obj.arethereorders():
            printordersbutton["state"] = "normal"
        else:
            printordersbutton["state"] = "disable"

        thisrow = thisrow + 1
        this_frame.rowconfigure(thisrow, weight=1)

#    #####    This is a frame for updating patient data
#    ####    Will  likely be used only rarely
#    ####     Mostly for changing the room number
#    ####     I suspect most providers will be too lazy to even do that
#    ####    Frame name is ChangePatientData

    def settextforalterdatascreen(self):
        thisframe = self.window.nametowidget("change_patient_data")
        onepatient = self.patient_obj.ThePatients[self.whichpatientforalterscreen]
        thisframe.nametowidget('entryname').insert(0, onepatient.name)
        thisframe.nametowidget('entrydob').insert(0, onepatient.dobstr)
        thisframe.nametowidget('entryroom').insert(0, onepatient.roomnumber)

        thisframe.tkraise()

    def buildpatientchangeform(self):
        def updatedata():
            thispatient = OnePatientClass()
            thispatient.name = namevar.get().title()
            thispatient.dobstr = dobvar.get()

            thispatient.roomnumber = roomvar.get()
            if thispatient.builddate() == -1:
                messagebox.showinfo("Date Error", "You entered date in the wrong format")
                return

            self.patient_obj.updatedate(self.whichpatientforalterscreen, thispatient)
            self.patient_obj.sortpatients(NAME)

            deleteentryboxes()
            self.opendisplaycensusframe()

        def cancel():
            deleteentryboxes()
            self.window.nametowidget("display_census").tkraise()

        def deleteentryboxes():
            entryroom.delete(0, 'end')
            entryname.delete(0, 'end')
            entrydob.delete(0, 'end')

        times24 = tkfont.Font(family="Times", size=24)
        times16 = tkfont.Font(family="Times", size=16)

        thisframe = self.window.nametowidget("change_patient_data")
        thisrow = 0

        thisframe.columnconfigure(0, weight=1)
        thisframe.columnconfigure(4, weight=1)

        thisrow = thisrow + 1
        screentitle = tk.Label(thisframe, text="Change Patient's Data", font=times24, height=3)
        screentitle.grid(row=thisrow, column=1, columnspan=3, sticky='n')

        thisrow = thisrow + 1
        labelname = tk.Label(thisframe, pady=20, text="Name", padx=75, font=times16, height=1)
        labelname.grid(row=thisrow, column=1, columnspan=1, sticky='news')

        labeldob = tk.Label(thisframe, text="Date of Birth", padx=75, font=times16, height=1)
        labeldob.grid(row=thisrow, column=2, columnspan=1)

        labelroomnumber = tk.Label(thisframe, text="Room Number", padx=75, font=times16, height=1)
        labelroomnumber.grid(row=thisrow, column=3, columnspan=1)
        thisrow = thisrow + 1

        thisrow = thisrow + 1
        namevar = tk.StringVar(thisframe)
        entryname = tk.Entry(thisframe, name='entryname', textvariable=namevar)
        entryname.grid(row=thisrow, column=1)

        dobvar = tk.StringVar(thisframe)
        entrydob = tk.Entry(thisframe, name='entrydob', textvariable=dobvar)
        entrydob.grid(row=thisrow, column=2)

        roomvar = tk.StringVar(thisframe)
        entryroom = tk.Entry(thisframe, name='entryroom', textvariable=roomvar)
        entryroom.grid(row=thisrow, column=3)

        thisrow = thisrow + 1

        updatedatabutton = tk.Button(thisframe, pady=25, width=10, text="Update Data", font=times16, command=updatedata)
        updatedatabutton.grid(row=thisrow, column=1)

        cancelbutton = tk.Button(thisframe, pady=25, width=10, font=times16, text="Cancel", command=cancel)
        cancelbutton.grid(row=thisrow, column=3)
        thisframe.rowconfigure(thisrow, weight=1)

    def buildeverything(self):
        self.create_new_census_frame()
        self.buildcensuslistnotempty()
        self.buildcensuslistempty()
        self.builddisplaycensusframe()
        self.buildpatientchangeform()
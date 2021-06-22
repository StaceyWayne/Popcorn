from datetime import datetime
import os
from tkinter import font as tkfont
import tkinter as tk
from fpdf import FPDF
from datetime import date
import pickle
from tkinter import messagebox

NAME = 0
ROOM = 1
DOB = 2




class ProviderFileClass:
    def __init__(self):
        self.name = ""
        self.dea = ""
        self.title = ""


class ProviderClass:
    def __init__(self, window):

        self.name = ""
        self.dea = ""
        self.title = ""
        self.window = window

    def loadprovider(self):
        if os.path.exists("Provider.swm") and os.access("Provider.swm", os.R_OK):
            with open("Provider.swm", 'rb') as mypicklefile:
                temp = pickle.load(mypicklefile)

            self.name = temp.name
            self.dea = temp.dea
            self.title = temp.title

            return 1
        else:
            return 0

#   This is for any provider data
#   Frame name is providerframe
    def buildproviderframe(self):
        #     global this_provider

        this_frame = self.window.nametowidget("provider_frame")

        this_frame.rowconfigure(0, weight=1)

        this_frame.columnconfigure(0, weight=1)
        this_frame.columnconfigure(0, weight=3)

        times24 = tkfont.Font(family="Times", size=24)
        times16 = tkfont.Font(family="Times", size=16)

        thisrow = 1
        labelspacer1 = tk.Label(this_frame, text="", anchor='center', width=10, height=1)
        labelspacer1.grid(row=thisrow, column=1, columnspan=1)

        thisrow = thisrow + 1
        screentitle = tk.Label(this_frame, text="Provider Data", font=times24, anchor='center', height=1, width=45)
        screentitle.grid(row=thisrow, column=1, columnspan=3)

        thisrow = thisrow + 1
        name_label = tk.Label(this_frame, padx=100, text="Name:", font=times16, height=1)
        name_label.grid(row=thisrow, column=1, sticky='w')

        namevar = tk.StringVar(this_frame)
        namevar.set(self.name)
        name_entry = tk.Entry(this_frame,  width=30, font=times16, textvariable=namevar)
        name_entry.config(state="normal")

        name_entry.grid(row=thisrow, column=2)

        thisrow = thisrow + 1
        name_label = tk.Label(this_frame, padx=100, text="DEA #:", font=times16, height=1)
        name_label.grid(row=thisrow, column=1, sticky='w')

        deavar = tk.StringVar(this_frame, self.dea)
        dea_entry = tk.Entry(this_frame, width=30, font=times16, textvariable=deavar)
        dea_entry.grid(row=thisrow, column=2)

        thisrow = thisrow + 1
        title_label = tk.Label(this_frame, padx=100, text="Order sheet title:", font=times16, height=1)
        title_label.grid(row=thisrow, column=1, sticky='w')

        title_var = tk.StringVar(this_frame, self.title)
        title_entry = tk.Entry(this_frame, width=30, font=times16, textvariable=title_var)
        title_entry.grid(row=thisrow, column=2)



        def save_provider():
            local_provider = ProviderFileClass()

            local_provider.name = name_entry.get()
            local_provider.dea = dea_entry.get()
            local_provider.title = title_entry.get()

            with open("Provider.swm", "wb") as mypicklefile:
                pickle.dump(local_provider, mypicklefile)
                mypicklefile.close()

        #    global this_provider
            self.name = local_provider.name
            self.dea = local_provider.dea
            self.title = local_provider.title
        #    this_provider = local_provider
            self.window.nametowidget("base_frame").tkraise()

        def cancel():
            self.window.nametowidget("base_frame").tkraise()

        thisrow = thisrow + 1
        save_button = tk.Button(this_frame, text="Save", font=times16, command=save_provider)
        save_button.grid(row=thisrow,  column=1)

        cancel_button = tk.Button(this_frame, text="Cancel", font=times16, command=cancel)
        cancel_button.grid(row=thisrow,  column=2)

        thisrow = thisrow + 1
        this_frame.rowconfigure(thisrow, weight=1)

class PDF(FPDF):
    def __init__(self, this_provider, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.this_provider = this_provider

    def header(self):

        self.set_font('Times', 'B', 24)

        self.cell(200, 9, self.this_provider.title, align='C')
        # Line break
        self.ln(10)

    def footer(self):

        self.set_font('Times', '', 18)
        # Calculate width of title and position

        self.set_y(-60)
        self.cell(20, 10, txt="Provider:", align='L')

        #       ProviderName="Stacey Melnick, ANP"  # eventually this will be uploaded from a file
        #      ProviderDEA="MM4718839"
        size_one_letter = 6.35  
        # 1 pt is 1/72 inches
        start_position_right = size_one_letter*(5*len(self.this_provider.name))
        self.set_x(start_position_right)
        self.cell(0, 10, self.this_provider.name, align='R')

        self.set_y(-40)
        underline = "_"*len(self.this_provider.name)

        self.cell(20, 10, txt="Signature", align='L')
        self.set_x(start_position_right)
        self.cell(0, 10, underline, align='R')

        self.set_y(-30)
        self.cell(20, 10, txt="Date", align='L')
        self.set_x(start_position_right)
        self.cell(0, 10, date.today().strftime("%m/%d/%y"), align='R')

        self.set_y(-15)
        self.cell(20, 10, txt="DEA#:", align='L')
        self.set_x(start_position_right)
        self.cell(0, 10, self.this_provider.dea, align='R')


#   easier than learning Python's, no manipulation will be done here
class DateClass:  
    Month = 1
    Day = 1
    Year = 1900
    OneNumber = 1900*10000+Month*100+Day  
    # This will put the dates into a single number


class OnePatientClass:

    def __init__(self):
        self.name = ""
        self.dobstr = ""
        self.roomnumber = ""
        self.dob = DateClass()
        self.order = ""

    def parseoneline(self, oneline):

        oneline = oneline.replace("\n", "")
        oneline = oneline.replace('"', "")
        tempstr = oneline.partition('@')

        # lastname = tempstr[0]
        # tempstr = tempstr[2].partition(',')
        # firstname = tempstr[0]
        # self.name = lastname + ", " + firstname
        self.name = tempstr[0]

        tempstr = tempstr[2].partition('@')
        self.roomnumber = tempstr[0]
        # tempstr = tempstr[2].partition(',')
        self.dobstr = tempstr[2]
        self.builddate()

    def parseoneline_bdayreport(self, oneline):
        # the birthday report doesn't seem too have Jr/Sr/III appendages
        firststop = oneline.find("(")
        if firststop == -1:
            return-1

        self.name = oneline[:firststop - 1]
        self.name = self.name.title()

        oneline = oneline[firststop:]
        self.dobstr = oneline[-12:]
        if not(self.builddate() == 1):
            return -1

        temp = oneline.partition("\t")
        secondstop = temp[2].find("\t")
        if secondstop > -1:
            #            x = temp[2]
            #            self.roomnumber = "1"
            self.roomnumber = temp[2][:secondstop]
        else:
            return -1

        return 1

    def builddate(self):

        try:
            thedate = datetime.strptime(self.dobstr, '%b %d, %Y')
        except ValueError:

            try:
                thedate = datetime.strptime(self.dobstr, '%m/%d/%Y')
            except ValueError:
                return -1

        self.dob.Day = thedate.day
        self.dob.Month = thedate.month
        self.dob.Year = thedate.year

        self.dobstr = thedate.__format__('%b %d, %Y')
        self.dob.OneNumber = self.dob.Year*10000 + self.dob.Month*100+self.dob.Day
        return 1


class PatientClass:
    def __init__(self, provider):
        self.ThePatients = []
        self.NextSort = [False, False, False]  
        # False means forward
        self.CensusName = ""
        self.thisprovider = provider

    def add_patient_one_patient(self, onepatient):
        self.ThePatients.append(onepatient)

    def add_patient_csv(self, oneline):  
        # gets a line of text, parses it and adds it to the array of patients

        onepatient = OnePatientClass()
        onepatient.parseoneline(oneline)

        self.ThePatients.append(onepatient)

    def resetnextsort(self, which):

        for index in range(3):
            if which == index:
                self.NextSort[which] = not(self.NextSort[which])
            else:
                self.NextSort[index] = False
    
    def sortpatients(self, bywhat):

        # ByWhat meaning/ 1/name, 2/room, 3/date of birth
        # I'm sure that there is a more elegant way of doing this but I don't know how

        if bywhat == NAME:
            self.ThePatients.sort(key=lambda x: x.name, reverse=self.NextSort[NAME])
        elif bywhat == ROOM:
            self.ThePatients.sort(key=lambda x: x.roomnumber, reverse=self.NextSort[ROOM])
        else:
            self.ThePatients.sort(key=lambda x: x.dob.OneNumber, reverse=self.NextSort[DOB])

        self.resetnextsort(bywhat)

    def clearcensus(self):
        self.__init__(self.thisprovider)
        #  This was too easy - waiting for something to go wrong

    def savecensus(self):

        filename = self.CensusName+".csv"
        file_object = open(filename, "w")

        for patient in self.ThePatients:
            oneline = patient.name + "@" + patient.roomnumber + "@" + patient.dobstr + "\n"
            file_object.write(oneline)

        file_object.close()

    def deleteorders(self):
        for patient in self.ThePatients:
            patient.order = ""

    def arethereorders(self):

        if len(self.ThePatients)==0:
            return False

        for onepatient in self.ThePatients:
            if not(onepatient.order == ""):
                return True

        return False

    def updatedate(self, whichone, onepatient):
        self.ThePatients[whichone] = onepatient

# ###     This function will print all orders and then delete them

    def printallorders(self):

        orderoutputfile = PDF(self.thisprovider)

        if self.thisprovider.name == "":
            messagebox.showerror("File Error", "No provider information loaded")

        for ThisPatient in self.ThePatients:
            if not(ThisPatient.order == ""):
                orderoutputfile.add_page()
                orderoutputfile.set_font("Times", size=14)

                # First Print patient data
                orderoutputfile.ln(20)
                orderoutputfile.cell(25, 25)
                orderoutputfile.cell(20, 10, txt="Patient:", align='L')
                orderoutputfile.cell(100, 10, txt=ThisPatient.name, align='R')

                orderoutputfile.ln(6)
                orderoutputfile.cell(25, 25)
                orderoutputfile.cell(20, 10, txt="DOB:", align='L')
                orderoutputfile.cell(100, 10, txt=ThisPatient.dobstr, align='R')

                orderoutputfile.ln(6)
                orderoutputfile.cell(25, 25)
                orderoutputfile.cell(20, 10, txt="Room:", align='L')
                orderoutputfile.cell(100, 10, txt=ThisPatient.roomnumber, align='R')

                orderoutputfile.ln(40)
                orderoutputfile.cell(50, 50)
                orderoutputfile.multi_cell(0, 5, ThisPatient.order)

        orderoutputfile.output("Orders.pdf")

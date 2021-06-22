import tkinter as tk
from tkinter import font as tkFont
from itertools import cycle
from fpdf import FPDF


import os
from tkinter import messagebox


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

    def whichChosen(self):  #Stacey added this
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
        

#Should of known for the start I would be needing this
#Initially just had an array of patients in the main program

NAME = 0
ROOM = 1
DOB = 2

title = 'CRM Physicians Order Sheet'

class PDF(FPDF):
    def header(self):

        self.set_font('Times', 'B', 18)
        # Calculate width of title and position
        w = self.get_string_width(title) + 6
  #      self.set_x((210 - w) / 2)
        # Colors of frame, background and text
  #      self.set_draw_color(0, 80, 180)
  #      self.set_fill_color(230, 230, 0)
  #      self.set_text_color(220, 50, 50)
        # Thickness of frame (1 mm)
 #       self.set_line_width(1)
        # Title
 #       self.cell(w, 9, title, 1, 1, 'C', True)
        self.cell(200, 9, title, align='C')
        # Line break
        self.ln(10)


MONTHABBREVIATIONS= ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

class DateClass():  #easier than learning Python's, no manipulation will be done here
    Month=1
    Day=1
    Year=1900
    OneNumber=1900*10000+Month*100+Day  #This will put the dates into a single number

class OnePatientClass():

    def __init__(self):
        self.Name = ""
        self.DOBStr = ""
        self.RoomNumber = ""
        self.DOB = DateClass()
        self.Orders = ""

    def BuildDate(self):
        MonthStr=self.DOBStr[:3]
        DayStr=self.DOBStr[4:6]
        YearStr=self.DOBStr[8:]
        self.DOB.Day = int(DayStr)
        self.DOB.Year = int(YearStr)
        self.DOB.Month = MONTHABBREVIATIONS.index(MonthStr)+1
        self.DOB.OneNumber = self.DOB.Year*10000 + self.DOB.Month*100+self.DOB.Day


class PatientClass():
    def __init__(self):
        self.ThePatients = []
        self.NextSort=[False,False,False]  #False means forward
        self.CensusName=""


    def AddAPatient(self,oneline):  #gets a line of text, parses it and adds it to the array of patients
        OnePatient=OnePatientClass()

        oneline = oneline.replace("\n", "")
        oneline = oneline.replace('"', "")
        TempStr = oneline.partition(',')

        OnePatient.Name = TempStr[0]
        TempStr = TempStr[2].partition(',')
        OnePatient.RoomNumber = TempStr[0]
        TempStr = TempStr[2].partition(',')
        OnePatient.DOBStr = TempStr[2]
        OnePatient.BuildDate()

        self.ThePatients.append(OnePatient)

    def resetNextSort(self,which):

        for index in range(3):
            if which==index:
                self.NextSort[which]=not(self.NextSort[which])
            else:
                self.NextSort[index]=False
    def SortPatients(self,ByWhat):

        #ByWhat meaning/ 1/name, 2/room, 3/date of birth
        #I'm sure that there is a more elegant way of doing this but I don't know how

        if ByWhat==NAME:
            self.ThePatients.sort(key=lambda x: x.Name, reverse=self.NextSort[NAME])
        elif ByWhat==ROOM:
            self.ThePatients.sort(key=lambda x: x.RoomNumber, reverse=self.NextSort[ROOM])
        else:
            self.ThePatients.sort(key=lambda x: x.DOB.OneNumber, reverse=self.NextSort[DOB])

        self.resetNextSort(ByWhat)


    def UpdateData(self,which,OnePatient):

        self.ThePatients[which] = OnePatient

    def ClearCensus(self):
        self.__init__()   ## This was too easy - waiting for something to go wrong

    def SaveCensus(self):

        FileName=self.CensusName+".csv"
        File_object=open(FileName,"w")

        for patient in self.ThePatients:
            OneLine = patient.Name + "," + patient.RoomNumber + ",00," + patient.DOBStr + "\n"
            File_object.write(OneLine)

        File_object.close()
        temp=1

    def AreThereOrders(self):

        for OnePatient in self.ThePatients:
            if not(OnePatient.Orders==""):
                return(True)

        return False



####     This function will print all orders and then delete them

    def PrintAllOrders(self):

        OrderOutputFile = PDF()

        for ThisPatient in self.ThePatients:
            if not(ThisPatient.Orders==""):
                OrderOutputFile.add_page()
                OrderOutputFile.set_font("Times",size=14)

                #First Print patient data
                OrderOutputFile.ln(20)
                OrderOutputFile.cell(25,25)
                OrderOutputFile.cell(20,10,txt="Patient:", align='L')
                OrderOutputFile.cell(40, 10, txt=ThisPatient.Name, align='R')

                OrderOutputFile.ln(6)
                OrderOutputFile.cell(25,25)
                OrderOutputFile.cell(20,10,txt="DOB:", align='L')
                OrderOutputFile.cell(40, 10, txt=ThisPatient.DOBStr, align='R')

                OrderOutputFile.ln(6)
                OrderOutputFile.cell(25,25)
                OrderOutputFile.cell(20,10,txt="Room:", align='L')
                OrderOutputFile.cell(40, 10, txt=ThisPatient.RoomNumber, align='R')

                OrderOutputFile.ln(40)
                OrderOutputFile.cell(50,50)
                OrderOutputFile.multi_cell(0,5,ThisPatient.Orders)

        OrderOutputFile.output("Orders.pdf")




NAME = 0
ROOM = 1
DOB = 2


def show_frame(frame):
    frame.tkraise()

#########  Frame for adding order  ############
##########  Frame = AddOrderFrame  ##########
def BuildOrderFrame(Chosen):
    Times14 = tkFont.Font(family="Times", size=14)
    Times24 = tkFont.Font(family="Times", size=24)
    PtName = Patients.ThePatients[Chosen].Name
    PtRoomNumber = Patients.ThePatients[Chosen].RoomNumber
    PtDOB =  Patients.ThePatients[Chosen].DOBStr

    ThisRow=1
    LabelTitle = tk.Label(AddOrderFrame, text="Add Order for Patient",height=2, font=Times24).grid(column=2,row=ThisRow,columnspan=3,stick="NEWS")

    ThisRow = ThisRow +1
    LabelSpacer = tk.Label(AddOrderFrame,text="",width = 20).grid(column=1,row=ThisRow)
    LabelPatient1  = tk.Label(AddOrderFrame, text="Patient", font=Times14,width=15)
    LabelPatient1.grid(column=2,row=ThisRow,stick="NEWS")
    LabelDOB1 = tk.Label(AddOrderFrame, text="DOB",  font=Times14, width=15)
    LabelDOB1.grid(column=3, row=ThisRow,stick="NEWS")
    LabelRoom1 = tk.Label(AddOrderFrame, text="Room Number",  font=Times14, width=15)
    LabelRoom1.grid(column=4, row=ThisRow,stick="NEWS")

    ThisRow = ThisRow + 1
    LabelPatient2 = tk.Label(AddOrderFrame, text=PtName,width=15, font=Times14)
    LabelPatient2.grid(column=2,row=ThisRow,stick="NEWS")
    LabelDOB2 = tk.Label(AddOrderFrame, text=PtDOB,  width=15, font=Times14)
    LabelDOB2.grid(column=3, row=ThisRow, stick="NEWS")
    LabelRoom2= tk.Label(AddOrderFrame, text=PtRoomNumber, width=15, font=Times14)
    LabelRoom2.grid(column=4, row=ThisRow, stick="NEWS")

    ThisRow = ThisRow + 1
 #   OrdersVar = tk.StringVar(AddOrderFrame,Patients.ThePatients[Chosen].Orders)
#   EntryName = tk.Text(AddOrderFrame, textvariable = OrdersVar , height=10)
    EntryOrders = tk.Text(AddOrderFrame,width=45, height=15)
    EntryOrders.config(font=Times14)
    EntryOrders.insert(tk.END,Patients.ThePatients[Chosen].Orders)
    EntryOrders.grid(row=ThisRow,column=2,sticky="NEWS",columnspan=3)

    def UpdateOrders():
        thistext=EntryOrders.get(1.0, "end-1c")  #what do these arguments mean?  Just copied them off a website
        Patients.ThePatients[Chosen].Orders=thistext
        for  widget in DisplayCensus.winfo_children():
            widget.destroy()
        BuildDisplayCensusFrame()
        DisplayCensus.tkraise()

    def Cancel():
        for  widget in DisplayCensus.winfo_children():
            widget.destroy()
        BuildDisplayCensusFrame()
        DisplayCensus.tkraise()

    ThisRow = ThisRow + 1
    UpdateButton = tk.Button(AddOrderFrame, text="Update Orders",font=Times14, command=UpdateOrders)
    UpdateButton.grid(column=2, row= ThisRow, sticky="NEWS")
    CancelButton = tk.Button(AddOrderFrame, text="Cancel",font=Times14, command=Cancel)
    CancelButton.grid(column=4, row= ThisRow, sticky="NEWS")


########  The Frame for showing the Census                   ################
###########   Fame = DisplayCensus  #######################

def BuildDisplayCensusFrame():
    Times12 = tkFont.Font(family="Times", size=12)
    ThisRow=0
#    LabelSpacer1 = tk.Label(DisplayCensus, text="", font="Times,24", anchor='center', width=10, height=1).pack()
    LabelSpacer1 = tk.Label(DisplayCensus, text="",height=2, width=5).grid(column=1,row=ThisRow)
    LabelSpacer2 = tk.Label(DisplayCensus, text="",height=2,width=30).grid(column=2,row=ThisRow)
    LabelSpacer3 = tk.Label(DisplayCensus, text="",height=2,width=30).grid(column=3, row=ThisRow)
    LabelSpacer4 = tk.Label(DisplayCensus, text="",height=2,width=30).grid(column=4, row=ThisRow)
    LabelSpacer5 = tk.Label(DisplayCensus, text="",height=2,width=1).grid(column=5, row=ThisRow)





    LabelTitleBaseFrame = tk.Label(DisplayCensus, text="Census List For " + NursingHomeName, font=("Times",24),anchor='center').grid(column=1,row=ThisRow,columnspan=5)

    def SortList(WhichVar):  #I'm confident that instead of passing a number I could pass the quality to be sorted by - but how?
        Patients.SortPatients(WhichVar)
        for  widget in DisplayCensus.winfo_children():
            widget.destroy()

        BuildDisplayCensusFrame()
        DisplayCensus.tkraise()

    def MoveList(Direction):
        PatientListBox.Scroll(Direction)
        temp=1

#Move forward/backward buttons
    ThisRow = ThisRow + 1
    ButtonBackward = tk.Button(DisplayCensus,text="Jump backward" , font=Times12,command=lambda: MoveList(-1)).grid(column=2,row=ThisRow, sticky="NEWS")
    ButtonForward = tk.Button(DisplayCensus, text="Jump forward", font=Times12,command=lambda: MoveList(1)).grid(column=4,row=ThisRow, sticky="NEWS")



####  Sorting buttons
    ThisRow = ThisRow + 1
    SortByName = tk.Button(DisplayCensus, text="Name",font=Times12,command=lambda: SortList(NAME)).grid(column=2, row=ThisRow, sticky="NEWS")
    SortByRoom = tk.Button(DisplayCensus, text="Room",font=Times12,command=lambda: SortList(ROOM)).grid(column=3, row=ThisRow, sticky="NEWS")
    SortByDOB = tk.Button(DisplayCensus, text="Date of Birth",font=Times12,command=lambda: SortList(DOB)).grid(column=4, row=ThisRow, sticky="NEWS")


    ThisRow= ThisRow + 1
    PatientListBox=MultiListbox(DisplayCensus,['Name', 'Room', 'Date of Birth'])

    for index,patient in enumerate(Patients.ThePatients):
        PatientListBox.add_patient(patient,index)


    PatientListBox.grid(column=2,row=ThisRow, columnspan=4, sticky="NEWS")
    ThisRow = ThisRow + 1

    def AlterData():
        Chosen=PatientListBox.whichChosen()
        if Chosen==-1:
            messagebox.showinfo("Error","Need to select a patient.")
            return
        BuildPatientChangeForm(PatientListBox.whichChosen())
        ChangePatientData.tkraise()

    def SaveCensus():
        Patients.CensusName=CensusNameVar.get()
        SaveCensusFile()

    def NewPatient():#Needs to be tested
        NewPatient=OnePatientClass()
        Patients.ThePatients.append(NewPatient)
        BuildPatientChangeForm(len(Patients.ThePatients)-1)
        ChangePatientData.tkraise()

    def Order():
        Chosen=PatientListBox.whichChosen()
        if Chosen==-1:
            messagebox.showinfo("Error","Need to select a patient.")
            return
        BuildOrderFrame(Chosen)
        AddOrderFrame.tkraise()

    def PrintOrders():
        Patients.PrintAllOrders()

    AlterDataButton = tk.Button(DisplayCensus, text="Alter Patient's Data", font=Times12,width=15,command=AlterData)
    AlterDataButton.grid(row=ThisRow,column=2, sticky="NEWS")

    SaveDataButton = tk.Button(DisplayCensus, text="Save Census", font=Times12,width=15,command=SaveCensus)
    SaveDataButton.grid(row=ThisRow,column=3, sticky="NEWS")

    DeleteDataButton = tk.Button(DisplayCensus, text="Delete Census", font=Times12,width=15,command=DeleteCensus)
    DeleteDataButton.grid(row=ThisRow,column=4, sticky="NEWS")

    ThisRow = ThisRow+ 1
    CensusNameVar = tk.StringVar(DisplayCensus,Patients.CensusName)
    EntryName = tk.Entry(DisplayCensus, textvariable = CensusNameVar).grid(row=ThisRow,column=3, sticky="NEWS")

    OrderButton = tk.Button(DisplayCensus, text="Order", font=Times12, width=15, command=Order)
    OrderButton.grid(row=ThisRow, column=4,sticky="NEWS")

    NewPatientButton  = tk.Button(DisplayCensus, text="Add Patient", font=Times12, width=15, command=NewPatient)
    NewPatientButton.grid(row=ThisRow, column=2,sticky="NEWS")

    ThisRow = ThisRow + 1
    PrintOrdersButton = tk.Button(DisplayCensus, text="Print Orders", font=Times12, width=15, command=PrintOrders)
    PrintOrdersButton.grid(row=ThisRow, column=2,sticky="NEWS")

    if Patients.AreThereOrders():
        PrintOrdersButton["state"] = "normal"
    else:
        PrintOrdersButton["state"]= "disable"

def SaveCensusFile():
    Patients.SaveCensus()



def DeleteCensus():
    Times20 = tkFont.Font(family="Times", size=20)
    LabelTitle = tk.Label(DeleteCensusFrame,text="Are you sure that you want to delete the current census?",font=Times20,height=3)
    LabelTitle.grid(column=0,row=0,sticky="S")
    LabelClarify = tk.Label(DeleteCensusFrame,text="This will delete all data including current orders",font=Times20,height=3)
    LabelClarify.grid(column=0,row=1,sticky="S")
    ButtonDelete = tk.Button(DeleteCensusFrame,text="Delete",font=Times20,width=20,command=ReallyDeleteCensus).grid(column=0,row=2,sticky="W")
    ButtonCancel = tk.Button(DeleteCensusFrame, text="Cancel",font=Times20,width=20, command=CancelDeleteCensus).grid(column=0, row=3, sticky="W")
    DeleteCensusFrame.tkraise()

def CancelDeleteCensus():
    for widget in DeleteCensusFrame.winfo_children():
        widget.destroy()

    DisplayCensus.tkraise()

def ReallyDeleteCensus():
    for widget in DeleteCensusFrame.winfo_children():
        widget.destroy()

    Patients.ClearCensus()

    PatientCensusFrame.tkraise()

def BuildPatientChangeForm(WhichPatient):

    ThisPatient = Patients.ThePatients[WhichPatient]
    ThisRow = 0
    LabelSpacer1 = tk.Label(ChangePatientData, text="", anchor='center', width=10, height=1).grid(row=ThisRow, column=1,columnspan=1)



    ThisRow= ThisRow + 1
    ScreenTitle = tk.Label(ChangePatientData, text="Change Patient's Data", font="Times,24", anchor='center',  height=1).grid(
        row=ThisRow, column=1, columnspan=7)

    ThisRow = ThisRow+ 1
    LabelName = tk.Label(ChangePatientData, text="Name", font="Times,14", anchor='center', width=20, height=1).grid(
        row=ThisRow, column=1, columnspan=1)

    LabelSpacer3 = tk.Label(ChangePatientData,  width=2, height=1).grid(
        row=ThisRow, column=3, columnspan=1)

    LabelDOB = tk.Label(ChangePatientData, text="Date of Birth", font="Times,14", anchor='center', width=20, height=1).grid(
        row=ThisRow, column=4, columnspan=1)

    LabelSpacer4 = tk.Label(ChangePatientData, width=2, height=1).grid(
        row=ThisRow, column=5, columnspan=1)

    LabelRoomNumber = tk.Label(ChangePatientData, text="Room Number", font="Times,14", anchor='center', width=20, height=1).grid(
        row=ThisRow, column=6, columnspan=1)
    ThisRow = ThisRow+ 1

    LabelSpacer5 = tk.Label(ChangePatientData, width=2, height=1).grid(
        row=ThisRow, column=1, columnspan=1)

    ThisRow = ThisRow+ 1
    NameVar = tk.StringVar(ChangePatientData,ThisPatient.Name)
    EntryName = tk.Entry(ChangePatientData, textvariable = NameVar).grid(row=ThisRow,column=1)

    LabelSpacer6 = tk.Label(ChangePatientData,  width=2, height=1).grid(
        row=ThisRow, column=3, columnspan=1)

    DOBVar= tk.StringVar(ChangePatientData,ThisPatient.DOBStr)
    DOBName = tk.Entry(ChangePatientData, textvariable = DOBVar).grid(row=ThisRow,column=4)


    LabelSpacer7 = tk.Label(ChangePatientData, width=2, height=1).grid(
        row=ThisRow, column=5, columnspan=1)

    RoomVar= tk.StringVar(ChangePatientData,ThisPatient.RoomNumber)
    DOBName = tk.Entry(ChangePatientData, textvariable = RoomVar).grid(row=ThisRow,column=6)

    def UpdateData():

        ThisPatient=OnePatientClass()
        ThisPatient.Name=NameVar.get()
        ThisPatient.DOB=DOBVar.get()
        ThisPatient.RoomNumber=RoomVar.get()
        Patients.UpdateData(WhichPatient,ThisPatient)
        Patients.SortPatients(NAME)

  #      ChangePatientData()

        for  widget in ChangePatientData.winfo_children():
            widget.destroy()

        for  widget in DisplayCensus.winfo_children():
            widget.destroy()

        BuildDisplayCensusFrame()
        DisplayCensus.tkraise()

    def Cancel():
        Patients.ThePatients.remove(WhichPatient)
        for  widget in ChangePatientData.winfo_children():
            widget.destroy()

        DisplayCensus.tkraise()

    ThisRow = ThisRow + 1

    UpdateDataButton = tk.Button(ChangePatientData,text="Update Data", command=UpdateData).grid(row=ThisRow,column=3)


def BuildTheBaseFrame():

    ThisRow = 0
    LabelSpacer1 = tk.Label(BaseFrame, text="", font="Times,24", anchor='center', width=10, height=1).grid(row=ThisRow, column=1,columnspan=1)

 #   ThisRow=ThisRow + 1
    LabelTitleBaseFrame = tk.Label(BaseFrame, text="Boom - The Program for Writing Orders", font="Times,24", anchor='center', width=75, height=3).grid(row=ThisRow, column=1, columnspan=5)

    ThisRow = ThisRow + 1
    LabelSpacer2 = tk.Label(BaseFrame, text="", font="Times,24", anchor='center', width=75, height=1).grid(row=ThisRow,
                                                                                                           column=2,
                                                                                                           columnspan=5)

    ThisRow = ThisRow + 1
    LabelCensus = tk.Label(BaseFrame, text="Census", font="Times,12", justify='left', height=1).grid(row=ThisRow,
                                                                                                     column=2,
                                                                                                     sticky='w')

    ThisRow = ThisRow + 1

    ButtonPatientList = tk.Button(BaseFrame, text="Load Patient List", font="Times,12", justify='left', height=1, command = LoadPatientCensus).grid(
        row=ThisRow, column=2, sticky='w')

def BuildPatientCensusFrame():

    entries = os.listdir()
    CSVFiles=[]

    for thisfile in entries:
        tempstr=thisfile.partition(".")
        if tempstr[2]=="csv":
            CSVFiles.append(thisfile)

    whichcensus=tk.StringVar()
    whichcensus.set(CSVFiles[0])
    drop = tk.OptionMenu(PatientCensusFrame, whichcensus, *CSVFiles)
    Times24 = tkFont.Font(family="Times", size=24)
    drop.config(font=Times24)
    drop.pack()
    menu=PatientCensusFrame.nametowidget(drop.menuname)
    menu.config(font=Times24)
    ChooseButton = tk.Button(PatientCensusFrame,text="Load", command=lambda: LoadPatientCensusFile(whichcensus.get()))
    ChooseButton.config(font=Times24)
    ChooseButton.pack()

    temp=1

def LoadPatientCensusFile(FileName):

    global NursingHomeName
    NursingHomeName = FileName.partition('.')[0]
    FileInput = open(FileName,'r')
    AllLines=FileInput.readlines()

    for OneLine in AllLines:
        if OneLine.count(',')==4:
            Patients.AddAPatient(OneLine)

    Patients.SortPatients(2)
    Patients.CensusName=NursingHomeName

    BuildDisplayCensusFrame()
    DisplayCensus.tkraise()

def LoadPatientCensus():
    PatientCensusFrame.tkraise()
    temp=1


#ThePatients = []
Patients = PatientClass()
NursingHomeName= ""


window = tk.Tk()
#window.state('zoomed')
window.geometry('800x500')
window.rowconfigure(0, weight=1)
window.columnconfigure(0, weight=1)

BaseFrame = tk.Frame(window)
PatientCensusFrame = tk.Frame(window)
DisplayCensus = tk.Frame(window)
ChangePatientData = tk.Frame(window)
DeleteCensusFrame = tk.Frame(window)
AddOrderFrame = tk.Frame(window)

for frame in (BaseFrame, PatientCensusFrame, DisplayCensus,ChangePatientData,DeleteCensusFrame,AddOrderFrame):
    frame.grid(row=0, column=0, sticky='nsew')

BuildTheBaseFrame()
BuildPatientCensusFrame()
#
# ==================Frame 2 code
#PatientCensusFrame = tk.Label(PatientCensusFrame, text='Page 2', font='times 35', bg='yellow')
#PatientCensusFrame.pack(fill='both', expand=True)

#frame2_btn = tk.Button(frame2, text='Enter', command=lambda: show_frame(frame3))
#frame2_btn.pack(fill='x', ipady=15)

# ==================Frame 3 code


show_frame(BaseFrame)

window.mainloop()
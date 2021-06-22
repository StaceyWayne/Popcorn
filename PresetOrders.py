import math
from tkinter import messagebox
import tkinter as tk
from tkinter import font as tkfont
from Misc import TextScrollCombo
import pickle

BUILDINGLABTEXT = 0
MAKINGNEWPRESETLAB = 1


class OneOrderClass:
    def __init__(self, the_id, thelabel):

        self.thelabel = the_id
        self.thetext = thelabel

#   One class that will  be used three times for all the preset orders


class PresetOrderClass:
    def __init__(self, thisframe, title):
        self.thisframe = thisframe
        self.title = title
        self.theorders = []
        self.loadorders()
        self.returndestination = thisframe
        self.parententryorders = -1

    def setparententryorders(self,parententyroders):
        self.parententryorders = parententyroders

    def setreturnframe(self, fromframe):
        self.returndestination = fromframe

    def testingprocess(self):

        for index in range(30):
            temp = OneOrderClass("test" + str(index), "lab" + str(index))
            self.theorders.append(temp)

    def loadorders(self):
        orderfilename = self.title + ".swm"
        try:
            orderfile = open(orderfilename, "rb")
            temp = pickle.load(orderfile)
            self.theorders = temp
        except FileNotFoundError:
            pass

#  ########  Frame for presetorders  ############

    #  #####   This will be called on by buildorderFrame and BaseFrame ultimately
    #  ###   When called from BaseFrame we won't be displaying a textbox, just the buttons
    #  ##   All buttons will be disabled
    #        We will have the option to remove labs and add new ones
    #       in addition to adding orders
    def buildframe(self):

        def buttonpressed(thistxt, index):
            nonlocal orderbuttons
            temp = thistxt
#       this means we need to delete
            if orderbuttons[index].cget('bg') == 'red':  

                for oneorder in self.theorders:
                    if oneorder.thetext == thistxt:
                        self.theorders.remove(oneorder)

                for widget in buttonframe2.winfo_children():
                    widget.destroy()

                orderbuttons = []
                buildorderbutton()
            else:
                orderentrytext = big_text_box.gettext()
                orderentrytext = orderentrytext[:len(orderentrytext)-1]
                if orderentrytext.find(thistxt) == -1:
                    big_text_box.appendtext(thistxt)

        def deletesomebutton():

            for thisbutton in orderbuttons:
                thisbutton.configure(bg='red')

        def makeneworderpart1():
            neworderidtext.config(state='normal')
            neworderidlabel.config(state='normal')
            nonlocal the_return_text
            the_return_text = big_text_box.gettext()
            # the_return_text = the_return_text.replace("\n", "")
#       not sure why I need to do this
            big_text_box.cleartext()
            cancelbutton.config(command=cancelmakeneworder)
            neworderbutton.config(command=makeneworderpart2)
            for thisbutton in orderbuttons:
                thisbutton.config(state="disable")

        def makeneworderpart2():

            nonlocal orderbuttons
            temptext = big_text_box.gettext()
            temptext = temptext.replace("\n", "")
            thisneworder = OneOrderClass(idvar.get(), temptext)

            idvar.set("")

            if thisneworder.thelabel == "" or thisneworder.thetext == "":
                error_txt = "We need both a label for the button and text for the lab.\n They may be the same"
                messagebox.showinfo("Error", error_txt)
            else:
                self.theorders.append(thisneworder)
                neworderbutton.config(command=makeneworderpart1)
                cancelbutton.config(command=cancel)
                big_text_box.settext(the_return_text)
                for widget in buttonframe2.winfo_children():
                    widget.destroy()
                orderbuttons = []
                buildorderbutton()

                neworderidtext.config(state='disable')
                neworderidlabel.config(state='disable')

#              not sure if I need to delete all the widgets before leaving
        def cancel():  
            self.returndestination.tkraise()

        def cancelmakeneworder():
            neworderidtext.config(state='disable')
            neworderidlabel.config(state='disable')
            nonlocal the_return_text
            big_text_box.settext(the_return_text)
            cancelbutton.config(command=cancel)

        def statorders():
            if big_text_box.gettext().find("Stat") == -1:
                big_text_box.settext("Stat " + big_text_box.gettext())

        def saveorders():
            orderfilename = self.title + ".swm"
            outputfile = open(orderfilename, "wb")
            pickle.dump(self.theorders, outputfile)
            #          with open(orderfilename, "wb") as mypicklefile:
            #              pickle.dump(self.theorders, mypicklefile)
            outputfile.close()

        def buildorderbutton():  
            # these are for the actual orders
            nonlocal orderbuttons
            nonlocal numberofbuttonframes
            nonlocal orderbuttonframes

            #or thisframe in orderbuttonframes:
            #    thisframe.destroy()
            orderbuttonframes=[]

            numberofbuttonframes = math.ceil(len(self.theorders) / 25)

            if numberofbuttonframes==0:
                return

            if numberofbuttonframes==1:
                nextorderframebuttons.config(state='disable')

            for index in range(numberofbuttonframes):
                orderbuttonframes.append(tk.Frame(buttonframe2, height=20, width=200))
                orderbuttonframes[index].grid(column=1, row=1, sticky='news')

            for index, oneorder in enumerate(self.theorders):

                #onebutton = tk.Button(buttonframe2, text=oneorder.thelabel, image=pixelvirtual, width=80, height=40)
                whichframe = orderbuttonframes[math.floor(index/25)]
                onebutton = tk.Button(whichframe, text=oneorder.thelabel, image=pixelvirtual, width=80, height=40)

                onebutton.config(compound='c')

                if len(oneorder.thelabel) > 8:
                    onebutton.config(font=times9, wraplength=200)
                else:
                    onebutton.config(font=times14, wraplength=100)

                # This syntax for lambda is bizarre
                onebutton.config(command=lambda x=oneorder.thetext, y=index: buttonpressed(x, y))
                orderbuttons.append(onebutton)
                thiscolumn = index % 5
                thisrowlocal = int(2 + (index - thiscolumn) / 5)

                onebutton.grid(row=thisrowlocal, column=thiscolumn)

            orderbuttonframes[0].tkraise()

        def done():
            nonlocal the_return_text
            if not(self.parententryorders == -1):
                the_return_text = big_text_box.gettext()
                # need to make sure this ends up on a new line
                # text widget does something funny with '\n'

                temp_text = self.parententryorders.get(1.0, tk.END)

                if temp_text[len(temp_text)-1] == '\n' and temp_text[len(temp_text)-2]=='\n':
                    temp_text = temp_text[:len(temp_text)-1]

                the_return_text = temp_text + the_return_text
                self.parententryorders.delete('1.0', tk.END)
                self.parententryorders.insert(tk.END, the_return_text)

            big_text_box.cleartext()
            self.returndestination.tkraise()

        def makeoneline():
            temp = big_text_box.gettext()
            temp = temp.replace("\n", ",")
            temp = temp.replace(",,","")
            temp = temp[:len(temp)-1]
            temp = temp + '\n'
            big_text_box.settext(temp)

        def nextorderbuttonframe():
            nonlocal whichorderbuttonframe
            whichorderbuttonframe = whichorderbuttonframe + 1
            if whichorderbuttonframe==numberofbuttonframes:
                whichorderbuttonframe = 0
            orderbuttonframes[whichorderbuttonframe].tkraise()


        #this pixelvirtual needs to be defined outside the function building the buttons
        #otherwise I can't reconfigure the buttons after the facte
        pixelvirtual = tk.PhotoImage(width=1, height=1)

        the_return_text = ""
        times24 = tkfont.Font(family="Times", size=24)

        times14 = tkfont.Font(family="Times", size=14)
        times9 = tkfont.Font(family="Times", size=9)
        thisrow = 1

        labeltitle = tk.Label(self.thisframe, text=self.title, width=45, height=2, font=times24)
        labeltitle.grid(column=1, row=thisrow, stick="NEWS")

        thisrow = thisrow + 1
        neworderlableframe = tk.Frame(self.thisframe, height=20, width=100)
        neworderlableframe.grid(column=1, row=thisrow)
        neworderidlabel = tk.Label(neworderlableframe, text="Label")
        neworderidlabel.grid(column=1, row=1)
        neworderidlabel.config(font=times14)
        neworderidlabel.config(state="disabled")
        idvar = tk.StringVar(neworderlableframe)

        neworderidtext = tk.Entry(neworderlableframe, textvariable=idvar, width=15)

        neworderidtext.grid(column=2, row=1)
        neworderidtext.config(state='disabled')

        thisrow = thisrow + 1
        #    EntryOrders = tk.Text(self.thisframe, width=45, height=1)
        big_text_box = TextScrollCombo(self.thisframe)

        big_text_box.grid(column=1, row=thisrow)
        big_text_box.config(width=600, height=50)

        thisrow = thisrow + 1
        buttonframe1 = tk.Frame(self.thisframe, height=20, width=100)
        #   this will have control buttons
        buttonframe1.grid(column=1, row=thisrow)

        thisrow = thisrow + 1
        numberofbuttonframes = 0
        orderbuttonframes = []
        whichorderbuttonframe = 0

        buttonframe2 = tk.Frame(self.thisframe, height=20, width=200)
        #   this will have all the orders
        buttonframe2.grid(column=1, row=thisrow)

        thisrow = thisrow + 1
        nextorderframebuttons = tk.Button(self.thisframe, text="Next set of orders", command=nextorderbuttonframe)
        nextorderframebuttons.grid(column=1, row=thisrow)

        orderbuttons = []
        buildorderbutton()

        deletebutton = tk.Button(buttonframe1, text="Delete Order", font=times14, command=lambda: deletesomebutton())
        deletebutton.grid(row=1, column=1)
        neworderbutton = tk.Button(buttonframe1, text="New Order", font=times14, command=makeneworderpart1)
        neworderbutton.grid(row=1, column=2)
        cancelbutton = tk.Button(buttonframe1, text="Cancel", font=times14, command=cancel)
        cancelbutton.grid(row=1, column=3)
        savebutton = tk.Button(buttonframe1, text="Save", font=times14, command=saveorders)
        savebutton.grid(row=1, column=4)
        statbutton = tk.Button(buttonframe1, text="Stat", font=times14, command=statorders)
        statbutton.grid(row=1, column=5)
        donebutton = tk.Button(buttonframe1, text="Done", font=times14, command=done)
        donebutton.grid(row=1, column=6)
        makeonelinebutton = tk.Button(buttonframe1, text="Make one line", font=times14, command=makeoneline)
        makeonelinebutton.grid(row=1, column=7)
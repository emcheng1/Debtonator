from tkinter import *
from tkinter.font import Font
from hi import *

'''
TO-DO:
0. Full functionality (done)
1. Add scrolling
2. Data validation for extra spaces at the end
3. Keyboard shortcuts: new row, debtonate (only works if you first click in workspaceframe)
4. Documentation
5. Pretty money with 2 dec places (done)
'''

#-----------------------------KEYBOARD SHORTCUT FUNCTIONS--------------------
def key(event):
    print(repr(event.char))
    # New row: Enter
    if event.char == '\r': 
        gui.addRow()

    # Delete row: Ctrl + x
    elif event.char == '\x18': 
        # delete current row
        pass

    # Debtonate: Ctrl + d
    elif event.char == '\x04':
        gui.debtonate()

def callback(event):
    gui.workspaceframe.focus_set()
    print("clicked at", event.x, event.y)

#-----------------------------ROW MAKER CLASS-----------------------------------

class Row:
    def __init__(self, numrows, gui):
        self.debtor = Entry(gui.entryframe)
        self.debtor.grid(row = 4 + numrows, column = 1)
        self.creditor = Entry(gui.entryframe)
        self.creditor.grid(row = 4 + numrows, column = 4)
        self.amount = Entry(gui.entryframe)
        self.amount.grid(row = 4 + numrows, column = 5)

#--------------------------------MAIN CLASS--------------------------------------

class GUI:
    def __init__(self, master):
        self.master = master
        master.title("Debtonator")
        self.titlefont = Font(family = 'Courier New', size = 31)
        self.headingfont = Font(family='System', size = 16)
        self.copyrightfont = Font(family = 'Courier New', size = 8)
        self.numrows=0
        self.storage=[]
        self.createWidgets()

    def addRow(self):
        self.numrows += 1
        Label(self.entryframe, text="{}".format(self.numrows), bg="dark green", fg="white").grid(row=4+self.numrows, column=0, sticky=N+E+W)
        # curRow = Row(self.numrows, self)
        # curRow.bind("<Return>", callback)
        # self.storage.append(curRow)
        self.storage.append(Row(self.numrows, self))

    #--------------------------SCROLLING-----------------------------------------------------------


    #--------------------------DATA VALIDATE AND ADD TESTCASE--------------------------------------

    def dataIsValid(self):
        datavalid = True
        for row in self.storage:
            # Try/except is for whether the amount is float-convertible.
            try: 
                float(row.amount.get())
                if not (len(row.debtor.get()) and len(row.creditor.get())): 
                    # If the rows are empty, data is invalid
                    datavalid = False
                    break
                if row.debtor.get() == row.creditor.get():
                    # Why would someone want to pay themselves?
                    datavalid = False
                    break
            except:
                datavalid = False
        return datavalid

    def createTestcase(self):
        # parse data and create adj list
        self.nodeset = set() # just for hashing/time complexity purposes
        self.nodelist = [] # list where we keep track of number/node correspondence
        self.testcase = {}
        for row in self.storage:
            # Add everything to nodelist and nodeset
            if row.debtor.get() not in self.nodeset:
                self.nodeset.add(row.debtor.get())
                self.nodelist.append(row.debtor.get())
            if row.creditor.get() not in self.nodeset:
                self.nodeset.add(row.creditor.get())
                self.nodelist.append(row.creditor.get())

        # Initialize self.testcase
        for i in range(len(self.nodelist)):
            self.testcase[i] = set()

        # Populate self.testcase
        for row in self.storage:
            node = self.nodelist.index(row.debtor.get())
            self.testcase[node].add((self.nodelist.index(row.creditor.get()), int(float(row.amount.get())*100)))
        print("testcase: ", self.testcase)

    #----------------------------------PARSE AND DISPLAY RESULTS---------------------------
    def prettyMoney(self, value):
        if value[-2] == '.':
            value += '0'
        return value

    def parseResults(self):
        result = self.debtonatorresult[0]
        initInteractions = self.debtonatorresult[1]
        finalInteractions = self.debtonatorresult[2]
        benchmark  = self.debtonatorresult[3]

        # Display the least of benchmark, final interactions, initial interactions.
        resultstring = ""

        # If final interactions is the least:... etc
        if min(initInteractions, finalInteractions, benchmark) == finalInteractions:
            for index in result:
                if len(result[index]):
                    resultstring += self.nodelist[index] + ' pays '
                    for edge in result[index]:
                        resultstring += self.nodelist[edge[0]] + ' $' + self.prettyMoney(str(edge[1]/100)) + ', '
                    resultstring = resultstring[:-2]
                    resultstring += '.\n'
        elif min(initInteractions, finalInteractions, benchmark) == benchmark: 
            netvalues = self.Debtonator.netValues
            bank = self.nodelist[0]
            for entry in netvalues:
                if entry != 0 and netvalues[entry] <= 0:
                    i += 1
                    resultstring += self.nodelist[entry] + ' pays ' + bank + ' $' + str(-1 * netvalues[entry]) + '.\n'
                elif entry != 0:
                    i += 1
                    resultstring += bank + ' pays ' + self.nodelist[entry] + ' $' + str(netvalues[entry]) + '.\n' 
        elif min(initInteractions, finalInteractions, benchmark) == initInteractions:
            resultstring += "The debt network cannot be reduced.\n"

        # Delete any old results
        try:
            self.resultstring1.grid_forget()
        except:
            pass

        self.resultstring1 = Label(self.resultsframe, text=resultstring, bg="linen")
        self.resultstring1.grid(row=2, column=0, sticky=N)

        # Display the edge reduction stats.
        resultstring2 = ''
        if self.Debtonator.initialInteractions != self.Debtonator.numInteractions:
            resultstring2 += 'Number of transactions reduced from {} to {}.'.format(self.Debtonator.initialInteractions, 
                self.Debtonator.numInteractions)
            print(resultstring2)
        else:
            resultstring2 += 'Number of transactions did not change from {}.'.format(self.Debtonator.initialInteractions)

        # Delete any old result strings
        try:
            self.resultstring2.grid_forget()
        except:
            pass

        self.resultstring2 = Label(self.resultsframe, text=resultstring2, bg="linen")
        self.resultstring2.grid(row=3, column=0, sticky=N+W)

        # Upper/Lower bound comparisons
        # self.resultstring3 = ''
        # self.resultstring3 += 'Compare to a strict lower bound of {} transaction(s) and a guaranteed upper bound of {} transaction(s).'.format(
        #   max(len(self.Debtonator.netPosNodes), len(self.Debtonator.netNegNodes)), self.Debtonator.numPeople - 1)
        # Label(self.resultsframe, text=self.resultstring3, bg="white").grid(row=3 + i, column=0, sticky=N+W)


    def displayResults(self):
        # create results frame below workspace frame
        self.resultsframe = Frame(self.master, bg="linen")
        self.resultsframe.grid(row = 3, column = 0, columnspan = 8, sticky=N+W)

        Label(self.resultsframe, text="    ", bg="linen").grid(row=0, column=0, columnspan=8)

        self.resultstitle = Label(self.resultsframe, text="Results", font=self.headingfont, fg="black", bg="linen")
        self.resultstitle.grid(row=1, column=0, sticky=N+W)

        self.parseResults()

    #--------------------------------------MAIN DEBTONATE FUNCTION--------------------------------------

    def debtonate(self):
        if self.dataIsValid():
            print("Data is valid.")
            # Remove error message, if any
            try:
                self.errormsg.grid_forget()
            except:
                pass

            # create adjacency list
            self.createTestcase()

            # debtonate the testcase
            self.Debtonator = debtonator(self.testcase)
            self.debtonatorresult = self.Debtonator.guimain()

            # display the results
            self.displayResults()
        else:
            # display error message
            self.errormsg = Message(self.buttonframe, text="Error: one or more invalid data fields.", fg="black", bg="linen")
            self.errormsg.grid(row=2, column=8, columnspan=2, sticky=N+E+W)

    #----------------------------------------CREATE BASE GUI-------------------------------

    def createWidgets(self):
        # Title frame: title text, caption text
        self.titleframe = Frame(self.master, bg="dark green")
        self.titleframe.grid(row = 0, column = 0, columnspan=8, sticky=N+E+W)

        self.title = Label(self.titleframe, text="DESKTOP DEBTONATOR", font=self.titlefont, fg="linen", bg="dark green")
        self.title.grid(row = 0, column=0)

        self.info = Label(self.titleframe, text="A tool to simplify group debts.", fg="linen", bg="dark green")
        self.info.grid(row = 1, column=0, sticky=N+E+W)

        # Workspace frame: workspace title, workspace instructions
        self.workspaceframe = Frame(self.master, bg="linen")
        self.workspaceframe.grid(row = 1, columnspan=8, sticky = N+E+W)

        self.workspacetitle = Label(self.workspaceframe, text="Workspace", font=self.headingfont, bg="linen", fg="black")
        self.workspacetitle.grid(row = 0, column = 0, columnspan=2, sticky = N+W)

        self.workspaceinfo = Label(self.workspaceframe, text="Please enter your information below without currency symbols.", bg="linen")
        self.workspaceinfo.grid(row=1, column=0, columnspan = 8, sticky = N+W)

        # In Workspace frame: column headers
        self.label1 = Label(self.workspaceframe, text="Debtor", bg="linen")
        self.label1.grid(row=2, column = 1, columnspan=2, sticky = W)

        self.label3 = Label(self.workspaceframe, text= "Creditor", bg="linen")
        self.label3.grid(row=2, column=3)

        self.label4 = Label(self.workspaceframe, text= "Amount", bg="linen")
        self.label4.grid(row=2, column=5, stick = W)

        # Entry frame
        self.entryframe = Frame(self.workspaceframe, bg="dark green")
        self.entryframe.grid(row=3, column=0, columnspan=6, sticky=W)

        self.addRow()

        # Keyboard shortcut for new row
        self.workspaceframe.bind("<Button-1>", callback)
        self.workspaceframe.bind("<Key>", key)

        # Button frame
        self.buttonframe = Frame(self.workspaceframe, bg = "linen")
        self.buttonframe.grid(row=3, column=6, rowspan=10,columnspan=2, sticky=N)
        Button(self.buttonframe, text="New Row", command=self.addRow, bg="dark green", fg="linen").grid(row=0, column=8, columnspan=2, sticky=N+E+W)
        Button(self.buttonframe, text="Debtonate", command = self.debtonate, bg="dark green", fg="linen").grid(row=1, column=8, columnspan=2, sticky=N+E+W)

        # Copyright frame
        self.copyrightframe = Frame(self.master)
        self.copyrightframe.grid(row = 4, column = 0, columnspan = 8, sticky=S)
        sym = u"\u00A9"
        self.copyright = Label(self.copyrightframe, text="Copyright 2017{} Emily Cheng".format(sym), font = self.copyrightfont,
            fg="black", bg="linen")
        self.copyright.grid(row = 0, column=0, sticky = N+E+W)
 

root = Tk()
root.iconbitmap('favicon.ico')

Grid.rowconfigure(root, 1, weight=1)
Grid.columnconfigure(root, 0, weight=1)
root.configure(background="linen")

gui = GUI(root)
gui.workspaceframe.focus_set()

root.mainloop()
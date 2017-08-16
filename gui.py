from tkinter import *
import tkinter.font as tkFont
import tkinter.ttk as ttk


class MultiColumnListbox(object):

    def __init__(self, frame, header, initial_state):
        self.tree = None
        self._setup_widgets(frame, header)
        self._build_tree(header, initial_state)

    def _setup_widgets(self, frame, header):

#        container = ttk.Frame()
#        container.pack(fill='both', expand=True)

        self.tree = ttk.Treeview(columns=header, show="headings")               #Create tree
        vsb = ttk.Scrollbar(orient="vertical", command=self.tree.yview)         #Create VSB
        hsb = ttk.Scrollbar(orient="horizontal", command=self.tree.xview)       #Create HSB
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)     #Configure tree
        self.tree.grid(column=0, row=0, sticky='nsew', in_=frame)           #Pack
        vsb.grid(column=1, row=0, sticky='ns', in_=frame)                   #Pack
        hsb.grid(column=0, row=1, sticky='ew', in_=frame)                   #Pack
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

    def _build_tree(self, header, state):
        for col in header:
            self.tree.heading(col, text=col.title())                            #must set command for sort
            self.tree.column(col, width=tkFont.Font().measure(col.title()))

        for item in state:
            self.insert(item, header)

    def insert(self, item, header):
        self.tree.insert('', 'end', values=item)
        for ix, val in enumerate(item):
            col_w = tkFont.Font().measure(val)
            if self.tree.column(header[ix],width=None)<col_w:
                self.tree.column(header[ix], width=col_w)


def plot_demand():
    print('demand')
    return

def plot_usage():
    print('usage')
    return



#GUI-------------------------------------------------------------------------------------------
root = Tk()
root.title('Notebook Demo')
root.geometry('500x500')


#NB--------------------------------------------------------------------------------------------
nb = ttk.Notebook(root)
nb.pack(fill='both', expand='yes')

p1 = ttk.Frame(nb)
p2 = ttk.Frame(nb)
p3 = ttk.Frame(nb)
p4 = ttk.Frame(nb)
p5 = ttk.Frame(nb)

nb.add(p1, text='Home')
nb.add(p2, text='Purchase Log')
nb.add(p3, text='Usage Log')
nb.add(p4, text ='Seller info')
nb.add(p5, text = 'Analysis')

#HOME--------------------------------------------------------------------------------------------

e1 = Entry(p1)
e2 = Entry(p1)
e3 = Entry(p1)
e4 = Entry(p1)
l1 = Label(p1, text = 'Annual Demand')
l2 = Label(p1, text = 'Safety Stock')
l3 = Label(p1, text = 'Holding Cost')
l4 = Label(p1, text = '')
l5 = Label(p1, text = '')
l1.grid(row = 0)
l2.grid(row = 1)
l3.grid(row = 2)
e1.grid(row = 0, column = 1)
e2.grid(row = 1, column = 1)
e3.grid(row = 2, column = 1)


#c = Checkbutton(topFrame, text = "really?")
#c.grid(columnspan = 2)

#b = Button(topFrame, text = "done", command = func1)
b1 = Button(p1, text = "Save")
b2 = Button(p1, text = "Analyze")

b1.grid(row = 3)
b2.grid(row = 3, column = 1, padx = 2)
#b.bind("<Button-1>", func1)
#b.grid(columnspan = 2)


#PURCHASE--------------------------------------------------------------------------------------------

purchase_head = ['ID', 'NAME', 'OC', 'UC']

purchase_tf = ttk.Frame(p2)
purchase_bf = ttk.Frame(p2)

purchase_tf.pack(fill='both', expand=True)
purchase_bf.pack(side = BOTTOM)

#TF
purchase_lb = MultiColumnListbox(purchase_tf, purchase_head, [tuple(purchase_head)])


#BF
pe1 = Entry(purchase_bf)
pe2 = Entry(purchase_bf)
pe3 = Entry(purchase_bf)
pe4 = Entry(purchase_bf)
pl1 = Label(purchase_bf, text = 'Annual Demand')
pl2 = Label(purchase_bf, text = 'Safety Stock')
pl3 = Label(purchase_bf, text = 'Holding Cost')
pl4 = Label(purchase_bf, text = '')
pl5 = Label(purchase_bf, text = '')
pe1.grid(row = 0)
pe2.grid(row = 0, column = 1)
pe3.grid(row = 0, column = 2)


#USAGE--------------------------------------------------------------------------------------------

usage_head = ['ID', 'NAME', 'OC', 'UC']

usage_tf = ttk.Frame(p3)
usage_bf = ttk.Frame(p3)

usage_tf.pack(fill='both', expand=True)
usage_bf.pack(side = BOTTOM)

#TF
usage_lb = MultiColumnListbox(usage_tf, usage_head, [tuple(usage_head)])


#BF
ue1 = Entry(usage_bf)
ue2 = Entry(usage_bf)
ue3 = Entry(usage_bf)
ue4 = Entry(usage_bf)
ul1 = Label(usage_bf, text = 'Annual Demand')
ul2 = Label(usage_bf, text = 'Safety Stock')
ul3 = Label(usage_bf, text = 'Holding Cost')
ul4 = Label(usage_bf, text = '')
ul5 = Label(usage_bf, text = '')
ue1.grid(row = 0)
ue2.grid(row = 0, column = 1)
ue3.grid(row = 0, column = 2)


#SELLER--------------------------------------------------------------------------------------------

seller_head = ['ID', 'NAME', 'OC', 'UC']

seller_tf = ttk.Frame(p4)
seller_bf = ttk.Frame(p4)

seller_tf.pack(fill='both', expand=True)
seller_bf.pack(side = BOTTOM)

#TF
seller_lb = MultiColumnListbox(seller_tf, seller_head, [tuple(seller_head)])

#BF
se1 = Entry(seller_bf)
se2 = Entry(seller_bf)
se3 = Entry(seller_bf)
se4 = Entry(seller_bf)
sl1 = Label(seller_bf, text = 'Annual Demand')
sl2 = Label(seller_bf, text = 'Safety Stock')
sl3 = Label(seller_bf, text = 'Holding Cost')
sl4 = Label(seller_bf, text = '')
sl5 = Label(seller_bf, text = '')
se1.grid(row = 0)
se2.grid(row = 0, column = 1)
se3.grid(row = 0, column = 2)


#ANALYSIS--------------------------------------------------------------------------------------------

analysis_head = ['ID', 'NAME', 'OC', 'UC']

analysis_tf = ttk.Frame(p5)
analysis_bf = ttk.Frame(p5)

analysis_tf.pack(fill='both', expand=True)
analysis_bf.pack(side = BOTTOM)

#TF
analysis_lb = MultiColumnListbox(analysis_tf, analysis_head, [tuple(analysis_head)])


#BF
ae1 = Entry(analysis_bf)
ae2 = Entry(analysis_bf)
ae3 = Entry(analysis_bf)
ae4 = Entry(analysis_bf)
al1 = Label(analysis_bf, text = 'Annual Demand')
al2 = Label(analysis_bf, text = 'Safety Stock')
al3 = Label(analysis_bf, text = 'Holding Cost')
al4 = Label(analysis_bf, text = '')
al5 = Label(analysis_bf, text = '')
ae1.grid(row = 0)
ae2.grid(row = 0, column = 1)
ae3.grid(row = 0, column = 2)
ab1 = Button(analysis_bf, text = 'filter')
ab1.grid(row = 0,column = 3)

ab2 = Button(analysis_bf, text = 'demand analysis', command = plot_demand)
ab2.grid(row = 1)

ab3 = Button(analysis_bf, text = 'usage analysis', command = plot_usage)
ab3.grid(row = 1, column = 1)







root.mainloop()

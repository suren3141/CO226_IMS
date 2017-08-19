from tkinter import *
import tkinter.font as tkFont
import tkinter.ttk as ttk
import pymysql as MySQLdb
import numpy as np
from matplot import Plotter

#MAIN FUNCTIONS------------------------------------------------------------------------------------------------
def EOQ(d, h, o):
    return np.sqrt(2*o*d/h)

def ROL(lead , SS, rate):
    return lead*rate + SS

def cost(up, discount, holding_cost, order_cost, quantity, demand):
    up*(1-discount) + order_cost / demand + (holding_cost*quantity) / (2 * demand)

#SQL FUNCTIONS------------------------------------------------------------------------------------------------
def on_bu_insert(ue_day, ue_quantity):
    try:
        u_day = int(ue_day.get())
        u_quantity = int(ue_quantity.get())
        #print(u_day)
        #print(type(u_quantity))
        usage_lb.insert((u_day, u_quantity))
    except:
        on_error('Enter valid values')


def on_bu_update():
    cur_item = usage_lb.tree.focus()
    u_day, u_quantity = usage_lb.tree.item(cur_item)['values']
    ue_day.insert(0, str(u_day))
    ue_quantity.insert(0, str(u_quantity))
    usage_lb.tree.delete(cur_item)

def on_bu_select():
    cur_item = usage_lb.tree.focus()
    #print (cur_item)
    #print (usage_lb.tree.item(cur_item)['values'])

def on_bu_delete():
    cur_item = usage_lb.tree.focus()
    usage_lb.tree.delete(cur_item)

#GUI FUNCTIONS-----------------------------------------------------------------------------------------
def on_save():
    demand = e_demand.get()
    safety_stock = e_ss.get()
    holding_cost = e_hc.get()

def on_analyze():
    on_save()
    nb.select(p5)

def plot_demand(usage_head, root):
    x_name = usage_head[0]
    y_name = usage_head[1]
    x, y = get_tree_val(usage_lb.tree, x_name, y_name)
    print('demand')
    on_plot(root, x, y)
    return

def plot_usage():

    print('usage')
    return


def get_tree_val(tv, x_name, y_name):
    children = tv.get_children()
    x = [int(tv.set(child,x_name)) for child in children]
    y = [int(tv.set(child,y_name)) for child in children]
#    print(x, y)
    return x, y

def on_plot(root, x, y):
    W = Plotter(root, x, y)



#GUI-------------------------------------------------------------------------------------------------------

class MultiColumnListbox(object):

    def __init__(self, frame, header, initial_state):
        self.tree = None
        self._setup_widgets(frame, header)
        self._build_tree(header, initial_state)

    def _setup_widgets(self, frame, header):

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
            self.tree.heading(col, text=col.title(),command=lambda c=col: self.sort_col(self.tree, c, 0))
            self.tree.column(col, width=tkFont.Font().measure(col.title()))

        for item in state:
            self.insert(item)

    def insert(self, item):
        self.tree.insert('', 0, values=item)
        '''for ix, val in enumerate(item):
            col_w = tkFont.Font().measure(val)
            if self.tree.column(header[ix],width=None)<col_w:
                self.tree.column(header[ix], width=col_w)'''

    def sort_col(self, tree, col, descending):
#        print(col)
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        #print(data)
        if data[0][0].isdigit():
            data = [(int(i), j) for i, j in data]
        data.sort(reverse=descending)
        for ix, item in enumerate(data):
            tree.move(item[1], '', ix)
        tree.heading(col, command=lambda col=col: self.sort_col(tree, col, int(not descending)))


def on_error(message):
    e = Toplevel(root)
    l = Label(e, text = message).pack()
    b = Button(e, text = "OK", command = e.destroy)
    b.pack(side = BOTTOM, padx = 2, pady = 2)

#VARIABLES-------------------------------------------------------------------------------------
demand = 40000
holding_cost = 30
safety_stock = 400
max_lead_time = -1
max_eff_unit_price = -1


#SQL------------------------------------------------------------------------------------------
db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="root",         # your username
                                          # your password
                     db="co226")    # name of the data base

cur = db.cursor()

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

e_demand = Entry(p1)
e_ss = Entry(p1)
e_hc = Entry(p1)
e4 = Entry(p1)
l1 = Label(p1, text = 'Annual Demand')
l2 = Label(p1, text = 'Safety Stock')
l3 = Label(p1, text = 'Holding Cost')
l4 = Label(p1, text = '')
l5 = Label(p1, text = '')
l1.grid(row = 0)
l2.grid(row = 1)
l3.grid(row = 2)
e_demand.grid(row = 0, column = 1)
e_ss.grid(row = 1, column = 1)
e_hc.grid(row = 2, column = 1)


b_save = Button(p1, text = "Save", command = on_save)
b_analyze = Button(p1, text = "Analyze", command = on_analyze)

b_save.grid(row = 3)
b_analyze.grid(row = 3, column = 1, padx = 2)


#PURCHASE--------------------------------------------------------------------------------------------

purchase_head = ['Date', 'Quantity']

purchase_tf = ttk.Frame(p2)
purchase_bf = ttk.Frame(p2)

purchase_tf.pack(fill='both', expand=True)
purchase_bf.pack(side = BOTTOM)

#TF
purchase_lb = MultiColumnListbox(purchase_tf, purchase_head, [])


#BF
pe_day = Entry(purchase_bf)
pe_quantity = Entry(purchase_bf)
pe3 = Entry(purchase_bf)
pe4 = Entry(purchase_bf)
pl1 = Label(purchase_bf, text = 'Annual Demand')
pl2 = Label(purchase_bf, text = 'Safety Stock')
pl3 = Label(purchase_bf, text = 'Holding Cost')
pl4 = Label(purchase_bf, text = '')
pl5 = Label(purchase_bf, text = '')
pe_day.grid(row = 0)
pe_quantity.grid(row = 0, column = 1)
pe3.grid(row = 0, column = 2)


#USAGE--------------------------------------------------------------------------------------------

usage_head = ["DAY", "QUANTITY"]

usage_tf = ttk.Frame(p3)
usage_bf = ttk.Frame(p3)

usage_tf.pack(fill='both', expand=True)
usage_bf.pack(side = BOTTOM)

#TF
cur.execute("select * from demand")
purchase_val = cur.fetchall()

usage_lb = MultiColumnListbox(usage_tf, usage_head, purchase_val)


#BF
ue_day = Entry(usage_bf)
ue_day.pack()
ue_quantity = Entry(usage_bf)
ue_quantity.pack()
ue3 = Entry(usage_bf)
ue4 = Entry(usage_bf)
ul1 = Label(usage_bf, text = 'Annual Demand')
ul2 = Label(usage_bf, text = 'Safety Stock')
ul3 = Label(usage_bf, text = 'Holding Cost')
ul4 = Label(usage_bf, text = '')
ul5 = Label(usage_bf, text = '')

bu_insert = Button(usage_bf, text = "INSERT", command = lambda : on_bu_insert(ue_day, ue_quantity))
bu_insert.pack()


bu_update = Button(usage_bf, text = "EDIT", command = on_bu_update)
bu_update.pack()

bu_delete = Button(usage_bf, text = "DELETE", command = on_bu_delete)
bu_delete.pack()

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
ae4 = Entry(analysis_bf)
al1 = Label(analysis_bf, text = 'Annual Demand')
al2 = Label(analysis_bf, text = 'Safety Stock')
al3 = Label(analysis_bf, text = 'Holding Cost')
al4 = Label(analysis_bf, text = '')
al5 = Label(analysis_bf, text = '')

ae1 = Entry(analysis_bf)
ae2 = Entry(analysis_bf)
ae3 = Entry(analysis_bf)
ae1.grid(row = 0)
ae2.grid(row = 0, column = 1)
ae3.grid(row = 0, column = 2)

ab1 = Button(analysis_bf, text = 'filter')
ab1.grid(row = 0,column = 3)

ab2 = Button(analysis_bf, text = 'demand analysis', command = lambda : plot_demand(usage_head, root))
ab2.grid(row = 1)

ab3 = Button(analysis_bf, text = 'usage analysis', command = plot_usage)
ab3.grid(row = 1, column = 1)

root.mainloop()

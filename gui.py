from tkinter import *
import tkinter.font as tkFont
import tkinter.ttk as ttk
import pymysql as MySQLdb
import math
from matplot import Plotter


#VARIABLES-------------------------------------------------------------------------------------
demand = 400000
holding_cost = 30
safety_stock = 400
max_lead_time = -1
max_eff_unit_price = -1
rate = 0
seller_analysis = []
stock_val = []
stock_analysis = []
lt_choice = 0
q_choice = 0
d_choice = 0


#MAIN FUNCTIONS------------------------------------------------------------------------------------------------
def EOQ(d, h, o):
    return math.sqrt(2*o*d/h)

def ROL(lead , SS, rate):
    return lead*rate + SS

def ROD(x1, y1, rol, rate):
    return x1 + (y1-rol)/rate

def cost(up, discount, holding_cost, order_cost, quantity, demand):
    return up*(1-discount)*demand + demand*order_cost / quantity + (holding_cost*quantity) / (2)

def u_rate(d):
    x_name = usage_head[0]
    y_name = usage_head[1]
    x, y = get_tree_val(usage_lb.tree, x_name, y_name)
    days = max(x)
    usage = [0] * (days+1)
    for i in range(len(x)):
        usage[x[i]] += y[i]

    global rate
    rate = sum(usage[-d:])/d


def find_demand(days):
    x, y = get_tree_val(usage_lb.tree, usage_head[0], usage_head[1])
    l = max(len(y), days)
    e_demand.delete(0, END)
    e_demand.insert(0, str(math.ceil(365*(sum(y[-l:])/l))))

def line_fit(x, x1, y1, m):
    return -m*(x-x1) + y1

def analyze_seller():
    cur.execute("SELECT * FROM SELLER")
    seller_data = cur.fetchall()

    cur.execute("SELECT * FROM OFFER")
    offer_data = cur.fetchall()

    n = max(seller_data, key=lambda x:x[0])[0]+1

    eoq_seller= [0]*n
    d_seller = [0]*n
    seller = [0]*n

    for row in seller_data:
        eoq_seller[row[0]] = round(EOQ(demand, holding_cost, row[1]))
        seller[row[0]] = row[1:]

    for row in offer_data:
        ind, q, d = row
        if q < eoq_seller[ind]:
            d_seller[ind] = max(d, d_seller[ind])
        else:
            tc = cost(seller[ind][1], d, holding_cost, seller[ind][0], q, demand)
            seller_analysis.append((ind, seller[ind][0], seller[ind][1], seller[ind][2], q, d, int(tc), "{0:.2f}".format(tc/demand)))

    for i in range(n):
        if eoq_seller[i]:
            oc, up, lt = seller[i]
            tc = cost(up, d_seller[i], holding_cost, oc, eoq_seller[i], demand)
            seller_analysis.append((i, oc, up, lt, eoq_seller[i], d_seller[i], int(tc), "{0:.2f}".format(tc/demand)))

    '''for i in range(len(seller_data)):
        ind, oc, up, lt, q, d = seller_data[i]
        if q < eoq_seller[ind]:
            d_seller[ind] = max(d, d_seller[ind])
            seller[ind] = (oc, up, lt)
        else:
            uc = cost(up, d, holding_cost, oc, q, demand)
            seller_analysis.append((ind, oc, up, lt, q, d, uc))

    print(eoq_seller)
    print(d_seller)
    print(seller)'''

    return seller_analysis


def analyze_stock(usage_head):
    x_name = usage_head[0]
    y_name = usage_head[1]
    x1, y1 = get_tree_val(usage_lb.tree, x_name, y_name)
    x2, y2 = get_tree_val(purchase_lb.tree, x_name, y_name)
    l = max(max(x1), max(x2))
    x = range(1,l+1)
    y = [0]*(l+1)
    global stock_val
    stock_val = [0] * (l+1)
    for i in range(len(x2)):
        stock_val[x2[i]] += y2[i]
    for i in range(len(x1)):
        stock_val[x1[i]] -= y1[i]
    #print(stock_val)
    for i in range(1, l+1):
        stock_val[i] += (stock_val[i] + stock_val[i-1])

    global stock_analysis
    stock_analysis = [(i, stock_val[i]) for i in range(l+1)]
    return stock_val

#SQL FUNCTIONS------------------------------------------------------------------------------------------------

def on_b_insert(entries, mlb, flag):
    val = []
    rep = 0
    if flag == 1:
        try:
            for i in range(len(entries)):
                val.append(int(entries[i].get()))
            mlb.insert(tuple(val))
        except:
            on_error('Enter valid values')
            rep = -1

    elif flag == 2:
        rep = on_seller_insert(entries)
    elif flag == 3:
        rep = on_offer_insert(entries)
    return rep


def on_b_update(mlb, labels, flag):
    cur_item = mlb.tree.focus()
    if cur_item == '':
        on_error('Select an entry')
    else:
        val = mlb.tree.item(cur_item)['values']
        win = Update(mlb, labels, root, cur_item, val, flag)

def on_b_delete(mlb):
    cur_item = mlb.tree.focus()
    if cur_item == '':
        on_error('Select an entry')
    else:
        mlb.tree.delete(cur_item)


#def b_select(mlb):
#    return mlb.tree.focus()


def on_seller_insert(entries):
    try:
        v1 = int(entries[0].get())
        v2 = int(entries[1].get())
        v3 = float(entries[2].get())
        v4 = int(entries[3].get())
        seller_lb.insert((v1, v2, v3, v4))
    except:
        on_error('Enter valid values')
        return -1
    return 0


def on_offer_insert(entries):
    try:
        v1 = int(entries[0].get())
        v2 = int(entries[1].get())
        v3 = float(entries[2].get())
        offer_lb.insert((v1, v2, v3))
    except:
        on_error('Enter valid values')
        return -1
    return 0



#GUI FUNCTIONS-----------------------------------------------------------------------------------------
def on_save():
    d = e_demand.get().strip()
    ss = e_ss.get().strip()
    hc = e_hc.get().strip()
    try:
        global demand
        demand= int(d)
    except:
        pass
    try:
        global safety_stock
        safety_stock= int(ss)
    except:
        pass
    try:
        global holding_cost
        holding_cost= int(hc)
    except:
        pass
    analyze_seller()


def on_analyze():
    on_save()
    #print(demand, safety_stock, holding_cost)
    nb.select(p5)

def plot_demand(usage_head, root):
    x_name = usage_head[0]
    y_name = usage_head[1]
    x, y = get_tree_val(usage_lb.tree, x_name, y_name)
    days = max(x)
    usage = [0] * (days+1)
    for i in range(len(x)):
        usage[x[i]] += y[i]
    on_plot(root, range(days), usage[1:], 'plot')

def plot_stock(root):
    x1 = len(stock_val)

    y1 = stock_val[-1]

    xx = range(x1, x1 + math.ceil(y1/rate))
    yy = [line_fit(i, x1, y1, rate) for i in xx]

    #print(xx)
    #print(yy)

    rol = ROL(10, safety_stock, rate)

    rod = ROD(x1, y1, rol, rate)

    y3 = range(math.floor(rol))
    x3 = [rod]*len(y3)

    W = Plotter(root, range(1,x1), stock_val[1:], 'step')
    W.a.plot(range(x1), [safety_stock]*x1, 'y--')
    W.a.plot(x3, y3, 'g--')
    W.a.plot(xx, yy, 'r--')


def get_tree_val(tv, x_name, y_name):
    children = tv.get_children()
    data = [(int(tv.set(child,x_name)), int(tv.set(child,y_name))) for child in children]
    data = sorted(data, key = lambda x:x[0])
    x = [a[0] for a in data]
    y = [a[1] for a in data]
    return x, y

def on_plot(root, x, y, type):
    W = Plotter(root, x, y, type)

def on_filter():
    return



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

'''
class Message:
    def __init__(text):
'''

class Update(object):

    def __init__(self, mlb, labels, root, cur_item, val, ind):
        self.win = Toplevel(root)
        self.setup_win(mlb, labels, cur_item, val, ind)

    def setup_win(self, mlb, lab, cur_item, val, ind):
        #print(val)
        l = len(lab)

        tf = Frame(self.win)
        bf = Frame(self.win)
        tf.pack()
        bf.pack(side = BOTTOM)

        entries = []
        labels = []

        #TF
        for i in range(l):
            entries.append(Entry(self.win))
            labels.append(Label(self.win, text = lab[i]))
            labels[i].pack(side = LEFT)
            entries[i].pack()
            #labels[i].grid(row = 0, column = i)
            #entries[i].grid(row = 1, column = i)
            entries[i].insert(0, str(val[i]))
            #tf.columnconfigure(i, weight = 1)
        #tf.rowconfigure(0, weight = 1)
        #tf.rowconfigure(1, weight = 1)

        #BF
        b_ok = Button(bf, text = "OK", command = lambda : self.on_ok(entries, mlb, cur_item, ind))
        b_ok.pack()

        b_cancel = Button(bf, text = "CANCEL", command = self.on_cancel)
        b_cancel.pack()

    def on_cancel(self):
        self.win.destroy()

    def on_ok(self, entries, mlb, cur_item, ind):
        reply = on_b_insert(entries, mlb, ind)
        if reply == 0:
            mlb.tree.delete(cur_item)
            self.win.destroy()


#SQL------------------------------------------------------------------------------------------
db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="root",         # your username
                                          # your password
                     db="co226")    # name of the data base

cur = db.cursor()

#GUI-------------------------------------------------------------------------------------------
root = Tk()
root.title('IMS')
root.geometry('800x500')


#NB--------------------------------------------------------------------------------------------
nb = ttk.Notebook(root)
nb.pack(fill='both', expand='yes')

p1 = ttk.Frame(nb)
p2 = ttk.Frame(nb)
p3 = ttk.Frame(nb)
p4 = ttk.Frame(nb)
p5 = ttk.Frame(nb)
p6 = ttk.Frame(nb)

nb.add(p1, text='Home')
nb.add(p2, text='Purchase Log')
nb.add(p3, text='Usage Log')
nb.add(p4, text ='Seller info')
nb.add(p5, text = 'Seller analysis')
nb.add(p6, text = 'Stock analysis')

#HOME--------------------------------------------------------------------------------------------

h_l = ['Annual Demand', 'Units', 'Safety Stock', 'Holding Cost']
e_demand = Entry(p1)
e_ss = Entry(p1)
e_hc = Entry(p1)
h_l = [Label(p1, text = x) for x in h_l]

h_l[0].grid(row = 1, column = 2)
h_l[1].grid(row = 1, column = 5, sticky = W)
h_l[2].grid(row = 2, column = 2)
h_l[3].grid(row = 3, column = 2)
e_demand.grid(row = 1, column = 4)
e_ss.grid(row = 2, column = 4)
e_hc.grid(row = 3, column = 4)

b_save = Button(p1, text = "Save", command = on_save)
b_analyze = Button(p1, text = "Analyze", command = on_analyze)
b_find_demand = Button(p1, text = "Find Demand", command = lambda : find_demand(365))

b_save.grid(row = 4, column = 2)
b_analyze.grid(row = 4, column = 4, padx = 2)
b_find_demand.grid(row = 1, column = 6)

for i in range(20):
    p1.rowconfigure(i, weight = 1)
for j in range(10):
    p1.columnconfigure(j, weight = 1)

#PURCHASE--------------------------------------------------------------------------------------------

purchase_head = ['Day', 'Quantity']

purchase_lf = ttk.Frame(p2)
purchase_rf = ttk.Frame(p2)

purchase_lf.grid(row = 0, column = 0, sticky = 'nesw')#purchase_lf.pack(fill='both', expand=True)
purchase_rf.grid(row = 0, column = 1, sticky = 'nesw')#purchase_rf.pack(side = RIGHT)

p2.rowconfigure(0, weight = 1)
p2.columnconfigure(0, weight = 8)
p2.columnconfigure(1, weight = 1)

#LF
cur.execute("select * from purchase")
purchase_val = cur.fetchall()

purchase_lb = MultiColumnListbox(purchase_lf, purchase_head, purchase_val)


#RF
p_l = ['Day', 'Quantity', 'Units']
p_l = [Label(purchase_rf, text = x) for x in p_l]

pe_day = Entry(purchase_rf)
pe_quantity = Entry(purchase_rf)

bp_insert = Button(purchase_rf, text = "INSERT", command = lambda : on_b_insert([pe_day, pe_quantity], purchase_lb, 1))
ttk.Separator(purchase_rf,orient=HORIZONTAL).grid(row=6, columnspan = 4,sticky = 'ew')
bp_update = Button(purchase_rf, text = "EDIT", command = lambda: on_b_update(purchase_lb, usage_head, 1))
bp_delete = Button(purchase_rf, text = "DELETE", command = lambda : on_b_delete(purchase_lb))

p_l[0].grid(row = 1, column = 1)
pe_day.grid(row = 1, column = 2, columnspan = 2)
p_l[1].grid(row = 3, column = 1)
pe_quantity.grid(row = 3, column = 2, columnspan = 2)
p_l[2].grid(row = 3, column =4, sticky = 'w')
bp_insert.grid(row = 5, column = 2)
bp_update.grid(row = 7, column = 2)
bp_delete.grid(row = 8, column = 2)

for i in range(30):
    purchase_rf.rowconfigure(i, weight = 1)
for i in range(4):
    purchase_rf.columnconfigure(i, weight = 1)


#USAGE--------------------------------------------------------------------------------------------

usage_head = ['Day', 'Quantity']

usage_lf = ttk.Frame(p3)
usage_rf = ttk.Frame(p3)

usage_lf.grid(row = 0, column = 0, sticky = 'nesw')
usage_rf.grid(row = 0, column = 1, sticky = 'nesw')

p3.rowconfigure(0, weight = 1)
p3.columnconfigure(0, weight = 8)
p3.columnconfigure(1, weight = 1)

#LF
cur.execute("select * from demand")
usage_val = cur.fetchall()

usage_lb = MultiColumnListbox(usage_lf, usage_head, usage_val)

#RF
u_l = ['Day', 'Quantity', 'Units']
u_l = [Label(usage_rf, text = x) for x in u_l]

ue_day = Entry(usage_rf)
ue_quantity = Entry(usage_rf)

bu_insert = Button(usage_rf, text = "INSERT", command = lambda : on_b_insert([ue_day, ue_quantity], usage_lb, 1))
ttk.Separator(usage_rf,orient=HORIZONTAL).grid(row=6, columnspan = 4,sticky = 'ew')
bu_update = Button(usage_rf, text = "EDIT", command = lambda: on_b_update(usage_lb, usage_head, 1))
bu_delete = Button(usage_rf, text = "DELETE", command = lambda : on_b_delete(usage_lb))

u_l[0].grid(row = 1, column = 1)
ue_day.grid(row = 1, column = 2, columnspan = 2)
u_l[1].grid(row = 3, column = 1)
ue_quantity.grid(row = 3, column = 2, columnspan = 2)
u_l[2].grid(row = 3, column =4, sticky = 'w')
bu_insert.grid(row = 5, column = 2)
bu_update.grid(row = 7, column = 2)
bu_delete.grid(row = 8, column = 2)

for i in range(30):
    usage_rf.rowconfigure(i, weight = 1)
for i in range(4):
    usage_rf.columnconfigure(i, weight = 1)


#SELLER--------------------------------------------------------------------------------------------

seller_head = ['SELLER_ID', 'ORDERING COST', 'UNIT PRICE', 'LEAD TIME']
offer_head = ['SELLER_ID', 'QUANTITY', 'DISCOUNT']

seller_ltf = ttk.Frame(p4)
seller_rtf = ttk.Frame(p4)
seller_lbf = ttk.Frame(p4)
seller_rbf = ttk.Frame(p4)
seller_ltf.grid(row = 0, column = 0, sticky = 'nesw')
seller_rtf.grid(row = 0, column = 1, sticky = 'nesw')
ttk.Separator(p4,orient=HORIZONTAL).grid(row=1, columnspan = 2,sticky = 'ew')
seller_lbf.grid(row = 2, column = 0, sticky = 'nesw')
seller_rbf.grid(row = 2, column = 1, sticky = 'nesw')

p4.grid_columnconfigure(0, weight=8)
p4.grid_columnconfigure(1, weight=1)
p4.grid_rowconfigure(0, weight=4)
p4.grid_rowconfigure(2, weight=5)


#LTF
cur.execute("SELECT * FROM SELLER")
seller_data = cur.fetchall()
seller_lb = MultiColumnListbox(seller_ltf, seller_head, seller_data)

#RTF
s_l = ['Seller Id', 'Ordering cost', 'Unit Price', 'Lead time', 'days']
s_l = [Label(seller_rtf, text = x) for x in s_l]

s_e = [Entry(seller_rtf) for i in range(4)]

bs_insert = Button(seller_rtf, text = "INSERT", command = lambda : on_b_insert(s_e, seller_lb, 2))
ttk.Separator(seller_rtf,orient=HORIZONTAL).grid(row=6, columnspan = 4,sticky = 'ew')
bs_update = Button(seller_rtf, text = "EDIT", command = lambda: on_b_update(seller_lb, seller_head, 2))
bs_delete = Button(seller_rtf, text = "DELETE", command = lambda : on_b_delete(seller_lb))

s_l[0].grid(row = 1, column = 1)
s_e[0].grid(row = 1, column = 2, columnspan = 2)
s_l[1].grid(row = 2, column = 1)
s_e[1].grid(row = 2, column = 2, columnspan = 2)
s_l[2].grid(row = 3, column = 1)
s_e[2].grid(row = 3, column = 2, columnspan = 2)
s_l[3].grid(row = 4, column = 1)
s_e[3].grid(row = 4, column = 2, columnspan = 2)
s_l[4].grid(row = 4, column =4, sticky = 'w')
bs_insert.grid(row = 5, column = 2)
bs_update.grid(row = 7, column = 2)
bs_delete.grid(row = 8, column = 2)

for i in range(10):
    seller_rtf.rowconfigure(i, weight = 1)
for i in range(4):
    seller_rtf.columnconfigure(i, weight = 1)

#LBF

cur.execute("SELECT * FROM OFFER")
offer_data = cur.fetchall()

offer_lb = MultiColumnListbox(seller_lbf, offer_head, offer_data)

#LTF
o_l = ['Seller Id', 'Quantity', 'Discount']
o_l = [Label(seller_rbf, text = x) for x in o_l]

o_e = [Entry(seller_rbf) for i in range(3)]

bo_insert = Button(seller_rbf, text = "INSERT", command = lambda : on_b_insert(s_e, offer_lb, 3))
ttk.Separator(seller_rbf,orient=HORIZONTAL).grid(row=5, columnspan = 4,sticky = 'ew')
bo_update = Button(seller_rbf, text = "EDIT", command = lambda: on_b_update(offer_lb, offer_head, 3))
bo_delete = Button(seller_rbf, text = "DELETE", command = lambda : on_b_delete(offer_lb))

o_l[0].grid(row = 1, column = 1)
o_e[0].grid(row = 1, column = 2, columnspan = 2)
o_l[1].grid(row = 2, column = 1)
o_e[1].grid(row = 2, column = 2, columnspan = 2)
o_l[2].grid(row = 3, column = 1)
o_e[2].grid(row = 3, column = 2, columnspan = 2)
bo_insert.grid(row = 4, column = 2)
bo_update.grid(row = 6, column = 2)
bo_delete.grid(row = 7, column = 2)

for i in range(10):
    seller_rbf.rowconfigure(i, weight = 1)
for i in range(4):
    seller_rbf.columnconfigure(i, weight = 1)


#SELLER ANALYSIS--------------------------------------------------------------------------------------------

analysis_head = ['SELLER_ID', 'ORDERING COST', 'UNIT PRICE', 'LEAD TIME', 'QUANTITY', 'DISCOUNT', 'TOTAL COST', 'UNIT COST']

analysis_lf = ttk.Frame(p5)
analysis_rf = ttk.Frame(p5)

analysis_lf.grid(row = 0, column = 0, sticky = 'nesw')
analysis_rf.grid(row = 0, column = 1, sticky = 'nesw')

p5.rowconfigure(0, weight = 1)
p5.columnconfigure(0, weight = 8)
p5.columnconfigure(1, weight = 1)

#TF
analyze_seller()
analysis_lb = MultiColumnListbox(analysis_lf, analysis_head, seller_analysis)


#BF
sa_l = ['Max unit cost', 'Max lead time' ,'days']
sa_l = [Label(analysis_rf, text = x) for x in sa_l]

sa_e = [Entry(analysis_rf) for i in range(2)]

bsa_filter = Button(usage_rf, text = "Filter", command = lambda : on_filter())

sa_l[0].grid(row = 1, column = 1)
sa_e[0].grid(row = 1, column = 2, columnspan = 2)
sa_l[1].grid(row = 3, column = 1)
sa_e[1].grid(row = 3, column = 2, columnspan = 2)
sa_l[2].grid(row = 3, column = 4)
#bsa_filter.grid(row = 3, column = 1)

for i in range(20):
    analysis_rf.rowconfigure(i, weight = 1)
for i in range(4):
    analysis_rf.columnconfigure(i, weight = 1)




#STOCK ANALYSIS--------------------------------------------------------------------------------------------
u_rate(60)

stock_head = ['Day', 'Stock']

stock_lf = ttk.Frame(p6)
stock_rf = ttk.Frame(p6)

stock_lf.grid(row = 0, column = 0, sticky = 'nesw')
stock_rf.grid(row = 0, column = 1, sticky = 'nesw')

p6.rowconfigure(0, weight = 1)
p6.columnconfigure(0, weight = 8)
p6.columnconfigure(1, weight = 1)

#LF
analyze_stock(usage_head)
stock_lb = MultiColumnListbox(stock_lf, stock_head, stock_analysis)

#RF
st_l = ['Days']
st_l = [Label(stock_rf, text = x) for x in st_l]

st_e = [Entry(stock_rf) for i in st_l]

bst_stock = Button(stock_rf, text = "Stock analysis", command = lambda : plot_stock(root))
bst_demand = Button(stock_rf, text = "Demand analysis", command = lambda: plot_demand(usage_head, root))

st_l[0].grid(row = 1, column = 1)
st_e[0].grid(row = 1, column = 2, columnspan = 2)
bst_demand.grid(row = 3, column = 1)
bst_stock.grid(row = 3, column = 3)

for i in range(20):
    stock_rf.rowconfigure(i, weight = 1)
for i in range(4):
    stock_rf.columnconfigure(i, weight = 1)










#END
root.mainloop()

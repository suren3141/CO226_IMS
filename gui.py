from tkinter import *
import tkinter.font as tkFont
import tkinter.ttk as ttk
import pymysql as MySQLdb
import math
from matplot import Plotter


#GLOBAL VARIABLES-------------------------------------------------------------------------------------
demand = 0
holding_cost = 30
safety_stock = 0
max_lead_time = (-1)
max_unit_cost = float(-1)
rate = 0
seller_analysis = []
stock_val = []
stock_analysis = []
s_choice = 0
lt_choice = 0
q_choice = 0
uc_choice = 0
current_stock = 0
rod = 0
rol = 0

#MAIN FUNCTIONS------------------------------------------------------------------------------------------------
def EOQ(d, h, o):
    # economic order quantity is the optimum quantity of goods to be purchased at one time in order to
    # minimize the annual total costs of ordering and carrying or holding items in inventory
    return math.sqrt(2*o*d/h)

def ROL(lead , SS, rate):
    # Reorder level. Level at which order should be made in order to avoid stock out
    return lead*rate + SS

def ROD(x1, y1, rol, rate):
    #Day corresponding to reorder level
    return x1 + (y1-rol)/rate

def cost(up, discount, holding_cost, order_cost, quantity, demand):
    #total cost given inputs
    return up*(1-discount)*demand + demand*order_cost / quantity + (holding_cost*quantity) / (2)

def u_rate(d):
    #usage rate taken as an average of past d days
    #Could use better model
    x, y = get_tree_val(usage_lb.tree, 'Day', 'Quantity')
    days = max(x)
    usage = [0] * (days+1)
    for i in range(len(x)):
        usage[x[i]] += y[i]

    global rate
    rate = sum(usage[-d:])/d

def get_demand(days):
    #Get annual demand using sum of past number of days
    #Could use a better model
    x, y = get_tree_val(usage_lb.tree, usage_head[0], usage_head[1])
    l = max(len(y), days)
    return math.ceil(365*(sum(y[-l:])/l))

def line_fit(x, x1, y1, m):
    #Points of predicted usage
    #Could use better model
    return -m*(x-x1) + y1

def analyze_seller():
    #Analyze all sellers to find best combinatoin
    global seller_analysis
    seller_analysis = []    #Make list empty

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

    #print(holding_cost)
    #for row in seller_analysis:
    #    print(row)

    for i in range(n):
        if eoq_seller[i]:
            oc, up, lt = seller[i]
            tc = cost(up, d_seller[i], holding_cost, oc, eoq_seller[i], demand)
            seller_analysis.append((i, oc, up, lt, eoq_seller[i], d_seller[i], int(tc), "{0:.2f}".format(tc/demand)))


    #return seller_analysis


def analyze_stock():
    #Find stock levels at the end of each day
    x1, y1 = get_tree_val(usage_lb.tree, 'Day', 'Quantity')
    x2, y2 = get_tree_val(purchase_lb.tree, 'Day', 'Quantity')
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
    update_global()
    global current_stock
    current_stock= stock_val[-1]
    if current_stock < rol:
        on_error("Attenion! Order now to avoid Stock out")
    #return stock_val

#SQL FUNCTIONS------------------------------------------------------------------------------------------------

def insert_to_db(table, values):

    if table=='seller':
        TEMP = ','.join(i + '=VALUES(' + i + ')' for i in ['OC','UP','LT'])
        cur.execute(
            "INSERT INTO {} VALUES({}) ON DUPLICATE KEY UPDATE {}".format(table, ','.join(str(i) for i in values),
                                                                          TEMP))
    if table == 'offer':
        TEMP = ','.join(i + '=VALUES(' + i + ')' for i in ['Q','D'])
        print(values,TEMP)
        cur.execute(
            "INSERT INTO {} VALUES({}) ON DUPLICATE KEY UPDATE {}".format(table, ','.join(str(i) for i in values),
                                                                          TEMP))

    if table == 'demand':
        cur.execute("INSERT INTO {} VALUES({})".format(table, ','.join(str(i) for i in values)))
    if table == 'purchase':
        cur.execute("INSERT INTO {} VALUES({})".format(table, ','.join(str(i) for i in values)))

    db.commit()

def delete_from_db_using_id(table, id):
    cur.execute("DELETE FROM {} WHERE ID={}".format(table, id))
    db.commit()

def delete_from_db_using_values(table, values):
    TEMP=''
    if table=='seller':
        TEMP = 'ID={} and OC={} and UP={} and LT={}'.format(values[0],values[1],values[2],values[3])
    if table == 'offer':
        TEMP = 'ID={} and Q={} and D={}'.format(values[0],values[1],values[2])
    if table == 'demand':
        TEMP = 'D={} and Q={}'.format(values[0],values[1])
    if table == 'purchase':
        TEMP = 'D={} and Q={}'.format(values[0],values[1])
    cur.execute("DELETE FROM {} WHERE {}".format(table, TEMP))
    db.commit()

#BUTTON functions----------------------------------------------------------------------------------------------------------

def on_b_insert(entries, mlb, flag):
    val = []
    rep = 0
    if flag == 1:
        try:
            for i in range(len(entries)):
                val.append(int(entries[i].get()))
            if mlb==usage_lb:
                insert_to_db('demand',val)
            elif mlb==purchase_lb:
                insert_to_db('purchase',val)
            mlb.insert(tuple(val))
            analyze_stock()
            refresh(stock_lb, stock_analysis)
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
        # sql is updated when ok pressed. Goto update class to see it

def on_b_delete(mlb, root, flag = 0):
    cur_item = mlb.tree.focus()
    if cur_item == '':
        on_error('Select an entry')
    else:
        w = Confirm("Do you want to delete this entry and all other related entries", root)
        root.wait_window(w.win)
        if w.reply:
            val = (mlb.tree.item(cur_item)['values'])
            if mlb == usage_lb:
                delete_from_db_using_values('demand',val)
            elif mlb == purchase_lb:
                delete_from_db_using_values('purchase', val)
            elif mlb == offer_lb:
                delete_from_db_using_values('offer', val)
            elif mlb == seller_lb:
                delete_from_db_using_values('seller', val)

            if flag == 1:
                id = seller_lb.tree.item(cur_item)['values'][0]
                #cur.execute('delete from seller where id = {}'.format(id))
                cur.execute('select * from offer')
                temp = cur.fetchall()
                #print(temp)
                for child in offer_lb.tree.get_children():
                    offer_lb.tree.delete(child)
                for row in temp:
                    offer_lb.insert(row)

            mlb.tree.delete(cur_item)
            analyze_stock()
            refresh(stock_lb, stock_analysis)
            analyze_seller()
            refresh(analysis_lb, seller_analysis)

            #print('1')
    return


def on_seller_insert(entries):
    # TODO: is there any possibility to ignore entering certain fields?
    try:
        v1 = int(entries[0].get())
        v2 = int(entries[1].get())
        v3 = float(entries[2].get())
        v4 = int(entries[3].get())
        insert_to_db('seller',[v1,v2,v3,v4])
        seller_lb.insert((v1, v2, v3, v4))
        analyze_seller()
        refresh(analysis_lb, seller_analysis)
    except:
        print('2')
        on_error('Enter valid values')
        return -1
    return 0


def on_offer_insert(entries):
    # TODO: is there any possibility to ignore entering certain fields?
    try:
        v1 = int(o_e[0].get())
        v2 = int(o_e[1].get())
        v3 = float(o_e[2].get())
        insert_to_db('offer',[v1,v2,v3])
        offer_lb.insert((v1, v2, v3))
        analyze_seller()
        refresh(analysis_lb, seller_analysis)
    except:
        print('err 3')
        on_error('Enter valid values')
        return -1
    return 0

def find_demand(days):
    val = get_demand(days)
    e_demand.delete(0, END)
    e_demand.insert(0, str(val))

def refresh(mlb, arr):
    #Refresh a list box with values in arr
    for child in mlb.tree.get_children():
        try:
            mlb.tree.delete(child)
        except:
            print (child)
    for row in arr:
        mlb.insert(row)


def on_save():
    d = e_demand.get().strip()
    ss = e_ss.get().strip()
    hc = e_hc.get().strip()
    try:
        global demand
        demand= int(d)
        h_l1[1].config(text = d)
    except:
        pass
    try:
        global safety_stock
        safety_stock= int(ss)
        h_l1[4].config(text =ss)
    except:
        pass
    try:
        global holding_cost
        holding_cost= int(hc)
        h_l1[6].config(text = hc)
    except:
        pass
    analyze_seller()
    refresh(analysis_lb, seller_analysis)


#def on_analyze():
#    on_save()
#    nb.select(p5)

def update_global():
    u_rate(60)
    x1 = max(stock_val)
    y1 = stock_val[-1]
    global rol
    rol = ROL(lt_choice, safety_stock, rate)
    global rod
    rod = ROD(x1, y1, rol, rate)


def plot_demand(root):
    x, y = get_tree_val(usage_lb.tree, 'Day', 'Quantity')
    days = max(x)
    usage = [0] * (days+1)
    for i in range(len(x)):
        usage[x[i]] += y[i]
    W = Plotter(root, range(days), usage[1:], 'plot')

def plot_stock(root):
    x1 = len(stock_val)

    y1 = stock_val[-1]

    xx = range(x1, x1 + math.ceil(y1/rate))
    yy = [line_fit(i, x1, y1, rate) for i in xx]

    rol = ROL(lt_choice, safety_stock, rate)

    rod = ROD(x1, y1, rol, rate)

    y3 = range(math.floor(rol))
    x3 = [rod]*len(y3)

    W = Plotter(root, range(1,x1), stock_val[1:], 'step')
    W.a.plot(range(x1), [safety_stock]*x1, 'y--')
    W.a.plot(x3, y3, 'g--')
    W.a.text(x3[-1], y3[-1], 'Reorder Level', horizontalalignment='right')
    W.a.plot(xx, yy, 'r--')


def get_tree_val(tv, x_name, y_name):
    children = tv.get_children()
    data = [(int(tv.set(child,x_name)), int(tv.set(child,y_name))) for child in children]
    data = sorted(data, key = lambda x:x[0])
    x = [a[0] for a in data]
    y = [a[1] for a in data]
    return x, y

#def on_plot(root, x, y, type):
#    W = Plotter(root, x, y, type)

def filter_lb():
    if max_unit_cost < 0 and max_lead_time < 0:
        temp = seller_analysis
    elif max_unit_cost < 0:
        temp = filter(lambda x:int(x[3]) <= max_lead_time, seller_analysis)
    elif max_lead_time< 0:
        temp = filter(lambda x:float(x[-1]) <= max_unit_cost, seller_analysis)
    else:
        temp = [x for x in seller_analysis if (int(x[3]) <= max_lead_time and float(x[-1]) <= max_unit_cost)]
    children = analysis_lb.tree.get_children()
    for child in children:
        analysis_lb.tree.delete(child)
    for row in temp:
        analysis_lb.insert(row)

def on_filter():
    global max_lead_time
    global max_unit_cost
    try:
        v1 = float(sa_e[0].get())
    except:
        v1 = float(-1)
        sa_e[0].delete(0, END)

    try:
        v2 = int(sa_e[1].get())
    except:
        v2 = -1
        sa_e[1].delete(0, END)
    max_lead_time = v2
    max_unit_cost = v1
    filter_lb()

def on_choice():
    cur_item = analysis_lb.tree.focus()
    if cur_item == '':
        on_error('Select an entry')
    val = analysis_lb.tree.item(cur_item)['values']
    make_choice(val)
    h_l1[-1].config(text = str(lt_choice))
    h_l1[-3].config(text = str(q_choice))
    h_l1[-5].config(text = str(uc_choice))
    h_l1[-7].config(text = str(s_choice))

def make_choice(val):
    global s_choice
    global q_choice
    global lt_choice
    global uc_choice
    s_choice = val[0]
    q_choice = val[4]
    lt_choice = val[3]
    uc_choice = val[-1]
    #print(val)

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
    l = Label(e, text = message, font=("Arial", 16)).pack()
    b = Button(e, text = "OK", command = e.destroy)
    b.pack(side = BOTTOM, padx = 4, pady = 4)


class Confirm:

    def __init__(self, message, root):
        self.reply = 0
        self.win = Toplevel(root)
        self.setup_win(message)

    def setup_win(self, message):

        f = Frame(self.win)
        f.pack()

        l = Label(f, text = message)
        l.pack()

        b_ok = Button(f, text = "YES", command = self.on_ok)
        b_ok.pack()

        b_cancel = Button(f, text = "NO", command = self.on_cancel)
        b_cancel.pack()

    def on_cancel(self):
        self.win.destroy()

    def on_ok(self):
        self.reply = 1
        self.win.destroy()




class Update(object):

    def __init__(self, mlb, labels, root, cur_item, val, ind):
        self.win = Toplevel(root)
        self.setup_win(mlb, labels, cur_item, val, ind)
        self.previous_val = val

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
        val=[]
        for i in range(len(entries)):
            val.append((entries[i].get()))
        if mlb == usage_lb:
            cur.execute("delete from DEMAND WHERE D={} AND Q={} LIMIT 1".format(
                                                                                   self.previous_val[0],
                                                                                   self.previous_val[1]))
        elif mlb == purchase_lb:
            cur.execute("DELETE FROM purchase WHERE D={} AND Q={} LIMIT 1".format(
                                                                                   self.previous_val[0],
                                                                                   self.previous_val[1]))
        elif mlb == offer_lb:
            print(val)
            insert_to_db('offer', val)
        elif mlb == seller_lb:
            print(val)
            insert_to_db('seller',val)

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
bp_delete = Button(purchase_rf, text = "DELETE", command = lambda : on_b_delete(purchase_lb, root))

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

#set vars
demand = get_demand(60)
safety_stock = math.ceil(2*demand/365)

#RF
u_l = ['Day', 'Quantity', 'Units']
u_l = [Label(usage_rf, text = x) for x in u_l]

ue_day = Entry(usage_rf)
ue_quantity = Entry(usage_rf)

bu_insert = Button(usage_rf, text = "INSERT", command = lambda : on_b_insert([ue_day, ue_quantity], usage_lb, 1))
ttk.Separator(usage_rf,orient=HORIZONTAL).grid(row=6, columnspan = 4,sticky = 'ew')
bu_update = Button(usage_rf, text = "EDIT", command = lambda: on_b_update(usage_lb, usage_head, 1))
bu_delete = Button(usage_rf, text = "DELETE", command = lambda : on_b_delete(usage_lb, root))

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
bs_delete = Button(seller_rtf, text = "DELETE", command = lambda : on_b_delete(seller_lb, root, 1))

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

bo_insert = Button(seller_rbf, text = "INSERT", command = lambda : on_b_insert(o_e, offer_lb, 3))
ttk.Separator(seller_rbf,orient=HORIZONTAL).grid(row=5, columnspan = 4,sticky = 'ew')
bo_update = Button(seller_rbf, text = "EDIT", command = lambda: on_b_update(offer_lb, offer_head, 3))
bo_delete = Button(seller_rbf, text = "DELETE", command = lambda : on_b_delete(offer_lb, root))

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
def_choice = sorted(seller_analysis, key = lambda x:float(x[-1]))[0]
make_choice(def_choice)
analysis_lb = MultiColumnListbox(analysis_lf, analysis_head, seller_analysis)


#BF
sa_l = ['Max unit cost', 'Max lead time' ,'days']
sa_l = [Label(analysis_rf, text = x) for x in sa_l]

sa_e = [Entry(analysis_rf) for i in range(2)]

bsa_filter = Button(analysis_rf, text = "Filter", command = lambda : on_filter())
bsa_choice = Button(analysis_rf, text = "Choose", command = lambda : on_choice())

sa_l[0].grid(row = 1, column = 1)
sa_e[0].grid(row = 1, column = 2, columnspan = 2, sticky = 'w')
sa_l[1].grid(row = 3, column = 1)
sa_e[1].grid(row = 3, column = 2, columnspan = 2, sticky = 'w')
sa_l[2].grid(row = 3, column = 4)
bsa_filter.grid(row = 5, column = 2)
bsa_choice.grid(row = 8, column = 2)


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
analyze_stock()
stock_lb = MultiColumnListbox(stock_lf, stock_head, stock_analysis)

#RF
st_l = ['Days']
st_l = [Label(stock_rf, text = x) for x in st_l]

st_e = [Entry(stock_rf) for i in st_l]

bst_stock = Button(stock_rf, text = "Stock analysis", command = lambda : plot_stock(root))
bst_demand = Button(stock_rf, text = "Demand analysis", command = lambda: plot_demand(root))

st_l[0].grid(row = 1, column = 1)
st_e[0].grid(row = 1, column = 2, columnspan = 2)
bst_demand.grid(row = 3, column = 1)
bst_stock.grid(row = 3, column = 3)

for i in range(20):
    stock_rf.rowconfigure(i, weight = 1)
for i in range(4):
    stock_rf.columnconfigure(i, weight = 1)



#HOME--------------------------------------------------------------------------------------------

h_l1 = ['Annual Demand', str(demand), 'Units', 'Safety Stock', str(safety_stock), 'Holding Cost', str(holding_cost), 'Chosen Seller info:', 'Seller ID', str(s_choice), 'Unit Cost', str(uc_choice), 'Quantity', str(q_choice), 'Lead time', str(lt_choice)]
h_l2 = ['Annual Demand', 'Units', 'Safety Stock', 'Holding Cost']
e_demand = Entry(p1)
e_ss = Entry(p1)
e_hc = Entry(p1)
h_l1 = [Label(p1, text = x) for x in h_l1]
h_l2 = [Label(p1, text = x) for x in h_l2]

h_l1[0].grid(row = 1, column = 2)
h_l1[1].grid(row = 1, column = 4)
h_l1[2].grid(row = 1, column = 5, sticky = 'e')
h_l1[3].grid(row = 2, column = 2)
h_l1[4].grid(row = 2, column = 4)
h_l1[5].grid(row = 3, column = 2)
h_l1[6].grid(row = 3, column = 4)
h_l1[7].grid(row = 4, column = 1, sticky = 'e')
h_l1[8].grid(row = 5, column = 2)
h_l1[9].grid(row = 5, column = 4)
h_l1[10].grid(row = 6, column = 2)
h_l1[11].grid(row = 6, column = 4)
h_l1[12].grid(row = 7, column = 2)
h_l1[13].grid(row = 7, column = 4)
h_l1[14].grid(row = 8, column = 2)
h_l1[15].grid(row = 8, column = 4)

ttk.Separator(p1,orient=HORIZONTAL).grid(row=9, columnspan = 10,sticky = 'ew')

Label(p1, text = "Change default values").grid(row = 10, column = 1, sticky = 'w')
h_l2[0].grid(row = 11, column = 2)
h_l2[1].grid(row = 11, column = 5, sticky = W)
h_l2[2].grid(row = 12, column = 2)
h_l2[3].grid(row = 13, column = 2)
e_demand.grid(row = 11, column = 4)
e_ss.grid(row = 12, column = 4)
e_hc.grid(row = 13, column = 4)

b_save = Button(p1, text = "Save", command = on_save)
#b_analyze = Button(p1, text = "Analyze", command = on_analyze)
b_find_demand = Button(p1, text = "Find Demand", command = lambda : find_demand(365))

b_save.grid(row = 15, column = 3)
#b_analyze.grid(row = 4, column = 4, padx = 2)
b_find_demand.grid(row = 11, column = 6)

for i in range(20):
    p1.rowconfigure(i, weight = 1)
for j in range(10):
    p1.columnconfigure(j, weight = 1)







#END
root.mainloop()

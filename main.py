import numpy as np
import matplotlib.pyplot as plt
import math

def EOQ(d, h, o):
    return np.sqrt(2*o*d/float(h))

def ROL(lead , SS, rate):
    return lead*rate + SS

def cost(up, discount, holding_cost, order_cost, quantity):
    up*(1-discount) + order_cost / demand + (holding_cost*quantity) / (2 * demand)

def f(t):
    a = 1000
    b =.5
    w0 = 1.0/60
    w1 = 1.0/23
    w2 = 1.0/8
    w3 = 1.0/3
    c0 = .08*a
    c1 = .05 * a
    c2 = .025 * a
    c3 = .01 * a
    return c0 * np.sin(w0*t) - c1 * np.sin(w1*t) + c2 * np.sin(w2*t) - c3 * np.sin(w3*t) + .005 *a* np.random.random() + (a + b*t)

'''
seller = [
    25000,

]

discounts = [
    [(.06, 8000), (.1, 15000)]
]
'''


x = np.arange(1, 366)
y = f(x).astype(int)
#print(type(y))

demand = math.ceil(sum(y)/5000.)*5000
hc = 30
#rate = sum(y[-60:])/60.0

print (demand)
#print (rate)




#plt.plot(x, y)
#plt.show()












import MySQLdb

db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="root",         # your username
                                          # your password
                     db="e14379lab04")    # name of the data base

# you must create a Cursor object. It will let
#  you execute all the queries you need
cur = db.cursor()

# Use all the SQL you like
#cur.execute("CREATE TABLE demand(d INT, quantity INT);")
for i in range(len(x)):
	cur.execute("INSERT INTO demand VALUES ({},{})".format(x[i],y[i]))

cur.execute("SELECT * FROM demand")

# print all the first cell of all the rows
for row in cur.fetchall():
    print(row)

db.close()
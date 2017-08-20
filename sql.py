#READ ME
#run mysql and create database called co226

import numpy as np
import pymysql as MySQLdb
import math
import random
import matplotlib.pyplot as plt

db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="root",         # your username
                                          # your password
                     db="co226")    # name of the data base

# you must create a Cursor object. It will let
#  you execute all the queries you need
cur = db.cursor()

#DEMAND sim----------------------------------------------------------------------------------------------------------------------

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

x = np.arange(1, 366)
y = f(x).astype(int)

try:
    cur.execute("DROP TABLE DEMAND")
except:
    pass

cur.execute("CREATE TABLE DEMAND(D INT, Q INT)")

for i in range(365):
    cur.execute("INSERT INTO DEMAND VALUES({}, {})".format(x[i], y[i]))

cur.execute("SELECT * FROM DEMAND")

print('Usage')
for row in cur.fetchall():
    print(row)


#SELLER sim-------------------------------------------------------------------------------------------------------------------------

try:
    cur.execute("DROP TABLE OFFER")
    cur.execute("DROP TABLE SELLER")
except:
    pass

cur.execute("CREATE TABLE SELLER(ID INT, OC INT, UP FLOAT, LT INT, PRIMARY KEY(ID)) ENGINE=InnoDB")
cur.execute("CREATE TABLE OFFER(ID INT, Q INT, D FLOAT, FOREIGN KEY (ID) REFERENCES SELLER(ID) ON DELETE CASCADE ON UPDATE CASCADE) ENGINE = InnoDB")


seller = [
    (1, 23000, 100, 10),
    (2, 21000, 101.5, 12),
    (3, 25000, 98.5, 5)
]


offer = [
    (3, 6000, .012),
    (3, 12000, .02),
    (1, 5000, .02),
    (1, 10000, .03),
    (1, 20000, .04),
    (2, 5000, .03),
    (2, 9000, .04),
    (2, 16000, .05)
]

#test
'''
offer = [
    (3, 6000, 0),
    (3, 12000, 0),
    (1, 5000, 0),
    (1, 10000, 0),
    (1, 20000, 0),
    (2, 5000, 0),
    (2, 9000, 0),
    (2, 16000, 0)
]
'''

for i in seller:
    cur.execute("INSERT INTO SELLER VALUES({})".format(','.join(str(j) for j in i)))

for i in offer:
    cur.execute("INSERT INTO OFFER VALUES({})".format(','.join(str(j) for j in i)))


print()
print('SELLERS')
cur.execute("SELECT * FROM SELLER")

for row in cur.fetchall():
    print(row)

cur.execute("SELECT * FROM OFFER")

print()
print('OFFERS')
for row in cur.fetchall():
    print(row)


#USAGE sim------------------------------------------------------------------------------------
cur.execute("select * from demand")
usage_val = cur.fetchall()

def find_demand(days):
    y = [x[1] for x in usage_val]
    l = max(len(y), days)
    return math.ceil(365*(sum(y[-l:])/l))

demand = find_demand(365)
holding_cost = 30
safety_stock = demand*2/365

def EOQ(d, h, o):
    return math.sqrt(2*o*d/h)


def cost(up, discount, holding_cost, order_cost, quantity, demand):
    return up*(1-discount)*demand + demand*order_cost / quantity + (holding_cost*quantity) / (2)

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
            seller_analysis.append((ind, seller[ind][0], seller[ind][1], seller[ind][2], q, d, tc))


    for i in range(n):
        if eoq_seller[i]:
            oc, up, lt = seller[i]
            uc = cost(up, d_seller[i], holding_cost, oc, eoq_seller[i], demand)
            seller_analysis.append((i, oc, up, lt, eoq_seller[i], d_seller[i], uc))


    return seller_analysis


cur.execute("SELECT * FROM SELLER")
seller_data = cur.fetchall()

cur.execute("SELECT * FROM OFFER")
offer_data = cur.fetchall()


seller_analysis = []
analyze_seller()

seller_analysis = sorted(seller_analysis, key = lambda x:x[-1])


#for row in seller_analysis:
#    print(row)


#choice - BEST SELLER OFFER
id, oc, up, lt, q, d, tc = seller_analysis[0]

print(q)

stock = q

purchase_val = [0]*370
stock_val = [0] * 366

stock_val[0] = q

purchases = [(1, q)]

for x, y in usage_val:
    #print(x,y)
    stock -= y
    if stock < safety_stock:
        stock += q
        day = round(x + (random.random())*2)
        purchases.append((day, q))
        purchase_val[day] = q

for x, y in usage_val:
    stock_val[x] = stock_val[x-1] - y + purchase_val[x]



x = range(366)
y = [safety_stock]* 366
plt.step(x, stock_val)
plt.plot(x, y)
#plt.show()

try:
    cur.execute("DROP TABLE PURCHASE")
except:
    pass

cur.execute("CREATE TABLE PURCHASE(D INT, Q INT)")

for x, y in purchases:
    cur.execute("INSERT INTO PURCHASE VALUES({}, {})".format(x, y))

cur.execute("SELECT * FROM PURCHASE")

print()
print("USAGE")
for row in cur.fetchall():
    print(row)



db.commit()
db.close()
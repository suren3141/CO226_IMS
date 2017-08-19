#READ ME
#run mysql and create database called co226

import pymysql as MySQLdb
import numpy as np

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



db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="root",         # your username
                                          # your password
                     db="co226")    # name of the data base

# you must create a Cursor object. It will let
#  you execute all the queries you need
cur = db.cursor()

# Use all the SQL you like
cur.execute("CREATE TABLE DEMAND(D INT, Q INT)")

for i in range(365):
    cur.execute("INSERT INTO DEMAND VALUES({}, {})".format(x[i], y[i]))

cur.execute("SELECT * FROM DEMAND")

# print all the first cell of all the rows
for row in cur.fetchall():
    print(row)

db.close()
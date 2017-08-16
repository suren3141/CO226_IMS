#gihanchanaka@gmail.com

#This is the test driver for Item_Demand object
import matplotlib.pyplot as plot
from Item_Demand import Item_Demand

averageSalesPerDay=100
WheelDemand = Item_Demand(averageSalesPerDay)
sales=[0]*365
for day in range(365):
    sales[day]=WheelDemand.salesOfDay(day)


freq=[0]*(averageSalesPerDay*5 + 1)
for i in range(365):
    freq[sales[i]]=freq[sales[i]]+1

plot.plot(range(365),sales)
plot.show()
plot.figure()
plot.plot(range(len(freq)),freq)
plot.show()

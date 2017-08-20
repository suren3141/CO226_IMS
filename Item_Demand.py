#gihanchanaka@gmail.com
import random
import math
import PoissonDristribution
import random
class Item_Demand():
    #The only functions you can use are
    #   constructor(averagePerDay)------ 0<=averagePerDay<=100
    #   salesOfDay(day) ----- 0<=day<=364


    def __init__(self,averagePerDay):
        self.mean=averagePerDay
        self.sales = [0] * 365
        self.temp = [0] * 365

        for day in range(365):
            self.sales[day]=round(PoissonDristribution.getNumberInPoissonDistribution(self.mean))
        self.sales.sort()

        d=0
        while True:
            self.temp[math.floor(d/2)]=self.sales[d]
            d += 1
            if d==365: break
            self.temp[364-math.floor(d/2)] = self.sales[d]
            d += 1

        randomShift=round(random.random()*365)

        for d in range(365):
            self.sales[d]=self.temp[(d+randomShift)%365]




    def salesOfDay(self,day):
        return self.sales[day]




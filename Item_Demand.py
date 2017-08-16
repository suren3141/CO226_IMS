#gihanchanaka@gmail.com
import random
import math
import PoissonDristribution

class Item_Demand():
    #The only functions you can use are
    #   constructor(averagePerDay)------ 0<=averagePerDay<=100
    #   salesOfDay(day) ----- 0<=day<=364


    def __init__(self,averagePerDay):
        self.mean=averagePerDay
        self.sales = [0] * 365

        for day in range(365):
            self.sales[day]=round(PoissonDristribution.getNumberInPoissonDistribution(self.mean))

    def salesOfDay(self,day):
        return self.sales[day]




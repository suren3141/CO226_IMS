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
        randomPhase=random.random()*2*3.14
        for day in range(365):
            linear=self.mean*0.7
            sinePart=self.mean*0.25
            poissonPart=self.mean*0.3

            saless=linear+sinePart*math.sin(randomPhase+(2*3.14*day/365))+PoissonDristribution.getNumberInPoissonDistribution(poissonPart)
            self.sales[day]=round(saless)

    def salesOfDay(self,day):
        return self.sales[day]




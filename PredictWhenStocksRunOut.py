#gihanchanaka@gmail.com
import PoissonDristribution

def noOfDaysStocksWillLast(meanSalesPerDay,stock):
	#This is a good enough special case of the general functions
	return noOfDaysStocksWillLastWithConfidence(0.8,meanSalesPerDay,stock)

def probabilityThatStocksWillRunOutBy(days,meanSalesPerDay,stock):
	newMean=meanSalesPerDay*days
	return PoissonDristribution.cumilativeProbability(newMean,stock)

def noOfDaysStocksWillLastWithConfidence(confidence,meanSalesPerDay,stock):
	#31 is returned if the stocks dont run out within a month
	for days in range(30):
		if(probabilityThatStocksWillRunOutBy(days,meanSalesPerDay,stock) >= confidence):
			return days
			break

	return 31


#gihanchanaka@gmail.com
import math
import random

def poisson(mean,x):
    return math.exp(-1 * mean) * pow(mean, x) / math.factorial(x)


def getNumberInPoissonDistribution(mean):
    cumilProbRand = random.random()
    cumilProbPoisson = 0
    n = 0
    while cumilProbRand > cumilProbPoisson:
        n = n + 1
        cumilProbPoisson = cumilProbPoisson + poisson(mean,n)

        if n >= 5 * mean:
            return n

    if (cumilProbPoisson - cumilProbRand) > poisson(mean,n) / 2:
        return n
    else:
        return n - 1
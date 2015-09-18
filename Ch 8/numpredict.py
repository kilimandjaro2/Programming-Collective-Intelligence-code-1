#!/usr/bin/python

from random import random, randint
import math
import optimization
from pylab import *

def wineprice(rating, age):
    peak_age = rating - 50

    # calculate price based on rating
    price = rating / 2
    if age > peak_age:
        # past its peak age, goes bad in 5 years
        price = price * (5 - (age - peak_age))
    else:
        # increase to 5x original value as it approaches its peak
        price = price * (5 * ((age + 1)/peak_age))

    if price < 0:
        price = 0
    return price

def wineset1():
    '''generate 300 bottles of wines and calculate prices,
       randomly add/substract 20 percent to capture variation'''
    rows = []
    for i in range(300):
        # create random age and rating
        rating = random() * 50 + 50
        age = random() * 50

        # get reference price
        price = wineprice(rating, age)

        # add some noise
        price *= (random() * 0.4 + 0.8)

        # add to the dataset
        rows.append({'input': (rating, age), 'result': price})
    return rows

def wineset2():
    '''add heterogeneous variables'''
    rows = []
    for i in range(300):
        rating = random() * 50 + 50
        age = random() * 50
        # not related to price
        aisle = float(randint(1, 20))
        # much larger in magnitude
        bottlesize = [375.0, 750.0, 1500.0, 3000.0][randint(0, 3)]
        price = wineprice(rating, age)
        price *= (bottlesize / 750)
        price *= (random() * 0.9 + 0.2)
        rows.append({'input': (rating, age, aisle, bottlesize),
                     'result': price})
    return rows

def wineset3():
    '''add discount for some cases'''
    rows = wineset1()
    for row in rows:
        if random() < 0.5:
            # wine was bought at a discount store
            row['result'] *= 0.5
    return rows

def euclidean(v1, v2):
    d = 0.0
    for i in range(len(v1)):
        d += (v1[i] - v2[i])**2
    return math.sqrt(d)

def getdistances(data, vec1):
    distancelist = []
    for i in range(len(data)):
        vec2 = data[i]['input']
        distancelist.append((euclidean(vec1, vec2), i))
    distancelist.sort()
    return distancelist

def knnestimate(data, vec1, k = 3):
    # get sorted distances
    dlist = getdistances(data, vec1)
    avg = 0.0

    # take the average of the top k results
    for i in range(k):
        idx = dlist[i][1]
        avg += data[idx]['result']
    avg /= k
    return avg

def inverseweight(dist, num = 1.0, const = 0.1):
    '''weight based on the inverse of distance'''
    return num/(dist + const)

def subtractweight(dist, const = 1.0):
    '''weight based on subtraction from given constant'''
    if dist > const:
        return 0
    else:
        return const - dist

def gaussian(dist, sigma = 1.0):
    '''weight based on gaussian curve'''
    return math.e**(-dist**2/(2 * sigma**2))

def weightedknn(data, vec1, k = 5, weightf = inverseweight):
    # get distances
    dlist = getdistances(data, vec1)
    avg = 0.0
    totalweight = 0.0

    # get weighted average
    for i in range(k):
        dist = dlist[i][0]
        idx = dlist[i][1]
        weight = weightf(dist)
        avg += (weight * data[idx]['result'])
        totalweight += weight
    avg /= totalweight
    return avg

def dividedata(data, test = 0.05):
    trainset = []
    testset = []
    for row in data:
        if random() < test:
            testset.append(row)
        else:
            trainset.append(row)
    return trainset, testset

def testalgorithm(algf, trainset, testset):
    error = 0.0
    for row in testset:
        guess = algf(trainset, row['input'])
        error += (row['result'] - guess)**2
    return error / len(testset)

def crossvalidate(algf, data, trials = 100, test = 0.05):
    error = 0.0
    for i in range(trials):
        trainset, testset = dividedata(data, test)
        error += testalgorithm(algf, trainset, testset)
    return error / trials

def rescale(data, scale):
    scaleddata = []
    for row in data:
        scaled = [scale[i] * row['input'][i] for i in range(len(scale))]
        scaleddata.append({'input': scaled, 'result': row['result']})
    return scaleddata

def createcostfunction(algf, data):
    def costf(scale):
        sdata = rescale(data, scale)
        return crossvalidate(algf, sdata, trials = 10)
    return costf

def probguess(data, vec1, low, high, k = 5, weightf = gaussian):
    dlist = getdistances(data, vec1)
    nweight = 0.0
    tweight = 0.0

    for i in range(k):
        dist = dlist[i][0]
        idx = dlist[i][1]
        weight = weightf(dist)
        v = data[idx]['result']

        # is this point in the range?
        if v >= low and v <= high:
            nweight += weight
        tweight += weight

    if tweight == 0:
        return 0

    # the probability is the weights in the range divided by all the weights
    return nweight / tweight

def cumulativegraph(data, vec1, high, k = 5, weightf = gaussian):
    t1 = arange(0.0, high, 0.1)
    cprob = array([probguess(data, vec1, 0, v, k, weightf) for v in t1])
    plot(t1, cprob)

def probabilitygraph(data, vec1, high, k = 5, weightf = gaussian, ss = 5.0):
    # make a range for the prices
    t1 = arange(0.0, high, 0.1)

    # get the probabilityfor the entire range
    probs = [probguess(data, vec1, v, v + 0.1, k, weightf) for v in t1]

    # smooth them by adding the gaussian of the nearby probabilities
    smoothed = []
    for i in range(len(probs)):
        sv = 0.0
        for j in range(len(probs)):
            dist = abs(i - j) * 0.1
            weight = gaussian(dist, sigma = ss)
            sv += weight * probs[j]
        smoothed.append(sv)
    smoothed = array(smoothed)

    plot(t1, smoothed)


if __name__ == "__main__":
    # data = wineset1()
    # print data[0:10]

    # print "actual price", wineprice(99.0, 5.0)
    # print "KNN predict", knnestimate(data, (99.0, 5.0))
    # print "weighted KNN predict", weightedknn(data, (99.0, 5.0))
    #
    # print "cross validated knn", crossvalidate(knnestimate, data)
    # print "cross validated weighted knn", crossvalidate(weightedknn, data)

    # data = wineset2()
    # sdata = rescale(data, [10.0, 10.0, 0.0, 0.5])

    # print "cross validated knn", crossvalidate(knnestimate, data)
    # print "cross validated knn (rescaled)", crossvalidate(knnestimate, sdata)
    # print "cross validated weighted knn", \
    #       crossvalidate(weightedknn, data)
    # print "cross validated weighted knn (rescaled)", \
    #       crossvalidate(weightedknn, sdata)

    # weightdomain = [(0, 20)]*4
    # costf = createcostfunction(knnestimate, data)
    # scale1 = optimization.geneticoptimize(weightdomain, costf)
    # print "scale from genetic optimization", scale1
    # scale2 = optimization.swarmoptimize(weightdomain, costf,
    #                                       popsize = 5, lrate = 1,
    #                                       maxv = 4, iters = 20)
    # print "scale from genetic optimization", scale2

    data = wineset3()

    print probguess(data, [99, 20], 40, 60)
    print probguess(data, [99, 20], 80, 120)
    print probguess(data, [99, 20], 120, 1000)
    print probguess(data, [99, 20], 30, 120)

    cumulativegraph(data, [99, 20], 120)
    probabilitygraph(data, [99, 20], 120)
    # different bigger ss, more smooth
    probabilitygraph(data, [99, 20], 120, ss = 3.0)
    probabilitygraph(data, [99, 20], 120, ss = 1.0)
    
    show()

#!/usr/bin/python

import math
import matplotlib.pylab as plt
from xml.dom.minidom import parseString
from urllib import urlopen, quote_plus

yahookey = "Your Key Here"

class Matchrow:
    def __init__(self, row, allnum = False):
        if allnum:
            self.data = [float(row[i]) for i in range(len(row) - 1)]
        else:
            self.data = row[0:len(row) - 1]
        self.match = int(row[len(row) - 1])


def loadmatch(f, allnum = False):
    rows = []
    for line in file(f):
        rows.append(Matchrow(line.split(','), allnum))
    return rows

def plotagematches(rows):
    xdm, ydm = [r.data[0] for r in rows if r.match == 1], \
               [r.data[1] for r in rows if r.match == 1]
    xdn, ydn = [r.data[0] for r in rows if r.match == 0], \
               [r.data[1] for r in rows if r.match == 0]

    plt.plot(xdm, ydm, 'go')
    plt.plot(xdn, ydn, 'r+')
    plt.show()

def lineartrain(rows):
    averages = {}
    counts = {}

    for row in rows:
        # get the class of this point
        cl = row.match

        averages.setdefault(cl, [0.0] * len(row.data))
        counts.setdefault(cl, 0)

        # add this point to the averages
        for i, d in enumerate(row.data):
            averages[cl][i] += float(d)

        # keep track of how many points in each classes
        counts[cl] += 1

    # divide sums by counts to get the averages
    for cl, avg in averages.items():
        for i, _ in enumerate(avg):
            avg[i] /= counts[cl]

    return averages

def dotproduct(v1, v2):
    return sum([v * v2[i] for i, v in enumerate(v1)])

def dpclassify(point, avgs):
    '''linear classifier'''
    # class = sign((X - (M0 + M1)/2) dot (M0 - M1))
    #       = sign(X dot M0 - X dot M1 + (M0 dot M0 - M1 dot M1) / 2)
    b = (dotproduct(avgs[1], avgs[1]) - dotproduct(avgs[0], avgs[0])) / 2
    y = dotproduct(point, avgs[0]) - dotproduct(point, avgs[1]) + b
    if y > 0:
        return 0
    else:
        return 1

def yesno(v):
    if v == 'yes':
        return 1
    elif v == 'no':
        return -1
    else:
        return 0

def matchcount(interest1, interest2):
    l1 = interest1.split(':')
    l2 = interest2.split(':')
    x = 0
    for v in l1:
        if v in l2:
             x += 1
    return x

def getlocation(address):
    if address in loc_cache:
        return loc_cache[address]
    data = urlopen('http://api.local.yahoo.com/MapsService/V1/' + \
                   'geocode?appid=%s&location=%s' %
                   (yahookey,quote_plus(address))).read()
    doc = parseString(data)
    lat = doc.getElementsByTagName('Latitude')[0].firstChild.nodeValue
    long = doc.getElementsByTagName('Longitude')[0].firstChild.nodeValue
    loc_cache[address] = (float(lat), float(long))
    return loc_cache[address]

def milesdistance(a1, a2):
    return 0

# def milesdistance(a1, a2):
#     lat1, long1 = getlocation(a1)
#     lat2, long2 = getlocation(a2)
#     latdif = 69.1 * (lat2 - lat1)
#     longdif = 53.0 * (long2 - long1)
#     return (latdif**2 + longdif**2)**0.5

def loadnumerical():
    oldrows = loadmatch('matchmaker.csv')
    newrows = []
    for row in oldrows:
        d = row.data
        data = [float(d[0]), yesno(d[1]), yesno(d[2]),
                float(d[5]), yesno(d[6]), yesno(d[7]),
                matchcount(d[3], d[8]),
                milesdistance(d[4], d[9]),
                row.match]
        newrows.append(Matchrow(data))
    return newrows

def scaledata(rows):
    low = [99999999.0]*len(rows[0].data)
    high = [-99999999.0]*len(rows[0].data)

    # find the lowest and highest values
    for row in rows:
        d = row.data
        for i in range(len(d)):
            if d[i] < low[i]:
                low[i] = d[i]
            if d[i] > high[i]:
                high[i] = d[i]

    # create a function that scales data
    def scaleinput(d):
        return [(d[i] - low[i])/(high[i] - low[i]) if high[i] - low[i] else 0
                for i in range(len(low))]

    # scale all the data
    newrows = [Matchrow(scaleinput(row.data) + [row.match])
               for row in rows]

    # return the new data and the function
    return newrows, scaleinput

def rbf(v1, v2, gamma = 20):
    '''radial-basis kernel'''
    dv = [v - v2[i] for i, v in enumerate(v1)]
    l = len(dv)
    return math.e**(-gamma * l)

def nlclassify(point, rows, offset, gamma = 10):
    sum0 = 0.0
    sum1 = 0.0
    count0 = 0
    count1 = 0

    for row in rows:
        if row.match == 0:
            sum0 += rbf(point, row.data, gamma)
            count0 += 1
        else:
            sum1 += rbf(point, row.data, gamma)
            count1 += 1
    y = (1.0/count0) * sum0 - (1.0/count1) * sum1 + offset

    if y < 0:
        return 0
    else:
        return 1

def getoffset(rows, gamma = 10):
    l0 = []
    l1 = []
    for row in rows:
        if row.match == 0:
            l0.append(row.data)
        else:
            l1.append(row.data)
    sum0 = sum(sum([rbf(v1, v2, gamma) for v1 in l0]) for v2 in l0)
    sum1 = sum(sum([rbf(v1, v2, gamma) for v1 in l1]) for v2 in l1)

    return (1.0/(len(l1)**2)) * sum1 - (1.0/(len(l0)**2)) * sum0


if __name__ == "__main__":
    agesonly = loadmatch('agesonly.csv', allnum = True)
    matchmaker = loadmatch('matchmaker.csv')

    # plotagematches(agesonly)

    # avgs = lineartrain(agesonly)
    # print avgs

    numericalset = loadnumerical()
    # print numericalset[0].data

    scaledset, scalef = scaledata(numericalset)
    # print scalef(numericalset[0].data)

    avgs = lineartrain(scaledset)
    print "Linear classifier", dpclassify(scalef(numericalset[0].data), avgs)

    ssoffset = getoffset(scaledset)
    print "Non-linear classifier", \
          nlclassify(scalef(numericalset[0].data), scaledset, ssoffset)

    # use LIBSVM
    from svm import *

    answers, inputs = [r.match for r in scaledset], \
                      [r.data for r in scaledset]
    param = svm_parameter('-t 2') # set to RBF kernel
    prob = svm_problem(answers, inputs)
    m = libsvm.svm_train(prob, param)
    x, max_idx = gen_svm_nodearray(scalef(numericalset[0].data))
    print "* \nSVM classifier", libsvm.svm_predict(m, x)

    # cross validation in LIBSVM
    import svmutil
    cv_acc = svmutil.svm_train(answers, inputs, '-v 3')

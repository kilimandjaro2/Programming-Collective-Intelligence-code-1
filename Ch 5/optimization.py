#!/usr/bin/python

import time
import random
import math
import pprint

people = [('Seymour', 'BOS'),
          ('Franny', 'DAL'),
          ('Zooey', 'CAK'),
          ('Walt', 'MIA'),
          ('Buddy', 'ORD'),
          ('Les', 'OMA')]

destination = 'LGA'

# load flights information
flights = {}
with open('schedule.txt', 'r') as f:
    for line in f:
        origin, dest, depart, arrive, price = line.strip().split(',')
        flights.setdefault((origin, dest), [])

        # add details to flights
        flights[(origin, dest)].append((depart, arrive, int(price)))

# utility function
def getminutes(t):
    x = time.strptime(t, '%H:%M')
    return x[3] * 60 + x[4]

def printschedule(r):
    for d in range(len(r)/2):
        name = people[d][0]
        origin = people[d][1]
        out = flights[(origin, destination)][r[d]]
        ret = flights[(destination, origin)][r[d + 1]]
        print "%10s%10s %5s-%5s $%3s %5s-%5s $%3s" % (name, origin, \
                                                      out[0], out[1], out[2], \
                                                      ret[0], ret[1], ret[2])

# cost function
def schedulecost(sol):
    totalprice = 0
    latestarrival = 0
    earliestdep = 24 * 60

    for d in range(len(sol) / 2):
        # get the inbound and outbound flights
        origin = people[d][1]
        outbound = flights[(origin, destination)][int(sol[d])]
        returnf = flights[(destination, origin)][int(sol[d + 1])]

        # total price is the price of all outbound and return flights
        totalprice += outbound[2]
        totalprice += returnf[2]

        # track the latest arrival and earliest departure
        if latestarrival < getminutes(outbound[1]):
            latestarrival = getminutes(outbound[1])
        if earliestdep > getminutes(returnf[0]):
            earliestdep = getminutes(returnf[0])

    # every person must wait at the airport until the latest person arrives.
    # They also must arrive at the same time and wait for their flights.
    totalwait = 0
    for d in range(len(sol)/2):
        origin = people[d][1]
        outbound = flights[(origin, destination)][int(sol[d])]
        returnf = flights[(destination, origin)][int(sol[d + 1])]
        totalwait += latestarrival - getminutes(outbound[1])
        totalwait += getminutes(returnf[0]) - earliestdep

    # does this solution require an extra day of car rental?
    if latestarrival > earliestdep:
        totalprice += 50

    return totalprice + totalwait

def randomoptimize(domain, costf):
    best = 999999999
    bestr = None
    # randomly test combinations
    for i in range(10000):
        # create a random solution
        r = [random.randint(domain[i][0], domain[i][1])
             for i in range(len(domain))]

        # get the cost
        cost = costf(r)

        # compare it to the best one so far
        if cost < best:
            best = cost
            bestr = r
    return bestr


if __name__ == "__main__":
    # s = [1, 4, 3, 2, 7, 3, 6, 3, 2, 4, 5, 3]
    # printschedule(s)
    # print schedulecost(s)

    domain = [(0, 8)] * (len(people) * 2)
    s = randomoptimize(domain, schedulecost)
    printschedule(s)
    print schedulecost(s)

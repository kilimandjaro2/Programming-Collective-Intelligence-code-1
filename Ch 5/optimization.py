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
    '''Random searching'''
    best = 999999999
    bestr = None
    # randomly test combinations
    for i in range(1000):
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

def hillclimb(domain, costf):
    '''Hill climbing'''
    # create a random solution
    sol = [random.randint(domain[i][0], domain[i][1])
           for i in range(len(domain))]

    while 1:
        # create list of neighboring solutions
        neighbors = []
        for j in range(len(domain)):

            # one away in each direction
            if sol[j] > domain[j][0]:
                neighbors.append(sol[0:j] + [sol[j] + 1] + sol[j+1:])
            if sol[j] < domain[j][1]:
                neighbors.append(sol[0:j] + [sol[j] - 1] + sol[j+1:])

        # see what the best solution amongst the neighbors is
        current = costf(sol)
        best = current
        for j in range(len(neighbors)):
            cost = costf(neighbors[j])
            if cost < best:
                best = cost
                sol = neighbors[j]

        # if there's no improvement, then we've reached the top
        if best == current:
            break

    return sol

def annealingoptimize(domain, costf, T = 10000.0, cool = 0.95, step = 1):
    '''Simulated annealing'''
    # initialize the values randomly
    vec = [random.randint(domain[i][0], domain[i][1])
           for i in range(len(domain))]

    while T > 0.1:
        # choose one of the indice
        i = random.randint(0, len(domain) - 1)

        # choose a direction to change it
        dir = random.randint(-step, step)

        # create a new lsit with one of the values changed
        vecb = vec[:]
        vecb[i] += dir
        if vecb[i] < domain[i][0]:
            vecb[i] = domain[i][0]
        elif vecb[i] > domain[i][1]:
            vecb[i] = domain[i][1]

        # calculate the current cost and the new cost
        ea = costf(vec)
        eb = costf(vecb)
        p = pow(math.e, (- eb - ea) / T)

        # is it better, or does it make the probability cutoff
        if eb < ea or random.random() < p:
            vec = vecb

        # decrease the temperature
        T = T * cool

    return vec

def geneticoptimize(domain, costf, popsize = 50, step = 1,
                    mutprob = 0.2, elite = 0.2, maxiter = 100):
    '''Genetic algorithms'''
    # mutation operation
    def mutate(vec):
        i = random.randint(0, len(domain) - 1)
        if random.random() < 0.5 and vec[i] > domain[i][0]:
            return vec[0:i] + [vec[i] - step] + vec[i+1:]
        elif vec[i] < domain[i][1]:
            return vec[0:i] + [vec[i] + step] + vec[i+1:]
        return vec

    # crossover operation
    def crossover(r1, r2):
        i = random.randint(1, len(domain) - 2)
        return r1[0:i] + r2[i:]

    # build the inital population
    pop = []
    for i in range(popsize):
        vec = [random.randint(domain[i][0], domain[i][1])
               for i in range(len(domain))]
        pop.append(vec)

    # how many winners from each generation?
    topelite = int(elite * popsize)

    # main loop
    for i in range(maxiter):
        scores = [(costf(v), v) for v in pop]
        scores.sort()
        ranked = [v for (s, v) in scores]

        # start with the pure winners
        pop = ranked[0:topelite]

        # add mutated and bred forms of the winners
        while len(pop) < popsize:
            if random.random() < mutprob:
                # mutation
                c = random.randint(0, topelite)
                pop.append(mutate(ranked[c]))
            else:
                # crossover
                c1 = random.randint(0, topelite)
                c2 = random.randint(0, topelite)
                pop.append(crossover(ranked[c1], ranked[c2]))

        # print current best score
        # print scores[0][0]

    return scores[0][1]


if __name__ == "__main__":
    # s = [1, 4, 3, 2, 7, 3, 6, 3, 2, 4, 5, 3]
    # printschedule(s)
    # print schedulecost(s)

    domain = [(0, 8)] * (len(people) * 2)

    s = randomoptimize(domain, schedulecost)
    printschedule(s)
    print "Random searching", schedulecost(s)

    s = hillclimb(domain, schedulecost)
    printschedule(s)
    print "Hill climbing", schedulecost(s)

    s = annealingoptimize(domain, schedulecost)
    printschedule(s)
    print "Simulated annealing", schedulecost(s)

    s = geneticoptimize(domain, schedulecost)
    printschedule(s)
    print "Genetic algorithms", schedulecost(s)

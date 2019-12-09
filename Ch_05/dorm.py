#!/usr/bin/python

import random
import math
import optimization

# the dorms, each of which has two available spaces
dorms = ['Zeus', 'Athena', 'Hercules', 'Bacchus', 'Pluto']

# people, along with their first and second choices
prefs = [('Toby', ('Bacchus', 'Hercules')),
		 ('Steve', ('Zeus', 'Pluto')),
		 ('Andrea', ('Athena', 'Zeus')),
		 ('Sarah', ('Zeus', 'Pluto')),
		 ('Dave', ('Athena', 'Bacchus')),
		 ('Jeff', ('Hercules', 'Pluto')),
		 ('Fred', ('Pluto', 'Athena')),
		 ('Suzie', ('Bacchus', 'Hercules')),
		 ('Laura', ('Bacchus', 'Hercules')),
		 ('Neil', ('Hercules', 'Athena'))]

# [(0, 9), (0, 8), ..., (0, 0)]
domain = [(0, (len(dorms) * 2) -i - 1) for i in range(len(dorms) * 2)]

def printsolution(vec):
	slots = []
	# create two slots for each dorm
	for i in range(len(dorms)):
		slots += [i, i]

	# loop over each students assignment
	for i in range(len(vec)):
		x = int(vec[i])

		# choose the slot from the remaining ones
		dorm = dorms[slots[x]]
		# show the student and assigned dorm
		print prefs[i][0], dorm
		# remove the slot
		del slots[x]

def dormcost(vec):
	cost = 0
	# create a list of slots
	slots = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]

	# loop over each student
	for i in range(len(vec)):
		x = int(vec[i])
		dorm = dorms[slots[x]]
		pref = prefs[i][1]
		# first choice costs 0, second choice costs 1
		if pref[0] == dorm:
			cost += 0
		elif pref[1] == dorm:
			cost += 1
		else:
			# not on the list costs 3
			cost += 3

		# remove the selected slot
		del slots[x]

	return cost


if __name__ == "__main__":
	# printsolution([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

	s = optimization.randomoptimize(domain, dormcost)
	print "Random searching", dormcost(s)
	printsolution(s)
	print '\n'

	s = optimization.geneticoptimize(domain, dormcost)
	print "Genetic algorithms", dormcost(s)
	printsolution(s)
	print '\n'

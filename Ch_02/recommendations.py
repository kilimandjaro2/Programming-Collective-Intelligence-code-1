#!/usr/bin/env python3
# encoding: utf-8

# recommendations.py	# This file's Name

#from editor import *			# Idea From David Beazley working "en vivo"
# Toutes les Libraries indispensables

# Dans le Terminal: PS1="\$ "	 Un prompt minimal!!!

from pprint import pprint  # A importer toujours...car tres utile
# print ("dir() === Indispensables en direct dans le Terminal"); pprint(dir())

__ref__ = """
# ===  References  ===
# Reworked by ZZ : --- on : --- 12/8/19, 20:32

LES REFERENCES SONT OBLIGATOIRES...
http://

Created by ZZ - 3/5/18, 7:13 PM.
Copyright (c) 2018 __MyCompanyName__. All rights reserved.

"""

__doc__ = """
# ===  Documentation  ===
# Template  minimum
	  traiter les sources avec ypf
	  https://yapf.now.sh/
(Yet another Python formatter)
# ===========================

=== Procedure a suivre: ===
# <Indispensable>

0/Presentation:
Une seule file qui est auto-suffisante, car elle comporte tout a la fois:
	-Le programme
	-Le lancement de L'Execution
	-Le resultat de l'Execution
tout cela sans quitter notre Editeur favori: BBEDIT!

1/Edition
Pour un maximum de clarte:
	Faire le menage dans les noms de folders et de files (en particulier, des files identiques en .py et .ipynd doivent porter des noms identiques(seule change l'extension)
	
Puis Editer dans BBEDITun job en se servant de ce Template.

2/Runs et Tests
En plus il comporte, via le "if __name__ == '__main__', un moyen de le tester "in extenso" ou de le garder tel quel pour des Imports.

3/Les sorties
Elles sont incorporees a cette file, via un "Cut and paste" dans la variable "output"

4/Une fois totalement edite, la file est incorporee dans Jupyter via un "Cut and paste"

5/Corrections minimes
Apres suppression du "Shebang", ce job runs  directement dans un Notebook sous Jupyter

6/Autre solulion (preferable), l'Import
Il est preferable de faire un import des noms de domaine du fichier  .py, car ainsi on ne conserve qu'un exemplaire de source unique.


Et aussi...

Cas de recuperation d'anciens codes:
====================================
1/3 Examen du contenu:
	deux blancs pour l'indentation ===> 1 tabulation

2/3   2to3 for Converting Python 2 scripts to Python 3
	Ref: la Doc de Python3:
		https://docs.python.org/2/library/2to3.html
		
	explications:
	https://pythonprogramming.net/converting-python2-to-python3-2to3/
	et
	Outil:   2to3 on Line:
	https://www.pythonconverter.com/


3/3	YAPF (Yet another Python formatter)
	https://yapf.now.sh/

"""


def first():
	"""<Documentation de first()>"""

	print("""< # Entering"first"   > """)

	# 	test cases
	
	p1 = 'Gene Seymour'

	p2 = 'Jack Matthews'
	print(sim_distance(critics, p1 , p2))
	print(sim_pearson (critics, p1 , p2))
	
	p2 = 'Lisa Rose'	
	print(sim_distance(critics, p1 , p2))
	print(sim_pearson (critics, p1 , p2))

	p0 = 'Toby'	
	print(topMatches(critics, p0 , n=3))
	
	pprint(getRecommendations(critics, p0))
	
	mv = 'Superman Returns'
	print(topMatches(movies, mv))
	
	mv = 'Just My Luck'
	print(getRecommendations(movies, 'Just My Luck'))
	
	print(calculateSimilarItems(critics))
	
	pprint(getRecommendedItems(critics, itemsim, p0))

	print("""< # END of "first"	> """)
	return


from math import sqrt

# A dictionary of movie critics and their ratings of a set of movie
critics = {
	'Lisa Rose': {
		'Lady in the Water': 2.5,
		'Snakes on a Plane': 3.5,
		'Just My Luck': 3.0,
		'Superman Returns': 3.5,
		'You, Me and Dupree': 2.5,
		'The Night Listener': 3.0
	},
	'Gene Seymour': {
		'Lady in the Water': 3.0,
		'Snakes on a Plane': 3.5,
		'Just My Luck': 1.5,
		'Superman Returns': 5.0,
		'The Night Listener': 3.0,
		'You, Me and Dupree': 3.5
	},
	'Michael Phillips': {
		'Lady in the Water': 2.5,
		'Snakes on a Plane': 3.0,
		'Superman Returns': 3.5,
		'The Night Listener': 4.0
	},
	'Claudia Puig': {
		'Snakes on a Plane': 3.5,
		'Just My Luck': 3.0,
		'The Night Listener': 4.5,
		'Superman Returns': 4.0,
		'You, Me and Dupree': 2.5
	},
	'Mick LaSalle': {
		'Lady in the Water': 3.0,
		'Snakes on a Plane': 4.0,
		'Just My Luck': 2.0,
		'Superman Returns': 3.0,
		'The Night Listener': 3.0,
		'You, Me and Dupree': 2.0
	},
	'Jack Matthews': {
		'Lady in the Water': 3.0,
		'Snakes on a Plane': 4.0,
		'The Night Listener': 3.0,
		'Superman Returns': 5.0,
		'You, Me and Dupree': 3.5
	},
	'Toby': {
		'Snakes on a Plane': 4.5,
		'You, Me and Dupree': 1.0,
		'Superman Returns': 4.0
	}
}


def sim_distance(prefs, person1, person2):
	'''Return a distance-based similarity score for person1 and person2.'''
	# get the list of shared items
	si = {}
	for item in prefs[person1]:
		if item in prefs[person2]:
			si[item] = 1

	# if no ratings in common, return 0
	if len(si) == 0:
		return 0

	# add up the squares of all the differences
	sum_of_squares = sum([
		pow(prefs[person1][item] - prefs[person2][item], 2)
		for item in prefs[person1] if item in prefs[person2]
	])
# 	return 1 / (1 + sum_of_squares)  # between (0, 1)  # BUG
	return 1 / (1 + sqrt(sum_of_squares))  # between (0, 1)  # BUG corrige


def sim_pearson(prefs, p1, p2):
	'''Return the Pearson correlation coefficient for p1 and p2.'''
	# get the list of shared items
	si = {}
	for item in prefs[p1]:
		if item in prefs[p2]:
			si[item] = 1

	# find the number of elements
	n = len(si)

	# if no ratings in common, return 0
	if len(si) == 0:
		return 0

	# add up all the preferences
	sum1 = sum([prefs[p1][item] for item in si])
	sum2 = sum([prefs[p2][item] for item in si])

	# sum up the squares
	sum1Sq = sum([pow(prefs[p1][item], 2) for item in si])
	sum2Sq = sum([pow(prefs[p2][item], 2) for item in si])

	# sum up the products
	pSum = sum([prefs[p1][item] * prefs[p2][item] for item in si])

	# calculate Pearson score
	num = pSum - (sum1 * sum2) / n
	den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
	if den == 0:
		return 0
	else:
		return num / den  # between(-1, 1)


def topMatches(prefs, person, n=5, similarity=sim_pearson):
	'''Return the best matches for person from the prefs dictionary.'''
	scores = [(similarity(prefs, person, other), other) for other in prefs
			  if other != person]
	# sort the list so the highest scores appear at the top
	scores.sort(reverse=True)
	return scores[0:n]


def getRecommendations(prefs, person, similarity=sim_pearson):
	'''Get recommendations for a person by using a weighed averaged ranking.'''
	totals = {}
	simSums = {}
	for other in prefs:
		# don't compare me to myself (skip to the next iteration)
		if other == person:
			continue

		sim = similarity(prefs, person, other)

		# ignore scores of zero or lower
		if sim <= 0:
			continue

		for item in prefs[other]:
			# only score movies I haven't seen yet
			if item not in prefs[person] or prefs[person][item] == 0:
				# similarity * score
				totals.setdefault(item, 0)
				totals[item] += prefs[other][item] * sim
				# sum of similarities
				simSums.setdefault(item, 0)
				simSums[item] += sim

	# create the normalized list
	rankings = [(total / simSums[item], item)
				for item, total in list(totals.items())]

	# return the sorted list
	rankings.sort(reverse=True)
	return rankings


def transformPrefs(prefs):
	'''Swipe the people and the item.'''
	results = {}
	for person in prefs:
		for item in prefs[person]:
			results.setdefault(item, {})
			# flip item and person
			results[item][person] = prefs[person][item]
	return results


movies = transformPrefs(critics)


def calculateSimilarItems(prefs, n=10):
	'''Return a dictionary of items showing which other items they are most similiar to.'''
	result = {}

	# invert the preference matrix to be item-centric
	itemPrefs = transformPrefs(prefs)
	c = 0
	for item in itemPrefs:
		# status updates for large datasets
		c += 1
		if c % 100 == 0:
			print("%d/%d" % (c, len(itemPrefs)))
		# find the most similar items to this one
		scores = topMatches(itemPrefs, item, n=n, similarity=sim_distance)
		result[item] = scores
	return result


itemsim = calculateSimilarItems(critics)


def getRecommendedItems(prefs, itemMatch, user):
	'''Get recommendations using the item-based filtering.'''
	userRatings = prefs[user]
	scores = {}
	totalSim = {}

	# loop over items rated by this user
	for (item, rating) in list(userRatings.items()):
		# loop over items similar to this one
		for (similarity, item2) in itemMatch[item]:
			# ignore if user has already reated this item
			if item2 in userRatings:
				continue

			# weighted sum of rating times similarity
			scores.setdefault(item2, 0)
			scores[item2] += similarity * rating

			# sum of all the similarities
			totalSim.setdefault(item2, 0)
			totalSim[item2] += similarity

	# divide each total score by total weighting to get an average
	rankings = [(score / totalSim[item], item)
				for item, score in list(scores.items())]

	# return the rankings from highest to lowest
	rankings.sort(reverse=True)
	return rankings


if __name__ == '__main__':

	# 	print(__ref__)
	# 	print(__doc__)

	print("""
	# ========== Job Begins ========== #""")
	print((first.__doc__))
	first()

	print("""
	# ========== Job ends  =========== #
	""")

output = """
<...Results of the ( or  more) run  -via a "Cut and paste"-...>

	# ========== Job Begins ========== #
<Documentation de first()>
< # Entering"first"   > 
0.8
0.963795681875635
0.14814814814814814
0.39605901719066977
[(0.9912407071619299, 'Lisa Rose'), (0.9244734516419049, 'Mick LaSalle'), (0.8934051474415647, 'Claudia Puig')]
[(3.3477895267131017, 'The Night Listener'), (2.8325499182641614, 'Lady in the Water'), (2.530980703765565, 'Just My Luck')]
[(0.6579516949597695, 'You, Me and Dupree'), (0.4879500364742689, 'Lady in the Water'), (0.11180339887498941, 'Snakes on a Plane'), (-0.1798471947990544, 'The Night Listener'), (-0.42289003161103106, 'Just My Luck')]
[(4.0, 'Michael Phillips'), (3.0, 'Jack Matthews')]
{'Lady in the Water': [(0.4, 'You, Me and Dupree'), (0.2857142857142857, 'The Night Listener'), (0.2222222222222222, 'Snakes on a Plane'), (0.2222222222222222, 'Just My Luck'), (0.09090909090909091, 'Superman Returns')], 'Snakes on a Plane': [(0.2222222222222222, 'Lady in the Water'), (0.18181818181818182, 'The Night Listener'), (0.16666666666666666, 'Superman Returns'), (0.10526315789473684, 'Just My Luck'), (0.05128205128205128, 'You, Me and Dupree')], 'Just My Luck': [(0.2222222222222222, 'Lady in the Water'), (0.18181818181818182, 'You, Me and Dupree'), (0.15384615384615385, 'The Night Listener'), (0.10526315789473684, 'Snakes on a Plane'), (0.06451612903225806, 'Superman Returns')], 'Superman Returns': [(0.16666666666666666, 'Snakes on a Plane'), (0.10256410256410256, 'The Night Listener'), (0.09090909090909091, 'Lady in the Water'), (0.06451612903225806, 'Just My Luck'), (0.05333333333333334, 'You, Me and Dupree')], 'You, Me and Dupree': [(0.4, 'Lady in the Water'), (0.18181818181818182, 'Just My Luck'), (0.14814814814814814, 'The Night Listener'), (0.05333333333333334, 'Superman Returns'), (0.05128205128205128, 'Snakes on a Plane')], 'The Night Listener': [(0.2857142857142857, 'Lady in the Water'), (0.18181818181818182, 'Snakes on a Plane'), (0.15384615384615385, 'Just My Luck'), (0.14814814814814814, 'You, Me and Dupree'), (0.10256410256410256, 'Superman Returns')]}
[(3.182634730538922, 'The Night Listener'), (2.5983318700614575, 'Just My Luck'), (2.4730878186968837, 'Lady in the Water')]
< # END of "first"	> 

	# ========== Job ends  =========== #
	
logout
"""

#!/usr/bin/python

from __future__ import division
from math import sqrt

# A dictionary of movie critics and their ratings of a set of movie
critics = {'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
                         'Just My Luck': 3.0, 'Superman Returns': 3.5,
                         'You, Me and Dupree': 2.5, 'The Night Listener': 3.0},
           'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
                            'Just My Luck': 1.5, 'Superman Returns': 5.0,
                            'The Night Listener': 3.0,
                            'You, Me and Dupree': 3.5},
           'Michael Phillips': {'Lady in the Water': 2.5,
                                'Snakes on a Plane': 3.0,
                                'Superman Returns': 3.5,
                                'The Night Listener': 4.0},
           'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
                            'The Night Listener': 4.5, 'Superman Returns': 4.0,
                            'You, Me and Dupree': 2.5},
           'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                            'Just My Luck': 2.0, 'Superman Returns': 3.0,
                            'The Night Listener': 3.0,
                            'You, Me and Dupree': 2.0},
           'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                             'The Night Listener': 3.0, 'Superman Returns': 5.0,
                             'You, Me and Dupree': 3.5},
           'Toby': {'Snakes on a Plane': 4.5, 'You, Me and Dupree': 1.0,
                    'Superman Returns': 4.0}}

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
    sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2)
                          for item in prefs[person1] if item in prefs[person2]])
    return 1/(1 + sum_of_squares) # between (0, 1)

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
    num = pSum - (sum1 * sum2)/n
    den = sqrt((sum1Sq - pow(sum1, 2)/n) * (sum2Sq - pow(sum2, 2)/n))
    if den == 0:
        return 0
    else:
        return num/den # between(-1, 1)

def topMatches(prefs, person, n = 5, similarity = sim_pearson):
    '''Return the best matches for person from the prefs dictionary.'''
    scores = [(similarity(prefs, person, other), other)
              for other in prefs if other != person]
    # sort the list so the highest scores appear at the top
    scores.sort(reverse = True)
    return scores[0:n]

def getRecommendations(prefs, person, similarity = sim_pearson):
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
    rankings = [(total/simSums[item], item) for item, total in totals.items()]

    # return the sorted list
    rankings.sort(reverse = True)
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

def calculateSimilarItems(prefs, n = 10):
    '''Return a dictionary of items showing which other items they are most similiar to.'''
    result = {}

    # invert the preference matrix to be item-centric
    itemPrefs = transformPrefs(prefs)
    c = 0
    for item in itemPrefs:
        # status updates for large datasets
        c += 1
        if c%100 == 0:
            print "%d/%d" % (c, len(itemPrefs))
        # find the most similar items to this one
        scores = topMatches(itemPrefs, item, n = n, similarity=sim_distance)
        result[item] = scores
    return result

itemsim = calculateSimilarItems(critics)

def getRecommendedItems(prefs, itemMatch, user):
    '''Get recommendations using the item-based filtering.'''
    userRatings = prefs[user]
    scores = {}
    totalSim = {}

    # loop over items rated by this user
    for (item, rating) in userRatings.items():
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
    rankings = [(score/totalSim[item], item)
                for item, score in scores.items()]

    # return the rankings from highest to lowest
    rankings.sort(reverse = True)
    return rankings


# test cases
# print sim_distance(critics, 'Jack Matthews', 'Gene Seymour')
# print sim_pearson(critics, 'Jack Matthews', 'Gene Seymour')
# print sim_distance(critics, 'Lisa Rose', 'Gene Seymour')
# print sim_pearson(critics, 'Lisa Rose', 'Gene Seymour')
# print topMatches(critics, 'Toby', n = 3)
print getRecommendations(critics, 'Toby')
# print topMatches(movies, 'Superman Returns')
# print getRecommendations(movies, 'Just My Luck')
# print calculateSimilarItems(critics)
print getRecommendedItems(critics, itemsim, 'Toby')

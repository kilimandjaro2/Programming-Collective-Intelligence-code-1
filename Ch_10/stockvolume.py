#!/usr/bin/python

import nmf
import urllib2
import numpy as np

tickers = ['YHOO', 'AVP', 'BIIB', 'BP', 'CL', 'CVX',
		   'AAPL', 'EXPE', 'GOOG', 'PG', 'XOM', 'AMGN']

shortest = 300
prices = {}
dates = None

for t in tickers:
	# open the url
	rows = urllib2.urlopen('http://real-chart.finance.yahoo.com/table.csv?' + \
						   's=%s&d=8&e=24&f=2015&g=d&a=3&b=12&c=1996' % t + \
						   '&ignore=.csv').readlines()

	# extract the volume field from every line
	prices[t] = [float(r.split(',')[5]) for r in rows[1:] if r.strip() != '']
	if len(prices[t]) < shortest:
		shortest = len(prices[t])

	if not dates:
		dates = [r.split(',')[0] for r in rows[1:] if r.strip() != '']

l1 = [[prices[tickers[i]][j]
	   for i in range(len(tickers))]
	  for j in range(shortest)]

# non-negative matrix factorization
w, h = nmf.factorize(np.matrix(l1), pc = 5)

# print h
# print w

# loop over all the features
for i in range(np.shape(h)[0]):
	print "Feature %d" % i

	# get the top stocks for this feature
	ol = [(h[i, j], tickers[j]) for j in range(np.shape(h)[1])]
	ol.sort()
	ol.reverse()
	for j in range(12):
		print ol[j]
	print

	# show the top dates for this feature
	porder = [(w[d, i], d) for d in range(300)]
	porder.sort()
	porder.reverse()
	print [(p[0], dates[p[1]]) for p in porder[0:3]]
	print

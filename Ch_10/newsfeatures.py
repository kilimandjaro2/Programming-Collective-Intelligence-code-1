#!/usr/bin/python

import feedparser
import re
import numpy as np

feedlist = ['http://today.reuters.com/rss/topNews',
			'http://today.reuters.com/rss/domesticNews',
			'http://today.reuters.com/rss/worldNews',
			'http://hosted.ap.org/lineups/TOPHEADS-rss_2.0.xml',
			'http://hosted.ap.org/lineups/USHEADS-rss_2.0.xml',
			'http://hosted.ap.org/lineups/WORLDHEADS-rss_2.0.xml',
			'http://hosted.ap.org/lineups/POLITICSHEADS-rss_2.0.xml',
			'http://www.nytimes.com/services/xml/rss/nyt/HomePage.xml',
			'http://www.nytimes.com/services/xml/rss/nyt/International.xml',
			'http://news.google.com/?output=rss',
			'http://feeds.salon.com/salon/news',
			'http://www.foxnews.com/xmlfeed/rss/0,4313,0,00.rss',
			'http://www.foxnews.com/xmlfeed/rss/0,4313,80,00.rss',
			'http://www.foxnews.com/xmlfeed/rss/0,4313,81,00.rss',
			'http://rss.cnn.com/rss/edition.rss',
			'http://rss.cnn.com/rss/edition_world.rss',
			'http://rss.cnn.com/rss/edition_us.rss']

def stripHTML(h):
	p = ''
	s = 0
	for c in h:
		if c == '<':
			s = 1
		elif c == '>':
			s = 0
			p += ' '
		elif s == 0:
			p += c
	return p

def separatewords(text):
	splitter = re.compile('\\W*')
	return [s.lower() for s in splitter.split(text) if len(s) > 3]

def getarticlewords():
	allwords = {}
	articlewords = []
	articletitles = []
	ec = 0
	# loop over every feed
	for feed in feedlist:
		f = feedparser.parse(feed)

		# loop over every article
		for e in f.entries:
			# ignore identical articles
			if e.title.encode('utf8') in articletitles:
				continue

			# extract the words
			txt = e.title.encode('utf8') + \
				  stripHTML(e.description.encode('utf8'))
			words = separatewords(txt)
			articlewords.append({})
			articletitles.append(e.title.encode('utf8'))

			# increase the counts for this word in allwords and in articlewords
			for word in words:
				allwords.setdefault(word, 0)
				allwords[word] += 1
				articlewords[ec].setdefault(word, 0)
				articlewords[ec][word] += 1
			ec += 1
	return allwords, articlewords, articletitles

def makematrix(allw, articlew):
	wordvec = []

	# only take words that are common but not too common
	for w, c in allw.items():
		if c > 3 and c < len(articlew) * 0.6:
			wordvec.append(w)

	# creat the word matrix
	l1 = [[(word in f and f[word] or 0) for word in wordvec] for f in articlew]
	return l1, wordvec

def showfeatures(w, h, titles, wordvec, out = 'features.txt'):
	outfile = file(out, 'w')
	pc, wc = np.shape(h)
	toppatterns = [[] for i in range(len(titles))]
	patternnames = []

	# loop over all the features
	for i in range(pc):
		slist = []
		# create a list of words and their weights
		for j in range(wc):
			slist.append((h[i, j], wordvec[j]))
		# reverse sort the word list
		slist.sort()
		slist.reverse()

		# print the first six elements
		n = [s[1] for s in slist[0:6]]
		outfile.write(str(n) + '\n')
		patternnames.append(n)

		# create a list of articles for this feature
		flist = []
		for j in range(len(titles)):
			# add the article with its weight
			flist.append((w[j, i], titles[j]))
			toppatterns[j].append((w[j, i], i, titles[j]))
		# reverse sort the list
		flist.sort()
		flist.reverse()

		# show the top 3 articles
		for f in flist[0:3]:
			outfile.write(str(f) + '\n')
		outfile.write('\n')

	outfile.close()
	# return the pattern names for later use
	return toppatterns, patternnames

def showarticles(titles, toppatterns, patternnames, out = 'articles.txt'):
	outfile = file(out, 'w')

	# loop over all the articles
	for j in range(len(titles)):
		outfile.write(titles[j] + '\n')

		# get the top features for this article and reverse sort them
		toppatterns[j].sort()
		toppatterns[j].reverse()

		# print the top three patterns
		for i in range(3):
			try:
				outfile.write(str(toppatterns[j][i][0]) + ' ' +
							  str(patternnames[j][i][1]) + '\n')
			except IndexError:
				outfile.close()
				return
		outfile.write('\n')


if __name__ == "__main__":
	allw, articlew, artt = getarticlewords()
	wordmatrix, wordvec = makematrix(allw, articlew)

	# print wordvec[0:10]
	# print artt[1]
	# print wordmatrix[1][0:10]

	# hierarchical clustering
	import clusters
	clust = clusters.hcluster(wordmatrix)
	clusters.drawdendrogram(clust, artt, jpeg = 'news.jpg')

	# non-negative matrix factorization
	import nmf
	# m1 = np.matrix([[1, 2, 3], [4, 5, 6]])
	# m2 = np.matrix([[1, 2], [3, 4], [5, 6]])
	# w, h = nmf.factorize(m1 * m2, pc = 3, iter = 100)
	# print w * h

	v = np.matrix(wordmatrix)
	weights, feats = nmf.factorize(v, pc = 20, iter = 50)
	topp, pn = showfeatures(weights, feats, artt, wordvec)
	showarticles(artt, topp, pn)

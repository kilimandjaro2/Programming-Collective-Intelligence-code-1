#!/usr/bin/python

import urllib2
import sqlite3
import re
import nn
from bs4 import BeautifulSoup
from urlparse import urljoin

IGNOREWORDS = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it'])

mynet = nn.searchnet('nn.db')

class Crawler:
	# initialize the crawler with the name of database
	def __init__(self, dbname):
		self.con = sqlite3.connect(dbname)

	def __del__(self):
		self.con.close()

	def dbcommit(self):
		self.con.commit()

	# auxilliary function for getting an entry id and adding it if not present
	def getentryid(self, table, field, value, createnew = True):
		cur = self.con.execute(
			  "SELECT rowid FROM %s WHERE %s = '%s'" % (table, field, value))
		res = cur.fetchone()
		if res == None:
			cur = self.con.execute(
				  "INSERT INTO %s (%s) VALUES ('%s')" % (table, field, value))
			return cur.lastrowid
		else:
			return res[0]

	# index an individual page
	def addtoindex(self, url, soup):
		if self.isindexed(url):
			return
		print "Indexing %s" % url

		# get the individual words
		text = self.gettextonly(soup)
		words = self.separatewords(text)

		# get the url id
		urlid = self.getentryid('urllist', 'url', url)

		# link each word to the list
		for i in range(len(words)):
			word = words[i]
			if word in IGNOREWORDS:
				continue
			wordid = self.getentryid('wordlist', 'word', word)
			self.con.execute(
					"INSERT INTO wordlocation(urlid, wordid, location) \
					VALUES (%d, %d, %d)" % (urlid, wordid, i))

	# extract the text from an html page
	def gettextonly(self, soup):
		v = soup.string
		if v == None:
			c = soup.contents
			resulttext = ''
			for t in c:
				subtext = self.gettextonly(t)
				resulttext += subtext + '\n'
			return resulttext
		else:
			return v.strip()

	# separate words by any non-whitespace character
	def separatewords(self, text):
		splitter = re.compile('\\W*')
		return [s.lower() for s in splitter.split(text) if s != '']

	# return True if url is already indexed
	def isindexed(self, url):
		u = self.con.execute(
			"SELECT rowid FROM urllist WHERE url = '%s'" % url).fetchone()
		if u != None:
			# check if it has actually been crawled
			v = self.con.execute(
				"SELECT * FROM wordlocation WHERE urlid = %d" % u[0]).fetchone()
			if v != None:
				return True
		return False

	# add a link between two pages
	def addlinkref(self, urlFrom, urlTo, linkText):
		pass

	# starting with a list of pages, do a breadth first search to the given
	# depth, indexing pages as we go
	def crawl(self, pages, depth = 2):
		for i in range(depth):
			newpages = set()
			for page in pages:
				try:
					c = urllib2.urlopen(page)
				except:
					print "Could not open %s" % page
					continue
				soup = BeautifulSoup(c.read())
				self.addtoindex(page, soup)

				links = soup('a')
				for link in links:
					if 'href' in dict(link.attrs):
						# combine base url with another, e.g.
						# urljoin('a.com', 'a.com/about') -> 'a.com/about'
						# urljoin('a.com', 'b.com') -> 'b.com'
						url = urljoin(page, link['href'])
						if url.find("'") != -1:
							continue
						url = url.split('#')[0] # remove location portion
						if url[0:4] == 'http' and not self.isindexed(url):
							newpages.add(url)
						linkText = self.gettextonly(link)
						self.addlinkref(page, url, linkText)

				self.dbcommit()
			pages = newpages

	# create the database table
	def createindextables(self):
		self.con.execute('CREATE TABLE urllist(url)')
		self.con.execute('CREATE TABLE wordlist(word)')
		self.con.execute('CREATE TABLE wordlocation(urlid, wordid, location)')
		self.con.execute('CREATE TABLE link(fromid INTEGER, toid INTEGER)')
		self.con.execute('CREATE TABLE linkwords(wordid, linkid)')
		# indices to speed up searching
		self.con.execute('CREATE INDEX wordidx ON wordlist(word)')
		self.con.execute('CREATE INDEX urlidx ON urllist(url)')
		self.con.execute('CREATE INDEX wordurlidx ON wordlocation(wordid)')
		self.con.execute('CREATE INDEX urltoidx ON link(toid)')
		self.con.execute('CREATE INDEX urlfromidx ON link(fromid)')
		self.dbcommit()

	# precalculate PageRank
	def calculatepagerank(self, iterations = 20):
		# clear out the current PageRank tables
		self.con.execute('DROP TABLE IF EXISTS pagerank')
		self.con.execute('CREATE TABLE pagerank(urlid PRIMARY KEY, score)')

		# initialize every url with a PageRank of 1
		self.con.execute('INSERT INTO pagerank SELECT rowid, 1.0 FROM urllist')
		self.dbcommit()

		for i in range(iterations):
			print "Iteration %d" % (i)
			# loop through all the pages
			for (urlid, ) in self.con.execute('SELECT rowid FROM urllist'):
				pr = 0.15

				# loop through all the pages that link to this one
				for (linker, ) in self.con.execute(
					'SELECT DISTINCT fromid FROM link WHERE toid = %d' % urlid):
					# get the PageRank of the linker
					linkingpr = self.con.execute(
						'SELECT score FROM pagerank WHEN urlid = %d' \
						% linker).fetchone()[0]

					# get the total number of links from the linker
					linkingcount = self.con.execute(
						'SELECT COUNT(*) FROM link WHERE fromid = %d' \
						% linker).fetchone()[0]
					pr += 0.85 * (linkingpr / linkingcount)
				self.con.execute(
					'UPDATE pagerank SET score = %f \
					 WHERE urlid = %d' % (pr, urlid))
			self.dbcommit()


class searcher:
	def __init__(self, dbname):
		self.con = sqlite3.connect(dbname)

	def __del__(self):
		self.con.close()

	def getmatchrows(self, q):
		# strings to build the query
		fieldlist = 'w0.urlid'
		tablelist = ''
		clauselist = ''
		wordids = []

		# split the words by spaces
		words = q.split(' ')
		tablenumber = 0

		for word in words:
			# get the word id
			wordrow = self.con.execute(
			 'SELECT rowid FROM wordlist WHERE word = "%s"' % word).fetchone()
			if wordrow != None:
				wordid = wordrow[0]
				wordids.append(wordid)
				if tablenumber > 0:
					tablelist += ','
					clauselist += ' and '
					clauselist += \
					'w%d.urlid=w%d.urlid and ' % (tablenumber - 1, tablenumber)
				fieldlist += ',w%d.location' % tablenumber
				tablelist += 'wordlocation w%d' % tablenumber
				clauselist += 'w%d.wordid=%d' % (tablenumber, wordid)
				tablenumber += 1

		# create the query from the separate parts
		fullquery = \
		 'SELECT %s FROM %s WHERE %s' % (fieldlist, tablelist, clauselist)
		# print fullquery
		cur = self.con.execute(fullquery)
		rows = [row for row in cur]

		return rows, wordids

	def getscoredlist(self, rows, wordids):
		totalscores = dict([(row[0], 0) for row in rows])

		# PUT THE SCORE FUNCTION HERE
		# weights = []

		# combination of weights
		weights = [
				   (1.0, self.frequencyscore(rows)),
				   (1.0, self.locationscore(rows)),
				   (1.0, self.distancescore(rows)),
				   (1.0, self.pagerankscore(rows)),
				   (1.0, self.linktextscore(rows, wordids)),
				   ]

		for (weight, scores) in weights:
			for url in totalscores:
				totalscores[url] += weight*scores[url]

		return totalscores

	def geturlname(self, id):
		return self.con.execute(
		 'SELECT url FROM urllist WHERE rowid = %d' % id).fetchone()[0]

	def query(self, q):
		rows, wordids = self.getmatchrows(q)
		scores = self.getscoredlist(rows, wordids)
		rankedscores = sorted([(score, url) \
							   for (url, score) in scores.items()], reverse = 1)
		for (score, urlid) in rankedscores[0:10]:
			print "%f\t%s" % (score, self.geturlname(urlid))
		return wordids, [r[1] for r in rankedscores[0:10]]

	def normalizescores(self, scores, smallIsBetter = 0):
		vsmall = 0.00001 # avoid division by zero errors
		if smallIsBetter:
			minscore = min(scores.values())
			return dict([(u, float(minscore)/max(vsmall, l)) \
						 for (u, l) in scores.items()])
		else:
			maxscore = max(scores.values())
			if maxscore == 0:
				maxscore = vsmall
			return dict([(u, float(c)/maxscore) for (u, c) in scores.items()])

	def frequencyscore(self, rows):
		counts = dict([(row[0], 0) for row in rows])
		for row in rows:
			counts[row[0]] += 1
		return self.normalizescores(counts)

	def locationscore(self, rows):
		locations = dict([(row[0], 1000000) for row in rows])
		for row in rows:
			# e.g. row = (urlid, location1, location2, ...)
			loc = sum(row[1:])
			if loc < locations[row[0]]:
				locations[row[0]] = loc
		return self.normalizescores(locations, smallIsBetter = 1)

	def distancescore(self, rows):
		# if there's only one word, everyone wins!
		if len(rows[0]) <= 2:
			return dict([(row[0], 1.0) for row in rows])

		# initialize the dictionary with large values
		mindistance = dict([(row[0], 1000000) for row in rows])

		for row in rows:
			dist = sum([abs(row[i] - row[i-1]) for i in range(2, len(row))])
			if dist < mindistance[row[0]]:
				mindistance[row[0]] = dist
		return self.normalizescores(mindistance, smallIsBetter = 1)

	def inboundlinkscore(self, rows):
		uniqueurls = set([row[0] for row in rows])
		inboundcount = dict([(u, self.con.execute(\
			'SELECT COUNT(*) FROM link WHERE toid = %d' % u).fetchone()[0]) \
			for u in uniqueurls])
		return self.normalizescores(inboundcount)

	def pagerankscore(self, rows):
		pageranks = dict([(row[0], self.con.execute(
						   'SELECT score FROM pagerank WHERE urlid = %d' \
						   % row[0]).fetchone()[0]) for row in rows])
		maxrank = max(pageranks.values())
		normalizedscores = dict([(u, float(l)/maxrank) \
								 for (u, l) in pageranks.items()])
		return normalizedscores

	def linktextscore(self, rows, wordids):
		linkscores = dict([(row[0], 0) for row in rows])
		for wordid in wordids:
			cur = self.con.execute(
				'SELECT link.fromid, link.toid FROM linkwords, link \
				 WHERE wordid = %d and linkwords.linkid = link.rowid' % wordid)
			for (fromid, toid) in cur:
				if toid in linkscores:
					pr = self.con.execute(
						'SELECT score FROM pagerank WHERE urlid = %d' \
						 % fromid).fetchone()[0]
					linkscores[toid] += pr
		maxscore = max(linkscores.values())
		if maxscore == 0:
			maxscore = 0.00001
		normalizedscores = dict([(u, float(l)/maxscore) \
								 for (u, l) in linkscores.items()])
		return normalizedscores

	def nnscore(self, rows, wordids):
		# get unique url ids as an ordered list
		urlids = [urlid for urlid in set([row[0] for row in rows])]
		nnres = mynet.getresult(wordids, urlids)
		scores = dict([(urlids[i], nnres[i]) for i in range(len(urlids))])
		return self.normalizescores(scores)


if __name__ == "__main__":
	pagelist = ['http://kiwitobes.com']
	crawler = Crawler('searchindex.db')
	# try:
	#	 crawler.createindextables()
	# except sqlite3.OperationalError:
	#	 pass
	# crawler.crawl(pagelist)
	# crawler.calculatepagerank()

	e = searcher('searchindex.db')

	# cur = crawler.con.execute('SELECT * FROM pagerank ORDER BY score DESC')
	# for i in range(10):
	#	 nxt = cur.next()
	#	 print e.geturlname(nxt[0]), nxt[1]

	e.query('make things')

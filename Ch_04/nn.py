#!/usr/bin/python

import sqlite3
from math import tanh


def dtanh(y):
	'''Slope of the tanh().'''
	return 1.0 - y*y


class Searchnet:
	def __init__(self, dbname):
		self.con = sqlite3.connect(dbname)

	def __del__(self):
		self.con.close()

	def maketables(self):
		self.con.execute('CREATE TABLE hiddennode(create_key)')
		self.con.execute('CREATE TABLE wordhidden(fromid, toid, strength)')
		self.con.execute('CREATE TABLE hiddenurl(fromid, toid, strength)')
		self.con.commit()

	def getstrength(self, fromid, toid, layer):
		if layer == 0:
			table = 'wordhidden'
		else:
			table = 'hiddenurl'
		res = self.con.execute(
			'SELECT strength FROM %s WHERE fromid = %d and toid = %d' \
			% (table, fromid, toid)).fetchone()
		if res == None:
			if layer == 0:
				return -0.2
			if layer == 1:
				return 0
		return res[0]

	def setstrength(self, fromid, toid, layer, strength):
		if layer == 0:
			table = 'wordhidden'
		else:
			table = 'hiddenurl'
		res = self.con.execute(
			'SELECT rowid FROM %s WHERE fromid = %d AND toid = %d' \
			% (table, fromid, toid)).fetchone()
		if res == None:
			self.con.execute(
				'INSERT INTO %s (fromid, toid, strength) VALUES (%d, %d, %f)' \
				% (table, fromid, toid, strength))
		else:
			rowid = res[0]
			self.con.execute(
				'UPDATE %s SET strength = %f WHERE rowid = %d' \
				% (table, strength, rowid))

	def generatehiddennode(self, wordids, urls):
		if len(wordids) > 3:
			return None
		# check if we already created a node for this set of words
		createkey = '_'.join(sorted([str(wi) for wi in wordids]))
		res = self.con.execute(
			'SELECT rowid FROM hiddennode WHERE create_key = "%s"' \
			% createkey).fetchone()

		# if not, create it
		if res == None:
			cur = self.con.execute(
				'INSERT INTO hiddennode (create_key) VALUES ("%s")' \
				 % createkey)
			hiddenid = cur.lastrowid
			# put in some default weights
			for wordid in wordids:
				self.setstrength(wordid, hiddenid, 0, 1.0/len(wordids))
			for urlid in urls:
				self.setstrength(hiddenid, urlid, 1, 0.1)
			self.con.commit()

	def getallhiddenids(self, wordids, urlids):
		l1 = {}
		for wordid in wordids:
			cur = self.con.execute(
				'SELECT toid FROM wordhidden WHERE fromid = %d' % wordid)
			for row in cur:
				l1[row[0]] = 1
		for urlid in urlids:
			cur = self.con.execute(
				'SELECT fromid FROM hiddenurl WHERE toid = %d' % urlid)
			for row in cur:
				l1[row[0]] = 1
		return l1.keys()

	def setupnetwork(self, wordids, urlids):
		# value lists
		self.wordids = wordids
		self.hiddenids = self.getallhiddenids(wordids, urlids)
		self.urlids = urlids

		# node outputs
		self.ai = [1.0] * len(self.wordids)
		self.ah = [1.0] * len(self.hiddenids)
		self.ao = [1.0] * len(self.urlids)

		# create weights matrix
		self.wi = [[self.getstrength(wordid, hiddenid, 0) \
					for hiddenid in self.hiddenids] for wordid in self.wordids]
		self.wo = [[self.getstrength(hiddenid, urlid, 1) \
					for urlid in self.urlids] for hiddenid in self.hiddenids]

	def feedforward(self):
		# the only inputs are the query words
		for i in range(len(self.wordids)):
			self.ai[i] = 1.0

		# hidden activations
		for j in range(len(self.hiddenids)):
			sum = 0.0
			for i in range(len(self.wordids)):
				sum += self.ai[i] * self.wi[i][j]
			self.ah[j] = tanh(sum)

		# output activations
		for k in range(len(self.urlids)):
			sum = 0.0
			for j in range(len(self.hiddenids)):
				sum += self.ah[j] * self.wo[j][k]
			self.ao[k] = tanh(sum)

		return self.ao[:]

	def getresult(self, wordids, urlids):
		self.setupnetwork(wordids, urlids)
		return self.feedforward()

	def backpropagate(self, targets, N = 0.5):
		# calcuate errors for output
		output_deltas = [0.0] * len(self.urlids)
		for k in range(len(self.urlids)):
			error = targets[k] - self.ao[k]
			output_deltas[k] = dtanh(self.ao[k]) * error

		# calculate errors for hidden layer
		hidden_deltas = [0.0] * len(self.hiddenids)
		for j in range(len(self.hiddenids)):
			error = 0.0
			for k in range(len(self.urlids)):
				error += output_deltas[k] * self.wo[j][k]
			hidden_deltas[j] = dtanh(self.ah[j]) * error

		# update output weights
		for j in range(len(self.hiddenids)):
			for k in range(len(self.urlids)):
				change = output_deltas[k] * self.ah[j]
				self.wo[j][k] = self.wo[j][k] + N * change

		# update input weights
		for i in range(len(self.wordids)):
			for j in range(len(self.hiddenids)):
				change = hidden_deltas[j] * self.ai[i]
				self.wi[i][j] = self.wi[i][j] + N * change

	def trainquery(self, wordids, urlids, selection):
		# generate a hidden node if necessary
		self.generatehiddennode(wordids, urlids)

		self.setupnetwork(wordids, urlids)
		self.feedforward()
		targets = [0.0] * len(urlids)
		targets[urlids.index(selection)] = 1.0
		error = self.backpropagate(targets)
		self.updatedatabase()

	def updatedatabase(self):
		# set them to database values
		for i in range(len(self.wordids)):
			for j in range(len(self.hiddenids)):
				self.setstrength(self.wordids[i], self.hiddenids[j],
								 0, self.wi[i][j])
		for j in range(len(self.hiddenids)):
			for k in range(len(self.urlids)):
				self.setstrength(self.hiddenids[j], self.urlids[k],
								 1, self.wo[j][k])
		self.con.commit()


if __name__ == "__main__":
	mynet = Searchnet('nn.db')
	try:
		mynet.maketables()
	except sqlite3.OperationalError:
		pass

	wWorld, wRiver, wBank = 101, 102, 103
	uWorldBank, uRiver, uEarth = 201, 202, 203
	mynet.generatehiddennode([wWorld, wBank], [uWorldBank, uRiver, uEarth])

	# print "Before training:", mynet.getresult([wWorld, wBank],
	#											[uWorldBank, uRiver, uEarth])
	#
	# mynet.trainquery([wWorld, wBank], [uWorldBank, uRiver, uEarth], uWorldBank)
	# print "After training:", mynet.getresult([wWorld, wBank],
	#										  [uWorldBank, uRiver, uEarth])

	# training set
	allurls = [uWorldBank, uRiver, uEarth]
	for i in range(30):
		mynet.trainquery([wWorld, wBank], allurls, uWorldBank)
		mynet.trainquery([wRiver, wBank], allurls, uRiver)
		mynet.trainquery([wWorld], allurls, uEarth)

	print mynet.getresult([wWorld, wBank], allurls)
	print mynet.getresult([wRiver, wBank], allurls)
	print mynet.getresult([wBank], allurls)

#!/usr/bin/python

import numpy as np

def difcost(a, b):
	dif = 0
	# loop over every row and column in the matrix
	for i in range(np.shape(a)[0]):
		for j in range(np.shape(a)[1]):
			# add together the differences
			dif += pow(a[i, j] - b[i, j], 2)
	return dif

def factorize(v, pc = 10, iter = 50):
	ic = np.shape(v)[0]
	fc = np.shape(v)[1]

	# initialize the weight and feature matricies with random values
	w = np.matrix([[np.random.random() for j in range(pc)] for i in range(ic)])
	h = np.matrix([[np.random.random() for i in range(fc)] for i in range(pc)])

	# perform operation a maximum of iter times
	for i in range(iter):
		wh = w * h

		# calculate the current difference
		cost = difcost(v, wh)

		if i % 10 == 0:
			print cost

		# terminate if the matrix has been fully factorized
		if cost == 0:
			break

		# update feature matrix
		hn = np.transpose(w) * v
		hd = np.transpose(w) * w * h
		hd[hd == 0] = 0.000001

		h = np.matrix(np.array(h) * np.array(hn) / np.array(hd))
		np.nan_to_num(h)

		# update weights matrix
		wn = v * np.transpose(h)
		wd = w * h * np.transpose(h)
		wd[wd == 0] = 0.000001

		w = np.matrix(np.array(w) * np.array(wn) / np.array(wd))
		np.nan_to_num(w)

	return w, h

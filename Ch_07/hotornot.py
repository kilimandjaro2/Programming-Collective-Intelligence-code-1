#!/usr/bin/python
"""
Note: since the HotOrNot API is depreciated, this program is of no practical use.
"""

import urllib2
import xml.dom.minidom
import treepredict

api_key = "479NUNJHETN"

def getrandomratings(c):
	# construct url for getRandomProfile
	url = "http://services.hotornot.com/rest/?app_key=%s" % api_key
	url += "&method=Rate.getRandomProfile&retrieve_num=%d" % c
	url += "&get_rate_info=true&meet_users_only=true"

	f1 = urllib2.urlopen(url).read()

	doc = xml.dom.minidom.parseString(f1)

	emid = doc.getElementsByTagName('emid')
	ratings = doc.getElementByTagName('rating')

	# combine the emids and ratings together into a list
	result = []
	for e, r in zip(emid, ratings):
		if r.firstChild != None:
			result.append((e.firstChild.data, r.firstChild.data))
	return result

stateregions = {'New England':['ct','mn','ma','nh','ri','vt'],
				'Mid Atlantic':['de','md','nj','ny','pa'],
				'South':['al','ak','fl','ga','ky','la','ms','mo',
					   'nc','sc','tn','va','wv'],
				'Midwest':['il','in','ia','ks','mi','ne','nd','oh','sd','wi'],
				'West':['ak','ca','co','hi','id','mt','nv','or','ut','wa','wy']}

def getpeopledata(ratings):
	result = []
	for emid, rating in ratings:
		# url forthe MeetMe.getProfile method
		url = "http://services.hotornot.com/rest/?app_key=%s" % api_key
		url += "&method=MeetMe.getProfile&emid=%s&get_keywords=true" % emid

		# get all the info about this persion
		try:
			rating = int(float(rating) + 0.5)
			doc2 = xml.dom.minidom.parseString(urllib2.urlopen(url).read())
			gender = doc2.getElementsByTagName('gender')[0].firstChild.data
			age = doc.getElementsByTagName('age')[0].firstChild.data
			loc = doc.getElementsByTagName('location')[0].firstChild.data[0:2]

			# convert state to region
			for r, s in stateregions.items():
				if loc in s:
					region = r

			if region != None:
				result.append((gender, int(age), region, rating))
		except:
			pass
	return result


if __name__ == "__main__":
	l1 = getrandomratings(500)
	print "Get", len(l1), "ratings"
	pdata = getpeopledata(l1)
	print "Get", len(pdata), "info of people"

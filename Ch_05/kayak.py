#!/usr/bin/python
"""
Note: since the Kayak API is depreciated, this program is of no practical use.
"""

import time
import urllib2
import xml.dom.minidom

kayakkey = 'YOURKEYHERE'

def getkayaksession():
	# construct the url to start a session
	url = 'http://www.kayak.com/k/ident/apisession?token=%s&version=1' % kayakkey

	# parse the resulting xml
	doc = xml.dom.minidom.parseString(urllib2.urlopen(url).read())

	# find <sid>xxxxxxxx</sid>
	sid = doc.getElementsByTagName('sid')[0].firstChild.data
	return sid

def flightsearch(sid, origin, destination, depart_date):
	# construct search url
	url = 'http://www.kayak.com/s/apisearch?basicmode=true&oneway=y&origin=%s' \
		  % origin
	url += '&destination=%s&depart_date=%s' % (destination, depart_date)
	url += '&return_date=none&depart_time=a&return_time=a'
	url += '&travelers=1&cabin=e&action=doFlights&apimode=1'
	url += '&_sid_=%s&version=1' % (sid)

	# get the xml
	doc = xml.dom.minidom.parseString(urllib2.urlopen(url).read())

	# extract the search id
	searchid = doc.getElementsByTagName('searchid')[0].firstChild.data

	return searchid

def flightsearchresults(sid, searchid):
	# removes leading $, commas and converts number to a float
	def parseprice(p):
		return float(p[1:].replace(',', ''))

	# polling loop
	while 1:
		time.sleep(2)

		# construct url for polling
		url = 'http://www.kayak.com/s/basic/flight?'
		url += 'searchid=%s&c=5&apimode=1&_sid_=%s&version=1' % (searchid,sid)
		doc = xml.dom.minidom.parseString(urllib2.urlopen(url).read())

		# look for morepending tag, and wait until it is no longer trun
		morepending = doc.getElementsByTagName('morepending')[0].firstChild
		if morepending == None or morepending.data == 'false':
			break

	# now download the complete list
	url = 'http://www.kayak.com/s/basic/flight?'
	url += 'searchid=%s&c=999&apimode=1&_sid_=%s&version=1' % (searchid,sid)
	doc = xml.dom.minidom.parseString(urllib2.urlopen(url).read())

	# get the various elements as lists
	prices = doc.getElementsByTagName('price')
	departures = doc.getElementsByTagName('depart')
	arrivals = doc.getElementsByTagName('arrive')

	# zip them together
	return zip([p.firstChild.data.split(' ')[1] for p in departures],
			   [p.firstChild.data.split(' ')[1] for p in arrivals],
			   [parseprice(p.firstChild.data) for p in prices])

def createschedule(people, dest, dep, ret):
	# get a session id for these searches
	sid = getkayaksession()
	flights = {}

	for p in people:
		name, origin = p
		# outbound flight
		searchid = flightsearch(sid, origin, dest, dep)
		flights[(origin, dest)] = flightsearchresults(sid, searchid)

		# return flight
		searchid = flightsearch(sid, dest, origin, ret)
		flights[(dest, origin)] = flightsearchresults(sid, searchid)

	return flights

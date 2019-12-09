#!/usr/bin/python

from pydelicious import get_popular, get_userposts, get_urlposts

def initializeUserDict(tag, count = 5):
	'''Get a list of users who recently posted a popular link.'''
	user_dict = {}
	# get the top count popular posts
	for p1 in get_popular(tag = tag)[0:count]:
		# find all users who posted this
		for p2 in get_urlposts(p1['href']):
			user = p2['user']
			user_dict.setdefault(user, {})
	return user_dict

def fillItems(user_dict):
	'''Fill in ratings for all the users.'''
	all_items = {}
	# find links posted by all users
	for user in user_dict:
		for i in range(3):
			try:
				posts = get_userposts(user)
				break
			except:
				print("Failed user "+user+", retrying")
				time.sleep(4)
		for post in posts:
			url = post['href']
			user_dict[user][url] = 1.0
			all_items[url] = 1

	# fill in missing items with 0
	for ratings in list(user_dict.values()):
		for item in all_items:
			if item not in ratings:
				ratings[item] = 0.0
